"""
Associa — Granger Causality
=============================
Tests whether signal_x contains information that helps predict signal_y
beyond what signal_y's own past provides (and vice versa).

Directional: GC(X→Y) ≠ GC(Y→X).

IMPORTANT: Granger Causality assumes stationarity. Use the Stationarizer
to preprocess signals before calling this method. Non-stationary inputs
produce spurious results (Rostami 2025 investigation).

Two approaches:
    1. granger_causality()  — statsmodels wrapper (quick, standard)
    2. granger_var()        — Full VAR pipeline with lag selection (AIC/BIC)
                              and residual diagnostics (recommended)
"""

import numpy as np
from typing import Dict, Optional, Tuple


def granger_causality(signal_x: np.ndarray, signal_y: np.ndarray,
                      config: Optional[Dict] = None) -> Dict:
    """
    Granger Causality test via VAR model.

    Fits a VAR(p) model, selects optimal lag via AIC/BIC, runs F-test.

    Parameters
    ----------
    signal_x, signal_y : 1-D arrays (same length, should be stationary)
    config : optional dict with:
        maxlag : int (default 10) — maximum lag to search
        alpha  : float (default 0.05)
        criterion : str (default 'aic') — lag selection: 'aic', 'bic', 'hqic'

    Returns
    -------
    dict with results for both directions (X→Y and Y→X)
    """
    from statsmodels.tsa.api import VAR

    cfg = config or {}
    maxlag = cfg.get('maxlag', 10)
    alpha = cfg.get('alpha', 0.05)
    criterion = cfg.get('criterion', 'aic')

    x = np.asarray(signal_x, dtype=np.float64).ravel()
    y = np.asarray(signal_y, dtype=np.float64).ravel()

    n = min(len(x), len(y))
    if n < maxlag + 15:
        return {'method': 'granger_causality',
                'error': f'Signals too short ({n}) for maxlag={maxlag}'}

    x, y = x[:n], y[:n]

    try:
        data = np.column_stack([x, y])
        model = VAR(data)

        # Optimal lag selection
        lag_result = model.select_order(maxlags=min(maxlag, n // 3))
        selected_lag = getattr(lag_result, criterion, None)
        if selected_lag is None or selected_lag == 0:
            selected_lag = 1

        # Fit VAR
        fitted = model.fit(maxlags=selected_lag)

        # Granger test: X→Y (does X help predict Y?)
        gc_x_to_y = _granger_ftest(fitted, caused='y1', causing='y0')
        # Granger test: Y→X (does Y help predict X?)
        gc_y_to_x = _granger_ftest(fitted, caused='y0', causing='y1')

        # Lag selection info
        lag_info = {
            'aic': int(lag_result.aic) if hasattr(lag_result, 'aic') else None,
            'bic': int(lag_result.bic) if hasattr(lag_result, 'bic') else None,
            'hqic': int(lag_result.hqic) if hasattr(lag_result, 'hqic') else None,
            'selected': selected_lag,
            'criterion': criterion,
        }

        return {
            'method': 'granger_causality',
            'statistic': float(gc_x_to_y['f_stat']),  # primary: X→Y
            'p_value': float(gc_x_to_y['p_value']),
            'direction': 'directional',
            'details': {
                'x_to_y': gc_x_to_y,
                'y_to_x': gc_y_to_x,
                'lag_selection': lag_info,
                'n_points': n,
                'significant_x_to_y': gc_x_to_y['p_value'] < alpha,
                'significant_y_to_x': gc_y_to_x['p_value'] < alpha,
            },
        }

    except Exception as e:
        return {'method': 'granger_causality', 'error': str(e)}


def _granger_ftest(fitted_var, caused: str, causing: str) -> Dict:
    """
    Extract Granger F-test from a fitted VAR model.

    Uses statsmodels' built-in test_causality method.
    """
    try:
        test = fitted_var.test_causality(caused, causing, kind='f')
        return {
            'f_stat': float(test.test_statistic),
            'p_value': float(test.pvalue),
            'df': (int(test.df_num), int(test.df_denom)),
        }
    except Exception as e:
        # Fallback: manual F-test via grangercausalitytests
        try:
            from statsmodels.tsa.stattools import grangercausalitytests
            lag = fitted_var.k_ar

            if caused == 'y1':
                data = np.column_stack([fitted_var.endog[:, 1], fitted_var.endog[:, 0]])
            else:
                data = np.column_stack([fitted_var.endog[:, 0], fitted_var.endog[:, 1]])

            gc = grangercausalitytests(data, maxlag=lag, verbose=False)
            f_stat = gc[lag][0]['ssr_ftest'][0]
            p_val = gc[lag][0]['ssr_ftest'][1]
            return {'f_stat': float(f_stat), 'p_value': float(p_val), 'df': None}
        except:
            return {'f_stat': np.nan, 'p_value': 1.0, 'df': None, 'error': str(e)}
