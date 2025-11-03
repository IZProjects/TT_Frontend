import dash
from dash import dcc, callback, Output, Input, html, State
import pandas as pd
import dash_mantine_components as dmc
from supabase_client import supabase_anon, supabase_service
from dash_iconify import DashIconify
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import (format_number, format_growth, get_last_date, get_first_date, convert_date_format,
                           parse_data_for_charts, convert_to_last_day_of_month, round_sig, get_corr, merge_dict_lists)
from utils.EODHD_functions import get_historical_stock_data
import yfinance as yf
from statsmodels.tsa.seasonal import STL




dash.register_page(__name__, path='/trend', name='Landing Page', title='tab title',
                   description="""google blurb description""") # '/' is home page




# ----------------------------------------- Creates the dropdowns -----------------------------------------------------
period_dropdown_kw = dmc.Select(
    placeholder="Filter by period",
    id="period-select-kw",
    data=["Long Term", "Short Term"],
    value="Long Term",
    w={"base": 130, "md": 200},
    mb=10,
    nothingFoundMessage="Nothing found...",
    checkIconPosition="right",
    persistence=True,
    persistence_type ='session'
)

data_dropdown_kw = dmc.Select(
    placeholder="Add stock to the chart",
    id="data-select-kw",
    w={"base": 130, "sm":400, "md": 500, "xl": 1000},
    mb=10,
    clearable=True,
    searchable=True,
    nothingFoundMessage="Nothing found...",
    checkIconPosition="right",
    persistence=True,
    persistence_type='session'
)


# ------------------------------------------------ Page Layout --------------------------------------------------------
layout = dmc.Box([
    dcc.Store(id='kw-data-store'),
    dcc.Store(id='stock-data-store'),
    dcc.Store(id='price-data-store'),
    dmc.Title(id='kw-data-title', order=1, style={'margin-bottom':'10px'}),
    dmc.Group(id='kw-data-badges', style={'margin-bottom':'20px'}),
    dmc.Divider(variant="solid", style={'margin-bottom':'20px'}),

    dmc.Group(children=[period_dropdown_kw, data_dropdown_kw],
              style={'margin-bottom': '20px'}),
    dmc.Group(id='kw-details', gap='xl', justify='flex-start'),
    dcc.Graph(id='main-chart'),
    dmc.Accordion(
        children=[
            dmc.AccordionItem(
                [
                    dmc.AccordionControl(
                        dmc.Group(
                            children = [
                                dmc.Title("Trend", order=3),
                                dmc.HoverCard(
                                    shadow='md',
                                    width=250,
                                    children=[
                                        dmc.HoverCardTarget(
                                            DashIconify(icon="material-symbols:info-outline", width=20)
                                        ),
                                        dmc.HoverCardDropdown(
                                            "Calculated using Seasonal-Trend decomposition. "
                                            "This separates seaonality from the trend."
                                        ),
                                    ]
                                ),
                            ],
                            gap='sm'
                        ),
                    ),
                    dmc.AccordionPanel(id='trend-container'),
                ],
                value="trend-accord",

            ),
            dmc.AccordionItem(
                [
                    dmc.AccordionControl(
                        dmc.Group(
                            children = [
                                dmc.Title("Seasonality", order=3),
                                dmc.HoverCard(
                                    shadow='md',
                                    width=250,
                                    children=[
                                        dmc.HoverCardTarget(
                                            DashIconify(icon="material-symbols:info-outline", width=20)
                                        ),
                                        dmc.HoverCardDropdown(
                                            "Calculated using Seasonal-Trend decomposition. "
                                            "A positive value means seasonality has added to the trend and a negative "
                                            "value means seasonality has subtracted to the trend."),
                                    ]
                                ),
                            ],
                            gap='sm'
                        ),
                    ),
                    dmc.AccordionPanel(id='seasonality-container'),
                ],
                value="seasonality-accord",
            ),
            dmc.AccordionItem(
                [
                    dmc.AccordionControl(
                        dmc.Group(
                            children = [
                                dmc.Title("Momentum", order=3),
                                dmc.HoverCard(
                                    shadow='md',
                                    width=250,
                                    children=[
                                        dmc.HoverCardTarget(
                                            DashIconify(icon="material-symbols:info-outline", width=20)
                                        ),
                                        dmc.HoverCardDropdown(
                                            "Calculated using the derivative of the trendline. "
                                        ),
                                    ]
                                ),
                            ],
                            gap='sm'
                        ),
                    ),
                    dmc.AccordionPanel(id='momentum-container'),
                ],
                value="momentum-accord",
            ),
        ],
        variant="separated",
        style={'margin-top': '20px', 'margin-bottom': '20px'},
        value=["trend-accord","seasonality-accord", "momentum-accord"],
    ),
    dmc.Paper(id='kw-info', withBorder=True, style={'margin-bottom': '20px'}),
    dmc.Paper(id='relation-table', style={'margin-bottom': '20px'}),
    dmc.Divider(variant="solid", style={'margin-bottom': '20px'}),
    dmc.Stack(children=[
        dmc.Text("Related Companies", fw=700, size='sm'),
        dmc.Group(id='kw-stock-btns-container'),
    ], gap='xs', style={'margin-bottom': '20px'}),
    dmc.Divider(variant="solid", style={'margin-bottom': '20px'}),
])

