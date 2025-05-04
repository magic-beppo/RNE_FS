# navbar.py
import os
from dash import dcc, html

# 1) Which deployment are we in?
#    ➤ In Railway:   export DEPLOYMENT=railway
#    ➤ In AWS:       export DEPLOYMENT=aws
#    ➤ Locally:      defaults to "aws"
DEPLOYMENT = os.getenv("DEPLOYMENT", "aws").lower()

# 2) Declare every menu‐item once, with:
#     - the icon class
#     - the visible label
#     - the "slug" used on Railway
#     - the "slug" used on AWS
ROUTES = {
    "home-link":      ("fas fa-home",       "Home",               "menu",           "home-aws"),
    "Macro1":         ("fas fa-chart-line", "Macro-WEO",          "macroimf",       "macro-imf"),
    "Macro2":         ("fas fa-chart-line", "Macro-FAO",          "macrofao",       "fao-macro"),
    "SOI":            ("fas fa-chart-line", "FS Indicators",      "fs",             "fs-indicators"),
    "SUA":            ("fas fa-database",   "SUA Balances",       "balances",       "balances"),
    "Trade Analyst":  ("fas fa-database",   "Trade Analyst",      "tradeanalyst",   "trade-analyst"),
    "Tracker":        ("fas fa-database",   "Food Trade Tracker", "food",           "trade-tracker"),
    "FIB":            ("fas fa-database",   "Food Import Bill",   "fib",            "fibs"),
    "VW":             ("fas fa-database",   "Virtual Water",      "virtualwater",   "virtual-water"),
    "Precipitation":  ("fas fa-database",   "Precipitation",      "precipitation",  "precipitation"),
    "Diversity":      ("fas fa-database",   "Crop Diversity",     "distributions",  "distributions"),
    "Fertilizer":     ("fas fa-database",   "Fertilizer",         "fertilizer",     "fertilizer"),
    "SDGs":           ("fas fa-database",   "SDGs",               "sdg",            "sdg"),
}

def Navbar():
    links = [
        dcc.Location(id="url", refresh=False)
    ]

    for _id, (icon, label, slug_r, slug_a) in ROUTES.items():
        if DEPLOYMENT == "railway":
            domain = f"rne{slug_r}-production.up.railway.app"
        else:  # aws
            # if we don’t have an AWS slug, skip it
            if not slug_a:
                continue
            domain = f"{slug_a}.fsobs.org"

        href = f"https://{domain}/"
        links.append(
            html.A(
                [ html.I(className=icon), f" {label}" ],
                href=href,
                id=_id,
                className="nav-link"
            )
        )

    return html.Nav(className="navbar", children=links)
