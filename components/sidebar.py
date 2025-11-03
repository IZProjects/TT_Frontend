import dash_mantine_components as dmc
from dash_iconify import DashIconify


sidebar = dmc.Box(
    children = [

        dmc.NavLink(
            label="Discover Trends",
            leftSection=DashIconify(icon="iconamoon:trend-up-bold", width=25),
            #href="/discover-trends",
            href="/",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Discover Companies",
            leftSection=DashIconify(icon="ep:office-building", width=25),
            href="/discover-companies",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.Divider(variant="solid", style={'margin-top': '5px', 'margin-bottom': '5px'}),
        dmc.NavLink(
            label="Login",
            leftSection=DashIconify(icon="material-symbols:login", width=25),
            href="/login",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Sign Up",
            leftSection=DashIconify(icon="icons8:add-user", width=25),
            href="/signup",
            active="exact",
            variant="filled",
            color="indigo",
        ),

        dmc.NavLink(
            label="My Account",
            leftSection=DashIconify(icon="mdi:user", width=25),
            href="/my_account",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.Divider(variant="solid", style={'margin-top': '5px', 'margin-bottom': '5px'}),
        dmc.NavLink(
            label="Pricing",
            leftSection=DashIconify(icon="material-symbols:upgrade", width=25),
            href="/pricing",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.Divider(variant="solid", style={'margin-top': '5px', 'margin-bottom': '5px'}),
        dmc.NavLink(
            label="FAQ",
            leftSection=DashIconify(icon="mdi:faq", width=25),
            href="/faq",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="feedback",
            leftSection=DashIconify(icon="mdi:faq", width=25),
            href="/feedback",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        ]
    )