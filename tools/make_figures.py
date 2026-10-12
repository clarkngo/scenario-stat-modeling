"""Render paper figures from results/results.json (matplotlib is used for plotting only).

Usage:  python3 tools/make_figures.py
Writes: assets/fig_sweep.png, assets/fig_fit.png
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "model"))
from baseline import ols_fit      # noqa: E402
from revised import huber_fit     # noqa: E402
from scenario import make_data, apply_shock, NOISE_SD  # noqa: E402

OLS_C, HUB_C, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False})


def fig_sweep(rows):
    c = [r["contamination"] * 100 for r in rows]
    fig, ax = plt.subplots(figsize=(4.2, 2.8), dpi=200)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.axhline(NOISE_SD, color=MUTED, lw=1, ls="--")
    ax.text(0, NOISE_SD - 45, "noise floor σ = 40", ha="left", color=MUTED, fontsize=8)
    ax.plot(c, [r["ols_rmse"] for r in rows], "-o", color=OLS_C, lw=2, ms=4)
    ax.plot(c, [r["hub_rmse"] for r in rows], "-o", color=HUB_C, lw=2, ms=4)
    ax.text(c[-1], rows[-1]["ols_rmse"], "  OLS", color=INK, va="center", fontsize=8)
    ax.text(c[-1], rows[-1]["hub_rmse"] + 40, "  Huber", color=INK, va="center", fontsize=8)
    ax.set_xlabel("Training rows hit by the shock (%)")
    ax.set_ylabel("Clean-test RMSE ($1000s)")
    ax.set_xlim(-1, c[-1] + 7)
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "assets", "fig_sweep.png"))
    plt.close(fig)


def fig_fit():
    rng = np.random.default_rng(7)
    X, y = make_data(200, rng)
    ys, mask = apply_shock(y, 0.10, rng)
    b_o, b_h = ols_fit(X, ys), huber_fit(X, ys)[0]
    # Partial-residual view: remove the age effect so price is plotted against size alone.
    xs = np.linspace(X[:, 0].min(), X[:, 0].max(), 50)
    fig, ax = plt.subplots(figsize=(4.2, 2.8), dpi=200)
    ax.grid(color=GRID, lw=0.8)
    ax.scatter(X[~mask, 0], ys[~mask] - b_h[2] * X[~mask, 1], s=8, color=MUTED, alpha=0.6, lw=0)
    ax.scatter(X[mask, 0], ys[mask] - b_h[2] * X[mask, 1], s=14, facecolors="none",
               edgecolors=INK, lw=0.8)
    ax.plot(xs, b_o[0] + b_o[1] * xs, color=OLS_C, lw=2)
    ax.plot(xs, b_h[0] + b_h[1] * xs, color=HUB_C, lw=2)
    ax.text(xs[-1], b_o[0] + b_o[1] * xs[-1], " OLS", color=INK, fontsize=8, va="center")
    ax.text(xs[-1], b_h[0] + b_h[1] * xs[-1], " Huber", color=INK, fontsize=8, va="center")
    ax.set_xlabel("House size (standardized)")
    ax.set_ylabel("Price, age-adjusted ($1000s)")
    top = 1600
    off = int((ys[mask] - b_h[2] * X[mask, 1] > top).sum())
    ax.text(xs[0], top - 80, f"+{off} shocked rows above (×10 prices, up to "
            f"{ys[mask].max():,.0f})", color=MUTED, fontsize=7.5, va="top")
    ax.set_ylim(-200, top)
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "assets", "fig_fit.png"))
    plt.close(fig)


if __name__ == "__main__":
    with open(os.path.join(ROOT, "results", "results.json")) as f:
        rows = json.load(f)["rows"]
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    fig_sweep(rows)
    fig_fit()
    print("wrote assets/fig_sweep.png, assets/fig_fit.png")
