import yfinance as yf


def fetch_news(stock, count: int = 5) -> list[dict]:
    news = yf.Search(stock, news_count=count, max_results=1).news
    return news
