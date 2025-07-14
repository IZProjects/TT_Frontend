import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import dash_mantine_components as dmc
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd

app = dash.Dash(__name__)

data = [
  {"date": "Mar 22", "Apples": 2890, "Oranges": 2338, "Tomatoes": 2452},
  {"date": "Mar 23", "Apples": 2756, "Oranges": 2103, "Tomatoes": 2402},
  {"date": "Mar 24", "Apples": 3322, "Oranges": 986, "Tomatoes": 1821},
  {"date": "Mar 25", "Apples": 3470, "Oranges": 2108, "Tomatoes": 2809},
  {"date": "Mar 26", "Apples": 3129, "Oranges": 1726, "Tomatoes": 2290}
]


# Dummy data for plotting
def create_figure(i):
    fig = dmc.LineChart(
        h=300,
        dataKey="date",
        data=data,
        series=[
            {"name": "Apples", "color": "indigo.6"},
            {"name": "Oranges", "color": "blue.6"},
            {"name": "Tomatoes", "color": "teal.6"}
        ],
        curveType="linear",
        tickLine="xy",
        withXAxis=False,
        withDots=False,
    )
    return fig

# Card with locked overlay
def locked_card(i):
    return dmc.Paper(
        children=[
            dmc.LineChart(
                h=300,
                dataKey="date",
                data=data,
                series=[
                    {"name": "Apples", "color": "indigo.6"},
                    {"name": "Oranges", "color": "blue.6"},
                    {"name": "Tomatoes", "color": "teal.6"}
                ],
                curveType="linear",
                tickLine="xy",
                withXAxis=False,
                withDots=False,
            ),
            html.Div(
                children=[
                    dmc.Button(
                        "🔒 Unlock this trend now!",
                        variant="gradient",
                        gradient={"from": "violet", "to": "blue"},
                        size="md",
                        radius="md",
                        style={"zIndex": 2}
                    )
                ],
                style={
                    "position": "absolute",
                    "top": 0,
                    "left": 0,
                    "right": 0,
                    "bottom": 0,
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "backdropFilter": "blur(4px)",
                    "backgroundColor": "rgba(255, 255, 255, 0.7)",
                    "zIndex": 1,
                    "borderRadius": "12px"
                }
            )
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        style={"position": "relative", "overflow": "hidden"}
    )

cards = []
for i in range(10):
    cards.append(locked_card(i))

# Layout with Grid
layout = dmc.Container([
    dmc.Title("Locked Trends"),
    dmc.SimpleGrid(cards, cols={"base": 1, "md": 3},),
], fluid=True, style={"padding": "2rem"})

app.layout = dmc.MantineProvider(id="mantine-provider",children=[layout])




if __name__ == "__main__":
    app.run(debug=True)
