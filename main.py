import yfinance as yf

data = yf.download("AAPL", start="2000-01-01")
# flatten columns
data.columns = data.columns.droplevel(1)

data.to_csv("data/raw/AAPL.csv", index=True)

# print(data.head())
print("saved")