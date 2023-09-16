# tensorflow base image
FROM tensorflow/tensorflow:latest-gpu

# image labels
LABEL maintainer="https://github.com/cameronblumenthal"
LABEL version="1.0"
LABEL base.image="tensorflow/tensorflow:latest-gpu"
LABEL base.image.maintainer="NVIDIA CORPORATION <cudatools@nvidia.com>"

# copy and install python packages
COPY requirements.txt /tmp/

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r /tmp/requirements.txt
