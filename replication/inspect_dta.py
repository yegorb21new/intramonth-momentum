import pandas as pd
import numpy as np

df = pd.read_stata(r"E:\_coding\momentum-replication\data\momentum_daily.dta")

df = df[df["date"] >= "1980-01-01"].copy()

pretom_mask = (df["t"] >= -9) & (df["t"] <= -4)
rest_mask = ~pretom_mask

def mean_bps(series):
    return series.mean() * 10000

def t_stat(series):
    s = series.dropna()
    n = len(s)
    mean = s.mean()
    std = s.std(ddof=1)
    se = std / np.sqrt(n)
    return mean / se

print("WML PreTOM mean (bps/day):", mean_bps(df.loc[pretom_mask, "wml_vw"]))
print("WML PreTOM t-stat:", t_stat(df.loc[pretom_mask, "wml_vw"]))

print("WML Rest mean (bps/day):", mean_bps(df.loc[rest_mask, "wml_vw"]))
print("WML Rest t-stat:", t_stat(df.loc[rest_mask, "wml_vw"]))

print("Losers PreTOM mean (bps/day):", mean_bps(df.loc[pretom_mask, "losers_vw"]))
print("Losers PreTOM t-stat:", t_stat(df.loc[pretom_mask, "losers_vw"]))

print("Losers Rest mean (bps/day):", mean_bps(df.loc[rest_mask, "losers_vw"]))
print("Losers Rest t-stat:", t_stat(df.loc[rest_mask, "losers_vw"]))