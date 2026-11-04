"""Figures for the GARCH study (matplotlib is used for plotting only).

Usage:  python3 tools/make_garch_figures.py
Writes: assets/fig_garch_covid.png   1% VaR lines vs. daily returns around the 2020 crash
        assets/fig_garch_news.png    news-impact curves: tomorrow's volatility vs. today's return
"""
import json
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG_C, REV_C, NAIVE_C = "#2a78d6", "#eb6834", "#8a8984"
INK, MUTED, GRID, PT = "#0b0b0b", "#52514e", "#e4e3df", "#b9b8b3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False})


def to_year(d):
    d = np.asarray(d)
    y, mth, day = d // 10000, d // 100 % 100, d % 100
    return y + (mth - 1) / 12 + (day - 1) / 365


def fig_covid(res):
    w = res["window"]
    x, r = to_year(w["dates"]), np.array(w["returns"])
    fig, ax = plt.subplots(figsize=(6.4, 3.0), dpi=200)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.vlines(x, 0, r, color=PT, lw=0.9)
    lines = (("var_rolling", NAIVE_C, "Naive (past-year volatility)"),
             ("var_garch-n", ORIG_C, "GARCH, normal (original)"),
             ("var_gjr-t", REV_C, "GJR-GARCH, Student-t (revised)"))
    for key, color, _ in lines:
        ax.plot(x, w[key], color=color, lw=1.6)
    # Mark breaches of the naive and revised limits.
    for key, color, dy in (("var_rolling", NAIVE_C, -0.9), ("var_gjr-t", REV_C, -1.6)):
        hit = r < np.array(w[key])
        ax.scatter(x[hit], r[hit] + dy, marker="^", s=14, color=color, zorder=3, lw=0)
    # Legend in the calm upper-right corner, clear of the crash-day lines.
    for i, (key, color, label) in enumerate(lines):
        ax.text(0.99, 0.96 - i * 0.07, label + " —", transform=ax.transAxes, color=color,
                fontsize=7.5, fontweight="bold", ha="right", va="top")
    ax.text(0.99, 0.75, "▲ a day whose loss broke that limit", transform=ax.transAxes,
            color=MUTED, fontsize=7, ha="right", va="top")
    ax.set_ylabel("Daily market return (%)")
    ax.set_xlim(x[0], x[-1])
    ax.set_xticks([2020, 2020.25, 2020.5, 2020.75, 2021])
    ax.set_xticklabels(["Jan 2020", "Apr", "Jul", "Oct", "Jan 2021"])
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "assets", "fig_garch_covid.png"))
    plt.close(fig)


def fig_news(res):
    """sigma_t+1 as a function of today's shock e_t, starting from the long-run variance."""
    e = np.linspace(-6, 6, 241)
    fig, ax = plt.subplots(figsize=(4.2, 2.8), dpi=200)
    ax.grid(color=GRID, lw=0.8)
    for name, color, label in (("garch-n", ORIG_C, "GARCH (original)"),
                               ("gjr-t", REV_C, "GJR-GARCH (revised)")):
        p = res["models"][name]["params"]
        s2_bar = p["omega"] / (1 - p["persistence"])
        s2 = p["omega"] + (p["alpha"] + p["gamma"] * (e < 0)) * e ** 2 + p["beta"] * s2_bar
        ax.plot(e, np.sqrt(s2), color=color, lw=2)
        ax.text(e[0] + 0.15, math.sqrt(s2[0]), label, color=INK, fontsize=7.5, va="bottom")
    ax.set_xlabel("Today's surprise move (%)")
    ax.set_ylabel("Tomorrow's predicted volatility (%)")
    ax.text(-3, 0.12, "bad day", transform=ax.get_xaxis_transform(), ha="center", color=MUTED, fontsize=7.5)
    ax.text(3, 0.12, "good day", transform=ax.get_xaxis_transform(), ha="center", color=MUTED, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "assets", "fig_garch_news.png"))
    plt.close(fig)


if __name__ == "__main__":
    with open(os.path.join(ROOT, "results", "garch_results.json")) as f:
        res = json.load(f)
    fig_covid(res)
    fig_news(res)
    print("wrote assets/fig_garch_covid.png, assets/fig_garch_news.png")
