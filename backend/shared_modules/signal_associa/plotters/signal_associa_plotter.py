"""
Signal Associa Plotter
======================
Publication-style matplotlib figures for the Signal Associa shared module.

Consumes the results dict produced by signal_associa_runner (NOT the raw engine
output), so the schema is stable and plotter-controlled:

    results = {
        'mode'          : 'single' | 'batch',
        'signal_names'  : [str, ...],
        'sampling_rate' : float,
        'n_samples'     : int,
        'signals'       : {name: 1D np.ndarray}      # optional (traces)
        'pairs'         : [(a, b), ...],
        'methods'       : [method_name, ...],
        'pair_results'  : [ {signal_x, signal_y, method, statistic,
                             p_value, p_best, significant, effect_size,
                             null_distribution(optional)} , ... ],
        'config'        : {...},
        'run_id'        : str,
        'alpha'         : float,
    }

Mirrors the cornealia_plotter conventions: a class with save=/save_dir=/formats=,
a shared publication style, a `_save_fig` helper, and one method per figure.

Location: backend/plotters/signal_associa_plotter.py
Author: CelLAB / Han Mechanobiology Lab
"""

import os
import math
from itertools import combinations

import numpy as np
import matplotlib
matplotlib.use('Agg')          # headless — server-side rendering
import matplotlib.pyplot as plt


# ============================================================================
# PUBLICATION STYLE
# ============================================================================

def set_publication_style():
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['savefig.facecolor'] = 'white'
    plt.rcParams['savefig.bbox'] = 'tight'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.linewidth'] = 1.4
    plt.rcParams['text.usetex'] = False
    plt.rcParams['mathtext.default'] = 'regular'


COLORS = {
    'raw':       '#0072B2',   # Blue
    'stat':      '#D55E00',   # Vermillion (real statistic)
    'null':      '#999999',   # Gray (null distribution)
    'sig':       '#009E73',   # Green (significant)
    'nonsig':    '#CC5555',   # Red (not significant)
    'accent':    '#5b9bd5',   # App blue
    'neutral':   '#4A4A4A',
}

# Stable per-method color for multi-method plots
METHOD_COLORS = {
    'ccm':                '#0072B2',
    'granger_causality':  '#D55E00',
    'pearson':            '#009E73',
    'spearman':           '#56B4E9',
    'mutual_information':  '#CC79A7',
    'transfer_entropy':   '#E69F00',
}

METHOD_LABELS = {
    'ccm':                'CCM',
    'granger_causality':  'Granger',
    'pearson':            'Pearson',
    'spearman':           'Spearman',
    'mutual_information':  'MI',
    'transfer_entropy':   'TE',
}


def _mlabel(m):
    return METHOD_LABELS.get(m, str(m))


def _mcolor(m, i=0):
    return METHOD_COLORS.get(m, list(METHOD_COLORS.values())[i % len(METHOD_COLORS)])


# ============================================================================
# PLOTTER CLASS
# ============================================================================

