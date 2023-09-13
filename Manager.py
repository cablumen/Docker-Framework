from json import load as jsonload
from os.path import dirname, realpath, join, isfile, isdir
from os import remove, mkdir, rename
from pickle import dump as pickledump
from pickle import load as pickleload
from sys import exit as sysexit
from uuid import uuid5, NAMESPACE_OID
from subprocess import run as run_subprocess
from shutil import rmtree
import docker

class Manager(object):
    def __init__(self, manager_config, run_config):
        #   manager config parsing
        # concurrent_workers
        if manager_config['concurrent_workers'] < 1:
            print("Error: manager_config.json's concurrent_workers cannot be less than 1")
            sysexit()
        self.concurrent_workers = manager_config['concurrent_workers']

        # entry_point
        root_path = dirname(realpath(__file__))
        src_path = join(root_path, "src")
        container_entry_path = join(src_path, manager_config['entry_path'])
        if not isfile(container_entry_path):
            print("Error: no entry_point file in src directory")
            sysexit()
        self.entry_path = manager_config['entry_path']

        # save_path
        if not manager_config['save_path'].endswith('.pk'):
            print("Error: save_path must be pickle type (.pk)")
            sysexit()
        self.save_path = join(root_path, manager_config['save_path'])

        # log_path
        self.log_path = join(root_path, "logs")
        if not isdir(self.log_path):
            mkdir(self.log_path)

        self.config_hash = str(uuid5(NAMESPACE_OID, str(run_config)))
        self.state = {"config_hash": self.config_hash}

        self.docker_client = docker.from_env()
        run_hashes = [x["hash"] for x in run_config]

        # save current state if thrown exception
        try:
            self.execute_config(run_hashes)
        except Exception:
            self.save_state()
            raise

    def execute_config(self, run_hashes):
        self.get_state()

        # check if all configs are finished
        self.config_count = len(run_hashes)
        if len(self.state["finished"]) == self.config_count:
            print("Manager: run_config has been completed. Delete " + str(self.save_path) + " to re-run.")
            sysexit()

        self.create_run_image()

        print("Manager: running " + str(len(self.state["queued"])) + " configs")
        while True:
            # detect when containers change state and update internal state
            running_containers = self.docker_client.containers.list(all=True, filters={'status':'running'})
            running_container_names = [x.name for x in running_containers]
            running_hashes = [x for x in self.state["running"] if x in running_container_names]
            finished_hashes = [x for x in self.state["running"] if x not in running_container_names]
            self.state["running"] = running_hashes
            self.state["finished"].extend(finished_hashes)

            # if any containers finished, persist state for next run
            if len(finished_hashes) > 0:
                self.delete_containers(finished_hashes)
                self.save_state()

                # check if all configs are finished
                if len(self.state["finished"]) == self.config_count:
                    self.delete_run_image()
                    break

            # execute another container if running containers is less than configuration
            if len(self.state["running"]) < self.concurrent_workers:
                containers_to_run = self.concurrent_workers - len(self.state["running"])
                series_hash_list = self.state["queued"][0:containers_to_run]
                self.state["queued"] = self.state["queued"][containers_to_run:]
                self.state["running"].extend(series_hash_list)
                self.create_containers(series_hash_list)

    def get_state(self):
        # check for persisted manager data
        if isfile(self.save_path):
            save_file = open(self.save_path, 'rb')
            save_state = pickleload(save_file)
            save_file.close()
            # if pickled data is associated with this run config, use it
            if save_state["config_hash"] == self.state["config_hash"]:
                # insure finished and running containers were deleted
                check_for_deletion = save_state["running"] + save_state["finished"]
                self.delete_containers(check_for_deletion)

                # re-run running containers because no guarantee of completion 
                self.state["queued"] =  save_state["running"] + save_state["queued"]
                self.state["running"] = []
                self.state["finished"] = save_state["finished"]
            # if pickled data is not associated with this run config, delete
            else:
                self.delete_state()
        else:
            self.state["queued"] = [x["hash"] for x in run_config]
            self.state["running"] = []
            self.state["finished"] = []

    def save_state(self):
        save_file = open(self.save_path, 'wb')
        pickledump(self.state, save_file)
        save_file.close()

    def delete_state(self):
        remove(self.save_path)

    def create_run_image(self):
        # remove image if it exists
        self.delete_run_image()
        self.docker_client.images.build(path = "./", tag=self.config_hash)

    def delete_run_image(self):
        try:
            self.docker_client.images.get(self.config_hash)
            self.docker_client.images.remove(self.config_hash)
        except docker.errors.NotFound:
            pass
        except Exception:
            print("Error: unable to delete docker image")
            raise

    def create_containers(self, hash_list):
        for series_hash in hash_list:
            self.create_container(series_hash)

    def create_container(self, series_hash):
        self.delete_container(series_hash)

        # create container using manager_config.json values
        self.docker_client.containers.run(image=self.config_hash, name=series_hash, entrypoint=['python', self.entry_path, series_hash], detach=True)

    def delete_containers(self, hash_list):
        for series_hash in hash_list:
            self.delete_container(series_hash)

    def delete_container(self, series_hash):
        # remove container
        try:
            container = self.docker_client.containers.get(series_hash)
            if container.status != "exited":
                print("Warning: attempting to delete unfinished container")

            # collect files in log folder
            src_path = series_hash + ":/logs/"
            run_subprocess(["docker", "cp", "-q", src_path, self.log_path])

            # rename logs folder to container id
            old_container_path = join(self.log_path, "logs")
            new_container_path = join(self.log_path, series_hash)
            if isdir(new_container_path):
                rmtree(new_container_path)

            rename(old_container_path, new_container_path)

            # write container stdout to file
            stdout_path = join(new_container_path, "stdout.txt")
            stdout_file = open(stdout_path, "w")
            stdout_file.write(container.logs().decode())
            stdout_file.close()

            container.remove()
        except docker.errors.NotFound:
            pass
        except Exception:
            print("Error: unable to delete container")
            raise

if __name__ == "__main__":
    manager_config_path = "./manager_config.json"
    if not isfile(manager_config_path):
        print("Error: no manager_config.json file in root directory")
        sysexit()

    manager_config = jsonload(open(manager_config_path))

    run_config_path = "./run_config.json"
    if not isfile(run_config_path):
        print("Error: no run_config.json file in root directory")
        sysexit()

    run_config = jsonload(open(run_config_path))

    manager = Manager(manager_config, run_config)
