# Intramonth Momentum & Liquidity Flow Analysis

## Overview

This project analyzes intramonth equity return behavior to investigate whether **institutional liquidity flows drive predictable selling pressure in recent underperformers ("losers") near month-end**.

The analysis is inspired by academic research on return concentration and flow driven price impact, with a focus on **post-2024 (T+1 settlement) market behavior**.

---

## Key Question

Do stocks with poor prior performance exhibit systematic underperformance in the final trading days of the month due to forced institutional selling?

---

## Data

- Universe: Current S&P 500 constituents (~500 equities)
- Source: Yahoo Finance (`yfinance`)
- Frequency: Daily
- Time range:
  - Full dataset: 2000–present
  - Primary analysis: 2025–2026 (post T+1 settlement)

---

## Methodology

### 1. Return Construction
- Daily returns computed as:
  \[
  r_t = \frac{P_t}{P_{t-1}} - 1
  \]

### 2. Intramonth Indexing
- Each trading day is labeled relative to month-end:
  - `T = 0` → last trading day of the month
  - `T = -1, -2, ...` → prior trading days

### 3. Momentum Definition (12–1)
- Long-term momentum:
  - 12-month return excluding the most recent month
- Computed as:
  - `12m return - 1m return`

### 4. Cross-Sectional Ranking
- Stocks ranked daily into percentiles based on momentum:
  - Bottom 10% → **Losers**
  - Top 10% → **Winners**

### 5. Window Analysis
Two key windows evaluated:
- **Pre-month-end (original):** `T−9 to T−4`
- **Shifted window (post T+1 hypothesis):** `T−6 to T−2`

### 6. Metrics
- Average daily returns:
  - Losers vs Winners
  - Window vs rest of month
- Monthly spread (WML = Winners − Losers)

---

## Results (2025–2026)

### 1. Strong Effect

| Group | Window (T−6 to T−2) | Rest of Month |
|------|--------------------|--------------|
| **Losers** | **−0.33% / day** | +0.15% / day |
| Winners | +0.75% / day | +0.22% / day |

- Both losers and winners exhibit amplified returns in the pre-month-end window, resulting in a sharp increase in cross-sectional dispersion
- Losers shift from positive to negative returns, while winners experience a significant increase in positive returns

---

### 2. Concentrated / Episodic Behavior

- Effect is **not present every month**
- Strongest in:
  - Feb–Apr 2026
- Weak or negligible in other months

---

### 3. Window Shift Evidence

- Stronger signal observed in:
  - **T−6 to T−2**
- Weaker in:
  - T−9 to T−4

This is consistent with:
> **Timing shifts following T+1 settlement implementation**

---

### 4. Not Explained by Market Direction

- Similar spread magnitude in:
  - Up months
  - Down months

Suggests:
> Effect is driven by **flows / positioning**, not general market trends

---

## Interpretation

The results support a **flow-driven mechanism**:

- Institutional rebalancing and liquidity needs lead to:
  - **systematic selling of recent losers**
  - concentrated in a narrow pre-month-end window

The behavior appears:
- **non-linear**
- **regime-dependent**
- **time-shifted in recent years**

---

## Limitations

- Uses **current S&P 500 membership** (survivorship bias)
- No transaction costs or liquidity filters
- Small recent sample (2025–2026)
- Equal-weighted returns (no size weighting)

---

## Future Work

- Expand to survivorship-bias-free datasets (CRSP)
- Incorporate liquidity and market cap filters
- Test robustness across longer time horizons
- Simulate trade execution and PnL
- Explore volatility and positioning regimes

---

## Tech Stack

- Python
- pandas
- matplotlib
- yfinance

---

## Repository Structure

```
intramonth-momentum/
│
├── data/
│ ├── raw/ # downloaded price data
│ └── processed/
│
├── src/
├── notebooks/
├── main.py
└── README.md
```