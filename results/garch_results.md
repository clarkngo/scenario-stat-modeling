Data: Kenneth R. French Data Library, daily US market return. Train 19900102–20141231 (6301 days); test 20150102–20260831 (2932 days).

**Fitted parameters (train)**

| Model | ω | α | γ | β | ν | Persistence | Half-life (days) | −log L | AIC | BIC |
|---|---|---|---|---|---|---|---|---|---|---|
| GARCH(1,1), normal (original) | 0.0123 | 0.084 | 0.000 | 0.906 | — | 0.9898 | 67 | 8395.6 | 16799.2 | 16826.1 |
| GARCH(1,1), Student-t | 0.0072 | 0.074 | 0.000 | 0.922 | 7.1 | 0.9959 | 168 | 8283.5 | 16577.0 | 16610.7 |
| GJR-GARCH(1,1), normal | 0.0160 | 0.005 | 0.137 | 0.909 | — | 0.9828 | 40 | 8295.2 | 16600.4 | 16634.2 |
| GJR-GARCH(1,1), Student-t (revised) | 0.0116 | 0.001 | 0.141 | 0.918 | 8.0 | 0.9892 | 64 | 8199.5 | 16411.0 | 16451.5 |

**1% Value-at-Risk backtest (test period; target breach rate 1%)**

| Model | Breaches | Breach rate | Kupiec p | Christoffersen p | Feb–Apr 2020 (COVID crash) breaches | Avg VaR (%) |
|---|---|---|---|---|---|---|
| Rolling 250-day volatility, normal | 76/2932 | 2.59% | 0.000 | 0.000 | 12 | -2.43 |
| EWMA λ = 0.94 (RiskMetrics), normal | 67/2932 | 2.29% | 0.000 | 0.000 | 6 | -2.26 |
| GARCH(1,1), normal (original) | 60/2932 | 2.05% | 0.000 | 0.000 | 6 | -2.28 |
| GARCH(1,1), Student-t | 56/2932 | 1.91% | 0.000 | 0.000 | 6 | -2.51 |
| GJR-GARCH(1,1), normal | 58/2932 | 1.98% | 0.000 | 0.000 | 5 | -2.26 |
| GJR-GARCH(1,1), Student-t (revised) | 51/2932 | 1.74% | 0.000 | 0.000 | 2 | -2.47 |

**5% Value-at-Risk backtest (test period; target breach rate 5%)**

| Model | Breaches | Breach rate | Kupiec p | Christoffersen p | Feb–Apr 2020 (COVID crash) breaches | Avg VaR (%) |
|---|---|---|---|---|---|---|
| Rolling 250-day volatility, normal | 161/2932 | 5.49% | 0.229 | 0.000 | 14 | -1.71 |
| EWMA λ = 0.94 (RiskMetrics), normal | 180/2932 | 6.14% | 0.006 | 0.002 | 8 | -1.58 |
| GARCH(1,1), normal (original) | 163/2932 | 5.56% | 0.172 | 0.167 | 6 | -1.60 |
| GARCH(1,1), Student-t | 172/2932 | 5.87% | 0.036 | 0.020 | 7 | -1.58 |
| GJR-GARCH(1,1), normal | 149/2932 | 5.08% | 0.839 | 0.456 | 7 | -1.59 |
| GJR-GARCH(1,1), Student-t (revised) | 154/2932 | 5.25% | 0.534 | 0.325 | 7 | -1.57 |

**Out-of-sample fit** (average negative log-likelihood per test day; lower is better)

| Model | −log L per day |
|---|---|
| Rolling 250-day volatility, normal | 1.5163 |
| EWMA λ = 0.94 (RiskMetrics), normal | 1.3598 |
| GARCH(1,1), normal (original) | 1.3370 |
| GARCH(1,1), Student-t | 1.3080 |
| GJR-GARCH(1,1), normal | 1.3156 |
| GJR-GARCH(1,1), Student-t (revised) | 1.2867 |
