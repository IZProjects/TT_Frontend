import dash
from dash import dcc, callback, Output, Input, dash_table, html
import pandas as pd
import dash_mantine_components as dmc


dash.register_page(__name__, path='/subscription', name='Landing Page', title='tab title',
                   description="""google blurb description""") # '/' is home page


layout = dmc.Box([
    html.H1(children="Pay Me Pls"),

])

