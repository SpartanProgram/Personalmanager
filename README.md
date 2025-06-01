# KI-gestützte Verteilung wissenschaftlichen Personals

Dieses Projekt implementiert ein KI-basiertes System zur automatisierten Verteilung von wissenschaftlichem Personal auf Forschungsprojekte. Die Verteilung erfolgt auf Basis von Kompetenzen, Verfügbarkeit und optional weiteren Kriterien.

## Funktionen
- Extraktion relevanter Features aus Mitarbeiter- und Projektdaten
- Scoring-Modul zur Bewertung von Zuordnungen
- Prüfung der zeitlichen Verfügbarkeit
- Kombinierte Bewertung und Optimierung
- Der Code wird in Jupyter Notebooks ausgeführt

## Tech Stack
- **Python 3.11**, PyTorch, scikit-learn, Pandas, NumPy
- **Anaconda3**, **Visual Studio Code**, Jupyter Notebook
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
├── environment.yml        # Conda-Umgebung mit kompatiblen Python-Abhängigkeiten
└── requirements.txt       # Liste der Python-Abhängigkeiten
```
## Projekinstallation

```bash
# Clonen des Projektes per SSH
git clone git@gitlab.rz.htw-berlin.de:softwareentwicklungsprojekt/sose2025/team-10-personalmanager-gfai-bvvi.git
```
```bash
# Per Terminal oder VS-Code mit Git verbinden
git config --global user.email "-->HTW-Mail-Adresse<--"
git config --global user.name "-->Name<--"
```

# 🐍 Anaconda Installation
## Debian-Linux Installation
```bash
   sudo apt update && sudo apt upgrade -y

   # Anaconda-Installer herunterladen:
   wget https://repo.anaconda.com/archive/Anaconda3-2024.10-1-Linux-x86_64.sh

   # Installation starten:
   bash Anaconda3-2024.10-1-Linux-x86_64.sh

   # Anweisungen folgen (Lizenz akzeptieren, Pfad bestätigen, conda init aktivieren)

   # Shell neu laden:
   source ~/.bashrc

   # Testen:
   conda info
   
   # Nach der Installation Python3.11 Umgebungen erstellen:
   conda env create -f environment.yml
   conda activate .personalverteilung
```

## Windowns Installation
Offiziellen Installer herunterladen von:
   https://www.anaconda.com/products/distribution

Doppelklick auf die .exe-Datei und Setup durchlaufen
- Für "Just Me" oder "All Users"
- Option „Anaconda in PATH aufnehmen“ optional (empfohlen: Anaconda Prompt verwenden)
```bash
   # Nach der Installation:
   # - „Anaconda Prompt“ oder „Anaconda Navigator“ starten
   # - Test mit: 
   conda info

   # Nach der Installation Python3.11 Umgebungen erstellen:
   conda env create -f environment.yml
   conda activate .cenv
```

# Python-Version

Dieses Projekt verwendet Python 3.11. Falls du nicht mit Conda arbeitest und eine 
andere Python-Version installiert hast, empfiehlt es sich, pyenv zu verwenden:

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

## Ausführungsreihenfolge

Die Analyse besteht aus drei Jupyter-Notebooks, die in folgender Reihenfolge ausgeführt werden sollten:

1. **`/data/data.ipynb`**
   - Erstellt:
     - `personen.csv` – Personen mit Kompetenzen und Zeitbudget
     - `teilaufgaben.csv` – Teilaufgaben mit Aufwand und benötigter Kompetenz

2. **`/tests/scoreMatching.ipynb`**
   - Liest:
     - `/data/personen.csv`
     - `/data/teilaufgaben.csv`
   - Führt das Matching durch und speichert:
     - `/tests/matching_ergebnis.csv`

3. **`/visualizations/figures.ipynb`**
   - Liest:
     - `/tests/matching_ergebnis.csv`
   - Erstellt eine Visualisierung:
     - Balkendiagramm der zugewiesenen Aufwände je Teilaufgabe

## Lizenz

Apache License 2.0 – siehe [LICENSE](https://gitlab.rz.htw-berlin.de/softwareentwicklungsprojekt/sose2025/team-10-personalmanager-gfai-bvvi/-/blob/master/LICENSE.txt?ref_type=heads).