# ------------------------------------------------ Callbacks ----------------------------------------------------------
# ---------------------------------- Stores the keyword data from kw_joined -------------------------------------------
@callback(
     Output("kw-data-store", "data"),
     Input("page-metadata", "data"),
)
def get_kw_data(metadata):
    response = (
        supabase_service.table("kw_joined")
        .select("*")
        .eq("type", metadata[1])
        .eq("keyword", metadata[0])
        .execute()
    )
    data = response.data
    data = data[0]
    return data

# ---------------------------------- Creates the header with the KW and tags ------------------------------------------
@callback(
    [Output("kw-data-title", "children"),
     Output("kw-data-badges", "children"),],
    Input("kw-data-store", "data"),
)
def get_kw_header(data):
    title = data['keyword']

    categories = [item.strip() for item in data['categories'].split(",")]
    badges = [dmc.Badge(children=category, color="blue", radius="xs") for category in categories]
    if data['type'] == 'Tiktok':
        source_icon = DashIconify(icon="mage:tiktok-circle", width=30)
    else:
        source_icon = DashIconify(icon="logos:google-icon", width=25)
    badges.insert(0, source_icon)


    return title, badges

# ------------------------------------- Stores the stock data from kw_tickers -----------------------------------------
@callback(
    Output("stock-data-store", "data"),
    Input("kw-data-store", "data"),
)
def get_stock_info(data):
    tickers = [item['ticker'] for item in data['tickers']]
    response = (
        supabase_service.table("kw_tickers")
        .select("ticker, full_name, code, source")
        .in_("ticker", tickers)
        .execute()
    )
    return response.data

# ------------------------------------- Sets up what's in the data-select dropdown ------------------------------------
@callback(
    Output("data-select-kw", "data"),
    Input("kw-data-store", "data"),
)
def get_stock_info(data):
    tickers = [item['ticker'] for item in data['tickers']]
    exchange = [item['exchange'] for item in data['tickers']]
    labels = [{"value": tickers[i], "label": f"Stock Price: {tickers[i]} ({exchange[i]})"} for i in range(len(tickers))]
    return labels


