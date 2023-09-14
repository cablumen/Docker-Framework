from json import load as jsonload
from os.path import dirname, realpath, join, isfile, isdir
from os import remove, mkdir
from pickle import dump as pickledump
from pickle import load as pickleload
from sys import exit as sysexit
from uuid import uuid5, NAMESPACE_OID
from subprocess import run as run_subprocess
from shutil import rmtree as shutil_rmtree
import docker

class Manager(object):
    def __init__(self):
        #   manager config parsing
        # concurrent_containers
        if not isinstance(manager_config['concurrent_containers'], int):
            print("Error: manager_config.json's concurrent_containers must be type of int")
            sysexit()

        if manager_config['concurrent_containers'] < 1:
            print("Error: manager_config.json's concurrent_containers cannot be less than 1")
            sysexit()
        self.concurrent_containers = manager_config['concurrent_containers']

        # container_entry_path
        if not isinstance(manager_config['container_entry_path'], str):
            print("Error: manager_config.json's container_entry_path must be type of str")
            sysexit()

        root_path = dirname(realpath(__file__))
        src_path = join(root_path, "src")
        container_entry_path = join(src_path, manager_config['container_entry_path'])
        if not isfile(container_entry_path):
            print("Error: no container_entry_path file in src directory")
            sysexit()
        self.entry_point = manager_config['container_entry_path']

        post_entry_path = join(src_path, manager_config['post_run_entry_path'])
        if not isfile(post_entry_path):
            print("Error: no post_run_entry_path file in src directory")
            sysexit()
        self.post_entry_point = manager_config['post_run_entry_path']

        # rerun_completed_configs
        if not isinstance(manager_config['rerun_completed_configs'], bool):
            print("Error: manager_config.json's rerun_completed_configs must be type of bool")
            sysexit()
        self.rerun_configs = manager_config['rerun_completed_configs']

        # use_gpus
        if not isinstance(manager_config['use_gpus'], bool):
            print("Error: manager_config.json's use_gpus must be type of bool")
            sysexit()
        self.use_gpus = manager_config['use_gpus']

        # save_path
        self.save_path = join(root_path, "manager_save.pk")

        # hash of run_config.json to check uniqueness
        self.config_hash = str(uuid5(NAMESPACE_OID, str(run_config)))

        # log_path
        logs_folder = join(src_path, "logs")
        if not isdir(logs_folder):
            mkdir(logs_folder)

        self.log_path = join(logs_folder, self.config_hash)
        if not isdir(self.log_path):
            mkdir(self.log_path)

        self.state = {}

        self.docker_client = docker.from_env()

        # save current state if thrown exception
        try:
            self.execute_config()
        except Exception:
            self.save_state()
            raise

    def execute_config(self):
        self.get_state()

        self.create_run_image()

        print("Manager: running " + str(len(self.state["queued"])) + " configs with hash " + self.config_hash)
        while True:
            # detect when containers change state
            running_containers = self.docker_client.containers.list(all=True, filters={'status':'running'})
            running_container_names = [x.name for x in running_containers]
            running_hashes = [x for x in self.state["running"] if x in running_container_names]
            finished_hashes = [x for x in self.state["running"] if x not in running_container_names]
            self.state["running"] = running_hashes

            # if any containers finished, persist state for next run
            if len(finished_hashes) > 0:
                self.delete_containers(finished_hashes)
                self.state["finished"].extend(finished_hashes)
                self.save_state()

                # check if all configs are finished
                if len(self.state["queued"]) + len(self.state["running"]) == 0:
                    if self.post_entry_point:
                        self.execute_post_run()

                    self.delete_run_image()
                    break

            # execute another container if running containers is less than configuration
            if len(self.state["running"]) < self.concurrent_containers:
                containers_to_run = self.concurrent_containers - len(self.state["running"])
                series_hash_list = self.state["queued"][0:containers_to_run]
                self.state["queued"] = self.state["queued"][containers_to_run:]
                self.state["running"].extend(series_hash_list)
                self.create_containers(series_hash_list)
                self.save_state()

    def execute_post_run(self):
        # create post-run container
        post_run_container_name = "post-run"
        self.delete_container(post_run_container_name)
        post_run_container = self.docker_client.containers.create(image=self.config_hash, name=post_run_container_name, entrypoint=['python', self.post_entry_point], detach=True)

        # copy log files into post-run container
        dest_path = post_run_container_name + ":/data"
        copy_returncode = run_subprocess(["docker", "cp", "-q", self.log_path + "/.", dest_path]).returncode
        if copy_returncode != 0:
            print("Warning: data copy from container to host unsuccessful.")

        # run post-run container
        post_run_container.start()
        print("Manager: started post run container.")

        # wait for post-run container to exit
        while True:
            running_containers = self.docker_client.containers.list(all=True, filters={'status':'running'})
            running_container_names = [x.name for x in running_containers]
            if post_run_container_name not in running_container_names:
                break

        # delete post-run container
        self.delete_container(post_run_container_name)

    def get_state(self):
        # check for persisted manager data
        if isfile(self.save_path):
            self.load_saved_state()

            # if manager data is associated with this run config
            if self.config_hash == self.state["config_hash"]:
                # check if all configs are finished
                if len(self.state["queued"]) == 0:
                    if not self.rerun_configs:
                        print("Manager: run_config has been completed. To re-run, delete manager_save.pk or set rerun_completed_configs to true.")
                        sysexit()
                    else:
                        self.delete_saved_state()
                        self.load_run_config()

            # if manager data is not associated with this run config, delete it then load run config
            else:
                self.delete_saved_state()
                self.load_run_config()

        # manager data doesn't exist, load run config
        else:
            self.load_run_config()

    def save_state(self):
        save_file = open(self.save_path, 'wb')
        pickledump(self.state, save_file)
        save_file.close()

    def load_run_config(self):
        self.state["config_hash"] = self.config_hash
        self.state["queued"] = [x["HASH"] for x in run_config]
        self.state["running"] = []
        self.state["finished"] = []

    def load_saved_state(self):
        # load data from pickle file
        save_file = open(self.save_path, 'rb')
        save_state = pickleload(save_file)
        save_file.close()

        # ensure finished and running containers are deleted
        check_for_deletion = save_state["running"] + save_state["finished"]
        self.delete_containers(check_for_deletion)

        # re-run running containers because no guarantee of completion
        self.state["config_hash"] = save_state["config_hash"]
        self.state["queued"] =  save_state["running"] + save_state["queued"]
        self.state["running"] = []
        self.state["finished"] = save_state["finished"]

    def delete_saved_state(self):
        if isfile(self.save_path):
            remove(self.save_path)

    def create_run_image(self):
        # remove image for run if it exists
        self.delete_run_image()

        self.docker_client.images.build(path = "./", tag=self.config_hash)

    def delete_run_image(self):
        try:
            self.docker_client.images.get(self.config_hash)
            self.docker_client.images.remove(self.config_hash)
        except docker.errors.NotFound:
            pass
        except Exception:
            print("Error: unable to delete docker image.")
            raise

    def create_containers(self, hash_list):
        for series_hash in hash_list:
            self.create_container(series_hash)

    def create_container(self, series_hash):
        # remove container for series if it exists
        self.delete_container(series_hash)

        # get environment variables from run_config.json
        container_env = {}
        series_config = [x for x in run_config if x["HASH"] == series_hash][0]
        for key, value in series_config.items():
            container_env[key] = value

        gpu_request = None
        if self.use_gpus:
            # TODO: remove assumption that gpu to be used is device id 1
            gpu_request=[docker.types.DeviceRequest(device_ids=["all"], capabilities=[['gpu']])]

        # create container using manager_config.json values
        self.docker_client.containers.run(image=self.config_hash, name=series_hash, entrypoint=['python', self.entry_point], device_requests=gpu_request, environment=container_env, detach=True)
        print("Manager: started " + series_hash + " container.")

    def delete_containers(self, hash_list):
        for series_hash in hash_list:
            self.delete_container(series_hash)

    def delete_container(self, series_hash):
        # remove container
        try:
            container = self.docker_client.containers.get(series_hash)
            if container.status != "exited":
                print("Warning: attempting to delete unfinished container.")

            # create folder for container data
            dest_path = join(self.log_path, series_hash)
            if isdir(dest_path):
                shutil_rmtree(dest_path)
                mkdir(dest_path)

            # collect files in log folder
            src_path = series_hash + ":/logs/."
            copy_returncode = run_subprocess(["docker", "cp", "-q", src_path, dest_path]).returncode

            # if copy was successful, try to rename folder
            if copy_returncode != 0:
                print("Warning: data copy from container to host unsuccessful.")

            # write container stdout to file
            stdout_path = join(dest_path, "stdout.txt")
            stdout_file = open(stdout_path, "w")
            stdout_file.write(container.logs().decode())
            stdout_file.close()

            container.remove()
        except docker.errors.NotFound:
            pass
        except Exception:
            print("Error: unable to delete container.")
            raise

if __name__ == "__main__":
    # get contents of manager_config.json
    manager_config_path = "./manager_config.json"
    if not isfile(manager_config_path):
        print("Error: manager_config.json file not in root directory.")
        sysexit()

    manager_config = jsonload(open(manager_config_path))

    # get contents of run_config.json
    run_config_path = "./run_config.json"
    if not isfile(run_config_path):
        print("Error: run_config.json file not in root directory.")
        sysexit()

    run_config = jsonload(open(run_config_path))

    manager = Manager()
