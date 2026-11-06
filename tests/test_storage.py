from pathlib import Path

import pandas as pd

from src.collectors.storage import load_price_history, store_data_in_file


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