import pandas as pd


AUTHOR_DTA_PATH = r"E:\_coding\momentum-replication\data\momentum_daily.dta"

T1_EFFECTIVE_DATE = "2024-05-28"
T2_START_DATE = "2017-09-05"


def bps(x):
    return x * 10_000


def calc_boundary_shift(df, return_col):
    # restrict to T+2 era pre-period plus post-T+1 period
    sample = df[df["date"] >= T2_START_DATE].copy()

    pre = sample[sample["date"] < T1_EFFECTIVE_DATE]
    post = sample[sample["date"] >= T1_EFFECTIVE_DATE]

    pre_t4 = pre[pre["t"] == -4][return_col].mean()
    pre_t3 = pre[pre["t"] == -3][return_col].mean()

    post_t4 = post[post["t"] == -4][return_col].mean()
    post_t3 = post[post["t"] == -3][return_col].mean()

    pre_diff = pre_t4 - pre_t3
    post_diff = post_t4 - post_t3

    did = post_diff - pre_diff

    return {
        "pre_t4": pre_t4,
        "pre_t3": pre_t3,
        "post_t4": post_t4,
        "post_t3": post_t3,
        "pre_diff": pre_diff,
        "post_diff": post_diff,
        "did": did,
    }


df = pd.read_stata(AUTHOR_DTA_PATH)

# Create possible loser-return definitions.
# We are testing which definition matches the paper/repo headline T+1 DiD most closely.
df["losers_raw"] = df["losers_vw"]
df["losers_minus_mktrf"] = df["losers_vw"] - df["mktrf"]
df["losers_minus_market"] = df["losers_vw"] - (df["mktrf"] + df["rf"])

return_cols = [
    "losers_raw",
    "losers_minus_mktrf",
    "losers_minus_market",
]

for col in return_cols:
    result = calc_boundary_shift(df, col)

    print(f"\nReturn definition: {col}")
    print(f"Pre T-4:   {bps(result['pre_t4']): .2f} bps")
    print(f"Pre T-3:   {bps(result['pre_t3']): .2f} bps")
    print(f"Post T-4:  {bps(result['post_t4']): .2f} bps")
    print(f"Post T-3:  {bps(result['post_t3']): .2f} bps")
    print(f"Pre diff T-4 minus T-3:   {bps(result['pre_diff']): .2f} bps")
    print(f"Post diff T-4 minus T-3:  {bps(result['post_diff']): .2f} bps")
    print(f"DiD-style shift:          {bps(result['did']): .2f} bps")