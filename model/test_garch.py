"""Sanity checks for model/garch.py: run with  python3 model/test_garch.py"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from garch import (fit, kupiec, norm_ppf, std_t_ppf, unpack, variance_path,  # noqa: E402
                   neg_loglik, rolling_sigma)

# 1. Quantiles match published table values.
assert abs(norm_ppf(0.01) - (-2.3263478740)) < 1e-8
assert abs(norm_ppf(0.05) - (-1.6448536270)) < 1e-8
assert abs(std_t_ppf(0.01, 5.0) - (-3.364930 * math.sqrt(3 / 5))) < 1e-3   # t_5 table value
assert abs(std_t_ppf(0.01, 1e6) - norm_ppf(0.01)) < 1e-3                  # t -> normal

# 2. Reparameterization always satisfies the constraints.
rng = np.random.default_rng(3)
for _ in range(1000):
    o, a, g, b, nu = unpack(rng.normal(0, 3, 5), True, True)
    assert o > 0 and a >= 0 and g >= 0 and b >= 0 and a + g / 2 + b < 1 and nu > 2

# 3. GJR with gamma = 0 is plain GARCH.
e = rng.normal(0, 1, 500)
assert np.allclose(variance_path(e, 0.05, 0.1, 0.0, 0.85, 1.0),
                   variance_path(np.abs(e), 0.05, 0.1, 0.0, 0.85, 1.0))

# 4. MLE recovers the parameters of a simulated GJR-t series.
T, (omega, alpha, gamma, beta, nu) = 8000, (0.02, 0.03, 0.12, 0.88, 6.0)
z = rng.standard_t(nu, T) * math.sqrt((nu - 2) / nu)
r, s2 = np.empty(T), omega / (1 - alpha - gamma / 2 - beta)
for t in range(T):
    r[t] = math.sqrt(s2) * z[t]
    s2 = omega + (alpha + gamma * (r[t] < 0)) * r[t] ** 2 + beta * s2
p = fit(r, "gjr-t")
assert abs(p["gamma"] - gamma) < 0.04 and abs(p["beta"] - beta) < 0.03, p
assert abs(p["alpha"] - alpha) < 0.03 and 4.5 < p["nu"] < 8.5, p
# ...and the richer model fits this data better than plain Gaussian GARCH.
assert p["neg_loglik"] < fit(r, "garch-n")["neg_loglik"]

# 5. Kupiec test: exact coverage gives LR = 0; double the breaches is rejected.
hits = np.zeros(1000, bool)
hits[:10] = True
assert abs(kupiec(hits, 0.01)[0]) < 1e-12
hits[:20] = True
assert kupiec(hits, 0.01)[1] < 0.01

# 6. Rolling volatility equals a direct computation.
x = rng.normal(0, 2, 400)
assert abs(rolling_sigma(x, 250)[300] - np.std(x[50:300])) < 1e-10

print("all garch tests passed")
