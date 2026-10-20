import argparse

from src.fetcher import get_stock, get_stocks_from_watchlist

def main():
    parser = argparse.ArgumentParser(description="Pobierz dzienne notowania z Alpha Vantage.")
    parser.add_argument("symbol", nargs="?", help="Pobierz pojedynczy symbol zamiast całej listy")
    args = parser.parse_args()
    if args.symbol:
        get_stock(args.symbol)
    else:
        get_stocks_from_watchlist()

if __name__ == "__main__":
    main()
