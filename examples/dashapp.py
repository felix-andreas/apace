# -*- coding: utf-8 -*-
import elements as el
from elements.linbeamdyn import Latticedata, twissdata
from elements.plotting import getTwissFigure
import numpy as np

D1 = el.Drift('D1', length=0.55)
Q1 = el.Quad('Q1', length=0.2, k1=1.2)
B1 = el.Bend('B1', length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
Q2 = el.Quad('Q2', length=0.4, k1=-1.2)
FODO = el.Line('fodo-cell', [Q1, D1, B1, D1, Q2, D1, B1, D1, Q1])
interFODO = el.Line('inter-Fodo', [FODO] * 10)
ring = el.Mainline('fodo-ring', [FODO]*8)

latticedata = Latticedata(ring)
twiss = twissdata(latticedata)
fig = getTwissFigure(twiss, ring)

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly

# plotly.offline.plot(fig, 'offline')
# exit()


app = dash.Dash()

markdown_text = '''
### Dash and Markdown

Dash apps can be written in Markdown.
Dash uses the [CommonMark](http://commonmark.org/)
specification of Markdown.
Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
if this is your first introduction to Markdown!
'''

app.layout = html.Div(children=[
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center'
        }
    ),
    html.Button('Set betax to 1', id='button'),
    html.Button('print betax', id='button2'),
    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center'
    }),
    html.Label('Multi-Select Dropdown'),
    dcc.Dropdown(
        options=[
            {'label': 'New York City', 'value': 'NYC'},
            {'label': u'Montréal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        value=['MTL', 'SF'],
        multi=True
    ),

    dcc.Graph(id='example-graph', figure=fig),
    dcc.Markdown(children=markdown_text),
    html.P(id='placeholder', children='nope'),
    html.P(id='placeholder2', children='nope'),
    dcc.Slider(
        id='slider',
        min=0,
        max=10
    )
])


# @app.callback(dash.dependencies.Output('example-graph', 'figure'), [dash.dependencies.Input('slider', 'value')])
# def update(input):
#     print('callback update')
#     print('input', input)
#     trace1 = go.Scatter(x=twiss.s, y=np.ones(twiss.betax.shape), marker=dict(color='#c6262e'))
#     # fig.data.update(trace1)
#     array = np.ones(twiss.betax.size)
#     if input == None:
#         input = 0
#     array *= input
#     twiss.betax[:] = array #change in place
#     print('set', twiss.betax[0: 10])
#     return getTwissFigure(twiss,ring)


@app.callback(dash.dependencies.Output('placeholder2', 'children'), [dash.dependencies.Input('button2', 'n_clicks')])
def update2(input):
    print('callback update2')
    print('input', input)
    print('read', twiss.betax[0: 10])
    twiss.betax[:] *= 0#change in place
    return 'nope'


if __name__ == '__main__':
    app.run_server(debug=True)
