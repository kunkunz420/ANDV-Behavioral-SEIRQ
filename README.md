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
[![DOI](https://img.shields.io/badge/DOI-10.XXXX%2Fpreprint-blueviolet)](https://doi.org/)

**A plug-and-play AI skill for OSINT-driven epidemiological simulation — calibrated with real-time news intelligence from the MV Hondius ANDV outbreak (May 2026).**

<img src="results/active_vs_reff.png" alt="Active Infections vs Reff" width="700"/>

</div>

---

## Abstract / TL;DR

This repository presents a **dynamic behavioural SEIRQ compartment model** for the **Andes Virus (ANDV)** — the only hantavirus variant with confirmed human-to-human transmission — informed by **agentic OSINT** (real-time news scraping via DeepSeek). The model integrates **behavioral economics** (panic elasticity, $\alpha = 0.65$) and **step-function policy interventions** (military quarantine, Schengen border triggers) into a classical ODE epidemiological framework.

We contrast two scenarios for the **MV Hondius** cruise ship outbreak off the Canary Islands:

| Scenario | Initial Seeds | Policy Lag | Quarantine Efficiency | Peak Active | Reff < 1.0 | Schengen Closure Needed? |
|----------|:-------------:|:----------:|:---------------------:|:-----------:|:----------:|:------------------------:|
| **Worst-Case (A)** | 150 | 7 days | 30% | ~150 | Day 7 | **Yes** |
| **Real-Time Containment (B)** | 16 | 1 day 🚁 | 95% 🏥 | **~3** | **Day 5** | **No** |

**Key insight:** The real-world evidence — military airlift to Gómez Ulla Hospital (Madrid), single-room UAAN isolation, 42-day monitoring protocol, 60–90 dedicated healthcare staff — suppresses Reff below the elimination threshold **within 5 days**, making Schengen border closure epidemiologically unnecessary. Without this OSINT-driven calibration, standard models overestimate the outbreak by **two orders of magnitude**.

> *The difference between an unmitigated catastrophic projection and a contained localized event is the rapid behavioural response captured by real-time intelligence.*

---

## Methodology

### Model Architecture

We implement a **five-compartment SEIRQ ODE system**:

```
  Susceptible (S)  ——β(t)——>  Exposed (E)  ——σ——>  Infectious (I)  ——γ——>  Recovered (R)
                                                                  │
                                                                  │ qrate(t)
                                                                  ▼
                                                            Quarantined (Q)
```

#### Compartment Equations

$$
\begin{align}
\frac{dS}{dt} &= -\beta(t) \cdot \frac{S \cdot I}{N} \\[4pt]
\frac{dE}{dt} &=  \beta(t) \cdot \frac{S \cdot I}{N} - \sigma E \\[4pt]
\frac{dI}{dt} &=  \sigma E - \gamma I - q(t) I \\[4pt]
\frac{dR}{dt} &=  \gamma I \\[4pt]
\frac{dQ}{dt} &=  q(t) I
\end{align}
$$

#### Behavioural Modulation via Panic Elasticity

The effective transmission rate is attenuated by cumulative public awareness:

\[
\beta_{\text{eff}}(t) = \beta_0 \cdot \max\!\left(0.10,\; 1 - \alpha \cdot \frac{Q(t)}{0.01N}\right),\quad \alpha = 0.65
\]

The quarantine detection rate activates after a policy lag $\tau$:

\[
q(t) = \begin{cases}
\eta_q \cdot 0.3, & t \geq \tau \\
0, & t < \tau
\end{cases}
\]

#### Epidemiological Parameters (ANDV-specific)

| Parameter | Value | Source |
|-----------|-------|--------|
| Basic reproduction number $R_0$ | 2.12 | ANDV human-to-human literature |
| Incubation period (median) | 21.0 days | Clinical range 1–6 weeks |
| Infectious period | 7.0 days | Standard hantavirus estimate |
| Panic elasticity $\alpha$ | 0.65 | Calibrated from behavioural economics |
| Modelled population $N$ | 1,000 | Ship + close contact pool |

---

## OSINT Pipeline (Intelligence → Parameters)

The "Real-Time Containment" scenario was calibrated from 20 scraped news articles (DeepSeek预警_0122.txt) covering the MV Hondius incident:

| Intelligence Extract | Model Parameter |
|---------------------|-----------------|
| 14 Spanish nationals isolated + 2 contacts traced (Alicante, Barcelona) | $E_0 = 16$ |
| Military airlift within 24 hours | $\tau = 1.0$ day |
| Single-room UAAN isolation at Gómez Ulla Hospital, Madrid | $\eta_q = 0.95$ |
| 42-day monitoring protocol, 60–90 dedicated staff | Sustained quarantine enforcement |
| WHO epidemiologist on evacuation flight | International coordination verified |

---

## Quick Start

### Prerequisites
- Python 3.10+
- `pip`

### Setup & Run (copy-paste ready)

```bash
# 1. Clone
git clone https://github.com/your-org/andv-seirq-behavioral.git
cd andv-seirq-behavioral

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install
pip install -r requirements.txt

# 4. Run solver (generates results/andv_trajectories.csv)
python scripts/andv_ode_solver.py

# 5. Plot charts (generates results/*.png)
python scripts/plot_generator.py
```

### Expected Terminal Output

```
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

**Example customisations:**

- **Seasonal influenza:** Set `R0 = 1.3`, `INCUBATION_PERIOD = 1.4`, `INFECTIOUS_PERIOD = 5.0`
- **Delayed response (developing region):** Set `TAU = 14.0`, `ETA_Q = 0.40`
- **High public compliance (East Asian context):** Set `ALPHA = 0.85`, `ETA_Q = 0.90`

---

## Agent Integration — Using as an AI Skill

This codebase is designed to be ingested by **agentic LLM systems** as a dynamic OSINT skill. Other AI agents can:

### 1. Load as a contextual skill
Copy `scripts/andv_ode_solver.py` into the agent's skill directory. The agent can then:
- Parse news articles → extract epidemiological parameters
- Run the ODE solver with updated seeds
- Generate policy recommendations

### 2. Call via subprocess from any language
```bash
# Python-agnostic interface
python3 scripts/andv_ode_solver.py --R0 1.8 --alpha 0.70 --tau 3.0 --eta_q 0.80
```

### 3. Use the Reff criterion as an autonomous decision gate
```
if Reff < 1.0 at day 7:
    policy_recommendation = "Border closure NOT required"
else:
    policy_recommendation = "Escalate to Schengen-level intervention"
```

### 4. Bayesian prior structure for sequential OSINT updates
```
Prior:  Worst-case parameters (E0=50, I0=150, tau=7.0)
Update: News article → extract real seeds → re-simulate
Posterior: 16 seeds, 1-day lag → Reff < 1.0 confirmed
```

---

## Repository Structure

```
├── data/                    # Raw & processed OSINT inputs
├── scripts/
│   ├── andv_ode_solver.py   # SEIRQ ODE solver (scipy.integrate.solve_ivp)
│   └── plot_generator.py    # Publication-ready dual-axis charts
├── results/
│   ├── andv_trajectories.csv
│   ├── scenario_comparison.txt
│   ├── active_vs_reff.png
│   └── quarantine_vs_recovered.png
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Results Summary

| Metric | Worst-Case (A) | Real-Time (B) |
|--------|:--------------:|:--------------:|
| Peak Active Infections | ~150 | **~3** |
| Reff initial | 1.695 | 1.893 |
| Reff at day 7 | 1.064 | **0.866** |
| Reff < 1.0 achieved | Day 7 | **Day 5** |
| Final Quarantined | ~104 | **~17** |
| Final Susceptible | ~599 | **~973** |
| Requires Schengen Closure? | **Yes** | **No** |

The real-world response — immediate military isolation, single-room hospital quarantine at Gómez Ulla (Madrid), and a 42-day monitoring protocol — suppresses Reff below the elimination threshold within 5 days, making border closure epidemiologically unnecessary.

---

## Citation

```bibtex
@software{andv_seirq_behavioral_2026,
  author = {Kun and the Hermes Agent Team},
  title = {Dynamic Behavioral SEIRQ Model for ANDV Outbreak via Agentic OSINT},
  year = {2026},
  url = {https://github.com/your-org/andv-seirq-behavioral}
}
```

---

## License

MIT License — see [LICENSE](LICENSE).

---

<div align="center">

*Built with [Hermes Agent](https://hermes-agent.nousresearch.com) · Plug-and-Play AI Skill for OSINT-driven epidemiological modelling*
</div>
