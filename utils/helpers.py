from datetime import datetime, timedelta
import calendar
import math

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