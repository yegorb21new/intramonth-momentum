import pandas as pd
import requests
import os
from io import StringIO
import yfinance as yf
import matplotlib.pyplot as plt


def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    tables = pd.read_html(StringIO(response.text))
    sp500_table = tables[0]

    tickers = sp500_table["Symbol"].tolist()
    tickers = [t.replace(".", "-") for t in tickers]
    tickers.append("SPY")

    return tickers


def load_data():
    all_data = []

    for file in os.listdir("data/raw"):
        if file.endswith(".csv"):
            ticker = file.replace(".csv", "")
            df = pd.read_csv(f"data/raw/{file}")
            df["Ticker"] = ticker
            all_data.append(df)

    combined = pd.concat(all_data, ignore_index=True)

    combined["Date"] = pd.to_datetime(combined["Date"])
    combined = combined.sort_values(["Ticker", "Date"])

    return combined


def preprocess_data(combined):
    combined["ret_1d"] = combined.groupby("Ticker")["Close"].pct_change()

    combined["month"] = combined["Date"].dt.to_period("M")
    combined["day_rank"] = combined.groupby(["Ticker", "month"])["Date"].rank(method="first", ascending=True)
    combined["days_in_month"] = combined.groupby(["Ticker", "month"])["Date"].transform("count")
    combined["T"] = combined["day_rank"] - combined["days_in_month"]

    return combined


def add_momentum(combined):
    combined["ret_12m"] = combined.groupby("Ticker")["Close"].pct_change(252)
    combined["ret_1m"] = combined.groupby("Ticker")["Close"].pct_change(21)
    combined["momentum"] = combined["ret_12m"] - combined["ret_1m"]
    combined["momentum_rank"] = combined.groupby("Date")["momentum"].rank(pct=True)

    return combined


def filter_date_range(combined, start_date=None, end_date=None):
    if start_date is not None:
        combined = combined[combined["Date"] >= start_date].copy()

    if end_date is not None:
        combined = combined[combined["Date"] <= end_date].copy()

    return combined


def calculate_window_returns(combined, window_start, window_end):
    window_mask = (combined["T"] >= window_start) & (combined["T"] <= window_end)
    rest_mask = ~window_mask

    loser_window = combined[(combined["momentum_rank"] <= 0.1) & window_mask]["ret_1d"].mean()
    winner_window = combined[(combined["momentum_rank"] >= 0.9) & window_mask]["ret_1d"].mean()

    loser_rest = combined[(combined["momentum_rank"] <= 0.1) & rest_mask]["ret_1d"].mean()
    winner_rest = combined[(combined["momentum_rank"] >= 0.9) & rest_mask]["ret_1d"].mean()

    return {
        "loser_window": loser_window,
        "winner_window": winner_window,
        "spread_window": winner_window - loser_window,
        "loser_rest": loser_rest,
        "winner_rest": winner_rest,
        "spread_rest": winner_rest - loser_rest,
    }


def calculate_monthly_window_spreads(combined, window_start, window_end):
    window_mask = (combined["T"] >= window_start) & (combined["T"] <= window_end)

    window_data = combined[window_mask].copy()
    window_data["year_month"] = window_data["Date"].dt.to_period("M")

    monthly = window_data.groupby("year_month").apply(
        lambda df: pd.Series({
            "loser_ret": df[df["momentum_rank"] <= 0.1]["ret_1d"].mean(),
            "winner_ret": df[df["momentum_rank"] >= 0.9]["ret_1d"].mean()
        })
    )

    monthly["spread"] = monthly["winner_ret"] - monthly["loser_ret"]

    return monthly