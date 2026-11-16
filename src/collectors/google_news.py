import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


def fetch_google_news(stock: str, count: int = 10) -> list[dict]:

    if not stock or not stock.strip():
        raise ValueError("Stock query cannot be empty.")

    if count < 1:
        raise ValueError("Count must be greater than zero.")

    query = urllib.parse.quote_plus(stock)

    url = (
        "https://news.google.com/rss/search?"
        f"q={query}&hl=en-US&gl=US&ceid=US:en"
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            xml_data = response.read()

    except (urllib.error.URLError, TimeoutError) as error:
        raise RuntimeError(
            f"Could not retrieve Google News RSS: {error}"
        ) from error

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as error:
        raise RuntimeError(
            "Could not parse Google News RSS response."
        ) from error

    articles = []

    for item in root.findall("./channel/item")[:count]:
        source_element = item.find("source")

        articles.append({
            "title": item.findtext("title"),
            "publisher": (
                source_element.text if source_element is not None else None
            ),
            "link": item.findtext("link"),
            "published": item.findtext("pubDate"),
            "description": item.findtext("description"),
            "guid": item.findtext("guid"),
            "provider": "Google News",
            "relatedTickers": [stock.upper()]
        })

    return articles
