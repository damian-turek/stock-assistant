from datetime import datetime, timezone

from src.collectors.news import fetch_news
from src.collectors.storage import store_news_in_file


def main():
    stock = "NVDA"
    articles = fetch_news(stock)
    collected_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S%fZ")
    file_path = f"data/raw/news/{stock}_{collected_at}.json"
    store_news_in_file(articles, file_path)
    print(f"{stock}: saved {len(articles)} articles to {file_path}")


if __name__ == "__main__":
    main()
