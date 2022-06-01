from scorer import Scorer

import json

from kafka import KafkaConsumer
from pymongo import MongoClient

# Connect to MongoDB
mongoclient = MongoClient(host=['localhost:27018'])
db = mongoclient.twitto

# Setup Kafka consumer
consumer = KafkaConsumer(
    'twitto',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

# Scorer definition
s = Scorer()

# Main loop
for message in consumer:
    # get tweet
    tweet = message.value
    # add score
    c_score = s.score(tweet["text"])
    tweet["score"] = c_score
    
    # save in mongodb
    result = db.test.insert_one(tweet)
    print(f'Inserted {result.inserted_id} with score {c_score}')