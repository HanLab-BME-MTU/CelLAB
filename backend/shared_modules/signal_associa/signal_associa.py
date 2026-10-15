"""
Associa — Single-Pair Signal Coupling Analyzer
================================================
Master orchestrator that wires Stationarizer + SurrogateGenerator + Methods.

Semantic-agnostic: doesn't know if signals are FA intensities or NK trajectories.
Pipelines (FASTIA, IMMUNIA) provide signals and interpret results.

Workflow:
    1. Two raw signals enter
    2. Stationarizer transforms both → raw + stationary versions stored
    3. For each requested method:
       a. Pick signal version (raw or stationary) per method config
       b. Run method on original signals → real statistic
       c. If surrogates requested: generate N surrogates, test each → null distribution
       d. Compute empirical p-value from null distribution
    4. Return structured results

Usage:
    from signal_associa import Associa

    engine = Associa({
        'stationarizer': {'method': 'bandpass', 'sampling_rate': 0.1},
        'surrogate': {'method': 'iaaft', 'n_iterations': 100},
        'methods': {
            'granger': {'maxlag': 5, 'signal_version': 'stationary'},
            'ccm': {'E': 2, 'signal_version': 'raw', 'n_surrogates': 100},
            'pearson': {'signal_version': 'raw'},
        },
    })
    result = engine.run(signal_x, signal_y)

Author: CelLAB / Han Mechanobiology Lab
"""

import numpy as np
from typing import Dict, Optional, List
from .stationarizer import Stationarizer, StationarityResult, run_diagnostics
from .surrogate_generator import SurrogateGenerator


# Default signal version for each method (scientifically motivated)
METHOD_DEFAULTS = {
    'pearson':             {'signal_version': 'raw',        'n_surrogates': 0},
    'spearman':            {'signal_version': 'raw',        'n_surrogates': 0},
    'pearson_lagscan':     {'signal_version': 'raw',        'n_surrogates': 100},
    'mutual_information':  {'signal_version': 'raw',        'n_surrogates': 100},
    'granger_causality':   {'signal_version': 'stationary', 'n_surrogates': 0},
    'ccm':                 {'signal_version': 'raw',        'n_surrogates': 100},
    'transfer_entropy':    {'signal_version': 'raw',        'n_surrogates': 100},
}

# Method function registry
METHOD_FUNCTIONS = {}

def _load_methods():
    """Lazy-load method functions to avoid import-time cost."""
    global METHOD_FUNCTIONS
    if METHOD_FUNCTIONS:
        return
    from .methods.correlation import pearson, spearman, pearson_lagscan
    from .methods.mutual_info import mutual_information
    from .methods.granger import granger_causality
    from .methods.ccm import ccm, ccm_test_surrogates_batch
    from .methods.transfer_entropy import transfer_entropy

    METHOD_FUNCTIONS.update({
        'pearson': pearson,
        'spearman': spearman,
        'pearson_lagscan': pearson_lagscan,
        'mutual_information': mutual_information,
        'granger_causality': granger_causality,
        'ccm': ccm,
        'transfer_entropy': transfer_entropy,
    })
    METHOD_FUNCTIONS['_ccm_batch_surr'] = ccm_test_surrogates_batch


