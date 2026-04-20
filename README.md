# Intramonth Momentum & Liquidity Flow Analysis

## Overview

This project investigates intramonth equity return behavior to explore whether **institutional liquidity flows are associated with time-concentrated cross-sectional return patterns near month-end**.

The analysis is inspired by academic research on return concentration and flow-driven price impact, with a particular focus on **post-2024 (T+1 settlement) market behavior**. Citation to original paper:
```
Nathan, D., Suominen, M., and Tasa, J. (2026).
"The Intramonth Momentum Cycle." Working Paper.
Available at SSRN: https://ssrn.com/abstract=6426026
```

---

## Research Question

Do stocks with poor prior performance exhibit systematic differences in return behavior in the final trading days of the month?

---

## Data

- Universe: Current S&P 500 constituents (~500 equities)
- Source: Yahoo Finance (`yfinance`)
- Frequency: Daily
- Time range:
  - Raw data: 2000–present
  - Primary analysis: June 2024–present (post T+1 settlement)

---

## Methodology

### 1. Return Construction
Daily returns are computed as:

\[
r_t = \frac{P_t}{P_{t-1}} - 1
\]

---

### 2. Intramonth Indexing
Each trading day is labeled relative to month-end:

- `T = 0` → last trading day of the month  
- `T = -1, -2, ...` → prior trading days  

---

### 3. Momentum Definition
Momentum is defined as:

- 12-month return excluding the most recent month

Computed as:

- `12m return − 1m return`

---

### 4. Cross-Sectional Ranking
Stocks are ranked daily by momentum:

- Bottom 10% → **Losers**
- Top 10% → **Winners**

---

### 5. Window Analysis
Intramonth windows evaluated:

- Baseline: `T−9 to T−4`
- Shifted (post–T+1 hypothesis): `T−6 to T−2`

---

### 6. Metrics

The analysis computes:

- Average daily returns:
  - Winners vs losers
  - Window vs rest of month
- Monthly cross-sectional spread:
  - WML (Winner − Loser)
- Descriptive statistics:
  - mean, standard deviation
  - simple t-statistics (monthly level)
- Robustness checks:
  - leave-one-out sensitivity analysis

---

## Current Findings

Initial analysis of the June 2024–present sample suggests:

- Cross-sectional return differences between winners and losers tend to be **larger in specific pre-month-end windows than in the rest of the month**
- This increase in dispersion appears in multiple months and is **not driven by a single outlier observation**
- The effect is **variable across months**, indicating potential regime dependence
- Both winners and losers contribute to the spread, with **winner-side returns playing a significant role in the expanded sample**

These observations are **descriptive** and based on a limited sample period. They should not be interpreted as statistically definitive or causal.

---

## Interpretation

The observed patterns are **consistent with**, but do not prove, the possibility that:

- institutional rebalancing or liquidity-driven activity may contribute to time-specific return behavior
- intramonth effects may shift over time (e.g., post T+1 settlement)

Alternative explanations (e.g., macro events, volatility regimes, factor rotations) remain plausible.

---

## Limitations

- Uses **current S&P 500 membership** (survivorship bias)
- Short effective sample period for primary analysis
- No transaction costs or liquidity constraints
- Equal-weighted returns (no size adjustment)
- Assumes independence of monthly observations in simple statistical summaries

---

## Future Work

- Expand sample and test stability across time
- Incorporate survivorship-bias-free datasets
- Analyze sensitivity to volatility and macro regimes
- Implement and evaluate trading strategies
- Introduce more rigorous statistical testing

---

## Tech Stack

- Python
- pandas
- matplotlib
- yfinance
