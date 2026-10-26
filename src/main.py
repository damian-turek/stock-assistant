from src.fetcher import get_stock 
import scrappers

def main():
    get_stock()
    scrappers.basicStockScrapper()

if __name__ == "__main__":
    main()
