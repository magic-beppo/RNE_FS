import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

# Sample Data
data = {
    'Year': [2018, 2019, 2020, 2021, 2022, 2018, 2019, 2020, 2021, 2022, 2018, 2019, 2020, 2021, 2022],
    'Country': ['Country A', 'Country A', 'Country A', 'Country A', 'Country A', 'Country B', 'Country B', 'Country B', 'Country B', 'Country B', 'Country C', 'Country C', 'Country C', 'Country C', 'Country C'],
    'Region': ['Region 1', 'Region 1', 'Region 1', 'Region 1', 'Region 1', 'Region 2', 'Region 2', 'Region 2', 'Region 2', 'Region 2', 'Region 3', 'Region 3', 'Region 3', 'Region 3', 'Region 3'],
    'FS Indicator': ['Indicator 1', 'Indicator 1', 'Indicator 1', 'Indicator 1', 'Indicator 1', 'Indicator 2', 'Indicator 2', 'Indicator 2', 'Indicator 2', 'Indicator 2', 'Indicator 3', 'Indicator 3', 'Indicator 3', 'Indicator 3', 'Indicator 3'],
    'Value': [0.8, 0.7, 0.6, 0.9, 0.8, 0.6, 0.8, 0.7, 0.6, 0.7, 0.7, 0.9, 0.8, 0.7, 0.6]
}

df = pd.DataFrame(data)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Label('Select Year'),
        dcc.Slider(
            id='year-slider',
            min=df['Year'].min(),
            max=df['Year'].max(),
            value=df['Year'].min(),
            marks={str(year): str(year) for year in df['Year'].unique()},
            step=None
        )
    ]),
    html.Div([
        html.Label('Select Country'),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in df['Country'].unique()],
            value=df['Country'].unique()[0]
        )
    ]),
    html.Div([
        html.Label('Select Region'),
        dcc.Dropdown(
            id='region-dropdown',
            options=[{'label': region, 'value': region} for region in df['Region'].unique()],
            value=df['Region'].unique()[0]
        )
    ]),
    html.Div([
        html.Label('Select FS Indicator'),
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[{'label': indicator, 'value': indicator} for indicator in df['FS Indicator'].unique()],
            value=df['FS Indicator'].unique()[0]
        )
    ]),
    dcc.Graph(id='indicator-graph')
])

@app.callback(
    Output('indicator-graph', 'figure'),
    [
        Input('year-slider', 'value'),
        Input('country-dropdown', 'value'),
        Input('region-dropdown', 'value'),
        Input('indicator-dropdown', 'value')
    ]
)
def update_graph(selected_year, selected_country, selected_region, selected_indicator):
    filtered_df = df[
        (df['Year'] == selected_year) &
        (df['Country'] == selected_country) &
        (df['Region'] == selected_region) &
        (df['FS Indicator'] == selected_indicator)
    ]

    traces = []
    for country in df['Country'].unique():
        country_df = df[
            (df['Year'] == selected_year) &
            (df['Country'] == country) &
            (df['Region'] == selected_region) &
            (df['FS Indicator'] == selected_indicator)
        ]
        if not country_df.empty:
            traces.append(go.Indicator(
                mode="number+gauge",
                value=country_df['Value'].values[0],
                title={'text': country},
                domain={'row': 0, 'column': df['Country'].unique().tolist().index(country)},
                gauge={'axis': {'range': [0, 1]}}
            ))

    layout = go.Layout(
        grid={'rows': 1, 'columns': len(df['Country'].unique()), 'pattern': "independent"}
    )

    return {'data': traces, 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
