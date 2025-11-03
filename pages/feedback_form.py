import dash
from dash import Dash, dcc, html, Input, Output, State, no_update, callback, ALL, ctx
import dash_mantine_components as dmc
import pandas as pd

dash.register_page(__name__, path='/feedback', name='feedback', title='tab title',
                   description="""google blurb description""") # '/' is home page


initial_values = [
    {"label": "Receive email notifications", "checked": False},
    {"label": "Receive sms notifications", "checked": False},
    {"label": "Receive push notifications", "checked": False},
]

# ------------------------------------------------ Page Layout --------------------------------------------------------
layout = dmc.Box([
    dmc.Title("Feedback Form", order=2, mb="md"),
    dmc.Divider(variant="solid", style={'margin-top': '5px', 'margin-bottom': '20px'}),
    dmc.Stack(
        gap="md",
        children=[
            dmc.Text("Please check the pages you found useful", fw=500),
            dmc.Stack([
                dmc.Checkbox(label="Discover Trends", id='DT-check'),
                dmc.Checkbox(label="Discover Companies", id='DC-check'),
                dmc.Checkbox(label="Trends", id='T-check'),
                dmc.Checkbox(label="Companies", id='C-check'),
            ], gap='xs', style={'margin-left':'20px','margin-bottom':'10px'}),

            dmc.Group([
                dmc.Text("Do you think this site will help you find trades?", fw=500),
                dmc.SegmentedControl(
                    id="helpful",
                    value="Yes",
                    data=["Yes", "No"],
                    mb=10,
                ),
            ], gap='xl', style={'margin-bottom':'10px'}),

            dmc.Textarea(
                id="new-data",
                label="What new data or features would you like to see us add?",
                placeholder="Add your comments here...",
                autosize=True, minRows=3, maxRows=8,
                style={'margin-bottom':'10px'}
            ),

            dmc.Textarea(
                id="criticism",
                label="Do you have any constructive criticism?",
                placeholder="Add your comments here...",
                autosize=True, minRows=3, maxRows=8,
                style={'margin-bottom': '10px'}
            ),

            dmc.Group([
                dmc.Text("Would you be willing to pay a monthly subscription to keep the site running?",
                         fw=500),
                dmc.SegmentedControl(
                    id="pay",
                    value="Yes",
                    data=["Yes", "No"],
                    mb=10,
                ),
                dmc.NumberInput(
                    id='how-much',
                    label="If so, how much?",
                    placeholder="Dollars",
                    prefix="$",
                    value=0,
                    w=250,
                    mb="md"
                ),
            ], gap='xl', style={'margin-bottom':'10px'}),

            dmc.Textarea(
                id="other",
                label="Other comments",
                placeholder="Add your comments here...",
                autosize=True, minRows=3, maxRows=8,
                style={'margin-bottom': '10px'}
            ),

            dmc.TextInput(
                id="email",
                label="Email",
                placeholder="you@example.com",
                withAsterisk=True,
                required=True,
                description="We'll only use this to follow up if needed.",
                style={'margin-bottom': '10px'}
            ),

            dmc.Button("Submit", id="submit"),
        ]
    ),
])
