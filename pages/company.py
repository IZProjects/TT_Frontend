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
from utils.helpers import (parse_data_for_charts, round_sig, adjust_to_nearest_dates, get_corr_companies,
                           merge_dict_lists_companies, convert_to_last_day_of_month)
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
    dcc.Store(id='company-data-store'),
    dcc.Store(id='price-data-store2'),
    dmc.Paper(id='company-header', style={'margin-bottom': '10px'}),
    dmc.Group(id='company-badge', style={'margin-bottom': '30px'},),
    dmc.Group(children=[trend_dropdown], style={'margin-bottom': '20px'}),
    dcc.Graph(id='main-chart-company'),
    dmc.Divider(variant="solid", style={'margin-bottom': '20px', 'margin-top': '20px'}),
    dmc.Paper(id='company-info', withBorder=True, style={'margin-bottom': '20px'}),
    dmc.Paper(id='relation-table-companies', style={'margin-bottom': '20px'}),
    dmc.Divider(variant="solid", style={'margin-bottom': '20px', 'margin-top': '20px'}),
    dmc.Stack(children=[
        dmc.Text("Related Trends", fw=700, size='sm'),
        dmc.Group(id='kw-btns-container'),
    ], gap='xs', style={'margin-bottom': '20px'}),
])


# ------------------------------------------------ Callbacks ----------------------------------------------------------
# ---------------------------- Stores the keyword data from kw_companies & stock price --------------------------------
@callback(
     [Output("company-data-store", "data"),
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
    return data, price_dict
# --------------------------------------------------- Generate Header -------------------------------------------------
@callback(
    [Output("company-header", "children"),
     Output("company-badge", "children"),],
     Input("company-data-store", "data"),
)
def get_header_company(data):
    header = dmc.Title(f"{data['full_name']} ({data['ticker']}.{data['code']})")
    badge = dmc.Badge(data['exchange'], radius='xs')
    return header, badge




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
     Output("company-info", "children"),
    Input("company-data-store", "data"),
)
def gen_company_description(data):
    info_section = dmc.Container(dcc.Markdown(data['description'], style={"margin-top": '15px'}), fluid=True, )
    return info_section

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

    trend_grid = dmc.Group(children=trend_btns, gap="md",)
    return trend_grid


@callback(
    Output("relation-table-companies", "children"),
    [Input("company-data-store", "data"),
     Input("price-data-store2", "data"),]
)
def create_relation_table(data, price_data):
    data_tbl = data['keywords']
    corr = get_corr_companies(data, price_data)
    data_tbl = merge_dict_lists_companies(data_tbl, corr)
    rows = [
        dmc.TableTr(
            [
                dmc.TableTd(element["keyword"]),
                dmc.TableTd(element["type"]),
                dmc.TableTd(element["Long-term Correlation"]),
                dmc.TableTd(element["Short-term Correlation"]),
                dmc.TableTd(dcc.Markdown(element["relation"])),
            ]
        )
        for element in data_tbl
    ]

    head = dmc.TableThead(
        dmc.TableTr(
            [
                dmc.TableTh("Keyword/Hashtag"),
                dmc.TableTh("Source"),
                dmc.TableTh("Long-term Correlation"),
                dmc.TableTh("Short-term Correlation"),
                dmc.TableTh("Relationship with Trend"),
            ]
        )
    )
    body = dmc.TableTbody(rows)

    tbl = dmc.Table(children=[head, body],
                    striped=True,
                    highlightOnHover=True,
                    withTableBorder=True,
                    withColumnBorders=True,
                    )
    return tbl