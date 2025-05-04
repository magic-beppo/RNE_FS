import os
import sys
import requests
import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go

# ─── Navbar import boilerplate ────────────────────────────────────────────────
home_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Home'))
sys.path.insert(0, home_path)
from navbar import Navbar

def fetch_fs_data(area_codes, fields, domain="faostat"):
    """
    Pulls FAOSTAT Food-Security facts for the given area_codes and fields,
    returns a pandas.DataFrame matching your CSV schema.
    """
    # 1) Base URL must be HTTPS
    base = "https://api.data.fao.org/1.0/query"

    # 2) OData filter for your area codes
    filter_str = " or ".join(f"area_code eq {c}" for c in area_codes)

    params = {
        "domain": domain,
        "filter": filter_str,
        "fields": ",".join(fields),
        "format": "JSON",
        "limit": -1
    }

    # 3) Build and *prepare* the full URL
    from requests import Request
    prep = Request("GET", base, params=params).prepare()
    full_url = prep.url
    print("▶️ Fetching FAO data from:", full_url)  
    # this will 100% be the URL we actually call below

    # 4) Call *that* URL directly
    r = requests.get(full_url, timeout=30)
    r.raise_for_status()    # now this line will see the same HTTPS URL

    # 5) Load into DF and rename to your schema
    df = pd.DataFrame(r.json().get("data", []))
    df.rename(columns={
        "area_code":    "Area Code",
        "area":         "Area",
        "item_code":    "Item Code",
        "item":         "Item",
        "element_code": "Element Code",
        "element":      "Element",
        "year":         "Year",
        "unit":         "Unit",
        "value":        "Value",
        "flag":         "Flag"
    }, inplace=True)

    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["Year"]  = df["Year"].apply(lambda x: int(str(x).split("-")[0]) + 1)

    return df

# ─── Fetch data on app startup ────────────────────────────────────────────────
area_codes = [59, 103, 112, 121, 212, 276, 5305, 5000, 5308, 5103, 5100, 5300]
fields = [
    "area_code","area",
    "item_code","item",
    "element_code","element",
    "year","unit","value","flag"
]
df = fetch_fs_data(area_codes, fields)

# ─── Prepare dropdown/slider options ─────────────────────────────────────────
years      = sorted(df["Year"].unique())
countries  = df["Area"].unique().tolist()
indicators = df["Item"].unique().tolist()
slider_marks = {y: f"{y}/{str(y+1)[-2:]}" for y in years}

# defaults for charts
default_first    = [59,103,112,121,212,276]
default_c1       = df[df["Area Code"].isin(default_first)]["Area"].unique().tolist()
default_c2       = df[df["Area Code"].isin(area_codes)]["Area"].unique().tolist()

# ─── Dash app setup ──────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    assets_folder='assets',
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
        '/assets/style.css'
    ]
)

