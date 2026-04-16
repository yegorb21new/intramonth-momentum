import pandas as pd
import requests
import os
from io import StringIO
import yfinance as yf
import matplotlib.pyplot as plt

# get tickers
# url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
# headers = {"User-Agent": "Mozilla/5.0"}
# response = requests.get(url, headers=headers)
# tables = pd.read_html(StringIO(response.text))
# sp500_table = tables[0]

# tickers = sp500_table["Symbol"].tolist()
# tickers = [t.replace(".", "-") for t in tickers]
# tickers.append("SPY")

# success_count = 0
# failed_tickers = []

# for ticker in tickers:
#     try:
#         data = yf.download(ticker, start="2000-01-01")
#         data.columns = data.columns.droplevel(1)
#         data.to_csv(f"data/raw/{ticker}.csv")
#         success_count += 1
#         print(f"saved {ticker}")
#     except Exception as e:
#         failed_tickers.append((ticker, str(e)))
#         print(f"failed {ticker}: {e}")

# print(f"\nSuccessful downloads: {success_count}")
# print(f"Failed downloads: {len(failed_tickers)}")

# if failed_tickers:
#     print("\nFailed tickers:")
#     for ticker, error in failed_tickers:
#         print(f"{ticker}: {error}")


# empty_files = []

# for ticker in tickers:
#     path = f"data/raw/{ticker}.csv"
#     if os.path.exists(path):
#         if os.path.getsize(path) < 1000:  # very small file = likely bad
#             empty_files.append(ticker)
#     else:
#         empty_files.append(ticker)

# print(f"\nBad/empty files: {len(empty_files)}")
# if empty_files:
#     print(empty_files)

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
combined = combined[combined["Date"] >= "2020-01-01"].copy()
print(combined["Date"].min(), combined["Date"].max())

combined = combined[combined["Date"] >= "2025-01-01"].copy()
print(combined["Date"].min(), combined["Date"].max())

# print(combined.head())
# print(f"\nTotal rows: {len(combined)}")
# print(f"Unique tickers: {combined['Ticker'].nunique()}")

combined["ret_1d"] = combined.groupby("Ticker")["Close"].pct_change()
# print(combined.head(10))

# get last trading day of each month per ticker
combined["month"] = combined["Date"].dt.to_period("M")

# rank days within each month (reverse so month-end = 0)
combined["day_rank"] = combined.groupby(["Ticker", "month"])["Date"].rank(method="first", ascending=True)

combined["days_in_month"] = combined.groupby(["Ticker", "month"])["Date"].transform("count")

# T = 0 is last day → so subtract
combined["T"] = combined["day_rank"] - combined["days_in_month"]

# print(combined[["Date", "Ticker", "T"]].head(40))

# average return by T (all stocks)
avg_by_T = combined.groupby("T")["ret_1d"].mean()

# focus on last ~20 trading days
window = avg_by_T.loc[-20:0]

# print(window)
# show avg return for all stocks by trading days to month end
# plt.figure(figsize=(10, 5))
# plt.plot(window.index, window.values)
# plt.axhline(0)
# plt.title("Average Return by T (All Stocks)")
# plt.xlabel("T (Trading Days to Month-End)")
# plt.ylabel("Average Daily Return")
# plt.show()

# 12-1 momentum (skip last 21 trading days)
combined["ret_12m"] = combined.groupby("Ticker")["Close"].pct_change(252)
combined["ret_1m"] = combined.groupby("Ticker")["Close"].pct_change(21)

combined["momentum"] = combined["ret_12m"] - combined["ret_1m"]

# rank into deciles each day
combined["momentum_rank"] = combined.groupby("Date")["momentum"].rank(pct=True)

# define losers and winners
losers = combined[combined["momentum_rank"] <= 0.1]
winners = combined[combined["momentum_rank"] >= 0.9]

loser_avg = losers.groupby("T")["ret_1d"].mean()
winner_avg = winners.groupby("T")["ret_1d"].mean()

window_losers = loser_avg.loc[-20:0]
window_winners = winner_avg.loc[-20:0]

# define window
window_mask = (combined["T"] >= -9) & (combined["T"] <= -4)
rest_mask = ~window_mask

loser_window = combined[(combined["momentum_rank"] <= 0.1) & window_mask]["ret_1d"].mean()
winner_window = combined[(combined["momentum_rank"] >= 0.9) & window_mask]["ret_1d"].mean()

loser_rest = combined[(combined["momentum_rank"] <= 0.1) & rest_mask]["ret_1d"].mean()
winner_rest = combined[(combined["momentum_rank"] >= 0.9) & rest_mask]["ret_1d"].mean()

# print(f"Losers avg return (T-9 to T-4): {loser_window}")
# print(f"Winners avg return (T-9 to T-4): {winner_window}")
# print(f"Spread (WML): {winner_window - loser_window}")

# print(f"\nLosers rest: {loser_rest}")
# print(f"Winners rest: {winner_rest}")
# print(f"Spread rest: {winner_rest - loser_rest}")

# define window again (after filtering)
window_mask = (combined["T"] >= -9) & (combined["T"] <= -4)

# keep only window data
window_data = combined[window_mask].copy()

# add year-month label
window_data["year_month"] = window_data["Date"].dt.to_period("M")

# compute loser and winner returns per month
monthly = window_data.groupby(["year_month"]).apply(
    lambda df: pd.Series({
        "loser_ret": df[df["momentum_rank"] <= 0.1]["ret_1d"].mean(),
        "winner_ret": df[df["momentum_rank"] >= 0.9]["ret_1d"].mean()
    })
)

# compute spread
monthly["spread"] = monthly["winner_ret"] - monthly["loser_ret"]

# print(monthly)

print("\nMonthly spread stats:")
print(monthly["spread"].describe())

# plt.figure(figsize=(10,5))
# plt.plot(window_losers.index, window_losers.values, label="Losers")
# plt.plot(window_winners.index, window_winners.values, label="Winners")
# plt.axhline(0)
# plt.legend()
# plt.title("Losers vs Winners Return by T")
# plt.show()

# plt.figure(figsize=(10,5))
# monthly["spread"].plot(kind="bar")
# plt.axhline(0)
# plt.title("Monthly WML Spread (T-9 to T-4)")
# plt.ylabel("Spread")
# plt.show()

# compute SPY return for each month (full month return)
spy = combined[combined["Ticker"] == "SPY"].copy()
spy["year_month"] = spy["Date"].dt.to_period("M")

spy_monthly = spy.groupby("year_month")["ret_1d"].sum()

# merge with your monthly spreads
monthly = monthly.merge(spy_monthly.rename("spy_ret"), left_index=True, right_index=True)

# split months
down_months = monthly[monthly["spy_ret"] < 0]
up_months = monthly[monthly["spy_ret"] >= 0]

print("\nDown months avg spread:", down_months["spread"].mean())
print("Up months avg spread:", up_months["spread"].mean())