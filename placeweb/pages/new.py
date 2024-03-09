from dash import html, register_page, page_registry
import dash_bootstrap_components as dbc

register_page(__name__)


def layout():
    return html.Div(
        [
            html.H3(children="New Experiment", style={"textAlign": "left"}),
        ]
    )
