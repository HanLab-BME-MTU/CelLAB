"""
Associa — Convergent Cross Mapping (CCM)
==========================================
Tests dynamical coupling between two signals via state-space reconstruction.

CCM is stationarity-agnostic — it works on raw (non-stationary) signals.
This is complementary to Granger Causality which requires stationarity.

Directional: CCM(X->Y) tests whether Y's state space predicts X.
(In CCM logic, if X drives Y, then Y's attractor contains X's information.)

Algorithm matches pyEDM (Sugihara Lab) implementation:
  - Leave-one-out cross-validation (no bootstrap splitting)
  - Exponential distance weighting for simplex projection
  - No correlation clipping (negative rho allowed)
Validated against pyEDM v1.15.4 to floating-point precision (~3e-7).

Two interfaces:
    ccm()                        — single pair, returns rho + optional lag scan
    ccm_test_surrogates_batch()  — test N pre-generated surrogates at once
                                    (GPU-vectorized for Strategy B parallelism)

CPU: numpy + scipy.spatial.cKDTree
GPU: cupy (optional, auto-fallback to CPU)

From SimpleCCMAnalyzer (Rostami 2025), refactored for Associa.
"""

import numpy as np
from typing import Dict, Optional
from scipy.spatial import cKDTree
from scipy.special import betainc as _betainc


def _pearsonr(a, b):
    """
    Fast Pearson r and two-sided p (same values as scipy.stats.pearsonr,
    without its per-call overhead, which dominated CPU run time).
    """
    a = a - a.mean()
    b = b - b.mean()
    den = np.sqrt(np.dot(a, a) * np.dot(b, b))
    if not np.isfinite(den) or den == 0:
        return np.nan, np.nan
    r = float(np.dot(a, b) / den)
    r = min(max(r, -1.0), 1.0)
    df = len(a) - 2
    if df <= 0:
        return r, np.nan
    if abs(r) >= 1.0:
        return r, 0.0
    p = float(_betainc(0.5 * df, 0.5, df / (df + r * r * df / (1.0 - r * r))))
    return r, p


# =================================================================
# PUBLIC API
# =================================================================

def ccm(signal_x: np.ndarray, signal_y: np.ndarray,
        config: Optional[Dict] = None) -> Dict:
    """
    Convergent Cross Mapping between two 1-D signals.

    Parameters
    ----------
    signal_x, signal_y : 1-D arrays (same length)
    config : optional dict with:
        E             : int (default 2) — embedding dimension
        tau           : int (default 1) — embedding delay
        lags          : tuple (default (-2,-1,0,1,2)) — lags to scan
        min_points    : int (default 20) — minimum signal length
        bidirectional : bool (default True) — test both directions

    Returns
    -------
    dict with: method, statistic (best rho), p_value, direction, details
    """
    cfg = config or {}
    E = cfg.get('E', 2)
    tau = cfg.get('tau', 1)
    lags = cfg.get('lags', (-2, -1, 0, 1, 2))
    min_pts = cfg.get('min_points', 20)
    bidir = cfg.get('bidirectional', True)

    x = np.asarray(signal_x, dtype=np.float64).ravel()
    y = np.asarray(signal_y, dtype=np.float64).ravel()

    n = min(len(x), len(y))
    if n < min_pts:
        return {'method': 'ccm', 'error': f'Signals too short ({n} < {min_pts})'}
    x, y = x[:n], y[:n]

    # Direction 1: X->Y (embed Y's manifold, predict X)
    rho_xy, lag_xy, p_xy = _scan_lags(x, y, E, tau, lags)

    # Direction 2: Y->X (embed X's manifold, predict Y)
    if bidir:
        rho_yx, lag_yx, p_yx = _scan_lags(y, x, E, tau, lags)
    else:
        rho_yx, lag_yx, p_yx = np.nan, 0, np.nan

    best_rho = np.nanmax([rho_xy, rho_yx])
    best_p = float(p_xy if rho_xy >= rho_yx else p_yx)

    return {
        'method': 'ccm',
        'statistic': float(best_rho),
        'p_value': best_p,   # fitting p-value of cross-map correlation
        'direction': 'directional',
        'details': {
            'rho_x_to_y': float(rho_xy),
            'rho_y_to_x': float(rho_yx),
            'p_fit_x_to_y': float(p_xy),
            'p_fit_y_to_x': float(p_yx),
            'lag_x_to_y': int(lag_xy),
            'lag_y_to_x': int(lag_yx),
            'E': E, 'tau': tau,
            'n_points': n,
        },
    }


