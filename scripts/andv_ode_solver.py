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
  - Total population pool        N          = 450000000

Usage:
    python scripts/andv_ode_solver.py

Output:
    results/andv_trajectories.csv   — full time series for both scenarios
    results/scenario_comparison.txt — numeric summary (peak, final size, Reff)
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
        # kappa = 0.3: baseline detection ramp; scaled by efficiency
        quarantine_rate = eta_q * 0.3
    else:
        quarantine_rate = 0.0

    # --- Panic-driven behavioural reduction ---
    # Awareness grows with the fraction of the population that has been
    # quarantined. Q / (0.01 * N) normalises so that Q reaching 1% of N
    # causes (alpha * 1.0) reduction in beta.
    denom = max(0.01 * N, 1.0)
    awareness = 1.0 - alpha * (Q / denom)
    awareness = np.clip(awareness, 0.10, 1.0)   # floor at 10% contact

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
    detected and removed per day, approximated as:
        qrate_capture = 1 - exp(-qrate * dt),  but here we use the simpler
        linear fraction qrate / (qrate + gamma) for a steady-state estimate.
    """
    denom = max(0.01 * N, 1.0)
    awareness = 1.0 - alpha * (Q / denom)
    awareness = np.clip(awareness, 0.10, 1.0)

    if t >= tau:
        qrate = eta_q * 0.3
    else:
        qrate = 0.0

    # Fraction of infectious people captured by quarantine per generation
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
    t_max: float = 200.0,
    t_eval: int = 2001,
) -> Dict:
    """
    Run one full SEIRQ simulation for a given scenario.

    Returns a dict with keys: 't', 'S', 'E', 'I', 'R', 'Q', 'active', 'Reff'.
    """
    y0 = [S0, E0, I0, R0_pop, Q0]

    sol = solve_ivp(
        seirq_ode,
        [0.0, t_max],
        y0,
        t_eval=np.linspace(0, t_max, t_eval),
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


def scenario_summary(data: Dict, label: str) -> Dict:
    """
    Extract key epidemiological metrics from a simulation result.

    Returns a dict with peak day, peak value, final sizes, and Reff trajectory.
    """
    active = data["active"]
    t = data["t"]
    Reff = data["Reff"]

    peak_idx = int(np.argmax(active))

    below_one = np.where(Reff < 1.0)[0]
    below_day = float(t[below_one[0]]) if len(below_one) > 0 else None

    return {
        "scenario": label,
        "peak_day": float(t[peak_idx]),
        "peak_active": float(active[peak_idx]),
        "final_R": float(data["R"][-1]),
        "final_Q": float(data["Q"][-1]),
        "final_S": float(data["S"][-1]),
        "Reff_initial": float(Reff[0]),
        "Reff_day_7": float(Reff[min(70, len(Reff) - 1)]),
        "Reff_final": float(Reff[-1]),
        "Reff_below_1_day": below_day,
    }


# ---------------------------------------------------------------------------
# 3.  Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

    # ── Epidemiological constants (ANDV-specific) ──────────────────────
    R0 = 2.12                         # basic reproduction number
    INCUBATION_PERIOD = 21.0          # median incubation (days)  [1–6 weeks]
    INFECTIOUS_PERIOD = 7.0           # infectious period (days)
    N = 1_000                         # modelled population pool

    sigma = 1.0 / INCUBATION_PERIOD
    gamma = 1.0 / INFECTIOUS_PERIOD
    beta0 = R0 * gamma

    # ── Scenario A: Worst-case (no friction) ───────────────────────────
    # 150 disembarked seeds, 7-day policy lag, 30% quarantine efficiency.
    scenario_a = simulate_scenario(
        beta0=beta0, sigma=sigma, gamma=gamma,
        S0=N - 50 - 150, E0=50, I0=150, R0_pop=0, Q0=0,
        eta_q=0.30, tau=7.0, N=N, alpha=0.65,
    )
    summary_a = scenario_summary(scenario_a, "Worst-Case (150 seeds, 7d lag)")

    # ── Scenario B: Real-world containment ─────────────────────────────
    # 16 seeds (14 passengers + 2 contacts), 1-day policy lag,
    # 95% quarantine efficiency (military hospital isolation).
    scenario_b = simulate_scenario(
        beta0=beta0, sigma=sigma, gamma=gamma,
        S0=N - 16 - 2, E0=16, I0=2, R0_pop=0, Q0=0,
        eta_q=0.95, tau=1.0, N=N, alpha=0.65,
    )
    summary_b = scenario_summary(scenario_b, "Real-Time Containment (16 seeds, 1d lag)")

    # ── Build tidy CSV ─────────────────────────────────────────────────
    records = []
    for label, data in [("Worst-Case", scenario_a),
                        ("Real-Time-Containment", scenario_b)]:
        for i in range(len(data["t"])):
            records.append({
                "Day": data["t"][i],
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
    print(f"[OK] Trajectories written → {csv_path}")

    # ── Text summary ────────────────────────────────────────────────────
    lines = [
        "=" * 72,
        "  ANDV SEIRQ — Scenario Comparison Summary",
        "=" * 72,
        "",
        f"  R0 = {R0},  Incubation = {INCUBATION_PERIOD}d,  Infectious = {INFECTIOUS_PERIOD}d",
        "",
        f"  {'Metric':<38} {'Worst-Case (A)':<22} {'Real-Time (B)':<22}",
        f"  {'─'*38} {'─'*22} {'─'*22}",
        f"  {'Peak active infections':<38} {summary_a['peak_active']:<22.1f} {summary_b['peak_active']:<22.1f}",
        f"  {'Peak day':<38} {summary_a['peak_day']:<22.0f} {summary_b['peak_day']:<22.0f}",
        f"  {'Final recovered (R)':<38} {summary_a['final_R']:<22.1f} {summary_b['final_R']:<22.1f}",
        f"  {'Final quarantined (Q)':<38} {summary_a['final_Q']:<22.1f} {summary_b['final_Q']:<22.1f}",
        f"  {'Final susceptible (S)':<38} {summary_a['final_S']:<22.1f} {summary_b['final_S']:<22.1f}",
        f"  {'Reff (initial)':<38} {summary_a['Reff_initial']:<22.3f} {summary_b['Reff_initial']:<22.3f}",
        f"  {'Reff (day 7)':<38} {summary_a['Reff_day_7']:<22.3f} {summary_b['Reff_day_7']:<22.3f}",
        f"  {'Reff (final)':<38} {summary_a['Reff_final']:<22.4f} {summary_b['Reff_final']:<22.4f}",
        f"  {'Reff below 1.0 on day':<38} {summary_a['Reff_below_1_day'] if summary_a['Reff_below_1_day'] is not None else 'Never':<22} {summary_b['Reff_below_1_day'] if summary_b['Reff_below_1_day'] is not None else 'Never':<22}",
        "",
        "─" * 72,
        "  Key insight:",
        f"  With real-time military isolation (1-day lag, 95% efficiency) the outbreak",
        f"  peaks at only {summary_b['peak_active']:.0f} active infections and Reff drops below 1.0",
        f"  on day {summary_b['Reff_below_1_day']:.0f} — avoiding the catastrophic trajectory of the",
        f"  worst-case scenario ({summary_a['peak_active']:.0f} peak active).",
        "=" * 72,
    ]
    summary_text = "\n".join(lines)
    txt_path = os.path.join(OUTPUT_DIR, "scenario_comparison.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"[OK] Summary written → {txt_path}")

    print("\nDone. Both scenarios simulated successfully.")
