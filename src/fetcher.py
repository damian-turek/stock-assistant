import pandas as pd
import yfinance as yf

def get_stock():
    data = yf.Ticker('NVDA')
    info = data.info
    stock_data = {
        "x": [
            "Symbol",
            "Name",
            "Current price",
            "Open price",
            "Lowest today",
            "Currency",
        ],
        "y": [
            info.get("symbol"),
            info.get("shortName"),
            info.get("currentPrice") or info.get("regularMarketPrice"),
            info.get("open"),
            info.get("dayLow"),
            info.get("currency"),
        ]
    }
    df = pd.DataFrame(stock_data)
    print(df)
    return df