def ccm_test_surrogates_batch(surrogates: np.ndarray,
                               signal_effect: np.ndarray,
                               lag: int = 0,
                               config: Optional[Dict] = None) -> np.ndarray:
    """
    Test N surrogates with full lag scan + bidirectional testing.
    Each surrogate gets the same treatment as the real stat:
      - Scan all lags in both directions
      - Return max rho per surrogate

    GPU-accelerated: loops over lags x directions (10 iterations),
    each iteration vectorized across all N surrogates.
    """
    cfg = config or {}
    E = cfg.get('E', 2)
    tau = cfg.get('tau', 1)
    lags = cfg.get('lags', (-2, -1, 0, 1, 2))
    bidir = cfg.get('bidirectional', True)
    gpu = cfg.get('gpu_enabled', False)

    if hasattr(surrogates, "get"):
        surrogates = surrogates.get()
    surr = np.asarray(surrogates, dtype=np.float64)
    effect = np.asarray(signal_effect, dtype=np.float64).ravel()
    n_surr = surr.shape[0]

    # GPU path
    if gpu:
        try:
            import cupy as cp
            return _batch_ccm_full_scan_gpu(cp, surr, effect, lags, bidir, E, tau)
        except ImportError:
            pass

    # CPU path: vectorized across surrogates (same result as the serial scan)
    return _batch_ccm_full_scan_cpu(surr, effect, lags, bidir, E, tau)


# =================================================================
# INTERNAL: Core CCM computation
# =================================================================

def _scan_lags(cause, effect, E, tau, lags):
    """Find the lag with highest CCM rho (allows negative rho)."""
    best_rho, best_lag, best_p = -np.inf, 0, np.nan
    for lag in lags:
        rho, p_fit = _ccm_single(cause, effect, E, tau, lag)
        if np.isfinite(rho) and rho > best_rho:
            best_rho, best_lag, best_p = rho, lag, p_fit
    return (float(best_rho) if np.isfinite(best_rho) else np.nan), best_lag, best_p


def _ccm_single(cause, effect, E, tau, lag):
    """
    Single CCM evaluation at one lag using leave-one-out.
    Matches pyEDM (Sugihara Lab) algorithm exactly.

    Parameters
    ----------
    cause  : 1-D array — signal to predict (target in pyEDM terms)
    effect : 1-D array — signal to embed (column in pyEDM terms)
    E      : embedding dimension
    tau    : embedding delay
    lag    : time lag for alignment

    Returns
    -------
    float : cross-map correlation rho (can be negative)
    """
    cause = np.asarray(cause, dtype=np.float64)
    effect = np.asarray(effect, dtype=np.float64)

    # Align for lag
    if lag > 0:
        cause, effect = cause[lag:], effect[:-lag]
    elif lag < 0:
        L = -lag
        cause, effect = cause[:-L], effect[L:]

    # Embed effect
    n = len(effect)
    n_embed = n - (E - 1) * tau
    if n_embed <= E + 2:
        return np.nan, np.nan

    X_embed = np.column_stack([effect[i * tau : i * tau + n_embed] for i in range(E)])
    y_cause = cause[(E - 1) * tau : (E - 1) * tau + n_embed]

    # kNN with leave-one-out (exclude self)
    k = E + 1
    tree = cKDTree(X_embed)
    dd, nn = tree.query(X_embed, k=k + 1)
    dd, nn = dd[:, 1:], nn[:, 1:]  # drop self-match

    # Exponential weights
    w = np.exp(-dd / (dd[:, 0:1] + 1e-12))
    w = w / (w.sum(axis=1, keepdims=True) + 1e-12)

    # Predict cause from effect neighbors
    y_hat = np.sum(w * y_cause[nn], axis=1)

    # Correlation (no clipping — allow negative, matching pyEDM)
    rho, p_fit = _pearsonr(y_hat, y_cause)
    return (float(rho), float(p_fit)) if np.isfinite(rho) else (np.nan, np.nan)


# =================================================================
# CPU VECTORIZED SURROGATE TESTING
# =================================================================

def _rowwise_corr(A, B):
    A = A - A.mean(axis=1, keepdims=True)
    B = B - B.mean(axis=1, keepdims=True)
    den = np.sqrt((A * A).sum(axis=1) * (B * B).sum(axis=1))
    with np.errstate(invalid='ignore', divide='ignore'):
        r = (A * B).sum(axis=1) / den
    r[~np.isfinite(r)] = np.nan
    return r


def _knn_weights(X, E):
    """Leave-one-out kNN (k = E+1) with exponential weights, as in _ccm_single."""
    k = E + 1
    dd, nn = cKDTree(X).query(X, k=k + 1)
    dd, nn = dd[:, 1:], nn[:, 1:]
    w = np.exp(-dd / (dd[:, 0:1] + 1e-12))
    w = w / (w.sum(axis=1, keepdims=True) + 1e-12)
    return w, nn