app.layout = html.Div([
    Navbar(),

    html.H1("1. Food Security by Indicator and Peer: Mashreq Countries"),
    html.Div([
        html.Label("Select one or several indicators:", style={'fontSize': '15px'}),
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[{'label': i, 'value': i} for i in indicators],
            value=[indicators[0]],
            multi=True
        ),
        html.Div(style={'height': '20px'}),
        html.Label("Select countries:", style={'fontSize': '15px'}),
        dcc.Checklist(
            id='country-checklist',
            options=[{'label': c, 'value': c} for c in countries],
            value=default_c1,
            inline=True,
            labelStyle={'marginRight': '10px'}
        ),
        html.Div(style={'height': '20px'}),
        dcc.Checklist(
            id='animation-checkbox',
            options=[{'label': 'Enable Animation over Time', 'value': 'animate'}],
            value=[]
        ),
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0, disabled=True),
        dcc.Slider(
            id='year-slider',
            min=years[0], max=years[-1], value=years[0],
            marks=slider_marks, step=None
        ),
        html.Div(style={'height': '20px'}),
        html.Div(id='gauge-charts')
    ]),

    html.Hr(),

    html.H1("2. Evolution of Indicators Over Time"),
    html.Div([
        html.Div([
            html.Label("Select indicator:", style={'fontSize': '15px'}),
            dcc.Dropdown(
                id='indicator-time-dropdown',
                options=[{'label': i, 'value': i} for i in indicators],
                value=indicators[0]
            )
        ], style={'flex': '1', 'padding': '0 10px'}),
        html.Div([
            html.Label("Select countries:", style={'fontSize': '15px'}),
            dcc.Checklist(
                id='country-time-checklist',
                options=[{'label': c, 'value': c} for c in countries],
                value=default_c2,
                inline=True,
                labelStyle={'marginRight': '10px'}
            )
        ], style={'flex': '1', 'padding': '0 10px'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    dcc.Graph(id='line-plot'),

    html.Hr(),

    html.H1("3. Create your own Food Security Analysis"),
    html.Div([
        html.Div([
            html.Label("Select variable for the y-axis", style={'fontSize': '15px'}),
            dcc.Dropdown(id='yaxis-dropdown',
                         options=[{'label': i, 'value': i} for i in indicators],
                         value=indicators[0])
        ], style={'flex': '1', 'padding': '0 10px'}),
        html.Div([
            html.Label("Select variable for the x-axis", style={'fontSize': '15px'}),
            dcc.Dropdown(id='xaxis-dropdown',
                         options=[{'label': i, 'value': i} for i in indicators],
                         value=indicators[1])
        ], style={'flex': '1', 'padding': '0 10px'}),
        html.Div([
            html.Label("Select variable for the bubble size", style={'fontSize': '15px'}),
            dcc.Dropdown(id='size-dropdown',
                         options=[{'label': i, 'value': i} for i in indicators],
                         value=indicators[2])
        ], style={'flex': '1', 'padding': '0 10px'})
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}),
    html.Div([
        html.Div([
            html.Label("Select year(s):", style={'fontSize': '15px'}),
            dcc.Checklist(
                id='year-checklist',
                options=[{'label': y, 'value': y} for y in years if y < max(years)],
                value=[years[-2]],
                inline=True,
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}
            )
        ], style={'flex': '1', 'padding': '0 10px'}),
        html.Div([
            html.Label("Select countries:", style={'fontSize': '15px'}),
            dcc.Checklist(
                id='country-radio',
                options=[{'label': c, 'value': c} for c in countries],
                value=default_countries_first_chart,
                inline=True,
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}
            )
        ], style={'flex': '1', 'padding': '0 10px'})
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}),
    html.Div([
        html.Div([
            html.Label("Regression Line Type", style={'fontSize': '15px'}),
            dcc.Dropdown(id='regression-type-dropdown',
                         options=[
                             {'label': 'Linear (degree 1)', 'value': 1},
                             {'label': 'Quadratic (degree 2)', 'value': 2}
                         ],
                         value=1)
        ], style={'flex': '1', 'padding': '0 10px'}),
        html.Div([
            dcc.Checklist(id='trendline-checkbox',
                         options=[{'label': 'Show Regression Line', 'value': 'show'}],
                         value=['show'])
        ], style={'flex': '1', 'padding': '0 10px'})
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}),
    html.Div(style={'height': '20px'}),
    dcc.Graph(id='scatter-plot'),
])

