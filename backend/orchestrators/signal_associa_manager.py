"""
Associa Manager — backend orchestrator for the Associa CelLAB module.

Wraps shared_modules/associa/ engine. Handles:
  - CSV loading (auto-detect single/batch)
  - Config assembly (stationarizer, methods, surrogate)
  - Run dispatch (single pair or batch C(N,2))
  - Results storage (timestamped run folders)

Location: backend/associa_manager.py
"""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Lazy import of shared_modules/associa
_associa_module = None


def _get_associa():
    """Lazy-load the Associa engine."""
    global _associa_module
    if _associa_module is None:
        import sys
        # This file lives in backend/orchestrators/, engine in backend/shared_modules/
        root = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(root / 'shared_modules'))
        from signal_associa.signal_associa import Associa
        _associa_module = Associa
    return _associa_module


class AssociaState:
    """Per-pipeline state for one Associa instance."""

    def __init__(self):
        self.signals: Dict[str, np.ndarray] = {}   # name → 1D array
        self.signal_names: List[str] = []
        self.n_samples: int = 0
        self.mode: str = ''   # 'single' or 'batch'
        self.pairs: List[Tuple[str, str]] = []
        self.file_path: str = ''
        self.sampling_rate: float = 1.0
        self.config: Dict = {}
        self.runs: Dict[str, Dict] = {}  # run_id → results
        self.output_dir: Optional[Path] = None


