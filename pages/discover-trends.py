from dash import dcc, html, Input, Output, callback, register_page, State
import pandas as pd
import dash_mantine_components as dmc
from datetime import datetime, timedelta
from supabase_client import supabase_anon, supabase_service
from dash_iconify import DashIconify
from utils.helpers import format_number, format_growth

# ---------------------------------------------- Functions ------------------------------------------------------------
# ---------------------- Prepare timeseries string to list of dictionaries for dmc.Charts -----------------------------
def parse_volume_data(data_str, source, projected=False, monthly=True):
    """
    Convert a string of 'MM/DD/YYYY: volume' pairs into a list of dictionaries
    with formatted date and volume.

    Args:
        data_str (str): String with entries like "MM/DD/YYYY: volume, ..."
        source (str): Either "Google Search" or "Tiktok"
        projected (bool): If True, append " (estimated)" to label
        monthly (bool): monthly will give Aug 2025, non monthly will givem week of 01/01/2025 or 01/01/2025

    Returns:
        List[dict]: List of dictionaries with formatted 'date' and volume/views
    """
    prj = " (estimated)" if projected else ""

    if source == "Tiktok":
        label = "views" + prj
    else:
        label = "volume" + prj

    pairs = [item.strip() for item in data_str.split(",") if item.strip()]
    result = []

    for pair in pairs:
        date_str, volume_str = pair.split(": ")
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")

        # Choose format based on period
        if monthly:
            formatted_date = date_obj.strftime("%b %Y")   # "Aug 2025"
        else:
            if source == "Tiktok":
                formatted_date = f"week of {date_obj.strftime('%m/%d/%Y')}"  # "week of 08/01/2020"
            else:
                formatted_date = date_obj.strftime("%m/%d/%Y")  # "08/01/2020"

        result.append({"date": formatted_date, label: int(volume_str)})

    return result


