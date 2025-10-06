import dash
from dash import dcc, callback, Output, Input, html
import pandas as pd
import dash_mantine_components as dmc
from supabase_client import supabase_anon, supabase_service
from utils.helpers import get_first_last_multi_trends
import yfinance as yf
from utils.EODHD_functions import get_historical_stock_data
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils.helpers import parse_data_for_charts, round_sig, adjust_to_nearest_dates
from datetime import datetime
from dash_iconify import DashIconify


dash.register_page(__name__, path='/company', name='Landing Page', title='tab title',
                   description="""google blurb description""") # '/' is home page


# ----------------------------------------- Creates the dropdowns -----------------------------------------------------
trend_dropdown = dmc.Select(
    placeholder="Select a trend to add",
    id="trend-select",
    w={"base": 130, "sm":400, "md": 500, "xl": 1000},
    mb=10,
    nothingFoundMessage="Nothing found...",
    checkIconPosition="right",
    persistence=True,
    persistence_type ='session'
)


# ------------------------------------------------ Page Layout --------------------------------------------------------
layout = dmc.Box([
    html.H1(id='tag_company'),
    html.H1(id='stock_company'),
    dcc.Store(id='company-data-store'),
    dcc.Store(id='price-data-store2'),
    dmc.Paper(id='company-header', style={'margin-bottom': '20px'}),
    dmc.Group(children=[trend_dropdown], style={'margin-bottom': '20px'}),
    dcc.Graph(id='main-chart-company'),
    dmc.Divider(variant="solid", style={'margin-bottom': '20px', 'margin-top': '20px'}),
    dmc.SimpleGrid(
        id='company-grid',
        cols={"base": 1, "md": 2},
        children=[
            dmc.Paper(id='company-info', withBorder=True,),
            dmc.Paper(children=dmc.Stack(id='company-correlation', justify='space-between')),
        ],
    ),
    dmc.Divider(variant="solid", style={'margin-bottom': '20px', 'margin-top': '20px'}),
    dmc.Stack(children=[
        dmc.Text("Related Trends", fw=700, size='sm'),
        dmc.Group(id='kw-btns-container'),
    ], gap='xs', style={'margin-bottom': '20px'}),
])


# ------------------------------------------------ Callbacks ----------------------------------------------------------
# ---------------------------- Stores the keyword data from kw_companies & stock price --------------------------------
@callback(
    [Output("stock_company", "children"),
     Output("company-data-store", "data"),
     Output("price-data-store2", "data"),],
     Input("page-metadata", "data"),
)
def get_kw_data(metadata):
    stock = metadata[0]
    response = (
        supabase_service.table("kw_companies")
        .select("*")
        .eq("ticker_id", stock)
        .execute()
    )
    data = response.data[0]
    start_date, end_date = get_first_last_multi_trends(data['keywords'])
    if data['source'] == "EODHD":
        price_data = get_historical_stock_data(data['ticker_id'],
                                               from_date=start_date, to_date=end_date)
        price_data["date"] = pd.to_datetime(price_data["date"])
    else:
        price_data = yf.download(data['ticker_id'],
                                 start=start_date, end=end_date)
        price_data = price_data.droplevel('Ticker', axis=1)
        price_data = price_data.reset_index()
        price_data.columns = price_data.columns.str.lower()

    price_dict = price_data.to_dict(orient="list")
    return metadata, data, price_dict
# --------------------------------------------------- Generate Header -------------------------------------------------
@callback(
    Output("company-header", "children"),
     Input("company-data-store", "data"),
)
def get_header_company(data):
    header = dmc.Title(f"{data['full_name']} ({data['ticker']})")

    return header




