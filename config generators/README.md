# config generators folder

This folder contains sampling algorithms that generate run_config.json which stores every permutation of parameters tested during hyper-parameter search.

#### How to generate a run_config.json
1. Follow the "Author a default_config.json" section in the README in the /src/ folder.  
2. Run one of the sampling algorithms such as GridSearch.py to generate a run_config.json in the root folder  
3. Refer to the contents of run_config.json to map series hashes (a unique guid for each hyper-parameter premutation) to its hyper-parameter values.  

