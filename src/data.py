import os
import pandas as pd
import requests
from io import StringIO
import yfinance as yf


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


def download_price_data(tickers, start="2000-01-01", output_dir="data/raw"):
    os.makedirs(output_dir, exist_ok=True)

    success_count = 0
    failed_tickers = []

    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start)
            data.columns = data.columns.droplevel(1)
            data.to_csv(f"{output_dir}/{ticker}.csv")
            success_count += 1
            print(f"saved {ticker}")
        except Exception as e:
            failed_tickers.append((ticker, str(e)))
            print(f"failed {ticker}: {e}")

    print(f"\nSuccessful downloads: {success_count}")
    print(f"Failed downloads: {len(failed_tickers)}")

    if failed_tickers:
        print("\nFailed tickers:")
        for ticker, error in failed_tickers:
            print(f"{ticker}: {error}")


def validate_raw_files(tickers, data_dir="data/raw", min_file_size=1000):
    empty_files = []

    for ticker in tickers:
        path = f"{data_dir}/{ticker}.csv"
        if os.path.exists(path):
            if os.path.getsize(path) < min_file_size:
                empty_files.append(ticker)
        else:
            empty_files.append(ticker)

    print(f"\nBad/empty files: {len(empty_files)}")
    if empty_files:
        print(empty_files)

    return empty_files