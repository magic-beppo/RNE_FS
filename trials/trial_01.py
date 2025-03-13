import plotly.graph_objs as go
import pandas as pd

# Sample Data
data = {
    'Year': [2018, 2019, 2020, 2021, 2022],
    'Country A': [0.8, 0.7, 0.6, 0.9, 0.8],
    'Country B': [0.6, 0.8, 0.7, 0.6, 0.7],
    'Country C': [0.7, 0.9, 0.8, 0.7, 0.6]
}

df = pd.DataFrame(data)

years = df['Year'].tolist()
countries = df.columns[1:]

# Create traces
traces = []
for country in countries:
    traces.append(go.Indicator(
        mode="number+gauge",
        value=df[country].iloc[0],
        title={'text': country},
        domain={'row': 0, 'column': df.columns.get_loc(country)-1},
        gauge={'axis': {'range': [0, 1]}}
    ))

# Create frames
frames = []
for year in years:
    frame = {'data': [], 'name': str(year)}
    for country in countries:
        frame['data'].append(go.Indicator(
            mode="number+gauge",
            value=df[df['Year'] == year][country].values[0],
            title={'text': country},
            gauge={'axis': {'range': [0, 1]}},
            domain={'row': 0, 'column': df.columns.get_loc(country)-1}
        ))
    frames.append(frame)

# Layout
layout = go.Layout(
    grid={'rows': 1, 'columns': len(countries), 'pattern': "independent"},
    updatemenus=[{
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 87},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }],
    sliders=[{
        'steps': [
            {
                'args': [
                    [str(year)],
                    {'frame': {'duration': 500, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}
                ],
                'label': str(year),
                'method': 'animate'
            } for year in years
        ],
        'transition': {'duration': 500},
        'x': 0.1,
        'len': 0.9,
        'currentvalue': {'font': {'size': 20}, 'prefix': 'Year: ', 'visible': True, 'xanchor': 'center'},
        'pad': {'b': 10, 't': 50},
    }]
)

# Create figure
fig = go.Figure(data=traces, layout=layout, frames=frames)

fig.show()
