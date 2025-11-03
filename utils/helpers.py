from datetime import datetime, timedelta
import calendar
import math
import pandas as pd
import numpy as np
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
def format_growth(growth) -> tuple[str, str]:
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
    if growth == 0:
        return '0%', 'gray'
    if growth == None:
        return '+999%+', 'green'

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

# ------------------------------------- for getting the 1st and last date of trend string -----------------------------
def get_last_date(input_str: str) -> str:
    """
    Extract the last date from a 'MM/DD/YYYY: Value' string.

    Args:
        input_str (str): A string like "06/01/2024: 10783, 07/01/2024: 77881,..."

    Returns:
        str: The last date in MM/DD/YYYY format.
    """
    # split into date:value parts, remove empty entries
    parts = [p.strip() for p in input_str.strip().strip(",").split(",") if p.strip()]

    # get last part
    last_part = parts[-1]
    date_str, _ = [x.strip() for x in last_part.split(":")]

    # ensure it's valid date
    datetime.strptime(date_str, "%m/%d/%Y")
    return date_str


def get_first_date(input_str: str) -> str:
    """
    Extract the first date from a 'MM/DD/YYYY: Value' string.

    Args:
        input_str (str): A string like "06/01/2024: 10783, 07/01/2024: 77881,..."

    Returns:
        str: The first date in MM/DD/YYYY format.
    """
    # split into date:value parts, remove empty entries
    parts = [p.strip() for p in input_str.strip().strip(",").split(",") if p.strip()]

    # get first part
    first_part = parts[0]
    date_str, _ = [x.strip() for x in first_part.split(":")]

    # ensure it's valid date
    datetime.strptime(date_str, "%m/%d/%Y")
    return date_str

# ------------------------------------- convert MM/DD/YYYY into YYYY-MM-DD --------------------------------------------
def convert_date_format(date_str: datetime) -> str:
    """
    Convert a date from MM/DD/YYYY format to YYYY-MM-DD format.

    Args:
        date_str (str): Date in MM/DD/YYYY format.

    Returns:
        str: Date in YYYY-MM-DD format.
    """
    dt = datetime.strptime(date_str, "%m/%d/%Y")
    return dt.strftime("%Y-%m-%d")


def get_first_last_multi_trends(data):
    all_dates = []

    for item in data:
        trend = item.get("trend", "")
        if trend:
            all_dates.append(get_first_date(trend))
            all_dates.append(get_last_date(trend))

    if not all_dates:
        return None, None

    # convert all strings to datetime
    parsed = [datetime.strptime(d, "%m/%d/%Y") for d in all_dates]

    earliest = min(parsed).strftime("%Y-%m-%d")
    latest = max(parsed).strftime("%Y-%m-%d")

    return earliest, latest


# ---------------------- converts the MM/DD/YYYY from 1st day of the month to last day of the month -------------------
def convert_to_last_day_of_month(input_str: str) -> str:
    """
    Convert dates in 'MM/DD/YYYY: Value' format from the first day of the month
    to the last day of the month.

    Args:
        input_str (str): A string like "06/01/2024: 10783, 07/01/2024: 77881, ..."

    Returns:
        str: Updated string with last day of each month instead of the first.
        "06/30/2024: 10783, 07/31/2024: 77881, 08/31/2024: 94655"
    """
    parts = [p.strip() for p in input_str.split(",") if p.strip()]
    output_parts = []

    for part in parts:
        date_str, val = [x.strip() for x in part.split(":")]
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        last_day = calendar.monthrange(dt.year, dt.month)[1]  # last day of the month
        new_date = dt.replace(day=last_day).strftime("%m/%d/%Y")
        output_parts.append(f"{new_date}: {val}")

    return ", ".join(output_parts)

