# tensorflow base image
FROM cablumen/mnist-exploration:latest

# copy source files
COPY /src /

# copy run_config
COPY run_config.json / 
