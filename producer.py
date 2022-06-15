import tweepy
import json
import argparse

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from time import sleep

TWEET_FIELDS=[
    "created_at",
    "text",
    "lang",
    "entities",
    # "retweet_count",
]

# Argument parsing
parser = argparse.ArgumentParser(description='Fetch some tweets and upload them in kafka')
parser.add_argument('--port', type=int, default=9092, help="Kafka port")
parser.add_argument('--host', type=str, default="localhost", help="Kafka hostname")
parser.add_argument('--secret', type=str, default="secret.json", help="The secret file containing the bearer token")
parser.add_argument('-t', '--topic', type=str, default="twitto", help="The name of the topic. Carefull, this should be the same in consumer.py")
parser.add_argument('query', nargs='+', type=str, help="The query to filter the tweets with.")
parser.add_argument('--fields', nargs='+', default=[], type=str)
args = parser.parse_args()

# loading api keys
with open(args.secret, "r") as secrets:
    keys = json.load(secrets)

# Producer init
SLEEP_TIME = 5
broker_av = False
while not broker_av :
    try:
        producer = KafkaProducer(bootstrap_servers=[f'{args.host}:{args.port}'])
        broker_av = True 
    except NoBrokersAvailable as e:
        print(f"{e}. Retry in {SLEEP_TIME}s")
        sleep(SLEEP_TIME)

# Create child class or tweepy Streaming Client
class MyStream(tweepy.StreamingClient):
    def on_tweet(self, data):
        res = producer.send(args.topic, value=json.dumps(data.data).encode('utf-8')) # TODO: ERROR HANDELING
        print(f"Sent {data.id} [{res}]")
        return True
    
    def on_connection_error(self):
        self.disconnect()

# Launching the streaming client
streaming_client = MyStream(keys["justine_api"]["bearer_token"])
streaming_client.add_rules(tweepy.StreamRule(' '.join(args.query)))
streaming_client.filter(tweet_fields=TWEET_FIELDS + args.fields)
