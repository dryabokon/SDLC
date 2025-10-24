@echo off

set DOCKER_PORT_1=8080
set DOCKER_PORT_2=50000
set JENKINS_VOL_PATH=D:\jenkins-docker\data
set JENKINS_VOL_MOUNT=/var/jenkins_home
set CONTAINER_NAME=jenkins
set IMAGE_NAME=jenkins:latest
set CODEBASE_PATH=D:\source\digits\a_demo_codebase

docker run -d ^
-p %DOCKER_PORT_1%:%DOCKER_PORT_1% ^
-p %DOCKER_PORT_2%:%DOCKER_PORT_2% ^
-v %JENKINS_VOL_PATH%:%JENKINS_VOL_MOUNT% ^
-v %CODEBASE_PATH%:/workspace ^
--name %CONTAINER_NAME% ^
%IMAGE_NAME%

rem docker exec -it %CONTAINER_NAME% cat %JENKINS_VOL_MOUNT%/secrets/initialAdminPassword