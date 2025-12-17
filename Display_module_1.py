import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
import os
import sys

# Import CSV uploader component
from csv_uploader import CSVUploader
  
# Get the absolute path to the 'Home' directory
home_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Home'))
sys.path.insert(0, home_path)

# Import Navbar from Home directory
from navbar import Navbar

# Load the CSV file
BasePath = os.path.dirname(os.path.abspath(__file__))
PathData = os.path.join(BasePath, 'FS_selection.csv')

df = pd.read_csv(PathData, encoding='ISO-8859-1', dtype={'Item Code': str})

# Ensure 'Value' column is numeric
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

# ═══════════════════════════════════════════════════════════════════════
# IMPROVED YEAR HANDLING - Handles both 3-year averages and single years
# ═══════════════════════════════════════════════════════════════════════

def process_year(year_str):
    """
    Convert year string to display year.
    - For ranges like "2000-2002": return midpoint (2001)
    - For single years like "2000": return as-is (2000)
    """
    year_str = str(year_str)
    if '-' in year_str:
        start_year = int(year_str.split('-')[0])
        return start_year + 1  # Midpoint
    else:
        return int(year_str)

# Store original year for labels
df['Year_Original'] = df['Year'].astype(str)

# Create display year (for filtering and sliders)
df['Year'] = df['Year_Original'].apply(process_year)

# Create indicator to know if it's a 3-year average
df['Is_Average'] = df['Year_Original'].str.contains('-', regex=False)

# ═══════════════════════════════════════════════════════════════════════

years = sorted(df['Year'].unique().tolist())
countries = df['Area'].unique().tolist()
indicators = df['Item'].unique().tolist()

def create_slider_label(year):
    """Create slider label showing if it's a 3-year average or single year"""
    year_data = df[df['Year'] == year]['Year_Original'].unique()
    
    if len(year_data) == 1:
        original = year_data[0]
        if '-' in original:
            return f"{year} (avg)"
        else:
            return str(year)
    else:
        return str(year)

slider_marks = {year: create_slider_label(year) for year in years}

# Default selected Area Codes
default_area_codes_first_chart = [59, 103, 112, 121, 212, 276]
default_area_codes_second_chart = [59, 103, 112, 121, 212, 276, 5305, 5000, 5308, 5100, 5300]
default_countries_first_chart = df[df['Area Code'].isin(default_area_codes_first_chart)]['Area'].unique().tolist()
default_countries_second_chart = df[df['Area Code'].isin(default_area_codes_second_chart)]['Area'].unique().tolist()

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
    '/assets/style.css'
]

# Initialize the Dash app
app = dash.Dash(__name__, assets_folder='assets')
server = app.server

# Initialize CSV uploader component
uploader = CSVUploader(
    app=app,
    csv_path=PathData,
    required_columns=['Area', 'Area Code', 'Year', 'Item', 'Item Code', 'Value', 'Unit'],
    password='ChangeThisPassword123!'
)

# App layout
app.layout = html.Div([
    uploader.get_layout(),
    Navbar(),
    
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
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}
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
            interval=1000,
            n_intervals=0,
            disabled=True
        ),
        dcc.Slider(
            id='year-slider',
            min=min(years),
            max=max(years),
            value=2022,
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
                style={'width': '900px'}
            ),
        ], style={'padding': '0 10px'}),
        html.Div([
            html.Label("Select countries:", style={'fontSize': '15px'}),
            dcc.Checklist(
                id='country-time-checklist',
                options=[{'label': country, 'value': country} for country in countries],
                value=default_countries_second_chart,
                inline=True,
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}
            ),
        ], style={'padding': '0 10px'}),
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}),
    dcc.Graph(id='line-plot'),
    
    html.Hr(),

    html.H1("3. Create your own Food Security Analysis"),

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

    html.Div([
        html.Div([
            html.Label("Select year(s):", style={'fontSize': '15px'}),
            dcc.Checklist(
                id='year-checklist',
                options=[{'label': year, 'value': year} for year in years if year < 2023],
                value=[2022],
                inline=True,
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}
            ),
        ], style={'flex': '1', 'padding': '0 10px'}),

        html.Div([
            html.Label("Select countries:", style={'fontSize': '15px'}),
            dcc.Checklist(
                id='country-radio',
                options=[{'label': country, 'value': country} for country in countries],
                value=default_countries_first_chart,
                inline=True,
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}
            ),
        ], style={'flex': '1', 'padding': '0 10px'}),
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}),

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
    max_value = max(values) if values else 1
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
        
        year_original = df[df['Year'] == selected_year]['Year_Original'].iloc[0] if len(df[df['Year'] == selected_year]) > 0 else str(selected_year)
        
        fig = create_bullet_chart(values, selected_countries, f'{indicator} in {year_original}', unit)
        
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


# ═══════════════════════════════════════════════════════════════════════
# FUZZY YEAR MATCHING FOR SCATTER PLOTS
# ═══════════════════════════════════════════════════════════════════════

