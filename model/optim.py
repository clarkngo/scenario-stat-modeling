"""Hand-written optimizer shared by the models (NumPy only, no SciPy)."""
import numpy as np


def nelder_mead(fun, x0, step=1.0, tol=1e-6, max_iter=2000):
    """Derivative-free minimizer (Nelder & Mead, 1965), written from scratch.

    x0 : (d,) start; returns (x_best, f_best, n_iter)
    """
    d = x0.shape[0]
    simplex = np.vstack([x0] + [x0 + step * np.eye(d)[i] for i in range(d)])   # (d+1, d)
    fvals = np.array([fun(x) for x in simplex])
    for it in range(1, max_iter + 1):
        order = np.argsort(fvals)
        simplex, fvals = simplex[order], fvals[order]
        if np.abs(fvals[-1] - fvals[0]) <= tol * (1 + np.abs(fvals[0])):
            break
        centroid = simplex[:-1].mean(axis=0)
        xr = centroid + (centroid - simplex[-1])                   # reflect
        fr = fun(xr)
        if fr < fvals[0]:
            xe = centroid + 2 * (centroid - simplex[-1])           # expand
            fe = fun(xe)
            simplex[-1], fvals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < fvals[-2]:
            simplex[-1], fvals[-1] = xr, fr
        else:
            xc = centroid + 0.5 * (simplex[-1] - centroid)         # contract
            fc = fun(xc)
            if fc < fvals[-1]:
                simplex[-1], fvals[-1] = xc, fc
            else:                                                  # shrink toward best
                simplex[1:] = simplex[0] + 0.5 * (simplex[1:] - simplex[0])
                fvals[1:] = np.array([fun(x) for x in simplex[1:]])
    best = np.argmin(fvals)
    return simplex[best], fvals[best], it