# ---------------------- converts the MM/DD/YYYY from 1st day of the week to last day of the week -------------------
def convert_to_week_end(input_str: str) -> str:
    """
    Convert dates in 'MM/DD/YYYY: Value' format to the last day (Sunday)
    of that week.

    Args:
        input_str (str): A string like "06/01/2024: 10783, 07/01/2024: 77881, ..."

    Returns:
        str: Updated string with dates set to the last day of their week.
    """
    parts = [p.strip() for p in input_str.split(",") if p.strip()]
    output_parts = []

    for part in parts:
        date_str, val = [x.strip() for x in part.split(":")]
        dt = datetime.strptime(date_str, "%m/%d/%Y")

        # weekday(): Monday=0, Sunday=6 → find days to add until Sunday
        days_to_sunday = 6 - dt.weekday()
        week_end = dt + timedelta(days=days_to_sunday)

        new_date = week_end.strftime("%m/%d/%Y")
        output_parts.append(f"{new_date}: {val}")

    return ", ".join(output_parts)

# ---------------------- Prepare timeseries string to list of dictionaries for dcc.Graph -----------------------------
def parse_data_for_charts(data_str, period):
    """
    Convert a string of 'MM/DD/YYYY: volume' pairs into separate lists
    for dates and volumes.

    Args:
        data_str (str): String with entries like "MM/DD/YYYY: volume, ..."
        period (str): monthly, weekly or daily

    Returns:
        (list, list): (dates, volumes)
    """
    if period == 'monthly':
        data_str = convert_to_last_day_of_month(data_str)
    elif period == 'weekly':
        data_str = convert_to_week_end(data_str)
    elif period == 'daily':
        pass
    else:
        print("invalid period input")

    pairs = [item.strip() for item in data_str.split(",") if item.strip()]

    dates, volumes = [], []

    for pair in pairs:
        date_str, volume_str = pair.split(": ")
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")

        dates.append(date_obj)
        volumes.append(int(volume_str))

    return dates, volumes

# ----------------------------------------------- Round 3 sig fig -----------------------------------------------------
def round_sig(x, sig=3):
    return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1) if x != 0 else 0


# -------------------------------------------- adj df1 to dates of df2 ------------------------------------------------
def adjust_to_nearest_dates(df1, df2):
    """
    Adjust the index of df1 to the nearest available dates in df2.

    This function takes two pandas DataFrames with datetime indices and aligns
    the index of df1 to the closest dates found in df2’s index. For each date in df1:
      - If it falls before the earliest date in df2, it is mapped to the first date in df2.
      - If it falls after the latest date in df2, it is mapped to the last date in df2.
      - Otherwise, it is mapped to whichever date in df2’s index is closest (before or after).

    Args:
        df1 (pd.DataFrame): The DataFrame whose index will be adjusted.
        df2 (pd.DataFrame): The reference DataFrame providing valid dates.

    Returns:
        pd.DataFrame: A copy of df1 with its index replaced by the nearest dates from df2.
    """
    ref_dates = df2.index.sort_values().unique()

    adjusted_index = []
    for d in df1.index:
        pos = ref_dates.searchsorted(d)
        if pos == 0:
            adjusted_index.append(ref_dates[0])
        elif pos == len(ref_dates):
            adjusted_index.append(ref_dates[-1])
        else:
            before, after = ref_dates[pos - 1], ref_dates[pos]
            adjusted_index.append(before if abs(d - before) <= abs(after - d) else after)

    df1 = df1.copy()
    df1.index = adjusted_index
    return df1


# ------------------------------------ get correlation between trend and stock price ----------------------------------
def get_corr(trend, price_data, lt=True):
    pairs = [p.strip() for p in trend.split(",") if p.strip()]
    trend = [(datetime.strptime(d.split(":")[0].strip(), "%m/%d/%Y"),
                     int(d.split(":")[1].strip().replace(",", ""))) for d in pairs]
    df_trend = pd.DataFrame(trend, columns=["date", "trend_volume"]).set_index("date")

    if lt==True:
        corr_name = 'Long-term Correlation'
    else:
        corr_name = 'Short-term Correlation'

    results = []
    for price_dict in price_data:
        df_price = pd.DataFrame(price_dict)
        df_price["date"] = pd.to_datetime(df_price["date"])
        df_price = df_price.set_index("date")
        df_trend = adjust_to_nearest_dates(df_trend, df_price)
        df_combined = df_price.join(df_trend, how="inner")
        correlation = df_combined["close"].corr(df_combined["trend_volume"])
        correlation = round(correlation,2)
        ticker = price_dict['ticker']
        code = price_dict['code']
        results.append({'ticker':ticker, 'code':code, corr_name:correlation})
    return results

