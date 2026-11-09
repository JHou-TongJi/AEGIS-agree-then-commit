"""Conformal risk control (Angelopoulos et al., 2024) for a monotone commit rule.

Units are exchangeable groups (documents, or conditions); the loss of a unit at threshold lam
is the share of its items that are committed *and* wrong.  The calibrated threshold is the
smallest lam with  (n/(n+1)) * mean_i L_i(lam) + B/(n+1) <= alpha,  B = 1.
"""
import numpy as np


def calibrate(unit_losses, lams, alpha, B=1.0):
    """unit_losses: array (n_units, n_lams), non-increasing in lam. Returns lam_hat or None."""
    L = np.asarray(unit_losses, float)
    n = L.shape[0]
    bound = n / (n + 1) * L.mean(0) + B / (n + 1)
    ok = np.where(bound <= alpha)[0]
    return None if len(ok) == 0 else lams[ok[0]]


def min_feasible_alpha(n, B=1.0):
    return B / (n + 1)
