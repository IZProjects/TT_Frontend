from dash import dcc, Input, Output, clientside_callback, callback, html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

burger = dmc.Burger(id="burger-button", size="sm", hiddenFrom="md", opened=False),

dropdown = dcc.Dropdown(id="my-dynamic-dropdown", placeholder="Search...", className='Dropdown-2', optionHeight=55)

theme_toggle = dmc.Switch(
    offLabel=DashIconify(icon="radix-icons:sun", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][8]),
    onLabel=DashIconify(icon="radix-icons:moon", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][6]),
    id="color-scheme-switch",
    persistence=True,
    persistence_type='local',
    checked=False,
    label= "Theme",
    labelPosition='left'
)

menu = dmc.Menu(
            children=[
                dmc.MenuTarget(
                    dmc.Box(
                        id='avatar-indicator',
                        children=[dmc.ActionIcon(DashIconify(icon="solar:settings-outline", width=150), variant='subtle')]
                    )
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            html.A(
                                children=[
                                    html.Span("Logout"),
                                    DashIconify(icon="hugeicons:login-01", width=20)
                                ],
                                href="/logout",
                                id="logoutMenuItem",
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "textDecoration": "none",
                                    "color": "inherit",
                                    "padding": "0.2rem 0.6rem",
                                    "borderRadius": "1px",
                                    "transition": "background-color 0.2s",
                                    "width": "100%",  # ensures the spacing fills the container
                                    "boxSizing": "border-box",
                                }
                            )
                        ),
                        dmc.MenuItem(theme_toggle),

                    ]
                ),
            ]
        )

title = dmc.Title("Tickersight", c="blue", visibleFrom='md')

header = dmc.Grid(
    children=[
        dmc.GridCol(burger, span="content"),
        dmc.GridCol(title, span="content"),
        dmc.GridCol(dropdown, span="auto", id='search-dropdown'),
        #dmc.GridCol(theme_toggle, span="content"),
        dmc.GridCol(menu, span="content"),
    ],
    gutter={"base": "xs", "md": "xl"},
    justify="space-around",
    align="center",
)

clientside_callback(
    """
    function(theme) {
        if (theme === 'dark') {
            return 'darkDropdown';
        } else {
            return 'lightDropdown';
        }
    }
    """,
    Output("search-dropdown", "className"),
    Input("mantine-provider", "forceColorScheme")
)

