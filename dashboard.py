import dash
import plotly
import plotly.graph_objs as go

from time import sleep
from dash.dependencies import Output,Input
from dash import dcc
from dash import html

import numpy as np

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
        X = np.random.randn(500)

        # plotting data
        data = plotly.graph_objs.Histogram(
                x = X 
                )

        return { 'data': [data],'layout' : go.Layout()
                }
        
    # Erreurs renvoyees dans le fichier log
    except Exception as e:
        with open('error.txt','a') as f:
            f.write(str(e))
            f.write('\n') 

if __name__ == '__main__':

    try:
        app.run_server(debug=True, host="0.0.0.0", port= 6969)
    except KeyboardInterrupt:
        print("Stopping")

