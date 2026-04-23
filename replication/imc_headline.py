import pandas as pd
import numpy as np

# load authors' bundled portfolio data
df = pd.read_stata(r"E:\_coding\momentum-replication\data\momentum_daily.dta")

# match paper sample
df = df[df["date"] >= "1980-01-01"].copy()

# define PreTOM
pretom_mask = (df["t"] >= -9) & (df["t"] <= -4)
rest_mask = ~pretom_mask

# full WML wealth
df["full_wml_growth"] = 1 + df["wml_vw"]

# PreTOM-only: invest in WML only on PreTOM days, otherwise cash
df["pretom_only_growth"] = np.where(pretom_mask, 1 + df["wml_vw"], 1.0)

# Rest-only: invest in WML only outside PreTOM, otherwise cash
df["rest_only_growth"] = np.where(rest_mask, 1 + df["wml_vw"], 1.0)

# cumulative wealth from $1
df["full_wml_wealth"] = df["full_wml_growth"].cumprod()
df["pretom_only_wealth"] = df["pretom_only_growth"].cumprod()
df["rest_only_wealth"] = df["rest_only_growth"].cumprod()

print("PreTOM-only cumulative wealth:", round(df["pretom_only_wealth"].iloc[-1], 2))
print("Full WML cumulative wealth:", round(df["full_wml_wealth"].iloc[-1], 2))
print("Rest-of-month cumulative wealth:", round(df["rest_only_wealth"].iloc[-1], 2))


full_terminal = df["full_wml_wealth"].iloc[-1]
pretom_terminal = df["pretom_only_wealth"].iloc[-1]
rest_terminal = df["rest_only_wealth"].iloc[-1]

pretom_log_wealth = np.log(pretom_terminal)
full_log_wealth = np.log(full_terminal)
rest_log_wealth = np.log(rest_terminal)

pretom_share = pretom_log_wealth / full_log_wealth
rest_share = rest_log_wealth / full_log_wealth

print("\nLog wealth:")
print("PreTOM-only log wealth:", round(pretom_log_wealth, 4))
print("Full WML log wealth:", round(full_log_wealth, 4))
print("Rest-of-month log wealth:", round(rest_log_wealth, 4))

print("\nShare of full log wealth:")
print("PreTOM share:", round(pretom_share * 100, 1), "%")
print("Rest share:", round(rest_share * 100, 1), "%")