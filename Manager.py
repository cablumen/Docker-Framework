import json
import docker
import os
import sys

# https://github.com/FNNDSC/swarm/blob/master/swarm.py

class Manager(object):
    def __init__(self, manager_config, run_config):
        if manager_config['concurrent_workers'] < 1:
            print("Error: manager_config.json's concurrent_workers cannot be less than 1")
            sys.exit()
        self.concurrent_workers = manager_config['concurrent_workers']

        root_path = os.path.dirname(os.path.realpath(__file__))
        src_path = os.path.join(root_path, "src")
        container_entry_path = os.path.join(src_path, manager_config['container_entry_point'])
        if not os.path.isfile(container_entry_path):
            print("Error: no container_entry_point file in src directory")
            sys.exit()
        self.container_entry_point = manager_config['container_entry_point']

        post_processing_entry_path = os.path.join(src_path, manager_config['post_processing_entry_point'])
        if not os.path.isfile(post_processing_entry_path):
            print("Error: no post_processing_entry_point file in src directory")
            sys.exit()
        self.post_processing_entry_point = manager_config['post_processing_entry_point']

        self.docker_client = docker.from_env()
        self.execute_config(run_config)

    def execute_config(self, run_config):
        queued_series = run_config
        running_series = []
        
        while len(queued_series) != 0:
            series_to_run = queued_series.pop(0)
            running_series.append(self.execute_series(series_to_run))

    def execute_series(self, series_config):
        # create container using Dockerfile

        # copy over the series_config

        # tell it to run and return some obj to monitor state
        pass

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