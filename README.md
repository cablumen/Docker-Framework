# Docker-Framework

This repo provides a framework for machine learning hyper-parameter search that requires few dependencies and is portable and scalable to different compute providers. This framework is open-source and hosted with my other projects at https://github.com/cablumen.  

### How to use

0. \[Windows\] [Install wsl](https://learn.microsoft.com/en-us/windows/wsl/install).  
1. [Install python](https://www.python.org/downloads/). [Install docker](https://docker-py.readthedocs.io/en/stable/).  
2. Run \\config generator\\RunConfigGenerator.py then Manager.py to run example demo.  
3. Delete example files (MNIST.py, PostProcessing.py) and then copy your project into the src folder.  
4. Investigate the \\base image\\ folder. Follow the README to containerize your project's dependencies in a docker image.  
5. Follow the "Author a default_config.json" section of the README in the \\src\\ folder.  
6. Follow the "How to generate a run_config.json" section of the README in the \\config generator\\ folder.  
7. Follow the "Project integration" section of the README.md in the \\src\\ folder.  
8. Edit the Dockerfile in this folder to use your docker image and update manager_config.json to your desired settings. See the below section for more details on manager_config.json parameters.  
9. Run Manager.py.  

### manager_config.json parameters

&emsp;concurrent_workers: number of containers to run concurrently. Int type \>= 1.  
&emsp;container_entry_path: relative filepath from \\src\\ folder to python file that is run after container creation. Str type.  
&emsp;post_run_entry_path: relative filepath from \\src\\ folder to python file that is run after all containers have completed. Str type.  
&emsp;rerun_completed_configs: whether to rerun configurations that have fully completed. Bool type.  
&emsp;use_gpus: whether to allow docker containers to access all gpu resources. Bool type.  

### TODO  

Better documentation for RunConfigGenerator.py  
Maybe integrate RunConfigGenerator into Manager.py?  
    This simplifies things for users although we need some sort of mechanism whether to choose new run_config or saved state   
More robust implementations of sampling algorithms  