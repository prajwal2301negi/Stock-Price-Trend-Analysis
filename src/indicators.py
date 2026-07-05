"""
indicators.py
-------------
Technical indicator calculations: Simple Moving Averages (SMA) and the
Relative Strength Index (RSI), plus bullish/bearish crossover detection.
"""

import pandas as pd


def add_sma(df: pd.DataFrame, windows=(20, 50), price_col: str = "Close") -> pd.DataFrame:
    """
    Add one Simple Moving Average column per window to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Price data containing `price_col`.
    windows : iterable of int
        Window lengths in trading days, e.g. (20, 50).
    price_col : str
        Column to average (default "Close").

    Returns
    -------
    pd.DataFrame
        Copy of `df` with new columns "SMA_<window>".
    """
    out = df.copy()
    for w in windows:
        out[f"SMA_{w}"] = out[price_col].rolling(window=w, min_periods=w).mean()
    return out


def add_rsi(df: pd.DataFrame, period: int = 14, price_col: str = "Close") -> pd.DataFrame:
    """
    Add the Relative Strength Index (RSI) using Wilder's smoothing method.

    RSI = 100 - (100 / (1 + RS)), where RS = average gain / average loss
    over the lookback `period`, smoothed with an exponential moving
    average that approximates Wilder's original technique.

    Parameters
    ----------
    df : pd.DataFrame
        Price data containing `price_col`.
    period : int
        RSI lookback period (default 14, the standard setting).
    price_col : str
        Column used for the calculation (default "Close").

    Returns
    -------
    pd.DataFrame
        Copy of `df` with a new "RSI_<period>" column.
    """
    out = df.copy()
    delta = out[price_col].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's smoothing = an EMA with alpha = 1/period
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Where avg_loss is 0, RSI should be 100 (no losses -> maximum strength)
    rsi = rsi.where(avg_loss != 0, 100)

    out[f"RSI_{period}"] = rsi
    return out


def detect_sma_crossovers(df: pd.DataFrame, fast_col: str = "SMA_20", slow_col: str = "SMA_50") -> pd.DataFrame:
    """
    Detect Golden Cross (bullish) and Death Cross (bearish) signals based
    on the crossover of a fast SMA over/under a slow SMA.

    - Golden Cross: fast SMA crosses ABOVE slow SMA  -> bullish signal
    - Death Cross:  fast SMA crosses BELOW slow SMA  -> bearish signal

    Returns
    -------
    pd.DataFrame
        Copy of `df` with a "Signal" column containing one of:
        "Golden Cross", "Death Cross", or "" (no crossover on that day).
    """
    out = df.copy()
    diff = out[fast_col] - out[slow_col]
    prev_diff = diff.shift(1)

    golden_cross = (prev_diff < 0) & (diff > 0)
    death_cross = (prev_diff > 0) & (diff < 0)

    out["Signal"] = ""
    out.loc[golden_cross, "Signal"] = "Golden Cross"
    out.loc[death_cross, "Signal"] = "Death Cross"
    return out


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience wrapper: adds SMA-20, SMA-50, RSI-14, and crossover signals."""
    out = add_sma(df, windows=(20, 50))
    out = add_rsi(out, period=14)
    out = detect_sma_crossovers(out, fast_col="SMA_20", slow_col="SMA_50")
    return out
