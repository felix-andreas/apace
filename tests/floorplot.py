import sys

sys.path.append('..')

from elements.utils import AttrDict

import plotly.io as pio
import plotly.graph_objs as go


# filled Rectangle
def generator_retangle():
    for xstart in range(50):
        yield AttrDict(type='rect', x0=0 + xstart, y0=0, x1=0.4 + xstart, y1=0.1, fillcolor='rgba(128,0,0,1)', line=dict(width=0))


rect = AttrDict(type='rect', x0=0, y0=0, x1=1, y1=1, fillcolor='rgba(128,0,0,1', line=dict(width=0))

layout = go.Layout(
    autosize=True,
    xaxis=dict(
        range=[0, 50],
        showgrid=True,
        zeroline=False,
        showline=False,
        ticks='',
        showticklabels=False
    ),
    yaxis=dict(
        showgrid=True,
        zeroline=False,
        showline=False,
        ticks='',
        showticklabels=False
    ),
    shapes=list(generator_retangle())

)


fig = go.Figure(layout=layout)
rect.x1 = 4

pio.write_image(fig, 'test.pdf')