# -------------------------------------------- Creates the main chart -------------------------------------------------
@callback(
    [Output("main-chart", "figure"),
     Output("kw-details", "children"),],
    [Input("kw-data-store", "data"),
     Input("period-select-kw", "value"),
     Input("data-select-kw", "value"),
     Input("price-data-store", "data"),
     Input("mantine-provider", "forceColorScheme")]
)
def gen_main_chart(data, period_filter, ticker, price_data, theme):
    # ------------------------------------ Gets label Views vs Volume -------------------------------------------------
    if data['type'] == 'Google Search':
        label = 'Views'
        if period_filter == "Short Term":
            period = 'daily'
        else:
            period = 'monthly'
    else:
        label = 'Volume'
        if period_filter == "Short Term":
            period = 'weekly'
        else:
            period = 'monthly'

    # --------------------------- Gets long term or short term data based on dropdown ---------------------------------
    if period_filter == "Short Term":
        trend = data['trend_st']
    else:
        trend = data['trend']

    # ------------------------------- Gets the volume & growth details above chart ------------------------------------
    volume_str = format_number(data['volume'])
    growth_str, growth_colour = format_growth(data['yoy'])

    details = [
        dmc.Group(children=[
            dmc.Text(children=f"{label}: ", size="xl", fw=700),
            dmc.Text(children=volume_str, c="blue", size="xl", fw=500),
        ], gap='xs'),
        dmc.Group(children=[
            dmc.Text(children="YoY Growth: ", size="xl", fw=700),
            dmc.Text(children=growth_str, c=growth_colour, size="xl", fw=500),
        ], gap='xs')
    ]

    # ------------------------------------------ creates the base chart ----------------------------------------------
    kw_trend_x, kw_trend_y = parse_data_for_charts(trend, period=period)
    kw_trend_y = [round_sig(n, 3) for n in kw_trend_y]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=kw_trend_x, y=kw_trend_y, name=f"{data['type']} {label}", line=dict(color='dodgerblue')),
        secondary_y=False,
    )


    if period_filter == "Long Term":
        # -------------------------- Gets the dotted line projected vols if long term ---------------------------------
        kw_trend_x_prj, kw_trend_y_prj = parse_data_for_charts(data['trend_projected'], period=period)
        kw_trend_x_prj.insert(0, kw_trend_x[-1])
        kw_trend_y_prj.insert(0, kw_trend_y[-1])
        kw_trend_y_prj = [round_sig(n, 3) for n in kw_trend_y_prj]
        fig.add_trace(
            go.Scatter(x=kw_trend_x_prj, y=kw_trend_y_prj, name=f"{data['type']} {label} Estimated",
                       line=dict(color='dodgerblue', dash='dot')),
            secondary_y=False,
        )

        # -------------------------- Gets the current month vol (so far) if long term ---------------------------------
        current_month = dmc.Group(children=[
            dmc.Text(children=f"Current Month {label}: ", size="xl", fw=700),
            dmc.Text(children=str(format_number(int(kw_trend_y_prj[-1]))), c="blue", size="xl", fw=500),
            dmc.HoverCard(
                shadow='md',
                width=250,
                children=[
                    dmc.HoverCardTarget(
                        DashIconify(icon="material-symbols:info-outline", width=20)
                    ),
                    dmc.HoverCardDropdown("Current month volumes are incomplete and are updated weekly"),
                ]
            ),
        ], gap='xs')

        details.append(current_month)

    fig.update_layout(hovermode="x unified")

    # -------------------------- Generates candle stick charts onto the figure if selected ----------------------------
    start_date = kw_trend_x[0]
    if period_filter == "Long Term":
        end_date = kw_trend_x_prj[-1]
    else:
        end_date = kw_trend_x[-1]

    if ticker:
        stock_data = [d for d in price_data if d['ticker'] == ticker][0]
        stock_data.pop('ticker')
        stock_data.pop('code')
        df_price = pd.DataFrame(stock_data)
        df_price["date"] = pd.to_datetime(df_price["date"])
        df_price = df_price[(df_price["date"] >= start_date) & (df_price["date"] <= end_date)]
        df_price = df_price.reset_index(drop=True)
        fig.add_trace(
            go.Candlestick(x=df_price['date'],
                           open=df_price['open'], high=df_price['high'],
                           low=df_price['low'], close=df_price['close'],
                           name=f"Stock Price: {ticker}"),
            secondary_y=True,
        )
        fig.update_layout(xaxis_rangeslider_visible=False)

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

    return fig, details


# -------------------------------------- Gets stock price and stores it -----------------------------------------------
@callback(
     Output("price-data-store", "data"),
    [Input("kw-data-store", "data"),
     Input("stock-data-store", "data"),],
    State("data-select-kw", "data"),
)
def get_price_data(data, sData, data_filter):
    trend = data['trend'] + ', ' + data['trend_st']

    start_date = convert_date_format(get_first_date(trend))
    end_date = convert_date_format(get_last_date(trend))

    final_data = []
    for tag in data_filter:
        ticker = tag['value']
        if ticker != 'Trendline':
            stock_data = [d for d in sData if d['ticker'] == ticker][0]

            if stock_data['source'] == "EODHD":
                price_data = get_historical_stock_data(f"{stock_data['ticker']}.{stock_data['code']}",
                                                       from_date=start_date, to_date=end_date)
                price_data["date"] = pd.to_datetime(price_data["date"])
            else:
                price_data = yf.download(f"{stock_data['ticker']}.{stock_data['code']}",
                                         start=start_date, end=end_date)
                price_data = price_data.droplevel('Ticker', axis=1)
                price_data = price_data.reset_index()
                price_data.columns = price_data.columns.str.lower()

            data_dict = price_data.to_dict(orient="list")
            data_dict['ticker'] = ticker
            data_dict['code'] = stock_data['code']
            final_data.append(data_dict)
    return final_data

