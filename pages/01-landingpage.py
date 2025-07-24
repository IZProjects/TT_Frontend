from dash import dcc, callback, Output, Input, dash_table, html, register_page, State
import pandas as pd
import dash_mantine_components as dmc
import requests
import flask


register_page(__name__, path='/', name='Landing Page', title='tab title',
                   description="""google blurb description""") # '/' is home page


layout = dmc.Box([
    html.H1(children="Google metadata title/description", hidden=True),
    html.H1(id='page1-user-data'),
    html.H1(id='page1-user-access_token'),

])

@callback(
    [Output("page1-user-data", "children"),
     Output("page1-user-access_token", "children")],
     [Input("user-data", "data"),
      Input("user-access_token", "data"),]
)
def print_user_data(user_data, User_access_token):
    return str(user_data), User_access_token


