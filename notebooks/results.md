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