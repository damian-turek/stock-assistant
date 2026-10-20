
import csv
import os
from pathlib import Path

import requests


API_URL = "https://www.alphavantage.co/query"
DATA_DIR = Path(__file__).resolve().parent.parent / "dataFiles"
WATCHLIST_FILE = DATA_DIR / "companies.csv"
ENV_FILES = (
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent / ".env",
)


def _load_api_key() -> str | None:
    key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if key:
        return key
    for env_file in ENV_FILES:
        if not env_file.is_file():
            continue
        for line in env_file.read_text(encoding="utf-8").splitlines():
            name, separator, value = line.partition("=")
            if name.strip().removeprefix("export ").strip() == "ALPHA_VANTAGE_API_KEY" and separator:
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                return value or None
    return None


def get_stock(symbol: str = "NVDA", api_key: str | None = None) -> Path:
    key = api_key or _load_api_key()
    if not key:
        raise ValueError(
            "Brak klucza API. Ustaw zmienną ALPHA_VANTAGE_API_KEY."
        )

    try:
        response = requests.get(
            API_URL,
            params={
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol.upper(),
                "outputsize": "compact",
                "apikey": key,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Nie udało się pobrać danych Alpha Vantage ({type(exc).__name__})."
        ) from exc
    except ValueError as exc:
        raise RuntimeError("Alpha Vantage zwróciło nieprawidłową odpowiedź JSON.") from exc

    series = payload.get("Time Series (Daily)")
    if not series:
        message = (
            payload.get("Note")
            or payload.get("Information")
            or payload.get("Error Message")
            or "API nie zwróciło dziennych notowań."
        )
        raise RuntimeError(f"Alpha Vantage: {message}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / f"{symbol.upper()}_daily.csv"
    columns = [
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        for date, values in sorted(series.items()):
            writer.writerow(
                {
                    "date": date,
                    "open": values.get("1. open", ""),
                    "high": values.get("2. high", ""),
                    "low": values.get("3. low", ""),
                    "close": values.get("4. close", ""),
                    "volume": values.get("5. volume", ""),
                }
            )

    print(f"Zapisano {len(series)} notowań do {output_path}")
    return output_path


def get_stocks_from_watchlist(api_key: str | None = None) -> list[Path]:
    if not WATCHLIST_FILE.is_file():
        raise FileNotFoundError(
            f"Nie znaleziono listy spółek: {WATCHLIST_FILE}"
        )

    with WATCHLIST_FILE.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        if not reader.fieldnames or not {"nazwa", "symbol"}.issubset(reader.fieldnames):
            raise ValueError("Plik companies.csv musi mieć nagłówki: nazwa;symbol")
        companies = [
            (row["nazwa"].strip(), row["symbol"].strip())
            for row in reader
            if row.get("symbol") and row["symbol"].strip()
        ]

    if not companies:
        raise ValueError("Plik companies.csv nie zawiera żadnych symboli.")

    saved_files = []
    failed_symbols = []
    for name, symbol in companies:
        print(f"Pobieranie: {name} ({symbol.upper()})")
        try:
            saved_files.append(get_stock(symbol, api_key=api_key))
        except (RuntimeError, ValueError) as exc:
            failed_symbols.append(symbol.upper())
            print(f"Nie udało się pobrać {symbol.upper()}: {exc}")
            if "rate limit" in str(exc).lower() or "call frequency" in str(exc).lower():
                print("API ograniczyło liczbę żądań; przerywam pobieranie listy.")
                break
    if failed_symbols:
        print(f"Niepobrane symbole: {', '.join(failed_symbols)}")
    return saved_files
