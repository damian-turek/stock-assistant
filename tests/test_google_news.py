import io
import json

from src.collectors.google_news import fetch_google_news
from src.collectors.storage import store_news_in_file


def test_fetch_google_news(monkeypatch):

    sample_xml = b"""
    <rss>
        <channel>
            <item>
                <title>NVIDIA announces new technology</title>
                <link>https://example.com/news</link>
                <pubDate>Sun, 15 Nov 2026 10:00:00 GMT</pubDate>
                <description>Sample news description</description>
                <guid>article-123</guid>
                <source>Example News</source>
            </item>
        </channel>
    </rss>
    """

    def mock_urlopen(request, timeout):
        return io.BytesIO(sample_xml)

    monkeypatch.setattr(
        "src.collectors.google_news.urllib.request.urlopen",
        mock_urlopen
    )

    news = fetch_google_news("NVIDIA", count=10)

    assert len(news) == 1
    assert news[0]["title"] == "NVIDIA announces new technology"
    assert news[0]["publisher"] == "Example News"
    assert news[0]["guid"] == "article-123"
    assert news[0]["provider"] == "Google News"


def test_store_google_news(tmp_path):

    news = [
        {
            "title": "NVIDIA announces new technology",
            "publisher": "Example News",
            "link": "https://example.com/news",
            "published": "Sun, 15 Nov 2026 10:00:00 GMT",
            "description": "Sample description",
            "guid": "article-123",
            "provider": "Google News",
            "relatedTickers": ["NVIDIA"]
        }
    ]

    file_path = tmp_path / "google_news.json"

    store_news_in_file(news, str(file_path))

    with file_path.open(encoding="utf-8") as file:
        loaded_news = json.load(file)

    assert loaded_news == news
    assert loaded_news[0]["provider"] == "Google News"
