from dash import html, register_page, dcc, Input, Output, callback
import dash_mantine_components as dmc

register_page(__name__, path='/signup-confirmation', name='Signup Confirmation')

layout = dmc.Center(
    dmc.Paper(
        shadow='lg',
        withBorder=True,
        p="30px",
        mt=60,
        children=[
            dmc.Container(id='resend-error', style={'margin-bottom': '20px'}),
            dmc.Text("📧 Check your inbox!", size='lg', fw=700),
            dmc.Text("We sent you a confirmation email. Click the link to finish signing up.", size='sm', mt=10),
            dmc.Text("After confirming, you can return and log in.", size='sm', c='dimmed', mt=5, style={'margin-bottom': '20px'}),
            html.A("Resend confirmation email", href="/resend-confirmation", target="_self", style={"fontSize": "14px"}),
            dmc.Text(id="resend-message", size='sm', c='dimmed', mt=5),
        ]
    )
)

@callback(
    Output("resend-message", "children"),
    Input("url", "search")
)
def show_resend_message(search):
    from urllib.parse import parse_qs
    params = parse_qs(search.lstrip("?"))
    if "resent" in params:
        return "A new confirmation email has been sent!"
    return ""

@callback(
    Output("resend-error", "children"),
      Input('url', 'hash'),
)
def login_error(hash):
    if "#error_no_email" in hash:
        alert = dmc.Alert(
            children=["Sorry! An error has occurred. Please to sign up again.", dmc.Anchor(children="sign Up", href='/signup')],
            title="Error",
            color="red",
            withCloseButton=True,
            hide=False
        ),
    elif "#error_no_resend" in hash:
        alert = dmc.Alert(
            children=["Please wait 60 seconds before trying to resend again"],
            title="Error",
            color="red",
            withCloseButton=True,
            hide=False
        ),
    else:
        alert = ''

    return alert