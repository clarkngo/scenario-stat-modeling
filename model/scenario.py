"""Scenario generator: a housing-price baseline and a data-entry "scenario shock".

Baseline world:   price = b0 + b1 * size + b2 * age + eps,  eps ~ N(0, sigma^2)
Scenario shock:   a fraction `contamination` of TRAINING rows is corrupted by a
                  unit-entry error (price recorded x10) -- a gross vertical outlier.
The TEST set is always clean: we ask how well each estimator recovers the
true market relationship after learning from shocked data.

PROTOTYPE NOTE: data are synthetic with known ground truth so estimator
bias can be measured exactly. The full paper will add a real dataset.
"""
import numpy as np

TRUE_BETA = np.array([300.0, 85.0, -20.0])  # intercept, size (std), age (std); $1000s
NOISE_SD = 40.0


def make_data(n, rng):
    """Return standardized features X: (n, 2) and clean response y: (n,)."""
    X = rng.standard_normal((n, 2))                       # (n, 2)
    y = TRUE_BETA[0] + X @ TRUE_BETA[1:] + rng.normal(0, NOISE_SD, n)
    return X, y


def apply_shock(y, contamination, rng, factor=10.0):
    """Multiply a random `contamination` share of y by `factor`.

    returns y_shocked : (n,), mask : (n,) bool of corrupted rows
    """
    n = y.shape[0]
    k = int(round(contamination * n))
    mask = np.zeros(n, dtype=bool)
    mask[rng.choice(n, size=k, replace=False)] = True
    y_shocked = y.copy()
    y_shocked[mask] *= factor
    return y_shocked, mask
