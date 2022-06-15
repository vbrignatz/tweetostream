from turtle import width
import dash
import plotly
import plotly.graph_objs as go
import argparse
import threading
import json
import datetime

from time import sleep
from scorer import Scorer
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from dash.dependencies import Output,Input
from dash import dcc
from dash import html
from pymongo import MongoClient
import dash_bootstrap_components as dbc

# Argument parsing
parser = argparse.ArgumentParser(description='Fetch some tweets and upload them in kafka')
parser.add_argument('--kafkaport', type=int, default=9092, help="Kafka port")
parser.add_argument('--kafkahost', type=str, default="localhost", help="Kafka hostname")
parser.add_argument('--mongohost', type=str, default="localhost", help="Mongo hostname")
parser.add_argument('--mongoport', type=int, default=27017, help="Mongo port")
parser.add_argument('-t', '--topic', type=str, default="twitto", help="The name of the topic. Carefull, this should be the same in producer.py")
parser.add_argument('-p', '--port', type=int, default=8085, help="Dash port")
parser.add_argument('--log', type=str, default="errors.log", help="log file")

parser.add_argument('N', type=int, default=100, help="The number of recent tweets to add in graph.")
args = parser.parse_args()

# Scorer definition
s = Scorer()

# Connection to mongoDB 
client = MongoClient(host=[f'{args.mongohost}:{args.mongoport}'])
db = client.twitto

# Definition of Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.SKETCHY])
app.layout = html.Div(
    [
        dbc.Row(
            [
            dbc.Col(
                html.Div("Tweets dentiments about covid"),
                width=12)
            ]
        ),
        dbc.Row(
            [
            dbc.Col(
                children = [
                    html.Div(id='my-output-graph'),
                    html.H2('Live Twitter Sentiment'),
                    dcc.Graph(id='new-tweet-score', animate=True),
                    dcc.Interval(
                            id='graph-update',
                            interval=1000 #millisec
                        ),
                    ], 
                width=12,
                style={"border":"2px black solid"}
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    children = [
                        html.Div(id='my-output-histo'),
                        html.H2('My histogram'),
                        dcc.Graph(id='histogram', animate=True),
                        dcc.Interval(
                            id='hist-update',
                            interval=20000 #millisec
                        ),
                    ],
                    width=6,
                    style={"border":"2px black solid"}
                    ),
                dbc.Col(
                    children = [
                        html.H2('Feeds'),
                        html.Div(id='tweet1', style={'whiteSpace': 'pre-line'}),
                        html.Div(id='tweet2', style={'whiteSpace': 'pre-line'}),
                        dcc.Interval(
                            id='tweet-update',
                            interval=5000 #millisec
                        ),
                        ],
                    width=6,
                    style={"border":"2px black solid"}
                    )
            ]
        )
    ]
)

