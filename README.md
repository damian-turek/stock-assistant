# stock-assistant

Collect recent NVDA news from the repository root:

```bash
.venv/bin/python -m src.main
```

The current entry point saves the entire recent-news response to a JSON
file under `data/raw/news/`, named with the symbol and UTC collection
timestamp. Successful empty responses are saved as `[]`; provider errors
remain visible. This endpoint does not retrieve arbitrary historical date
ranges.

Historical-price fetching and CSV storage remain available in
`src/collectors/prices.py` and `src/collectors/storage.py`. The current
entry point does not redownload prices while developing news collection.

Tests

```bash
.venv/bin/python -m pytest -v
```