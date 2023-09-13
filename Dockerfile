# tensorflow base image
FROM cablumen/mnist-exploration:latest

# copy source files 
COPY /src /

# copy run_config into source for configuration fetching
COPY run_config.json / 