import json
import os
import pickle
import sys
import uuid
import docker

# https://github.com/FNNDSC/swarm/blob/master/swarm.py

class Manager(object):
    def __init__(self, manager_config, run_config):
        #   manager config parsing
        # concurrent_workers
        if manager_config['concurrent_workers'] < 1:
            print("Error: manager_config.json's concurrent_workers cannot be less than 1")
            sys.exit()
        self.concurrent_workers = manager_config['concurrent_workers']

        # entry_point
        root_path = os.path.dirname(os.path.realpath(__file__))
        src_path = os.path.join(root_path, "src")
        container_entry_path = os.path.join(src_path, manager_config['entry_path'])
        if not os.path.isfile(container_entry_path):
            print("Error: no entry_point file in src directory")
            sys.exit()
        self.entry_path = manager_config['entry_path']

        # save_path
        if not manager_config['save_path'].endswith('.pk'):
            print("Error: save_path must be pickle type (.pk)")
            sys.exit()
        self.save_path = os.path.join(root_path, manager_config['save_path'])


        self.config_hash = str(uuid.uuid5(uuid.NAMESPACE_OID, str(run_config)))
        self.state = {"config_hash": self.config_hash}

        self.docker_client = docker.from_env()
        run_hashes = [x["hash"] for x in run_config]
        self.execute_config(run_hashes)

    def execute_config(self, run_hashes):
        self.get_state()

        # check if all configs are finished
        self.config_count = len(run_hashes)
        if len(self.state["finished"]) == self.config_count:
            print("Manager: run_config has been completed. Delete " + str(self.save_path) + " to re-run.")
            sys.exit()

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
                self.create_containers(series_hash_list)
                self.state["running"].extend(series_hash_list)

    def get_state(self):
        # check for persisted manager data
        if os.path.isfile(self.save_path):
            save_file = open(self.save_path, 'rb')
            save_state = pickle.load(save_file)
            save_file.close()
            # if pickled data is associated with this run config, use it
            if save_state["config_hash"] == self.state["config_hash"]:
                # no guarantee running jobs were complete 
                save_state["queued"].extend(save_state["running"])
                self.delete_containers(save_state["running"])

                self.state["queued"] = save_state["queued"]
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
        pickle.dump(self.state, save_file)
        save_file.close()

    def delete_state(self):
        os.remove(self.save_path)

    def create_run_image(self):
        self.docker_client.images.build(path = "./", tag=self.config_hash)

    def delete_run_image(self):
        self.docker_client.images.remove(self.config_hash)

    def create_containers(self, hash_list):
        for series_hash in hash_list:
            self.create_container(series_hash)

    def create_container(self, series_hash):
        self.delete_container(series_hash)

        # create volume to persist data
        self.docker_client.volumes.create(name=series_hash)

        # create container using manager_config.json values
        self.docker_client.containers.run(image=self.config_hash, name=series_hash, entrypoint=['python', self.entry_path, series_hash], volumes={str(series_hash): {'bind': '/save', 'mode': 'rw'}}, detach=True)

    def delete_containers(self, hash_list):
        for series_hash in hash_list:
            self.delete_container(series_hash)

    def delete_container(self, series_hash):
        # remove container
        try:
            container = self.docker_client.containers.get(series_hash)
            if container.status != "exited":
                print("Warning: attempting to delete unfinished container")

            container.remove()
        except docker.errors.NotFound:
            pass
        except Exception:
            print("Error: unable to delete container")
            raise

        # remove volume used by container
        try:
            #TODO: copy contents out of volume
            volume = self.docker_client.volumes.get(series_hash)
            volume.remove()
        except docker.errors.NotFound:
            pass
        except Exception:
            print("Error: unable to delete volume")
            raise


if __name__ == "__main__":
    manager_config_path = "./manager_config.json"
    if not os.path.isfile(manager_config_path):
        print("Error: no manager_config.json file in root directory")
        sys.exit()

    manager_config = json.load(open(manager_config_path))

    run_config_path = "./run_config.json"
    if not os.path.isfile(run_config_path):
        print("Error: no run_config_path.json file in root directory")
        sys.exit()

    run_config = json.load(open(run_config_path))

    manager = Manager(manager_config, run_config)
