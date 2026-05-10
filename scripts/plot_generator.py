#!/usr/bin/env python3
"""
plot_generator.py
==================
Generates publication-ready dual-axis charts for the ANDV SEIRQ model.

Plots produced:
  1. Active Infections vs. Reff (dual-axis, log-linear)
  2. Cumulative Quarantined vs. Cumulative Recovered (dual-axis)

All saved to the `results/` directory at 300 DPI with seaborn styling.

Usage:
    python scripts/plot_generator.py

Dependencies:
    pandas, numpy, matplotlib, seaborn
"""

from __future__ import annotations

import os
import sys
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns

warnings.filterwarnings("ignore", category=UserWarning)

# =========================================================================
# 0.  Aesthetic configuration — academic seaborn style
# =========================================================================
sns.set_theme(style="whitegrid", context="talk", palette="muted", font_scale=0.95)

rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "axes.unicode_minus": False,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "legend.fontsize": 8,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "lines.linewidth": 2.0,
})

COLOURS = {
    "Worst-Case": "#e74c3c",
    "Real-Time-Containment": "#2ecc71",
}

LINE_STYLES = {
    "Worst-Case": "--",
    "Real-Time-Containment": "-",
}

AXIS_ALPHA = 0.75

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "results")


def load_trajectories() -> pd.DataFrame:
    """Load the merged trajectories CSV produced by andv_ode_solver.py."""
    path = os.path.join(OUTPUT_DIR, "andv_trajectories.csv")
    if not os.path.isfile(path):
        print(f"[ERROR] Trajectories not found at {path}.")
        print("        Run `python scripts/andv_ode_solver.py` first.")
        sys.exit(1)
    df = pd.read_csv(path)
    print(f"[OK] Loaded {len(df):,} rows from {path}")
    return df


# =========================================================================
# 1.  Active Infections vs. Reff (dual-axis log-linear chart)
# =========================================================================

def plot_active_vs_reff(df: pd.DataFrame) -> str:
    """
    Create a dual-axis chart:
      Left y-axis : Active Infections (log scale)
      Right y-axis: Effective Reproduction Number Reff (linear)

    Saves to results/active_vs_reff.png.

    Parameters
    ----------
    df : pd.DataFrame
        Trajectories data with columns: Day, Scenario, Active_Infections, Reff.

    Returns
    -------
    str
        Path to the saved PNG file.
    """
    fig, ax1 = plt.subplots(figsize=(10, 5.5))

    # Left axis: Active Infections (log scale)
    for scenario in ["Worst-Case", "Real-Time-Containment"]:
        sub = df[df["Scenario"] == scenario].copy()
        sub = sub.sort_values("Day")
        ax1.plot(
            sub["Day"], sub["Active_Infections"],
            color=COLOURS[scenario],
            linestyle=LINE_STYLES[scenario],
            alpha=AXIS_ALPHA,
            label=f"{scenario} — Active Infections",
        )

    ax1.set_xlabel("Time (days)")
    ax1.set_ylabel("Active Infections (log scale)", color="#2c3e50")
    ax1.set_yscale("log")
    ax1.set_xlim(0, df["Day"].max())
    ax1.grid(True, alpha=0.25, which="both")
    ax1.tick_params(axis="y", labelcolor="#2c3e50")

    # Annotation: detection threshold
    ax1.axhline(y=1.0, color="gray", linewidth=0.6, linestyle=":", alpha=0.5)

    # Right axis: Reff (linear)
    ax2 = ax1.twinx()
    for scenario in ["Worst-Case", "Real-Time-Containment"]:
        sub = df[df["Scenario"] == scenario].copy()
        sub = sub.sort_values("Day")
        ax2.plot(
            sub["Day"], sub["Reff"],
            color=COLOURS[scenario],
            linestyle=LINE_STYLES[scenario],
            alpha=AXIS_ALPHA * 0.6,
            linewidth=1.5,
            label=f"{scenario} — Reff",
        )

    # Elimination threshold line
    ax2.axhline(y=1.0, color="crimson", linewidth=1.2, linestyle="-", alpha=0.7)
    ax2.text(
        df["Day"].max() * 0.70, 1.04, "Reff = 1 (Elimination Threshold)",
        fontsize=8, color="crimson", fontstyle="italic",
    )
    ax2.set_ylabel("Effective Reproduction Number (Reff)", color="crimson")
    ax2.set_ylim(0, 2.5)
    ax2.tick_params(axis="y", labelcolor="crimson")

    # Combined legend
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines_1 + lines_2, labels_1 + labels_2,
        loc="upper right", fontsize=7, framealpha=0.85,
        ncol=1,
    )

    # Title & layout
    fig.suptitle(
        "ANDV SEIRQ: Active Infections & Effective Reproduction Number",
        fontsize=14, fontweight="bold", y=0.97,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])

    path = os.path.join(OUTPUT_DIR, "active_vs_reff.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[OK] Chart saved to {path}")
    return path


