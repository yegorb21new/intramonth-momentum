import yfinance as yf

tickers = ["AAPL", "MSFT", "SPY"]

for ticker in tickers:
    data = yf.download(ticker, start="2000-01-01")
    # flatten columns
    data.columns = data.columns.droplevel(1)
    data.to_csv(f"data/raw/{ticker}.csv", index=True)

# print(data.head())
print("saved")