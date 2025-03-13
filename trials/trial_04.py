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

# Initialize the Dash app
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
        html.Label('Drag the dimensions to the desired axes'),
        html.Div(id='x-axis', className='droppable', children='X-Axis', style={'border': '1px solid black', 'padding': '10px', 'margin': '10px', 'minHeight': '50px'}),
        html.Div(id='y-axis', className='droppable', children='Y-Axis', style={'border': '1px solid black', 'padding': '10px', 'margin': '10px', 'minHeight': '50px'}),
        html.Div(id='size', className='droppable', children='Bubble Size', style={'border': '1px solid black', 'padding': '10px', 'margin': '10px', 'minHeight': '50px'}),
    ], style={'display': 'flex', 'justifyContent': 'space-around'}),
    html.Div([
        html.Label('Available Dimensions'),
        html.Div(
            id='dimensions',
            children=[
                html.Div('FS Indicator 1', className='draggable', draggable="true", id='fs-indicator-1', style={'margin': '10px', 'padding': '10px', 'border': '1px solid #ddd', 'cursor': 'move'}),
                html.Div('FS Indicator 2', className='draggable', draggable="true", id='fs-indicator-2', style={'margin': '10px', 'padding': '10px', 'border': '1px solid #ddd', 'cursor': 'move'}),
                html.Div('FS Indicator 3', className='draggable', draggable="true", id='fs-indicator-3', style={'margin': '10px', 'padding': '10px', 'border': '1px solid #ddd', 'cursor': 'move'}),
            ],
            style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'marginTop': '20px'}
        )
    ]),
    dcc.Graph(id='scatter-plot')
])

# Callback to update the scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [
        Input('year-slider', 'value'),
        Input('x-axis', 'children'),
        Input('y-axis', 'children'),
        Input('size', 'children')
    ]
)
def update_graph(selected_year, xaxis_col, yaxis_col, size_col):
    filtered_df = df[df['Year'] == selected_year]

    # Ensure the dimensions are correctly mapped
    xaxis_col = xaxis_col if xaxis_col in df.columns else 'FS Indicator 1'
    yaxis_col = yaxis_col if yaxis_col in df.columns else 'FS Indicator 2'
    size_col = size_col if size_col in df.columns else 'FS Indicator 3'

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
