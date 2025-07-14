from dash import dcc, html, Input, Output, callback, register_page
import pandas as pd
import dash_mantine_components as dmc
from datetime import datetime

# ---------------------------------------------- Functions ------------------------------------------------------------
# ---------------------- Prepare timeseries string to list of dictionaries for dmc.Charts -----------------------------
def parse_volume_data(data_str):
    """
    Convert a string of 'MM/DD/YYYY: volume' pairs into a list of dictionaries
    with formatted date and volume.

    Args:
        data_str (str): A string with entries like "MM/DD/YYYY: volume, ..." in this form:
        "06/01/2020: 75510, 07/01/2020: 76157, 08/01/2020: 76706, ..."

    Returns:
        List[dict]: List of dictionaries with 'date' in "Mon YYYY" format and 'volume' as int in this form:
        [{"date": "Jun 2020", "volume": 75510}, {"date": "Jul 2020", "volume": 76157} ,...]
    """
    pairs = [item.strip() for item in data_str.split(',')]
    result = []
    for pair in pairs:
        date_str, volume_str = pair.split(': ')
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        formatted_date = date_obj.strftime("%b %Y")
        result.append({"date": formatted_date, "volume": int(volume_str)})
    return result

# -------------------------------------- format int to string with K, M, B --------------------------------------------
def format_number(n):
    """
    Convert an integer into a string with suffix:
    K for thousand, M for million, B for billion.

    Examples:
        950      -> '950'
        1500     -> '1.5K'
        2000000  -> '2M'
        7200000000 -> '7.2B'
    """
    abs_n = abs(n)
    if abs_n >= 1_000_000_000:
        formatted = f"{n / 1_000_000_000:.1f}B"
    elif abs_n >= 1_000_000:
        formatted = f"{n / 1_000_000:.1f}M"
    elif abs_n >= 1_000:
        formatted = f"{n / 1_000:.1f}K"
    else:
        formatted = str(n)

    # Remove trailing .0 if unnecessary
    if formatted.endswith(".0K") or formatted.endswith(".0M") or formatted.endswith(".0B"):
        formatted = formatted[:-3] + formatted[-1]

    return formatted

# ------------------------------------------- format growth % and colour ----------------------------------------------
def format_growth(a: int, b: int) -> tuple[str, str]:
    """
    Calculate percentage growth from `a` to `b` and return:
    - A formatted string with a % sign
    - A color: 'green' for positive, 'red' for negative, 'gray' for zero

    Rules:
    - If a == 0 and b == 0: return '0%', 'gray'
    - If a == 0 and b != 0: return '+999%+', 'green'
    - If percentage growth > 999% or < -999%: cap as '±999%+'
    - Prefix '+' for positive growth, '-' for negative growth
    """
    if a == 0:
        if b == 0:
            return '0%', 'gray'
        else:
            return '+999%+', 'green'

    growth = ((b - a) / abs(a)) * 100
    sign = '+' if growth >= 0 else '-'
    abs_growth = abs(growth)

    if abs_growth > 999:
        formatted = f'{sign}999%+'
    else:
        formatted = f'{sign}{abs_growth:.0f}%'

    if growth > 0:
        color = 'green'
    elif growth < 0:
        color = 'red'
    else:
        color = 'gray'

    return formatted, color


