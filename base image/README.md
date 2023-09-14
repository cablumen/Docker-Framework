# base image folder

This folder simplifies building the containers used by my other projects https://github.com/cablumen.  
The containers used by my other repos will follow this naming scheme \<github repo\>:latest.  
&emsp;Moving forward my github repos will only use lower-case to align with dockerhub repos.  

#### How to build a base image

1. Change the contents of requirements.txt to match the libraries used by your project.  
2. Run **docker build -t \<image name\> .** to create a new base image.  

#### Common commands  
&emsp;Get list of python packages from outside running container  
&emsp;&emsp;docker exec \<container ID\> pip list  

&emsp;Get list of python packages from inside running container  
&emsp;&emsp;docker run -it \<image name\>  
&emsp;&emsp;pip list  

&emsp;Build a new image  
&emsp;&emsp;Navigate to this folder  
&emsp;&emsp;docker build -t \<image name\> .  

&emsp;View an image's labels  
&emsp;&emsp;docker image inspect --format='{{json .Config.Labels}}' \<image name\>  

&emsp;Share images to Docker Hub  
&emsp;&emsp;docker push -a \<docker repo\>:latest  