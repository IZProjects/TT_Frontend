import dash_mantine_components as dmc
from dash_iconify import DashIconify


sidebar = dmc.Box(
    children = [

        dmc.NavLink(
            label="Discover Trends",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            #href="/discover-trends",
            href="/",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Discover Companies",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            href="/discover-companies",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.Divider(variant="solid", style={'margin-top': '5px', 'margin-bottom': '5px'}),
        dmc.NavLink(
            label="Login",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            href="/login",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Sign Up",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            href="/signup",
            active="exact",
            variant="filled",
            color="indigo",
        ),

        dmc.NavLink(
            label="My Account",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            href="/my_account",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.Divider(variant="solid", style={'margin-top': '5px', 'margin-bottom': '5px'}),
        dmc.NavLink(
            label="Pricing",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            href="/pricing",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        ]
    )