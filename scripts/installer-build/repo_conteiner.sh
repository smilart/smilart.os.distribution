#! /bin/bash

git clone git@github.com:smilart/docker-registry.git

docker-registry (1.0)
docker build --rm=true --tag="localhost:5000/repos:1.0" ./docker-registry
docker tag localhost:5000/repos:1.0 localhost:5000/repos:latest
docker run -d -p 5000:5000 --name="main_container" repos


docker.smilart_base (1.0)
docker.java (1.7u60)
docker.zookeeper (3.4.6)
docker.osgi (4.4.1)

docker.mongodb (2.4.10)
docker.rabbitmq (3.3.5-1)

docker.service (1.0)
docker.samba (1.0)

git clone ....
docker build --rm=true --tag="localhost:5000/smilart_base:1.0" ./docker.smilart_base/
docker tag  localhost:5000/smilart_base:1.0 localhost:5000/smilart_base:latest
docker push localhost:5000/smilart_base


docker export main_container > /tmp/repos.tar

docker stop main_container
docker rm main_container
docker rmi $(docker images -q)




