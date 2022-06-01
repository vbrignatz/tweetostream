import tweepy
import json
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from time import sleep

with open("secret.json", "r") as secrets:
    keys = json.load(secrets)

# TODO: find a better solution
SLEEP_TIME = 10
print(f"Waiting {SLEEP_TIME}s for services to start...")
sleep(SLEEP_TIME)
print("Starting ...")

producer = KafkaProducer(bootstrap_servers=['kafka_server:9092'])


class MyStream(tweepy.StreamingClient):
    def on_tweet(self, data):
        res = producer.send("twitto", value=json.dumps(data.data).encode('utf-8'))
        print(f"Sent {data.id} [{res}]")
        return True
    
    def on_connection_error(self):
        self.disconnect()

streaming_client = MyStream(keys["vincent_api"]["bearer_token"])

streaming_client.add_rules(tweepy.StreamRule('covid'))
streaming_client.filter(tweet_fields=["created_at", "text"])
