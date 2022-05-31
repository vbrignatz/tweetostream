import tweepy
import json
from kafka import KafkaProducer

with open("secret.json", "r") as secrets:
    keys = json.load(secrets)

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])


class MyStream(tweepy.StreamingClient):
    def on_tweet(self, data):
        producer.send("twitto", value=json.dumps(data.data).encode('utf-8'))
        print(data.id)
        return True
    
    def on_connection_error(self):
        self.disconnect()

streaming_client = MyStream(keys["vincent_api"]["bearer_token"])

streaming_client.add_rules(tweepy.StreamRule('covid'))
streaming_client.filter(tweet_fields=["created_at", "text"])