# =========================================================================
# 2.  Cumulative Quarantine vs. Cumulative Recovered (dual-axis)
# =========================================================================

def plot_quarantine_vs_recovered(df: pd.DataFrame) -> str:
    """
    Dual-axis chart comparing cumulative quarantined (Q) and
    cumulative recovered (R) populations for both scenarios.

    Saves to results/quarantine_vs_recovered.png.

    Parameters
    ----------
    df : pd.DataFrame
        Trajectories data with columns: Day, Scenario, Quarantined, Recovered.

    Returns
    -------
    str
        Path to the saved PNG file.
    """
    fig, ax1 = plt.subplots(figsize=(10, 5.5))

    # Left axis: Cumulative Quarantined
    for scenario in ["Worst-Case", "Real-Time-Containment"]:
        sub = df[df["Scenario"] == scenario].copy()
        sub = sub.sort_values("Day")
        ax1.plot(
            sub["Day"], sub["Quarantined"],
            color=COLOURS[scenario],
            linestyle=LINE_STYLES[scenario],
            alpha=AXIS_ALPHA,
            label=f"{scenario} — Quarantined",
        )

    ax1.set_xlabel("Time (days)")
    ax1.set_ylabel("Cumulative Quarantined (Q)", color="#2c3e50")
    ax1.set_xlim(0, df["Day"].max())
    ax1.grid(True, alpha=0.25)
    ax1.tick_params(axis="y", labelcolor="#2c3e50")

    # Right axis: Cumulative Recovered
    ax2 = ax1.twinx()
    for scenario in ["Worst-Case", "Real-Time-Containment"]:
        sub = df[df["Scenario"] == scenario].copy()
        sub = sub.sort_values("Day")
        ax2.plot(
            sub["Day"], sub["Recovered"],
            color=COLOURS[scenario],
            linestyle=LINE_STYLES[scenario],
            alpha=AXIS_ALPHA * 0.6,
            linewidth=1.5,
            label=f"{scenario} — Recovered",
        )

    ax2.set_ylabel("Cumulative Recovered (R)", color="#8e44ad")
    ax2.tick_params(axis="y", labelcolor="#8e44ad")

    # Combined legend
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines_1 + lines_2, labels_1 + labels_2,
        loc="upper left", fontsize=7, framealpha=0.85,
    )

    fig.suptitle(
        "ANDV SEIRQ: Cumulative Quarantined vs. Cumulative Recovered",
        fontsize=14, fontweight="bold", y=0.97,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])

    path = os.path.join(OUTPUT_DIR, "quarantine_vs_recovered.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[OK] Chart saved to {path}")
    return path


# =========================================================================
# 3.  Main entry point
# =========================================================================

if __name__ == "__main__":
    df = load_trajectories()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    p1 = plot_active_vs_reff(df)
    p2 = plot_quarantine_vs_recovered(df)

    print("\n[ALL DONE] Publication-ready charts generated:")
    print(f"  1. {p1}")
    print(f"  2. {p2}")
