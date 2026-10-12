"""Revised model: Huber M-estimation via Iteratively Reweighted Least Squares (IRLS).

Derivation (see paper Section 5):
    rho_d(u) = u^2 / 2               if |u| <= d
             = d|u| - d^2 / 2        otherwise
    psi_d(u) = rho_d'(u) = clip(u, -d, d)
Setting sum_i psi_d(r_i / s) x_i = 0 and writing psi_d(u) = w(u) u gives
    w_i = min(1, d / |r_i / s|)
    beta <- (X^T W X)^{-1} X^T W y
which is a weighted least-squares solve repeated until beta stops moving.
The scale s is re-estimated each step with the normalized MAD, so the
threshold d = 1.345 keeps ~95% efficiency under Gaussian noise.
"""
import numpy as np

from baseline import add_intercept

MAD_TO_SIGMA = 1.4826  # 1 / Phi^{-1}(0.75)


def robust_scale(r):
    """Normalized median absolute deviation of residuals r: (n,) -> float."""
    s = MAD_TO_SIGMA * np.median(np.abs(r - np.median(r)))
    return max(s, 1e-12)                               # guard against s = 0


def huber_weights(u, delta):
    """w(u) = min(1, delta / |u|), with |u| clipped away from 0.  u: (n,) -> (n,)"""
    return np.minimum(1.0, delta / np.maximum(np.abs(u), 1e-12))


def huber_fit(X, y, delta=1.345, max_iter=100, tol=1e-8, beta0=None):
    """Huber regression by IRLS.

    X : (n, p) features (no intercept), y : (n,)
    returns beta : (p + 1,), info : dict(iterations, weights, scale)
    """
    Xd = add_intercept(X)                              # (n, p+1)
    if beta0 is None:
        beta0, *_ = np.linalg.lstsq(Xd, y, rcond=None) # OLS warm start
    beta = beta0.copy()
    for it in range(1, max_iter + 1):
        r = y - Xd @ beta                              # (n,)
        s = robust_scale(r)
        w = huber_weights(r / s, delta)                # (n,)
        sw = np.sqrt(w)[:, None]                       # (n, 1)
        # Weighted LS as an ordinary LS on rescaled rows: avoids forming X^T W X.
        beta_new, *_ = np.linalg.lstsq(sw * Xd, sw[:, 0] * y, rcond=None)
        if np.linalg.norm(beta_new - beta) <= tol * (1 + np.linalg.norm(beta)):
            beta = beta_new
            break
        beta = beta_new
    return beta, {"iterations": it, "weights": w, "scale": s}
