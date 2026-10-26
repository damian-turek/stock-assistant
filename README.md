# stock-assistant

Pobieranie dziennych notowań z Yahoo Finance i zapis do tabeli
`public.stock_prices` w Supabase. Lokalny CSV jest opcjonalny i domyślnie
wyłączony.

W `src/.env` (lub głównym `.env`) ustaw:

```dotenv
SUPABASE_URL=https://twoj-projekt.supabase.co
SUPABASE_KEY=sb_secret_...
```

Użyj serwerowego klucza `sb_secret_...` z Supabase Dashboard → Settings → API Keys. Klucz `sb_publishable_...` nie zapisze danych przy włączonym RLS. Nie umieszczaj pliku `.env` w repozytorium ani nie udostępniaj klucza. Schemat tabeli znajdziesz w
[`supabase_schema.sql`](supabase_schema.sql); wykonaj go w SQL Editor projektu
Supabase przed pierwszym uruchomieniem.

Wymagania:

```powershell
python -m pip install -r requirements.txt
```

Lista spółek jest w `dataFiles/companies.csv`: średnik jako separator oraz
kolumny `nazwa;symbol`. Domyślnie pobierany jest ostatni rok danych.

Uruchom wszystkie symbole:

```powershell
python -m src.main
```

Pojedynczy symbol i zakres danych:

```powershell
python -m src.main NVDA --period 5y
```

Aby dodatkowo zapisać lokalny CSV, dodaj przełącznik `--save-to-csv`:

```powershell
python -m src.main NVDA --save-to-csv
```

Obsługiwane zakresy Yahoo Finance to m.in. `1mo`, `3mo`, `6mo`, `1y`, `2y`,
`5y`, `10y`, `ytd` i `max`. Dane są wysyłane przez Supabase REST API do tabeli
`stock_prices`; klucz główny `(symbol, date)` pozwala ponawiać import bez
duplikowania notowań.


