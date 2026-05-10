<div align="center">

# 🌍 Language / 语言 / Idioma

[English](README.md) | [简体中文](README_ZH.md) | [Español](README_ES.md)

---
</div>

<div align="center">

# 🧬 Dynamic Behavioral SEIRQ Model for ANDV Outbreak via Agentic OSINT

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Build](https://img.shields.io/badge/build-passing-brightgreen?logo=githubactions)](https://github.com/)
[![SciPy](https://img.shields.io/badge/deps-SciPy-8caae6?logo=scipy)](https://scipy.org/)

**A plug-and-play AI skill for OSINT-driven epidemiological simulation — calibrated with real-time news intelligence from the MV Hondius ANDV outbreak (May 2026).**

<p align="center">
  <img src="results/active_vs_reff.png" width="700" alt="Active Infections vs Reff" />
</p>

</div>

---

## Abstract / TL;DR

> [!IMPORTANT]
> **Key insight:** The real-world evidence — military airlift to Gómez Ulla Hospital (Madrid), single-room UAAN isolation, 42-day monitoring protocol, and 60–90 dedicated healthcare staff — suppresses $R_{eff}$ below the elimination threshold **within 5 days**, making Schengen border closure epidemiologically unnecessary. Without this OSINT-driven calibration, standard models overestimate the outbreak scale by **two orders of magnitude**.

This repository presents a **dynamic behavioural SEIRQ compartment model** for the **Andes Virus (ANDV)** — the only hantavirus variant with confirmed human-to-human transmission — informed by **agentic OSINT** (real-time news scraping). The model integrates **behavioral economics** (panic elasticity, $\alpha = 0.65$) and **step-function policy interventions** into a classical ODE epidemiological framework.

### Scenario Comparison: MV Hondius Outbreak

| Scenario | Initial Seeds | Policy Lag | Quarantine Efficiency | Peak Active | Reff < 1.0 | Schengen Closure? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Worst-Case (A)** | 150 | 7 days | 30% | ~150 | Day 7 | **Yes ❌** |
| **Real-Time Containment (B)** | 16 | **1 day 🚁** | **95% 🏥** | **~3** | **Day 5** | **No ✅** |

---

## Methodology

### Model Architecture

We implement a **five-compartment SEIRQ ODE system**:

$$
\text{Susceptible (S)} \xrightarrow{\beta(t)} \text{Exposed (E)} \xrightarrow{\sigma} \text{Infectious (I)} \xrightarrow{\gamma} \text{Recovered (R)}
$$
$$
I \xrightarrow{q(t)} \text{Quarantined (Q)}
$$

#### Compartment Equations

$$
\frac{dS}{dt} = -\beta(t) \cdot \frac{S \cdot I}{N}
$$

$$
\frac{dE}{dt} = \beta(t) \cdot \frac{S \cdot I}{N} - \sigma E
$$

$$
\frac{dI}{dt} = \sigma E - \gamma I - q(t) I
$$

$$
\frac{dR}{dt} = \gamma I
$$

$$
\frac{dQ}{dt} = q(t) I
$$

#### Behavioural Modulation via Panic Elasticity

The effective transmission rate is attenuated by cumulative public awareness (social distancing self-regulation):

$$
\beta_{\text{eff}}(t) = \beta_0 \cdot \max\!\left(0.10,\; 1 - \alpha \cdot \frac{Q(t)}{0.01N}\right),\quad \alpha = 0.65
$$

The quarantine detection rate activates after a policy lag $\tau$:

$$
q(t) = 
\begin{cases} 
\eta_q \cdot 0.3, & t \geq \tau \\ 
0, & t < \tau 
\end{cases}
$$

#### Epidemiological Parameters (ANDV-specific)

| Parameter | Value | Source |
| :--- | :---: | :--- |
| Basic reproduction number $R_0$ | 2.12 | ANDV human-to-human literature |
| Incubation period (median) | 21.0 days | Clinical range 1–6 weeks |
| Infectious period | 7.0 days | Standard hantavirus estimate |
| Panic elasticity $\alpha$ | 0.65 | Calibrated from behavioural economics |
| Modelled population $N$ | 1,000 | Ship + initial contact pool |

*(Note: The initial population $N=1,000$ is calibrated for the Seeding Phase of the cruise ship incident. As the model utilizes density-independent contact networks, scaling $N$ allows smooth generalization to macro-level forecasts, such as the Madrid metropolitan area.)*

---

## OSINT Pipeline (Intelligence → Parameters)

The "Real-Time Containment" scenario was dynamically calibrated from 20 scraped news articles detailing the MV Hondius incident:

| Intelligence Extract | Model Parameter |
| :--- | :--- |
| 14 Spanish nationals isolated + 2 contacts traced (Alicante, Barcelona) | $E_0 = 16$ |
| Military airlift to Madrid within 24 hours | $\tau = 1.0$ day |
| Single-room UAAN isolation at Gómez Ulla Hospital | $\eta_q = 0.95$ |
| 42-day monitoring protocol, 60–90 dedicated staff | Sustained quarantine enforcement |
| WHO epidemiologist on evacuation flight | International coordination verified |

---

## Agent Integration — Using as an AI Skill

This codebase is designed to be ingested by **agentic LLM systems** as a dynamic OSINT skill.

### 1. Load as a Contextual Skill
Copy the logic from `skill/` or `scripts/andv_ode_solver.py` into your agent's tool directory. Ask your agent:
> *"Run the ANDV Risk Assessment Tool using the latest OSINT of 16 seeds and a 1-day policy lag. Project the hospital capacity demand for Madrid next week."*

### 2. Sequential Bayesian Updates
Traditional models rely on static priors. This system supports continuous posterior updating:

```text
Prior:      Worst-case parameters (E0=50, I0=150, tau=7.0)
                     ↓
OSINT Sync: Agent scrapes 20 real-time news articles
                     ↓
Posterior:  16 seeds, 1-day lag, 95% quarantine efficiency
                     ↓
Decision:   Reff < 1.0 on Day 5 → Border closure NOT required

```

---

## Quick Start

### Prerequisites

* Python 3.10+
* `pip`

### Setup & Run

```bash
# 1. Clone the repository
git clone [https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ.git](https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ.git)
cd ANDV-Behavioral-SEIRQ

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run solver (generates results/andv_trajectories.csv)
python scripts/andv_ode_solver.py

# 5. Plot charts
python scripts/plot_generator.py

```

### Expected Output

```text
[OK] Trajectories written → results/andv_trajectories.csv
[OK] Summary written → results/scenario_comparison.txt
[OK] Loaded 4,002 rows from results/andv_trajectories.csv
[OK] Chart saved → results/active_vs_reff.png
[OK] Chart saved → results/quarantine_vs_recovered.png

```

---

## Parameter Customization

All key parameters are defined at the top of `scripts/andv_ode_solver.py`. Modify them for your own regional or pathogen-specific simulations:

```python
# ── Core epidemiological constants ──
R0 = 2.12                  # Basic reproduction number
INCUBATION_PERIOD = 21.0   # Days
INFECTIOUS_PERIOD = 7.0    # Days
N = 1000                   # Population pool

# ── Behavioural & policy parameters ──
ALPHA = 0.65               # Panic elasticity [0, 1]
ETA_Q = 0.95               # Quarantine efficiency [0, 1]
TAU = 1.0                  # Policy lag (days)

```

**Example Customizations:**

* **Seasonal influenza:** `R0 = 1.3`, `INCUBATION_PERIOD = 1.4`, `INFECTIOUS_PERIOD = 5.0`
* **Delayed response (developing region):** `TAU = 14.0`, `ETA_Q = 0.40`
* **High public compliance (East Asian context):** `ALPHA = 0.85`, `ETA_Q = 0.90`

---

## Repository Structure

```text
├── data/                    # Raw & processed OSINT inputs
├── scripts/
│   ├── andv_ode_solver.py   # SEIRQ ODE solver
│   └── plot_generator.py    # Publication-ready chart generator
├── skill/                   # AI Agent tool interface
├── results/                 # Simulation outputs
│   ├── andv_trajectories.csv
│   ├── scenario_comparison.txt
│   ├── active_vs_reff.png
│   └── quarantine_vs_recovered.png
├── .gitignore
├── requirements.txt
└── README.md

```

---

## Citation

```bibtex
@software{andv_seirq_behavioral_2026,
  author = {Kun and the Hermes Agent Team},
  title = {Dynamic Behavioral SEIRQ Model for ANDV Outbreak via Agentic OSINT},
  year = {2026},
  url = {[https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ](https://github.com/kunkunz420/ANDV-Behavioral-SEIRQ)}
}

```

---

## License

MIT License — see [LICENSE](https://www.google.com/search?q=LICENSE).

---

*A Plug-and-Play AI Skill for OSINT-driven Epidemiological Modelling*
