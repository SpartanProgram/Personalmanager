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

## Projektstruktur

```text
team-10-personalmanager-gfai-bvvi/
├── README.md              # Projektbeschreibung
├── LICENSE.txt            # Lizenzinformation
├── data/                  # Datensätze, Input- & Output-Dateien
├── src/                   # Quellcode des Projekts
├── tests/                 # Testfälle
├── docs/                  # Projektbezogene Dokumentation
├── visualizations/        # Grafiken zur Darstellung der Projektzuordnungen
└── requirements.txt       # Liste der Python-Abhängigkeiten
```

```bash
# VS-Code mit Git verbinden
git config --global user.email "-->HTW-Mail-Adresse<--"
git config --global user.name "-->Name<--"
```

# Python-Version

Dieses Projekt verwendet Python 3.11. Falls du eine andere Python-Version 
installiert hast, empfiehlt es sich, pyenv zu verwenden:

pyenv installieren (falls noch nicht vorhanden)
Anleitung: https://github.com/pyenv/pyenv#installation
```bash
# gewünschte Version installieren
pyenv install 3.11.9

# lokal für dieses Projekt festlegen
pyenv local 3.11.9
```

```bash
# Virtuelle Umgebung erstellen
python3.11 -m venv .venv
source .venv/bin/activate  # oder .\.venv\Scripts\activate auf Windows

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Lizenz

Apache License 2.0 – siehe [LICENSE](https://gitlab.rz.htw-berlin.de/softwareentwicklungsprojekt/sose2025/team-10-personalmanager-gfai-bvvi/-/blob/master/LICENSE.txt?ref_type=heads).