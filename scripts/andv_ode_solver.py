#!/usr/bin/env python3
"""
andv_ode_solver.py
==================
Dynamic Behavioral SEIRQ ODE model for the Andes Virus (ANDV) outbreak.

Mathematical framework:
  - S : Susceptible
  - E : Exposed (infected, not yet infectious)
  - I : Infectious (community-circulating)
  - R : Recovered / immune
  - Q : Quarantined (detected and isolated)

The ODE system:

    dS/dt = -beta(t) * S * I / N
    dE/dt =  beta(t) * S * I / N - sigma * E
    dI/dt =  sigma * E - gamma * I - qrate(t) * I
    dR/dt =  gamma * I
    dQ/dt =  qrate(t) * I

Key behavioural components:

  [1] Panic Elasticity (alpha = 0.65)
      The effective transmission rate beta(t) is modulated by a time-
      dependent awareness term derived from the cumulative quarantine
      burden. As the public observes more individuals being isolated,
      spontaneous social distancing reduces contact rates.

         beta_eff(t) = beta0 * max(0.10,
                                   1.0 - alpha * Q(t) / max(0.01*N, 1))

  [2] Quarantine Efficiency (eta_q)
      After a policy lag (tau), the detection and isolation rate of
      infectious individuals ramps up:

         qrate(t) = eta_q * kappa    for t >= tau
                   0                  otherwise

      where kappa = 0.3 is the baseline detection ramp.

  [3] Policy Intervention (step-function via policy_lag)
      The user specifies a policy_lag in days. Before this threshold
      no structured quarantine is enforced; after it, the full military
      or public-health machinery activates.

Default epidemiological parameters (ANDV-specific):
  - Basic reproduction number    R0         = 2.12
  - Incubation period            T_inc      = 21.0 days    (median)
  - Infectious period            T_inf      = 7.0 days
  - Total population pool        N          = 1000

Usage:
    python scripts/andv_ode_solver.py

Output:
    results/andv_trajectories.csv   — daily time series for both scenarios
"""

from __future__ import annotations

import os
import sys
import warnings
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# 1.  Core ODE system
# ---------------------------------------------------------------------------

def seirq_ode(
    t: float,
    y: List[float],
    beta0: float,
    sigma: float,
    gamma: float,
    eta_q: float,
    tau: float,
    N: float,
    alpha: float,
) -> List[float]:
    """
    Right-hand side of the SEIRQ ODE system with behavioural modulation.

    Parameters
    ----------
    t : float
        Current time (days).
    y : list of float
        State vector [S, E, I, R, Q].
    beta0 : float
        Baseline transmission rate (day^-1).  beta0 = R0 * gamma.
    sigma : float
        Incubation rate (1 / incubation_period, day^-1).
    gamma : float
        Recovery rate (1 / infectious_period, day^-1).
    eta_q : float
        Quarantine efficiency in [0, 1].
    tau : float
        Policy lag (days) — quarantine activates after this time.
    N : float
        Total population (constant).
    alpha : float
        Panic elasticity parameter in [0, 1].

    Returns
    -------
    list of float
        Time derivatives [dS/dt, dE/dt, dI/dt, dR/dt, dQ/dt].
    """
    S, E, I, R, Q = y

    # --- Time-dependent quarantine detection rate ---
    if t >= tau:
        quarantine_rate = eta_q * 0.3
    else:
        quarantine_rate = 0.0

    # --- Panic-driven behavioural reduction ---
    denom = max(0.01 * N, 1.0)
    awareness = 1.0 - alpha * (Q / denom)
    awareness = np.clip(awareness, 0.10, 1.0)

    beta_eff = beta0 * awareness

    # --- ODE equations ---
    dS = -beta_eff * S * I / N
    dE =  beta_eff * S * I / N - sigma * E
    dI =  sigma * E - gamma * I - quarantine_rate * I
    dR =  gamma * I
    dQ =  quarantine_rate * I

    return [dS, dE, dI, dR, dQ]


def compute_reff(
    S: float,
    Q: float,
    N: float,
    R0: float,
    alpha: float,
    t: float,
    tau: float,
    eta_q: float,
) -> float:
    """
    Compute the time-varying effective reproduction number.

    Reff(t) = R0 * (S/N) * awareness(t) * (1 - qrate_capture(t))

    where qrate_capture is the fraction of infectious individuals who are
    detected and removed per day, approximated as qrate / (qrate + gamma).
    """
    denom = max(0.01 * N, 1.0)
    awareness = 1.0 - alpha * (Q / denom)
    awareness = np.clip(awareness, 0.10, 1.0)

    if t >= tau:
        qrate = eta_q * 0.3
    else:
        qrate = 0.0

    q_capture = qrate / (qrate + gamma) if (qrate + gamma) > 0 else 0.0

    return R0 * (S / N) * awareness * (1.0 - q_capture)


# ---------------------------------------------------------------------------
# 2.  Scenario helpers
# ---------------------------------------------------------------------------

