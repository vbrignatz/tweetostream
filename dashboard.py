import dash
from dash.dependencies import Output,Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from pymongo import MongoClient
import pandas as pd
import math
from numpy import nan
from scorer import Scorer


mongoclient = MongoClient(port=27017)
db = mongoclient.twitto


app = dash.Dash()
app.layout = html.Div(
    [   html.H2('Live Twitter Sentiment'),
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*100000
        ),
        html.H2("Change the value in the text box to see callbacks in action!"),
    html.Div([
        "Input: ",
        dcc.Input(id='my-input', value='initial value', type='text')
    ]),
    html.Br(),
    html.Div(id='my-output'),
     html.H2('Live Twitter by Country'),
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update2',
            interval=1*100000
        ),
    ]
)

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])

def update_graph_scatter(input_data):
    ''' Fonction de mise à jour du graph 
    Il faut être connecté à MongoDB
    Pour être en temps réel : il faut que le 
    consummer.py soit en route ( et donc le producter.py aussi ) '''
    
    try:


        #Creation de la requete de selection des enregistremetns sur la base mongodb.test
        df = pd.DataFrame(list(db.test.find()))
        df = df.dropna(subset=['score'])

        df["id"] = pd.to_numeric(df["id"])

        df.sort_values('id', inplace=True)

        # rolling : mise à l'échelle des identifiants pour plus de visibilité
        df['id'] = df['id'].rolling(int(len(df)/5)).mean()
        #df['score'] = df['score'].rolling(int(len(df)/5)).mean()
    
        # Nos axes prennent en comptes les 100 dernieres valeurs
        X = df.id.values[-100:] 
        Y = df.score.values[-100:]
        #afficher un tableau sur plotly affichant les 3 derniers textes
        tableau = df.text.values[-3:]

        data = plotly.graph_objs.Scatter(
                x= list(X),
                y= list(Y),
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[min(Y),max(Y)]),)}

    #Erreurs renvoyees dans le fichier errors.txt
    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n') 
s = Scorer()
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

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update2', 'n_intervals')])

def update_graph_scatter2(input_data):
    ''' Fonction de mise à jour du graph 
    Il faut être connecté à MongoDB
    Pour être en temps réel : il faut que le 
    consummer.py soit en route ( et donc le producter.py aussi ) '''
    
    try:


        #Creation de la requete de selection des enregistremetns sur la base mongodb.test
        df = pd.DataFrame(list(db.test.find()))
        df = df.dropna(subset=['score'])

        df["id"] = pd.to_numeric(df["id"])

        df.sort_values('id', inplace=True)

        # rolling : mise à l'échelle des identifiants pour plus de visibilité
        df['id'] = df['id'].rolling(int(len(df)/5)).mean()
        #df['score'] = df['score'].rolling(int(len(df)/5)).mean()
    
        # Nos axes prennent en comptes les 100 dernieres valeurs
        X = df.id.values[-100:] 
        Y = df.score.values[-100:]
        #afficher un tableau sur plotly affichant les 3 derniers textes
        tableau = df.text.values[-3:]

        data = plotly.graph_objs.Scatter(
                x= list(X),
                y= list(Y),
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[min(Y),max(Y)]),)}

    #Erreurs renvoyees dans le fichier errors.txt
    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n') 
        
#format de la date pur recupper date et heure et seconde dans un dataframe
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
if __name__ == '__main__':
    app.run_server(debug=True,port=8052)
