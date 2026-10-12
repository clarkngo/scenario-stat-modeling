"""Original model: Ordinary Least Squares (OLS) linear regression in pure NumPy.

Derivation (see paper Section 2):
    L(beta) = (1/2n) * ||y - X beta||^2
    grad L  = -(1/n) X^T (y - X beta) = 0   =>   X^T X beta = X^T y
We solve the normal equations with a Cholesky-free, numerically stable
least-squares solve (np.linalg.lstsq uses an SVD under the hood) and also
offer batch gradient descent so students can watch the loss converge.
"""
import numpy as np


def add_intercept(X):
    """Prepend a column of ones.  X: (n, p) -> (n, p + 1)."""
    return np.hstack([np.ones((X.shape[0], 1)), X])


def ols_fit(X, y):
    """Closed-form OLS.

    X : (n, p) feature matrix (no intercept column)
    y : (n,)   response
    returns beta : (p + 1,) with beta[0] the intercept
    """
    Xd = add_intercept(X)                              # (n, p+1)
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)      # (p+1,)
    return beta


def ols_fit_gd(X, y, lr=0.1, n_iter=2000, tol=1e-10):
    """Batch gradient descent on the mean-squared-error loss.

    Assumes standardized features so a fixed learning rate converges.
    returns beta : (p + 1,), losses : list[float]
    """
    Xd = add_intercept(X)                              # (n, p+1)
    n = Xd.shape[0]
    beta = np.zeros(Xd.shape[1])                       # (p+1,)
    losses = []
    for _ in range(n_iter):
        r = y - Xd @ beta                              # (n,)
        losses.append(0.5 * np.mean(r ** 2))
        grad = -(Xd.T @ r) / n                         # (p+1,)
        beta -= lr * grad
        if np.linalg.norm(grad) < tol:
            break
    return beta, losses


def predict(beta, X):
    """X: (n, p), beta: (p + 1,) -> (n,)"""
    return add_intercept(X) @ beta
