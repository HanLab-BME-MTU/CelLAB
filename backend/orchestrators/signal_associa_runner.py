"""
Signal Associa Runner
=====================
Disk-backed, async-compatible runners for the Signal Associa shared module.

These mirror the Cornealia runner pattern in app.py: each function takes
(project, ws_id, pipeline_id, step_id, params, results_dir, progress_cb=None),
writes ALL outputs to the project's results_dir, and returns
{"status": ..., "outputs": {...}}.

Pipeline types
--------------
signal_associa_single :  import  → analysis
signal_associa_batch  :  batch_setup → batch_run → batch_results

On-disk layout (per step results_dir)
-------------------------------------
    signals.npz            # cached signals (import / batch_setup)
    associa_results.pkl    # full run dict (pickle) incl. null distributions
    summary.csv            # flat per-pair-per-method table
    summary.json           # {columns, rows} for the GUI Tables tab
    meta.json              # run metadata
    plots/*.png            # figures from signal_associa_plotter
    runs/<run_id>/...      # timestamped copy for run history

Location: backend/signal_associa_runner.py
Author: CelLAB / Han Mechanobiology Lab
"""

from __future__ import annotations

import csv
import json
import os
import pickle
import shutil
import sys
import time
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# ── Engine import (lazy) ────────────────────────────────────────────────────
_Associa = None


def _get_engine():
    """Lazy-load the Associa engine from backend/shared_modules/signal_associa."""
    global _Associa
    if _Associa is None:
        # This file lives in backend/orchestrators/, engine in backend/shared_modules/
        root = Path(__file__).resolve().parent.parent
        shared = root / 'shared_modules'
        if str(shared) not in sys.path:
            sys.path.insert(0, str(shared))
        from signal_associa.signal_associa import Associa
        _Associa = Associa
    return _Associa


# ── Plotter import (lazy) ───────────────────────────────────────────────────
_Plotter = None


def _get_plotter():
    """Load the plotter from backend/shared_modules/signal_associa/plotters/.

    Uses the same sys.path insert as the engine, so the plotter lives inside
    the module (like cornealia/plotters/cornealia_plotter.py).
    """
    global _Plotter
    if _Plotter is None:
        # This file lives in backend/orchestrators/, plotter in backend/shared_modules/
        root = Path(__file__).resolve().parent.parent
        shared = root / 'shared_modules'
        if str(shared) not in sys.path:
            sys.path.insert(0, str(shared))
        from signal_associa.plotters.signal_associa_plotter import signal_associa_plotter
        _Plotter = signal_associa_plotter
    return _Plotter


# ═════════════════════════════════════════════════════════════════════════════
# PARAM / CONFIG HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def _flatten_params(params: Dict) -> Dict:
    """Flatten nested {section: {k: v}} params into one dict (Cornealia style)."""
    flat: Dict = {}
    for key, val in (params or {}).items():
        if isinstance(val, dict):
            flat.update(val)
        else:
            flat[key] = val
    return flat


def _as_bool(v, default=False) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return default
    return str(v).strip().lower() in ('1', 'true', 'yes', 'on')


def _build_assoc_config(p: Dict, sampling_rate: float) -> Tuple[Dict, float, List[str]]:
    """Build the engine config + alpha from flat GUI params.

    Mirrors AssociaManager.run() so results are identical, but decoupled from
    the in-memory manager.
    """
    surr_method = p.get('surr_method', 'iaaft')
    n_surrogates = int(float(p.get('surr_n', 100) or 100))
    alpha = float(p.get('surr_alpha', 0.05) or 0.05)

    active: Dict[str, Dict] = {}
    # CCM defaults ON (matches manager: m_ccm truthy unless explicitly false)
    if _as_bool(p.get('m_ccm', True), True):
        active['ccm'] = {
            'E': int(float(p.get('ccm_E', 2) or 2)),
            'tau': int(float(p.get('ccm_tau', 1) or 1)),
            'n_boot': int(float(p.get('ccm_n_boot', 20) or 20)),
            'signal_version': 'raw',
            'n_surrogates': n_surrogates,
            # GPU for the CCM surrogate test (CuPy); falls back to the CPU path if unavailable
            'gpu_enabled': _as_bool(p.get('ccm_gpu', False)),
        }
    if _as_bool(p.get('m_granger')):
        active['granger_causality'] = {
            'maxlag': int(float(p.get('gc_maxlag', 5) or 5)),
            'criterion': p.get('gc_criterion', 'aic'),
            'signal_version': 'stationary',
            'n_surrogates': n_surrogates,
        }
    if _as_bool(p.get('m_pearson')):
        active['pearson'] = {'signal_version': 'raw', 'n_surrogates': n_surrogates}
    if _as_bool(p.get('m_lagscan')):
        # Lag-scanned Pearson (Machacek & Danuser): best |r| over lags -max_lag..+max_lag,
        # parametric 1.96/sqrt(N) and IAAFT surrogates (same lag scan on every surrogate)
        active['pearson_lagscan'] = {
            'max_lag': int(float(p.get('lag_max_lag', 15) or 15)),
            'min_overlap': int(float(p.get('lag_min_overlap', 10) or 10)),
            'signal_version': 'raw',
            'n_surrogates': n_surrogates,
        }
    if _as_bool(p.get('m_mi')):
        active['mutual_information'] = {'signal_version': 'raw',
                                        'n_surrogates': n_surrogates}
    if _as_bool(p.get('m_te')):
        active['transfer_entropy'] = {'signal_version': 'raw',
                                      'n_surrogates': n_surrogates}
    if not active:
        active['ccm'] = {'E': 2, 'tau': 1, 'n_boot': 20,
                         'signal_version': 'raw', 'n_surrogates': n_surrogates}

    assoc_config: Dict = {
        'surrogate': {'method': surr_method, 'n_iterations': 100},
        'methods': active,
    }
    # Sequential surrogate test (Besag & Clifford 1991): stop a pair once it can no longer be
    # significant. Same decisions as the full test, fewer surrogates for non-coupled pairs.
    if _as_bool(p.get('early_stop', False)):
        assoc_config['early_stopping'] = {
            'enabled': True,
            'chunk': int(float(p.get('early_stop_chunk', 10) or 10)),
            'alpha': alpha,
        }

    stat_method = p.get('stat_method', p.get('method', 'auto'))
    if stat_method and stat_method not in ('none', 'None'):
        assoc_config['stationarizer'] = {
            'method': stat_method,
            'sampling_rate': float(p.get('sampling_rate', sampling_rate) or sampling_rate),
            'bandpass_low': float(p.get('bp_low', 0.008) or 0.008),
            'bandpass_high': float(p.get('bp_high', 0.25) or 0.25),
        }

    return assoc_config, alpha, list(active.keys())


