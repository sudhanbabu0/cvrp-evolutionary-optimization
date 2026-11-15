# Capacitated Vehicle Routing Problem (CVRP) — Evolutionary Optimization Suite

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Academic Assessment](https://img.shields.io/badge/PBL-Task%202%20(30%20Marks)-emerald.svg)]()

An end-to-end Evolutionary Computing framework solving the **Capacitated Vehicle Routing Problem (CVRP)** using Christian Prins' permutation giant-tour representation, Order Crossover (OX1), hybrid 2-opt inversion mutation, and adaptive diversity injection.

Features an **interactive web dashboard** with real-time route simulation, parameter tuning, and dual-axis convergence charts.

---

## 🚀 Key Results & Benchmark Comparison

Benchmark on $N = 35$ customer nodes, central depot at $(50, 50)$, fleet capacity $Q = 100$, and fleet limit $K = 8$:

| Metric | Deterministic Greedy NN | Genetic Algorithm (Ours) | Net Gain / Savings |
| :--- | :---: | :---: | :---: |
| **Total Route Travel Distance** | $1036.59\text{ km}$ | **$727.17\text{ km}$** | **$-309.42\text{ km}$ ($-29.85\%$)** |
| **Delivery Vans Utilized** | 7 Vans | **6 Vans (Theoretical Min)** | **$-1$ Van ($-14.3\%$)** |
| **Constraint Violations** | 0 | 0 | Strictly Feasible |
| **Computation Time** | $0.42\text{ ms}$ | $0.796\text{ s}$ | Real-time Dispatch Ready |
| **Fitness Score $F(S)$** | $0.00096377$ | **$0.00137330$** | **$+42.5\%$ Fitness** |

---

## 📁 Repository Structure

```
cvrp_evolutionary_project/
├── app.py                     # Web Dashboard server (Flask + REST API)
├── main.py                    # Master CLI (demo, sensitivity suite, plots)
├── requirements.txt           # Python dependencies (numpy, matplotlib, flask, gunicorn)
├── Procfile                   # Cloud deployment command (for Render / Railway)
├── .gitignore                 # Standard python ignores
├── src/                       # Core evolutionary computing engine
│   ├── dataset.py             # 35-customer CVRP instance & Euclidean distance matrix
│   ├── decoder.py             # Christian Prins' greedy capacity-splitting decoder
│   ├── operators.py           # Hybrid seeding, OX1 crossover, 50/50 swap/inversion
│   ├── ga_engine.py           # Generational loop, elitism, diversity injection
│   ├── baseline_nn.py         # Deterministic greedy nearest-neighbor solver
│   ├── experiments.py         # 70-run OFAT sensitivity suite across 5 parameters
│   └── visualize.py           # Publication-grade 300 DPI chart generation
├── templates/
│   └── index.html             # Interactive HTML5 Canvas + Tailwind + Chart.js dashboard
├── outputs/
│   ├── tables/                # CSV & Markdown sensitivity tables
│   ├── plots/                 # 300 DPI charts (convergence, routes, parameters)
│   └── best_routes.json       # Serialized optimal route coordinates & metrics
└── docs/
    ├── PROJECT_REPORT.md      # Comprehensive academic report (all 15 PBL questions)
    ├── LITERATURE_SURVEY.md   # Peer-reviewed references on GA-CVRP
    └── PRESENTATION_OUTLINE.md# 10-15 minute slide deck & demo script
```

---

## 💻 Local Installation & Usage

### 1. Clone the repository & install dependencies:
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
pip install -r requirements.txt
```

### 2. Launch the Interactive Web Dashboard:
```bash
python app.py
```
Open **`http://localhost:5000`** in any web browser.

### 3. Run the Terminal Live Demo:
```bash
python main.py --demo
```

### 4. Execute the Full 70-Run Sensitivity Suite:
```bash
python main.py --experiments
```

---

## 🌐 Deploying to the Web from GitHub (Free)

Because this application uses a Python backend (Flask + NumPy) to dynamically optimize routes in real time, it requires a Python web host rather than static GitHub Pages. The fastest free hosting options with 1-click GitHub integration are:

### Option A: Render.com (Recommended - 100% Free)
1. Push this repository to GitHub.
2. Sign in to [Render.com](https://render.com) with your GitHub account.
3. Click **New +** &rarr; **Web Service**.
4. Select your GitHub repository.
5. Configure the service:
   * **Name**: `cvrp-optimizer` (or your choice)
   * **Environment**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn app:app`
6. Click **Create Web Service**. Within 2 minutes, Render will provide a live public URL (e.g., `https://cvrp-optimizer.onrender.com`).

### Option B: Railway.app
1. Go to [Railway.app](https://railway.app) and link your GitHub account.
2. Click **New Project** &rarr; **Deploy from GitHub repo**.
3. Select this repository. Railway automatically detects the `Procfile` and `requirements.txt` and deploys your site.

### Option C: PythonAnywhere
1. Create a free account at [PythonAnywhere.com](https://www.pythonanywhere.com).
2. Open a Bash console and clone your GitHub repository:
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   ```
3. Go to the **Web** tab, create a new Flask web app pointing to `app.py`.

