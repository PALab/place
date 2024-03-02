from dash import Dash, html, page_container, page_registry
import dash_bootstrap_components as dbc

app = Dash(
    external_stylesheets=[dbc.themes.SPACELAB],
    use_pages=True,
)

app.layout = html.Div(
    [
        dbc.NavbarSimple(
            children=[
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
                dbc.NavItem(
                    dbc.NavLink(
                        "PLACE Configuration",
                        href="/configuration",
                    )
                ),
            ],
            brand="PLACE 0.10.0",
            brand_href="/",
            color="primary",
            dark=True,
        ),
        dbc.Nav(
            [
                dbc.NavItem(
                    dbc.NavLink(
                        "Experiments",
                        href=page_registry["pages.experiments"]["path"],
                        active="exact",
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "New", href=page_registry["pages.new"]["path"], active="exact"
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Configuration",
                        href=page_registry["pages.configuration"]["path"],
                        active="exact",
                    )
                ),
            ],
            pills=True,
        ),
        page_container,
        html.Div(
            [
                html.Footer(
                    "Python Laboratory Automation, Control, and Experimentation (PLACE)",
                    style={"textAlign": "center"},
                ),
                html.Footer(
                    "Version: 0.10.0 | Authors: Paul Freeman, Jonathan Simpson | 2018-2023",
                    style={"textAlign": "center"},
                ),
                html.Footer(
                    "Originally created by: Jami L Johnson, Henrik tom Wörden, and Kasper van Wijk)",
                    style={"textAlign": "center"},
                ),
            ]
        ),
    ]
)


def start():
    app.run(debug=True)
