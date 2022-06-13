import dash
import plotly
import plotly.graph_objs as go
import argparse

from time import sleep
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

# Connection to mongoDB 
client = MongoClient(host=[f'{args.mongohost}:{args.mongoport}'])
db = client.twitto

# Definition of Dash app
app = dash.Dash()
app.layout = html.Div([
    html.H2('My histogram'),
    dcc.Graph(id='histogram', animate=True),
    dcc.Interval(
        id='hist-update',
        interval=1000 #millisec
    ),
    ]
)

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

if __name__ == '__main__':

    try:
        app.run_server(debug=True, host="0.0.0.0", port= 8085)
    except KeyboardInterrupt:
        print("Stopping")

