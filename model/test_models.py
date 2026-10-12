"""Sanity checks: run with  python3 model/test_models.py"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from baseline import ols_fit, ols_fit_gd    # noqa: E402
from revised import huber_fit, huber_weights  # noqa: E402
from scenario import make_data, apply_shock, TRUE_BETA  # noqa: E402

rng = np.random.default_rng(0)
X, y = make_data(2000, rng)

# 1. Closed form and gradient descent agree.
b_cf = ols_fit(X, y)
b_gd, losses = ols_fit_gd(X, y)
assert np.allclose(b_cf, b_gd, atol=1e-4), (b_cf, b_gd)
assert losses[-1] <= losses[0]

# 2. On clean data both estimators recover the truth.
b_h, _ = huber_fit(X, y)
assert np.linalg.norm(b_cf - TRUE_BETA) < 5
assert np.linalg.norm(b_h - TRUE_BETA) < 5

# 3. Huber weights: 1 inside the threshold, delta/|u| outside.
w = huber_weights(np.array([0.0, 1.0, -2.69, 13.45]), 1.345)
assert np.allclose(w, [1, 1, 0.5, 0.1])

# 4. Under a 20% shock Huber beats OLS on coefficient error.
ys, mask = apply_shock(y, 0.2, rng)
assert mask.sum() == 400
e_ols = np.linalg.norm(ols_fit(X, ys) - TRUE_BETA)
e_hub = np.linalg.norm(huber_fit(X, ys)[0] - TRUE_BETA)
assert e_hub < e_ols, (e_hub, e_ols)

print("all tests passed")
