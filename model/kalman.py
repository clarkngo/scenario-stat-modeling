"""Time-varying CAPM beta with a Kalman filter, and a robust (Huber) revision. NumPy only.

State-space model (monthly, returns in percent):
    observation   y_t     = H_t theta_t + eps_t,    eps_t ~ N(0, R),  H_t = [1, m_t]   (1, 2)
    state         theta_t = theta_{t-1} + eta_t,    eta_t ~ N(0, Q),  Q = diag(q_a, q_b)
where y_t is an industry's excess return, m_t the market excess return and
theta_t = [alpha_t, beta_t]. "How much does this industry move when the market moves 1%?"
is beta_t, and the random walk lets that answer drift over time.

Original filter (Gaussian): the textbook predict/update recursion. Its update moves the
state in proportion to the surprise v_t, so one extreme month can move beta arbitrarily far.

Revised filter (Huber): standardize the surprise u_t = v_t / sqrt(S_t) and replace it with
psi_c(u_t) = clip(u_t, -c, c). The covariance shrinks only when the month is "believable"
(psi_c'(u_t) = 1), following Masreliez & Martin (1977). With c = inf it is the original filter.
"""
import numpy as np

from optim import nelder_mead  # noqa: F401  (re-exported for tests)

HUBER_C = 1.345  # 95% efficiency under Gaussian surprises


def kalman_filter(y, m, q, r, c=np.inf, theta0=None, p0=1e4):
    """Run the (optionally robust) Kalman filter.

    y, m : (T,) industry and market excess returns
    q    : (2,) state noise variances [q_alpha, q_beta]
    r    : observation noise variance
    c    : Huber threshold on standardized surprises (np.inf -> Gaussian filter)
    returns dict with
        theta_pred (T, 2) one-step-ahead state  E[theta_t | y_1..t-1]
        theta_filt (T, 2) filtered state        E[theta_t | y_1..t]
        v (T,) surprises, S (T,) their variances, clipped (T,) bool
    """
    T = y.shape[0]
    Q = np.diag(q)                                         # (2, 2)
    theta = np.zeros(2) if theta0 is None else np.asarray(theta0, float)
    P = np.eye(2) * p0                                     # (2, 2) diffuse prior
    out_pred, out_filt = np.empty((T, 2)), np.empty((T, 2))
    v_all, S_all, clipped = np.empty(T), np.empty(T), np.zeros(T, bool)
    for t in range(T):
        # Predict: random walk keeps the mean, adds uncertainty.
        P = P + Q
        H = np.array([1.0, m[t]])                          # (2,)
        out_pred[t] = theta
        # Surprise and its variance.
        v = y[t] - H @ theta
        PH = P @ H                                         # (2,)
        S = H @ PH + r
        K = PH / S                                         # (2,) Kalman gain
        u = v / np.sqrt(S)
        if abs(u) <= c:
            theta = theta + K * v
            P = P - np.outer(K, PH)                        # = P - K S K^T
        else:
            # Bounded influence: move as if the surprise were c standard deviations,
            # and learn nothing about uncertainty from an unbelievable month.
            theta = theta + K * np.sqrt(S) * c * np.sign(u)
            clipped[t] = True
        P = 0.5 * (P + P.T)                                # keep symmetric
        out_filt[t], v_all[t], S_all[t] = theta, v, S
    return {"theta_pred": out_pred, "theta_filt": out_filt, "v": v_all, "S": S_all,
            "clipped": clipped}


def neg_loglik(log_params, y, m, burn=24):
    """Gaussian prediction-error log-likelihood (negated). log_params = log[q_a, q_b, r]."""
    q_a, q_b, r = np.exp(log_params)
    f = kalman_filter(y, m, np.array([q_a, q_b]), r)
    v, S = f["v"][burn:], f["S"][burn:]
    return 0.5 * np.sum(np.log(2 * np.pi * S) + v ** 2 / S)


def fit_mle(y, m, x0=None):
    """Maximum-likelihood q_a, q_b, r for the Gaussian filter. Returns (q (2,), r, info)."""
    if x0 is None:
        x0 = np.log(np.array([0.01, 0.001, np.var(y)]))
    x, f, it = nelder_mead(lambda p: neg_loglik(p, y, m), x0)
    q_a, q_b, r = np.exp(x)
    return np.array([q_a, q_b]), r, {"neg_loglik": float(f), "iterations": it}


def rolling_ols_beta(y, m, window=60):
    """Benchmark used by practitioners: OLS beta over the trailing `window` months. (T,)"""
    T = y.shape[0]
    beta = np.full(T, np.nan)
    for t in range(window, T):
        mm, yy = m[t - window:t], y[t - window:t]
        mc = mm - mm.mean()
        beta[t] = (mc @ (yy - yy.mean())) / (mc @ mc)
    return beta
