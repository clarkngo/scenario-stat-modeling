"""GARCH(1,1) (original) vs GJR-GARCH(1,1)-t (revised): Value-at-Risk backtest on real data.

Data: Kenneth R. French Data Library, daily US market return (Mkt-RF + RF), in percent
(data/french_daily.csv; refresh with tools/fetch_french.py).
Fit on TRAIN (1990-2014), then forecast each TEST day (2015 onward) using only earlier days.

Usage:  python3 model/run_garch.py
Writes: results/garch_results.json, results/garch_results.md
"""
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import garch as G  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, TEST_START = 19900101, 20150101
LEVELS = (0.01, 0.05)
STRESS = (20200201, 20200501, "Feb–Apr 2020 (COVID crash)")
FITTED = ("garch-n", "garch-t", "gjr-n", "gjr-t")
LABELS = {"rolling": "Rolling 250-day volatility, normal", "ewma": "EWMA λ = 0.94 (RiskMetrics), normal",
          "garch-n": "GARCH(1,1), normal (original)", "garch-t": "GARCH(1,1), Student-t",
          "gjr-n": "GJR-GARCH(1,1), normal", "gjr-t": "GJR-GARCH(1,1), Student-t (revised)"}


def load():
    with open(os.path.join(ROOT, "data", "french_daily.csv")) as f:
        rows = [r for r in csv.DictReader(f) if int(r["date"]) >= START]
    dates = np.array([int(r["date"]) for r in rows])
    r = np.array([float(r["mkt_rf"]) + float(r["rf"]) for r in rows])   # total market return, %
    return dates, r


def backtest(r, mu, sigma, q, test, stress_mask, p):
    var = mu + q * sigma                                     # (T,) VaR as a return threshold
    hits = (r < var)[test]
    lr_uc, p_uc = G.kupiec(hits, p)
    lr_cc, p_cc = G.christoffersen(hits, p)
    return {"breaches": int(hits.sum()), "days": int(hits.size), "rate": float(hits.mean()),
            "kupiec_p": p_uc, "christoffersen_p": p_cc,
            "stress_breaches": int((r < var)[stress_mask].sum()),
            "avg_var": float(np.mean(var[test]))}


def run():
    dates, r = load()
    train, test = dates < TEST_START, dates >= TEST_START
    stress = (dates >= STRESS[0]) & (dates < STRESS[1])
    rt = r[train]
    mu_train = float(rt.mean())
    out = {"meta": {"start": int(dates[0]), "train_end": int(dates[train][-1]),
                    "test_start": int(dates[test][0]), "end": int(dates[-1]),
                    "train_days": int(train.sum()), "test_days": int(test.sum()),
                    "stress_label": STRESS[2], "levels": LEVELS}, "models": {}}

    sigmas, params = {}, {}
    sigmas["rolling"] = G.rolling_sigma(r)
    sigmas["ewma"] = G.ewma_sigma(r - mu_train, s2_0=float(np.var(rt)))
    for name in FITTED:
        params[name] = G.fit(rt, name)
        sigmas[name] = G.forecast_sigma(params[name], r)

    for name, sigma in sigmas.items():
        p = params.get(name)
        entry = {"label": LABELS[name]}
        if p:
            entry["params"] = {k: (None if isinstance(v, float) and np.isinf(v) else v)
                               for k, v in p.items()}
            entry["test_neg_loglik_per_day"] = G.predictive_neg_loglik(p, r[test], sigma[test])
        else:
            gauss = {"mu": mu_train, "nu": np.inf}
            entry["test_neg_loglik_per_day"] = G.predictive_neg_loglik(gauss, r[test], sigma[test])
        entry["quantiles"] = {}
        for lv in LEVELS:
            q = G.quantile(p, lv) if p else G.norm_ppf(lv)
            entry["quantiles"][str(lv)] = q
            entry[f"var_{lv}"] = backtest(r, p["mu"] if p else mu_train, sigma, q, test, stress, lv)
        out["models"][name] = entry

    # Summary statistics of the data, for the paper's data section.
    out["data_stats"] = {}
    for name, m in (("train", train), ("test", test)):
        x = r[m]
        z = (x - x.mean()) / x.std()
        out["data_stats"][name] = {
            "days": int(m.sum()), "mean": float(x.mean()), "sd": float(x.std()),
            "ann_vol": float(x.std() * np.sqrt(252)), "skew": float(np.mean(z ** 3)),
            "kurtosis": float(np.mean(z ** 4)), "min": float(x.min()), "min_date": int(dates[m][x.argmin()]),
            "max": float(x.max()), "max_date": int(dates[m][x.argmax()]),
            "beyond_4sd": float(np.mean(np.abs(z) > 4)),
            "ac1_r": float(np.corrcoef(x[:-1], x[1:])[0, 1]),
            "ac1_r2": float(np.corrcoef(x[:-1] ** 2, x[1:] ** 2)[0, 1])}

    # Series for figures: the 2020 window and the fitted news-impact curves.
    w = (dates >= 20191001) & (dates < 20210101)
    out["window"] = {"dates": dates[w].tolist(), "returns": r[w].tolist()}
    for name in ("rolling", "garch-n", "gjr-t"):
        p = params.get(name)
        q = G.quantile(p, 0.01) if p else G.norm_ppf(0.01)
        out["window"][f"var_{name}"] = ((p["mu"] if p else mu_train) + q * sigmas[name][w]).tolist()
    return out


