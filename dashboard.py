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
from dash.dependencies import Output,Input
from dash import dcc
from dash import html
from pymongo import MongoClient

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
app = dash.Dash()
app.layout = html.Div([
    html.H2("Change the value in the text box to see callbacks in action!"),
    html.Div([
        "Input: ",
        dcc.Input(id='my-input', value='initial value', type='text')
    ]),
    html.Br(),
    html.Div(id='my-output'),
    html.H2('Live Twitter Sentiment'),
    dcc.Graph(id='new-tweet-score', animate=True),
    dcc.Interval(
        id='graph-update',
        interval=1000 #millisec
    ),
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
    Output(component_id='my-output', component_property='children'),
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

if __name__ == '__main__':
    # TODO: find a better solution
    SLEEP_TIME = 10
    print(f"Waiting {SLEEP_TIME}s for services to start...")
    sleep(SLEEP_TIME)
    print("Starting ...")

    try:
        thread = Consumer()
        thread.start()
        app.run_server(debug=True, host="0.0.0.0", port=args.port)
    except KeyboardInterrupt:
        print("Stopping")
    finally:
        Consumer.consumer_stop.set()
