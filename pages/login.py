from dash import html, register_page, dcc, Input, Output, callback
from dash_iconify import DashIconify
import dash_mantine_components as dmc


register_page(__name__, path='/login', name='Login', title='tab title',
                   description="""google blurb description""") # '/' is home page

loginButtonStyle = {
    "background": "royalblue",
    "padding": "5px 20px",
    "border": "none",
    "borderRadius": "20px",
    "color": "white",
    "fontSize": "16px",
    "width": "100%"

}

loginWithGoogleStyle = {
    "textDecoration": "white",
    "borderRadius": "50px",
}

layout = dmc.Center(
    dmc.Paper(
        shadow='sm',
        p = "30px",
        mt = 60,
        withBorder=True,
        children = [
            dmc.Container(id='login-error-container', style={'margin-bottom': '20px', "width":'300px'}),
            html.Form(
                style = {"width":'300px'},
                method='POST',
                action="/signin/email",
                children = [
                    dmc.Text("Sign in ",  size='xl', fw=700),
                    dmc.Text("Please log in to continue", c='gray', size='xs', mb = 10),
                    html.A(
                        href='/signin/google',
                        style=loginWithGoogleStyle,
                        children=[
                            dmc.Button(
                                "Login with Google",
                                variant="outline",
                                color="royalblue",
                                fullWidth=True,
                                radius='xl',
                                leftSection=DashIconify(icon="flat-color-icons:google"),
                            ),
                        ]
                    ),
                    dmc.Divider(label="Or continue with", mb=10, mt=10),
                    dmc.TextInput(
                        label="Email",
                        name='email',
                        placeholder="Enter your Email",
                        required = True,

                        leftSection=DashIconify(icon="ic:round-alternate-email", width=20),
                    ),
                    dmc.PasswordInput(
                        mb=20,
                        label="Password",
                        placeholder="Enter your password",
                        leftSection=DashIconify(icon="bi:shield-lock", width=20),
                        name='password',
                        required = True
                    ),
                    html.Button(
                        children="Sign in",
                        n_clicks=0,
                        type="submit",
                        id="login-button",
                        style =loginButtonStyle
                    ),
                    dmc.Flex(
                        mt=10,
                        align='center',
                        children=[
                            dcc.Link('Forgot Password?', href='/reset-password', style={'fontSize': '12px'})
                        ]
                    ),
                    dmc.Divider(variant='solid', style={'margin-top': '10px'}),
                    dmc.Flex(
                        mt = 10,
                        align = 'center',
                        children = [
                            dmc.Text(f" Don't have an account?", c='gray', size = 'sm'),
                            dcc.Link('Sign up', href='/signup', style = {'fontSize':'14px'})
                        ]
                    ),
                ]
            )
        ]
    )
)

@callback(
    Output("login-error-container", "children"),
      Input('url', 'hash'),
)
def login_error(hash):
    if "#loginerror" in hash:
        alert = dmc.Alert(
            "Please try again.",
            title="Incorrect email or password",
            color="red",
            withCloseButton=True,
            hide=False
        ),
        return alert
    else:
        return ''