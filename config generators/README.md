# Config Generators

This folder allows for the generation of run_config.json which stores the complete list of parameters iterated over by the docker manager. To use a config generator, create and populate a default_confg.json in the src folder and then run one of the search algorithm scripts such as GridSearch.py.  

Generating a run_config.json requires two files:  
&emsp;default_config.json: is a json file of nested dictionaries found in the src folder. Each leaf node in the dictionary defines a configuration setting. If the leaf node is non-iterable (i.e. "config_name": value), then that configuration will be identical for all containers. If the leaf node is a list (i.e. "config_name": [parameter1, parameter2, ..., parameterN]), then the contents of the list will be used as parameters to the search algorithm to generate a range of configuration settings.  
&emsp;\<SearchAlgorithm\>.py: a python script that parses default_config.json and generates run_config.json.  
&emsp;&emsp;GridSearch: an implementation of the grid-search strategy. Iterable parameters should follow the syntax "config_name": [start_value, end_value, step]. Floats or ints are acceptable types for parameters.  
