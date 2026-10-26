#!/usr/bin/env python3
"""
Analiza ankiety Lab 01.
Uruchom: python analiza_lab02.py "odpowiedz z ankiet_.csv"
Wymagania: pandas, numpy, scipy, matplotlib.
Założenie do sprawdzenia: 15 kolumn odpowiedzi to trzy kolejne bloki po 5
ocen w kolejności: Jabłka, Pomarańcze, Banany.
"""
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

input_file = sys.argv[1] if len(sys.argv) > 1 else "odpowiedz z ankiet_.csv"
df = pd.read_csv(input_file, sep=";", encoding="cp1252")
answer_cols = list(df.columns[5:])
if len(answer_cols) != 15:
    raise ValueError(f"Oczekiwano 15 ocen na respondenta, znaleziono {len(answer_cols)}.")
mapping = {"Nigdy": 1, "Sporadycznie": 2, "Czasami": 3,
           "Cz?sto": 4, "Bardzo cz?sto": 5}
text = df[answer_cols].astype(str).apply(lambda col: col.str.strip())
numeric = text.replace(mapping).apply(pd.to_numeric, errors="coerce")
if numeric.isna().any().any():
    raise ValueError("Wykryto brakujące lub nierozpoznane odpowiedzi; sprawdź kodowanie CSV.")
categories = {
    "Jabłka": numeric.iloc[:, 0:5].to_numpy().ravel(),
    "Pomarańcze": numeric.iloc[:, 5:10].to_numpy().ravel(),
    "Banany": numeric.iloc[:, 10:15].to_numpy().ravel()
}
print(f"Liczba respondentów: {len(df)}; ocen łącznie: {numeric.size}")
for name, values in categories.items():
    w, p = stats.shapiro(values)
    print(f"{name}: n={len(values)}, Shapiro-Wilk W={w:.4f}, p={p:.6g}")
    print("  Częstości ocen:", pd.Series(values).value_counts().sort_index().to_dict())
h, p = stats.kruskal(*categories.values())
print(f"Kruskal-Wallis: H={h:.4f}, p={p:.6g}")
# Zachowujemy każdą obserwację; nie uśredniamy odpowiedzi.
long = []
for respondent in range(len(df)):
    for j, col in enumerate(answer_cols):
        long.append({"Respondent_ID": respondent+1, "Pytanie_nr": j+1,
                     "Kategoria": ["Jabłka","Pomarańcze","Banany"][j//5],
                     "Odpowiedz_tekst": text.iloc[respondent,j],
                     "Ocena_liczbowa": int(numeric.iloc[respondent,j])})
pd.DataFrame(long).to_csv("dane_uporzadkowane.csv", index=False, encoding="utf-8-sig")
plt.figure(figsize=(8,5))
for x, (name, values) in enumerate(categories.items(), 1):
    plt.scatter(np.random.default_rng(42+x).normal(x, .055, len(values)), values, alpha=.55)
plt.boxplot(list(categories.values()), tick_labels=list(categories.keys()))
plt.ylabel("Ocena (1 = Nigdy, 5 = Bardzo często)")
plt.yticks([1,2,3,4,5]); plt.title("Rozkład wszystkich ocen w trzech kategoriach")
plt.tight_layout(); plt.savefig("wizualizacja_danych.png", dpi=180)
