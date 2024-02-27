from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc

app = Dash(external_stylesheets=[dbc.themes.SPACELAB])

table_header = [
    html.Thead(
        html.Tr(
            [
                html.Th("Status"),
                html.Th("Timestamp"),
                html.Th("Title"),
                html.Th("Comments"),
                html.Th("Results"),
                html.Th("Repeat"),
                html.Th("Download"),
                html.Th("Delete"),
            ]
        )
    )
]

app.layout = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("PLACE 0.10.0", href="/")),
                dbc.NavItem(
                    dbc.NavLink(
                        "Install",
                        href="https://anaconda.org/freemapa/place",
                        external_link=True,
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Documentation",
                        href="http://127.0.0.1:8050/documentation/index.html",
                        external_link=True,
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Source",
                        href="https://www.github.com/palab/place",
                        external_link=True,
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "PAL",
                        href="https://pal.blogs.auckland.ac.nz/",
                        external_link=True,
                    )
                ),
            ],
            navbar=True,
        ),
        html.H3(children="Experiment History", style={"textAlign": "left"}),
        dbc.NavLink("New Experiment", href="/new"),
        dbc.Table(table_header, bordered=True),
    ]
)


def start():
    app.run(debug=True)
