"""
analysis.py
-----------
Plotting and summary-reporting utilities for the stock trend analysis.
Generates a two-panel chart (price + SMAs on top, RSI on bottom) with
crossover signals marked, and prints a text summary of the most recent
signals.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")


def plot_trend_chart(df: pd.DataFrame, ticker_name: str, save: bool = True) -> str:
    """
    Plot Close price with SMA-20 / SMA-50 overlays plus an RSI subplot,
    marking Golden Cross / Death Cross signals on the price panel.

    Parameters
    ----------
    df : pd.DataFrame
        Output of `indicators.add_all_indicators`, indexed by Date.
    ticker_name : str
        Display name used in the chart title and output filename.
    save : bool
        If True, saves the figure as a PNG into the output/ directory.

    Returns
    -------
    str
        Path to the saved PNG file (empty string if save=False).
    """
    fig, (ax_price, ax_rsi) = plt.subplots(
        2, 1, figsize=(14, 8), sharex=True,
        gridspec_kw={"height_ratios": [3, 1]}
    )

    # --- Price + SMA panel ---
    ax_price.plot(df.index, df["Close"], label="Close Price", color="#1f77b4", linewidth=1.2)
    ax_price.plot(df.index, df["SMA_20"], label="SMA 20", color="#ff7f0e", linewidth=1.1)
    ax_price.plot(df.index, df["SMA_50"], label="SMA 50", color="#2ca02c", linewidth=1.1)

    golden = df[df["Signal"] == "Golden Cross"]
    death = df[df["Signal"] == "Death Cross"]
    ax_price.scatter(golden.index, golden["Close"], marker="^", color="green", s=110,
                      label="Golden Cross (Bullish)", zorder=5)
    ax_price.scatter(death.index, death["Close"], marker="v", color="red", s=110,
                      label="Death Cross (Bearish)", zorder=5)

    ax_price.set_title(f"{ticker_name}: Price Trend with SMA Crossovers (5-Year History)", fontsize=13, fontweight="bold")
    ax_price.set_ylabel("Price")
    ax_price.legend(loc="upper left", fontsize=9)
    ax_price.grid(alpha=0.3)

    # --- RSI panel ---
    ax_rsi.plot(df.index, df["RSI_14"], color="#9467bd", linewidth=1.1, label="RSI (14)")
    ax_rsi.axhline(70, color="red", linestyle="--", linewidth=0.8, label="Overbought (70)")
    ax_rsi.axhline(30, color="green", linestyle="--", linewidth=0.8, label="Oversold (30)")
    ax_rsi.set_ylim(0, 100)
    ax_rsi.set_ylabel("RSI")
    ax_rsi.set_xlabel("Date")
    ax_rsi.legend(loc="upper left", fontsize=8)
    ax_rsi.grid(alpha=0.3)

    ax_rsi.xaxis.set_major_locator(mdates.YearLocator())
    ax_rsi.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    fig.tight_layout()

    out_path = ""
    if save:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, f"{ticker_name}_trend_analysis.png")
        fig.savefig(out_path, dpi=150)
        print(f"Saved chart -> {out_path}")

    plt.close(fig)
    return out_path


def summarize_signals(df: pd.DataFrame, ticker_name: str, last_n: int = 5) -> str:
    """
    Build a short text summary: most recent close/SMA/RSI values and the
    last `last_n` crossover signals found in the data.

    Returns
    -------
    str
        Human-readable summary (also printed to stdout).
    """
    latest = df.iloc[-1]
    signals = df[df["Signal"] != ""].tail(last_n)

    lines = [
        f"\n=== {ticker_name} Summary ===",
        f"Latest date       : {df.index[-1].date()}",
        f"Latest close      : {latest['Close']:.2f}",
        f"SMA 20 / SMA 50    : {latest['SMA_20']:.2f} / {latest['SMA_50']:.2f}",
        f"RSI (14)          : {latest['RSI_14']:.2f}",
        f"Trend momentum    : {'Bullish (SMA20 > SMA50)' if latest['SMA_20'] > latest['SMA_50'] else 'Bearish (SMA20 < SMA50)'}",
        f"RSI condition     : {'Overbought (>70)' if latest['RSI_14'] > 70 else 'Oversold (<30)' if latest['RSI_14'] < 30 else 'Neutral'}",
        f"\nLast {last_n} crossover signals:",
    ]

    if signals.empty:
        lines.append("  (none found in this data range)")
    else:
        for date, row in signals.iterrows():
            lines.append(f"  {date.date()}  ->  {row['Signal']}  (Close: {row['Close']:.2f})")

    summary = "\n".join(lines)
    print(summary)
    return summary
