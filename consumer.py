from scorer import Scorer

import json
import argparse

from kafka import KafkaConsumer
from pymongo import MongoClient

parser = argparse.ArgumentParser(description='Fetch some tweets and upload them in kafka')
parser.add_argument('--kafkaport', type=int, default=9092, help="Kafka port")
parser.add_argument('--kafkahost', type=str, default="localhost", help="Kafka hostname")
parser.add_argument('--mongohost', type=str, default="localhost", help="Mongo hostname")
parser.add_argument('--mongoport', type=int, default=27017, help="Mongo port")
parser.add_argument('-t', '--topic', type=str, default="twitto", help="The name of the topic. Carefull, this should be the same in producer.py")
args = parser.parse_args()

# Connect to MongoDB
mongoclient = MongoClient(host=[f'{args.mongohost}:{args.mongoport}'])
db = mongoclient.twitto

# Setup Kafka consumer
consumer = KafkaConsumer(
    args.topic,
    bootstrap_servers=[f'{args.kafkahost}:{args.kafkaport}'],
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