def _batch_ccm_full_scan_cpu(surr, effect, lags, bidir, E, tau):
    """
    Max cross-map rho over lags (and both directions) for every surrogate.
    Identical to looping _scan_lags per surrogate:
      forward  (surrogate -> effect): the effect embedding is shared, so its kNN and
               weights are computed once per lag and applied to all surrogates;
      reverse  (effect -> surrogate): each surrogate is embedded separately.
    """
    n_surr = surr.shape[0]
    best = np.full(n_surr, -np.inf)
    off = (E - 1) * tau
    for lag in lags:
        if lag > 0:
            S, eff = surr[:, lag:], effect[:-lag]
        elif lag < 0:
            S, eff = surr[:, :lag], effect[-lag:]
        else:
            S, eff = surr, effect
        n_embed = len(eff) - off
        if n_embed <= E + 2:
            continue

        # forward: _ccm_single(cause=surrogate, effect=effect)
        X = np.column_stack([eff[i * tau: i * tau + n_embed] for i in range(E)])
        w, nn = _knn_weights(X, E)
        Yc = S[:, off: off + n_embed]
        rho = _rowwise_corr((w[None] * Yc[:, nn]).sum(axis=2), Yc)
        best = np.fmax(best, rho)

        # reverse: _ccm_single(cause=effect, effect=surrogate)
        if bidir:
            yc = eff[off: off + n_embed]
            yc0 = yc - yc.mean()
            yc_ss = np.dot(yc0, yc0)
            for i in range(n_surr):
                Xi = np.column_stack([S[i, j * tau: j * tau + n_embed] for j in range(E)])
                wi, nni = _knn_weights(Xi, E)
                yh = (wi * yc[nni]).sum(axis=1)
                yh0 = yh - yh.mean()
                den = np.sqrt(np.dot(yh0, yh0) * yc_ss)
                if den > 0 and np.isfinite(den):
                    best[i] = max(best[i], np.dot(yh0, yc0) / den)

    best[~np.isfinite(best)] = np.nan
    return best


# =================================================================
# GPU VECTORIZED SURROGATE TESTING
# =================================================================

def _batch_ccm_full_scan_gpu(cp, surrogates_np, effect_np, lags, bidir, E, tau):
    """
    Full lag-scan CCM on GPU, vectorized across surrogates.
    Loops over lags x directions (small loop), each iteration
    processes all N surrogates in parallel.

    Uses np.fmax to safely ignore NaNs when tracking best rho.
    """
    n_surr = surrogates_np.shape[0]
    best_rhos = np.full(n_surr, -np.inf, dtype=np.float64)

    for lag in lags:
        # Direction 1: effect manifold predicts surrogates
        rhos_fwd = _batch_ccm_single_direction_gpu(
            cp, surrogates_np, effect_np, lag, E, tau, forward=True)
        best_rhos = np.fmax(best_rhos, rhos_fwd)

        if bidir:
            # Direction 2: surrogate manifolds predict effect
            rhos_rev = _batch_ccm_single_direction_gpu(
                cp, surrogates_np, effect_np, lag, E, tau, forward=False)
            best_rhos = np.fmax(best_rhos, rhos_rev)

    # Replace untouched -inf with NaN
    best_rhos[~np.isfinite(best_rhos)] = np.nan
    return best_rhos


