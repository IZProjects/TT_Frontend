import dash
from dash import dcc, html, Input, Output, State, callback, clientside_callback
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
import requests
import json

# Register the page
dash.register_page(__name__, path='/update-password', title='Update Password')


layout = dmc.Container([
        dcc.Store(id='reset-tokens-store'),
        dmc.Center([
            dmc.Paper([
                dmc.Stack([
                    dmc.Title("Update Your Password", order=2, ta="center"),

                    dmc.Alert(
                        id="token-validation-alert",
                        title="Invalid Reset Link",
                        children="Invalid or expired reset link. Please request a new password reset.",
                        color="red",
                        variant="light",
                        style={"display": "none"}
                    ),

                    dmc.Stack([
                        dmc.PasswordInput(
                            id="new-password-input",
                            label="New Password",
                            placeholder="Enter your new password",
                            required=True,
                            w="100%",
                            style={'margin-bottom':'20px'}
                        ),

                        dmc.PasswordInput(
                            id="confirm-password-input",
                            label="Confirm New Password",
                            placeholder="Confirm your new password",
                            required=True,
                            w="100%",
                            style={'margin-bottom': '20px'}
                        ),

                        dmc.Button(
                            "Update Password",
                            id="update-password-button",
                            fullWidth=True,
                            loading=False,
                            variant="filled"
                        ),

                        dmc.Alert(
                            id="password-update-alert",
                            style={"display": "none", 'margin-bottom': '20px'}
                        )
                    ], id="password-form-stack")
                ])
            ], p="xl", radius="md", withBorder=True, shadow="sm")
        ], style={"paddingTop": "3rem"})
    ], size="xs")


# Client-side callback to extract tokens from URL fragment
clientside_callback(
    """
    function(pathname) {
        // Extract tokens from URL fragment
        const fragment = window.location.hash.substring(1);
        const params = new URLSearchParams(fragment);

        const tokens = {
            access_token: params.get('access_token'),
            refresh_token: params.get('refresh_token'),
            expires_at: params.get('expires_at'),
            token_type: params.get('token_type'),
            type: params.get('type')
        };

        return tokens;
    }
    """,
    Output('reset-tokens-store', 'data'),
    Input('url', 'pathname')
)


# Callback to validate tokens and show/hide form
@callback(
    [Output('token-validation-alert', 'style'),
     Output('password-form-stack', 'style')],
    Input('reset-tokens-store', 'data')
)
def validate_tokens(tokens):
    if not tokens or not tokens.get('access_token') or tokens.get('type') != 'recovery':
        return {"display": "block"}, {"display": "none"}
    return {"display": "none"}, {"display": "block"}


# Callback for password update
@callback(
    [Output('password-update-alert', 'children'),
     Output('password-update-alert', 'color'),
     Output('password-update-alert', 'style'),
     Output('update-password-button', 'loading'),
     Output('new-password-input', 'value'),
     Output('confirm-password-input', 'value')],
    Input('update-password-button', 'n_clicks'),
    [State('new-password-input', 'value'),
     State('confirm-password-input', 'value'),
     State('reset-tokens-store', 'data')]
)
def update_password(n_clicks, new_password, confirm_password, tokens):
    if not n_clicks:
        raise PreventUpdate

    # Validate inputs
    if not new_password or not confirm_password:
        return "Please fill in both password fields.", "red", {
            "display": "block"}, False, new_password, confirm_password

    if new_password != confirm_password:
        return "Passwords do not match.", "red", {"display": "block"}, False, new_password, confirm_password

    if len(new_password) < 6:
        return "Password must be at least 6 characters long.", "red", {
            "display": "block"}, False, new_password, confirm_password

    if not tokens or not tokens.get('access_token'):
        return "Invalid or expired reset link.", "red", {"display": "block"}, False, new_password, confirm_password

    try:
        # Make request to update password
        response = requests.post(
            'http://127.0.0.1:8050/update-password-api',  # Adjust URL as needed
            json={
                'password': new_password,
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token']
            },
            headers={'Content-Type': 'application/json'}
        )

        result = response.json()

        if response.status_code == 200:
            return [
                dmc.Text("Password updated successfully! "),
                dmc.Anchor("Click here to login", href="/login")
            ], "green", {"display": "block"}, False, "", ""
        else:
            return result.get('error', 'Failed to update password'), "red", {
                "display": "block"}, False, new_password, confirm_password

    except Exception as e:
        return f"Network error: {str(e)}", "red", {"display": "block"}, False, new_password, confirm_password

