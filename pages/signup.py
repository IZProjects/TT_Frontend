from dash import html, register_page, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

register_page(__name__, path='/signup', name='Sign Up', title='tab title',
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

layout = dmc.Center(
    dmc.Paper(
        shadow='lg',
        withBorder=True,
        p="30px",
        mt=60,
        children=[
            html.Form(
                style={"width": '300px'},
                method='POST',
                action='/signup',
                children=[
                    dmc.Text("Sign up", size='xl', fw=700),
                    dmc.Text("Please up in to continue", c='gray', size='xs', mb=10),
                    dmc.TextInput(
                        label="First Name",
                        name='given_name',
                        placeholder="Enter your first name",
                        required=True,
                    ),
                    dmc.TextInput(
                        label="Last Name",
                        name='family_name',
                        placeholder="Enter your last name",
                        required=True,
                    ),
                    dmc.TextInput(
                        label="Email",
                        name='email',
                        placeholder="Enter your Email",
                        required=True,
                        leftSection=DashIconify(icon="ic:round-alternate-email", width=20),
                    ),
                    dmc.PasswordInput(
                        mb=20,
                        label="Password",
                        placeholder="Enter your password",
                        leftSection=DashIconify(icon="bi:shield-lock", width=20),
                        name='password',
                        required=True
                    ),
                    html.Button(
                        children="Sign up",
                        n_clicks=0,
                        type="submit",
                        id="register-button",
                        style=loginButtonStyle
                    ),
                    dmc.Flex(
                        mt=10,
                        align='center',
                        children=[
                            dmc.Text(f"Already have an Account?", c='gray', size='xs'),
                            dcc.Link('Sign in', href='/login', style={'fontSize': '12px'})
                        ]
                    )
                ]
            )
        ]
    )
)