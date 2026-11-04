"""GARCH(1,1) (original) and asymmetric, heavy-tailed GJR-GARCH(1,1) (revised). NumPy only.

Daily return model (percent):
    r_t = mu + e_t,   e_t = sigma_t z_t,   z_t i.i.d. with mean 0 and variance 1

Original, GARCH(1,1) (Bollerslev, 1986), Gaussian z_t:
    sigma_t^2 = omega + alpha e_{t-1}^2 + beta sigma_{t-1}^2

Revised, GJR-GARCH(1,1) (Glosten, Jagannathan & Runkle, 1993), standardized Student-t z_t
(Bollerslev, 1987):
    sigma_t^2 = omega + (alpha + gamma 1[e_{t-1} < 0]) e_{t-1}^2 + beta sigma_{t-1}^2
gamma > 0 lets a bad day raise tomorrow's variance more than a good day of the same size
("leverage effect"); the t distribution's nu < inf gives the crash days their real weight.

Constraints (positive variance, covariance stationarity under symmetric z):
    omega > 0, alpha, gamma, beta >= 0, alpha + gamma/2 + beta < 1.
They are enforced by a reparameterization so the hand-written Nelder-Mead can search freely.
"""
import math

import numpy as np

from optim import nelder_mead

MODELS = {           # name: (asymmetric?, student-t?)
    "garch-n": (False, False),
    "garch-t": (False, True),
    "gjr-n": (True, False),
    "gjr-t": (True, True),
}


# --- distributions -----------------------------------------------------------
def norm_ppf(p):
    """Standard normal quantile by bisection on the CDF (math.erf). Scalar p in (0, 1)."""
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def std_t_logpdf_const(nu):
    """log of the normalizing constant of the unit-variance Student-t (nu > 2)."""
    return math.lgamma((nu + 1) / 2) - math.lgamma(nu / 2) - 0.5 * math.log(math.pi * (nu - 2))


def std_t_ppf(p, nu, n=200_001):
    """Quantile of the unit-variance Student-t, p < 0.5, by numerical integration.

    Substituting x = tan(theta) maps the real line to (-pi/2, pi/2) and keeps the heavy
    tail finite, so a trapezoid rule on theta gives the CDF; we then invert by interpolation.
    """
    theta = np.linspace(-np.pi / 2 + 1e-9, 0.0, n)                       # (n,)
    x = np.tan(theta)
    pdf = np.exp(std_t_logpdf_const(nu) - (nu + 1) / 2 * np.log1p(x ** 2 / (nu - 2)))
    integrand = pdf / np.cos(theta) ** 2                                 # dx = sec^2 dtheta
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (integrand[1:] + integrand[:-1])
                                           * np.diff(theta))])
    cdf *= 0.5 / cdf[-1]           # exact symmetry: F(0) = 1/2 absorbs the tiny tail truncation
    return float(np.interp(p, cdf, x))


# --- variance recursion and likelihood ---------------------------------------
def variance_path(e, omega, alpha, gamma, beta, s2_0):
    """One-step-ahead conditional variances sigma_t^2 given e_1..e_{t-1}.

    e : (T,) demeaned returns; returns (T,) with s2[0] = s2_0.
    """
    T = e.shape[0]
    s2 = np.empty(T)
    s2[0] = s2_0
    neg = e < 0
    for t in range(1, T):
        s2[t] = omega + (alpha + gamma * neg[t - 1]) * e[t - 1] ** 2 + beta * s2[t - 1]
    return s2


def unpack(z, asym, student):
    """Map unconstrained z to (omega, alpha, gamma, beta, nu) satisfying the constraints."""
    omega = math.exp(z[0])
    e = np.exp(z[1:4] if asym else np.array([z[1], -np.inf, z[2]]))      # [a, g/2, b] weights
    den = 1.0 + e.sum()
    alpha, gamma, beta = e[0] / den, 2 * e[1] / den, e[2] / den           # alpha+gamma/2+beta<1
    nu = 2.0 + math.exp(z[-1]) if student else np.inf
    return omega, alpha, gamma, beta, nu


def neg_loglik(z, e, s2_0, asym, student):
    omega, alpha, gamma, beta, nu = unpack(z, asym, student)
    s2 = variance_path(e, omega, alpha, gamma, beta, s2_0)
    if student:
        ll = (std_t_logpdf_const(nu) - 0.5 * np.log(s2)
              - (nu + 1) / 2 * np.log1p(e ** 2 / (s2 * (nu - 2))))
    else:
        ll = -0.5 * (np.log(2 * np.pi) + np.log(s2) + e ** 2 / s2)
    return -float(np.sum(ll))


