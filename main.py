import pandas as pd
import requests
import os
from io import StringIO
import yfinance as yf

# get tickers
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
tables = pd.read_html(StringIO(response.text))
sp500_table = tables[0]

tickers = sp500_table["Symbol"].tolist()
tickers = [t.replace(".", "-") for t in tickers]

success_count = 0
failed_tickers = []

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

# print(combined.head())
# print(f"\nTotal rows: {len(combined)}")
# print(f"Unique tickers: {combined['Ticker'].nunique()}")

combined["ret_1d"] = combined.groupby("Ticker")["Close"].pct_change()
print(combined.head(10))