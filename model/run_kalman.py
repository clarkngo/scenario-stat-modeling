"""Kalman (original) vs robust Huber-Kalman (revised) time-varying beta on real data.

Data: Kenneth R. French Data Library, monthly, 1963-07 onward (data/french_monthly.csv;
refresh with tools/fetch_french.py). y = industry return - RF, m = Mkt-RF, in percent.

Usage:  python3 model/run_kalman.py
Writes: results/kalman_results.json, results/kalman_results.md
"""
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from kalman import HUBER_C, fit_mle, kalman_filter, rolling_ols_beta  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = 196307
MAIN = "BusEq"                         # business equipment: computers, software, electronics
CRASHES = {198710: "Oct 1987 crash", 200810: "Oct 2008 crisis", 202003: "Mar 2020 COVID"}
INJECT_AT, INJECT_SIZE = 201506, 30.0  # fake +30-point data error in a calm month
BURN = 24                              # months excluded while the diffuse prior settles
RECOVER_TOL = 0.02


def load():
    with open(os.path.join(ROOT, "data", "french_monthly.csv")) as f:
        rows = [r for r in csv.DictReader(f) if int(r["date"]) >= START]
    dates = np.array([int(r["date"]) for r in rows])
    m = np.array([float(r["mkt_rf"]) for r in rows])
    rf = np.array([float(r["rf"]) for r in rows])
    inds = [k for k in rows[0] if k not in ("date", "mkt_rf", "rf")]
    Y = {k: np.array([float(r[k]) for r in rows]) - rf for k in inds}
    return dates, m, Y


def metrics(y, m, f):
    """One-step-ahead errors and beta stability after the burn-in."""
    H_theta = f["theta_pred"][:, 0] + f["theta_pred"][:, 1] * m
    e = (y - H_theta)[BURN:]
    beta = f["theta_filt"][BURN:, 1]
    return {"rmse": float(np.sqrt(np.mean(e ** 2))), "mae": float(np.mean(np.abs(e))),
            "mean_abs_dbeta": float(np.mean(np.abs(np.diff(beta)))),
            "clipped_share": float(np.mean(f["clipped"][BURN:]))}


def excess_kurtosis(z):
    z = (z - z.mean()) / z.std()
    return float(np.mean(z ** 4) - 3.0)


def injection(y, m, q, r, c, k):
    """Effect of a single fake data error at index k on the filtered beta path."""
    y_bad = y.copy()
    y_bad[k] += INJECT_SIZE
    d = (kalman_filter(y_bad, m, q, r, c=c)["theta_filt"][:, 1]
         - kalman_filter(y, m, q, r, c=c)["theta_filt"][:, 1])
    after = np.abs(d[k:])
    still = np.nonzero(after >= RECOVER_TOL)[0]
    return {"max_shift": float(after.max()),
            "months_to_recover": int(still[-1] + 1) if still.size else 0,
            "path": d.tolist()}


def run():
    dates, m, Y = load()
    k_inj = int(np.nonzero(dates == INJECT_AT)[0][0])
    per_ind, main = {}, None
    for name, y in Y.items():
        q, r, info = fit_mle(y, m)
        g = kalman_filter(y, m, q, r)
        h = kalman_filter(y, m, q, r, c=HUBER_C)
        u = (g["v"] / np.sqrt(g["S"]))[BURN:]
        row = {"q_alpha": float(q[0]), "q_beta": float(q[1]), "r": float(r), **info,
               "surprise_excess_kurtosis": excess_kurtosis(u),
               "share_beyond_3sd": float(np.mean(np.abs(u) > 3)),
               "kalman": metrics(y, m, g), "robust": metrics(y, m, h)}
        inj_g = injection(y, m, q, r, np.inf, k_inj)
        inj_h = injection(y, m, q, r, HUBER_C, k_inj)
        row["inject"] = {"kalman": {k: v for k, v in inj_g.items() if k != "path"},
                         "robust": {k: v for k, v in inj_h.items() if k != "path"}}
        per_ind[name] = row
        if name == MAIN:
            crash = {}
            for d, label in CRASHES.items():
                i = int(np.nonzero(dates == d)[0][0])
                crash[label] = {
                    "market_return": float(m[i]),
                    "kalman_dbeta": float(g["theta_filt"][i, 1] - g["theta_filt"][i - 1, 1]),
                    "robust_dbeta": float(h["theta_filt"][i, 1] - h["theta_filt"][i - 1, 1]),
                    "robust_clipped": bool(h["clipped"][i])}
            main = {"industry": name, "dates": dates.tolist(),
                    "beta_kalman": g["theta_filt"][:, 1].tolist(),
                    "beta_robust": h["theta_filt"][:, 1].tolist(),
                    "beta_rolling60": [None if np.isnan(b) else float(b)
                                       for b in rolling_ols_beta(y, m)],
                    "clipped": h["clipped"].tolist(), "crash": crash,
                    "inject_path_kalman": inj_g["path"], "inject_path_robust": inj_h["path"]}
    meta = {"start": int(dates[0]), "end": int(dates[-1]), "months": int(dates.size),
            "burn": BURN, "huber_c": HUBER_C, "inject_at": INJECT_AT,
            "inject_size": INJECT_SIZE, "recover_tol": RECOVER_TOL}
    return {"meta": meta, "industries": per_ind, "main": main}


def to_markdown(res):
    meta, ind = res["meta"], res["industries"]
    lines = [f"Data: Kenneth R. French Data Library, {meta['start']}–{meta['end']} "
             f"({meta['months']} months). Huber c = {meta['huber_c']}.\n",
             "| Industry | Surprise excess kurtosis | Kalman MAE | Robust MAE | Kalman RMSE | "
             "Robust RMSE | Kalman avg monthly Δβ | Robust avg monthly Δβ | Months clipped |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, r in ind.items():
        k, h = r["kalman"], r["robust"]
        lines.append(f"| {name} | {r['surprise_excess_kurtosis']:.1f} | {k['mae']:.3f} | "
                     f"{h['mae']:.3f} | {k['rmse']:.3f} | {h['rmse']:.3f} | "
                     f"{k['mean_abs_dbeta']:.4f} | {h['mean_abs_dbeta']:.4f} | "
                     f"{h['clipped_share']:.1%} |")
    lines += ["", f"Injected data error: +{meta['inject_size']:.0f} points at {meta['inject_at']}.",
              "", "| Industry | Kalman max β shift | Robust max β shift | Kalman months to recover | "
              "Robust months to recover |", "|---|---|---|---|---|"]
    for name, r in ind.items():
        k, h = r["inject"]["kalman"], r["inject"]["robust"]
        lines.append(f"| {name} | {k['max_shift']:.3f} | {h['max_shift']:.3f} | "
                     f"{k['months_to_recover']} | {h['months_to_recover']} |")
    lines += ["", f"Crash months ({res['main']['industry']}):", "",
              "| Month | Market excess return | Kalman Δβ | Robust Δβ | Robust clipped? |",
              "|---|---|---|---|---|"]
    for label, c in res["main"]["crash"].items():
        lines.append(f"| {label} | {c['market_return']:.1f}% | {c['kalman_dbeta']:+.3f} | "
                     f"{c['robust_dbeta']:+.3f} | {'yes' if c['robust_clipped'] else 'no'} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    res = run()
    with open(os.path.join(ROOT, "results", "kalman_results.json"), "w") as f:
        json.dump(res, f)
    md = to_markdown(res)
    with open(os.path.join(ROOT, "results", "kalman_results.md"), "w") as f:
        f.write(md)
    print(md)