# ----------------------------------- Generates seasonality, trend ----------------------------------------------------
@callback(
     [Output("trend-container", "children"),
      Output("seasonality-container", "children"),
      Output("momentum-container", "children")],
    [Input("kw-data-store", "data"),
     Input("period-select-kw", "value"),]
)
def gen_STL(data, period):
    # ------------------------------------------- Sets STL period -----------------------------------------------------
    if period == 'Long Term':
        data_str = data['trend'] + ', ' + data['trend_projected']
        convert_to_last_day_of_month(data_str)
        STL_period = 3  #quaterly
    elif period == 'Short Term':
        data_str = data['trend_st']
        STL_period = 7  #weekly
    else:
        print(f"invalid period: {period}")

    # -------------------------------- preps timeseries string to STL format (df)--------------------------------------
    entries = [item.strip() for item in data_str.split(",")]
    STL_data = [(datetime.strptime(date.strip(), "%m/%d/%Y"), int(value.strip())) for date, value in
            (entry.split(":") for entry in entries)]
    df = pd.DataFrame(STL_data, columns=["Date", "Volume"])
    df.set_index("Date", inplace=True)
    df = df.iloc[:-1]
    stl = STL(df['Volume'], period=STL_period)
    res = stl.fit()
    stl_df = pd.DataFrame({
        'Observed': res.observed,
        'Trend': res.trend,
        'Seasonal': res.seasonal,
        'Residual': res.resid
    }, index=df.index.date)
    stl_df = stl_df.round(0).astype(int)
    stl_df['Trend_Momentum'] = stl_df['Trend'].diff()

    if data['type'] == "Tiktok":
        label = "views"
    else:
        label = "volume"

    # --------------------------------------------- creates dmc chart--------------------------------------------------
    trend = [
        {"date": idx, label: row["Trend"]}
        for idx, row in stl_df.iterrows()
    ]
    seasonal = [
        {"date": idx, label: row["Seasonal"]}
        for idx, row in stl_df.iterrows()
    ]

    momentum = [
        {"date": idx, label: row["Trend_Momentum"]}
        for idx, row in stl_df.iterrows()
    ]

    trend_chart = dmc.LineChart(
        h=180,
        dataKey="date",
        data=trend,
        series=[{"name": label, "color": "indigo.6"}],
        lineChartProps={"syncId": "STL"},
        valueFormatter={"function": "formatNumberIntl"},
        withDots=False,
    )
    seasonal_chart = dmc.LineChart(
        h=180,
        dataKey="date",
        data=seasonal,
        series=[{"name": label, "color": "teal.6"}],
        valueFormatter={"function": "formatNumberIntl"},
        lineChartProps={"syncId": "STL"},
        withDots=False,
    )
    momentum_chart = dmc.AreaChart(
        h=180,
        dataKey="date",
        data=momentum,
        type="split",
        series=[{"name": label, "color": "grape.6"}],
        valueFormatter={"function": "formatNumberIntl"},
        withDots=False,
    )

    return trend_chart, seasonal_chart, momentum_chart

# --------------------------------------------- creates related companies----------------------------------------------
@callback(
    Output("kw-stock-btns-container", "children"),
    Input("kw-data-store", "data")
)
def gen_stock_btns(data):
    tickers = [f"{item['ticker']}.{item['code']}" for item in data['tickers']]
    stock_btns = []
    for j in range(len(tickers)):
        stock_btn = dmc.Paper(children=[
            dmc.NavLink(label=f"{tickers[j]}", href=f"/company?company={tickers[j]}#query",
                        style={"textAlign": "center"})  # change href to exchange
        ], withBorder=True, shadow="xs")
        stock_btns.append(stock_btn)
    company_btns = dmc.Group(children=stock_btns, gap="md",)
    return company_btns

# -------------------------------------------- Creates the info & correlation -----------------------------------------
@callback(
     Output("kw-info", "children"),
    Input("kw-data-store", "data"),
)
def gen_trend_info(data):
    return dmc.Container(dcc.Markdown(data['description'], style={"margin-top": '15px'}), fluid=True,)


@callback(
    Output("relation-table", "children"),
    [Input("kw-data-store", "data"),
     Input("price-data-store", "data"),]
)
def create_relation_table(data, price_data):
    trend = convert_to_last_day_of_month(data['trend'])
    trend_st = convert_to_last_day_of_month(data['trend_st'])
    corr = get_corr(trend, price_data, lt=True)
    corr_st = get_corr(trend_st, price_data, lt=False)

    data_tbl = data['tickers']
    data_tbl = merge_dict_lists(data_tbl, corr)
    data_tbl = merge_dict_lists(data_tbl, corr_st)

    rows = [
        dmc.TableTr(
            [
                dmc.TableTd(element["ticker"]),
                dmc.TableTd(element["full_name"]),
                dmc.TableTd(element["exchange"]),
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
                dmc.TableTh("Ticker"),
                dmc.TableTh("Company Name"),
                dmc.TableTh("Exchange"),
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
                    withColumnBorders=True,)
    return tbl
