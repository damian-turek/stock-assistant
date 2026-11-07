import json
from pathlib import Path

import pandas as pd

from src.collectors.storage import (
    load_price_history,
    store_data_in_file,
    store_news_in_file,
)


def test_price_history_round_trip(tmp_path: Path) -> None:
    prices = pd.DataFrame(
        {
            "Close": [125.5, 192.25],
            "Volume": [1000, 2000],
        },
        index=pd.DatetimeIndex(
            ["2023-01-03", "2023-07-03"],
            tz="America/New_York",
            name="Date",
        ),
    )
    file_path = tmp_path / "prices" / "AAPL.csv"

    store_data_in_file(prices, str(file_path))
    loaded_prices = load_price_history(str(file_path))

    expected = prices.copy()
    expected.index = expected.index.tz_convert("UTC")
    pd.testing.assert_frame_equal(loaded_prices, expected)


def test_news_history_round_trip(tmp_path: Path) -> None:
    news = [
        {
            "id": "sample-article",
            "content": {
                "title": "Caf\u00e9 company announces earnings",
                "symbols": ["NVDA", "AAPL"],
                "published_at": "2026-11-07T10:00:00Z",
            },
        }
    ]
    file_path = tmp_path / "news" / "NVDA.json"

    store_news_in_file(news, str(file_path))
    with file_path.open(encoding="utf-8") as file:
        loaded_news = json.load(file)

    assert loaded_news == news
    assert "Caf\u00e9" in file_path.read_text(encoding="utf-8")


def test_store_empty_news(tmp_path: Path) -> None:
    file_path = tmp_path / "news" / "empty.json"

    store_news_in_file([], str(file_path))
    with file_path.open(encoding="utf-8") as file:
        loaded_news = json.load(file)

    assert loaded_news == []
