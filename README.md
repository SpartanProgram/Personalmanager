# KI-gestützte Verteilung wissenschaftlichen Personals

Dieses Projekt implementiert ein KI-basiertes Zuordnungssystem zur automatisierten Verteilung von wissenschaftlichem Personal auf Forschungsprojekte. Die Zuordnung erfolgt auf Basis von Kompetenzen, Verfügbarkeit und optional weiteren Kriterien.

## Funktionen
- Extraktion relevanter Features aus Mitarbeiter- und Projektdaten
- Scoring-Modul zur Bewertung von Zuordnungen
- Prüfung der zeitlichen Verfügbarkeit
- Kombinierte Bewertung und Optimierung


## Tech Stack
- **Python 3.11**, PyTorch, scikit-learn, Pandas, NumPy
- **Visual Studio Code**, Jupyter Notebook
- **Matplotlib, Seaborn** zur Visualisierung
- **Faker** zur Generierung von Pseudo-Daten

## Struktur

ki_zuordnung/
├── preprocessing/
├── scoring/
├── optimization/
├── tests/
└── main.py


## Ausführen
```bash
python main.py
```

## Lizenz

Apache License 2.0 – siehe LICENSE-Datei.