class AssociaManager:
    """
    Manages Associa instances per pipeline. Stateless between requests
    except for per-pipeline AssociaState.
    """

    def __init__(self):
        self._states: Dict[str, AssociaState] = {}

    def _require(self, pipeline_id: str) -> AssociaState:
        if pipeline_id not in self._states:
            self._states[pipeline_id] = AssociaState()
        return self._states[pipeline_id]

    # ─── Load CSV ────────────────────────────────────────────────────────────

    def load_csv(self, pipeline_id: str, file_path: str,
                 has_header: str = 'auto') -> Dict:
        """
        Load a CSV/TSV file. Auto-detect single vs batch.

        Returns:
            { mode, n_signals, n_samples, n_pairs, signal_names }
        """
        state = self._require(pipeline_id)
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Detect separator
        sep = '\t' if path.suffix.lower() in ('.tsv', '.tab') else ','

        # Read first line to detect header
        with open(str(path), 'r') as f:
            first_line = f.readline().strip()

        if has_header == 'auto':
            # If first row has any non-numeric value → header
            parts = first_line.split(sep)
            has_header_bool = any(not _is_numeric(p.strip()) for p in parts)
        else:
            has_header_bool = has_header == 'yes'

        # Load DataFrame
        df = pd.read_csv(str(path), sep=sep,
                         header=0 if has_header_bool else None)

        # Build signals dict
        signal_names = [str(c) for c in df.columns]
        if not has_header_bool:
            signal_names = [f'Signal_{i}' for i in range(len(df.columns))]

        signals = {}
        for i, col in enumerate(df.columns):
            arr = df[col].values.astype(np.float64)
            name = signal_names[i]
            signals[name] = arr

        n_signals = len(signals)
        n_samples = len(df)

        # Determine mode
        if n_signals == 2:
            mode = 'single'
            names = list(signals.keys())
            pairs = [(names[0], names[1])]
        elif n_signals > 2:
            mode = 'batch'
            names = list(signals.keys())
            pairs = list(combinations(names, 2))
        else:
            raise ValueError(f"CSV must have at least 2 columns (found {n_signals})")

        # Store state
        state.signals = signals
        state.signal_names = list(signals.keys())
        state.n_samples = n_samples
        state.mode = mode
        state.pairs = pairs
        state.file_path = file_path
        state.output_dir = path.parent / 'associa_results'

        return {
            'mode': mode,
            'n_signals': n_signals,
            'n_samples': n_samples,
            'n_pairs': len(pairs),
            'signal_names': state.signal_names,
        }

    # ─── Run Analysis ────────────────────────────────────────────────────────

    def run(self, pipeline_id: str, config: Dict = None) -> Dict:
        """
        Run Associa on all pairs.

        Config structure:
        {
            stationarizer: { method, bp_low, bp_high },
            methods: { m_ccm, m_granger, m_pearson, m_lagscan, m_mi, m_te,
                       ccm_E, ccm_tau, ccm_n_boot, gc_maxlag, gc_criterion,
                       lag_max_lag, lag_min_overlap },
            surrogate: { method, n, alpha },
        }

        Returns:
            { run_id, n_pairs, n_significant, summary: {columns, rows}, ... }
        """
        state = self._require(pipeline_id)
        if not state.signals:
            raise RuntimeError("No signals loaded. Call load_csv first.")

        Associa = _get_associa()
        config = config or {}

        # Parse method config
        mc = config.get('methods', {})
        active_methods = {}
        surr_cfg = config.get('surrogate', {})
        n_surrogates = int(surr_cfg.get('n', 100))
        alpha = float(surr_cfg.get('alpha', 0.05))
        surr_method = surr_cfg.get('method', 'iaaft')

        if mc.get('m_ccm', True):
            active_methods['ccm'] = {
                'E': int(mc.get('ccm_E', 2)),
                'tau': int(mc.get('ccm_tau', 1)),
                'n_boot': int(mc.get('ccm_n_boot', 20)),
                'signal_version': 'raw',
                'n_surrogates': n_surrogates,
            }
        if mc.get('m_granger'):
            active_methods['granger_causality'] = {
                'maxlag': int(mc.get('gc_maxlag', 5)),
                'criterion': mc.get('gc_criterion', 'aic'),
                'signal_version': 'stationary',
                'n_surrogates': 0,  # Granger uses F-test
            }
        if mc.get('m_pearson'):
            active_methods['pearson'] = {
                'signal_version': 'raw',
                'n_surrogates': 0,
            }
        if mc.get('m_lagscan'):
            # Lag-scanned Pearson (Machacek & Danuser); same lag scan on every IAAFT surrogate
            active_methods['pearson_lagscan'] = {
                'max_lag': int(mc.get('lag_max_lag', 15)),
                'min_overlap': int(mc.get('lag_min_overlap', 10)),
                'signal_version': 'raw',
                'n_surrogates': n_surrogates,
            }
        if mc.get('m_mi'):
            active_methods['mutual_information'] = {
                'signal_version': 'raw',
                'n_surrogates': n_surrogates,
            }
        if mc.get('m_te'):
            active_methods['transfer_entropy'] = {
                'signal_version': 'raw',
                'n_surrogates': n_surrogates,
            }

        if not active_methods:
            active_methods['ccm'] = {
                'E': 2, 'tau': 1, 'n_boot': 20,
                'signal_version': 'raw', 'n_surrogates': n_surrogates,
            }

        # Parse stationarizer config
        sc = config.get('stationarizer', {})
        stat_method = sc.get('stat_method', sc.get('method', 'none'))
        stat_cfg = {}
        if stat_method and stat_method not in ('none', 'None'):
            stat_cfg = {
                'method': stat_method,
                'sampling_rate': float(sc.get('sampling_rate', state.sampling_rate)),
                'bandpass_low': float(sc.get('bp_low', 0.008)),
                'bandpass_high': float(sc.get('bp_high', 0.25)),
            }

        # Build Associa config
        assoc_config = {
            'surrogate': {'method': surr_method, 'n_iterations': 100},
            'methods': active_methods,
        }
        if stat_cfg:
            assoc_config['stationarizer'] = stat_cfg

        # Run on all pairs
        t0 = time.time()
        pair_results = []
        n_significant = 0

        for sig_a, sig_b in state.pairs:
            x = state.signals[sig_a]
            y = state.signals[sig_b]

            try:
                assoc = Associa(config=assoc_config)
                raw = assoc.run(x, y)
                results = raw.get('results', raw)

                for method_name, r in results.items():
                    stat = r.get('statistic', r.get('statistic_xy', np.nan))
                    p = r.get('p_empirical', r.get('p_value', r.get('p_value_xy', np.nan)))
                    sig = bool(np.isfinite(p) and p < alpha)
                    if sig:
                        n_significant += 1

                    pair_results.append({
                        'signal_x': sig_a,
                        'signal_y': sig_b,
                        'method': method_name,
                        'statistic': float(stat) if np.isfinite(stat) else None,
                        'p_value': float(p) if np.isfinite(p) else None,
                        'significant': sig,
                        'effect_size': float(r.get('effect_size', np.nan)) if np.isfinite(r.get('effect_size', np.nan)) else None,
                    })
            except Exception as e:
                pair_results.append({
                    'signal_x': sig_a,
                    'signal_y': sig_b,
                    'method': 'error',
                    'statistic': None,
                    'p_value': None,
                    'significant': False,
                    'effect_size': None,
                    'error': str(e),
                })

        elapsed = time.time() - t0

        # Save run
        run_id = f'run_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        summary_cols = ['signal_x', 'signal_y', 'method', 'statistic', 'p_value', 'significant', 'effect_size']

        run_data = {
            'run_id': run_id,
            'n_pairs': len(state.pairs),
            'n_significant': n_significant,
            'elapsed_s': round(elapsed, 2),
            'config': config,
            'pair_results': pair_results,
            'summary': {
                'columns': summary_cols,
                'rows': pair_results,
            },
        }

        state.runs[run_id] = run_data

        # Save to disk
        if state.output_dir:
            self._save_run(state, run_id, run_data)

        return run_data

    def _save_run(self, state: AssociaState, run_id: str, run_data: Dict):
        """Save run to disk as JSON + CSV."""
        run_dir = state.output_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Summary CSV
        rows = run_data.get('pair_results', [])
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(str(run_dir / 'summary.csv'), index=False)

        # Meta JSON
        meta = {
            'run_id': run_id,
            'mode': state.mode,
            'n_signals': len(state.signal_names),
            'n_pairs': run_data['n_pairs'],
            'n_significant': run_data['n_significant'],
            'elapsed_s': run_data['elapsed_s'],
            'signal_names': state.signal_names,
            'timestamp': datetime.now().isoformat(),
        }
        with open(str(run_dir / 'meta.json'), 'w') as f:
            json.dump(meta, f, indent=2, default=str)

        print(f'[Associa] Saved {run_id} to {run_dir}')

    # ─── Query ───────────────────────────────────────────────────────────────

    def get_state(self, pipeline_id: str) -> Optional[AssociaState]:
        return self._states.get(pipeline_id)

    def has_pipeline(self, pipeline_id: str) -> bool:
        return pipeline_id in self._states


def _is_numeric(s: str) -> bool:
    """Check if a string is numeric."""
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False
