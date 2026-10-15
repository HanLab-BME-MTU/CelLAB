"""
Associa — Correlation Methods
===============================
Pearson and Spearman correlation between two 1-D signals (symmetric measures),
and lag-scanned Pearson cross-correlation (Machacek & Danuser baseline).
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


def pearson_lagscan(signal_x: np.ndarray, signal_y: np.ndarray,
                    config: Optional[Dict] = None) -> Dict:
    """
    Lag-scanned Pearson cross-correlation (Machacek & Danuser baseline).

    r(k) = corr(X(t), Y(t + k)) for k = -max_lag ... +max_lag; the test statistic is the
    signed extremum r* = r(k*), k* = argmax_k |r(k)|.

    Significance:
      - parametric: |r*| > 1.96 / sqrt(N_overlap) (as in the original method; does not
        correct for scanning many lags)
      - surrogate (via Associa, n_surrogates > 0): 'statistic' is |r*|, so every surrogate
        gets the same lag scan and the empirical p-value tests the magnitude of the extremum.

    Parameters
    ----------
    signal_x, signal_y : 1-D arrays (same length)
    config : optional dict
        max_lag     : int (default 15) — lags scanned in both directions
        min_overlap : int (default 10) — minimum number of overlapping points per lag
        alpha       : float (default 0.05)

    Returns
    -------
    dict with: method, statistic (|r*|), p_value (parametric at k*, uncorrected), direction,
               details (r_best, lag_best, n_overlap, parametric threshold, r_by_lag)
    """
    cfg = config or {}
    max_lag = int(cfg.get('max_lag', 15))
    min_overlap = int(cfg.get('min_overlap', 10))
    alpha = cfg.get('alpha', 0.05)

    x = np.asarray(signal_x, dtype=np.float64).ravel()
    y = np.asarray(signal_y, dtype=np.float64).ravel()
    n = min(len(x), len(y))
    x, y = x[:n], y[:n]
    if n < min_overlap:
        return {'method': 'pearson_lagscan', 'error': f'Signals too short ({n} < {min_overlap})'}

    lags = np.arange(-max_lag, max_lag + 1)
    r_by_lag = np.full(len(lags), np.nan)
    n_by_lag = np.zeros(len(lags), dtype=int)
    for i, k in enumerate(lags):
        if k >= 0:
            a, b = x[:n - k], y[k:]          # X(t) with Y(t + k)
        else:
            a, b = x[-k:], y[:n + k]
        m = len(a)
        if m < min_overlap or np.std(a) == 0 or np.std(b) == 0:
            continue
        r_by_lag[i] = np.corrcoef(a, b)[0, 1]
        n_by_lag[i] = m

    if not np.any(np.isfinite(r_by_lag)):
        return {'method': 'pearson_lagscan', 'error': 'No lag with enough overlap or variance'}

    i_best = int(np.nanargmax(np.abs(r_by_lag)))
    r_best = float(r_by_lag[i_best])
    k_best = int(lags[i_best])
    n_best = int(n_by_lag[i_best])
    threshold = 1.96 / np.sqrt(n_best)
    try:
        if k_best >= 0:
            _, p_best = pearsonr(x[:n - k_best], y[k_best:])
        else:
            _, p_best = pearsonr(x[-k_best:], y[:n + k_best])
    except Exception:
        p_best = np.nan

    if k_best > 0:
        direction = 'x_leads_y'
    elif k_best < 0:
        direction = 'y_leads_x'
    else:
        direction = 'simultaneous'

    return {
        'method': 'pearson_lagscan',
        'statistic': float(abs(r_best)),
        'p_value': float(p_best),
        'direction': direction,
        'details': {
            'r_best': r_best,
            'lag_best': k_best,
            'n_overlap': n_best,
            'threshold_parametric': float(threshold),
            'significant_parametric': bool(abs(r_best) > threshold),
            'significant_p_uncorrected': bool(p_best < alpha) if np.isfinite(p_best) else False,
            'max_lag': max_lag,
            'r_by_lag': {int(k): (float(r) if np.isfinite(r) else None) for k, r in zip(lags, r_by_lag)},
        },
    }