# ------------------------------------------------ Generate main chart ------------------------------------------------
@callback(
    Output("main-chart-company", "figure"),
     [Input("company-data-store", "data"),
      Input("price-data-store2", "data"),
      Input("trend-select", "value"),
      Input("mantine-provider", "forceColorScheme")],
)
def get_main_chart_company(data, price_data, trend, theme):
    # ----------------------------------------------- Generate stock chart --------------------------------------------
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df_price = pd.DataFrame(price_data)
    df_price["date"] = pd.to_datetime(df_price["date"])
    df_price = df_price.reset_index(drop=True)
    fig.add_trace(
        go.Candlestick(x=df_price['date'],
                       open=df_price['open'], high=df_price['high'],
                       low=df_price['low'], close=df_price['close'],
                       name=f"Stock Price: {data['ticker_id']}"),
        secondary_y=False,
    )
    fig.update_layout(xaxis_rangeslider_visible=False)
    # ----------------------------------------------- Generate Trend chart ---------------------------------------------
    if trend:
        if '#' in trend:
            dtype = 'Tiktok'
            trend_c = trend.replace("#", "")
            label = 'Views'
        else:
            dtype = 'Google Search'
            trend_c = trend
            label = 'Volume'

        trendData = next((d for d in data['keywords'] if d.get("keyword") == trend_c and d.get("type") == dtype), None)

        kw_trend_x, kw_trend_y = parse_data_for_charts(trendData['trend'], period='monthly')
        kw_trend_y = [round_sig(n, 3) for n in kw_trend_y]

        fig.add_trace(
            go.Scatter(x=kw_trend_x, y=kw_trend_y, name=f"{trend} {label} ({dtype})", line=dict(color='dodgerblue')),
            secondary_y=True,
        )

    # ----------------------------------------------- style chart -----------------------------------------------------
    fig.update_layout(
        legend=dict(orientation="h"),
    )

    if theme == 'light':
        fig.update_layout(
            plot_bgcolor='white',  # Set background color
            paper_bgcolor='white',  # Set plot area background color
            font_color='black',  # Set text color
            title=None,  # Set title
            xaxis=dict(title=''),  # Set X-axis title and grid color
            yaxis=dict(title='', gridcolor='lightgray'),  # Set Y-axis title and grid color
            margin=dict(l=40, r=0, t=40, b=40),  # Add margin
            xaxis_ticks='outside',  # Place X-axis ticks outside
            xaxis_tickcolor='lightgray',  # Set X-axis tick color
            yaxis_ticks='outside',  # Place Y-axis ticks outside
            yaxis_tickcolor='lightgray',  # Set Y-axis tick color
            yaxis2=dict(showgrid=False, showline=False, zeroline=False, ticks="outside", tickcolor="lightgray"),
        )
    else:
        fig.update_layout(
            plot_bgcolor='rgb(50, 50, 50)',  # Set background color
            paper_bgcolor='rgb(50, 50, 50)',  # Set plot area background color
            font_color='white',  # Set text color
            title=None,  # Set title
            xaxis=dict(title='', gridcolor='rgb(50, 50, 50)'),  # Set X-axis title and grid color
            yaxis=dict(title='', gridcolor='lightgray'),  # Set Y-axis title and grid color
            margin=dict(l=40, r=0, t=40, b=40),  # Add margin
            xaxis_ticks='outside',  # Place X-axis ticks outside
            xaxis_tickcolor='lightgray',  # Set X-axis tick color
            yaxis_ticks='outside',  # Place Y-axis ticks outside
            yaxis_tickcolor='lightgray',  # Set Y-axis tick color
            yaxis2=dict(showgrid=False, showline=False, zeroline=False, ticks="outside", tickcolor="lightgray"),
        )


    return fig

# ------------------------------------- Sets up what's in the trend-select dropdown ------------------------------------
@callback(
    Output("trend-select", "data"),
    Input("company-data-store", "data"),
)
def get_stock_info(data):
    keyword = ['#' + item['keyword'] if item['type'] == 'Tiktok' else item['keyword']
               for item in data['keywords']]
    source = [item['type'] for item in data['keywords']]
    labels = [{"value": keyword[i], "label": f"{keyword[i]} ({source[i]})"} for i in range(len(keyword))]
    return labels


