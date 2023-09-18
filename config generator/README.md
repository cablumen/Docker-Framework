# config generator folder

This folder contains sampling algorithms that generate run_config.json. run_config.json stores every permutation of parameters tested during hyper-parameter search.  

### How to generate a run_config.json

1. Follow the "Author a default_config.json" section in the README in the \\src\\ folder.  
2. Run RunConfigGenerator.py to generate a run_config.json in the repo root folder  
3. Refer to the contents of run_config.json to map series hashes (a unique guid for each hyper-parameter premutation) to its hyper-parameter values.  

### Sampling algorithms and parameters

&emsp;nominal: a sample list without numerical ordering or meaning i.e. \["donkey", "cow", "pig"\]  
&emsp;&emsp;args: a variadic argument. Any type(s), any length.  

&emsp;arithmetic: a sample list with a constant difference between subsequent samples. a~n+1~-a~n~=c.  
&emsp;&emsp;(parm1) start: first value to sample. Int or float type.  
&emsp;&emsp;(parm2) end: last value to sample. Inclusive if sampled by sequence. Int or float type.  
&emsp;&emsp;(parm3) step: constant difference between subsequent samples. Int or float type != 0  

&emsp;geometric: a sample list with a constant ratio between subsequent samples. \(a~n+1~/a~n~\)=c.  
&emsp;&emsp;(parm1) start: first value to sample. Int or float type.  
&emsp;&emsp;(parm2) end: last value to sample. Inclusive if sampled by sequence. Int or float type.  
&emsp;&emsp;(parm3) ratio: constant multiplicative ratio between subsequent samples. Int or float type > 0  

&emsp;interval: a sample list with n samples per order of magnitude.  
&emsp;&emsp;(parm1) start: first order of magnitude. -3 for thousandth, 2 for hundred, etc. Int type.  
&emsp;&emsp;(parm2) end: last order of magnitude. Inclusive of first value in last order of magnitude. Int type.  
&emsp;&emsp;(parm3) samples: number of equal distance samples within an order of magnitude. Int type >= 1.  