# ----------------------------------------------- Generate Cards ------------------------------------------------------
def create_cards(df, overlay_style):
    cards=[]
    for i in range(len(df)):
        # ------------------------------------------- free content allowance ------------------------------------------
        if i < 3:
            display_style = {
            "position": "absolute",
            "display": "none",
            "zIndex": 1,
            }
        else:
            display_style = overlay_style

        # ------------------------------------------- create stock buttons --------------------------------------------
        tickers = df.at[i,'Ticker'].split(",")
        exchanges = df.at[i,'Code'].split(",") # change code to exchange
        stock_btns = []
        for j in range(len(tickers)):
            stock_btn = dmc.Paper(children=[
                dmc.NavLink(label=f"{exchanges[j]}: {tickers[j]}", href=f"/company?company={tickers[j]}#query", style={"textAlign": "center"}) # change href to exchange
            ], withBorder=True, shadow="xs")
            stock_btns.append(stock_btn)

        # ------------------------------------------- create badges --------------------------------------------
        categories = df.at[i,'Category'].split(",")
        category_badges = [dmc.Badge(children=category, color="blue", radius="xs") for category in categories]
        type_badge = [dmc.Badge(children=df.at[i,'Type'], color="orange", radius="xs")]
        growth_badge = [dmc.Badge(children=df.at[i, 'Growth Indicator'], color="gray", radius="xs")]
        badges = growth_badge + type_badge + category_badges
        badge_section = dmc.Group(children=badges)

        # ------------------------------------------- create cards --------------------------------------------
        search_vol = parse_volume_data(df.at[i,'Search Volume'])
        volume_str = format_number(search_vol[-2]['volume'])
        growth_str, growth_colour = format_growth(search_vol[-14]['volume'], search_vol[-2]['volume'])

        info_text = dmc.Group(children=[
                dmc.Text(children=df.at[i,'Keyword'], fw=700, size='lg'),  # change children with actual name
                dmc.Group(children=[
                    dmc.Stack(children=[
                        dmc.Text(children=volume_str, c="blue", size="lg", fw=500),
                        # change children with actual volume
                        dmc.Text(children="Volume", c="dimmed", size="md"),
                    ], gap=0, align='center'),
                    dmc.Stack(children=[
                        dmc.Text(children=growth_str, c=growth_colour, size="lg", fw=500),
                        # change children with actual growth %
                        dmc.Text(children="YoY Growth", c="dimmed", size="md"),
                    ], gap=0, align='center'),
                ])
            ], justify="space-between"
        ),

        chart = dmc.AreaChart(
            h={"base": 300, "md": 300}, # change base from mobile testing
            dataKey="date",
            data=search_vol,
            series=[{"name": "volume", "color": "indigo.6"}],
            tickLine="xy",
            withGradient=False,
            withXAxis=True,
            withYAxis=False,
            withDots=False,
        )

        company_btns = dmc.SimpleGrid(children=stock_btns, cols=3)

        card = dmc.Card(children=[
            dmc.Stack(children=[
                dcc.Link(
                    children=info_text,
                    href=f"/trend?trend={df.at[i,'Keyword']}#query",
                    style={"textDecoration": "none", "color": "inherit"}
                ),
                dcc.Link(
                    children=chart,
                    href=f"/trend?trend={df.at[i,'Keyword']}#query",
                    style={"textDecoration": "none", "color": "inherit"}
                ),
                dmc.Divider(variant="solid"),
                dmc.Stack(children=[
                    dmc.Text("Tradable Companies", size='sm', c='indigo', fw=700),
                    company_btns
                ], gap='xs'),
                dmc.Divider(variant="solid"),
                badge_section,
            ])
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        w={"base": 450, "md": 500},  # change base from mobile testing
        style={"position": "relative"}
        )

        overlay = html.Div(
            children=[
                dmc.Button(
                    "🔒 Unlock this trend now!",
                    variant="gradient",
                    gradient={"from": "violet", "to": "blue"},
                    size="md",
                    radius="md",
                    style={"zIndex": 2}
                )
            ],
            style=display_style
        )


        overlay_card = dmc.Paper(
            children=[
            card,
            dcc.Link(overlay,href="/subscription",style={"textDecoration": "none", "color": "inherit"})
            ],
            style={"position": "relative", "overflow": "hidden"}
        )

        cards.append(overlay_card)
    return cards

# ------------------------------------------------ create dropdowns ---------------------------------------------------
growth_dropdown = dmc.Select(
    placeholder="Filter by growth",
    id="growth-multi-select",
    data=["Exploding","Accelerating","Declining","Stationary","Peaking"],
    w={"base": 130, "md": 400},
    mb=10,
    clearable=True,
    searchable=True,
    nothingFoundMessage="Nothing found...",
    checkIconPosition="right",
)

breakout_dropdown = dmc.Select(
    placeholder="Filter by trend type",
    id="breakout-multi-select",
    data = ["Breakout", "Established"],
    w={"base": 130, "md": 400},
    mb=10,
    clearable=True,
    searchable=True,
    nothingFoundMessage="Nothing found...",
    checkIconPosition="right",
)

category_dropdown = dmc.Select(
    placeholder="Filter by category",
    id="category-multi-select",
    data=[
    'entertainment', 'lifestyle', 'toys', 'art', 'business', 'technology', 'hr',
    'productivity', 'education', 'health', 'food-beverage', 'nutrition', 'food',
    'cpg', 'supplements', 'home', 'furniture', 'home-decor', 'design', 'retail',
    'telecommunication', 'travel', 'beauty', 'skincare', 'makeup-cosmetics',
    'personal-care', 'ecommerce', 'social-media', 'dating-relationships', 'gaming',
    'sports-outdoors', 'ai', 'media', 'marketing', 'robotics', 'automation', 'pets',
    'fashion', 'shoes', 'eco', 'industry', 'clothing', 'baby', 'science', 'healthcare',
    'company', 'pharma'
    ],
    w={"base": 130, "md": 400},
    mb=10,
    clearable=True,
    searchable=True,
    nothingFoundMessage="Nothing found...",
    checkIconPosition="right",
)

# ------------------------------------------------ page layout --------------------------------------------------------
register_page(__name__, name='Trend', title='Trend', description="""Page description for google blurb""")

layout = dmc.Box([
    dmc.VisuallyHidden(children="Google metadata title/description"), #change
    html.H1(children="Page 2"),
    dmc.Group(children=[growth_dropdown, breakout_dropdown, category_dropdown],
              style={'margin-top': '5px', 'margin-bottom': '20px'}),
    dmc.SimpleGrid(
        id='cards-simple-grid',
        cols={"base": 1, "md": 3},
    )
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
        tag, metadata = search.split("=")
        return tag, metadata
    else:
        return '',''



# ------------------------------------- Callback: Store dropdown filter -----------------------------------------------

@callback(
    Output("cards-simple-grid", "children"),
    [Input("growth-multi-select", "value"),
     Input("breakout-multi-select", "value"),
     Input("category-multi-select", "value"),
     Input("user-info", "data"),],

)
def generate_cards(growth_filter, breakout_filter, category_filter, user_info):
    #change to actual user info
    if 'yes' in user_info:
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

    df = pd.read_csv("Brand_Stock_Price_SVol_trend.csv")
    if growth_filter:
        df = df[df['Growth Indicator'] == growth_filter]
    if breakout_filter:
        df = df[df['is_breakout'] == breakout_filter]
    if category_filter:
        df = df[df['Category'].apply(lambda x: category_filter in x.split(','))]
    df = df.reset_index(drop=True)
    cards = create_cards(df, overlay_style)

    return cards

