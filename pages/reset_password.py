from dash import dcc, callback, Output, Input, dash_table, html, register_page, State
import dash_mantine_components as dmc
from urllib.parse import urlparse
import requests


register_page(__name__, path='/reset-password', name='Reset Password', title='tab title',
                   description="""google blurb description""") # '/' is home page


layout = dmc.Center(
    dmc.Paper(
        shadow='lg',
        withBorder=True,
        p="30px",
        mt=60,
        children=[
            html.Div(id="reset-error-message"),
            dmc.Title("Forgot Password", order=2, style={'margin-bottom':'20px'}),
            dmc.Text("Enter the email address associated with your account and we will send you a link to reset your password.",
                     size='sm',
                     style={'margin-bottom':'20px'}),
            dmc.TextInput(label="Email", placeholder="Email", id="reset-email", required=True, style={'margin-bottom':'30px'}),
            dmc.Button("Request Password Reset", id="reset-btn", style={'margin-bottom':'30px'}),
            html.Div(id="reset-status"),
        ],
    )
)


@callback(
    Output("reset-status", "children"),
    Input("reset-btn", "n_clicks"),
    State("reset-email", "value"),
    State("url", "href"),  # dcc.Location must be in layout
    prevent_initial_call=True
)
def send_reset_email(n_clicks, email, href):
    if not email:
        return "Please enter an email."

    try:
        # Dynamically extract the base URL
        parsed = urlparse(href)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        # Send POST request to Flask route using dynamic URL
        response = requests.post(f"{base_url}/reset-password", json={"email": email})
        result = response.json()
        if "error" in result:
            alert = dmc.Alert(
                children=result.get("error"),
                title="Error!",
                color="red",
                withCloseButton=True,
                hide=False
            )
        else:
            alert = dmc.Alert(
                children=result.get("message"),
                title="Success!",
                color="green",
                withCloseButton=True,
                hide=False
            )

        return alert
    except Exception as e:
        alert = dmc.Alert(
            "Please try again.",
            title="Error",
            color="red",
            withCloseButton=True,
            hide=False
        ),
        return alert


@callback(
    Output("reset-error-message", "children"),
    Input('url', 'hash'),
)
def login_error(hash):
    if "#error" in hash:
        alert = dmc.Alert(
            children="Sorry! An error has occurred. Please try again.",
            title="Error",
            color="red",
            withCloseButton=True,
            hide=False
        ),
    else:
        alert = ''

    return alert