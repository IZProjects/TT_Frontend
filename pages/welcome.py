from dash import dcc, Input, Output, callback, register_page, html
import dash_mantine_components as dmc

register_page(__name__, path='/welcome', name='Welcome', title='Welcome!')

layout = dmc.Center(id='welcome_page_holder')

@callback(
    Output("welcome_page_holder", "children"),
      Input('url', 'hash'),
)
def generate_welcome_page(hash):
    if "#error" in hash:
        content = dmc.Paper(
            shadow='md',
            withBorder=True,
            p="40px",
            mt=60,
            children=[
                dmc.Text("An error has occurred. Please try again", size='xl', fw=700),
                dmc.Text("We apologise for the inconvenience.", mt=10),
                dcc.Link("Return to Sign Up", href="/signup", style={"marginTop": "20px", "display": "block"}),
                dmc.Text(size='xl', fw=700, id="tester12"),
            ]
        )
    else:
        content = dmc.Paper(
            shadow='md',
            withBorder=True,
            p="40px",
            mt=60,
            children=[
                dmc.Text("🎉 Email confirmed!", size='xl', fw=700),
                dmc.Text("Thanks for confirming your email. You can now log in.", mt=10),
                dcc.Link("Go to Login", href="/login", style={"marginTop": "20px", "display": "block"}),
                dmc.Text(size='xl', fw=700, id="tester12"),
            ]
        )
    return content