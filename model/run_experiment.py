"""Monte Carlo comparison of OLS (original) vs Huber-IRLS (revised) under a scenario shock.

Usage:  python3 model/run_experiment.py
Writes: results/results.json, results/results.md
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from baseline import ols_fit, predict          # noqa: E402
from revised import huber_fit                   # noqa: E402
from scenario import TRUE_BETA, NOISE_SD, make_data, apply_shock  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVELS = [0.0, 0.05, 0.10, 0.20, 0.30]
N_TRAIN, N_TEST, N_REPS, SEED = 200, 1000, 200, 623


def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


def run():
    rng = np.random.default_rng(SEED)
    rows = []
    for c in LEVELS:
        stats = {"ols_rmse": [], "hub_rmse": [], "ols_berr": [], "hub_berr": [], "hub_iter": []}
        for _ in range(N_REPS):
            Xtr, ytr = make_data(N_TRAIN, rng)
            Xte, yte = make_data(N_TEST, rng)
            ytr_s, _ = apply_shock(ytr, c, rng)
            b_ols = ols_fit(Xtr, ytr_s)
            b_hub, info = huber_fit(Xtr, ytr_s)
            stats["ols_rmse"].append(rmse(predict(b_ols, Xte), yte))
            stats["hub_rmse"].append(rmse(predict(b_hub, Xte), yte))
            stats["ols_berr"].append(float(np.linalg.norm(b_ols - TRUE_BETA)))
            stats["hub_berr"].append(float(np.linalg.norm(b_hub - TRUE_BETA)))
            stats["hub_iter"].append(info["iterations"])
        row = {"contamination": c}
        for k, v in stats.items():
            row[k] = float(np.mean(v))
            row[k + "_sd"] = float(np.std(v, ddof=1))
        rows.append(row)
    return rows


def to_markdown(rows):
    head = ("| Shock (contamination) | OLS test RMSE | Huber test RMSE | "
            "OLS ‖β̂−β‖ | Huber ‖β̂−β‖ | Huber IRLS iters |\n"
            "|---|---|---|---|---|---|\n")
    body = "".join(
        f"| {r['contamination']:.0%} | {r['ols_rmse']:.1f} | {r['hub_rmse']:.1f} | "
        f"{r['ols_berr']:.1f} | {r['hub_berr']:.1f} | {r['hub_iter']:.1f} |\n"
        for r in rows)
    note = (f"\nMean over {N_REPS} replications; n_train={N_TRAIN}, n_test={N_TEST} (clean); "
            f"noise σ={NOISE_SD:.0f}, so σ is the irreducible RMSE floor.\n")
    return head + body + note


if __name__ == "__main__":
    rows = run()
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    meta = {"levels": LEVELS, "n_train": N_TRAIN, "n_test": N_TEST, "n_reps": N_REPS,
            "seed": SEED, "true_beta": TRUE_BETA.tolist(), "noise_sd": NOISE_SD}
    with open(os.path.join(ROOT, "results", "results.json"), "w") as f:
        json.dump({"meta": meta, "rows": rows}, f, indent=2)
    md = to_markdown(rows)
    with open(os.path.join(ROOT, "results", "results.md"), "w") as f:
        f.write(md)
    print(md)
