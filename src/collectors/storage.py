import json
from pathlib import Path

import pandas as pd


def store_data_in_file(data: pd.DataFrame, file_path: str) -> None:
    if data.empty:
        raise ValueError("The provided DataFrame is empty and cannot be stored.")

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=True, index_label="Date")


def load_price_history(file_path: str) -> pd.DataFrame:
    data = pd.read_csv(file_path, index_col="Date")
    if data.empty:
        raise ValueError(f"The file at {file_path} contains no price history rows.")

    data.index = pd.to_datetime(data.index, utc=True)
    return data


def store_news_in_file(data: list[dict], file_path: str) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
