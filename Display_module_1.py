import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
import os
import sys
  
  
# Get the absolute path to the 'Home' directory
home_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Home'))

# Ensure the 'Home' directory is added to the Python path
sys.path.insert(0, home_path)

# Import Navbar from Home directory
from navbar import Navbar

# Load the CSV file
BasePath = os.path.dirname(os.path.abspath(__file__))
PathData = os.path.join(BasePath, 'FS_selection.csv')

df = pd.read_csv(PathData, encoding='ISO-8859-1', dtype={'Item Code': str})

# Ensure 'Value' column is numeric
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

# Adjust year values by taking the midpoint of each period
df['Year'] = df['Year'].apply(lambda x: int(x.split('-')[0]) + 1)

years = df['Year'].unique().tolist()
countries = df['Area'].unique().tolist()
indicators = df['Item'].unique().tolist()

# Create a dictionary to format slider labels
slider_marks = {year: f"{year}/{str(year + 1)[-2:]}" for year in years}

# Default selected Area Codes
default_area_codes_first_chart = [59, 103, 112, 121, 212, 276]
default_area_codes_second_chart = [59, 103, 112, 121, 212, 276, 5305, 5000, 5308, 5100, 5300]
default_countries_first_chart = df[df['Area Code'].isin(default_area_codes_first_chart)]['Area'].unique().tolist()
default_countries_second_chart = df[df['Area Code'].isin(default_area_codes_second_chart)]['Area'].unique().tolist()

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
    '/assets/style.css'  # Use relative path
]

# Initialize the Dash app
app = dash.Dash(__name__, assets_folder='assets')

app.layout = html.Div([
    Navbar(),  # Include Navbar
    html.H1("1. Food Security by Indicator and Peer: Mashreq Countries"),
    html.Div([
        html.Label("Select one or several food security indicators:", style={'fontSize': '15px'}),
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[{'label': indicator, 'value': indicator} for indicator in indicators],
            value=['Prevalence of undernourishment (percent) (3-year average)'],
            multi=True,
            placeholder='Select Indicator(s)'
        ),
        html.Div(style={'height': '20px'}),
        html.Label("Select countries:", style={'fontSize': '15px'}),
        html.Div([
            dcc.Checklist(
                id='country-checklist',
                options=[{'label': country, 'value': country} for country in countries],
                value=default_countries_first_chart,
                inline=True,
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}  # Corrected style property
            ),
        ], id='country-checklist-container'),
        html.Div(style={'height': '20px'}),
        dcc.Checklist(
            id='animation-checkbox',
            options=[{'label': 'Enable Animation over Time', 'value': 'animate'}],
            value=[]
        ),
        dcc.Interval(
            id='interval-component',
            interval=1000,  # 1 second
            n_intervals=0,
            disabled=True
        ),
        dcc.Slider(
            id='year-slider',
            min=min(years),
            max=max(years),
            value=2015,  # Default year set to 2015
            marks=slider_marks,
            step=None
        ),
        html.Div(style={'height': '20px'}),
        html.Div(id='gauge-charts')
    ]),
    html.Hr(),
    
    html.H1("2. Evolution of Food Security Indicators Over Time"),
    html.Div([
        html.Div([
            html.Label("Select food security indicator:", style={'fontSize': '15px', 'width': '300px'}),
            html.Div(
                dcc.Dropdown(
                    id='indicator-time-dropdown',
                    options=[{'label': indicator, 'value': indicator} for indicator in indicators],
                    value='Prevalence of undernourishment (percent) (3-year average)',
                    placeholder='Select Indicator'
                ),
                style={'width': '900px'}  # Adjust the width to 900px
            ),
        ], style={'padding': '0 10px'}),
        html.Div([
            html.Label("Select countries:", style={'fontSize': '15px'}),
            dcc.Checklist(
                id='country-time-checklist',
                options=[{'label': country, 'value': country} for country in countries],
                value=default_countries_second_chart,
                inline=True,
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}  # Corrected style property
            ),
        ], style={'padding': '0 10px'}),
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}),
    dcc.Graph(id='line-plot'),
    
    html.Hr(),

    html.H1("3. Create your own Food Security Analysis"),

    # First row with y-axis, x-axis, and bubble size selectors
    html.Div([
        html.Div([
            html.Label("Select variable for the y-axis", style={'fontSize': '15px'}),
            dcc.Dropdown(
                id='yaxis-dropdown',
                options=[{'label': indicator, 'value': indicator} for indicator in indicators],
                value='Prevalence of undernourishment (percent) (3-year average)',
                placeholder='Select Y-axis Indicator'
            ),
        ], style={'flex': '1', 'padding': '0 10px'}),

        html.Div([
            html.Label("Select variable for the x-axis", style={'fontSize': '15px'}),
            dcc.Dropdown(
                id='xaxis-dropdown',
                options=[{'label': indicator, 'value': indicator} for indicator in indicators],
                value='Average dietary energy supply adequacy (percent) (3-year average)',
                placeholder='Select X-axis Indicator'
            ),
        ], style={'flex': '1', 'padding': '0 10px'}),

        html.Div([
            html.Label("Select variable for the bubble size", style={'fontSize': '15px'}),
            dcc.Dropdown(
                id='size-dropdown',
                options=[{'label': indicator, 'value': indicator} for indicator in indicators],
                value='Gross domestic product per capita, PPP, (constant 2017 international $)',
                placeholder='Select Size Indicator'
            ),
        ], style={'flex': '1', 'padding': '0 10px'}),
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}),

    # Second row with year checklist and country radio buttons
    html.Div([
        html.Div([
            html.Label("Select year(s):", style={'fontSize': '15px'}),
            dcc.Checklist(
                id='year-checklist',
                options=[{'label': year, 'value': year} for year in years if year < 2023],  # Exclude 2022 and 2023
                value=[2022],  # Set default year to 2015
                inline=True,
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}  # Adjust the style property as needed
            ),
        ], style={'flex': '1', 'padding': '0 10px'}),

        html.Div([
            html.Label("Select countries:", style={'fontSize': '15px'}),
            dcc.Checklist(
                id='country-radio',
                options=[{'label': country, 'value': country} for country in countries],
                value=default_countries_first_chart,  # Set default countries to the same as in the first section
                inline=True,
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}  # Adjust the style property as needed
            ),
        ], style={'flex': '1', 'padding': '0 10px'}),
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}),

    # Third row with regression type and trendline checkbox
    html.Div([
        html.Div([
            html.Label("Regression Line Type", style={'fontSize': '15px'}),
            dcc.Dropdown(
                id='regression-type-dropdown',
                options=[
                    {'label': 'Linear (degree 1)', 'value': 1},
                    {'label': 'Quadratic (degree 2)', 'value': 2}
                ],
                value=1,
                placeholder='Select Regression Type'
            ),
        ], style={'flex': '1', 'padding': '0 10px'}),

        html.Div([
            html.Label("", style={'fontSize': '15px'}),
            dcc.Checklist(
                id='trendline-checkbox',
                options=[{'label': 'Show Regression Line', 'value': 'show'}],
                value=['show']
            ),
    ], style={'flex': '1', 'padding': '0 10px'}),
], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}),

