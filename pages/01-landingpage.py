from dash import dcc, callback, Output, Input, dash_table, html, register_page
import pandas as pd
import dash_mantine_components as dmc
import requests
import flask


register_page(__name__, path='/', name='Landing Page', title='tab title',
                   description="""google blurb description""") # '/' is home page


layout = dmc.Box([
    html.H1(children="Google metadata title/description", hidden=True),
    html.H1(children="Page 1"),
])

