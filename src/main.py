"""
main.py
-------
End-to-end pipeline:
  1. Fetch 5 years of daily price data for TCS and Infosys via yfinance.
  2. Calculate SMA-20, SMA-50, and RSI-14.
  3. Detect Golden Cross / Death Cross signals.
  4. Save an annotated chart per stock into output/.
  5. Print a text summary of the latest trend & recent signals.

Run from the project root:
    python src/main.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetch_data import fetch_all, DEFAULT_TICKERS
from indicators import add_all_indicators
from analysis import plot_trend_chart, summarize_signals


def run(period: str = "5y"):
    print(f"Starting stock trend analysis for: {list(DEFAULT_TICKERS.keys())}\n")

    raw_data = fetch_all(DEFAULT_TICKERS, period=period, save=True)

    for name, df in raw_data.items():
        enriched = add_all_indicators(df)

        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        enriched_path = os.path.join(data_dir, f"{name}_with_indicators.csv")
        enriched.to_csv(enriched_path)
        print(f"Saved enriched dataset -> {enriched_path}")

        plot_trend_chart(enriched, name, save=True)
        summarize_signals(enriched, name)

    print("\nAnalysis complete. Charts saved in the 'output/' folder, datasets in 'data/'.")


if __name__ == "__main__":
    run()