html.Div(style={'height': '20px'}),

dcc.Graph(id='scatter-plot'),

])


def create_bullet_chart(values, labels, title, unit):
    max_value = max(values) if values else 1  # Ensure max_value is not zero

    # Generate a color array long enough to handle any number of countries
    colors = px.colors.qualitative.Plotly * (len(labels) // len(px.colors.qualitative.Plotly) + 1)
    
    fig = go.Figure()

    num_labels = len(labels)
    for i, value in enumerate(values):
        fig.add_trace(go.Indicator(
            mode="number+gauge",
            value=value,
            title={'text': labels[i]},
            gauge={
                'axis': {'range': [0, max_value]},
                'bar': {'color': colors[i]},
            },
            domain={'x': [i / num_labels, (i + 1) / num_labels], 'y': [0, 1]}
        ))

    fig.update_layout(
        title={'text': f'{title} ({unit})', 'font': {'size': 20}},
        grid={'rows': 1, 'columns': num_labels, 'pattern': "independent"},
        margin=dict(t=50, b=0, l=0, r=0)
    )

    return fig

@app.callback(
    Output('gauge-charts', 'children'),
    [Input('indicator-dropdown', 'value'),
     Input('year-slider', 'value'),
     Input('country-checklist', 'value')]
)
def update_gauge_charts(selected_indicators, selected_year, selected_countries):
    if not selected_indicators:
        return []

    charts = []
    for indicator in selected_indicators:
        values = []
        unit = ""
        for country in selected_countries:
            value = df[(df['Year'] == selected_year) & (df['Area'] == country) & (df['Item'] == indicator)]
            if not value.empty:
                values.append(float(value['Value'].values[0]))
                unit = value['Unit'].values[0]
            else:
                values.append(0)
        fig = create_bullet_chart(values, selected_countries, f'{indicator} in {selected_year}/{str(selected_year + 1)[-2:]}', unit)
        
        chart = dcc.Graph(
            figure=fig,
            style={'display': 'inline-block', 'width': '100%'}
        )
        charts.append(chart)
    
    return charts

def polynomial_fit(x, y, degree):
    coeffs = np.polyfit(x, y, degree)
    poly_func = np.poly1d(coeffs)
    y_pred = poly_func(x)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    return poly_func, coeffs, r_squared

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('xaxis-dropdown', 'value'),
     Input('yaxis-dropdown', 'value'),
     Input('size-dropdown', 'value'),
     Input('year-checklist', 'value'),
     Input('trendline-checkbox', 'value'),
     Input('regression-type-dropdown', 'value'),
     Input('country-radio', 'value')]
)
def update_scatter_plot(x_indicator, y_indicator, size_indicator, selected_years, trendline_option, regression_type, selected_countries):
    df_filtered = df[(df['Year'].isin(selected_years)) & (df['Area'].isin(selected_countries))]

    if df_filtered.empty:
        return go.Figure()

    df_pivot = df_filtered.pivot_table(values='Value', index=['Area', 'Year'], columns='Item').reset_index()

    fig = px.scatter(
        df_pivot,
        x=x_indicator,
        y=y_indicator,
        size=size_indicator,
        color='Area',
        hover_name='Area',
        labels={x_indicator: x_indicator, y_indicator: y_indicator, size_indicator: size_indicator},
        facet_col='Year',  # Separate plots for each year
        facet_col_wrap=2  # Adjust the number of columns for wrapping
    )

    if len(selected_years) == 1 and "show" in trendline_option:
        year = selected_years[0]
        df_year = df_pivot[df_pivot['Year'] == year]
        X = df_year[x_indicator]
        Y = df_year[y_indicator]

        poly_fit, coeffs, r_squared = polynomial_fit(X, Y, regression_type)

        X_sorted = np.sort(X)
        Y_pred = poly_fit(X_sorted)

        fig.add_trace(go.Scatter(
            x=X_sorted,
            y=Y_pred,
            mode='lines',
            line=dict(color='black', dash='dash'),
            name=f'Polynomial (degree {regression_type}) {year}'
        ))

        # Create the equation string
        equation_terms = []
        for i, coeff in enumerate(coeffs):
            power = len(coeffs) - i - 1
            if power == 1:
                term = f"{coeff:.4f}x"
            elif power == 2:
                term = f"{coeff:.4f}x<sup>2</sup>"
            else:
                term = f"{coeff:.4f}"
            equation_terms.append(term)
        equation = " + ".join(equation_terms)
        equation = f"y = {equation} (R² = {r_squared:.4f})"

        fig.add_annotation(
            x=0.5, y=0.9, xref='paper', yref='paper',
            text=equation, showarrow=False, font=dict(size=20, color="black")
        )

    fig.update_layout(
        title={
            'text': f'{x_indicator} vs {y_indicator} <br>with size {size_indicator} in selected years',
            'font': {'size': 20}
        },
        xaxis_title=x_indicator,
        yaxis_title=y_indicator,
        legend_title='Country',
        height=700
    )

    return fig

