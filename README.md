# scenario-stat-modeling

**Scenario-Driven Statistical Modeling: An AI-Guided Framework for Deriving and Revising Algorithmic Baselines from Scratch**
Clark Jason Ngo · DS 623 Math and Statistics for Data Science · City University of Seattle

> **Status: working prototype.** The pipeline, web portal, slides, and document builders work end to end. The section text is a first draft, and the experiment uses synthetic data with known ground truth.

The framework has five stages: **Derive → Implement → Shock → Diagnose → Revise.** The worked case derives OLS regression, shocks it with a unit-entry data error (×10 prices), traces the failure to the squared-error loss, and revises the model into Huber regression solved by IRLS. Both models use pure NumPy, with no scikit-learn, PyTorch, or SciPy fitting.

- Portal: https://clarkngo.github.io/scenario-stat-modeling/
- Slides: https://clarkngo.github.io/scenario-stat-modeling/presentations/ds623-scenario-stat-modeling.html

## Layout

| Path | What it is |
|---|---|
| `model/baseline.py` | OLS (closed form + gradient descent), NumPy only |
| `model/revised.py` | Huber M-estimator via IRLS, NumPy only |
| `model/scenario.py` | Data generator and scenario shock |
| `model/run_experiment.py` | Monte Carlo sweep → `results/results.json`, `results/results.md` |
| `paper/content.json` | **Single source of paper text**, used by the portal, DOCX, and PPTX |
| `index.html`, `style.css`, `script.js` | GitHub Pages portal: MathJax paper, in-browser lab, code tabs |
| `presentations/ds623-scenario-stat-modeling.html` | HTML slide deck (←/→, F for fullscreen) |
| `tools/build_docx.py` | Word paper in the course-paper format (2-column body, APA tables/figures) |
| `tools/build_pptx.py` | PowerPoint deck |
| `tools/make_figures.py` | Paper figures (matplotlib is used for plotting only) |

## Build locally

```bash
make all      # tests, experiment, figures, build/scenario-stat-modeling.docx and .pptx
make serve    # http://localhost:8623 (the portal fetches JSON, so open it over HTTP, not file://)
```

Requires Python 3 with `numpy`, `matplotlib`, `python-docx`, and `python-pptx`. Pushing to `main` deploys the site through `.github/workflows/static.yml`.