def safe_corr(a, b):
    """Return Pearson r, or None if not enough clean data or zero variance."""
    s = pd.DataFrame({"a": pd.to_numeric(a, errors="coerce"),
                      "b": pd.to_numeric(b, errors="coerce")}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(s) < 2:
        return None
    if s["a"].std(ddof=1) == 0 or s["b"].std(ddof=1) == 0:
        return None
    r = s["a"].corr(s["b"])
    return None if pd.isna(r) else round(float(r), 2)

def get_corr_companies(data, price_data, months_window=2):
    """
    data: {'keywords': [{'keyword','type','trend': 'MM/DD/YYYY: 1,234, ...'}, ...]}
    price_data: iterable with at least ['date','close']
    months_window: months back from max date for the "recent" correlation
    """
    df_price_base = pd.DataFrame(price_data).copy()
    df_price_base["date"] = pd.to_datetime(df_price_base["date"])
    df_price_base = df_price_base.set_index("date").sort_index()

    results = []

    for kw_dict in data.get('keywords', []):
        dtype = kw_dict.get('type', '')
        prefix = "#" if dtype == "Tiktok" else ""
        kw_label = f"{prefix}{kw_dict.get('keyword','')} ({dtype})"

        trend_str = kw_dict.get('trend', '') or ''
        pairs = [p.strip() for p in trend_str.split(",") if p.strip()]
        trend = []
        for item in pairs:
            if ":" not in item:
                continue
            dpart, vpart = item.split(":", 1)
            try:
                d = datetime.strptime(dpart.strip(), "%m/%d/%Y")
                v = int(vpart.strip().replace(",", ""))
                trend.append((d, v))
            except Exception:
                continue

        if not trend:
            results.append({
                "label": kw_label, "keyword": kw_dict.get('keyword'), "type": dtype,
                "Long-term Correlation": None, "Short-term Correlation": None
            })
            continue

        df_trend = pd.DataFrame(trend, columns=["date", "trend_volume"]).set_index("date").sort_index()

        # Your custom aligner
        aligned_price = adjust_to_nearest_dates(df_price_base, df_trend)

        # Join & clean
        df_combined = aligned_price.join(df_trend, how="inner")
        if df_combined.empty:
            results.append({
                "label": kw_label, "keyword": kw_dict.get('keyword'), "type": dtype,
                "Long-term Correlation": None, "Short-term Correlation": None
            })
            continue

        # Coerce numeric & drop infs early
        for col in ("close", "trend_volume"):
            df_combined[col] = pd.to_numeric(df_combined[col], errors="coerce")
        df_combined = df_combined.replace([np.inf, -np.inf], np.nan)

        # Overall correlation (safe)
        corr_all = safe_corr(df_combined["close"], df_combined["trend_volume"])

        # Recent window correlation (safe)
        cutoff = df_combined.index.max() - pd.DateOffset(months=months_window)
        df_last = df_combined[df_combined.index >= cutoff]
        corr_3m = safe_corr(df_last["close"], df_last["trend_volume"]) if not df_last.empty else None

        results.append({
            "label": kw_label,
            "keyword": kw_dict.get('keyword'),
            "type": dtype,
            "Long-term Correlation": corr_all,
            "Short-term Correlation": corr_3m
        })

    return results


def merge_dict_lists(list1, list2):
    # index list2 by (ticker, code)
    index = {(d['ticker'], d['code']): d for d in list2}
    merged = []
    for d in list1:
        key = (d.get('ticker'), d.get('code'))
        if key in index:
            merged.append({**d, **index[key]})
        else:
            merged.append(d.copy())
    return merged

def merge_dict_lists_companies(list1, list2):
    # index list2 by (ticker, code)
    index = {(d['keyword'], d['type']): d for d in list2}
    merged = []
    for d in list1:
        key = (d.get('keyword'), d.get('type'))
        if key in index:
            merged.append({**d, **index[key]})
        else:
            merged.append(d.copy())
    return merged