# -------------------------------------------- Creates the info & correlation -----------------------------------------
@callback(
    [Output("company-correlation", "children"),
     Output("company-info", "children")],
    [Input("company-data-store", "data"),
     Input("price-data-store2", "data"),]
)
def gen_correlation(data, price_data):
    info_section = dmc.Container(dcc.Markdown(data['description'], style={"margin-top": '15px'}), px='lg')

    kw_list = data['keywords']

    df_price = pd.DataFrame(price_data)
    df_price["date"] = pd.to_datetime(df_price["date"])
    df_price = df_price.set_index("date")

    cards = []
    for kw_dict in kw_list:
        dtype = kw_dict['type']
        if dtype == "Tiktok":
            prefix = "#"
        else:
            prefix = ""
        kw_label = f"{prefix}{kw_dict['keyword']} ({kw_dict['type']})"
        trend = kw_dict['trend']
        pairs = [p.strip() for p in trend.split(",") if p.strip()]
        trend = [(datetime.strptime(d.split(":")[0].strip(), "%m/%d/%Y"),
                  int(d.split(":")[1].strip().replace(",", ""))) for d in pairs]
        df_trend = pd.DataFrame(trend, columns=["date", "trend_volume"]).set_index("date")
        df_price = adjust_to_nearest_dates(df_price, df_trend)

        df_combined = df_price.join(df_trend, how="inner")
        df_last3m = df_combined[df_combined.index >= (df_combined.index.max() - pd.DateOffset(months=2))]

        correlation = df_combined["close"].corr(df_combined["trend_volume"])
        correlation = round(correlation,2)

        correlation_last3m = df_last3m["close"].corr(df_last3m["trend_volume"])
        correlation_last3m = round(correlation_last3m,2)

        card = dmc.Paper(
            children=[
                dmc.Stack(
                    children=[
                        dmc.Group(
                            children=[
                                dmc.Text(
                                    children=f"Correlation between {data['ticker_id']} & {kw_label}", fw=700),
                                dmc.HoverCard(
                                    shadow='md',
                                    width=400,
                                    children=[
                                        dmc.HoverCardTarget(
                                            DashIconify(icon="material-symbols:info-outline", width=20)
                                        ),
                                        dmc.HoverCardDropdown(
                                            "Correlation ranges from -1 to 1. "
                                            "A high correlation may mean the trend so far has been priced in. "
                                            "A low or negative correlation may mean the trend has not been priced in OR"
                                            " there is not a strong link between the trend and the stock OR there are "
                                            "other factors affecting the stock price. Always do additional research!"
                                        ),
                                    ]
                                ),
                            ],
                            gap='sm'
                        ),
                        dmc.Text(children="Long-term correlation", fw=500),
                        dmc.Title(children=str(correlation), order=2),
                        dmc.Text(children="Last 3 month correlation", fw=500),
                        dmc.Title(children=str(correlation_last3m), order=2),
                    ],
                    align="center",
                    gap="sm",
                )
            ],
            radius="sm",
            p="lg",
            shadow="sm",
            withBorder=True,
        )
        cards.append(card)

    return cards, info_section

# --------------------------------------------- creates related trends btn---------------------------------------------
@callback(
    Output("kw-btns-container", "children"),
    Input("company-data-store", "data")
)
def gen_stock_btns(data):
    kw_data = data['keywords']
    trend_btns = []
    for kw_dict in kw_data:
        ttype = kw_dict['type']
        if ttype == 'Tiktok':
            prefix = "#"
        else:
            prefix = ""
        kw = kw_dict['keyword']
        label = f"{prefix}{kw} ({ttype})"

        trend_btn = dmc.Paper(children=[
            dmc.NavLink(label=label, href=f"/trend?trend={kw}&source={ttype}#query",
                        style={"textAlign": "center"})  # change href to exchange
        ], withBorder=True, shadow="xs")

        trend_btns.append(trend_btn)

    trend_grid = dmc.SimpleGrid(children=trend_btns, cols=3)
    return trend_grid