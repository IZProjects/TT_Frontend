from dash import dcc, callback, Output, Input, dash_table, html, register_page, State
import dash_mantine_components as dmc
from urllib.parse import urlparse
import requests
from dash_iconify import DashIconify
from flask import session


register_page(__name__, path='/pricing', name='Pricing', title='tab title',
                   description="""google blurb description""") # '/' is home page

card_free = dmc.Card(
    shadow="md",
    radius="md",
    #p="xl",
    withBorder=True,
    w=300,
    style={"textAlign": "center"},
    children=[
        dmc.Group(
            mb="md",
            justify='space-around',
            children=[
                dmc.Badge("Most popular", color="gray", variant="light"),
                dmc.Badge("Sandbox", color="dark", leftSection=DashIconify(icon="mdi:cube-outline", width=14))
            ]
        ),
        dmc.Title("Free", order=2),
        dmc.Text("this is the description", c="dimmed", size="sm", mb="sm"),

        dmc.Title("$0", order=1),
        dmc.Text("USD/month", size="sm", ml="xs", c="dimmed"),

        dmc.Container(id='Free_btn'),

        dmc.Text("This includes:", size="sm", mt="lg", mb="xs", fw=500),
        dmc.Group(
            children=[
                DashIconify(icon="mdi:check-circle", width=16, color="gray"),
                dmc.Text("feature 1, feature 2, feature 3", size="sm")
            ]
        )
    ]
)

card_sub = dmc.Card(
    shadow="md",
    radius="md",
    #p="xl",
    withBorder=True,
    w=300,
    style={"textAlign": "center"},
    children=[
        dmc.Group(
            mb="md",
            justify='space-around',
            children=[
                dmc.Badge("Most popular", color="gray", variant="light"),
                dmc.Badge("Sandbox", color="dark", leftSection=DashIconify(icon="mdi:cube-outline", width=14))
            ]
        ),
        dmc.Title("Pro Tier", order=2),
        dmc.Text("this is the description", c="dimmed", size="sm", mb="sm"),

        dmc.Title("$1", order=1),
        dmc.Text("USD/month", size="sm", ml="xs", c="dimmed"),

        dmc.Container(id='Sub_btn'),

        dmc.Text("This includes:", size="sm", mt="lg", mb="xs", fw=500),
        dmc.Group(
            children=[
                DashIconify(icon="mdi:check-circle", width=16, color="gray"),
                dmc.Text("feature 1, feature 2, feature 3", size="sm")
            ]
        )
    ]
)

layout = dmc.Box([
    dmc.Stack([
        dmc.Title("Our Plans & Pricing", order=1),
        dmc.Text("Enjoy Tradeable Trends Pro risk free with a 30 day free trail.", size='lg'),
    ], align='center', style={'margin-bottom': '80px'}),
    dmc.Flex(
    children=[
        card_free,
        card_sub,
    ],
    direction={"base": "column", "sm": "row"},
    justify='center',
    align='center',
    gap=100
)
])



@callback(
    [Output("Free_btn", "children"),
     Output("Sub_btn", "children"),],
     [Input("sub-token", "data"),
      Input("user-data", "data")]
)
def print_user_data(sub_token,user_data):
    if user_data != None:
        if sub_token == '52F31A09L75S48E41':
            free_btn = html.A(
                dmc.Button("Current Plan", fullWidth=True, color="blue", mt="md", disabled=True),
                style={"textDecoration": "none"},  # removes underline
            ),

            sub_btn = html.A(
                dmc.Button("Subscribe", fullWidth=True, color="blue", mt="md"),
                target="_blank",  # Use "_blank" to open in new tab
                style={"textDecoration": "none"},  # removes underline
                href=f"https://buy.stripe.com/test_aFa3cvb5M0r61Me4kc9bO00?prefilled_email={user_data.get('email')}&client_reference_id={user_data.get('id')}",
            ),

        else:
            free_btn = html.A(
                dmc.Button("Cancel subscription", fullWidth=True, color="blue", mt="md"),
                target="_blank",  # Use "_blank" to open in new tab
                href=f"https://billing.stripe.com/p/login/test_aFa3cvb5M0r61Me4kc9bO00",
                style={"textDecoration": "none"},  # removes underline
            ),

            sub_btn = html.A(
                dmc.Button("Current Plan", fullWidth=True, color="blue", mt="md", disabled=True),
                style={"textDecoration": "none"},  # removes underline
            ),
    else:
        free_btn = html.A(
            dmc.Button("Subscribe", fullWidth=True, color="blue", mt="md"),
            target="_self",  # Use "_blank" to open in new tab
            href="/login",
            style={"textDecoration": "none"},  # removes underline
        ),

        sub_btn = html.A(
            dmc.Button("Subscribe", fullWidth=True, color="blue", mt="md"),
            target="_self",  # Use "_blank" to open in new tab
            style={"textDecoration": "none"},  # removes underline
            href="/login",
        ),


    return free_btn, sub_btn