# Class Consumer to run in background thread
class Consumer(threading.Thread):
    consumer_stop = threading.Event()

    def __init__(self) -> None:
        super().__init__()
        # the real time queue containing the lastest tweets
        self.tweet_queue = []
        self.max_queue_size = 100

        # queue containing tweets from start_time to end_time
        self.recent_tweets = []

        self.end_time = datetime.datetime.now()
        self.history_time = args.N # seconds
        self.start_time = datetime.datetime.now() - datetime.timedelta(seconds=self.history_time)


    def update(self):
        # take the content of tweet_queue
        self.recent_tweets, self.tweet_queue = self.recent_tweets + self.tweet_queue, []

        # update current time
        self.end_time = self.recent_tweets[-1]["datetime"]
        self.start_time = self.end_time - datetime.timedelta(seconds=self.history_time)

        # delete old data
        for i in range(len(self.recent_tweets)):
            if self.recent_tweets[i]["datetime"] > self.start_time:
                break
        self.recent_tweets = self.recent_tweets[i:]

        # return recent tweets
        return self.recent_tweets

    def run(self):
        # function ran by thread

        # init consumer
        consumer = KafkaConsumer(
            args.topic,
            bootstrap_servers=[f'{args.kafkahost}:{args.kafkaport}'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )

        # main loop
        for message in consumer:
            
            tweet = message.value
            # adding datetime
            tweet["datetime"] = datetime.datetime.strptime(tweet["created_at"], '%Y-%m-%dT%H:%M:%S.000Z') # 2022-05-31T13:30:48.000Z

            # adding to queue
            self.tweet_queue.append(tweet)
            # freeing space if needed
            if len(self.tweet_queue) > self.max_queue_size:
                self.tweet_queue.pop(0)

            if Consumer.consumer_stop.is_set():
                break

        consumer.close()

@app.callback(Output('new-tweet-score', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(input_data):
    ''' Fonction de mise à jour du graph 
    Il faut être connecté à MongoDB
    Pour être en temps réel : il faut que le 
    consummer.py soit en route ( et donc le producter.py aussi ) '''

    try:
        # get latest tweets
        tweets = thread.update()

        # setup axis
        X = [t["datetime"] for t in tweets]
        Y = [s.score(t["text"]) for t in tweets]

        # plotting data
        data = plotly.graph_objs.Scatter(
                x = X ,
                y = Y ,
                name = 'Scatter',
                mode = 'markers'
                )

        return { 'data': [data],'layout' : go.Layout(
                    xaxis=dict(range=[thread.start_time, thread.end_time]),
                    yaxis=dict(range=[-20, 20]),
                    )
                }

    # Erreurs renvoyees dans le fichier log
    except Exception as e:
        with open(args.log,'a') as f:
            f.write(str(e))
            f.write('\n') 

@app.callback(
    Output(component_id='my-output-graph', component_property='children'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    try:
        
        tweet = str(input_value)
        # add score
        c_score = s.score(tweet)
        return 'The sentiment score of the tweet is {}'.format(c_score)
        
        # save in mongodb
        #return print(f'result {result.inserted_id} with score {c_score}')
    except:
        return "Error, the input is not a tweet"

@app.callback(Output('histogram', 'figure'),
              [Input('hist-update', 'n_intervals')])   
def update_graph_histo(input_data):
    ''' Fonction de mise à jour de l'histogramme
    Il faut être connecté à MongoDB
    Pour être en temps réel : il faut que le 
    consummer.py soit en route ( et donc le producter.py aussi ) '''

    try:

        # setup axis
        X = [el["score"] for el in list(db.test.find({}, {"score":1 , '_id' : 0}))]

        # plotting data
        data = plotly.graph_objs.Histogram(
                x = X 
                )

        return { 'data': [data] #,'layout' : go.Layout()
                }
        
    # Erreurs renvoyees dans le fichier log
    except Exception as e:
        with open('error.txt','a') as f:
            f.write(str(e))
            f.write('\n') 

@app.callback(
    Output('tweet1', 'children'),
    [Input('tweet-update', 'n_intervals')]
)
def update_output1(value):
    text = "no tweet yet"
    if len(thread.recent_tweets) > 1:
        text = thread.recent_tweets[-1]["text"]
    return text

@app.callback(
    Output('tweet2', 'children'),
    [Input('tweet-update', 'n_intervals')]
)
def update_output2(value):
    text = "no tweet yet"
    if len(thread.recent_tweets) > 2:
        text = thread.recent_tweets[-2]["text"]
    return text

if __name__ == '__main__':

    SLEEP_TIME = 5
    broker_av = False
    while not broker_av :
        try:
            _ = KafkaConsumer(
                args.topic,
                bootstrap_servers=[f'{args.kafkahost}:{args.kafkaport}']
                )
            broker_av = True 
        except NoBrokersAvailable as e:
            print(f"{e}. Retry in {SLEEP_TIME}s")
            sleep(SLEEP_TIME)

    try:
        thread = Consumer()
        thread.start()
        app.run_server(debug=True, host="0.0.0.0", port=args.port)
    except KeyboardInterrupt:
        print("Stopping")
    finally:
        Consumer.consumer_stop.set()
