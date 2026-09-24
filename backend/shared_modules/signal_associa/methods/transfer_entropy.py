"""
Associa — Transfer Entropy
============================
Measures directed information transfer from signal_x to signal_y.

TE(X→Y) = H(Y_future | Y_past) - H(Y_future | Y_past, X_past)

If X contains information about Y's future that Y's own past doesn't,
TE is positive → X drives Y.

Directional: TE(X→Y) ≠ TE(Y→X).

Estimation methods (in order of preference):
  1. pyinform (C-based, fast, well-validated) — requires discretization
  2. kNN (Kraskov-Stögbauer-Grassberger) — works on continuous data,
     implemented via scipy.spatial.cKDTree

TE can work on both raw and stationary signals — it is more robust than
GC to non-stationarity but benefits from stationarization.
"""

import numpy as np
from typing import Dict, Optional

# Check for pyinform availability at import time
try:
    from pyinform import transfer_entropy as _pyinform_te
    _HAS_PYINFORM = True
except ImportError:
    _HAS_PYINFORM = False


def transfer_entropy(signal_x: np.ndarray, signal_y: np.ndarray,
                     config: Optional[Dict] = None) -> Dict:
    """
    Transfer Entropy from X to Y (and optionally Y to X).

    Parameters
    ----------
    signal_x, signal_y : 1-D arrays (same length)
    config : optional dict with:
        lag       : int (default 1) — history length
        k         : int (default 1) — prediction horizon
        bins      : int (default 16) — discretization bins for pyinform
        method    : str (default 'auto') — 'pyinform', 'knn', or 'auto'
        bidirectional : bool (default True)

    Returns
    -------
    dict with: method, statistic (TE X→Y), p_value, direction, details
    """
    cfg = config or {}
    lag = cfg.get('lag', 1)
    k_horizon = cfg.get('k', 1)
    bins = cfg.get('bins', 16)
    method = cfg.get('method', 'auto')
    bidir = cfg.get('bidirectional', True)

    x = np.asarray(signal_x, dtype=np.float64).ravel()
    y = np.asarray(signal_y, dtype=np.float64).ravel()

    n = min(len(x), len(y))
    min_len = lag + k_horizon + 10
    if n < min_len:
        return {'method': 'transfer_entropy',
                'error': f'Signals too short ({n} < {min_len})'}
    x, y = x[:n], y[:n]

    # Select estimation method
    if method == 'auto':
        method = 'pyinform' if _HAS_PYINFORM else 'knn'

    try:
        if method == 'pyinform':
            te_xy, te_yx = _te_pyinform(x, y, lag, k_horizon, bins, bidir)
            estimation_label = f'pyinform(bins={bins})'
        elif method == 'knn':
            te_xy = _te_knn(x, y, lag, k_horizon)
            te_yx = _te_knn(y, x, lag, k_horizon) if bidir else np.nan
            estimation_label = 'knn'
        else:
            return {'method': 'transfer_entropy',
                    'error': f'Unknown TE method: {method}'}

        # Net information flow
        net_te = te_xy - te_yx if np.isfinite(te_yx) else np.nan

        return {
            'method': 'transfer_entropy',
            'statistic': float(te_xy),
            'p_value': np.nan,  # no parametric p-value; use surrogates
            'direction': 'directional',
            'details': {
                'te_x_to_y': float(te_xy),
                'te_y_to_x': float(te_yx),
                'net_te': float(net_te) if np.isfinite(net_te) else None,
                'dominant_direction': 'x->y' if (np.isfinite(net_te) and net_te > 0) else 'y->x',
                'lag': lag,
                'k': k_horizon,
                'estimation': estimation_label,
                'n_points': n,
            },
        }
    except Exception as e:
        return {'method': 'transfer_entropy', 'error': str(e)}


# ═════════════════════════════════════════════════════════════
# PYINFORM-BASED TRANSFER ENTROPY (default, validated C library)
# ═════════════════════════════════════════════════════════════

def _te_pyinform(x: np.ndarray, y: np.ndarray, lag: int, k: int,
                 bins: int, bidir: bool) -> tuple:
    """
    Transfer Entropy via pyinform (C-based, well-validated).
    Requires discretized integer input.
    """
    x_d = _discretize(x, bins).astype(np.int64)
    y_d = _discretize(y, bins).astype(np.int64)

    te_xy = float(_pyinform_te(x_d, y_d, k=lag))
    te_yx = float(_pyinform_te(y_d, x_d, k=lag)) if bidir else np.nan

    return max(0.0, te_xy), max(0.0, te_yx) if np.isfinite(te_yx) else np.nan


# ═════════════════════════════════════════════════════════════
# KNN-BASED TRANSFER ENTROPY (fallback, Kraskov estimator)
# ═════════════════════════════════════════════════════════════

def _te_knn(x: np.ndarray, y: np.ndarray, lag: int, k: int,
            n_neighbors: int = 5) -> float:
    """
    Transfer Entropy via kNN conditional entropy estimation.

    TE(X->Y) = H(Y_f | Y_p) - H(Y_f | Y_p, X_p)

    Uses Chebyshev (max-norm) distances and digamma corrections.
    """
    from scipy.special import digamma
    from scipy.spatial import cKDTree

    n = len(y) - lag - k + 1
    if n < n_neighbors + 5:
        return 0.0

    # Build state vectors
    Y_past = np.column_stack([y[lag - 1 - j:lag - 1 - j + n] for j in range(lag)])
    X_past = np.column_stack([x[lag - 1 - j:lag - 1 - j + n] for j in range(lag)])
    Y_future = y[lag:lag + n].reshape(-1, 1)

    # Joint space: (Y_future, Y_past, X_past)
    joint = np.hstack([Y_future, Y_past, X_past])
    # Marginal 1: (Y_future, Y_past)
    marg_yfy = np.hstack([Y_future, Y_past])
    # Marginal 2: (Y_past, X_past)
    marg_ypxp = np.hstack([Y_past, X_past])
    # Marginal 3: Y_past
    marg_yp = Y_past

    # Build trees
    tree_joint = cKDTree(joint)
    tree_yfy = cKDTree(marg_yfy)
    tree_ypxp = cKDTree(marg_ypxp)
    tree_yp = cKDTree(marg_yp)

    # For each point, find k-th neighbor distance in joint space,
    # then count neighbors within that distance in marginal spaces
    te_sum = 0.0
    for i in range(n):
        # k+1 because query point is included
        d_joint = tree_joint.query(joint[i], k=n_neighbors + 1, p=np.inf)[0][-1]
        eps = d_joint + 1e-12

        n_yfy = tree_yfy.query_ball_point(marg_yfy[i], r=eps, p=np.inf)
        n_ypxp = tree_ypxp.query_ball_point(marg_ypxp[i], r=eps, p=np.inf)
        n_yp = tree_yp.query_ball_point(marg_yp[i], r=eps, p=np.inf)

        # Neighbor counts (subtract 1 for self)
        te_sum += digamma(max(len(n_yp) - 1, 1)) \
                - digamma(max(len(n_yfy) - 1, 1)) \
                - digamma(max(len(n_ypxp) - 1, 1))

    te = digamma(n_neighbors) + te_sum / n
    return max(0.0, float(te))


# ═════════════════════════════════════════════════════════════
# UTILITIES
# ═════════════════════════════════════════════════════════════

def _discretize(x: np.ndarray, bins: int) -> np.ndarray:
    """Discretize signal into equal-frequency bins."""
    percentiles = np.linspace(0, 100, bins + 1)
    edges = np.percentile(x, percentiles)
    edges[-1] += 1e-10
    return np.digitize(x, edges[1:-1])
