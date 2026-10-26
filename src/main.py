import argparse

from src.fetcher import get_stock, get_stocks_from_watchlist


def main():
    parser = argparse.ArgumentParser(
        description="Pobierz dzienne notowania z Yahoo Finance i wyślij do Supabase."
    )
    parser.add_argument("symbol", nargs="?", help="Pobierz pojedynczy symbol zamiast całej listy")
    parser.add_argument("--period", default="1y", help="Zakres Yahoo Finance, np. 1mo, 6mo, 1y, 5y (domyślnie: 1y)")
    parser.add_argument("--save-to-csv", action="store_true", help="Zapisz dodatkowo lokalny plik CSV")
    args = parser.parse_args()
    if args.symbol:
        get_stock(args.symbol, period=args.period, save_to_csv=args.save_to_csv)
    else:
        get_stocks_from_watchlist(period=args.period, save_to_csv=args.save_to_csv)


if __name__ == "__main__":
    main()


