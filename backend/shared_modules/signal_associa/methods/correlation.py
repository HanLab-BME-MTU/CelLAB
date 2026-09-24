"""
Associa — Correlation Methods
===============================
Pearson and Spearman correlation between two 1-D signals.
Symmetric measures (no directionality).
"""

import numpy as np
from scipy.stats import pearsonr, spearmanr
from typing import Dict, Optional


def pearson(signal_x: np.ndarray, signal_y: np.ndarray,
            config: Optional[Dict] = None) -> Dict:
    """
    Pearson correlation coefficient.
    Measures linear association between two signals.

    Parameters
    ----------
    signal_x, signal_y : 1-D arrays (same length)
    config : optional dict with 'alpha' (default 0.05)

    Returns
    -------
    dict with: method, statistic (r), p_value, direction, details
    """
    alpha = (config or {}).get('alpha', 0.05)
    x = np.asarray(signal_x, dtype=np.float64).ravel()
    y = np.asarray(signal_y, dtype=np.float64).ravel()

    n = min(len(x), len(y))
    if n < 3:
        return {'method': 'pearson', 'error': f'Signals too short ({n} < 3)'}

    x, y = x[:n], y[:n]

    try:
        r, p = pearsonr(x, y)
        return {
            'method': 'pearson',
            'statistic': float(r),
            'p_value': float(p),
            'direction': 'symmetric',
            'details': {
                'r_squared': float(r ** 2),
                'n_points': n,
                'significant': p < alpha,
            },
        }
    except Exception as e:
        return {'method': 'pearson', 'error': str(e)}


def spearman(signal_x: np.ndarray, signal_y: np.ndarray,
             config: Optional[Dict] = None) -> Dict:
    """
    Spearman rank correlation.
    Measures monotonic (not necessarily linear) association.
    Robust to outliers.
    """
    alpha = (config or {}).get('alpha', 0.05)
    x = np.asarray(signal_x, dtype=np.float64).ravel()
    y = np.asarray(signal_y, dtype=np.float64).ravel()

    n = min(len(x), len(y))
    if n < 3:
        return {'method': 'spearman', 'error': f'Signals too short ({n} < 3)'}

    x, y = x[:n], y[:n]

    try:
        rho, p = spearmanr(x, y)
        return {
            'method': 'spearman',
            'statistic': float(rho),
            'p_value': float(p),
            'direction': 'symmetric',
            'details': {
                'n_points': n,
                'significant': p < alpha,
            },
        }
    except Exception as e:
        return {'method': 'spearman', 'error': str(e)}
