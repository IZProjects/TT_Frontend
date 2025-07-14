from dash import Dash, dcc, Input, Output, callback, State, page_container, clientside_callback, ClientsideFunction, _dash_renderer
import dash_mantine_components as dmc
from components.header import header
from components.sidebar import sidebar
import os
from dotenv import load_dotenv
from flask import Flask, request, redirect, session, jsonify
from supabase_client import supabase

# ----------------------------- LOAD ENVIROMENT VARIABLES --------------------------------
load_dotenv()
flask_secret_key = os.getenv("SECRET_KEY")

# --------------------------------- Set up Flask Server ----------------------------------------------------------------
server = Flask(__name__)
#server.config.update(SECRET_KEY=flask_secret_key)
server.config.update(
    SECRET_KEY=flask_secret_key,
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True  # Required when using SameSite=None
)
#FOR PRODUCTION WHEN LAUNCHING
"""server.config.update(
    SECRET_KEY=flask_secret_key,
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE = True
)"""


# --------------------------------- Supabase Google OAuth --------------------------------------------------------------
@server.route("/signin/google")
def signin_with_google():
    response = supabase.auth.sign_in_with_oauth(
        {
            "provider": "google",
            "options": {
	            "redirect_to": f"{request.host_url}callback"
	        },
        }
    )
    return redirect(response.url)

@server.route("/callback")
def callback():
    code = request.args.get("code")
    next = request.args.get("next", "/")

    if code:
        # 1. Exchange the code for a session
        response = supabase.auth.exchange_code_for_session({"auth_code": code})
        access_token = response.session.access_token

        # 2. Get user info using the access token (best practice)
        user_response = supabase.auth.get_user(access_token)
        user = user_response.user

        # 3. Store user and token in Flask session
        session["access_token"] = access_token
        session["user"] = {
            "id": user.id,
            "email": user.email,
            "name": user.user_metadata.get("full_name"),
        }

    return redirect(next)

# --------------------------------- Supabase Email Sign Up -------------------------------------------------------------
@server.route("/signup", methods=["POST"])
def handle_signup():
    email = request.form.get("email")
    password = request.form.get("password")
    first_name = request.form.get("given_name")
    last_name = request.form.get("family_name")

    if not email or not password:
        return redirect("/signup#error_signup")

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "email_redirect_to": f"{request.host_url}welcome",
                "data": {
                    "full_name": f"{first_name} {last_name}"
                }
            }
        })

        # store metadata in session for later
        session["pending_email"] = email

        # Redirect to confirmation instruction page
        return redirect("/signup-confirmation")

    except Exception as e:
        return redirect("/signup#error_signup")

# --------------------------------- Supabase Resend Sign up confirmation ---------------------------------------------

@server.route("/resend-confirmation")
def resend_confirmation():
    pending_email = session.get("pending_email")

    if not pending_email:
        return redirect("/signup-confirmation#error_no_email")

    try:
        response = supabase.auth.resend({
            "type": "signup",
            "email": pending_email,
            "options": {
                "email_redirect_to": f"{request.host_url}welcome",
            },
        })
        return redirect("/signup-confirmation?resent=true")

    except Exception as e:
        return redirect("/signup-confirmation?resent=true#error_no_resend")


# --------------------------------- Supabase Email Sign In -------------------------------------------------------------
@server.route("/signin/email", methods=["POST"])
def signin_with_email():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return "Missing email or password", 400

    try:
        # Sign in via Supabase
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        access_token = response.session.access_token

        # Get user info
        user_response = supabase.auth.get_user(access_token)
        user = user_response.user

        # Save session
        session["access_token"] = access_token
        session["user"] = {
            "id": user.id,
            "email": user.email,
            "name": user.user_metadata.get("full_name"),
        }

        return redirect("/")  # Redirect after login

    except Exception as e:
        return redirect("/login#loginerror")  # Optional error handling

# --------------------------------- Supabase Reset Password ------------------------------------------------------------
@server.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        res = supabase.auth.reset_password_for_email(
            email,
            {"redirect_to": f"{request.host_url}update-password"}  # e.g. http://127.0.0.1:8050/update-password
        )
        if getattr(res, "error", None):
            return jsonify({"error": res.error.message}), 400

        return jsonify({"message": "Reset link sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -------------------------------------- Supabase Sign Out -------------------------------------------------------------
@server.route("/logout")
def logout():
    try:
        # Sign out from Supabase
        supabase.auth.sign_out()
    except Exception as e:
        print("Supabase sign-out error:", e)

    # Clear Flask session
    session.clear()

    # Redirect to homepage or login page
    return redirect("/login")  # or wherever you want the user to land after logging out



# --------------------------------- DASH APP CONFIG --------------------------------------------------------------------
_dash_renderer._set_react_version("18.2.0")
app = Dash(__name__, server=server, use_pages=True, external_stylesheets=dmc.styles.ALL, title='Google Search Title')

layout = dmc.AppShell(
    [
        dcc.Location(id='url', refresh=True),
        dcc.Store(id='user-info', data=['no']), #update this later
        dcc.Store(id='page-tag'),
        dcc.Store(id='page-metadata'),
        dcc.Store(id='user-data'),
        dcc.Store(id='user-access_token'),
        dmc.AppShellHeader(header, style={'padding-left': '20px', 'padding-right': '20px'}),
        dmc.AppShellNavbar(sidebar, style={'padding-left': '10px', 'padding-right': '10px', 'padding-top': '20px'}),
        dcc.Loading([
            dmc.AppShellMain(page_container),
        ], style={"position":"absolute", "top":"20%"})
    ],
    header={"height": 48},
    navbar={"width": 250, "breakpoint": "md", "collapsed": {"mobile": True}},
    padding="md",
    id="appshell",
)

app.layout = dmc.MantineProvider(id="mantine-provider",children=[layout])

# ---------------------------------- NAVBAR CALLBACK -------------------------------------------------------------------

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='side_bar_toggle'
    ),
    Output("appshell", "navbar"),
    Input("burger-button", "opened"),
    State("appshell", "navbar"),
)

# ------------------------------------ THEME CALLBACK -----------------------------------------------------------------

clientside_callback(
    """
    function(path, opened) {
        if (opened) {
            return !opened;
        }
        return opened;
    }
    """,
    Output("burger-button", "opened"),
    Input("url", "pathname"),
    State("burger-button", "opened"),
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_theme'
    ),
    Output("mantine-provider", "forceColorScheme"),
    Output("mantine-provider", "theme"),
    Input("color-scheme-switch", "checked"),
)

@app.callback(
    [Output("user-data", "data"),
     Output("user-access_token", "data"),],
     Input('url', 'pathname'),
)
def save_user_esssion(url):
    """
    Returns:
        user-data (dict): {'email': 'asde3t@gmail.com', 'id': '771643fd-4e07-4543-a3d1-f98fd11732ab', 'name': 'Ivan Zheng'}
        user-access_token (str): eyJhbGciOiJIUzI1NiIsImtpZCI6InczS0lUVjRnMENidXlNOFEiLCJ0eXAiOiJKV1QifQ.ey

    """
    print(session.get("user"))
    print(session.get("access_token"))
    return session.get("user"), session.get("access_token")


if __name__ == "__main__":
    app.run(debug=False)

