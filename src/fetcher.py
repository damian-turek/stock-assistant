import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests


YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
DATA_DIR = Path(__file__).resolve().parent.parent / "dataFiles"
WATCHLIST_FILE = DATA_DIR / "companies.csv"
ENV_FILES = (
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent / ".env",
)
CSV_COLUMNS = ("symbol", "date", "open", "high", "low", "close", "volume", "dividends", "stock_splits")


def _load_env_value(name: str) -> str | None:
    value = os.environ.get(name)
    if value:
        return value.strip().strip("\"'")
    for env_file in ENV_FILES:
        if not env_file.is_file():
            continue
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            key, separator, candidate = line.partition("=")
            if separator and key.strip().removeprefix("export ").strip() == name:
                candidate = candidate.strip()
                if len(candidate) >= 2 and candidate[0] == candidate[-1] and candidate[0] in "\"'":
                    candidate = candidate[1:-1]
                return candidate or None
    return None


def _get_supabase_config() -> tuple[str, str]:
    url = _load_env_value("SUPABASE_URL")
    key = _load_env_value("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Brak SUPABASE_URL lub SUPABASE_KEY w zmiennych środowiskowych albo pliku .env.")
    return url.rstrip("/"), key


def get_stock(symbol: str = "NVDA", period: str = "1y", save_to_csv: bool = False) -> Path | None:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol spółki nie może być pusty.")
    try:
        response = requests.get(
            YAHOO_CHART_URL.format(symbol=symbol),
            params={"range": period, "interval": "1d", "events": "div,splits"},
            headers={"User-Agent": "Mozilla/5.0 stock-assistant/1.0"},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Nie udało się pobrać danych Yahoo Finance dla {symbol} ({type(exc).__name__}).") from exc

    chart = payload.get("chart", {})
    if chart.get("error"):
        error = chart["error"]
        raise RuntimeError(f"Yahoo Finance: {error.get('description') or error.get('code') or 'błąd API'}")
    results = chart.get("result") or []
    if not results:
        raise RuntimeError(f"Yahoo Finance nie zwróciło notowań dla {symbol}.")
    result = results[0]
    timestamps = result.get("timestamp") or []
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    exchange_tz = result.get("meta", {}).get("exchangeTimezoneName", "UTC")
    try:
        market_timezone = ZoneInfo(exchange_tz)
    except ZoneInfoNotFoundError:
        market_timezone = timezone.utc
    events = result.get("events") or {}
    dividends = events.get("dividends") or {}
    splits = events.get("splits") or {}
    rows: list[dict[str, Any]] = []
    for index, timestamp in enumerate(timestamps):
        day = datetime.fromtimestamp(timestamp, tz=market_timezone).date().isoformat()
        dividend = (dividends.get(str(timestamp)) or {}).get("amount", 0)
        split = splits.get(str(timestamp)) or {}
        split_value = float(split.get("numerator", 0)) / float(split.get("denominator", 1)) if split else 0
        rows.append({
            "symbol": symbol,
            "date": day,
            "open": _at(quote.get("open"), index),
            "high": _at(quote.get("high"), index),
            "low": _at(quote.get("low"), index),
            "close": _at(quote.get("close"), index),
            "volume": _at(quote.get("volume"), index),
            "dividends": dividend,
            "stock_splits": split_value,
        })
    if not rows:
        raise RuntimeError(f"Yahoo Finance nie zwróciło dziennych notowań dla {symbol}.")

    output_path = None
    if save_to_csv:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DATA_DIR / f"{symbol}_daily.csv"
        with output_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

    _upload_to_supabase(rows)
    destination = f"{len(rows)} notowań do Supabase stock_prices"
    if output_path:
        destination += f" oraz {output_path}"
    print(f"Zapisano {destination}.")
    return output_path


def _at(values: list[Any] | None, index: int) -> Any:
    if not values or index >= len(values):
        return None
    return values[index]


def _upload_to_supabase(rows: list[dict[str, Any]]) -> None:
    url, key = _get_supabase_config()
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    try:
        response = requests.post(
            f"{url}/rest/v1/stock_prices",
            params={"on_conflict": "symbol,date"},
            headers=headers,
            json=rows,
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        error_response = getattr(exc, "response", None)
        status = getattr(error_response, "status_code", "nieznany")
        detail = ""
        if error_response is not None:
            try:
                body = error_response.json()
                if isinstance(body, dict):
                    detail = "; ".join(
                        f"{name}: {body[name]}"
                        for name in ("code", "message", "details", "hint")
                        if body.get(name)
                    )
            except (ValueError, json.JSONDecodeError):
                detail = error_response.text
        detail = " ".join(str(detail).split())[:800]
        if error_response is not None and "42501" in detail and "row-level security" in detail.lower():
            raise RuntimeError(
                "Supabase odrzucił zapis przez RLS (kod 42501). Ustaw w src/.env "
                "klucz serwerowy sb_secret_... z Supabase Dashboard → Settings → API Keys; "
                "klucz sb_publishable_... nie ma uprawnień do zapisu przy obecnej polityce RLS."
            ) from exc
        suffix = f" — {detail}" if detail else ""
        raise RuntimeError(f"Błąd zapisu do Supabase (HTTP {status}){suffix}") from exc


def get_stocks_from_watchlist(period: str = "1y", save_to_csv: bool = False) -> list[Path]:
    if not WATCHLIST_FILE.is_file():
        raise FileNotFoundError(f"Nie znaleziono listy spółek: {WATCHLIST_FILE}")
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
            output_path = get_stock(symbol, period=period, save_to_csv=save_to_csv)
            if output_path is not None:
                saved_files.append(output_path)
        except (RuntimeError, ValueError) as exc:
            failed_symbols.append(symbol.upper())
            print(f"Nie udało się pobrać lub zapisać {symbol.upper()}: {exc}")
    if failed_symbols:
        print(f"Nieobsłużone symbole: {', '.join(failed_symbols)}")
    return saved_files






