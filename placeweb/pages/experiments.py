from dash import html, register_page, page_registry
import dash_bootstrap_components as dbc

register_page(__name__, path="/")


def layout():
    return html.Div(
        [
            html.H3(children="Experiment History", style={"textAlign": "left"}),
            dbc.NavLink("New Experiment", href=page_registry["pages.new"]["path"]),
            html.Div(
                [
                    dbc.Table(
                        [
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
                        ],
                        bordered=True,
                    )
                ],
            ),
        ]
    )