class signal_associa_plotter:

    def __init__(self, results, save=True, save_dir='signal_associa_plots',
                 formats=('png',)):
        self.r = results or {}
        self.save = save
        self.save_dir = save_dir
        self.formats = formats
        self.alpha = float(self.r.get('alpha', 0.05))

        if self.save:
            os.makedirs(self.save_dir, exist_ok=True)

        set_publication_style()

    # -----------------------------------------------------------------------
    # INTERNAL HELPERS
    # -----------------------------------------------------------------------

    def _save_fig(self, fig, filename):
        paths = []
        if self.save:
            for fmt in self.formats:
                path = os.path.join(self.save_dir, f'{filename}.{fmt}')
                fig.savefig(path, dpi=300, bbox_inches='tight')
                paths.append(path)
        plt.close(fig)
        return paths

    def _pairs(self):
        return [tuple(p) for p in self.r.get('pairs', [])]

    def _methods(self):
        return list(self.r.get('methods', []))

    def _rows_for(self, sig_x=None, sig_y=None, method=None):
        out = []
        for row in self.r.get('pair_results', []):
            if method is not None and row.get('method') != method:
                continue
            if sig_x is not None and row.get('signal_x') != sig_x:
                continue
            if sig_y is not None and row.get('signal_y') != sig_y:
                continue
            out.append(row)
        return out

    # -----------------------------------------------------------------------
    # 1. SIGNAL TRACES
    # -----------------------------------------------------------------------

    def signal_traces(self, max_signals=12):
        """Stacked line plot of the loaded signals vs time/sample index."""
        signals = self.r.get('signals') or {}
        names = self.r.get('signal_names', list(signals.keys()))
        names = [n for n in names if n in signals][:max_signals]
        if not names:
            return []

        sr = float(self.r.get('sampling_rate', 1.0)) or 1.0
        n = len(names)
        fig, axes = plt.subplots(n, 1, figsize=(10, max(1.4 * n, 3)),
                                 sharex=True, squeeze=False)
        axes = axes[:, 0]

        for i, name in enumerate(names):
            y = np.asarray(signals[name], dtype=float).ravel()
            t = np.arange(len(y)) / sr
            axes[i].plot(t, y, '-', color=COLORS['accent'], linewidth=1.2)
            axes[i].set_ylabel(name, fontsize=9, rotation=0, ha='right', va='center')
            axes[i].tick_params(axis='both', labelsize=8)
            axes[i].margins(x=0)

        xlabel = 'Time (s)' if sr != 1.0 else 'Sample'
        axes[-1].set_xlabel(xlabel, fontsize=12, fontweight='bold')
        fig.suptitle(f'Input Signals (N = {len(names)})', fontsize=14, fontweight='bold')
        fig.tight_layout()
        return self._save_fig(fig, 'signal_traces')

    # -----------------------------------------------------------------------
    # 2. NULL DISTRIBUTION (single pair, per method)
    # -----------------------------------------------------------------------

    def null_distributions(self, pair=None, filename=None):
        """One panel per method: surrogate null histogram + real statistic line.

        pair : None → first pair; int → pair index; (x, y) tuple → that pair.
        filename : override output basename (used for per-pair figures).
        """
        pairs = self._pairs()
        if not pairs:
            return []
        if pair is None:
            sig_x, sig_y = pairs[0]
        elif isinstance(pair, int):
            if pair < 0 or pair >= len(pairs):
                return []
            sig_x, sig_y = pairs[pair]
        else:
            sig_x, sig_y = pair[0], pair[1]

        # One panel per method (not only those with a surrogate null).
        rows = [r for r in self._rows_for(sig_x, sig_y)
                if r.get('method') != 'error']
        if not rows:
            return []

        n = len(rows)
        ncol = min(n, 3)
        nrow = math.ceil(n / ncol)
        fig, axes = plt.subplots(nrow, ncol, figsize=(4.5 * ncol, 3.6 * nrow),
                                 squeeze=False)
        axes = axes.flatten()

        for i, row in enumerate(rows):
            ax = axes[i]
            null = np.asarray(row.get('null_distribution') or [], dtype=float)
            null = null[np.isfinite(null)]
            stat = row.get('statistic')
            p = row.get('p_best', row.get('p_value'))
            sig = bool(row.get('significant'))
            edge = COLORS['sig'] if sig else COLORS['nonsig']
            verdict = 'significant' if sig else 'n.s.'
            ptxt = f'p = {p:.3g}' if (p is not None and np.isfinite(p)) else 'p = n/a'

            if len(null):
                # Surrogate-based method → histogram + real statistic line
                ax.hist(null, bins=min(30, max(8, len(null) // 5)),
                        color=COLORS['null'], alpha=0.7, edgecolor='white',
                        linewidth=0.5, label=f'Surrogate null (n={len(null)})')
                if stat is not None and np.isfinite(stat):
                    ax.axvline(stat, color=COLORS['stat'], linewidth=2.5,
                               label=f'Real = {stat:.3f}')
                ax.set_xlabel('Statistic', fontsize=11, fontweight='bold')
                ax.set_ylabel('Count', fontsize=11, fontweight='bold')
                ax.legend(fontsize=8, loc='upper right', framealpha=0.9)
            else:
                # Analytic/parametric method (no surrogates) → stat + p summary
                stat_txt = f'{stat:.4f}' if (stat is not None and np.isfinite(stat)) else '—'
                ax.text(0.5, 0.60, stat_txt, transform=ax.transAxes, ha='center',
                        va='center', fontsize=22, fontweight='bold', color=edge)
                ax.text(0.5, 0.34, 'statistic', transform=ax.transAxes, ha='center',
                        va='center', fontsize=10, color=COLORS['neutral'])
                ax.text(0.5, 0.14, 'analytic test — no surrogate null',
                        transform=ax.transAxes, ha='center', va='center',
                        fontsize=8, color=COLORS['neutral'], style='italic')
                ax.set_xticks([]); ax.set_yticks([])
                for s in ax.spines.values():
                    s.set_edgecolor(edge); s.set_linewidth(1.4)

            ax.set_title(f'{_mlabel(row.get("method"))}  ({ptxt}, {verdict})',
                         fontsize=12, color=edge)
            ax.tick_params(axis='both', labelsize=9)

        for j in range(len(rows), len(axes)):
            axes[j].axis('off')

        fig.suptitle(f'Null Distributions — {sig_x} vs {sig_y}',
                     fontsize=14, fontweight='bold')
        fig.tight_layout()
        return self._save_fig(fig, filename or 'null_distributions')

    # -----------------------------------------------------------------------
    # 3. PAIR SUMMARY BAR (single pair, statistic + effect size per method)
    # -----------------------------------------------------------------------

    def pair_summary(self):
        pairs = self._pairs()
        if not pairs:
            return []
        sig_x, sig_y = pairs[0]
        rows = self._rows_for(sig_x, sig_y)
        rows = [r for r in rows if r.get('method') != 'error']
        if not rows:
            return []

        methods = [r.get('method') for r in rows]
        stats = [r.get('statistic') if r.get('statistic') is not None else np.nan
                 for r in rows]
        effs = [r.get('effect_size') if r.get('effect_size') is not None else np.nan
                for r in rows]
        sigs = [bool(r.get('significant')) for r in rows]
        x = np.arange(len(methods))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

        bar_cols = [COLORS['sig'] if s else COLORS['nonsig'] for s in sigs]
        ax1.bar(x, stats, color=bar_cols, edgecolor='black', linewidth=0.8)
        ax1.set_xticks(x)
        ax1.set_xticklabels([_mlabel(m) for m in methods], fontsize=10)
        ax1.set_ylabel('Statistic', fontsize=12, fontweight='bold')
        ax1.set_title('Coupling statistic (green = significant)',
                      fontsize=12)
        ax1.axhline(0, color=COLORS['neutral'], linewidth=1)
        ax1.tick_params(axis='both', labelsize=9)

        ax2.bar(x, effs, color=COLORS['accent'], edgecolor='black', linewidth=0.8)
        ax2.set_xticks(x)
        ax2.set_xticklabels([_mlabel(m) for m in methods], fontsize=10)
        ax2.set_ylabel('Effect size (z)', fontsize=12, fontweight='bold')
        ax2.set_title('Effect size vs surrogate null', fontsize=12)
        ax2.axhline(0, color=COLORS['neutral'], linewidth=1)
        ax2.tick_params(axis='both', labelsize=9)

        fig.suptitle(f'{sig_x} vs {sig_y}', fontsize=14, fontweight='bold')
        fig.tight_layout()
        return self._save_fig(fig, 'pair_summary')

    # -----------------------------------------------------------------------
    # 4. COUPLING MATRIX (batch: N×N heatmap, one per method)
    # -----------------------------------------------------------------------

    def coupling_matrix(self, value='statistic'):
        """N×N heatmap of `value` ('statistic' or 'neglog_p') per method.

        Symmetric fill for undirected methods; directed methods keep x→y.
        """
        names = self.r.get('signal_names', [])
        methods = self._methods()
        if len(names) < 2 or not methods:
            return []

        idx = {n: i for i, n in enumerate(names)}
        N = len(names)
        saved = []

        for mi, method in enumerate(methods):
            M = np.full((N, N), np.nan)
            for row in self._rows_for(method=method):
                a, b = row.get('signal_x'), row.get('signal_y')
                if a not in idx or b not in idx:
                    continue
                if value == 'neglog_p':
                    p = row.get('p_best', row.get('p_value'))
                    v = (-math.log10(p) if (p and p > 0 and np.isfinite(p))
                         else np.nan)
                else:
                    v = row.get('statistic')
                    v = v if (v is not None and np.isfinite(v)) else np.nan
                M[idx[a], idx[b]] = v
                M[idx[b], idx[a]] = v      # symmetric display

            fig, ax = plt.subplots(figsize=(max(5, 0.6 * N + 2),
                                            max(4, 0.6 * N + 1.5)))
            cmap = plt.cm.viridis.copy()
            cmap.set_bad('#eeeeee')
            im = ax.imshow(np.ma.masked_invalid(M), cmap=cmap, aspect='equal')
            ax.set_xticks(range(N)); ax.set_yticks(range(N))
            ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
            ax.set_yticklabels(names, fontsize=8)
            label = '−log₁₀ p' if value == 'neglog_p' else 'statistic'
            cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label(label, fontsize=10, fontweight='bold')
            ax.set_title(f'{_mlabel(method)} coupling — {label}',
                         fontsize=13, fontweight='bold')
            fig.tight_layout()
            saved += self._save_fig(fig, f'matrix_{method}_{value}')

        return saved

    # -----------------------------------------------------------------------
    # 5. SIGNIFICANCE MATRIX (batch: significant-or-not across all methods)
    # -----------------------------------------------------------------------

    def significance_matrix(self):
        names = self.r.get('signal_names', [])
        methods = self._methods()
        if len(names) < 2 or not methods:
            return []
        idx = {n: i for i, n in enumerate(names)}
        N = len(names)

        # count of methods finding each pair significant
        M = np.zeros((N, N))
        for row in self._rows_for():
            if not row.get('significant'):
                continue
            a, b = row.get('signal_x'), row.get('signal_y')
            if a in idx and b in idx:
                M[idx[a], idx[b]] += 1
                M[idx[b], idx[a]] += 1
        np.fill_diagonal(M, np.nan)

        fig, ax = plt.subplots(figsize=(max(5, 0.6 * N + 2),
                                        max(4, 0.6 * N + 1.5)))
        cmap = plt.cm.Greens.copy()
        cmap.set_bad('#eeeeee')
        im = ax.imshow(np.ma.masked_invalid(M), cmap=cmap, aspect='equal',
                       vmin=0, vmax=max(1, len(methods)))
        ax.set_xticks(range(N)); ax.set_yticks(range(N))
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(names, fontsize=8)
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04,
                            ticks=range(0, len(methods) + 1))
        cbar.set_label('# methods significant', fontsize=10, fontweight='bold')
        ax.set_title(f'Significant coupling (α = {self.alpha:g})',
                     fontsize=13, fontweight='bold')
        fig.tight_layout()
        return self._save_fig(fig, 'significance_matrix')

    # -----------------------------------------------------------------------
    # 6. COUPLING NETWORK (batch: nodes on a circle, significant edges)
    # -----------------------------------------------------------------------

    def coupling_network(self, method=None):
        """Circular network: nodes = signals, edges = significant coupling.

        If `method` is None, an edge is drawn when ANY method is significant,
        and its width scales with the number of concurring methods.
        """
        names = self.r.get('signal_names', [])
        if len(names) < 2:
            return []
        N = len(names)
        ang = np.linspace(0, 2 * np.pi, N, endpoint=False)
        pos = {n: (math.cos(a), math.sin(a)) for n, a in zip(names, ang)}

        # aggregate significance per unordered pair
        edge_count = {}
        edge_stat = {}
        for row in self._rows_for(method=method):
            if not row.get('significant'):
                continue
            a, b = row.get('signal_x'), row.get('signal_y')
            if a not in pos or b not in pos:
                continue
            key = tuple(sorted((a, b)))
            edge_count[key] = edge_count.get(key, 0) + 1
            s = row.get('statistic')
            if s is not None and np.isfinite(s):
                edge_stat.setdefault(key, []).append(abs(s))

        fig, ax = plt.subplots(figsize=(6.5, 6.5))
        maxc = max(edge_count.values()) if edge_count else 1
        for (a, b), c in edge_count.items():
            x = [pos[a][0], pos[b][0]]
            y = [pos[a][1], pos[b][1]]
            lw = 1.0 + 3.0 * (c / maxc)
            ax.plot(x, y, '-', color=COLORS['sig'],
                    linewidth=lw, alpha=0.55, zorder=1)

        for n, (x, y) in pos.items():
            ax.scatter([x], [y], s=420, color=COLORS['accent'],
                       edgecolor='black', linewidth=1.2, zorder=2)
            ax.text(x * 1.18, y * 1.18, n, fontsize=9, ha='center',
                    va='center', fontweight='bold')

        ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5)
        ax.set_aspect('equal'); ax.axis('off')
        title = ('Coupling network — significant edges'
                 if method is None else
                 f'{_mlabel(method)} network — significant edges')
        n_edges = len(edge_count)
        ax.set_title(f'{title}\n({n_edges} edges, α = {self.alpha:g})',
                     fontsize=13, fontweight='bold')
        fig.tight_layout()
        tag = method or 'any'
        return self._save_fig(fig, f'network_{tag}')

    # -----------------------------------------------------------------------
    # 7. PAIRS SUMMARY GRID (paired mode — combined view over all pairs)
    # -----------------------------------------------------------------------

    def pairs_summary(self):
        """Grid heatmap: rows = pairs, cols = methods; cell = statistic, shaded
        green when significant. One combined figure for all pre-paired columns.
        """
        from matplotlib.patches import Rectangle
        pairs = self._pairs()
        methods = self._methods()
        if not pairs or not methods:
            return []
        P, M = len(pairs), len(methods)

        fig, ax = plt.subplots(figsize=(max(1.7 * M + 2.5, 5), max(0.55 * P + 1.8, 3)))
        for i, (a, b) in enumerate(pairs):
            yrow = P - 1 - i
            for j, m in enumerate(methods):
                rr = self._rows_for(a, b, method=m)
                r = rr[0] if rr else {}
                stat = r.get('statistic')
                sig = bool(r.get('significant'))
                face = '#d6f0e4' if sig else '#f0f0f0'
                edge = COLORS['sig'] if sig else '#dddddd'
                ax.add_patch(Rectangle((j, yrow), 1, 1, facecolor=face,
                                       edgecolor=edge, linewidth=1.2))
                txt = f'{stat:.2f}' if (stat is not None and np.isfinite(stat)) else '—'
                ax.text(j + 0.5, yrow + 0.58, txt, ha='center', va='center',
                        fontsize=9, fontweight='bold',
                        color=(COLORS['sig'] if sig else COLORS['neutral']))
                p = r.get('p_best', r.get('p_value'))
                if p is not None and np.isfinite(p):
                    ax.text(j + 0.5, yrow + 0.22, f'p={p:.2g}', ha='center',
                            va='center', fontsize=7, color=COLORS['neutral'])

        ax.set_xlim(0, M); ax.set_ylim(0, P)
        ax.set_xticks([j + 0.5 for j in range(M)])
        ax.set_xticklabels([_mlabel(m) for m in methods], fontsize=10, fontweight='bold')
        ax.set_yticks([P - 1 - i + 0.5 for i in range(P)])
        ax.set_yticklabels([f'{a} ↔ {b}' for (a, b) in pairs], fontsize=9)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(f'Pairs Summary — statistic & significance (α = {self.alpha:g})',
                     fontsize=13, fontweight='bold', pad=10)
        fig.tight_layout()
        return self._save_fig(fig, 'pairs_summary')

    # -----------------------------------------------------------------------
    # CONVENIENCE: render the standard set for each mode
    # -----------------------------------------------------------------------

    def render_single(self):
        out = []
        out += self.signal_traces()
        out += self.null_distributions()
        out += self.pair_summary()
        return out

    def render_batch(self):
        # Paired mode: independent pairs → combined summary, no matrix/network
        if self.r.get('batch_type') == 'paired':
            out = []
            out += self.signal_traces()
            out += self.pairs_summary()
            return out
        # Pairwise mode (default): full N×N matrix + network
        out = []
        out += self.signal_traces()
        out += self.significance_matrix()
        out += self.coupling_matrix(value='statistic')
        out += self.coupling_network(method=None)
        return out
