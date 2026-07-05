"""
fetch_data.py
-------------
Downloads historical OHLCV price data for a given list of stock tickers
using the yfinance API and stores each as a CSV file in the data/ folder.

Usage (standalone):
    python fetch_data.py
"""

import os
import pandas as pd
import yfinance as yf

# NSE-listed tickers for Tata Consultancy Services and Infosys.
# yfinance requires the ".NS" suffix for NSE (National Stock Exchange, India) symbols.
DEFAULT_TICKERS = {
    "TCS": "TCS.NS",
    "INFOSYS": "INFY.NS",
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def fetch_stock_data(ticker: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a single ticker.

    Parameters
    ----------
    ticker : str
        Yahoo Finance ticker symbol (e.g. "TCS.NS").
    period : str
        Lookback period accepted by yfinance (default "5y" -> 5 years).
    interval : str
        Bar interval (default "1d" -> daily candles).

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by Date with Open/High/Low/Close/Volume columns.
    """
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)

    if df.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'. Check the symbol or your connection.")

    # yfinance sometimes returns a MultiIndex on columns when downloading
    # a single ticker with certain versions; flatten it if present.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index.name = "Date"
    return df


def fetch_all(tickers: dict = None, period: str = "5y", save: bool = True) -> dict:
    """
    Fetch data for every ticker in `tickers` and optionally save each to CSV.

    Parameters
    ----------
    tickers : dict
        Mapping of {display_name: yfinance_symbol}. Defaults to TCS & Infosys.
    period : str
        Lookback period, e.g. "5y".
    save : bool
        If True, writes a CSV per stock into the data/ directory.

    Returns
    -------
    dict
        Mapping of {display_name: DataFrame}.
    """
    tickers = tickers or DEFAULT_TICKERS
    os.makedirs(DATA_DIR, exist_ok=True)

    results = {}
    for name, symbol in tickers.items():
        print(f"Fetching {period} of daily data for {name} ({symbol}) ...")
        df = fetch_stock_data(symbol, period=period)
        print(f"  -> {len(df)} trading-day records retrieved for {name}.")

        if save:
            out_path = os.path.join(DATA_DIR, f"{name}.csv")
            df.to_csv(out_path)
            print(f"  -> saved to {out_path}")

        results[name] = df

    return results


if __name__ == "__main__":
    fetch_all()
