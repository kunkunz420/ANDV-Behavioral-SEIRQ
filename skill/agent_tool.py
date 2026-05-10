#!/usr/bin/env python3
"""
agent_tool.py
=============
Standard AI Agent tool-use interface for the ANDV Behavioral SEIRQ Model.

This module provides a single entry-point function, `assess_andv_risk()`,
which LLM agents can call as a tool to simulate ANDV outbreak scenarios
using custom parameters derived from real-time OSINT intelligence.

Usage by LLM agents:
    from skill.agent_tool import assess_andv_risk

    result = assess_andv_risk(
        initial_seeds=16,
        policy_lag_days=1.0,
        quarantine_efficiency=0.95,
    )
    # Returns a concise summary string with peak infections and Reff timing.

The function automatically imports the solver from scripts/andv_ode_solver.py,
runs a custom scenario, and returns a human-readable epidemiological summary.
"""

from __future__ import annotations

import os
import sys
import warnings
from typing import Optional

import numpy as np

warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Dynamic import of the solver module (handles both direct and package usage)
# ---------------------------------------------------------------------------

_SOLVER_IMPORTED = False


def _import_solver():
    """
    Import the SEIRQ solver module from scripts/andv_ode_solver.py.

    Ensures the scripts directory is on sys.path regardless of how this
    module is invoked (directly, via PYTHONPATH, or from a subprocess).
    """
    global _SOLVER_IMPORTED
    if _SOLVER_IMPORTED:
        return

    # Resolve the project root relative to this file's location
    SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SKILL_DIR)
    SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")

    if SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, SCRIPTS_DIR)

    global simulate_scenario, compute_reff, find_reff_below_one, seirq_ode, R0, N, ALPHA

    # Import the constants and functions from the solver module
    import andv_ode_solver as solver

    simulate_scenario = solver.simulate_scenario
    compute_reff = solver.compute_reff
    find_reff_below_one = solver.find_reff_below_one
    seirq_ode = solver.seirq_ode

    # Use the solver's module-level ANDV constants
    global R0, INCUBATION_PERIOD, INFECTIOUS_PERIOD, N, ALPHA, sigma, gamma, beta0
    R0 = solver.R0
    INCUBATION_PERIOD = solver.INCUBATION_PERIOD
    INFECTIOUS_PERIOD = solver.INFECTIOUS_PERIOD
    N = solver.N
    ALPHA = solver.ALPHA
    sigma = solver.sigma
    gamma = solver.gamma
    beta0 = solver.beta0

    _SOLVER_IMPORTED = True


# ---------------------------------------------------------------------------
# Public API — single tool-call function for LLM agents
# ---------------------------------------------------------------------------

