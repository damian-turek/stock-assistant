import time

import yfinance as yf


def fetch_news(symbol: str) -> list[dict]:
    time.sleep(5)
    stock = yf.Ticker(symbol)
    data = stock.news
    return data