# ═════════════════════════════════════════════════════════════════════════════
# CSV LOAD + SIGNAL CACHE
# ═════════════════════════════════════════════════════════════════════════════

def _is_numeric(s: str) -> bool:
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def _load_signals_csv(path: str, has_header: str = 'auto'):
    """Load a CSV/TSV → (signal_names, signals_dict, n_samples). Mirrors manager."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    sep = '\t' if p.suffix.lower() in ('.tsv', '.tab') else ','
    with open(str(p), 'r') as f:
        first = f.readline().strip()

    if has_header == 'auto':
        parts = first.split(sep)
        header = any(not _is_numeric(x.strip()) for x in parts)
    else:
        header = has_header == 'yes'

    df = pd.read_csv(str(p), sep=sep, header=0 if header else None)
    names = [str(c) for c in df.columns]
    if not header:
        names = [f'Signal_{i}' for i in range(len(df.columns))]

    signals = {}
    for i, col in enumerate(df.columns):
        signals[names[i]] = df[col].values.astype(np.float64)

    return names, signals, len(df)


def _save_signals(results_dir: Path, names: List[str], signals: Dict,
                  sampling_rate: float, n_samples: int, source: str = '',
                  batch_type: str = 'all_pairs'):
    """Cache signals as an .npz + meta so a later step can reload them."""
    results_dir.mkdir(parents=True, exist_ok=True)
    data = np.column_stack([signals[n] for n in names]) if names else np.empty((0, 0))
    np.savez_compressed(str(results_dir / 'signals.npz'),
                        data=data, names=np.array(names, dtype=object))
    meta = {
        'signal_names': names,
        'n_signals': len(names),
        'n_samples': int(n_samples),
        'sampling_rate': float(sampling_rate),
        'source': source,
        'batch_type': batch_type,
        'saved': datetime.now().isoformat(),
    }
    with open(str(results_dir / 'signals_meta.json'), 'w') as f:
        json.dump(meta, f, indent=2)


def _load_signals(results_dir: Path):
    """Reload cached signals → (names, signals_dict, sampling_rate, n_samples)."""
    npz = results_dir / 'signals.npz'
    meta_p = results_dir / 'signals_meta.json'
    if not npz.exists():
        raise FileNotFoundError(
            f"No cached signals in {results_dir.name}. Run the load step first.")
    z = np.load(str(npz), allow_pickle=True)
    names = [str(n) for n in z['names'].tolist()]
    data = z['data']
    signals = {n: np.asarray(data[:, i], dtype=np.float64) for i, n in enumerate(names)}
    sr, n = 1.0, data.shape[0] if data.ndim == 2 else 0
    if meta_p.exists():
        m = json.load(open(str(meta_p)))
        sr = float(m.get('sampling_rate', 1.0))
        n = int(m.get('n_samples', n))
    return names, signals, sr, n


# ═════════════════════════════════════════════════════════════════════════════
# CORE: run all pairs through the engine
# ═════════════════════════════════════════════════════════════════════════════

_MLABEL = {
    'ccm': 'CCM', 'granger_causality': 'Granger', 'pearson': 'Pearson',
    'spearman': 'Spearman', 'mutual_information': 'MI', 'transfer_entropy': 'TE',
    'pearson_lagscan': 'Lag-scanned Pearson',
}


def _row_from_result(a, b, method_name, r, alpha):
    """Build a pair_results row (dual-p schema) from one engine method result."""
    def _f(v):
        return float(v) if (v is not None and np.isfinite(v)) else None

    if not isinstance(r, dict) or 'error' in r:
        return {
            'signal_x': a, 'signal_y': b, 'method': method_name,
            'statistic': None, 'p_value': None, 'p_best': None,
            'significant': False, 'effect_size': None,
            'error': (r.get('error') if isinstance(r, dict) else 'error'),
        }, False

    stat = r.get('statistic', np.nan)
    p_emp = r.get('p_empirical', np.nan)       # surrogate (empirical) p
    p_par = r.get('p_value', np.nan)           # parametric / analytic p
    p_best = p_emp if np.isfinite(p_emp) else p_par
    sig = bool(np.isfinite(p_best) and p_best < alpha)
    null = r.get('null_distribution', None)

    row = {
        'signal_x': a, 'signal_y': b, 'method': method_name,
        'statistic': _f(stat),
        'p_parametric': _f(p_par),
        'sig_parametric': bool(np.isfinite(p_par) and p_par < alpha),
        'p_surrogate': _f(p_emp),
        'sig_surrogate': bool(np.isfinite(p_emp) and p_emp < alpha),
        'surr_mean': _f(r.get('surrogate_mean', np.nan)),
        'surr_std': _f(r.get('surrogate_std', np.nan)),
        'n_surrogates': int(r.get('n_surrogates', 0) or 0),
        'p_value': _f(p_par),
        'p_best': _f(p_best),
        'significant': sig,
        'effect_size': _f(r.get('effect_size', np.nan)),
        'direction': r.get('direction', ''),
        'signal_version': r.get('signal_version', ''),
        'null_distribution': (list(map(float, null)) if null is not None else None),
    }
    if method_name == 'pearson_lagscan':
        d = r.get('details', {}) or {}
        row['sig_parametric'] = bool(d.get('significant_parametric', False))
        row['r_best'] = _f(d.get('r_best', np.nan))
        row['lag_best'] = d.get('lag_best')
        row['threshold_parametric'] = _f(d.get('threshold_parametric', np.nan))
    return row, sig


def _run_one_pair_all_methods(a, b, x, y, assoc_config, alpha):
    """Worker: run ALL methods on one pair via a single Associa.run.

    Module-level + picklable so joblib can ship it to worker processes.
    Returns a list of (row, significant) tuples.
    """
    Associa = _get_engine()
    try:
        engine = Associa(config=assoc_config)
        raw = engine.run(np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64))
        results = raw.get('results', raw)
        out = []
        for method_name, r in results.items():
            out.append(_row_from_result(a, b, method_name, r, alpha))
        return out
    except Exception as e:
        return [({
            'signal_x': a, 'signal_y': b, 'method': 'error',
            'statistic': None, 'p_value': None, 'p_best': None,
            'significant': False, 'effect_size': None, 'error': str(e),
        }, False)]


def _run_pairs_parallel(signals, pairs, assoc_config, alpha, n_jobs, progress_cb=None,
                        cancel_evt=None):
    """CPU-parallel path: joblib over pairs (each worker = one pair, all methods).

    Progress is reported per completed pair (worker processes can't stream
    per-method status), so the board shows pair progress + worker count.
    """
    from joblib import Parallel, delayed

    all_methods = list(assoc_config.get('methods', {}).keys())
    total = max(len(pairs), 1)
    pair_results: List[Dict] = []
    n_significant = 0
    t0 = time.time()

    def _emit(done, is_done=False):
        if not progress_cb:
            return
        elapsed = time.time() - t0
        eta = (elapsed / done * (total - done)) if done > 0 else None
        max_surr = max([int(assoc_config['methods'].get(m, {}).get('n_surrogates', 0) or 0)
                        for m in all_methods] or [0])
        board = {
            'title': 'Coupling Analysis (parallel)',
            'status': 'done' if is_done else 'running',
            'pct': round(done / total * 100, 1),
            'unit': done, 'unit_total': total, 'pairs_total': len(pairs),
            'current_pair': f'{n_jobs} workers',
            'current_method': f'{done}/{total} pairs',
            'current_surrogates': max_surr,
            'elapsed_s': round(elapsed, 1),
            'eta_s': (round(eta, 1) if eta is not None else None),
            'n_significant': n_significant,
            'methods': [
                {'name': m, 'label': _MLABEL.get(m, m),
                 'surrogates': int(assoc_config['methods'].get(m, {}).get('n_surrogates', 0) or 0),
                 'status': 'done' if is_done else 'running'}
                for m in all_methods
            ],
        }
        progress_cb(done, total, phase='analysis',
                    message=f'{done}/{total} pairs · {n_jobs} workers', sa_board=board)

    _emit(0)
    tasks = (delayed(_run_one_pair_all_methods)(a, b, signals[a], signals[b], assoc_config, alpha)
             for (a, b) in pairs)
    # In a PyInstaller-frozen app, joblib's default 'loky' backend spawns workers by
    # re-launching the executable, which PyInstaller cannot handle (workers die with
    # TerminatedWorkerError / the app restarts on new ports). The stdlib 'multiprocessing'
    # backend IS supported by PyInstaller's runtime hook together with the launcher's
    # multiprocessing.freeze_support(), so use it when frozen; keep loky in dev.
    import sys as _sys
    backend = 'multiprocessing' if getattr(_sys, 'frozen', False) else 'loky'
    try:
        gen = Parallel(n_jobs=int(n_jobs), backend=backend, return_as='generator')(tasks)
    except TypeError:
        # Older joblib without return_as: fall back to blocking list
        gen = Parallel(n_jobs=int(n_jobs), backend=backend)(tasks)

    done = 0
    for pair_rows in gen:
        for row, sig in pair_rows:
            pair_results.append(row)
            if sig:
                n_significant += 1
        done += 1
        _emit(done)
        if cancel_evt is not None and cancel_evt.is_set():
            try:
                gen.close()            # stop dispatching the remaining pairs
            except Exception:
                pass
            raise _RunCancelled(done)

    _emit(total, is_done=True)
    return pair_results, n_significant


class _RunCancelled(Exception):
    """Raised when the user presses Stop (cancel_evt set)."""
    def __init__(self, n_done: int):
        super().__init__(f'cancelled after {n_done} pair(s)')
        self.n_done = n_done


def _run_pairs(signals: Dict, pairs: List[Tuple[str, str]], assoc_config: Dict,
               alpha: float, progress_cb=None, n_jobs: int = 1, cancel_evt=None):
    """Run each pair method-by-method so progress can report the current method.

    Emits a live 'sa_board' payload via progress_cb for a fixed-template GUI board.
    When n_jobs != 1, dispatches to the CPU-parallel (joblib-over-pairs) path.
    """
    # CPU parallel over pairs (joblib). Falls back to serial if joblib missing.
    if n_jobs and int(n_jobs) != 1 and len(pairs) > 1:
        try:
            return _run_pairs_parallel(signals, pairs, assoc_config, alpha,
                                       int(n_jobs), progress_cb=progress_cb,
                                       cancel_evt=cancel_evt)
        except _RunCancelled:
            raise
        except ImportError:
            print("[Associa] joblib not available — falling back to serial CPU.")
        except Exception as e:
            print(f"[Associa] parallel path failed ({e}) — falling back to serial CPU.")

    Associa = _get_engine()
    all_methods = list(assoc_config.get('methods', {}).keys())
    n_methods = max(len(all_methods), 1)
    pair_results: List[Dict] = []
    n_significant = 0

    unit = 0
    unit_total = max(len(pairs) * n_methods, 1)
    t0 = time.time()

    def _emit(cur_pair, cur_method, status_map, done=False):
        if not progress_cb:
            return
        elapsed = time.time() - t0
        eta = (elapsed / unit * (unit_total - unit)) if unit > 0 else None
        surr = 0
        if cur_method:
            surr = int(assoc_config['methods'].get(cur_method, {}).get('n_surrogates', 0) or 0)
        board = {
            'title': 'Coupling Analysis',
            'status': 'done' if done else 'running',
            'pct': round(unit / unit_total * 100, 1),
            'unit': unit, 'unit_total': unit_total,
            'pairs_total': len(pairs),
            'current_pair': cur_pair,
            'current_method': _MLABEL.get(cur_method, cur_method) if cur_method else None,
            'current_surrogates': surr,
            'elapsed_s': round(elapsed, 1),
            'eta_s': (round(eta, 1) if eta is not None else None),
            'n_significant': n_significant,
            'methods': [
                {'name': m, 'label': _MLABEL.get(m, m),
                 'surrogates': int(assoc_config['methods'].get(m, {}).get('n_surrogates', 0) or 0),
                 'status': status_map.get(m, 'pending')}
                for m in all_methods
            ],
        }
        msg = (f'{cur_pair} · {_MLABEL.get(cur_method, cur_method)}'
               if cur_method else (cur_pair or 'Done'))
        progress_cb(unit, unit_total, phase='analysis', message=msg, sa_board=board)

    for (a, b) in pairs:
        pair_label = f'{a} ↔ {b}'
        status_map = {m: 'pending' for m in all_methods}
        x, y = signals[a], signals[b]

        for method_name in all_methods:
            if cancel_evt is not None and cancel_evt.is_set():
                raise _RunCancelled(len({(r['signal_x'], r['signal_y']) for r in pair_results}))
            status_map[method_name] = 'running'
            _emit(pair_label, method_name, status_map)
            try:
                single_cfg = {k: v for k, v in assoc_config.items() if k != 'methods'}
                single_cfg['methods'] = {method_name: assoc_config['methods'][method_name]}
                engine = Associa(config=single_cfg)
                raw = engine.run(x, y)
                results = raw.get('results', raw)
                r = results.get(method_name, {'error': 'no result'})
                row, sig = _row_from_result(a, b, method_name, r, alpha)
            except Exception as e:
                row, sig = {
                    'signal_x': a, 'signal_y': b, 'method': method_name,
                    'statistic': None, 'p_value': None, 'p_best': None,
                    'significant': False, 'effect_size': None, 'error': str(e),
                }, False
            pair_results.append(row)
            if sig:
                n_significant += 1
            status_map[method_name] = 'done'
            unit += 1
            _emit(pair_label, None, status_map)

    _emit(None, None, {m: 'done' for m in all_methods}, done=True)
    return pair_results, n_significant


# ═════════════════════════════════════════════════════════════════════════════
# SAVE RESULTS (pickle + csv + json + plots + run history)
# ═════════════════════════════════════════════════════════════════════════════

_SUMMARY_COLS = ['signal_x', 'signal_y', 'method', 'statistic',
                 'p_parametric', 'sig_parametric', 'p_surrogate', 'sig_surrogate',
                 'surr_mean', 'surr_std', 'n_surrogates',
                 'p_best', 'significant', 'effect_size',
                 'r_best', 'lag_best', 'threshold_parametric']   # last three: lag-scanned Pearson only


def _pairs_wide(rows: List[Dict]) -> pd.DataFrame:
    """One row per pair; per method: statistic, parametric and surrogate p, significance
    (and best lag / signed r* for lag-scanned Pearson). Easier to read than the long table."""
    out: Dict[Tuple[str, str], Dict] = {}
    for r in rows:
        m = r.get('method')
        if not m or m == 'error':
            continue
        key = (r.get('signal_x'), r.get('signal_y'))
        row = out.setdefault(key, {'signal_x': key[0], 'signal_y': key[1]})
        lab = _MLABEL.get(m, m).replace(' ', '_').replace('-', '_')
        row[f'{lab}_statistic'] = r.get('statistic')
        row[f'{lab}_p_param'] = r.get('p_parametric')
        row[f'{lab}_p_surr'] = r.get('p_surrogate')
        row[f'{lab}_significant'] = bool(r.get('significant'))
        if m == 'pearson_lagscan':
            row[f'{lab}_lag_best'] = r.get('lag_best')
            row[f'{lab}_r_best'] = r.get('r_best')
    df = pd.DataFrame(list(out.values()))
    sig_cols = [c for c in df.columns if c.endswith('_significant')]
    if sig_cols:
        df['n_sig_methods'] = df[sig_cols].sum(axis=1).astype(int)
    return df


def _write_readme(results_dir: Path, result: Dict, mode: str):
    """Write a human-readable README.md documenting the run for future follow-up."""
    cfg = result.get('config', {}) or {}
    methods = result.get('methods', [])
    rows = result.get('pair_results', [])
    names = result.get('signal_names', [])
    pairs = result.get('pairs', [])

    # per-method surrogate count (as actually used), read from the result rows
    surr_by_method = {}
    for r in rows:
        m = r.get('method')
        if m and m not in surr_by_method and r.get('n_surrogates') is not None:
            surr_by_method[m] = r.get('n_surrogates')

    def _g(k, d=''):
        return cfg.get(k, d)

    L = []
    L.append(f"# Signal Associa — {mode.capitalize()} Run")
    L.append("")
    L.append(f"- **Run ID:** `{result.get('run_id', '')}`")
    L.append(f"- **Generated:** {datetime.now().isoformat(timespec='seconds')}")
    L.append(f"- **Mode:** {mode}")
    if mode == 'batch':
        _bt = result.get('batch_type', 'all_pairs')
        _btlabel = 'pre-paired columns (consecutive 2-col pairs)' if _bt == 'paired' else 'pairwise (all N-choose-2)'
        L.append(f"- **Batch type:** {_btlabel}")
    L.append("")

    L.append("## Input")
    L.append(f"- **Source file:** `{result.get('source_file') or _g('input_file') or _g('file_path') or 'n/a'}`")
    L.append(f"- **Signals ({len(names)}):** {', '.join(names) if names else 'n/a'}")
    L.append(f"- **Samples:** {result.get('n_samples', 'n/a')}")
    L.append(f"- **Sampling rate:** {result.get('sampling_rate', 1.0)} Hz")
    L.append(f"- **Pairs analysed:** {len(pairs)}")
    L.append("")

    L.append("## Methods & Settings")
    L.append(f"- **Significance level (α):** {result.get('alpha', 0.05)}")
    stat_method = _g('stat_method', _g('method', 'auto'))
    L.append(f"- **Stationarizer:** {stat_method}"
             + (f" (band {_g('bp_low', 0.008)}–{_g('bp_high', 0.25)} Hz)"
                if stat_method == 'bandpass' else ""))
    L.append(f"- **Surrogate method:** {_g('surr_method', 'iaaft')}")
    L.append(f"- **Surrogates requested (N):** {_g('surr_n', 100)}")
    L.append("")
    L.append("| Method | Surrogates used | Notes |")
    L.append("|---|---|---|")
    _notes = {
        'ccm': f"E={_g('ccm_E', 2)}, τ={_g('ccm_tau', 1)}, boots={_g('ccm_n_boot', 20)}",
        'granger_causality': f"maxlag={_g('gc_maxlag', 5)}, criterion={_g('gc_criterion', 'aic')}",
        'pearson': 'linear correlation',
        'pearson_lagscan': f"lags ±{_g('lag_max_lag', 15)}; |r*| vs 1.96/√N and IAAFT surrogates",
        'mutual_information': 'nonlinear dependence',
        'transfer_entropy': 'directed information',
    }
    for m in methods:
        L.append(f"| {_MLABEL.get(m, m)} | {surr_by_method.get(m, '—')} | {_notes.get(m, '')} |")
    L.append("")

    L.append("## Summary")
    L.append(f"- **Pairs:** {len(pairs)}")
    L.append(f"- **Significant (method-hits):** {result.get('n_significant', 0)}")
    L.append(f"- **Elapsed:** {result.get('elapsed_s', 'n/a')} s")
    _nj = result.get('n_jobs', 1)
    L.append(f"- **CPU workers:** {'serial (1)' if _nj == 1 else _nj}")
    L.append("")

    # Results table (compact)
    L.append("## Results")
    L.append("| Pair | Method | Statistic | p (param) | p (surr) | Significant |")
    L.append("|---|---|---|---|---|---|")

    def _fmt(v):
        if v is None:
            return '—'
        try:
            v = float(v)
        except (TypeError, ValueError):
            return str(v)
        return f"{v:.3g}"

    for r in rows:
        if r.get('method') == 'error':
            continue
        L.append(f"| {r.get('signal_x')} ↔ {r.get('signal_y')} | {_MLABEL.get(r.get('method'), r.get('method'))} "
                 f"| {_fmt(r.get('statistic'))} | {_fmt(r.get('p_parametric'))} | {_fmt(r.get('p_surrogate'))} "
                 f"| {'yes' if r.get('significant') else 'no'} |")
    L.append("")

    L.append("## Files in this directory")
    L.append("- `associa_results.pkl` — full results (incl. surrogate null distributions), for re-plotting")
    L.append("- `summary.csv` / `summary.json` — flat per-pair-per-method table")
    L.append("- `meta.json` — machine-readable run metadata")
    L.append("- `plots/` — figures (null distributions, matrices, network, …)")
    L.append("- `runs/<run_id>/` — timestamped copy of this run")
    L.append("")

    with open(str(results_dir / 'README.md'), 'w', encoding='utf-8') as f:
        f.write("\n".join(L))


def _save_results(results_dir: Path, result: Dict, mode: str, progress_cb=None):
    """Write pickle, summary.csv/json, meta.json, README.md, plots/, and a run-history copy."""
    results_dir.mkdir(parents=True, exist_ok=True)

    # Full pickle (includes null distributions + signals for re-plotting)
    with open(str(results_dir / 'associa_results.pkl'), 'wb') as f:
        pickle.dump(result, f)

    # Flat summary table (drop bulky null_distribution)
    rows = [{k: r.get(k) for k in _SUMMARY_COLS} for r in result['pair_results']]
    pd.DataFrame(rows).to_csv(str(results_dir / 'summary.csv'), index=False)
    with open(str(results_dir / 'summary.json'), 'w') as f:
        json.dump({'columns': _SUMMARY_COLS, 'rows': rows}, f, indent=2, default=str)
    _pairs_wide(rows).to_csv(str(results_dir / 'pairs_summary.csv'), index=False)

    # Meta
    meta = {
        'run_id': result.get('run_id'),
        'mode': mode,
        'signal_names': result.get('signal_names', []),
        'n_signals': len(result.get('signal_names', [])),
        'n_pairs': len(result.get('pairs', [])),
        'n_significant': result.get('n_significant', 0),
        'methods': result.get('methods', []),
        'elapsed_s': result.get('elapsed_s'),
        'alpha': result.get('alpha', 0.05),
        'batch_type': result.get('batch_type', 'all_pairs'),
        'config': result.get('config', {}),
        'timestamp': datetime.now().isoformat(),
    }
    with open(str(results_dir / 'meta.json'), 'w') as f:
        json.dump(meta, f, indent=2, default=str)

    # README.md — human-readable run documentation for future follow-up
    try:
        _write_readme(results_dir, result, mode)
    except Exception as e:
        print(f"[Associa] README generation failed: {e}")

    # Plots
    if progress_cb:
        progress_cb(9, 10, phase='plotting', message='Rendering figures...')
    plots_dir = results_dir / 'plots'
    plots_dir.mkdir(exist_ok=True)
    Plotter = _get_plotter()
    plotter = Plotter(result, save=True, save_dir=str(plots_dir), formats=('png',))
    if mode == 'batch':
        plotter.render_batch()
    else:
        plotter.render_single()

    # Run-history copy
    run_id = result.get('run_id')
    if run_id:
        run_dir = results_dir / 'runs' / run_id
        (run_dir / 'plots').mkdir(parents=True, exist_ok=True)
        for fn in ('summary.csv', 'pairs_summary.csv', 'summary.json', 'meta.json', 'README.md'):
            src = results_dir / fn
            if src.exists():
                shutil.copy2(str(src), str(run_dir / fn))
        for png in plots_dir.glob('*.png'):
            shutil.copy2(str(png), str(run_dir / 'plots' / png.name))

    return meta


def _resolve_csv(project, p: Dict) -> Optional[str]:
    """Resolve the CSV path param against the project data root."""
    raw = p.get('input_file') or p.get('file_path') or p.get('csv_path') or ''
    if not raw:
        return None
    resolved = project.resolve_data_path(raw)
    return str(resolved) if resolved is not None else None


# ═════════════════════════════════════════════════════════════════════════════
# RUNNERS
# ═════════════════════════════════════════════════════════════════════════════

def _do_load(project, ws_id, pipeline_id, step_id, params, results_dir,
             expected: str, progress_cb=None):
    """Shared load step for both single (import) and batch (batch_setup)."""
    if results_dir.exists():
        shutil.rmtree(str(results_dir))
    results_dir.mkdir(parents=True, exist_ok=True)

    p = _flatten_params(params)
    csv_path = _resolve_csv(project, p)
    if not csv_path:
        return {"status": "error",
                "error_msg": "No CSV selected. Click Browse to choose a signals file."}

    has_header = p.get('has_header', 'auto')
    sampling_rate = float(p.get('sampling_rate', 1.0) or 1.0)
    # Batch type: 'all_pairs' (pairwise N-choose-2) or 'paired' (consecutive 2-col pairs)
    batch_type = p.get('batch_type', 'all_pairs') if expected == 'batch' else 'all_pairs'

    if progress_cb:
        progress_cb(1, 3, phase='loading', message='Reading CSV...')
    names, signals, n_samples = _load_signals_csv(csv_path, has_header)
    n_signals = len(names)

    # Mode / validation
    if expected == 'single' and n_signals != 2:
        return {"status": "error",
                "error_msg": f"Single expects exactly 2 columns; found {n_signals}. "
                             f"Use Signal Associa — Batch for multi-signal files."}
    if expected == 'batch' and n_signals < 3:
        return {"status": "error",
                "error_msg": f"Batch expects 3+ columns; found {n_signals}. "
                             f"Use Signal Associa — Single for a 2-column file."}
    if expected == 'batch' and batch_type == 'paired' and n_signals % 2 != 0:
        return {"status": "error",
                "error_msg": f"Pre-paired mode needs an even number of columns "
                             f"(each consecutive pair = one analysis); found {n_signals}."}

    _save_signals(results_dir, names, signals, sampling_rate, n_samples,
                  source=os.path.basename(csv_path), batch_type=batch_type)

    # Preview traces
    if progress_cb:
        progress_cb(2, 3, phase='preview', message='Rendering signal preview...')
    plots_dir = results_dir / 'plots'
    plots_dir.mkdir(exist_ok=True)
    Plotter = _get_plotter()
    Plotter({'signal_names': names, 'signals': signals,
             'sampling_rate': sampling_rate}, save=True,
            save_dir=str(plots_dir), formats=('png',)).signal_traces()

    if n_signals == 2:
        n_pairs = 1
    elif batch_type == 'paired':
        n_pairs = n_signals // 2
    else:
        n_pairs = len(list(combinations(names, 2)))
    type_label = ('' if n_signals == 2
                  else (' · pre-paired columns' if batch_type == 'paired' else ' · pairwise'))
    return {"status": "done", "outputs": {
        "message": f"Loaded {n_signals} signals × {n_samples} samples "
                   f"({n_pairs} pair(s){type_label})",
        "n_signals": n_signals, "n_samples": n_samples, "n_pairs": n_pairs,
        "batch_type": batch_type,
        "signal_names": names, "mode": ('single' if n_signals == 2 else 'batch'),
    }}


def _do_analyze(project, ws_id, pipeline_id, step_id, params, results_dir,
                mode: str, load_step: str, progress_cb=None, cancel_evt=None):
    """Shared analysis step for single (analysis) and batch (batch_run)."""
    if results_dir.exists():
        shutil.rmtree(str(results_dir))
    results_dir.mkdir(parents=True, exist_ok=True)

    load_dir = project.get_results_dir(ws_id, pipeline_id, load_step)
    names, signals, sampling_rate, n_samples = _load_signals(load_dir)

    # Recover provenance + batch type from the load step's metadata
    source_file = ''
    batch_type = 'all_pairs'
    _meta_p = load_dir / 'signals_meta.json'
    if _meta_p.exists():
        try:
            _m = json.load(open(str(_meta_p)))
            source_file = _m.get('source', '')
            batch_type = _m.get('batch_type', 'all_pairs')
        except Exception:
            pass

    if mode == 'single':
        if len(names) != 2:
            return {"status": "error",
                    "error_msg": "Expected 2 signals for single analysis."}
        pairs = [(names[0], names[1])]
    elif batch_type == 'paired':
        # Consecutive columns form independent pairs: (0,1), (2,3), ...
        pairs = [(names[i], names[i + 1]) for i in range(0, len(names) - 1, 2)]
    else:
        pairs = list(combinations(names, 2))

    p = _flatten_params(params)
    assoc_config, alpha, methods = _build_assoc_config(p, sampling_rate)

    # CPU workers (joblib over pairs). 1 = serial per-method board; >1 or -1 = parallel.
    try:
        n_jobs = int(float(p.get('n_jobs', p.get('n_workers', 1)) or 1))
    except (TypeError, ValueError):
        n_jobs = 1
    if _as_bool(p.get('ccm_gpu', False)) and n_jobs != 1:
        print(f"[Associa] GPU enabled: running pairs in one process (CPU workers {n_jobs} -> 1) "
              f"so worker processes do not compete for the GPU.")
        n_jobs = 1

    if progress_cb:
        progress_cb(0, len(pairs), phase='analysis',
                    message=f'Running {len(pairs)} pair(s) × {len(methods)} method(s)'
                            + (f' · {n_jobs} workers' if n_jobs != 1 else ''))

    t0 = time.time()
    try:
        pair_results, n_significant = _run_pairs(signals, pairs, assoc_config,
                                                 alpha, progress_cb=progress_cb,
                                                 n_jobs=n_jobs, cancel_evt=cancel_evt)
    except _RunCancelled as c:
        return {"status": "cancelled",
                "outputs": {"message": f"Stopped by user after {c.n_done}/{len(pairs)} pair(s); "
                                       f"nothing saved — previous results kept."}}
    elapsed = round(time.time() - t0, 2)

    run_id = f'run_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    result = {
        'run_id': run_id,
        'mode': mode,
        'signal_names': names,
        'sampling_rate': sampling_rate,
        'n_samples': n_samples,
        'signals': {n: signals[n] for n in names},   # for re-plotting traces
        'pairs': pairs,
        'methods': methods,
        'pair_results': pair_results,
        'n_significant': n_significant,
        'elapsed_s': elapsed,
        'alpha': alpha,
        'config': p,
        'source_file': source_file,
        'batch_type': batch_type,
        'n_jobs': n_jobs,
    }

    _save_results(results_dir, result, mode, progress_cb=progress_cb)

    # Compact per-method report for the run panel template (no null distributions)
    report = [
        {
            'signal_x': r.get('signal_x'), 'signal_y': r.get('signal_y'),
            'method': r.get('method'), 'statistic': r.get('statistic'),
            'p_parametric': r.get('p_parametric'), 'p_surrogate': r.get('p_surrogate'),
            'p_value': r.get('p_best'), 'significant': bool(r.get('significant')),
            'lag_best': r.get('lag_best'), 'r_best': r.get('r_best'),   # lag-scanned Pearson only
        }
        for r in pair_results if r.get('method') != 'error'
    ]

    # Final (done) board so the live board persists after the run completes
    n_units = max(len(pairs) * max(len(methods), 1), 1)
    sa_board = {
        'title': 'Coupling Analysis', 'status': 'done', 'pct': 100.0,
        'unit': n_units, 'unit_total': n_units,
        'pairs_total': len(pairs),
        'current_pair': None, 'current_method': None, 'current_surrogates': 0,
        'elapsed_s': elapsed, 'eta_s': 0.0, 'n_significant': n_significant,
        'methods': [
            {'name': m, 'label': _MLABEL.get(m, m),
             'surrogates': int(assoc_config['methods'].get(m, {}).get('n_surrogates', 0) or 0),
             'status': 'done'}
            for m in methods
        ],
    }

    return {"status": "done", "outputs": {
        "message": f"{run_id}: {len(pairs)} pair(s), {n_significant} significant "
                   f"(α={alpha:g}) in {elapsed}s",
        "run_id": run_id, "n_pairs": len(pairs), "n_significant": n_significant,
        "methods": methods, "elapsed_s": elapsed, "alpha": alpha,
        "batch_type": batch_type,
        "sa_board": sa_board,
        "sa_report": report,
    }}


def _do_batch_results(project, ws_id, pipeline_id, results_dir, progress_cb=None):
    """Aggregate view: re-render matrices/network from the batch_run pickle."""
    if results_dir.exists():
        shutil.rmtree(str(results_dir))
    results_dir.mkdir(parents=True, exist_ok=True)

    run_dir = project.get_results_dir(ws_id, pipeline_id, 'batch_run')
    pkl = run_dir / 'associa_results.pkl'
    if not pkl.exists():
        return {"status": "error",
                "error_msg": "No batch results found. Run 'Batch Run' first."}

    with open(str(pkl), 'rb') as f:
        result = pickle.load(f)

    batch_type = result.get('batch_type', 'all_pairs')
    if progress_cb:
        progress_cb(5, 10, phase='plotting', message='Rendering aggregate figures...')
    plots_dir = results_dir / 'plots'
    plots_dir.mkdir(exist_ok=True)
    Plotter = _get_plotter()
    plotter = Plotter(result, save=True, save_dir=str(plots_dir), formats=('png',))

    if batch_type == 'paired':
        # Independent pairs → combined pairs-summary (no matrix/network)
        plotter.pairs_summary()
    else:
        # Pairwise → N×N significance matrix (+ CSV), coupling matrices, network
        names = result.get('signal_names', [])
        idx = {n: i for i, n in enumerate(names)}
        N = len(names)
        counts = np.zeros((N, N), dtype=int)
        for r in result.get('pair_results', []):
            if r.get('significant') and r.get('signal_x') in idx and r.get('signal_y') in idx:
                a, b = idx[r['signal_x']], idx[r['signal_y']]
                counts[a, b] += 1
                counts[b, a] += 1
        pd.DataFrame(counts, index=names, columns=names).to_csv(
            str(results_dir / 'significance_matrix.csv'))
        plotter.significance_matrix()
        plotter.coupling_matrix(value='statistic')
        plotter.coupling_matrix(value='neglog_p')
        plotter.coupling_network(method=None)

    total_sig = int(sum(1 for r in result.get('pair_results', []) if r.get('significant')))
    return {"status": "done", "outputs": {
        "message": f"Aggregated {len(result.get('pairs', []))} pairs — "
                   f"{total_sig} significant method-hits",
        "n_significant": total_sig,
    }}


# ── Public dispatch entry points (called from app.py) ───────────────────────

def _run_signal_associa(project, ws_id, pipeline_id, step_id, params,
                        results_dir, progress_cb=None, cancel_evt=None):
    """Single-pair pipeline: import → analysis."""
    try:
        if step_id == 'import':
            return _do_load(project, ws_id, pipeline_id, step_id, params,
                            results_dir, expected='single', progress_cb=progress_cb)
        elif step_id == 'analysis':
            return _do_analyze(project, ws_id, pipeline_id, step_id, params,
                               results_dir, mode='single', load_step='import',
                               progress_cb=progress_cb, cancel_evt=cancel_evt)
        return {"status": "error",
                "error_msg": f"Unknown Signal Associa step: {step_id}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "error_msg": str(e)}


def _run_signal_associa_batch(project, ws_id, pipeline_id, step_id, params,
                              results_dir, progress_cb=None, cancel_evt=None):
    """Batch pipeline: batch_setup → batch_run → batch_results."""
    try:
        if step_id == 'batch_setup':
            return _do_load(project, ws_id, pipeline_id, step_id, params,
                            results_dir, expected='batch', progress_cb=progress_cb)
        elif step_id == 'batch_run':
            return _do_analyze(project, ws_id, pipeline_id, step_id, params,
                               results_dir, mode='batch', load_step='batch_setup',
                               progress_cb=progress_cb, cancel_evt=cancel_evt)
        elif step_id == 'batch_results':
            return _do_batch_results(project, ws_id, pipeline_id, results_dir,
                                     progress_cb=progress_cb)
        return {"status": "error",
                "error_msg": f"Unknown Signal Associa batch step: {step_id}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "error_msg": str(e)}
