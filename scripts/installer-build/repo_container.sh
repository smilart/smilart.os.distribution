#! /bin/bash

#apt-get install docker.io, lxctl
set -vx

SCM="git@bitbucket.org:smilart"
PORT="5000"

declare -A CONT
CONT[smilart_base]="1.0"
CONT[java]="1.7u60"
CONT[zookeeper]="3.4.6"
CONT[osgi]="4.4.1"
CONT[mongodb]="2.4.10"
CONT[rabbitmq]="3.3.5-1"
CONT[service]="1.0"
CONT[samba]="1.0"
CONT[openvpn]="2.2.1-1"

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

docker run --rm -v /usr/local/bin:/target --name="nsenter" jpetazzo/nsenter

git clone $SCM/docker.smilart_base.git
docker build --rm=true --tag="localhost:5000/smilart_base:${CONT[smilart_base]}" ./docker.smilart_base
docker tag localhost:5000/smilart_base:${CONT[smilart_base]} localhost:5000/smilart_base:latest

echo "Release container docker-registry version 1.0"
git clone $SCM/docker-registry.git
(cd ./docker-registry &&  git fetch origin && git checkout --track origin/repos)

docker build --rm=true --tag="smilart/repos:1.0" ./docker-registry
docker tag smilart/repos:1.0 smilart/repos:latest
docker run -d -p 5000:5000 -p 55556:55556 --name="smilart_repo" smilart/repos

docker-enter smilart_repo netstat -anp |grep 5000 |grep python
while [ $? -ne 0 ]; do
    sleep 3
    docker-enter smilart_repo netstat -anp |grep 5000 |grep python
done

docker push localhost:5000/smilart_base

for K in "${!CONT[@]}"; do 
    if [ $K != "smilart_base" ]; then
        echo "Release container $K version ${CONT[$K]}"
        git clone $SCM/docker.$K.git
	docker build --rm=true --tag="localhost:$PORT/$K:${CONT[$K]}" ./docker.$K/
        docker tag  localhost:$PORT/$K:${CONT[$K]} localhost:$PORT/$K:latest
	docker push localhost:$PORT/$K
    fi
done

cd ..
[[ ! -d $TARGET_DIR ]] && mkdir -pv $TARGET_DIR
docker export smilart_repo > $TARGET_DIR/repos.tar

docker stop smilart_repo
docker rm smilart_repo
docker rmi $(docker images -q)

rm -fv /usr/local/bin/*
