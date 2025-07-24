from dash import dcc, callback, Output, Input, dash_table, html, register_page, State
import dash_mantine_components as dmc
from urllib.parse import urlparse
import requests
from dash_iconify import DashIconify
from flask import session


register_page(__name__, path='/pricing', name='Pricing', title='tab title',
                   description="""google blurb description""") # '/' is home page

layout = dmc.Center(
    dmc.Paper(
        shadow="md",
        radius="md",
        p="xl",
        withBorder=True,
        style={"width": 300, "textAlign": "center"},
        children=[
            dmc.Group(
                mb="md",
                children=[
                    dmc.Badge("Most popular", color="gray", variant="light"),
                    dmc.Badge("Sandbox", color="dark", leftSection=DashIconify(icon="mdi:cube-outline", width=14))
                ]
            ),
            dmc.Text("Product Name", fw=600, size="lg"),
            dmc.Text("this is the description", c="dimmed", size="sm", mb="sm"),

            dmc.Group(
                align="baseline",
                children=[
                    dmc.Text("A$", size="xl", fw=700),
                    dmc.Text("1", size=40, fw=700),
                    dmc.Text("per month", size="sm", ml="xs", c="dimmed")
                ]
            ),

            html.A(
                dmc.Button("Subscribe", fullWidth=True, color="blue", mt="md"),
                #href=f"https://buy.stripe.com/test_aFa3cvb5M0r61Me4kc9bO00?prefilled_email={session.get('user').get('email')}?client_reference_id={session.get('user').get('id')}",
                target="_blank",  # Use "_blank" to open in new tab
                style={"textDecoration": "none"},  # removes underline
                id='stripe-payment-link',
            ),

            dmc.Text("This includes:", size="sm", mt="lg", mb="xs", fw=500),
            dmc.Group(
                children=[
                    DashIconify(icon="mdi:check-circle", width=16, color="gray"),
                    dmc.Text("feature 1, feature 2, feature 3", size="sm")
                ]
            )
        ]
    )
)

@callback(
    Output("stripe-payment-link", "href"),
     Input("user-data", "data")
)
def print_user_data(user_data):
    href = f"https://buy.stripe.com/test_aFa3cvb5M0r61Me4kc9bO00?prefilled_email={user_data.get('email')}&client_reference_id={user_data.get('id')}"
    return href
