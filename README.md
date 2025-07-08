# 🤖 AI-Based Research Staff Assignment (Team 10 – HTW Berlin)

This project implements an **AI-powered system** to automatically assign academic staff to research tasks based on skills, availability, and optional constraints.

Developed as part of the **Software Development Project (SoSe 2025)** at **HTW Berlin**, in collaboration with **GFaI** and **BVVI**.

---

## 🧠 Key Features

- 🧠 Skill extraction from staff and task datasets
- 📊 Scoring module for optimized task-person assignments
- 📆 Availability checks for individuals
- 🧮 Combined evaluation and optimization logic
- 📓 Executed in modular **Jupyter Notebooks**

---

## 🛠️ Tech Stack

- **Languages**: Python 3.11
- **Libraries**: PyTorch, scikit-learn, pandas, NumPy
- **Visualization**: matplotlib, seaborn
- **Tools**: Anaconda, Jupyter Notebook, VS Code
- **Utilities**: Faker (for pseudodata generation)

---

## 🗂️ Project Structure

team-10-personalmanager-gfai-bvvi/
├── README.md # Project overview
├── LICENSE.txt # License file (Apache 2.0)
├── data/ # Generated datasets (persons, tasks)
├── src/ # Source code modules
├── tests/ # Matching logic & test notebooks
├── docs/ # Project documentation
├── visualizations/ # Charts & assignment plots
├── environment.yml # Conda environment
└── requirements.txt # Python dependencies

Setup with Conda (Recommended)

wget https://repo.anaconda.com/archive/Anaconda3-2024.10-1-Linux-x86_64.sh
bash Anaconda3-2024.10-1-Linux-x86_64.sh
source ~/.bashrc

# Setup environment
conda env create -f environment.yml
conda activate .personalverteilung

Windows
Download installer from:
👉 https://www.anaconda.com/products/distribution

After installation:

# In Anaconda Prompt
conda info
conda env create -f environment.yml
conda activate .cenv

🐍 Manual Setup (Without Conda)

# Using pyenv (if needed)
pyenv install 3.11.9
pyenv local 3.11.9

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

📋 Execution Order
data/data.ipynb

Generates:

personen.csv – List of people with skills & availability

teilaufgaben.csv – Tasks with workload & required skills

tests/scoreMatching.ipynb

Reads:

personen.csv, teilaufgaben.csv

Outputs:

matching_ergebnis.csv – Matched task assignments

visualizations/figures.ipynb

Visualizes:

Task distributions via bar charts

👥 Team Members
Zul Fahmi Nur Vagala – Data processing, visualization, matching with genetic algorithm

Sandin Taci – Scoring logic, data modeling, matching algorithm, visualization

Mohand Alansari – Project structure, pseudodata generation, documentation

📄 License
This project is licensed under the Apache 2.0 License.
