import dash
import plotly
import plotly.graph_objs as go
import argparse
import threading
import json

from scorer import Scorer
from kafka import KafkaConsumer
from dash.dependencies import Output,Input
from dash import dcc
from dash import html
from pymongo import MongoClient

parser = argparse.ArgumentParser(description='Fetch some tweets and upload them in kafka')
parser.add_argument('--kafkaport', type=int, default=9092, help="Kafka port")
parser.add_argument('--kafkahost', type=str, default="localhost", help="Kafka hostname")
parser.add_argument('--mongohost', type=str, default="localhost", help="Mongo hostname")
parser.add_argument('--mongoport', type=int, default=27017, help="Mongo port")
parser.add_argument('-p', '--port', type=int, default=8085, help="Dash port")
parser.add_argument('--log', type=str, default="errors.log", help="log file")

parser.add_argument('N', type=int, default=100, help="The number of recent tweets to add in graph.")
args = parser.parse_args()

s = Scorer()

client = MongoClient(host=[f'{args.mongohost}:{args.mongoport}'])
db = client.twitto

app = dash.Dash()
app.layout = html.Div(
    [   html.H2('Live Twitter Sentiment'),
        dcc.Graph(id='new-tweet-score', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),
    ]
)


class Consumer(threading.Thread):
    consumer_stop = threading.Event()

    def __init__(self) -> None:
        super().__init__()
        self.tweet_queue = []
        self.max_size = 100

    def run(self):
        consumer = KafkaConsumer(
             "twitto",
            bootstrap_servers=[f'{args.kafkahost}:{args.kafkaport}'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
        consumer.subscribe(['twitto'])
        self.valid = 0
        self.invalid = 0

        for message in consumer:
            self.tweet_queue.append(message.value)
            if len(self.tweet_queue) > self.max_size:
                self.tweet_queue.pop(0)

            if Consumer.consumer_stop.is_set():
                break

        consumer.close()

N_tweets = []
c_tweet_id = 0

@app.callback(Output('new-tweet-score', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(input_data):
    ''' Fonction de mise à jour du graph 
    Il faut être connecté à MongoDB
    Pour être en temps réel : il faut que le 
    consummer.py soit en route ( et donc le producter.py aussi ) '''

    
    try:
        global N_tweets
        global c_tweet_id

        c_tweets = []
        for i in range(args.N):
            if len(thread.tweet_queue) > 0:
                c_tweets.append(thread.tweet_queue.pop(0))
            else:
                break

        c_tweet_id += len(c_tweets)
        N_tweets = N_tweets + c_tweets
        N_tweets = N_tweets[-args.N:]

        scores = [s.score(d["text"]) for d in N_tweets]

        data = plotly.graph_objs.Bar(
                x=[i for i in range(c_tweet_id, c_tweet_id+len(scores))],
                y=scores,
                name='Last tweets score',
                )

        return { 'data': [data],'layout' : go.Layout(
                    xaxis=dict(range=[c_tweet_id, c_tweet_id+len(scores)]),
                    yaxis=dict(range=[-10, 10]),
                    )
                }

    # Erreurs renvoyees dans le fichier errors.txt
    except Exception as e:
        with open(args.log,'a') as f:
            f.write(str(e))
            f.write('\n') 



if __name__ == '__main__':
    try:
        thread = Consumer()
        thread.start()
        app.run_server(debug=True, port=args.port)
    except KeyboardInterrupt:
        print("Stopping")
    finally:
        Consumer.consumer_stop.set()
