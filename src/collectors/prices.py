import pandas as pd
import yfinance as yf


def fetch_price_history(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    ticker = yf.Ticker(symbol)
    data = ticker.history(
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=False,
        actions=True,
        raise_errors=True,
    )

    if data.empty:
        raise ValueError(
            f"No price history data found for {symbol} "
            f"from {start_date} to {end_date} (exclusive)"
        )

    return data
