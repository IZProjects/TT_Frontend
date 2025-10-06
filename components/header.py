from dash import dcc, Input, Output, clientside_callback, callback, html
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from supabase_client import supabase_anon, supabase_service

burger = dmc.Burger(id="burger-button", size="sm", hiddenFrom="md", opened=False),

dropdown = dmc.Select(
    placeholder="Search company or trend",
    id='header-dropdown',
    clearable=True,
    searchable=True,
    allowDeselect=True,
)

theme_toggle = dmc.Switch(
    offLabel=DashIconify(icon="radix-icons:sun", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][8]),
    onLabel=DashIconify(icon="radix-icons:moon", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][6]),
    id="color-scheme-switch",
    persistence=True,
    persistence_type='local',
    checked=False,
    #label= "Theme",
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
                                    html.Span("My Account")
                                ],
                                href="/my_account",
                                id="MyAccountMenuItem",
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

                        dmc.MenuItem(
                            html.A(
                                children=[
                                    html.Span("Login"),
                                ],
                                href="/login",
                                id="loginMenuItem",
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

                        dmc.MenuItem(
                            html.A(
                                children=[
                                    html.Span("Logout"),
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
                        #dmc.MenuItem(theme_toggle),

                    ]
                ),
            ]
        )

title_btn = dcc.Link(
                    children=dmc.Title("Tickersight", c="blue", visibleFrom='md'),
                    href="/",
                    style={"textDecoration": "none", "color": "inherit"}
                ),

header = dmc.Grid(
    children=[
        dmc.GridCol(burger, span="content"),
        dmc.GridCol(title_btn, span="content"),
        dmc.GridCol(dropdown, span="auto", id='search-dropdown'),
        dmc.GridCol(theme_toggle, span="content"),
        dmc.GridCol(menu, span="content"),
    ],
    gutter={"base": "xs", "md": "xl"},
    justify="space-around",
    align="center",
)

@callback(
     Output("header-dropdown", "data"),
     Input('url', 'pathname'),
)
def dropdown_data(url):
    kw_companies = (
        supabase_service.table("kw_companies")
        .select("ticker_id, full_name")
        .execute()
    )
    kw_companies = kw_companies.data

    kw_joined = (
        supabase_service.table("kw_joined")
        .select("keyword, type")
        .execute()
    )
    kw_joined = kw_joined.data

    dList = []
    for company_dict in kw_companies:
        label = f"Company: {company_dict['full_name']} ({company_dict['ticker_id']})"
        value = f"/company?company={company_dict['ticker_id']}#query"
        dList.append({'value':value, 'label':label})

    for kw_dict in kw_joined:
        label = f"Trend: {kw_dict['keyword']} ({kw_dict['type']})"
        value = f"/trend?trend={kw_dict['keyword']}&source={kw_dict['type']}#query"
        dList.append({'value':value, 'label':label})
    dList = sorted(dList, key=lambda x: x['label'])
    return dList

@callback(
     Output("url", "href"),
     Input('header-dropdown', 'value'),
)
def dropdown_to_url(dropdown):
    return dropdown