def get_fuzzy_year_data(df, year, indicator, country, tolerance=1):
    """
    Get data for a specific year, country, and indicator.
    If exact year not found, try years within ±tolerance.
    """
    # Try exact year first
    result = df[(df['Year'] == year) & (df['Area'] == country) & (df['Item'] == indicator)]
    
    if not result.empty:
        return result['Value'].iloc[0], year
    
    # Try nearby years
    for offset in range(1, tolerance + 1):
        # Try year + offset
        result = df[(df['Year'] == year + offset) & (df['Area'] == country) & (df['Item'] == indicator)]
        if not result.empty:
            return result['Value'].iloc[0], year + offset
        
        # Try year - offset
        result = df[(df['Year'] == year - offset) & (df['Area'] == country) & (df['Item'] == indicator)]
        if not result.empty:
            return result['Value'].iloc[0], year - offset
    
    return None, None


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
    
    # Build data manually with fuzzy year matching
    data_rows = []
    
    for year in selected_years:
        for country in selected_countries:
            # Get values for each indicator (with fuzzy matching)
            x_val, x_year = get_fuzzy_year_data(df, year, x_indicator, country, tolerance=1)
            y_val, y_year = get_fuzzy_year_data(df, year, y_indicator, country, tolerance=1)
            size_val, size_year = get_fuzzy_year_data(df, year, size_indicator, country, tolerance=1)
            
            # Only include if we have ALL three values
            if x_val is not None and y_val is not None and size_val is not None:
                # Get original year format for display
                year_original_list = df[df['Year'] == year]['Year_Original'].unique()
                year_original = year_original_list[0] if len(year_original_list) > 0 else str(year)
                
                data_rows.append({
                    'Area': country,
                    'Year': year,
                    'Year_Original': year_original,
                    x_indicator: x_val,
                    y_indicator: y_val,
                    size_indicator: size_val
                })
    
    if not data_rows:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected years and countries.<br><br>Try selecting different years (especially recent ones like 2020-2022).",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red"),
            align="center"
        )
        fig.update_layout(
            title="No Data Available",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=700
        )
        return fig
    
    df_pivot = pd.DataFrame(data_rows)
    facet_years = sorted(df_pivot['Year'].unique())

    fig = px.scatter(
        df_pivot,
        x=x_indicator,
        y=y_indicator,
        size=size_indicator,
        color='Area',
        hover_name='Area',
        labels={x_indicator: x_indicator, y_indicator: y_indicator, size_indicator: size_indicator},
        facet_col='Year',
        facet_col_wrap=2,
        category_orders={'Year': facet_years}
    )

    fig.for_each_annotation(lambda a: a.update(text=''))
    
    for idx, year in enumerate(facet_years):
        df_year = df_pivot[df_pivot['Year'] == year]
        
        xaxis_name = 'x' if idx == 0 else f'x{idx + 1}'
        yaxis_name = 'y' if idx == 0 else f'y{idx + 1}'
        xref = f'{xaxis_name} domain'
        yref = f'{yaxis_name} domain'
        
        year_original = df_year['Year_Original'].iloc[0] if len(df_year) > 0 else str(year)
        
        fig.add_annotation(
            x=0.98, y=0.98,
            xref=xref,
            yref=yref,
            text=f"Year: {year_original}",
            showarrow=False,
            font=dict(size=12, color="black", weight="bold"),
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='black',
            borderwidth=1,
            borderpad=4
        )
        
        if df_year.empty:
            continue
        
        if "show" in trendline_option:
            df_year_clean = df_year[[x_indicator, y_indicator]].dropna()
            
            if len(df_year_clean) < 2:
                continue
                
            X = df_year_clean[x_indicator]
            Y = df_year_clean[y_indicator]

            poly_fit_func, coeffs, r_squared = polynomial_fit(X, Y, regression_type)

            X_sorted = np.sort(X)
            Y_pred = poly_fit_func(X_sorted)

            fig.add_trace(go.Scatter(
                x=X_sorted,
                y=Y_pred,
                mode='lines',
                line=dict(color='black', dash='dash', width=2),
                name=f'Regression {year}',
                showlegend=False,
                xaxis=xaxis_name,
                yaxis=yaxis_name,
                hovertemplate=f'Regression line<br>Year: {year}<extra></extra>'
            ))

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
            equation = f"y = {equation}<br>R² = {r_squared:.4f}"

            fig.add_annotation(
                x=0.02, y=0.02,
                xref=xref,
                yref=yref,
                text=equation, 
                showarrow=False, 
                font=dict(size=10, color="black"),
                xanchor='left',
                yanchor='bottom',
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='black',
                borderwidth=1,
                borderpad=4
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
            return next_year, True
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

    yaxis_title = selected_indicator
    if '(' in selected_indicator and ')' in selected_indicator:
        yaxis_title = selected_indicator.split('(')[1].split(')')[0]

    for country in selected_countries:
        df_filtered = df[(df['Area'] == country) & (df['Item'] == selected_indicator)].copy()

        if df_filtered.empty:
            continue

        df_filtered = df_filtered.groupby('Year', as_index=False).agg({
            'Value': 'mean',
            'Year_Original': 'first'
        })

        df_filtered = df_filtered.dropna(subset=['Value'])

        if df_filtered.empty:
            continue

        area_code = df[df['Area'] == country]['Area Code'].iloc[0]
        line_width = 4 if area_code > 300 else 2

        hover_text = [f"{country} - {year_orig}" for year_orig in df_filtered['Year_Original']]

        fig.add_trace(go.Scatter(
            x=df_filtered['Year'],
            y=df_filtered['Value'],
            mode='lines+markers',
            name=country,
            text=hover_text,
            hovertemplate='%{text}<br>Value: %{y:.2f}<extra></extra>',
            line=dict(width=line_width)
        ))

    xaxis_title = "Year"
    if "(3-year average)" in selected_indicator:
        xaxis_title = "3-year average around the indicated year"
        selected_indicator = selected_indicator.replace(" (3-year average)", "")
    elif "(annual value)" in selected_indicator:
        xaxis_title = ""
        selected_indicator = selected_indicator.replace(" (annual value)", "")

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
            'dtick': 1,
            'tickfont': {'size': 14}
        },
        yaxis={
            'tickfont': {'size': 14}
        }
    )

    return fig


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)