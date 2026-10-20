# stock-assistant

Pobieranie dziennych notowań akcji z Alpha Vantage do plików CSV w folderze
`dataFiles`.

Ustaw klucz API w `.env` jako `ALPHA_VANTAGE_API_KEY=twoj-klucz`.

Zainstaluj zależności przed pierwszym uruchomieniem:

```powershell
python -m pip install -r requirements.txt
```

Domyślnie scraper czyta listę spółek z `dataFiles/companies.csv`. Plik ma
średnik jako separator oraz kolumny `nazwa;symbol`; dopisz tam dowolne firmy,
np. `Apple;AAPL`. Dla każdego symbolu powstanie osobny plik, np.
`dataFiles/NVDA_daily.csv` (najnowsze 100 sesji).

Uruchom całą listę z katalogu projektu:

```powershell
python -m src.main
```

Możesz też pobrać pojedynczą spółkę, podając symbol:

```powershell
python -m src.main NVDA
```