def fit(r, model, restarts=3):
    """Maximum-likelihood fit on returns r (T,). Returns a dict of parameters and fit statistics."""
    asym, student = MODELS[model]
    mu = float(np.mean(r))
    e = r - mu
    s2_0 = float(np.var(e))
    # Start near typical daily-equity values: persistence ~0.98, alpha ~0.08, nu ~6.
    z = [math.log(0.02 * s2_0), math.log(0.08 / 0.02)]
    z += [math.log(0.04 / 0.02), math.log(0.88 / 0.02)] if asym else [math.log(0.9 / 0.02)]
    z += [math.log(4.0)] if student else []
    z = np.array(z)
    best_f, step = np.inf, 0.5
    for _ in range(restarts):          # restart from the best point with a smaller simplex
        z, f, _ = nelder_mead(lambda q: neg_loglik(q, e, s2_0, asym, student), z, step=step,
                              tol=1e-10, max_iter=5000)
        if best_f - f < 1e-6:
            break
        best_f, step = f, step / 2
    omega, alpha, gamma, beta, nu = unpack(z, asym, student)
    k = 2 + (2 if asym else 1) + (1 if student else 0) + 1      # mu, omega, alpha, [gamma], beta, [nu]
    n = r.shape[0]
    persistence = alpha + gamma / 2 + beta
    return {"model": model, "mu": mu, "omega": omega, "alpha": alpha, "gamma": gamma,
            "beta": beta, "nu": nu, "s2_0": s2_0, "persistence": persistence,
            "half_life_days": math.log(0.5) / math.log(persistence),
            "long_run_vol": math.sqrt(omega / (1 - persistence)),
            "neg_loglik": best_f, "aic": 2 * best_f + 2 * k, "bic": 2 * best_f + k * math.log(n)}


def forecast_sigma(params, r):
    """One-step-ahead sigma_t over all of r, using parameters fitted on an earlier window."""
    e = r - params["mu"]
    return np.sqrt(variance_path(e, params["omega"], params["alpha"], params["gamma"],
                                 params["beta"], params["s2_0"]))


def quantile(params, p):
    """Lower-tail quantile of the standardized innovation z_t."""
    return norm_ppf(p) if math.isinf(params["nu"]) else std_t_ppf(p, params["nu"])


def predictive_neg_loglik(params, r, sigma):
    """Average out-of-sample negative log-likelihood per day (lower is better)."""
    e = r - params["mu"]
    if math.isinf(params["nu"]):
        ll = -0.5 * (np.log(2 * np.pi) + 2 * np.log(sigma) + (e / sigma) ** 2)
    else:
        nu = params["nu"]
        ll = (std_t_logpdf_const(nu) - np.log(sigma)
              - (nu + 1) / 2 * np.log1p((e / sigma) ** 2 / (nu - 2)))
    return float(-np.mean(ll))


# --- benchmarks ----------------------------------------------------------------
def rolling_sigma(r, window=250):
    """Naive benchmark: standard deviation of the previous `window` days. (T,), NaN at start."""
    T = r.shape[0]
    out = np.full(T, np.nan)
    c = np.concatenate([[0.0], np.cumsum(r)])
    c2 = np.concatenate([[0.0], np.cumsum(r ** 2)])
    t = np.arange(window, T)
    mean = (c[t] - c[t - window]) / window
    out[window:] = np.sqrt((c2[t] - c2[t - window]) / window - mean ** 2)
    return out


def ewma_sigma(r, lam=0.94, s2_0=None):
    """RiskMetrics (1996) EWMA: the GARCH special case omega = 0, alpha = 1 - lam, beta = lam."""
    e = r - r.mean() if s2_0 is None else r
    return np.sqrt(variance_path(e, 0.0, 1 - lam, 0.0, lam,
                                 float(np.var(e)) if s2_0 is None else s2_0))


# --- backtests -------------------------------------------------------------------
def _xlogy(k, p):
    return 0.0 if k == 0 else k * math.log(p)


def kupiec(hits, p):
    """Unconditional coverage LR test (Kupiec, 1995). hits: (n,) bool. Returns (LR, p-value)."""
    n, k = hits.size, int(hits.sum())
    phat = k / n
    lr = -2 * (_xlogy(n - k, 1 - p) + _xlogy(k, p) - _xlogy(n - k, 1 - phat) - _xlogy(k, phat))
    return lr, math.erfc(math.sqrt(max(lr, 0) / 2))          # chi-square(1) tail


def christoffersen(hits, p):
    """Conditional coverage = unconditional + independence of breaches (Christoffersen, 1998)."""
    h = hits.astype(int)
    a, b = h[:-1], h[1:]
    n00, n01 = int(np.sum((a == 0) & (b == 0))), int(np.sum((a == 0) & (b == 1)))
    n10, n11 = int(np.sum((a == 1) & (b == 0))), int(np.sum((a == 1) & (b == 1)))
    p01 = n01 / max(n00 + n01, 1)
    p11 = n11 / max(n10 + n11, 1)
    p1 = (n01 + n11) / max(n00 + n01 + n10 + n11, 1)
    lr_ind = -2 * (_xlogy(n00 + n10, 1 - p1) + _xlogy(n01 + n11, p1)
                   - _xlogy(n00, 1 - p01) - _xlogy(n01, p01)
                   - _xlogy(n10, 1 - p11) - _xlogy(n11, p11))
    lr_uc, _ = kupiec(hits, p)
    lr_cc = lr_uc + lr_ind
    return lr_cc, math.exp(-lr_cc / 2)                         # chi-square(2) tail
