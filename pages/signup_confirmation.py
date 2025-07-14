from dash import html, register_page
import dash_mantine_components as dmc

register_page(__name__, path='/signup-confirmation', name='Signup Confirmation')

layout = dmc.Center(
    dmc.Paper(
        shadow='lg',
        withBorder=True,
        p="30px",
        mt=60,
        children=[
            dmc.Text("📧 Check your inbox!", size='lg', fw=700),
            dmc.Text("We sent you a confirmation email. Click the link to finish signing up.", size='sm', mt=10),
            dmc.Text("After confirming, you can return and log in.", size='sm', c='dimmed', mt=5)
        ]
    )
)