def _batch_ccm_single_direction_gpu(cp, surrogates_np, effect_np, lag, E, tau, forward=True):
    """
    One direction, one lag, all surrogates in parallel on GPU.
    Matches CPU _ccm_single algorithm exactly:
      - Leave-one-out cross-validation
      - No correlation clipping
      - Correct (E-1)*tau offset for target alignment

    Optimization for forward direction:
      The effect embedding (and thus distances, kNN, weights) is shared
      across all surrogates. Computed ONCE, then predictions vectorized
      across N surrogates using shared weights.

    Parameters
    ----------
    forward=True  : embed effect (shared), predict surrogates
    forward=False : embed each surrogate, predict effect
    """
    surr_gpu = cp.asarray(surrogates_np, dtype=cp.float64)
    effect_gpu = cp.asarray(effect_np, dtype=cp.float64)
    n_surr, T = surr_gpu.shape

    # Align for lag
    if lag > 0:
        surr_aligned = surr_gpu[:, lag:]
        effect_aligned = effect_gpu[:-lag]
    elif lag < 0:
        L = -lag
        surr_aligned = surr_gpu[:, :-L]
        effect_aligned = effect_gpu[L:]
    else:
        surr_aligned = surr_gpu
        effect_aligned = effect_gpu

    n_aligned = effect_aligned.shape[0]
    n_embed = n_aligned - (E - 1) * tau

    if n_embed <= E + 2:
        return np.full(n_surr, np.nan, dtype=np.float64)

    # Target alignment offset
    offset = (E - 1) * tau
    k = E + 1
    kk = min(k, n_embed - 1)

    if forward:
        # ─── OPTIMIZED: shared embedding, distances computed ONCE ───
        # Embed effect (single matrix, not tiled)
        embed_idx = cp.arange(E)[:, None] * tau + cp.arange(n_embed)[None, :]
        X_embed = effect_aligned[embed_idx].T  # (n_embed, E)

        # Distance matrix: (n_embed, n_embed) — computed ONCE
        a2 = cp.sum(X_embed ** 2, axis=1, keepdims=True)       # (n_embed, 1)
        b2 = a2.T                                                # (1, n_embed)
        dot = X_embed @ X_embed.T                                # (n_embed, n_embed)
        d = cp.sqrt(cp.maximum(a2 + b2 - 2.0 * dot, 0.0))      # (n_embed, n_embed)

        # LOO: self-distance = inf
        idx = cp.arange(n_embed)
        d[idx, idx] = cp.inf

        # kNN: shared indices and weights — computed ONCE
        nn_idx = cp.argpartition(d, kth=kk-1, axis=1)[:, :kk]                  # (n_embed, k)
        row_idx = cp.arange(n_embed)[:, None]                    # (n_embed, 1)
        d_nn = d[row_idx, nn_idx]                                # (n_embed, k)

        # Exponential weights — shared
        d_min = cp.min(d_nn, axis=1, keepdims=True) + 1e-12
        w = cp.exp(-d_nn / d_min)                                # (n_embed, k)
        w = w / (cp.sum(w, axis=1, keepdims=True) + 1e-12)

        # Predict: vectorized across surrogates using shared weights
        y_predict = surr_aligned[:, offset : offset + n_embed]   # (n_surr, n_embed)
        y_nn = y_predict[:, nn_idx.ravel()].reshape(n_surr, n_embed, kk)  # (n_surr, n_embed, k)
        y_hat = cp.sum(w[None, :, :] * y_nn, axis=2)            # (n_surr, n_embed)

        # Pearson correlation per surrogate
        y_hat_zm = y_hat - cp.mean(y_hat, axis=1, keepdims=True)
        y_pred_zm = y_predict - cp.mean(y_predict, axis=1, keepdims=True)
        num = cp.sum(y_hat_zm * y_pred_zm, axis=1)
        den = cp.sqrt(cp.sum(y_hat_zm ** 2, axis=1) * cp.sum(y_pred_zm ** 2, axis=1) + 1e-12)
        rho = num / den

        return cp.asnumpy(rho)

    else:
        # ─── REVERSE: each surrogate has unique embedding ───
        # Build per-surrogate embeddings
        X_batch = cp.empty((n_surr, n_embed, E), dtype=cp.float64)
        for e in range(E):
            X_batch[:, :, e] = surr_aligned[:, e * tau : e * tau + n_embed]
        y_predict = cp.tile(effect_aligned[offset : offset + n_embed], (n_surr, 1))

        # Full pairwise distance: (n_surr, n_embed, n_embed)
        a2 = cp.sum(X_batch ** 2, axis=2, keepdims=True)
        b2 = a2.transpose(0, 2, 1)
        dot = cp.matmul(X_batch, X_batch.transpose(0, 2, 1))
        d = cp.sqrt(cp.maximum(a2 + b2 - 2.0 * dot, 0.0))

        # LOO: self-distance = inf
        idx = cp.arange(n_embed)
        d[:, idx, idx] = cp.inf

        # kNN
        nn_idx = cp.argpartition(d, kth=kk-1, axis=2)[:, :, :kk]
        surr_idx = cp.arange(n_surr)[:, None, None]
        pred_idx = cp.arange(n_embed)[None, :, None]
        d_nn = d[surr_idx, pred_idx, nn_idx]

        # Weights
        d_min = cp.min(d_nn, axis=2, keepdims=True) + 1e-12
        w = cp.exp(-d_nn / d_min)
        w = w / (cp.sum(w, axis=2, keepdims=True) + 1e-12)

        # Predict
        y_lib_nn = y_predict[surr_idx, nn_idx]
        y_hat = cp.sum(w * y_lib_nn, axis=2)

        # Correlation
        y_hat_zm = y_hat - cp.mean(y_hat, axis=1, keepdims=True)
        y_pred_zm = y_predict - cp.mean(y_predict, axis=1, keepdims=True)
        num = cp.sum(y_hat_zm * y_pred_zm, axis=1)
        den = cp.sqrt(cp.sum(y_hat_zm ** 2, axis=1) * cp.sum(y_pred_zm ** 2, axis=1) + 1e-12)
        rho = num / den

        return cp.asnumpy(rho)
