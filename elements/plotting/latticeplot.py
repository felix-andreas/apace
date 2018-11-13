import plotly
import plotly.io as pio
import plotly.graph_objs as go

from elements import Drift, Bend, Quad, Sext

# # filled Rectangle
# def generator_retangle():
#     for xstart in range(50):
#         yield AttrDict(type='rect', x0=0 + xstart, y0=0, x1=0.4 + xstart, y1=0.1, fillcolor='rgba(128,0,0,1)', line=dict(width=0))

range = [0, 60]
layout = go.Layout(
    hovermode='closest',

    xaxis=dict(
        showgrid=True,
        range=range,
        zeroline=False,
        showline=True,
        mirror='ticks',
        gridwidth=1,
        zerolinecolor='#969696',
        linewidth=1
    ),
    yaxis=dict(
        showgrid=True,
        zeroline=False,
        showline=True,
        mirror='ticks',
        gridwidth=1,
        zerolinecolor='#969696',
        linewidth=1
    )
)

updatemenus=list([
    dict(
        buttons=list([
            dict(
                args=['type', 'line'],
                label='line',
                method='restyle'
            ),
            dict(
                args=['type', 'bar'],
                label='bar',
                method='restyle'
            )
        ]),
        direction = 'left',
        pad = {'r': 10, 't': 10},
        showactive = True,
        type = 'buttons',
        x = 0.,
        xanchor = 'left',
        y = -0.2,
        yanchor = 'top'
    ),
])

# layout['updatemenus'] = updatemenus

# rect = AttrDict(type='rect', x0=0, y0=0, x1=1, y1=1, fillcolor='rgba(128,0,0,1', line=dict(width=0))
def plotTwiss(twiss, line, path):
    fig = getTwissFigure(twiss, line)
    pio.write_image(fig, path)
    # plotly.offline.plot(fig, path + 'offline')


def getTwissFigure(twiss, line):
    trace1 = go.Scatter(x=twiss.s, y=twiss.betax, marker=dict(color='#c6262e'))  # , marker={'color': 'red', 'symbol': 104, 'size': "10"}, text=["one", "two", "three"], name='1st Trace')
    trace2 = go.Scatter(x=twiss.s, y=twiss.betay, marker=dict(color='#3689e6'))  # , marker={'color': 'red', 'symbol': 104, 'size': "10"}, text=["one", "two", "three"], name='1st Trace')
    trace3 = go.Scatter(x=twiss.s, y=twiss.etax, marker=dict(color='#68b723'))  # , marker={'color': 'red', 'symbol': 104, 'size': "10"}, text=["one", "two", "three"], name='1st Trace')
    # layout = go.Layout(autosize=True)

    shapes = []
    names = []
    x_names = []
    y_names = []
    start = 0
    colors = {Bend:'#f9c440' , Quad: '#c6262e', Sext: '#029868'}
    for i, element in enumerate(line.lattice):
        end = start + element.length
        if not isinstance(element, Drift):
            shapes.append(dict(type='rect', x0=start, x1=end, yref='paper', y0=1.05, y1=1.12, fillcolor=colors[element.__class__], line=dict(width=0)))
            if element.length / line.length > 0.01:
                names.append(element.name)
                x_names.append(start + element.length / 2)
                y_names.append(10)
        start = end

    trace_name = go.Scatter(x=x_names, y=y_names, text=names, mode='text')
    layout['shapes'] = shapes
    # layout['title'] = line.name
    data = [trace1, trace2, trace3, trace_name]
    fig = go.Figure(data=data, layout=layout)

    """ use matplotlib figure  
    mpl_fig = plt.figure()
    plt.plot(twiss.s,twiss.betax)
    plt.plot(twiss.s,twiss.betay)
    plt.plot(twiss.s,twiss.etax)
    fig = tls.mpl_to_plotly(mpl_fig)
    """
    return fig

if __name__ == '__main__':
    pass
