import pandas as pd
import requests
import os
from io import StringIO
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np



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


def exclude_latest_month(combined):
    latest_month = combined["Date"].max().to_period("M")
    return combined[combined["Date"].dt.to_period("M") < latest_month].copy()


def scan_candidate_windows(
    combined,
    start_min=-12,
    start_max=-4,
    end_max=-1,
    min_len=3,
    max_len=8
):
    results = []

    for window_start in range(start_min, start_max + 1):
        for window_end in range(window_start, end_max + 1):
            length = window_end - window_start + 1

            if length < min_len or length > max_len:
                continue

            monthly_compare = calculate_monthly_window_vs_rest(
                combined,
                window_start,
                window_end
            )

            diff_stats = calculate_t_stats(
                monthly_compare[["diff_spread"]].rename(
                    columns={"diff_spread": "spread"}
                )
            )

            results.append({
                "window_start": window_start,
                "window_end": window_end,
                "length": length,
                "n_months": diff_stats["n"],
                "mean_diff": diff_stats["mean"],
                "std_diff": diff_stats["std"],
                "se_diff": diff_stats["se"],
                "t_stat_diff": diff_stats["t_stat"],
            })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(
        ["t_stat_diff", "mean_diff"],
        ascending=False
    )

    return results_df


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


def calculate_avg_returns_by_t(combined, t_min=-20, t_max=0):
    avg_by_t = combined.groupby("T")["ret_1d"].mean()
    return avg_by_t.loc[t_min:t_max]


def calculate_loser_winner_returns_by_t(combined, t_min=-20, t_max=0):
    losers = combined[combined["momentum_rank"] <= 0.1]
    winners = combined[combined["momentum_rank"] >= 0.9]

    loser_avg = losers.groupby("T")["ret_1d"].mean()
    winner_avg = winners.groupby("T")["ret_1d"].mean()

    loser_window = loser_avg.loc[t_min:t_max]
    winner_window = winner_avg.loc[t_min:t_max]

    return loser_window, winner_window


def split_monthly_spreads_by_spy_direction(combined, monthly):
    spy = combined[combined["Ticker"] == "SPY"].copy()
    spy["year_month"] = spy["Date"].dt.to_period("M")

    spy_monthly = spy.groupby("year_month")["ret_1d"].sum()

    monthly_with_spy = monthly.merge(
        spy_monthly.rename("spy_ret"),
        left_index=True,
        right_index=True
    )

    down_months = monthly_with_spy[monthly_with_spy["spy_ret"] < 0]
    up_months = monthly_with_spy[monthly_with_spy["spy_ret"] >= 0]

    return monthly_with_spy, down_months, up_months


def calculate_t_stats(monthly):
    spreads = monthly["spread"].dropna()

    n = len(spreads)
    mean = spreads.mean()
    std = spreads.std(ddof=1)

    # standard error
    se = std / np.sqrt(n)

    # t-stat
    t_stat = mean / se if se != 0 else np.nan

    return {
        "n": n,
        "mean": mean,
        "std": std,
        "se": se,
        "t_stat": t_stat
    }


def leave_one_out_t_stats(monthly):
    spreads = monthly["spread"].dropna()
    results = []

    for i in range(len(spreads)):
        subset = spreads.drop(spreads.index[i])

        n = len(subset)
        mean = subset.mean()
        std = subset.std(ddof=1)
        se = std / np.sqrt(n)
        t_stat = mean / se if se != 0 else np.nan

        results.append({
            "dropped_month": spreads.index[i],
            "mean": mean,
            "t_stat": t_stat
        })

    return pd.DataFrame(results)


def test_t1_shift(combined, split_date="2024-05-28"):
    # pre vs post split
    pre = combined[combined["Date"] < split_date]
    post = combined[combined["Date"] >= split_date]

    def get_stats(df):
        losers = df[df["momentum_rank"] <= 0.1]

        t_minus_4 = losers[losers["T"] == -4]["ret_1d"].mean()
        t_minus_3 = losers[losers["T"] == -3]["ret_1d"].mean()

        return t_minus_4, t_minus_3

    pre_t4, pre_t3 = get_stats(pre)
    post_t4, post_t3 = get_stats(post)

    # differences
    pre_diff = pre_t3 - pre_t4
    post_diff = post_t3 - post_t4

    return {
        "pre_t4": pre_t4,
        "pre_t3": pre_t3,
        "post_t4": post_t4,
        "post_t3": post_t3,
        "pre_diff": pre_diff,
        "post_diff": post_diff,
        "shift": post_diff - pre_diff
    }


def calculate_monthly_window_vs_rest(combined, window_start, window_end):
    window_mask = (combined["T"] >= window_start) & (combined["T"] <= window_end)
    rest_mask = ~window_mask

    df = combined.copy()
    df["year_month"] = df["Date"].dt.to_period("M")

    def compute_monthly_spread(subset):
        return subset.groupby("year_month").apply(
            lambda x: pd.Series({
                "loser_ret": x[x["momentum_rank"] <= 0.1]["ret_1d"].mean(),
                "winner_ret": x[x["momentum_rank"] >= 0.9]["ret_1d"].mean()
            })
        )

    window_monthly = compute_monthly_spread(df[window_mask]).rename(columns={
        "loser_ret": "window_loser_ret",
        "winner_ret": "window_winner_ret"
    })
    window_monthly["window_spread"] = (
        window_monthly["window_winner_ret"] - window_monthly["window_loser_ret"]
    )

    rest_monthly = compute_monthly_spread(df[rest_mask]).rename(columns={
        "loser_ret": "rest_loser_ret",
        "winner_ret": "rest_winner_ret"
    })
    rest_monthly["rest_spread"] = (
        rest_monthly["rest_winner_ret"] - rest_monthly["rest_loser_ret"]
    )

    monthly_compare = window_monthly.join(rest_monthly, how="outer")
    monthly_compare["diff_spread"] = (
        monthly_compare["window_spread"] - monthly_compare["rest_spread"]
    )

    return monthly_compare


def plot_avg_returns_by_t(avg_by_t, title="Average Return by T (All Stocks)"):
    plt.figure(figsize=(10, 5))
    plt.plot(avg_by_t.index, avg_by_t.values)
    plt.axhline(0)
    plt.title(title)
    plt.xlabel("T (Trading Days to Month-End)")
    plt.ylabel("Average Daily Return")
    plt.show()


def plot_loser_winner_returns_by_t(loser_series, winner_series, title="Losers vs Winners Return by T"):
    plt.figure(figsize=(10, 5))
    plt.plot(loser_series.index, loser_series.values, label="Losers")
    plt.plot(winner_series.index, winner_series.values, label="Winners")
    plt.axhline(0)
    plt.legend()
    plt.title(title)
    plt.xlabel("T (Trading Days to Month-End)")
    plt.ylabel("Average Daily Return")
    plt.show()


def plot_monthly_spreads(monthly, title="Monthly WML Spread"):
    plt.figure(figsize=(10, 5))
    monthly["spread"].plot(kind="bar")
    plt.axhline(0)
    plt.title(title)
    plt.ylabel("Spread")
    plt.show()