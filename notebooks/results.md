## Reference: Paper Results (Baseline)

### Source
[The Intramonth Momentum Cycle](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6426026)

### Key Setup
- Universe: [e.g., CRSP equities]
- Period: [e.g., 1980–2020]
- Momentum: 12–1
- Window: T−9 to T−4

### Reported Results
- Mean spread: X
- T-stat: Y

### Notes
- Uses survivorship-bias-free data
- Includes delisting returns
- Likely value-weighted (if applicable)

### Interpretation
These results serve as a reference benchmark and are not expected to match directly due to differences in data construction.


## Experiment: T−6 to T−2 Window (Post T+1)

### Config
- Start date: 2024-06-01
- Window: T−6 to T−2
- Universe: Current S&P 500
- Momentum: 12–1

### Results
- Mean spread: 0.00630
- Std: 0.00671
- T-stat: 3.12
- N months: 11

### Contribution
- Losers: ~0.00% (window), ~0.17% (rest)
- Winners: ~0.63% (window), ~0.18% (rest)

### Notes
- Spread increase primarily driven by winners
- Effect not driven by a single month (leave-one-out t-stat tests were stable, maintaining tstat of ~2.7-3.3)
- High variance across months

### Caveats
- Small sample
- Survivorship bias
- Potential macro regime effects