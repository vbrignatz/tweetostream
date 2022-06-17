import tweepy
import json
from kafka import KafkaProducer
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

parser = argparse.ArgumentParser(description='Fetch some tweets from kafka')
parser.add_argument('--kafkaport', type=int, default=9092, help="Kafka port")
parser.add_argument('--kafkahost', type=str, default="localhost", help="Kafka hostname")
parser.add_argument('--mongohost', type=str, default="localhost", help="Mongo hostname")
parser.add_argument('--mongoport', type=int, default=27017, help="Mongo port")
parser.add_argument('-t', '--topic', type=str, default="twitto", help="The name of the topic. Carefull, this should be the same in producer.py")
parser.add_argument('-k', '--key', type=str, default="emi_api", help="key to use api twitter")
parser.add_argument('query', nargs='+', type=str, help="The query to filter the tweets with.")
parser.add_argument('--fields', nargs='+', default=[], type=str)
args = parser.parse_args()


with open("secret.json", "r") as secrets:
    keys = json.load(secrets)

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])


class MyStream(tweepy.StreamingClient):
    def on_tweet(self, data):
        producer.send(args.topic, value=json.dumps(data.data).encode('utf-8'))
        print(data.id)
        return True
    
    def on_connection_error(self):
        self.disconnect()

streaming_client = MyStream(keys[f"{args.key}"]["bearer_token"])
streaming_client.add_rules(tweepy.StreamRule(' '.join(args.query)))
streaming_client.filter(tweet_fields=["created_at","text","entities"])