def create_bullet_chart(values, labels, title, unit):
    max_value = max(values) if values else 1
    colors = px.colors.qualitative.Plotly * (len(labels) // len(px.colors.qualitative.Plotly) + 1)
    fig = go.Figure()
    for i, val in enumerate(values):
        fig.add_trace(go.Indicator(
            mode="number+gauge",
            value=val,
            title={'text': labels[i]},
            gauge={'axis': {'range': [0, max_value]}, 'bar': {'color': colors[i]}},
            domain={'x': [i / len(labels), (i + 1) / len(labels)], 'y': [0, 1]}
        ))
    fig.update_layout(
        title={'text': f'{title} ({unit})', 'font': {'size': 20}},
        grid={'rows': 1, 'columns': len(labels), 'pattern': "independent"},
        margin=dict(t=50, b=0, l=0, r=0)
    )
    return fig

@app.callback(
    Output('gauge-charts', 'children'),
    Input('indicator-dropdown', 'value'),
    Input('year-slider', 'value'),
    Input('country-checklist', 'value')
)
def update_gauge_charts(selected_inds, year, selected_countries):
    if not selected_inds:
        return []
    charts = []
    for ind in selected_inds:
        values, unit = [], ""
        for c in selected_countries:
            slice_ = df[(df['Year']==year) & (df['Area']==c) & (df['Item']==ind)]
            if not slice_.empty:
                values.append(float(slice_['Value'].iloc[0]))
                unit = slice_['Unit'].iloc[0]
            else:
                values.append(0)
        fig = create_bullet_chart(values, selected_countries,
                                  f'{ind} in {year}/{str(year+1)[-2:]}', unit)
        charts.append(dcc.Graph(figure=fig, style={'display': 'inline-block','width':'100%'}))
    return charts

def polynomial_fit(x, y, degree):
    coeffs = np.polyfit(x, y, degree)
    poly = np.poly1d(coeffs)
    ss_res = np.sum((y - poly(x))**2)
    ss_tot = np.sum((y - y.mean())**2)
    return poly, coeffs, 1 - ss_res/ss_tot

@app.callback(
    Output('scatter-plot', 'figure'),
    Input('xaxis-dropdown', 'value'),
    Input('yaxis-dropdown', 'value'),
    Input('size-dropdown', 'value'),
    Input('year-checklist', 'value'),
    Input('trendline-checkbox', 'value'),
    Input('regression-type-dropdown', 'value'),
    Input('country-radio', 'value')
)
def update_scatter(x_ind, y_ind, size_ind, yrs, trend_opt, deg, countries_sel):
    df_f = df[df['Year'].isin(yrs) & df['Area'].isin(countries_sel)]
    if df_f.empty:
        return go.Figure()
    pivot = df_f.pivot_table(values='Value', index=['Area','Year'], columns='Item').reset_index()
    fig = px.scatter(pivot, x=x_ind, y=y_ind, size=size_ind,
                     color='Area', hover_name='Area',
                     facet_col='Year', facet_col_wrap=2)
    if len(yrs)==1 and 'show' in trend_opt:
        df1 = pivot[pivot['Year']==yrs[0]]
        poly, coeffs, r2 = polynomial_fit(df1[x_ind], df1[y_ind], deg)
        xs = np.sort(df1[x_ind])
        ys = poly(xs)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines',
                                 line=dict(color='black',dash='dash'),
                                 name=f'Degree {deg}'))
        eq = " + ".join(f"{c:.4f}x^{len(coeffs)-i-1}" for i,c in enumerate(coeffs))
        eq = f"y = {eq}  (R²={r2:.3f})"
        fig.add_annotation(x=0.5,y=0.9, xref='paper', yref='paper',
                           text=eq, showarrow=False, font=dict(size=16))
    fig.update_layout(title=f'{x_ind} vs {y_ind}', height=700)
    return fig

@app.callback(
    Output('line-plot', 'figure'),
    Input('indicator-time-dropdown', 'value'),
    Input('country-time-checklist', 'value')
)
def update_line(selected_ind, countries_sel):
    fig = go.Figure()
    for c in countries_sel:
        dfc = df[(df['Area']==c)&(df['Item']==selected_ind)]
        if dfc.empty:
            continue
        dfc = dfc.groupby('Year',as_index=False)['Value'].mean().dropna()
        lw = 4 if dfc['Area Code'].iloc[0]>300 else 2
        fig.add_trace(go.Scatter(x=dfc['Year'], y=dfc['Value'],
                                 mode='lines+markers', name=c,
                                 line=dict(width=lw)))
    fig.update_layout(title=selected_ind, xaxis_title='Year', yaxis_title=selected_ind, height=600)
    return fig

@app.callback(
    [Output('year-slider','value'), Output('interval-component','disabled')],
    Input('animation-checkbox','value'),
    Input('interval-component','n_intervals'),
    State('year-slider','value')
)
def animate_year(anim,n_int, curr):
    if 'animate' in anim:
        nxt = curr+1 if curr<max(years) else max(years)
        return nxt, nxt==max(years)
    return curr, True

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