# ----------------------------------------------- Generate Cards ------------------------------------------------------
def create_cards(data, overlay_style, period, free_limit):
    cards=[]
    for i in range(len(data)):
        # ------------------------------------------- free content allowance ------------------------------------------
        if i < free_limit:
            display_style = {
            "position": "absolute",
            "display": "none",
            "zIndex": 1,
            }
        else:
            display_style = overlay_style

        # ------------------------------------------- create stock buttons --------------------------------------------
        tickers = [f"{item['ticker']}.{item['code']}" for item in data[i]['tickers']]
        stock_btns = []
        for j in range(len(tickers)):
            stock_btn = dmc.Paper(children=[
                dmc.NavLink(label=f"{tickers[j]}", href=f"/company?company={tickers[j]}#query", style={"textAlign": "center"}) # change href to exchange
            ], withBorder=True, shadow="xs")
            stock_btns.append(stock_btn)

        # ------------------------------------------- create badges --------------------------------------------
        categories = [item.strip() for item in data[i]['categories'].split(",")]
        badges = [dmc.Badge(children=category, color="blue", radius="xs") for category in categories]

        # ------------------------------------------- create cards ---------------------------------------------
        if period == "Long Term":
            monthly = True
        else:
            monthly = False

        # ----------------------------------------- get actual trend ---------------------------------------------
        search_vol = parse_volume_data(data[i]['trend'], data[i]['type'], projected=False, monthly=monthly)

        # ------------- adds views est to actual trend so that the actual trend and prj trend lines join up -----------
        if search_vol and period == "Long Term":
            if data[i]['type'] == "Tiktok":
                search_vol[-1]["views (estimated)"] = search_vol[-1]["views"]
            else:
                search_vol[-1]["volume (estimated)"] = search_vol[-1]["volume"]

        # ------------------------------------- adds projected trend if long term -------------------------------------
        if any('trend_projected' in d for d in data) and period == "Long Term":
            search_vol = search_vol + parse_volume_data(data[i]['trend_projected'], data[i]['type'], projected=True,
                                                        monthly=monthly)

        # ------------------------------------- gets vol and growth for the card -------------------------------------
        volume_str = format_number(data[i]['volume'])
        growth_str, growth_colour = format_growth(data[i]['yoy'])
        if data[i]['type'] == 'Tiktok':
            value_name = 'Views'
            source_icon = DashIconify(icon="mage:tiktok-circle", width=30)
        else:
            value_name = 'Volume'
            source_icon = DashIconify(icon="logos:google-icon", width=25)

        # ---------------------- inserts data source icon (google or tiktok) to badges --------------------------------
        badges.insert(0, source_icon)

        # ------------------------------------- sets up text in the card ----------------------------------------------
        info_text = dmc.Group(children=[
                dmc.Text(children=data[i]['keyword'], fw=700, size='lg'),
                dmc.Group(children=[
                    dmc.Stack(children=[
                        dmc.Text(children=volume_str, c="blue", size="lg", fw=500),
                        # change children with actual volume
                        dmc.Text(children=value_name, c="dimmed", size="md"),
                    ], gap=0, align='center'),
                    dmc.Stack(children=[
                        dmc.Text(children=growth_str, c=growth_colour, size="lg", fw=500),
                        # change children with actual growth %
                        dmc.Text(children="YoY Growth", c="dimmed", size="md"),
                    ], gap=0, align='center'),
                ])
            ], justify="space-between"
        ),

        # -------------------------------------- creates the card chart ----------------------------------------------
        chart = dmc.AreaChart(
            h={"base": 300, "md": 300}, # change base from mobile testing
            dataKey="date",
            data=search_vol,
            valueFormatter={"function": "formatNumberIntl"},
            series=[{"name": "volume", "color": "indigo.6"},
                    {"name": "views", "color": "indigo.6"},
                    {"name": "volume (estimated)", "color": "indigo.6", "strokeDasharray": "5 5"},
                    {"name": "views (estimated)", "color": "indigo.6", "strokeDasharray": "5 5"}],
            tickLine="xy",
            withGradient=False,
            withXAxis=True,
            withYAxis=False,
            withDots=False,
        )

        # ------------------------------------------- creates stock btns ----------------------------------------------
        company_btns = dmc.SimpleGrid(children=stock_btns, cols=3)

        # ------------------------------------- sets up the card with link to the keyword page ------------------------
        card = dmc.Card(children=[
            dmc.Stack(children=[
                dcc.Link(
                    children=info_text,
                    href=f"/trend?trend={data[i]['keyword']}&source={data[i]['type']}#query",
                    style={"textDecoration": "none", "color": "inherit"}
                ),
                dcc.Link(
                    children=chart,
                    href=f"/trend?trend={data[i]['keyword']}&source={data[i]['type']}#query",
                    style={"textDecoration": "none", "color": "inherit"}
                ),
                dmc.Divider(variant="solid"),
                dmc.Stack(children=[
                    dmc.Text("Tradable Companies", size='sm', c='indigo', fw=700),
                    company_btns
                ], gap='xs'),
                dmc.Divider(variant="solid"),
                dmc.Group(children=badges),
            ])
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        w={"base": 450, "md": 500},  # change base from mobile testing
        style={"position": "relative"}
        )

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

        # ------------------------------------- combines overlay and card --------------------------------------------
        overlay_card = dmc.Paper(
            children=[
            card,
            dcc.Link(overlay,id='overlay-link',href='pricing', style={"textDecoration": "none", "color": "inherit"})
            ],
            style={"position": "relative", "overflow": "hidden"}
        )

        cards.append(overlay_card)
    return cards

# ------------------------------------------------ create dropdowns ---------------------------------------------------
period_dropdown = dmc.Select(
    placeholder="Filter by period",
    id="period-select",
    data=["Long Term", "Short Term"],
    value="Long Term",
    w={"base": 130, "md": 200},
    mb=10,
    clearable=True,
    searchable=True,
    nothingFoundMessage="Nothing found...",
    checkIconPosition="right",
    persistence=True,
    persistence_type='session'
)

category_dropdown = dmc.Select(
    placeholder="Filter by category",
    id="category-select",
    data=["Apparel & Accessories", "Baby", "Kids & Maternity", "Beauty & Personal Care", "Business Services",
          "Education", "Financial Services", "Food & Beverage", "Games", "Health", "Home Improvement",
          "Household Products", "Life Services", "News & Entertainment", "Pets", "Sports & Outdoor",
          "Tech & Electronics"],
    w={"base": 130, "md": 250},
    mb=10,
    clearable=True,
    searchable=True,
    nothingFoundMessage="Nothing found...",
    checkIconPosition="right",
    persistence=True,
    persistence_type='session'
)
source_dropdown = dmc.Select(
    placeholder="Filter by data source",
    id="source-select",
    data=["Google Search", "Tiktok"],
    w={"base": 130, "md": 250},
    mb=10,
    clearable=True,
    searchable=True,
    nothingFoundMessage="Nothing found...",
    checkIconPosition="right",
    persistence=True,
    persistence_type='session'
)
sort_dropdown = dmc.Select(
    placeholder="Sort by...",
    id="sort-select",
    data=["YoY Growth Descending", "YoY Growth Ascending", "Volume/Views Descending", "Volume/Views Ascending",
           "Alphabetically Descending", "Alphabetically Ascending"],
    w={"base": 130, "md": 250},
    mb=10,
    clearable=True,
    searchable=True,
    nothingFoundMessage="Nothing found...",
    checkIconPosition="right",
    persistence=True,
    persistence_type='session'
)

# ------------------------------------------------ page layout --------------------------------------------------------
register_page(__name__, path='/', name='Discover', title='Discover', description="""Page description for google blurb""")

layout = dmc.Box([
    dmc.VisuallyHidden(children="Google metadata title/description"), #change
    html.H1(children="Page 2"),
    dmc.Group(children=[period_dropdown, source_dropdown, category_dropdown, sort_dropdown],
              style={'margin-top': '5px', 'margin-bottom': '20px'}),
    dmc.Text("* Note: current month volumes are incomplete and are updated weekly", size='xs'),
    dmc.SimpleGrid(
        id='cards-simple-grid',
        cols={"base": 1, "md": 3},
    ),
    dmc.Flex(justify='flex-start',
             children=dmc.Pagination(id="pagination-withPages",
                                     total=100, value=1, withPages=False, style={"margin-top":"20px"}),),
])

# ------------------------------------- Callback: update page metadata store ------------------------------------------

@callback(
    [Output("page-tag", "data"),
     Output("page-metadata", "data"),],
     [Input('url', 'search'),
      Input('url', 'hash'),]
)
def get_page_metadata(search, hash):
    if "#query" in hash:
        search = search[1:]
        search = search.replace("%20", " ")
        pairs = [part.split("=", 1) for part in search.split("&")]
        tag = [k for k, v in pairs]  # keys
        metadata = [v for k, v in pairs]
        return tag, metadata
    else:
        return '',''


# ------------------------------------- Callback: Create the Cards ----------------------------------------------------
@callback(
    Output("cards-simple-grid", "children"),
    [Input("category-select", "value"),
     Input("source-select", "value"),
     Input("sort-select", "value"),
     Input("period-select", "value"),
     Input("user-data", "data"),
     Input("pagination-withPages", "value"),
     ]

)
def generate_cards(category_filter, source_filter, sort_filter, period_filter, user_data, page):
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

    # --------------------------------------- get the trend data from kw_joined ---------------------------------------
    limit = 9
    total = 300

    start = limit * (page - 1) + 1
    end = min(total, limit * page)
    data = supabase_service.table("kw_joined").select("*").range(start, end).execute().data

    # --------------------------------------- filter data for short-term & long term-----------------------------------
    if period_filter == "Short Term":
        for d in data:
            d.pop("trend", None)
            d.pop("trend_projected", None)
        for d in data:
            d['trend'] = d.pop('trend_st')

    # --------------------------------------- filter data based on dropdowns-------------------------------------------
    if category_filter:
        data = [
            row for row in data
            if category_filter in [x.strip() for x in row['categories'].split(',')]
        ]
    if source_filter:
        data = [
            row for row in data
            if source_filter in [x.strip() for x in row['type'].split(',')]
        ]

    # ---------------------------------------- sort data based on dropdown---------------------------------------------
    if sort_filter == "YoY Growth Ascending":
        data = sorted(data, key=lambda x: x['yoy'])
    elif sort_filter == "YoY Growth Descending":
        data = sorted(data, key=lambda x: x['yoy'], reverse=True)
    elif sort_filter == "Volume/Views Ascending":
        data = sorted(data, key=lambda x: x['volume'])
    elif sort_filter == "Volume/Views Descending":
        data = sorted(data, key=lambda x: x['volume'], reverse=True)
    elif sort_filter == "Alphabetically Ascending":
        data = sorted(data, key=lambda x: x['keyword'].lower())
    elif sort_filter == "Alphabetically Descending":
        data = sorted(data, key=lambda x: x['keyword'].lower(), reverse=True)

    # ---------------------------------------------- create the card --------------------------------------------------
    if page == 1:
        free_limit = 3
    else:
        free_limit = 0

    cards = create_cards(data, overlay_style, period_filter, free_limit)

    return cards
