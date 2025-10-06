from dash import dcc, html, Input, Output, callback, register_page, State
import pandas as pd
import dash_mantine_components as dmc
from datetime import datetime, timedelta
from supabase_client import supabase_anon, supabase_service
import re
from dash_iconify import DashIconify


def parse_vols_for_sparkline(s: str) -> list[int]:
    """
    Parse 'MM/DD/YYYY: Volume' pairs from a string and return volumes as ints.
    Handles commas in numbers and extra quotes/whitespace.
    """
    s = s.strip().strip('"').strip("'")
    return [int(v.replace(",", "")) for v in re.findall(r":\s*([+-]?\d[\d,]*)", s)]

# ----------------------------------------------- Generate Rows -------------------------------------------------------
def create_rows(data, overlay_style, free_limit):
    rows = []
    for i, dataRow in enumerate(data, start=1):
        # ---------------------------------------- First Column -------------------------------------------------------
        col1 = dmc.Stack(children=[


            dmc.NavLink(
                label=dmc.Text(f"{dataRow['ticker']}.{dataRow['code']}", fw=700, size='xl'),
                description=dmc.Text(f"{dataRow['full_name']}", fw=700, size='xl'),
                href=f"/company?company={dataRow['ticker']}.{dataRow['code']}#query",
            ),
            dmc.Group(children=[
                dmc.Badge(children=dataRow['exchange'], radius='sm', variant='filled', color='violet'),
            ])
        ], gap='md')

        # ---------------------------------------- Second Column -------------------------------------------------------
        sparklineRows = []
        for keywordData in dataRow['keywords']:
            trend = parse_vols_for_sparkline(keywordData['trend'])
            sparkline = dmc.Sparkline(w=300, h=100, data=trend, color='blue')

            if keywordData['type'] == 'Tiktok':
                source_icon = DashIconify(icon="mage:tiktok-circle", width=30)
                keywordName = f"#{keywordData['keyword']}"
            else:
                source_icon = DashIconify(icon="logos:google-icon", width=25)
                keywordName = keywordData['keyword']

            sparklineRow = dmc.SimpleGrid(
                children=[
                    dmc.NavLink(
                        label=dmc.Text(children=keywordName, fw=500, size='lg'),
                        leftSection=source_icon,
                        href=f"/trend?trend={keywordData['keyword']}&source={keywordData['type']}#query",
                    ),
                    sparkline
                ],
                cols=3,
                spacing="xs",
                verticalSpacing="10",
                style={'align':'bottom'}
            )

            sparklineRows.append(sparklineRow)

        col2 = dmc.Stack(
            children=sparklineRows
        )

        # ------------------------------------------- free content allowance ------------------------------------------
        if i < free_limit:
            display_style = {
            "position": "absolute",
            "display": "none",
            "zIndex": 1,
            }
        else:
            display_style = overlay_style

        # ------------------------------------- sets up the paywall overlay -------------------------------------------
        overlay = html.Div(
            children=[
                dmc.Button(
                    "🔒 Unlock this trend now!",
                    variant="gradient",
                    gradient={"from": "violet", "to": "blue"},
                    size="md",
                    radius="md",
                    style={"zIndex": 2},
                )
            ],
            style=display_style
        )

        # ----------------------------------------------- create row --------------------------------------------------
        row = dmc.SimpleGrid(cols={"base": 1, "md": 2},
                               children=[col1, col2])

        # ------------------------------------- combines overlay and row ----------------------------------------------
        overlay_row = dmc.Paper(
            children=[
            row,
            dcc.Link(overlay,id='overlay-link',href='pricing', style={"textDecoration": "none", "color": "inherit"})
            ],
            style={"position": "relative", "overflow": "hidden"}
        )

        # ---------------------------------------- Generate Table -----------------------------------------------------
        rows.append(overlay_row)
        rows.append(dmc.Divider(variant='solid'))
    table = dmc.Stack(rows, gap='lg')
    return table




# ------------------------------------------------ page layout --------------------------------------------------------
register_page(__name__, name='DiscoverCompanies', title='Discover Companies', description="""Page description for google blurb""")

layout = dmc.Box([
    dmc.VisuallyHidden(children="Google metadata title/description"), #change
    html.H1(children="Discover Companies"),
    dmc.Divider(variant='solid'),
    dmc.Paper(
        id='companies-paper',
        withBorder=False,
    ),
    dmc.Flex(justify='flex-start',
             children=dmc.Pagination(id="pagination-withPages2",
                                     total=300, value=1, withPages=False, style={"margin-top": "20px"}), ),
])

# ------------------------------------- Callback: Create the rows -----------------------------------------------------
@callback(
    Output("companies-paper", "children"),
     [Input("user-data", "data"),
      Input("pagination-withPages2", "value"),
      ]
)
def generate_groups(user_data, page):
    # ------------------------ if the user has paid no paywall, otherwise paywall -------------------------------------
    if user_data != None:
        response = (
            supabase_service.table("user_profiles")
            .select("subscription_status")
            .eq("id", user_data['id'])
            .single()
            .execute()
        )
        sub_status = response.data['subscription_status']
    else:
        sub_status = None

    if sub_status == 'active':
        overlay_style = {
            "position": "absolute",
            "display": "none",
            "zIndex": 1,
        }
    else:
        overlay_style = {
            "position": "absolute",
            "top": 0,
            "left": 0,
            "right": 0,
            "bottom": 0,
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "backdropFilter": "blur(4px)",
            "backgroundColor": "rgba(255, 255, 255, 0.7)",
            "zIndex": 1,
            "borderRadius": "12px"
        }


    if page == 1:
        free_limit = 3
    else:
        free_limit = 0

    # ------------------------------------------------- get data ------------------------------------------------------
    limit = 4
    total = 300

    start = limit * (page - 1) + 1
    end = min(total, limit * page)
    data = supabase_service.table("kw_companies").select("*").range(start, end).execute().data
    return create_rows(data, overlay_style, free_limit)
