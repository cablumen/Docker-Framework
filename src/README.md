# src folder

This folder will contain your project code, your authored default_config.json, and the in-box config.py.  
Any files persisted from docker containers will be stored in the logs folder with the folder structure: /logs/\<run_hash\>/\<series_hash\>/  

### Author a default_config.json

The default_config.json is a dictionary that defines the set of values to test for each hyper-parameter. See the in-box default_config.json as an example.  

1. Determine the list of hyper-parameters. This list will be specific to your project but might include things like batch_size, learning_rate, or neuron count.  
2. Think about the correct number and distribution of samples for each hyper-parameter.  
3. Explore the /config generators/ folder and determine the sampling algorithm that mosts aligns with the planned sampling distribution of each hyper-parameter.  
4. Create a file called default_config.json in this folder with an empty dict or edit an existing default_config.json.  
5. Add "key":value pairs to the dict where the key is the hyper-parameter name and the value is the list of parameters passed to the sampling algorithm. Each sampling algorithm requires different parameters so check the module docustring of \<Sampling Algorithm\>.py for the correct syntax.  
&emsp;Note: currently only grid-search is supported but I plan on adding more sampling algorithms in the future.  

### Project integration

In order to fully take advantage of this framework, some integration changes are necessary.  
1. Replace hyper-parameter delcarations with calls to config.py's to fetch environmental variables. See in-box MNIST.py for an example.  
2. If there are any files you want to persist, make sure they are written to the ./logs/ folder within the container.  
3. If you wish to run some data-processing logic after hyper-parameter search has completed, make sure it's implemented to traverse the file structure of the logs folder.  
