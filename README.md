# Docker-Framework

This repo provides a framework for machine learning hyper-parameter search that requires few dependencies and is portable and scalable to different compute providers. This framework is open-source and hosted with my other projects at https://github.com/cablumen.

#### How to use this repo

1. [Install python](https://www.python.org/downloads/). [Install docker](https://docker-py.readthedocs.io/en/stable/).  
2. Investigate the "base image" folder. Follow the README to containerize your project's dependencies in a docker image.  
3. Copy your project into the src folder.  
4. Investigate the "config generators" folder. Follow the README to author a default_config.json in the src folder. A good starting point is listing all hyper-parameters as a dict.  
5. Run one of the \<SearchAlgorithm\>.py scripts in the "config generators" folder to create a run_config.  
6. Make changes to your project so hyper-parameters are assigned to user environment variables, e.g. important_variable = os.environ[\'VARIABLE_NAME\'].  
7. Make changes to your project to write log files to the /logs/ folder in the container.  
8. In this folder, edit the Dockerfile to use your docker image and edit manager_config.json for your desired settings. See the below section for more details on manager_config.json parameters.  
9. Run Manager.py.  

#### manager_config.json parameters

&emsp;concurrent_workers: number of containers to run concurrently in parallel execution mode. Must be greater or equal to 1.  
&emsp;container_entry_point: python file to run your project.  
&emsp;post_processing_entry_point: python file to execute after iterating over every entry in run_config.json.  

#### TODO  
use correct formating for ReadMe's  
Revisit documentation  
Re-implement search algorithms for inheritence/extensibility  