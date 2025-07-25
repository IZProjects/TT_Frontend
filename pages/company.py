import dash
from dash import dcc, callback, Output, Input, dash_table, html
import pandas as pd
import dash_mantine_components as dmc


dash.register_page(__name__, path='/company', name='Landing Page', title='tab title',
                   description="""google blurb description""") # '/' is home page


layout = dmc.Box([
    html.H1(id="company_page"),

])

@callback(
    Output("company_page", "children"),
    [Input("page-tag", "data"),
     Input("page-metadata", "data"),]
)
def generate_page_text(tag, metadata):
    text = tag + ' ' + metadata
    return text