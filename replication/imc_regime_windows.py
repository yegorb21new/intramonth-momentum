import pandas as pd
import numpy as np
from author_data import load_author_data



AUTHOR_DTA_PATH = r"E:\_coding\momentum-replication\data\momentum_daily.dta"

REGIMES = {
    "T+5": ("1980-01-01", "1995-06-06"),
    "T+3": ("1995-06-07", "2017-09-04"),
    "T+2": ("2017-09-05", "2024-05-27"),
    "T+1": ("2024-05-28", "2025-12-31"),
}


def bps(x):
    return x * 10_000


def t_stat(series):
    s = series.dropna()
    n = len(s)

    if n < 2:
        return np.nan

    mean = s.mean()
    std = s.std(ddof=1)
    se = std / np.sqrt(n)

    return mean / se if se != 0 else np.nan


def summarize_by_t(df, return_col):
    summary = (
        df.groupby("T_end")[return_col]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"T_end": "t", "mean": "mean_return", "count": "n_obs"})
    )

    summary["mean_bps"] = summary["mean_return"] * 10_000

    return summary[["t", "mean_bps", "n_obs"]]


def scan_windows(
    df,
    return_col,
    start_min=-20,
    start_max=-1,
    end_max=0,
    min_len=3,
    max_len=8,
    min_day_obs_pct=0.80
):
    results = []

    day_counts = df.groupby("T_end").size()
    max_day_count = day_counts.max()
    min_day_count = max_day_count * min_day_obs_pct

    for window_start in range(start_min, start_max + 1):
        for window_end in range(window_start, end_max + 1):
            length = window_end - window_start + 1

            if length < min_len or length > max_len:
                continue

            included_days = list(range(window_start, window_end + 1))

            # Skip windows containing thin / rarely observed T_end values
            if any(day_counts.get(day, 0) < min_day_count for day in included_days):
                continue

            window_mask = (df["T_end"] >= window_start) & (df["T_end"] <= window_end)
            rest_mask = ~window_mask

            window_returns = df.loc[window_mask, return_col]
            rest_returns = df.loc[rest_mask, return_col]

            window_mean = window_returns.mean()
            rest_mean = rest_returns.mean()
            diff = window_mean - rest_mean

            results.append({
                "window_start": window_start,
                "window_end": window_end,
                "length": length,
                "window_mean_bps": bps(window_mean),
                "rest_mean_bps": bps(rest_mean),
                "diff_bps": bps(diff),
                "window_t_stat": t_stat(window_returns),
                "n_window_obs": window_returns.dropna().shape[0],
                "n_rest_obs": rest_returns.dropna().shape[0],
            })

    return pd.DataFrame(results)

def format_window(row):
    return f"T{int(row['window_start'])} to T{int(row['window_end'])}"


def build_regime_summary(df):
    summary_rows = []

    for regime_name, (start_date, end_date) in REGIMES.items():
        regime_df = df[
            (df["date"] >= start_date) &
            (df["date"] <= end_date)
        ].copy()

        loser_windows = scan_windows(regime_df, "losers_minus_mktrf")
        loser_windows = loser_windows.sort_values(
            ["diff_bps", "window_t_stat"],
            ascending=[True, True]
        )

        wml_windows = scan_windows(regime_df, "wml_vw")
        wml_windows = wml_windows.sort_values(
            ["diff_bps", "window_t_stat"],
            ascending=[False, False]
        )

        top_loser = loser_windows.iloc[0]
        top_wml = wml_windows.iloc[0]

        summary_rows.append({
            "regime": regime_name,
            "date_range": f"{start_date} to {end_date}",
            "obs": len(regime_df),
            "approx_months": regime_df["ym"].nunique(),

            "strongest_loser_window": format_window(top_loser),
            "loser_window_mean_bps": top_loser["window_mean_bps"],
            "loser_diff_vs_rest_bps": top_loser["diff_bps"],
            "loser_t_stat": top_loser["window_t_stat"],
            "loser_window_obs": top_loser["n_window_obs"],

            "strongest_wml_window": format_window(top_wml),
            "wml_window_mean_bps": top_wml["window_mean_bps"],
            "wml_diff_vs_rest_bps": top_wml["diff_bps"],
            "wml_t_stat": top_wml["window_t_stat"],
            "wml_window_obs": top_wml["n_window_obs"],
        })

    return pd.DataFrame(summary_rows)

df = load_author_data()

for regime_name, (start_date, end_date) in REGIMES.items():
    regime_df = df[
        (df["date"] >= start_date) &
        (df["date"] <= end_date)
    ].copy()

    print("\n" + "=" * 80)
    print(f"Regime: {regime_name}")
    print(f"Dates: {start_date} to {end_date}")
    print(f"Observations: {len(regime_df)}")

    print("\nLoser market-adjusted returns by t:")
    loser_by_t = summarize_by_t(regime_df, "losers_minus_mktrf")
    print(loser_by_t.to_string(index=False))

    print("\nWML returns by t:")
    wml_by_t = summarize_by_t(regime_df, "wml_vw")
    print(wml_by_t.to_string(index=False))

    print("\nTop candidate loser-underperformance windows:")
    loser_windows = scan_windows(regime_df, "losers_minus_mktrf")
    loser_windows = loser_windows.sort_values(
        ["diff_bps", "window_t_stat"],
        ascending=[True, True]
    )
    print(loser_windows.head(10).to_string(index=False))

    print("\nTop candidate WML windows:")
    wml_windows = scan_windows(regime_df, "wml_vw")
    wml_windows = wml_windows.sort_values(
        ["diff_bps", "window_t_stat"],
        ascending=[False, False]
    )
    print(wml_windows.head(10).to_string(index=False))


summary = build_regime_summary(df)

print("\n" + "=" * 100)
print("Settlement Regime Window Summary")
print("=" * 100)

print(summary.to_string(index=False))