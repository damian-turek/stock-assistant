from collectors.news import fetch_news
from collectors.google_news import fetch_google_news
from collectors.prices import fetch_price_history
from collectors.storage import store_data_in_file, store_news_in_file


def main():
    stocks = [
        "NVDA",
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "META",
        "TSLA",
        "BRK-B",
        "JPM",
    ]

    for stock in stocks:
        prices = fetch_price_history(stock, "2023-01-01", "2024-01-01")
        store_data_in_file(prices, f"data/raw/prices/{stock}.csv")
        news = fetch_news(stock, 10)
        store_news_in_file(news, f"data/raw/news/{stock}.json")

        google_news = fetch_google_news(stock, count=10)
        store_news_in_file(google_news, f"data/raw/news/google_{stock}.json")


if __name__ == "__main__":
    main()
