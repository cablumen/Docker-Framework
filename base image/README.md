# base image documentation

This folder simplifies building the containers used by my other projects (https://github.com/cablumen).
The containers used by my other repos will follow this naming scheme <github repo>:latest.
    Moving forward my github repos will only use lower-case to align with dockerhub repos.

Change the LABEL instructions and the contents of requirements.txt to generate new docker images.

Common commands
    Get list of python packages from outside running container
        docker exec <container ID> pip list

    Get list of python packages from inside running container
        docker run -it <image name>
        pip list

    Build a new image
        Navigate to this folder
        docker build -t <image name> .

    View an image's labels
        docker image inspect --format='{{json .Config.Labels}}' <image name>

    Share images to Docker Hub
        docker push -a <docker repo>:latest