@app.callback(
    [Output('year-slider', 'value'),
     Output('interval-component', 'disabled')],
    [Input('animation-checkbox', 'value'),
     Input('interval-component', 'n_intervals')],
    [State('year-slider', 'value')]
)
def animate_year_slider(animate, n_intervals, year_value):
    if 'animate' in animate:
        next_year = year_value + 1 if year_value < 2021 else 2021
        if next_year == 2021:
            return next_year, True  # Stop animation when it reaches the final year
        return next_year, False
    return year_value, True

@app.callback(
    Output('line-plot', 'figure'),
    [Input('indicator-time-dropdown', 'value'),
     Input('country-time-checklist', 'value')]
)
def update_line_plot(selected_indicator, selected_countries):
    if not selected_indicator:
        return go.Figure()

    fig = go.Figure()

    # Extract the y-axis title from the selected indicator
    yaxis_title = selected_indicator
    if '(' in selected_indicator and ')' in selected_indicator:
        yaxis_title = selected_indicator.split('(')[1].split(')')[0]

    for country in selected_countries:
        df_filtered = df[(df['Area'] == country) & (df['Item'] == selected_indicator)]

        # Skip if no data available
        if df_filtered.empty:
            continue

        # Ensure Year is a string before applying split
        df_filtered['Year'] = df_filtered['Year'].astype(str).apply(lambda x: int(x.split('-')[0]) + 1)
        df_filtered = df_filtered.groupby('Year', as_index=False)['Value'].mean()

        # Drop rows with NaN values
        df_filtered = df_filtered.dropna(subset=['Value'])

        # Skip if no data available after dropping NaNs
        if df_filtered.empty:
            continue

        # Determine if the country is a regional aggregate
        area_code = df[df['Area'] == country]['Area Code'].iloc[0]
        line_width = 4 if area_code > 300 else 2  # Thicker lines for regional aggregates

        fig.add_trace(go.Scatter(
            x=df_filtered['Year'],
            y=df_filtered['Value'],
            mode='lines+markers',
            name=country,
            text=[f"{country} - {year}" for year in df_filtered['Year']],
            line=dict(width=line_width)
        ))

    # Modify the x-axis title based on the selected indicator
    xaxis_title = "Year"
    if "(3-year average)" in selected_indicator:
        xaxis_title = "3-year average around the indicated year"
        selected_indicator = selected_indicator.replace(" (3-year average)", "")
    elif "(annual value)" in selected_indicator:
        xaxis_title = ""
        selected_indicator = selected_indicator.replace(" (annual value)", "")

    # Remove the remaining string in parenthesis from the chart title
    if '(' in selected_indicator and ')' in selected_indicator:
        selected_indicator = selected_indicator.split('(')[0].strip()

    fig.update_layout(
        title={
            'text': f"{selected_indicator}",
            'font': {'size': 24}
        },
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        height=600,
        xaxis={
            'tickmode': 'linear',
            'tick0': df_filtered['Year'].min(),
            'dtick': 1,  # Display labels for every year
            'tickfont': {'size': 14}
        },
        yaxis={
            'tickfont': {'size': 14}
        }
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')