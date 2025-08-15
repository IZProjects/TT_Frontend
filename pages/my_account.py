from dash import dcc, callback, Output, Input, dash_table, html, register_page, State
import pandas as pd
import dash_mantine_components as dmc
import requests
import flask


register_page(__name__, path='/my_account', name='My Account', title='My Account')


layout = dmc.Box([
    dmc.Title(f"My Account", order=1, style={'margin-bottom':'40px', 'margin-left':'30px'}),
    dmc.Container(id='account-name', fluid=True, style={'margin-left':'30px'}),
    dmc.Divider(variant="solid", style={'margin-bottom':'20px', 'margin-top':'20px', 'margin-left':'30px', 'margin-right':'30px'}),
    dmc.Container(id='account-email', fluid=True, style={'margin-left':'30px'}),
    dmc.Divider(variant="solid", style={'margin-bottom':'20px', 'margin-top':'20px', 'margin-left':'30px', 'margin-right':'30px'}),
    dmc.Container(id='account-sub-status', fluid=True, style={'margin-left':'30px'}),

])

@callback(
     [Output("account-name", "children"),
      Output("account-email", "children"),
      Output("account-sub-status", "children"),],
     [Input("user-data", "data"),
      Input("sub-token", "data"),]
)
def print_user_data(user_data, sub_token):
    change_password_btn = html.A(
        dmc.Button("Change Password", color="blue", mt="md"),
        href=f"/reset-password",
        target="_self",
        style={"textDecoration": "none"},
    )

    sub_btn = html.A(
        dmc.Button("Manage Subscription", color="blue", mt="md"),
        href=f"https://billing.stripe.com/p/login/test_aFa3cvb5M0r61Me4kc9bO00",
        target="_blank",
        style={"textDecoration": "none"},
    )

    if sub_token == '453T73R90U2104E83':
        sub_status = 'Active'
    else:
        sub_status = 'Free'

    name = dmc.SimpleGrid(
        children=[
            dmc.Text('Name:', fw=700, size='lg'),
            dmc.Text(user_data.get('name'), size='lg'),
        ],
        cols={"base": 1, "md": 3}
    )

    email = dmc.SimpleGrid(
        children=[
            dmc.Text('Email:', fw=700, size='lg'),
            dmc.Text(user_data.get('email'), size='lg'),
            change_password_btn
        ],
        cols={"base": 1, "md": 3}
    )

    sub = dmc.SimpleGrid(
        children=[
            dmc.Text('Subscription Status', fw=700, size='lg'),
            dmc.Text(sub_status, size='lg'),
            sub_btn
        ],
        cols={"base": 1, "md": 3}
    )

    return name, email, sub