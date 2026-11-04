"""Sanity checks for model/kalman.py: run with  python3 model/test_kalman.py"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from kalman import kalman_filter, fit_mle, nelder_mead  # noqa: E402

rng = np.random.default_rng(1)

# 1. With no state noise and a diffuse prior, the filter is recursive least squares:
#    its final state equals the full-sample OLS fit.
T = 400
m = rng.normal(0, 4, T)
y = 0.3 + 1.2 * m + rng.normal(0, 2, T)
f = kalman_filter(y, m, q=np.zeros(2), r=4.0, p0=1e8)
X = np.column_stack([np.ones(T), m])
ols, *_ = np.linalg.lstsq(X, y, rcond=None)
assert np.allclose(f["theta_filt"][-1], ols, atol=1e-4), (f["theta_filt"][-1], ols)

# 2. The robust filter with c = inf is exactly the Gaussian filter.
g = kalman_filter(y, m, q=np.array([0.01, 0.001]), r=4.0)
h = kalman_filter(y, m, q=np.array([0.01, 0.001]), r=4.0, c=np.inf)
assert np.array_equal(g["theta_filt"], h["theta_filt"])

# 3. Nelder-Mead finds the minimum of a shifted quadratic.
x, fx, _ = nelder_mead(lambda z: np.sum((z - np.array([1.0, -2.0, 0.5])) ** 2), np.zeros(3))
assert np.allclose(x, [1.0, -2.0, 0.5], atol=1e-2) and fx < 1e-4

# 4. MLE recovers the noise variances of a simulated drifting-beta series (order of magnitude).
T = 1500
m = rng.normal(0, 4, T)
beta = 1.0 + np.cumsum(rng.normal(0, np.sqrt(0.002), T))
y = 0.1 + beta * m + rng.normal(0, 2, T)
q, r, _ = fit_mle(y, m)
assert 2.5 < r < 6.0, r
assert 0.0005 < q[1] < 0.008, q

# 5. A single gross error moves the robust beta far less than the Gaussian beta.
y_bad = y.copy()
y_bad[800] += 60
d_g = np.abs(kalman_filter(y_bad, m, q, r)["theta_filt"][800, 1]
             - kalman_filter(y, m, q, r)["theta_filt"][800, 1])
d_r = np.abs(kalman_filter(y_bad, m, q, r, c=1.345)["theta_filt"][800, 1]
             - kalman_filter(y, m, q, r, c=1.345)["theta_filt"][800, 1])
assert d_r < d_g / 3, (d_r, d_g)

print("all kalman tests passed")
