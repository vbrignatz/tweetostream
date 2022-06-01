import dash
import plotly
import plotly.graph_objs as go

from dash.dependencies import Output,Input
from dash import dcc
from dash import html
from pymongo import MongoClient

client = MongoClient(host=["localhost:27017"])
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

@app.callback(Output('new-tweet-score', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(input_data):
    ''' Fonction de mise à jour du graph 
    Il faut être connecté à MongoDB
    Pour être en temps réel : il faut que le 
    consummer.py soit en route ( et donc le producter.py aussi ) '''

    N_TWEETS = 100
    
    try:
        # Nos axes prennent en comptes les N derniers tweets
        query = db.test\
            .find({}, {"score":1})\
            .sort("id")\
            .limit(N_TWEETS)
    
        data = plotly.graph_objs.Bar(
                x=[i for i in range(N_TWEETS)],
                y=[i['score'] for i in query],
                name='Last tweets score',
                )

        return { 'data': [data],'layout' : go.Layout(
                    xaxis=dict(range=[0,N_TWEETS]),
                    yaxis=dict(range=[-10, 10]),
                    )
                }

    #Erreurs renvoyees dans le fichier errors.txt
    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n') 



if __name__ == '__main__':
    app.run_server(debug=True, port=6969)
