"""
Associa — Mutual Information
==============================
Non-parametric measure of mutual dependence between two signals.
Captures both linear and nonlinear associations.
Symmetric: MI(X,Y) = MI(Y,X).
"""

import numpy as np
from typing import Dict, Optional


def mutual_information(signal_x: np.ndarray, signal_y: np.ndarray,
                       config: Optional[Dict] = None) -> Dict:
    """
    Mutual Information estimated via k-nearest neighbors (Kraskov method).

    Parameters
    ----------
    signal_x, signal_y : 1-D arrays (same length)
    config : optional dict with:
        n_neighbors   : int (default 3) — k for kNN estimator
        random_state  : int (default 42)

    Returns
    -------
    dict with: method, statistic (MI in nats), p_value, direction, details
    """
    from sklearn.feature_selection import mutual_info_regression

    cfg = config or {}
    n_neighbors = cfg.get('n_neighbors', 3)
    random_state = cfg.get('random_state', 42)

    x = np.asarray(signal_x, dtype=np.float64).ravel()
    y = np.asarray(signal_y, dtype=np.float64).ravel()

    n = min(len(x), len(y))
    if n < 10:
        return {'method': 'mutual_information', 'error': f'Signals too short ({n} < 10)'}

    x, y = x[:n], y[:n]

    try:
        # sklearn expects X as (n, 1)
        mi = mutual_info_regression(
            x.reshape(-1, 1), y,
            n_neighbors=n_neighbors,
            random_state=random_state,
        )[0]

        # Normalized MI: MI / min(H(X), H(Y))
        # Entropy estimated via histogram
        h_x = _entropy_hist(x)
        h_y = _entropy_hist(y)
        max_mi = min(h_x, h_y)
        nmi = float(np.clip(mi / max_mi, 0, 1)) if max_mi > 0 else 0.0

        return {
            'method': 'mutual_information',
            'statistic': float(mi),
            'p_value': np.nan,  # MI has no parametric p-value; use surrogates
            'direction': 'symmetric',
            'details': {
                'normalized_mi': nmi,
                'entropy_x': float(h_x),
                'entropy_y': float(h_y),
                'n_neighbors': n_neighbors,
                'n_points': n,
            },
        }
    except Exception as e:
        return {'method': 'mutual_information', 'error': str(e)}


def _entropy_hist(x: np.ndarray, bins: int = 50) -> float:
    """Shannon entropy estimated via histogram (in nats)."""
    counts, _ = np.histogram(x, bins=bins)
    p = counts / counts.sum()
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))
