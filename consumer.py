from scorer import Scorer

import json

from kafka import KafkaConsumer
from pymongo import MongoClient
from time import sleep

# TODO: find a better solution
SLEEP_TIME = 10
print(f"Waiting {SLEEP_TIME}s for services to start...")
sleep(SLEEP_TIME)
print("Starting ...")

# Connect to MongoDB
mongoclient = MongoClient(host=['mongo_server:27017'])
db = mongoclient.twitto

# Setup Kafka consumer
consumer = KafkaConsumer(
    'twitto',
    bootstrap_servers=['kafka_server:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

# Scorer definition
s = Scorer()

# Main loop
try:
    print("Going into the try")
    for message in consumer:
        print('into the loop')
        # get tweet
        tweet = message.value
        # add score
        c_score = s.score(tweet["text"])
        tweet["score"] = c_score
        
        # save in mongodb
        result = db.test.insert_one(tweet)
        print(f'Inserted {result.inserted_id} with score {c_score}')
except:
    print("got execption")