def to_markdown(res):
    m = res["meta"]
    lines = [f"Data: Kenneth R. French Data Library, daily US market return. Train "
             f"{m['start']}–{m['train_end']} ({m['train_days']} days); test "
             f"{m['test_start']}–{m['end']} ({m['test_days']} days).", "",
             "**Fitted parameters (train)**", "",
             "| Model | ω | α | γ | β | ν | Persistence | Half-life (days) | −log L | AIC | BIC |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in FITTED:
        p = res["models"][name]["params"]
        nu = "—" if p["nu"] is None else f"{p['nu']:.1f}"
        lines.append(f"| {res['models'][name]['label']} | {p['omega']:.4f} | {p['alpha']:.3f} | "
                     f"{p['gamma']:.3f} | {p['beta']:.3f} | {nu} | {p['persistence']:.4f} | "
                     f"{p['half_life_days']:.0f} | {p['neg_loglik']:.1f} | {p['aic']:.1f} | "
                     f"{p['bic']:.1f} |")
    for lv in m["levels"]:
        lines += ["", f"**{lv:.0%} Value-at-Risk backtest (test period; target breach rate {lv:.0%})**", "",
                  "| Model | Breaches | Breach rate | Kupiec p | Christoffersen p | "
                  f"{m['stress_label']} breaches | Avg VaR (%) |", "|---|---|---|---|---|---|---|"]
        for name, e in res["models"].items():
            b = e[f"var_{lv}"]
            lines.append(f"| {e['label']} | {b['breaches']}/{b['days']} | {b['rate']:.2%} | "
                         f"{b['kupiec_p']:.3f} | {b['christoffersen_p']:.3f} | "
                         f"{b['stress_breaches']} | {b['avg_var']:.2f} |")
    lines += ["", "**Out-of-sample fit** (average negative log-likelihood per test day; lower is better)", "",
              "| Model | −log L per day |", "|---|---|"]
    for name, e in res["models"].items():
        lines.append(f"| {e['label']} | {e['test_neg_loglik_per_day']:.4f} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    res = run()
    with open(os.path.join(ROOT, "results", "garch_results.json"), "w") as f:
        json.dump(res, f)
    md = to_markdown(res)
    with open(os.path.join(ROOT, "results", "garch_results.md"), "w") as f:
        f.write(md)
    print(md)