def simulate_scenario(
    beta0: float,
    sigma: float,
    gamma: float,
    S0: float,
    E0: float,
    I0: float,
    R0_pop: float,
    Q0: float,
    eta_q: float,
    tau: float,
    N: float,
    alpha: float,
    t_max: float = 60.0,
) -> Dict:
    """
    Run one full SEIRQ simulation for a given scenario over t_max days.

    Returns a dict with keys: 't', 'S', 'E', 'I', 'R', 'Q', 'active', 'Reff'.
    """
    y0 = [S0, E0, I0, R0_pop, Q0]

    # Evaluate every 0.1 day for smooth curves, then subsample to daily
    t_eval = np.linspace(0, t_max, int(t_max * 10) + 1)  # every 0.1 day

    sol = solve_ivp(
        seirq_ode,
        [0.0, t_max],
        y0,
        t_eval=t_eval,
        args=(beta0, sigma, gamma, eta_q, tau, N, alpha),
        method="RK45",
        dense_output=False,
    )

    t = sol.t
    S, E, I, R, Q = sol.y
    active = I.copy()

    Reff = np.full_like(t, np.nan)
    for i in range(len(t)):
        Reff[i] = compute_reff(S[i], Q[i], N, R0, alpha, t[i], tau, eta_q)

    return {
        "t": t,
        "S": S,
        "E": E,
        "I": I,
        "R": R,
        "Q": Q,
        "active": active,
        "Reff": Reff,
    }


def find_reff_below_one(t: np.ndarray, Reff: np.ndarray) -> float:
    """Return the first day where Reff drops below 1.0, or NaN if never."""
    below = np.where(Reff < 1.0)[0]
    return float(t[below[0]]) if len(below) > 0 else float("nan")


# ---------------------------------------------------------------------------
# 3.  Main entry point
# ---------------------------------------------------------------------------

# ── Epidemiological constants (ANDV-specific, module-level) ────────────
R0 = 2.12                         # basic reproduction number
INCUBATION_PERIOD = 21.0          # median incubation (days)
INFECTIOUS_PERIOD = 7.0           # infectious period (days)
N = 1_000                         # modelled population pool
ALPHA = 0.65                      # panic elasticity

sigma = 1.0 / INCUBATION_PERIOD
gamma = 1.0 / INFECTIOUS_PERIOD
beta0 = R0 * gamma


if __name__ == "__main__":
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

    # ── Scenario A: Worst-Case ─────────────────────────────────────────
    # E0=150 seeds, tau=7 days lag, eta_q=0.30 efficiency
    E0_a, I0_a = 150, 3
    S0_a = N - E0_a - I0_a
    scenario_a = simulate_scenario(
        beta0=beta0, sigma=sigma, gamma=gamma,
        S0=S0_a, E0=E0_a, I0=I0_a, R0_pop=0, Q0=0,
        eta_q=0.30, tau=7.0, N=N, alpha=0.65,
    )

    # ── Scenario B: Real-Time Containment ──────────────────────────────
    # E0=16 seeds, tau=1 day lag, eta_q=0.95 efficiency
    E0_b, I0_b = 16, 3
    S0_b = N - E0_b - I0_b
    scenario_b = simulate_scenario(
        beta0=beta0, sigma=sigma, gamma=gamma,
        S0=S0_b, E0=E0_b, I0=I0_b, R0_pop=0, Q0=0,
        eta_q=0.95, tau=1.0, N=N, alpha=0.65,
    )

    # ── Build daily trajectory CSV ─────────────────────────────────────
    records = []
    for label, data in [("Worst-Case", scenario_a),
                        ("Real-Time-Containment", scenario_b)]:
        # Subsample to daily integer days (t=0,1,2,...,60)
        t_arr = data["t"]
        for i in range(len(t_arr)):
            # Keep every 10th point (approx daily from 0.1-day resolution)
            if i % 10 == 0:
                records.append({
                    "Day": round(t_arr[i], 1),
                    "Scenario": label,
                    "Susceptible": data["S"][i],
                    "Exposed": data["E"][i],
                    "Infectious": data["I"][i],
                    "Recovered": data["R"][i],
                    "Quarantined": data["Q"][i],
                    "Active_Infections": data["active"][i],
                    "Reff": data["Reff"][i],
                })

    df = pd.DataFrame(records)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, "andv_trajectories.csv")
    df.to_csv(csv_path, index=False)
    print(f"[OK] Trajectories written to {csv_path}")
    print(f"     Rows: {len(df):,} | Scenarios: {df['Scenario'].nunique()}")
    print(f"     Day range: {df['Day'].min():.0f} — {df['Day'].max():.0f}")

    # ── Quick stats ────────────────────────────────────────────────────
    peak_a = float(scenario_a["active"].max())
    peak_b = float(scenario_b["active"].max())
    reff_a = find_reff_below_one(scenario_a["t"], scenario_a["Reff"])
    reff_b = find_reff_below_one(scenario_b["t"], scenario_b["Reff"])
    print(f"\n  Scenario A (Worst-Case): peak active = {peak_a:.1f}, "
          f"Reff < 1 on day {reff_a:.0f}")
    print(f"  Scenario B (Real-Time):  peak active = {peak_b:.1f}, "
          f"Reff < 1 on day {reff_b:.0f}")

    print("\nDone. Both scenarios simulated successfully.")
