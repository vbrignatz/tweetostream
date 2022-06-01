# Start the servers

To start the kafka, zookeeper and mongodb services, install docker ([see here](https://docs.docker.com/get-docker/)) and run :
```
docker-compose up
```

Two port will be used on your local computer :
 - `27018` for mongodb
 - `9092`  for kafka

A volume will be set in `./data/mongo` for persistent storage 


# Program

Launch the producer with :
```
python3 producer.py
```

Launch the consumer with :
```
python3 consumer.py
```

The producer will get the latest tweets with the choosen keyword and put them in the kafka topic `twitto`.
The consumer will get the tweets from kafka, add a score reflecting the sentiment in the text, and store them in MongoDB. 