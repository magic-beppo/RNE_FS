import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Sample Data
data = {
    'Year': [2018, 2019, 2020, 2021, 2022, 2018, 2019, 2020, 2021, 2022, 2018, 2019, 2020, 2021, 2022],
    'Country': ['Country A', 'Country A', 'Country A', 'Country A', 'Country A', 'Country B', 'Country B', 'Country B', 'Country B', 'Country B', 'Country C', 'Country C', 'Country C', 'Country C', 'Country C'],
    'Region': ['Region 1', 'Region 1', 'Region 1', 'Region 1', 'Region 1', 'Region 2', 'Region 2', 'Region 2', 'Region 2', 'Region 2', 'Region 3', 'Region 3', 'Region 3', 'Region 3', 'Region 3'],
    'FS Indicator 1': [0.8, 0.7, 0.6, 0.9, 0.8, 0.6, 0.8, 0.7, 0.6, 0.7, 0.7, 0.9, 0.8, 0.7, 0.6],
    'FS Indicator 2': [0.6, 0.5, 0.7, 0.8, 0.9, 0.5, 0.7, 0.6, 0.5, 0.6, 0.8, 0.7, 0.6, 0.5, 0.9],
    'FS Indicator 3': [0.9, 0.8, 0.7, 0.6, 0.7, 0.9, 0.8, 0.9, 0.6, 0.7, 0.6, 0.5, 0.8, 0.9, 0.7],
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
        html.Label('Select X-Axis Dimension'),
        dcc.Dropdown(
            id='xaxis-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns if col not in ['Year', 'Country', 'Region']],
            value='FS Indicator 1'
        )
    ]),
    html.Div([
        html.Label('Select Y-Axis Dimension'),
        dcc.Dropdown(
            id='yaxis-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns if col not in ['Year', 'Country', 'Region']],
            value='FS Indicator 2'
        )
    ]),
    html.Div([
        html.Label('Select Bubble Size Dimension'),
        dcc.Dropdown(
            id='size-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns if col not in ['Year', 'Country', 'Region']],
            value='FS Indicator 3'
        )
    ]),
    dcc.Graph(id='scatter-plot')
])

@app.callback(
    Output('scatter-plot', 'figure'),
    [
        Input('year-slider', 'value'),
        Input('xaxis-dropdown', 'value'),
        Input('yaxis-dropdown', 'value'),
        Input('size-dropdown', 'value')
    ]
)
def update_graph(selected_year, xaxis_col, yaxis_col, size_col):
    filtered_df = df[df['Year'] == selected_year]

    fig = px.scatter(
        filtered_df,
        x=xaxis_col,
        y=yaxis_col,
        size=size_col,
        color='Country',
        hover_name='Country',
        title=f'{xaxis_col} vs {yaxis_col} (Size: {size_col}) for {selected_year}',
        labels={
            xaxis_col: xaxis_col,
            yaxis_col: yaxis_col,
            size_col: size_col
        }
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
