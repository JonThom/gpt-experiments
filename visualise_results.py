import json
import dash
from dash import html
import dash_react_force_graph


app = dash.Dash(
    __name__
)

graphData = json.loads()

app.layout = html.Div(
    dash_react_force_graph.Graph2D(
        id='graph2D',
        graphData=graphData,
        heightRatio=0.8,
        nodeId="id",
        linkId="id",
        linkSource="__source",
        linkTarget="__target",
        nodeLabel="label",
        linkLabel="label",
        backgroundColor="#030039"
    )
)

if __name__ == '__main__':
    app.run_server(debug=True)
