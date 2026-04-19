from src.data import get_sp500_tickers, download_price_data, validate_raw_files
from src.analysis import (
    load_data,
    preprocess_data,
    add_momentum,
    filter_date_range,
    calculate_window_returns,
    calculate_monthly_window_spreads,
    calculate_avg_returns_by_t,
    calculate_loser_winner_returns_by_t,
    split_monthly_spreads_by_spy_direction,
    plot_avg_returns_by_t,
    plot_loser_winner_returns_by_t,
    plot_monthly_spreads
)

WINDOW_START = -6
WINDOW_END = -2

START_DATE = "2025-01-01"

# tickers = get_sp500_tickers()

# OPTIONAL: run once to download data
# download_price_data(tickers)

# OPTIONAL: validate downloaded files
# validate_raw_files(tickers)

combined = load_data()
combined = preprocess_data(combined)
combined = filter_date_range(combined, start_date=START_DATE)
combined = add_momentum(combined)

avg_by_T = calculate_avg_returns_by_t(combined)
window_losers, window_winners = calculate_loser_winner_returns_by_t(combined)

results = calculate_window_returns(combined, WINDOW_START, WINDOW_END)
monthly = calculate_monthly_window_spreads(combined, WINDOW_START, WINDOW_END)
monthly_with_spy, down_months, up_months = split_monthly_spreads_by_spy_direction(combined, monthly)

print(combined["Date"].min(), combined["Date"].max())


print(f"Losers avg return (T-6 to T-2): {results['loser_window']}")
print(f"Winners avg return (T-6 to T-2): {results['winner_window']}")
print(f"Spread (WML): {results['spread_window']}")

print(f"\nLosers rest: {results['loser_rest']}")
print(f"Winners rest: {results['winner_rest']}")
print(f"Spread rest: {results['spread_rest']}")


print("\nMonthly spread stats:")
print(monthly["spread"].describe())

print(monthly)


print("\nDown months avg spread:", down_months["spread"].mean())
print("Up months avg spread:", up_months["spread"].mean())

plot_avg_returns_by_t(avg_by_T)
plot_loser_winner_returns_by_t(window_losers, window_winners)
plot_monthly_spreads(monthly)