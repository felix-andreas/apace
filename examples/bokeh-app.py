# -*- coding: utf-8 -*-
import elements as el
from elements.linbeamdyn import Latticedata, twissdata
import numpy as np

D1 = el.Drift('D1', length=0.55)
Q1 = el.Quad('Q1', length=0.2, k1=1.2)
B1 = el.Bend('B1', length=1.5, angle=0.392701, e1=0.1963505, e2=0.1963505)
Q2 = el.Quad('Q2', length=0.4, k1=-1.2)
FODO = el.Line('fodo-cell', [Q1, D1, B1, D1, Q2, D1, B1, D1, Q1])
interFODO = el.Line('inter-Fodo', [FODO] * 10)
ring = el.Mainline('fodo-ring', [FODO] * 8)

latticedata = Latticedata(ring)
twiss = twissdata(latticedata)

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure

# Set up data
N = 6
x = np.linspace(0, 2 * np.pi, N)
y = np.sin(x)
source = ColumnDataSource(data=dict(x=x, y=y))
a = source.data['x']
b = source.data['y']
def do_stuff(attr, old, new):
    print('changed!!')
source.on_change('data', do_stuff)

print(id(a))
print(id(source.data['x']))
# Set up plot
plot = figure(plot_height=400, plot_width=400, title="my sine wave",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 50], y_range=[0, 15])

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

# Set up widgets
text = TextInput(title="title", value='my sine wave')
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase = Slider(title="phase", value=0.0, start=0.0, end=2 * np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)


# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value


text.on_change('value', update_title)
c = 2


def update_data(attrname, old, new):
    global a, b, c
    global source
    print(id(a))
    print(a, b)
    if c == 2:
        c = 1 / 2
    else:
        c = 2
    a *= 1
    b *= c
    print('b', b)
    print('y', source.data['y'])
    # source.data = dict(x=x, y=y)
    # source.trigger('change')


for w in [offset, amplitude, phase, freq]:
    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = widgetbox(text, offset, amplitude, phase, freq)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Sliders"