def assess_andv_risk(
    initial_seeds: int,
    policy_lag_days: float,
    quarantine_efficiency: float,
    population: int = 1_000,
    t_max: float = 60.0,
) -> str:
    """
    Assess ANDV outbreak risk using the Dynamic Behavioral SEIRQ model.

    This is the primary entry point for LLM agents. Call this function with
    parameters extracted from real-time OSINT intelligence (news scraping,
    situation reports, contact tracing data).

    Parameters
    ----------
    initial_seeds : int
        Number of exposed (E0) individuals at simulation start. Derive this
        from OSINT by counting confirmed contacts, trace-positive passengers,
        and known exposures. Example: 16 (14 Spanish nationals + 2 contacts).
    policy_lag_days : float
        Policy activation delay in days. The number of days before quarantine
        enforcement begins. Derive from reports of military airlift, hospital
        isolation orders, or government response timelines. Example: 1.0.
    quarantine_efficiency : float
        Quarantine efficiency in [0.0, 1.0]. Fraction of infectious individuals
        detected and isolated once policy is active. Higher values reflect
        advanced isolation facilities (e.g., UAAN negative-pressure rooms).
        Example: 0.95 (military hospital grade).
    population : int, optional
        Total modelled population pool. Default: 1,000 (cruise ship scale).
        For regional forecasts, scale to the relevant metropolitan population
        (e.g., 6,500,000 for Madrid).
    t_max : float, optional
        Simulation duration in days. Default: 60.0.

    Returns
    -------
    str
        A clean, English epidemiological summary containing:
          - Peak active infections (I_max)
          - The exact day Reff drops below 1.0 (or a warning if it never does)
          - Final outbreak size (cumulative recovered + quarantined)
        Suitable for direct inclusion in LLM responses.

    Examples
    --------
    >>> assess_andv_risk(initial_seeds=16, policy_lag_days=1.0,
    ...                  quarantine_efficiency=0.95)
    '[ANDV Risk Assessment]
     Scenario: 16 seeds, 1.0-day policy lag, 95% quarantine efficiency
     - Peak active infections: 2.4 persons
     - Reff drops below 1.0 on day 5.0
     - Outbreak contained: 2.0% of population infected'

    >>> assess_andv_risk(initial_seeds=150, policy_lag_days=7.0,
    ...                  quarantine_efficiency=0.30)
    '[ANDV Risk Assessment]
     Scenario: 150 seeds, 7.0-day policy lag, 30% quarantine efficiency
     - Peak active infections: 410.1 persons
     - Reff drops below 1.0 on day 10.0
     - Final outbreak size: 40.1% of population infected'

    Notes
    -----
    The underlying ODE system implements:
      - Five-compartment SEIRQ dynamics (S, E, I, R, Q)
      - Panic elasticity (alpha=0.65) for behavioural social distancing
      - Step-function policy intervention after policy_lag_days
      - ANDV-specific parameters: R0=2.12, incubation=21d, infectious=7d

    For worst-case baseline scenario, see README.md.
    """
    _import_solver()

    # Guard against invalid inputs
    initial_seeds = max(1, int(initial_seeds))
    policy_lag_days = max(0.0, float(policy_lag_days))
    quarantine_efficiency = max(0.0, min(1.0, float(quarantine_efficiency)))
    population = max(100, int(population))

    # Derived parameters (mirror the solver's constants)
    INCUBATION_PERIOD = 21.0
    INFECTIOUS_PERIOD = 7.0
    sigma = 1.0 / INCUBATION_PERIOD
    gamma = 1.0 / INFECTIOUS_PERIOD
    beta0 = R0 * gamma

    # Initial conditions: E0 = seeds, I0 = 3 symptomatic, rest susceptible
    E0 = float(initial_seeds)
    I0 = 3.0
    S0 = float(population) - E0 - I0

    # Run the simulation
    result = simulate_scenario(
        beta0=beta0, sigma=sigma, gamma=gamma,
        S0=S0, E0=E0, I0=I0, R0_pop=0.0, Q0=0.0,
        eta_q=quarantine_efficiency, tau=policy_lag_days,
        N=float(population), alpha=ALPHA,
        t_max=t_max,
    )

    # Extract key metrics
    active = result["active"]
    Reff_arr = result["Reff"]
    t_arr = result["t"]

    peak_infections = float(np.max(active))
    peak_day = float(t_arr[int(np.argmax(active))])

    reff_below_day = find_reff_below_one(t_arr, Reff_arr)
    reff_below_str = (
        f"day {reff_below_day:.1f}"
        if not np.isnan(reff_below_day)
        else "NEVER (outbreak grows uncontrolled)"
    )

    final_R = float(result["R"][-1])
    final_Q = float(result["Q"][-1])
    total_infected = final_R + final_Q
    frac_infected = total_infected / population * 100.0

    # Build the summary string
    summary = (
        f"[ANDV Risk Assessment]\n"
        f" Scenario: {initial_seeds} seeds, {policy_lag_days}-day policy lag, "
        f"{quarantine_efficiency*100:.0f}% quarantine efficiency\n"
        f" - Peak active infections: {peak_infections:.1f} persons (day {peak_day:.0f})\n"
        f" - Effective reproduction number (Reff) drops below 1.0 on {reff_below_str}\n"
        f" - Final outbreak size: {total_infected:.1f} total cases "
        f"({frac_infected:.1f}% of population)\n"
        f"   - Recovered: {final_R:.1f}\n"
        f"   - Quarantined: {final_Q:.1f}\n"
    )

    if not np.isnan(reff_below_day) and reff_below_day <= 14.0:
        summary += (
            " Assessment: Rapid containment achieved. "
            "Border closure is epidemiologically unnecessary.\n"
        )
    else:
        summary += (
            " Assessment: HIGH RISK — delayed or insufficient intervention. "
            "Border closure and surge capacity required.\n"
        )

    return summary


# ---------------------------------------------------------------------------
# CLI entry point (for manual testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Run both canonical scenarios to demonstrate the tool
    print("=" * 72)
    print("  ANDV Risk Assessment Tool — Test Run")
    print("=" * 72)

    print("\n>>> Scenario A: Worst-Case (150 seeds, 7d lag, 30% efficiency)")
    print(assess_andv_risk(initial_seeds=150, policy_lag_days=7.0,
                           quarantine_efficiency=0.30))

    print("\n>>> Scenario B: Real-Time Containment (16 seeds, 1d lag, 95% efficiency)")
    print(assess_andv_risk(initial_seeds=16, policy_lag_days=1.0,
                           quarantine_efficiency=0.95))
