import pandas as pd
import requests
import os
from io import StringIO
import yfinance as yf
import matplotlib.pyplot as plt
from src.analysis import get_sp500_tickers, load_data, preprocess_data, add_momentum, filter_date_range, calculate_window_returns, calculate_monthly_window_spreads


WINDOW_START = -6
WINDOW_END = -2

START_DATE = "2025-01-01"


tickers = get_sp500_tickers()

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

combined = load_data()

combined = preprocess_data(combined)

combined = filter_date_range(combined, start_date=START_DATE)
print(combined["Date"].min(), combined["Date"].max())


# average return by T (all stocks)
avg_by_T = combined.groupby("T")["ret_1d"].mean()

# focus on last ~20 trading days
window = avg_by_T.loc[-20:0]

combined = add_momentum(combined)

# define losers and winners
losers = combined[combined["momentum_rank"] <= 0.1]
winners = combined[combined["momentum_rank"] >= 0.9]

loser_avg = losers.groupby("T")["ret_1d"].mean()
winner_avg = winners.groupby("T")["ret_1d"].mean()

window_losers = loser_avg.loc[-20:0]
window_winners = winner_avg.loc[-20:0]

results = calculate_window_returns(combined, WINDOW_START, WINDOW_END)

print(f"Losers avg return (T-6 to T-2): {results['loser_window']}")
print(f"Winners avg return (T-6 to T-2): {results['winner_window']}")
print(f"Spread (WML): {results['spread_window']}")

print(f"\nLosers rest: {results['loser_rest']}")
print(f"Winners rest: {results['winner_rest']}")
print(f"Spread rest: {results['spread_rest']}")

monthly = calculate_monthly_window_spreads(combined, WINDOW_START, WINDOW_END)

print("\nMonthly spread stats:")
print(monthly["spread"].describe())

print(monthly)

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

# print("\nLoser-only stats:")
# print("Window:", loser_window)
# print("Rest:", loser_rest)

# print("\nWinner-only stats:")
# print("Window:", winner_window)
# print("Rest:", winner_rest)