class Associa:
    """
    Single-pair signal coupling analyzer.

    Orchestrates: Stationarizer → SurrogateGenerator → Association Methods.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Parameters
        ----------
        config : dict with sections:
            stationarizer : dict — passed to Stationarizer()
            surrogate     : dict — passed to SurrogateGenerator()
            methods       : dict — {method_name: {method_config + signal_version + n_surrogates}}
            seed          : int  — base random seed (default None)
            early_stopping: dict — optional sequential surrogate test (Besag & Clifford 1991):
                            {'enabled': False, 'chunk': 10, 'alpha': 0.05}. Surrogates are run in
                            chunks; a pair stops as soon as enough surrogates reach the real statistic
                            that it can no longer be significant at alpha with n_surrogates.
        """
        cfg = config or {}

        self.stationarizer = Stationarizer(cfg.get('stationarizer'))
        self.surrogate_gen = SurrogateGenerator(cfg.get('surrogate'))
        self.method_configs = cfg.get('methods', {'ccm': {}, 'granger_causality': {}})
        self.seed = cfg.get('seed', None)
        self.early_stopping = cfg.get('early_stopping') or {}

        _load_methods()

    def run(self, signal_x: np.ndarray, signal_y: np.ndarray) -> Dict:
        """
        Run complete coupling analysis on a pair of signals.

        Parameters
        ----------
        signal_x, signal_y : 1-D numpy arrays

        Returns
        -------
        dict:
            raw_x, raw_y           — original signals
            stationary_x, stationary_y — StationarityResult objects
            results                — {method_name: MethodResult dict}
            summary                — quick-look table
        """
        x = np.asarray(signal_x, dtype=np.float64).ravel()
        y = np.asarray(signal_y, dtype=np.float64).ravel()

        # ── Step 1: Stationarize both signals (only if a method uses the stationary version) ──
        needs_stationary = any(
            {**METHOD_DEFAULTS.get(m, {}), **(c or {})}.get('signal_version', 'raw') == 'stationary'
            for m, c in self.method_configs.items())
        if needs_stationary:
            stat_x = self.stationarizer.transform(x)
            stat_y = self.stationarizer.transform(y)
            signals = {'raw': (x, y), 'stationary': (stat_x.signal_out, stat_y.signal_out)}
        else:
            stat_x = stat_y = None
            signals = {'raw': (x, y), 'stationary': (x, y)}

        # ── Step 2: Run each requested method ──
        results = {}
        for method_name, method_cfg in self.method_configs.items():
            if method_name not in METHOD_FUNCTIONS:
                results[method_name] = {'error': f'Unknown method: {method_name}'}
                continue

            result = self._run_single_method(
                method_name, method_cfg, signals, x, y
            )
            results[method_name] = result

        # ── Step 3: Build summary ──
        summary = self._build_summary(results)

        return {
            'raw_x': x,
            'raw_y': y,
            'stationary_x': stat_x,
            'stationary_y': stat_y,
            'results': results,
            'summary': summary,
        }

    def _run_single_method(self, method_name: str, method_cfg: Dict,
                           signals: Dict, raw_x: np.ndarray, raw_y: np.ndarray) -> Dict:
        """Run one association method with optional surrogate testing."""

        # Merge user config with defaults
        defaults = METHOD_DEFAULTS.get(method_name, {})
        cfg = {**defaults, **method_cfg}

        signal_version = cfg.pop('signal_version', 'raw')
        n_surrogates = cfg.pop('n_surrogates', 0)

        # Pick signal version
        sx, sy = signals.get(signal_version, signals['raw'])

        # Ensure equal length
        n = min(len(sx), len(sy))
        sx, sy = sx[:n], sy[:n]

        # Run method on original signals
        func = METHOD_FUNCTIONS[method_name]
        real_result = func(sx, sy, cfg if cfg else None)

        if 'error' in real_result:
            return real_result

        # ── Surrogate testing ──
        if n_surrogates > 0:
            surr_result = self._run_surrogates(
                method_name, func, sx, sy, n_surrogates, cfg, real_result
            )
            real_result.update(surr_result)

        # Tag which signal version was used
        real_result['signal_version'] = signal_version

        return real_result

    def _run_surrogates(self, method_name: str, func, sx: np.ndarray, sy: np.ndarray,
                        n_surrogates: int, method_cfg: Dict, real_result: Dict) -> Dict:
        """
        Generate surrogates of X, test each against Y, build null distribution.

        For CCM with GPU: uses vectorized batch testing (Strategy B).
        For everything else: serial surrogate loop (Strategy A compatible).
        """
        real_stat = real_result.get('statistic', np.nan)
        seed = self.seed

        # ── Optional early stopping (same null statistics, computed chunk by chunk) ──
        if self.early_stopping.get('enabled', False):
            return self._run_surrogates_early(method_name, func, sx, sy, n_surrogates,
                                              method_cfg, real_stat)

        # ── CCM special path: batch surrogate testing ──
        if method_name == 'ccm' and method_cfg.get('gpu_enabled', False):
            batch_func = METHOD_FUNCTIONS.get('_ccm_batch_surr')
            if batch_func is not None:
                surrogates = self.surrogate_gen.generate_batch_gpu(sx, n_surrogates, seed)
                null_stats = batch_func(
                    surrogates if hasattr(surrogates, '__cuda_array_interface__') else np.asarray(surrogates),
                    sy, config=method_cfg
                )
                null_stats = np.asarray(null_stats, dtype=np.float64)
                p_emp = _empirical_pvalue(real_stat, null_stats)
                return {
                    'null_distribution': null_stats.tolist(),
                    'p_empirical': float(p_emp),
                    'n_surrogates': n_surrogates,
                    'surrogate_mean': float(np.mean(null_stats)),
                    'surrogate_std': float(np.std(null_stats)),
                    'effect_size': _effect_size(real_stat, null_stats),
                }

        # ── Standard path: generate surrogates, test ──
        surrogates = self.surrogate_gen.generate_batch(sx, n_surrogates, seed)

        if method_name == 'ccm' and METHOD_FUNCTIONS.get('_ccm_batch_surr') is not None:
            # CPU CCM: vectorized across surrogates (same statistic as the serial loop)
            null_stats = np.asarray(METHOD_FUNCTIONS['_ccm_batch_surr'](
                surrogates, sy, config=method_cfg), dtype=np.float64)
        else:
            null_stats = np.empty(n_surrogates, dtype=np.float64)
            for i in range(n_surrogates):
                surr_result = func(surrogates[i], sy, method_cfg if method_cfg else None)
                null_stats[i] = surr_result.get('statistic', np.nan)

        # Clean NaN surrogates
        valid = null_stats[np.isfinite(null_stats)]
        if len(valid) == 0:
            return {
                'null_distribution': [],
                'p_empirical': 1.0,
                'n_surrogates': 0,
            }

        p_emp = _empirical_pvalue(real_stat, valid)

        return {
            'null_distribution': valid.tolist(),
            'p_empirical': float(p_emp),
            'n_surrogates': len(valid),
            'surrogate_mean': float(np.mean(valid)),
            'surrogate_std': float(np.std(valid)),
            'effect_size': _effect_size(real_stat, valid),
        }

    def _null_chunk(self, method_name: str, func, sx: np.ndarray, sy: np.ndarray,
                    k: int, seed, method_cfg: Dict) -> np.ndarray:
        """Null statistics for k surrogates of X (GPU or vectorized CPU CCM, else serial)."""
        batch_func = METHOD_FUNCTIONS.get('_ccm_batch_surr') if method_name == 'ccm' else None
        if batch_func is not None and method_cfg.get('gpu_enabled', False):
            surr = self.surrogate_gen.generate_batch_gpu(sx, k, seed)
            null = batch_func(surr if hasattr(surr, '__cuda_array_interface__') else np.asarray(surr),
                              sy, config=method_cfg)
        elif batch_func is not None:
            null = batch_func(self.surrogate_gen.generate_batch(sx, k, seed), sy, config=method_cfg)
        else:
            surr = self.surrogate_gen.generate_batch(sx, k, seed)
            null = [func(surr[i], sy, method_cfg if method_cfg else None).get('statistic', np.nan)
                    for i in range(k)]
        return np.asarray(null, dtype=np.float64)

    def _run_surrogates_early(self, method_name: str, func, sx: np.ndarray, sy: np.ndarray,
                              n_surrogates: int, method_cfg: Dict, real_stat: float) -> Dict:
        """Sequential surrogate test (Besag & Clifford 1991). Stops once more than e_max
        surrogates reach the real statistic, where e_max is the largest exceedance count that
        would still be significant at alpha with n_surrogates; such pairs cannot become
        significant, so further surrogates cannot change the decision."""
        chunk = max(int(self.early_stopping.get('chunk', 10)), 1)
        alpha = float(self.early_stopping.get('alpha', 0.05))
        e_max = _max_significant_exceedances(n_surrogates, alpha)
        if not np.isfinite(real_stat):
            return {'null_distribution': [], 'p_empirical': 1.0, 'n_surrogates': 0,
                    'stopped_early': False}
        nulls, exceed, used, stopped = [], 0, 0, False
        for c0 in range(0, n_surrogates, chunk):
            k = min(chunk, n_surrogates - c0)
            s_seed = None if self.seed is None else int(self.seed) + c0
            null = self._null_chunk(method_name, func, sx, sy, k, s_seed, method_cfg)
            null = null[np.isfinite(null)]
            nulls.append(null)
            exceed += int(np.sum(null >= real_stat))
            used += len(null)
            if exceed > e_max:
                stopped = True
                break
        if used == 0:
            return {'null_distribution': [], 'p_empirical': 1.0, 'n_surrogates': 0,
                    'stopped_early': stopped}
        valid = np.concatenate(nulls)
        p_emp = exceed / used if stopped else (exceed + 1) / (used + 1)
        return {
            'null_distribution': valid.tolist(),
            'p_empirical': float(p_emp),
            'n_surrogates': int(used),
            'n_surrogates_max': int(n_surrogates),
            'stopped_early': bool(stopped),
            'surrogate_mean': float(np.mean(valid)),
            'surrogate_std': float(np.std(valid)),
            'effect_size': _effect_size(real_stat, valid),
        }

    def _build_summary(self, results: Dict) -> List[Dict]:
        """
        Build a quick-look summary table from all method results.
        Each row: method, statistic, p_value, p_empirical, significant, direction.
        """
        rows = []
        for name, r in results.items():
            if 'error' in r:
                rows.append({'method': name, 'error': r['error']})
                continue

            p_emp = r.get('p_empirical', np.nan)
            p_par = r.get('p_value', np.nan)
            # Use empirical p if surrogates were run, else parametric
            p_best = p_emp if np.isfinite(p_emp) else p_par

            rows.append({
                'method': name,
                'statistic': r.get('statistic', np.nan),
                'p_value': p_par,
                'p_empirical': p_emp,
                'p_best': p_best,
                'significant': p_best < 0.05 if np.isfinite(p_best) else False,
                'direction': r.get('direction', '?'),
                'signal_version': r.get('signal_version', '?'),
                'effect_size': r.get('effect_size', np.nan),
            })
        return rows


# ═════════════════════════════════════════════════════════════
# UTILITIES
# ═════════════════════════════════════════════════════════════

def _max_significant_exceedances(n_max: int, alpha: float) -> int:
    """Largest number of surrogates >= real that is still significant with n_max surrogates."""
    e = -1
    while (e + 2) / (n_max + 1) < alpha:
        e += 1
    return e


def _empirical_pvalue(real_stat: float, null_distribution: np.ndarray) -> float:
    """
    One-sided empirical p-value.
    p = (# surrogates ≥ real + 1) / (N + 1)
    The +1 corrections prevent p=0.
    """
    if not np.isfinite(real_stat) or len(null_distribution) == 0:
        return 1.0
    n_exceed = np.sum(null_distribution >= real_stat)
    return float((n_exceed + 1) / (len(null_distribution) + 1))


def _effect_size(real_stat: float, null_distribution: np.ndarray) -> float:
    """
    Effect size: (real - mean_null) / std_null.
    Like Cohen's d for the surrogate distribution.
    """
    if len(null_distribution) == 0:
        return np.nan
    std = np.std(null_distribution)
    if std < 1e-12:
        return np.inf if real_stat > np.mean(null_distribution) else 0.0
    return float((real_stat - np.mean(null_distribution)) / std)
