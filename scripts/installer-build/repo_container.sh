#! /bin/bash

#apt-get install docker.io
set -vx

SCM="git@bitbucket.org:smilart"
PORT="5000"

declare -A CONT
CONT[docker.smilart_base]="1.0"
CONT[docker.java]="1.7u60"
CONT[docker.zookeeper]="3.4.6"
CONT[docker.osgi]="4.4.1"
CONT[docker.mongodb]="2.4.10"
CONT[docker.rabbitmq]="3.3.5-1"
CONT[docker.service]="1.0"
CONT[docker.samba]="1.0"

if [ -z "$1" ]; then
    BUILD_DIR="docker"
else
    BUILD_DIR=$1
fi

if [ -z "$2" ]; then
    TARGET_DIR="chroot/var/lib/smilart_srv/repos"
else
    TARGET_DIR=$2
fi

[[ -d $BUILD_DIR ]] && rm -rfv $BUILD_DIR
mkdir $BUILD_DIR && cd $BUILD_DIR

echo "Release conteiner docker-registry version 1.0"
git clone git@github.com:smilart/docker-registry.git
git checkout tags/0.8.0

docker build --rm=true --tag="localhost:5000/repos:1.0" ./docker-registry
docker tag localhost:5000/repos:1.0 localhost:5000/repos:latest
docker run -d -p 5000:5000 --name="main_container" localhost:5000/repos

for K in "${!CONT[@]}"; do 
    echo "Release conteiner $K version ${CONT[$K]}"
    git clone $SCM/$K.git
    docker build --rm=true --tag="localhost:$PORT/$K:${CONT[$K]}" ./$K/
    docker tag  localhost:$PORT/$K:${CONT[$K]} localhost:$PORT/$K:latest
    docker push localhost:$PORT/$K
done

cd ..
[[ ! -d $TARGET_DIR ]] && mkdir -pv $TARGET_DIR
docker export main_container > $TARGET_DIR/repos.tar

docker stop main_container
docker rm main_container
docker rmi $(docker images -q)

