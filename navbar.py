from dash import dcc, html


def Navbar():
    return html.Nav(
        className="navbar",
        children=[
            dcc.Location(id='url', refresh=False),
            
            html.A([html.I(className="fas fa-home"), " Home"], href="https://rnemenu-production.up.railway.app/", id='home-link', className="nav-link"),
            
            html.A([html.I(className="fas fa-chart-line"), "Macro-WEO"], href="https://rnemacroimf-production.up.railway.app/", id='Macro1', className="nav-link"),

            html.A([html.I(className="fas fa-chart-line"), "Macro-FAO"], href="https://rnemacrofao-production.up.railway.app/", id='Macro2', className="nav-link"),
            
            html.A([html.I(className="fas fa-chart-line"), "FS Indicators"], href="https://rnefs-production.up.railway.app/", id='SOI', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " SUA Balances"], href="https://rnebalances-production.up.railway.app/", id='SUA', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Trade Analyst"], href="https://rnetradeanalyst-production.up.railway.app/", id='Trade Analyst', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Food Trade Tracker"], href="https://rnefood-production.up.railway.app/", id='Tracker', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Food Import Bill"], href="https://rnefib-production.up.railway.app/", id='FIB', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Virtual Water"], href="https://rnevirtualwater-production.up.railway.app/", id='VW', className="nav-link"),

            html.A([html.I(className="fas fa-database"), " Precipitation"], href="https://rneprecipitation-production.up.railway.app/", id='Precipitation2', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Crop Diversity"], href="https://rnedistributions-production.up.railway.app/", id='Diversity', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Fertilizer"], href="https://rnefertilizer-production.up.railway.app/", id='Fertilizer', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " SDGs"], href="https://rnesdg-production.up.railway.app/", id='SDGs', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Trade Concentration"], href="https://rneconcentrations-production.up.railway.app/", id='Concentraton', className="nav-link"),
            
        ],
    )

