from dash import Dash, dcc, html
from dash.dependencies import Input, Output

app = Dash(__name__)

app.layout = html.Div([
    html.Div(id='tweet1', style={'whiteSpace': 'pre-line'}),
    dcc.Interval(
        id='tweet-update',
        interval=1000 #millisec
    ),
    html.Div(id='tweet2', style={'whiteSpace': 'pre-line'})
])

@app.callback(
    Output('tweet1', 'children'),
    [Input('tweet-update', 'n_intervals')]
)
def update_output1(value):
    return 'place for tweet1  \n el famoso'

@app.callback(
    Output('tweet2', 'children'),
    [Input('tweet-update', 'n_intervals')]
)
def update_output2(value):
    return 'place for tweet2  \n italian'

if __name__ == '__main__':

    try:
        app.run_server(debug=True, host="0.0.0.0", port= 8085)
    except KeyboardInterrupt:
        print("Stopping")

