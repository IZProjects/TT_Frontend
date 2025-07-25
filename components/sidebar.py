import dash_mantine_components as dmc
from dash_iconify import DashIconify


sidebar = dmc.Box(
    children = [
         dmc.NavLink(
            label="Discover",
            leftSection=DashIconify(icon="lets-icons:search-alt", width = 20),
            href='/',
            variant = "filled",
            active="exact",
            color = "indigo",
        ),
        dmc.NavLink(
            label="Company Overview",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            href="/02-page2",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Company",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            href="/company",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Subscription",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            href="/subscription",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Trend",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            href="/trend",
            active="exact",
            variant="filled",
            color="indigo",
        ),
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
            label="Pricing",
            leftSection=DashIconify(icon="ep:office-building", width=20),
            href="/pricing",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        ]
    )