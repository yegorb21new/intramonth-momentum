import pandas as pd


AUTHOR_DTA_PATH = r"E:\_coding\momentum-replication\data\momentum_daily.dta"


def load_author_data():
    df = pd.read_stata(AUTHOR_DTA_PATH)

    # True trading-day countdown to month-end.
    # Last trading day of month = 0, prior days = -1, -2, ...
    df["day_rank"] = df.groupby("ym")["date"].rank(method="first", ascending=True)
    df["days_in_month"] = df.groupby("ym")["date"].transform("count")
    df["T_end"] = df["day_rank"] - df["days_in_month"]

    # Market-adjusted loser return used in T+1 boundary tests
    df["losers_minus_mktrf"] = df["losers_vw"] - df["mktrf"]

    return df