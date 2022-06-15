# Usage

## Docker
You first need to install docker ([see here](https://docs.docker.com/get-docker/)).

## Build and run

To build the app, use
```
docker compose -f docker/docker-compose.yml up --build
```

This will build the containers and launch them.

This will launch the kafka, zookeeper and mongodb containers as well as the producer, spark-db-saver and dashboard container.

You can connect to the mongo database on the port `27018`.
A volume will be set in `./data/mongo` for persistent storage 

## Program

The producer will get the latest tweets with the choosen keyword and put them in the kafka topic `twitto`.
The consumer will get the tweets from kafka, add a score reflecting the sentiment in the text, and store them in MongoDB. 