"""Figures for the Kalman prototype (matplotlib is used for plotting only).

Usage:  python3 tools/make_kalman_figures.py
Writes: assets/fig_kalman_beta.png, assets/fig_kalman_inject.png
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAL_C, ROB_C, ROLL_C, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#8a8984", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False})


def years(dates):
    d = np.array(dates)
    return d // 100 + (d % 100 - 0.5) / 12


def fig_beta(main, burn):
    x = years(main["dates"])[burn:]
    roll = np.array([np.nan if b is None else b for b in main["beta_rolling60"]])[burn:]
    fig, ax = plt.subplots(figsize=(6.4, 2.9), dpi=200)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.axhline(1.0, color=MUTED, lw=0.8, ls=":")
    ax.plot(x, roll, color=ROLL_C, lw=1.2)
    ax.plot(x, np.array(main["beta_kalman"])[burn:], color=KAL_C, lw=1.6)
    ax.plot(x, np.array(main["beta_robust"])[burn:], color=ROB_C, lw=1.6)
    # End labels, nudged apart when the two Kalman lines finish close together.
    yk, yr = main["beta_kalman"][-1], main["beta_robust"][-1]
    if abs(yk - yr) < 0.08:
        mid = (yk + yr) / 2
        yr, yk = (mid + 0.05, mid - 0.05) if yr >= yk else (mid - 0.05, mid + 0.05)
    for label, y in (("Kalman", yk), ("Robust Kalman", yr), ("60-month OLS", roll[-1])):
        ax.text(x[-1] + 0.6, y, label, color=INK, fontsize=7.5, va="center")
    ax.set_xlim(x[0], x[-1] + 9)
    ax.set_ylabel(f"Beta of {main['industry']} vs. market")
    ax.text(1994.5, 2.05, "dot-com boom →", color=MUTED, fontsize=7.5, ha="right", va="center")
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "assets", "fig_kalman_beta.png"))
    plt.close(fig)


def fig_inject(main, meta):
    x = years(main["dates"])
    k = int(np.nonzero(np.array(main["dates"]) == meta["inject_at"])[0][0])
    lo, hi = k - 12, min(k + 84, len(x))
    fig, ax = plt.subplots(figsize=(4.2, 2.8), dpi=200)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.axvline(x[k], color=MUTED, lw=0.8, ls="--")
    ax.text(x[k] - 0.15, 0.12, f"one fake +{meta['inject_size']:.0f}-point\nreturn typed in",
            transform=ax.get_xaxis_transform(), fontsize=7, color=MUTED, ha="right")
    ax.plot(x[lo:hi], np.array(main["inject_path_kalman"])[lo:hi], color=KAL_C, lw=1.8)
    ax.plot(x[lo:hi], np.array(main["inject_path_robust"])[lo:hi], color=ROB_C, lw=1.8)
    dk = np.array(main["inject_path_kalman"])
    dr = np.array(main["inject_path_robust"])
    ax.text(x[k] + 0.3, dk[k], f"Kalman ({dk[k]:+.2f})", color=INK, fontsize=7.5, va="center")
    ax.text(x[k] + 0.3, dr[k] - 0.006, f"Robust Kalman ({dr[k]:+.2f})", color=INK, fontsize=7.5,
            va="top")
    ax.set_ylabel("Beta error caused by the typo")
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "assets", "fig_kalman_inject.png"))
    plt.close(fig)


if __name__ == "__main__":
    with open(os.path.join(ROOT, "results", "kalman_results.json")) as f:
        res = json.load(f)
    fig_beta(res["main"], res["meta"]["burn"])
    fig_inject(res["main"], res["meta"])
    print("wrote assets/fig_kalman_beta.png, assets/fig_kalman_inject.png")
