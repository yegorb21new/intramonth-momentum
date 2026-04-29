## Baseline Replication: Author-Provided Portfolio Data

### Objective
Establish a control / baseline case before interpreting any public-data proxy results.

### Data Source
- Authors’ bundled dataset: `momentum_daily.dta`
- Source repo: Nathan, Suominen, and Tasa (2026), *The Intramonth Momentum Cycle*
- Sample used: **1980-01-01 to 2025-12-31**
- Frequency: daily
- Portfolio fields used:
  - `wml_vw`
  - `losers_vw`
  - `t`

### Method
- Defined **PreTOM** as trading days `t = -9` to `t = -4`
- Defined **Rest of Month** as all other trading days
- Computed:
  - mean daily WML returns in PreTOM and Rest
  - mean daily loser returns in PreTOM and Rest
  - cumulative wealth for:
    - full WML strategy
    - PreTOM-only WML strategy
    - Rest-of-month-only WML strategy
  - share of total **log wealth** attributable to PreTOM vs Rest

### Results
#### Mean Daily Returns
- **WML PreTOM mean:** `10.1495` bps/day
- **WML Rest mean:** `2.3876` bps/day
- **Losers PreTOM mean:** `-11.3227` bps/day
- **Losers Rest mean:** `5.5148` bps/day

#### Cumulative Wealth
- **PreTOM-only cumulative wealth:** `$18.78`
- **Full WML cumulative wealth:** `$44.46`
- **Rest-of-month cumulative wealth:** `$2.37`

#### Log Wealth Decomposition
- **PreTOM-only log wealth:** `2.9328`
- **Full WML log wealth:** `3.7946`
- **Rest-of-month log wealth:** `0.8618`

- **PreTOM share of full log wealth:** `77.3%`
- **Rest-of-month share of full log wealth:** `22.7%`

### Interpretation
This replication matches the paper’s headline portfolio-level findings essentially exactly. This confirms that:
- the paper’s `t` indexing was interpreted correctly
- the PreTOM window was implemented correctly
- the basic portfolio-level statistics and wealth calculations are being computed correctly in our Python code

### Importance
This is the first true control / baseline result for the project.

All subsequent Yahoo/public-data analysis should be treated as a **separate proxy extension**, not as direct paper replication.

### Notes
- Mean return replication matched essentially exactly
- Cumulative wealth replication matched exactly
- Log wealth decomposition matched exactly
- Simple t-stat approximations were close, but exact paper t-stat reproduction was not the focus of this step


## Exploratory Settlement-Regime Window Scan

### Objective
Test whether the strongest intramonth momentum / loser-underperformance windows vary across U.S. equity settlement regimes.

### Method
Using the authors’ bundled `momentum_daily.dta`, I constructed a true month-end countdown variable (`T_end`) where the final trading day of each month equals `0`, and prior trading days equal `-1`, `-2`, etc.

For each settlement regime, I scanned contiguous candidate windows and identified:
- the strongest loser-underperformance window using market-adjusted loser returns
- the strongest WML window using value-weighted WML returns

To reduce noise from rarely observed early-month positions, candidate windows containing thinly observed `T_end` values were excluded.

### Regime Summary

| Regime | Date Range | Obs | Approx. Months | Strongest Loser Window | Loser Mean (bps) | Loser Diff vs Rest (bps) | Loser t-stat | Strongest WML Window | WML Mean (bps) | WML Diff vs Rest (bps) | WML t-stat |
|---|---:|---:|---:|---|---:|---:|---:|---|---:|---:|---:|
| T+5 | 1980-01-01 to 1995-06-06 | 3,901 | 186 | T−3 to T−1 | -15.40 | -8.75 | -7.31 | T−3 to T−1 | 16.05 | 10.63 | 4.70 |
| T+3 | 1995-06-07 to 2017-09-04 | 5,601 | 268 | T−12 to T−5 | -10.02 | -11.10 | -3.28 | T−8 to T−4 | 15.59 | 15.35 | 3.12 |
| T+2 | 2017-09-05 to 2024-05-27 | 1,692 | 81 | T−7 to T−3 | -19.74 | -23.32 | -2.83 | T−7 to T−3 | 23.13 | 26.37 | 2.36 |
| T+1 | 2024-05-28 to 2025-12-31 | 401 | 20 | T−3 to T0 | -21.53 | -27.25 | -1.85 | T−8 to T−6 | 36.53 | 44.53 | 1.87 |

### Interpretation
This scan is exploratory and should not be interpreted as a formal hypothesis test because multiple candidate windows were evaluated.

The strongest WML window in the T+3 regime (`T−8` to `T−4`) is close to the paper’s canonical PreTOM window (`T−9` to `T−4`). In the T+2 regime, the strongest WML and loser-underperformance windows shift later to `T−7` to `T−3`, consistent with the idea that shorter settlement cycles may allow liquidity-driven selling pressure to occur closer to month-end.

The T+1 regime has only ~20 months of data and is too short to infer a stable new window. Its strongest loser-underperformance window (`T−3` to `T0`) is directionally consistent with the paper’s boundary-shift mechanism, but the WML scan is noisy.

### Caveats
- Exploratory window scan / multiple testing risk
- T+1 sample is very small
- Strongest-window ranking may reflect noise; clustering across nearby windows is more informative than exact top row
- Results use authors’ aggregate portfolio data, not stock-level microdata