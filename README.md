# Stock Price Trend Analysis

**Python · yfinance · Pandas · Matplotlib**

A trend-analysis pipeline for Indian equities (TCS and Infosys) that pulls
five years of historical price data, computes moving-average and momentum
indicators, and flags bullish/bearish crossover signals with annotated
charts.

- Extracted 5 years of historical price data for **TCS** and **Infosys**
  using the `yfinance` API, processing **1,200+ trading-day records per
  stock** for trend analysis.
- Calculated **20-day and 50-day Simple Moving Averages (SMA)** and the
  **Relative Strength Index (RSI)** to identify bullish/bearish crossover
  signals (Golden Cross / Death Cross) and momentum patterns.

## Example Output

Running the pipeline produces a two-panel chart per stock: closing price
with SMA-20 / SMA-50 overlays and marked crossovers on top, RSI momentum
below.

![Example chart](assets/example_chart.png)

*(Sample chart generated from synthetic data for illustration — running
`main.py` will produce real charts for TCS and Infosys in `output/`.)*

## Project Structure

```
stock-trend-analysis/
├── src/
│   ├── fetch_data.py     # Downloads OHLCV data via yfinance, saves CSVs
│   ├── indicators.py     # SMA, RSI, and crossover-signal calculations
│   ├── analysis.py       # Chart plotting + text summary reporting
│   └── main.py           # End-to-end pipeline entry point
├── data/                 # Raw & enriched CSV datasets (generated)
├── output/                # Saved PNG trend charts (generated)
├── requirements.txt
├── .gitignore
└── README.md
```

## How It Works

1. **Data extraction** (`fetch_data.py`) — downloads 5 years of daily
   OHLCV bars for `TCS.NS` and `INFY.NS` (NSE tickers) via `yfinance`,
   saving each stock's raw history as a CSV in `data/`.
2. **Indicator calculation** (`indicators.py`):
   - **SMA-20 / SMA-50** — rolling means of the closing price used to
     gauge short- vs. medium-term trend direction.
   - **RSI-14** — Wilder's Relative Strength Index, measuring momentum
     and identifying overbought (>70) / oversold (<30) conditions.
   - **Crossover detection** — flags a **Golden Cross** (bullish) when
     SMA-20 crosses above SMA-50, and a **Death Cross** (bearish) when it
     crosses below.
3. **Reporting** (`analysis.py`) — renders an annotated chart per stock
   and prints a text summary of the latest values and recent signals.
4. **Orchestration** (`main.py`) — runs steps 1–3 for every configured
   ticker and writes results to `data/` and `output/`.

## Setup

```bash
git clone https://github.com/prajwal2301negi/Stock-Price-Trend-Analysis.git
cd stock-trend-analysis
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run the full pipeline (fetches data, computes indicators, saves charts &
summaries):

```bash
python src/main.py
```

This will:
- Save `data/TCS.csv`, `data/INFOSYS.csv` (raw prices)
- Save `data/TCS_with_indicators.csv`, `data/INFOSYS_with_indicators.csv`
  (prices + SMA/RSI/signal columns)
- Save `output/TCS_trend_analysis.png`, `output/INFOSYS_trend_analysis.png`
- Print a summary of the latest trend and recent crossover signals to the
  console

### Using it as a library

```python
from src.fetch_data import fetch_stock_data
from src.indicators import add_all_indicators
from src.analysis import plot_trend_chart, summarize_signals

df = fetch_stock_data("TCS.NS", period="5y")
enriched = add_all_indicators(df)

plot_trend_chart(enriched, "TCS")
summarize_signals(enriched, "TCS")
```

### Adding more stocks

Edit `DEFAULT_TICKERS` in `src/fetch_data.py`:

```python
DEFAULT_TICKERS = {
    "TCS": "TCS.NS",
    "INFOSYS": "INFY.NS",
    "RELIANCE": "RELIANCE.NS",   # add any yfinance-recognized symbol
}
```

## Requirements

- Python 3.9+
- `yfinance`, `pandas`, `matplotlib`, `numpy` (see `requirements.txt`)
- An internet connection (to fetch price data from Yahoo Finance)

## License

Released under the MIT License — see [LICENSE](LICENSE).
