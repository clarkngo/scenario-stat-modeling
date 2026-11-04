# scenario-stat-modeling

**Forecasting Market Risk from Scratch: Revising GARCH into an Asymmetric, Heavy-Tailed Model for Value-at-Risk**
Clark Jason Ngo & Manas Teja Katakam · DS 623 Math and Statistics for Data Science · City University of Seattle

> **Status:** Draft 1 submitted. The portal, slides and paper body show working drafts built from our prototype results on real data.

We derive GARCH(1,1) from first principles, implement it and its maximum-likelihood fitting in NumPy, test it as a daily Value-at-Risk model on real US market returns, and revise the two assumptions that fail (equal reaction to good and bad news, and normal shocks) into GJR-GARCH with Student-t errors. The portal's lab replays the 2020 crash and other periods in the browser.

- Portal: https://clarkngo.github.io/scenario-stat-modeling/
- Slides: https://clarkngo.github.io/scenario-stat-modeling/presentations/ds623-scenario-stat-modeling.html
- Study guide (terms, our numbers, likely questions): https://clarkngo.github.io/scenario-stat-modeling/presentations/defense-guide.html

## GARCH study (chosen project direction)

We forecast **how wild tomorrow's stock market could be**. The original model is **GARCH(1,1) with normal errors**. The revised model is **GJR-GARCH(1,1) with Student-t errors**, which lets bad days raise risk more than good days and allows for crash-sized moves. Both models are fitted by maximum likelihood with a hand-written Nelder–Mead optimizer in NumPy. We judge them with **Value-at-Risk backtests** on real daily US market returns from the Kenneth R. French Data Library: we fit on 1990–2014 and test on 2015–Aug 2026, which includes the 2020 COVID crash.

| Path | What it is |
|---|---|
| `model/garch.py` | GARCH / GJR-GARCH, normal and Student-t likelihoods, quantiles, EWMA and rolling benchmarks, Kupiec and Christoffersen tests |
| `model/optim.py` | Nelder–Mead simplex optimizer (shared by the GARCH and Kalman code) |
| `model/run_garch.py` | Train/test backtest → `results/garch_results.{json,md}` |
| `model/test_garch.py` | Sanity checks; for example, the MLE recovers the parameters of simulated data |
| `tools/make_garch_figures.py` | `assets/fig_garch_covid.png`, `assets/fig_garch_news.png` |

```bash
make garch    # fit, backtest and draw the figures
```

Key results on the test period: the revised model has the best out-of-sample fit (−log L per day 1.287 vs 1.337). It also breaks its 1% limit only 2 times during Feb–Apr 2020, against 6 for the original and 12 for the naive past-year rule. The fitted α is near 0 while γ ≈ 0.14, so in this data only bad days push risk up.

## Kalman prototype (backup direction)

The course excludes regression as the main model, so we're proposing a **Kalman filter for a stock industry's time-varying beta**, revised into a **robust Kalman filter** that applies a Huber M-estimation update. It runs on real monthly data from the Kenneth R. French Data Library (1963–2026). We kept it as a backup after choosing GARCH.

| Path | What it is |
|---|---|
| `model/kalman.py` | Kalman filter, Huber-robust filter, MLE of noise variances, and Nelder–Mead, all from scratch in NumPy |
| `model/run_kalman.py` | Real-data experiment across 12 industries → `results/kalman_results.{json,md}` |
| `model/test_kalman.py` | Sanity checks; for example, with no drift the filter reproduces OLS exactly |
| `tools/fetch_french.py` | Downloads and cleans the French data → `data/french_monthly.csv` |
| `tools/make_kalman_figures.py` | `assets/fig_kalman_beta.png`, `assets/fig_kalman_inject.png` |

```bash
make kalman   # run the experiment and figures
make data     # re-download the latest French data
```

## Layout

| Path | What it is |
|---|---|
| `model/baseline.py`, `model/revised.py`, `model/scenario.py`, `model/run_experiment.py` | Earlier OLS → Huber prototype on synthetic data (kept for reference; not used by the portal) |
| `paper/content.json` | **Single source of paper text**, used by the portal, DOCX, and PPTX |
| `index.html`, `style.css`, `script.js` | GitHub Pages portal: MathJax paper, in-browser Value-at-Risk lab on the real data, code tabs |
| `presentations/ds623-scenario-stat-modeling.html` | HTML slide deck (←/→, F for fullscreen) |
| `tools/build_docx.py` | Word paper in the course-paper format (2-column body, APA tables/figures), built per draft stage |
| `tools/build_pptx.py` | PowerPoint deck |
| `tools/make_figures.py` | Paper figures (matplotlib is used for plotting only) |

## Build locally

```bash
make all      # tests, experiment, figures, build/scenario-stat-modeling.docx and .pptx
make serve    # http://localhost:8623 (the portal fetches JSON, so open it over HTTP, not file://)
```

### Paper drafts

The course requires two drafts before the final paper. Sections and references in `paper/content.json` each carry a `stage` (1 = Draft 1, 2 = Draft 2, 3 = Final Paper), and `draft.stage` sets the current one.

- **Draft 1:** title block, abstract, keywords, and references (front matter only).
- **Draft 2:** adds the two-column body. Sections due later appear as a heading, a "to be completed" note, and their planned subsections.
- **Final Paper:** all sections plus the code appendices.

```bash
python3 tools/build_docx.py             # current stage -> build/scenario-stat-modeling-draft1.docx
python3 tools/build_docx.py --stage 2   # preview a later stage
```

Requires Python 3 with `numpy`, `matplotlib`, `python-docx`, and `python-pptx`. Pushing to `main` deploys the site through `.github/workflows/static.yml`.
