from dash import dcc, html


def Navbar():
    return html.Nav(
        className="navbar",
        children=[
            dcc.Location(id='url', refresh=False),
            
            html.A([html.I(className="fas fa-home"), " Home"], href="https://morocco-menu-production.up.railway.app/", id='home-link', className="nav-link"),
            
            html.A([html.I(className="fas fa-chart-line"), "Macro-WEO"], href="https://faomorocco8-production.up.railway.app/", id='Macro1', className="nav-link"),

            html.A([html.I(className="fas fa-chart-line"), "Macro-FAO"], href="https://faomorocco12-production.up.railway.app", id='Macro2', className="nav-link"),
            
            html.A([html.I(className="fas fa-chart-line"), "FS Indicators"], href="https://faomorocco2-production.up.railway.app/", id='SOI', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " SUA Balances"], href="https://psdmorocco-production.up.railway.app/", id='SUA', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Trade Analyst"], href="https://faomorocco3-production.up.railway.app/", id='Trade Analyst', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Trade Tracker"], href="https://faomorocco4-production.up.railway.app/", id='Tracker', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Food Import Bill"], href="https://faomorocco5-production.up.railway.app/", id='FIB', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Virtual Water"], href="https://faomorocco6-production.up.railway.app/", id='Precipitation1', className="nav-link"),

            html.A([html.I(className="fas fa-database"), " Precipitation"], href="https://faomorocco9-production.up.railway.app//", id='Precipitation2', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Crop Diversity"], href="https://faomorocco10-production.up.railway.app/", id='Diversity', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " Fertilizer"], href="https://faomorocco11-production.up.railway.app/", id='Fertilizer', className="nav-link"),
            
            html.A([html.I(className="fas fa-database"), " GAEZ"], href="https://faomorocco11-production.up.railway.app/", id='GAEZ', className="nav-link"),
            
        ],
    )

