"""
cornealia_batch_plotter.py

Reads batch CSVs and generates publication-quality figures:
  - distributions: quick overview violin plots
  - as_vs_bs_improvement: per-patient change analysis
  - pub_boxplots: AS vs BS with paired stats
  - pub_K_deep_dive: multi-panel K analysis
  - pub_validation: computed vs machine (scatter + Bland-Altman)
  - pub_K_independence: K vs other metrics
  - pub_comprehensive: 12-panel mega figure
  - pub_representative: example images with overlays
  - pub_spatial_order: spatial analysis panels

Usage:
    from cornealia.plotters.cornealia_batch_plotter import cornealia_batch_plotter

    bp = cornealia_batch_plotter('batch_results')
    bp.all()
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import seaborn as sns
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from pathlib import Path
from scipy import stats
from scipy.stats import ttest_rel, spearmanr, pearsonr
from scipy.spatial import Voronoi
from numpy.polynomial.polynomial import polyfit
from matplotlib.lines import Line2D
from collections import defaultdict
import re
import os


# ============================================================================
# PUBLICATION STYLE  (shared with cornealia_plotter)
# ============================================================================

def set_publication_style():
    sns.set_style("ticks", {
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.edgecolor': 'black',
        'axes.linewidth': 1.8,
        'xtick.major.width': 1.8,
        'ytick.major.width': 1.8,
        'xtick.major.size': 6,
        'ytick.major.size': 6,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
    })
    sns.set_context("paper", font_scale=1.4, rc={
        'lines.linewidth': 2.5,
        'axes.labelweight': 'bold',
        'axes.titleweight': 'bold',
        'font.weight': 'bold',
    })
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['savefig.facecolor'] = 'white'
    plt.rcParams['savefig.bbox'] = 'tight'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['text.usetex'] = False
    plt.rcParams['mathtext.default'] = 'regular'


COLORS = {
    'AS':        '#D55E00',   # Vermillion — After Stripping
    'BS':        '#0072B2',   # Blue — Before Stripping
    'computed':  '#009E73',   # Green
    'machine':   '#CC79A7',   # Pink
    'neutral':   '#4A4A4A',   # Dark gray
    'identity':  '#999999',   # Gray (for y=x line)
    'highlight': '#F0E442',   # Yellow
}

# Metric definitions: (csv_column, display_label, unit)
COMPUTED_METRICS = {
    'K_um':      ('K_um',      'K',              r'$\mu m^{-2}$'),
    'K_ds_um':   ('K_ds_um',   '$K_{ds}$',       r'$\mu m^{-2}$'),
    'K_Vmin_um': ('K_Vmin_um', '$K_{Vmin}$',     r'$\mu m^{-2}$'),
    'K_gpeak_um':('K_gpeak_um','$K_{gpeak}$',    r'$\mu m^{-2}$'),
    'r_0_um':    ('r_0_um',    r'$r_0$',         r'$\mu m$'),
    'CD_calc':   ('CD_calc',   'Cell Density',   r'cells/$mm^2$'),
    'Ave_calc':  ('Ave_calc',  'Average Area',   r'$\mu m^2$'),
    'CV_calc':   ('CV_calc',   'CV',             '%'),
    'HEX_calc':  ('HEX_calc',  'Hexagonality',   '%'),
}

PLAIN_LABELS = {
    'K_um':      ('K',              'um^-2'),
    'K_ds_um':   ('K_ds',           'um^-2'),
    'K_Vmin_um': ('K_Vmin',         'um^-2'),
    'K_gpeak_um':('K_gpeak',        'um^-2'),
    'r_0_um':    ('r0',             'um'),
    'CD_calc':   ('Cell Density',   'cells/mm^2'),
    'Ave_calc':  ('Average Area',   'um^2'),
    'CV_calc':   ('CV',             '%'),
    'HEX_calc':  ('Hexagonality',   '%'),
}

# Paired metrics for validation: (computed_col, machine_col, label)
VALIDATION_PAIRS = [
    ('CD_calc',  'CD_cells_mm_2_', r'Cell Density (cells/$mm^2$)'),
    ('Ave_calc', 'Ave_micrometer_2_', r'Average Area ($\mu m^2$)'),
    ('CV_calc',  'CV',             'CV (%)'),
    ('HEX_calc', 'HEX___',        'Hexagonality (%)'),
]


# ============================================================================
# HELPER — extract patient ID and group from Image_Name
# ============================================================================

def _extract_patient_info(name):
    """
    Extract patient_id and group (AS/BS) from Image_Name.
    patient_id is the full image name with AS/BS suffix stripped.
    Handles both ' AS'/` BS' (space) and '_AS'/'_BS' (underscore) patterns.

    Examples:
        '001-3731L AS.jpg'                → ('001-3731L', 'AS')
        'W4034 25 186674 V0004000 AS'     → ('W4034 25 186674 V0004000', 'AS')
        'W4034 24 177482 V0003000_AS'     → ('W4034 24 177482 V0003000', 'AS')
        'W4034 25 186898 V0004000 AS D1'  → ('W4034 25 186898 V0004000', 'AS')
    """
    # Strip file extension if present
    import os.path
    name_bare = os.path.splitext(name)[0] if '.' in name else name

    # Determine group and strip suffix
    group = None
    patient_id = name_bare

    for suffix, grp in [(' AS D1', 'AS'), (' BS D1', 'BS'),
                         ('_AS', 'AS'), ('_BS', 'BS'),
                         (' AS', 'AS'), (' BS', 'BS')]:
        if name_bare.endswith(suffix):
            group = grp
            patient_id = name_bare[:-len(suffix)]
            break

    return patient_id, group


def _format_p(p):
    """Format p-value for display on plots."""
    if p < 0.001:
        return 'p < 0.001'
    elif p < 0.01:
        return f'p = {p:.3f}'
    elif p < 0.05:
        return f'p = {p:.3f}'
    else:
        return f'p = {p:.2f} (n.s.)'


# ============================================================================
# BATCH PLOTTER CLASS
# ============================================================================

class cornealia_batch_plotter:

    def __init__(self, csv_folder, save=False, save_dir='batch_plots', formats=('png', 'pdf')):
        """
        Parameters
        ----------
        csv_folder : str or Path
            Folder containing CSVs produced by run_batch.py
        save : bool
            If True, save all figures automatically
        save_dir : str
            Directory for saved figures
        formats : tuple
            File formats to save ('png', 'pdf', etc.)
        """
        self.save = save
        self.save_dir = save_dir
        self.formats = formats

        set_publication_style()

        # --- Load CSVs ---
        csv_path = Path(csv_folder)
        if csv_path.is_file() and csv_path.suffix == '.csv':
            # Single CSV file
            csv_files = [csv_path]
        else:
            # Folder — load all CSVs
            csv_files = sorted(csv_path.glob('*.csv'))

        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {csv_path}")

        dfs = []
        for f in csv_files:
            df = pd.read_csv(f)
            df['Month'] = f.stem
            dfs.append(df)

        self.df = pd.concat(dfs, ignore_index=True)

        # --- Column name normalization (handle both old and new CSV formats) ---
        col_renames = {}
        if 'r0_um' in self.df.columns and 'r_0_um' not in self.df.columns:
            col_renames['r0_um'] = 'r_0_um'
        if 'r0_px' in self.df.columns and 'r_0_px' not in self.df.columns:
            col_renames['r0_px'] = 'r_0_px'
        if col_renames:
            self.df.rename(columns=col_renames, inplace=True)

        # --- Extract patient_id and group (AS/BS) ---
        info = self.df['Image_Name'].apply(_extract_patient_info)
        self.df['patient_id'] = info.apply(lambda x: x[0])
        self.df['group'] = info.apply(lambda x: x[1])

        # --- Build paired dataframe (AS & BS for same patient+month) ---
        as_df = self.df[self.df['group'] == 'AS'].copy()
        bs_df = self.df[self.df['group'] == 'BS'].copy()
        self.paired = pd.merge(
            as_df, bs_df,
            on=['patient_id', 'Month'],
            suffixes=('_AS', '_BS'),
            how='inner'
        )

        # --- Reliability filtering: exclude pairs where EITHER AS or BS is unreliable ---
        self.has_reliability = 'reliable' in self.df.columns
        if self.has_reliability:
            self.paired_all = self.paired.copy()
            both_reliable = (
                (self.paired['reliable_AS'] == True) &
                (self.paired['reliable_BS'] == True)
            )
            self.paired = self.paired[both_reliable].copy()
            n_dropped = len(self.paired_all) - len(self.paired)

            # Also filter individual df for boxplots/histograms
            self.df_all = self.df.copy()
            self.df = self.df[self.df['reliable'] == True].copy()

        # --- Summary ---
        n_as = (self.df['group'] == 'AS').sum()
        n_bs = (self.df['group'] == 'BS').sum()
        n_other = self.df['group'].isna().sum()
        n_total_images = len(self.df_all) if self.has_reliability else len(self.df)
        print(f"Loaded {n_total_images} images from {len(csv_files)} CSVs")
        print(f"  AS: {n_as}  |  BS: {n_bs}  |  Unmatched: {n_other}")
        print(f"  Paired (same patient, AS+BS): {len(self.paired)}")
        if self.has_reliability:
            print(f"  Reliability filter: {n_dropped} pairs dropped "
                  f"({len(self.paired)} reliable pairs from {len(self.paired_all)} total)")

        if self.save:
            os.makedirs(self.save_dir, exist_ok=True)

        # --- Auto-detect image folder from image_path column ---
        self.image_folder = None
        if 'image_path' in self.df.columns:
            first_path = self.df['image_path'].dropna().iloc[0] if len(self.df) > 0 else None
            if first_path and isinstance(first_path, str):
                self.image_folder = str(Path(first_path).parent)
                print(f"  Image folder: {self.image_folder}")

        # --- Auto-load g(r) population data if NPZ exists ---
        self.gr_data = None
        npz_candidates = list(csv_path.parent.glob('gr_population_data.npz')) if csv_path.is_file() else list(csv_path.glob('gr_population_data.npz'))
        if not npz_candidates:
            # Check parent folder and siblings (batch_run/results/ etc.)
            search_dirs = [csv_path.parent, csv_path.parent.parent]
            if csv_path.is_file():
                search_dirs.append(csv_path.parent.parent)
            for sd in search_dirs:
                npz_candidates = list(sd.rglob('gr_population_data.npz'))
                if npz_candidates:
                    break
        if npz_candidates:
            npz = np.load(npz_candidates[0])
            names = npz.get('names', np.array([]))
            curves = npz.get('curves', np.array([]))
            r = npz.get('r', np.array([]))
            if len(r) > 0 and len(curves) > 0 and len(names) > 0:
                names_str = [str(n) for n in names]
                bs_idx = [i for i, n in enumerate(names_str) if 'BS' in n.upper()]
                as_idx = [i for i, n in enumerate(names_str) if 'AS' in n.upper()]
                if bs_idx and as_idx:
                    self.gr_data = {
                        'r': r,
                        'bs_curves': curves[bs_idx],
                        'as_curves': curves[as_idx],
                        'pixel_size': 0.58,
                    }
                    print(f"  g(r) population data loaded: {len(bs_idx)} BS, {len(as_idx)} AS curves")

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------

    def _save_fig(self, fig, filename):
        if self.save:
            for fmt in self.formats:
                path = os.path.join(self.save_dir, f'{filename}.{fmt}')
                fig.savefig(path, dpi=300 if fmt != 'pdf' else None, bbox_inches='tight')
            print(f"  Saved: {filename} → {', '.join(self.formats)}")

    def _paired_ttest(self, metric):
        """Perform paired t-test on AS vs BS for a given metric.
        Returns (t_stat, p_value, n_pairs)."""
        col_as = f'{metric}_AS'
        col_bs = f'{metric}_BS'
        if col_as not in self.paired.columns or col_bs not in self.paired.columns:
            return None, None, 0
        valid = self.paired[[col_as, col_bs]].dropna()
        if len(valid) < 3:
            return None, None, len(valid)
        t, p = stats.ttest_rel(valid[col_as], valid[col_bs])
        return t, p, len(valid)

    def _pub_style(self):
        """Apply publication style: 190mm width, 10pt bold, 600 DPI."""
        plt.rcParams.update({
            'font.size': 10,
            'font.weight': 'bold',
            'axes.labelsize': 10,
            'axes.titlesize': 10,
            'axes.labelweight': 'bold',
            'axes.titleweight': 'bold',
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
            'legend.fontsize': 7,
            'figure.dpi': 150,
            'savefig.dpi': 600,
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        })

    def _pub_panel_label(self, ax, label):
        """Place panel label in title, left-aligned."""
        title_text = ax.get_title(loc='center')
        ax.set_title('', loc='center')
        ax.set_title(label + '  ' + title_text,
                     fontweight='bold', fontsize=10, loc='left', pad=4)

    def _pub_save(self, fig, filename):
        """Save at 600 DPI."""
        if self.save:
            for fmt in self.formats:
                path = os.path.join(self.save_dir, f'{filename}.{fmt}')
                fig.savefig(path, dpi=600 if fmt != 'pdf' else None, bbox_inches='tight')
            print(f"  Saved: {filename} → {', '.join(self.formats)}")

    # ==================================================================
    # FIG 2: AS vs BS BOX PLOTS (2×3) — all 6 metrics
    # ==================================================================

    def pub_boxplots(self, save=None):
        """Publication-ready 2×3 AS vs BS boxplots with paired t-test brackets and median Δ%."""
        self._pub_style()
        save = save if save is not None else self.save

        fig_w = 190 / 25.4
        fig_h = fig_w * 0.68

        LABELS_SAFE = {
            'K_um':     ('K_um',     '$K$',              '$\\mu m^{-2}$'),
            'r_0_um':   ('r_0_um',   '$r_0$',            '$\\mu m$'),
            'CD_calc':  ('CD_calc',  'CD',               'cells/mm$^2$'),
            'Ave_calc': ('Ave_calc', 'Ave',              '$\\mu m^2$'),
            'CV_calc':  ('CV_calc',  'CV',               '%'),
            'HEX_calc': ('HEX_calc', 'HEX',             '%'),
        }

        avail = {k: v for k, v in LABELS_SAFE.items() if v[0] in self.df.columns}
        n = len(avail)
        ncols = 3
        nrows = max(1, (n + ncols - 1) // ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_w * 0.68 * nrows / 2))
        if nrows * ncols > 1:
            axes = axes.flatten()
        else:
            axes = [axes]
        for j in range(n, len(axes)):
            axes[j].set_visible(False)

        labels_panel = tuple(f'({chr(97+i)})' for i in range(n))

        for i, (key, (col, label, unit)) in enumerate(avail.items()):
            ax = axes[i]
            plot_data = self.df[self.df['group'].isin(['AS', 'BS'])]

            # Violin for density shape
            sns.violinplot(x='group', y=col, data=plot_data, ax=ax,
                           hue='group', palette={'AS': COLORS['AS'], 'BS': COLORS['BS']},
                           width=0.8, inner=None, linewidth=0,
                           order=['BS', 'AS'], legend=False, alpha=0.15, cut=0)

            # Box on top
            sns.boxplot(x='group', y=col, data=plot_data, ax=ax,
                        hue='group', palette={'AS': COLORS['AS'], 'BS': COLORS['BS']},
                        width=0.35, fliersize=1.5, linewidth=1.2,
                        order=['BS', 'AS'], legend=False,
                        boxprops=dict(alpha=0.9),
                        medianprops=dict(color='black', linewidth=2))

            # Strip
            sns.stripplot(x='group', y=col, data=plot_data, ax=ax,
                          hue='group', palette={'AS': COLORS['AS'], 'BS': COLORS['BS']},
                          size=1, alpha=0.15, jitter=0.25, order=['BS', 'AS'], legend=False)

            # Paired t-test
            t, p, n = self._paired_ttest(col)

            # Compute median Δ%
            col_as = f'{col}_AS'
            col_bs = f'{col}_BS'
            if col_as in self.paired.columns and col_bs in self.paired.columns:
                paired_valid = self.paired[[col_as, col_bs]].dropna()
                threshold = max(paired_valid[col_bs].quantile(0.01), 1e-6)
                mask = paired_valid[col_bs] > threshold
                pct_change = (paired_valid.loc[mask, col_as] - paired_valid.loc[mask, col_bs]) / paired_valid.loc[mask, col_bs] * 100
                med_pct = pct_change.median()
            else:
                med_pct = None

            # Clip y-axis
            data_vals = plot_data[col].dropna()
            q_low, q_high, y_margin = 0, 1, 0.3
            if len(data_vals) > 1:
                q_low, q_high = data_vals.quantile(0.01), data_vals.quantile(0.99)
                y_margin = (q_high - q_low) * 0.30
                if np.isfinite(q_low) and np.isfinite(q_high) and y_margin > 0:
                    ax.set_ylim(q_low - y_margin * 0.5, q_high + y_margin * 1.5)

            if p is not None:
                y_range = q_high - q_low
                bracket_y = q_high + y_range * 0.08
                ax.plot([0, 0, 1, 1], [bracket_y, bracket_y + y_range * 0.02,
                         bracket_y + y_range * 0.02, bracket_y],
                        color='black', linewidth=1)
                ax.text(0.5, bracket_y + y_range * 0.04, _format_p(p),
                        ha='center', va='bottom', fontsize=6.5, fontweight='bold')

                # Add median Δ% below p-value
                if med_pct is not None:
                    arrow = '↑' if med_pct > 0 else '↓'
                    color = COLORS['AS'] if med_pct > 0 else COLORS['BS']
                    ax.text(0.5, bracket_y + y_range * 0.16,
                            f'{arrow} {med_pct:+.1f}%',
                            ha='center', va='bottom', fontsize=7, fontweight='bold',
                            color=color)

            ax.set_xlabel('')
            ax.set_ylabel(f'{label} ({unit})', fontweight='bold', fontsize=9)
            ax.set_title(f'{label}', fontweight='bold', fontsize=11, pad=8)
            ax.tick_params(axis='both', labelsize=8)

            sns.despine(ax=ax)
            self._pub_panel_label(ax, labels_panel[i])

        plt.tight_layout(pad=1.0, h_pad=2.0, w_pad=1.0)
        if save:
            self._pub_save(fig, 'fig2_as_vs_bs_boxplots')
        plt.show()

    # ==================================================================
    # FIG 3: K DEEP DIVE (2×3)
    # ==================================================================

    def pub_K_deep_dive(self, save=None):
        """Publication-ready 2×3 K deep dive figure.

        (a) AS vs BS overlaid histograms for K
        (b) AS vs BS boxplot for K
        (c) Paired scatter colored by improvement
        (d) Per-patient % change histogram
        (e) Absolute ΔK histogram
        (f) Summary statistics
        """
        self._pub_style()
        save = save if save is not None else self.save

        col = 'K_um'
        col_as, col_bs = f'{col}_AS', f'{col}_BS'
        label = '$K$'
        unit = '$\\mu m^{-2}$'
        plain_unit = 'um^-2'

        # Prepare data
        as_data = self.df.loc[self.df['group'] == 'AS', col].dropna()
        bs_data = self.df.loc[self.df['group'] == 'BS', col].dropna()
        plot_data = self.df[self.df['group'].isin(['AS', 'BS'])]

        paired = self.paired.copy()
        paired['_diff'] = paired[col_as] - paired[col_bs]
        threshold = max(paired[col_bs].quantile(0.01), 1e-6)
        valid = paired[paired[col_bs] > threshold].copy()
        valid['_pct_change'] = (valid[col_as] - valid[col_bs]) / valid[col_bs] * 100
        improved = valid['_diff'] > 0
        n_improved = improved.sum()
        n_total = len(valid)
        median_pct = valid['_pct_change'].median()
        mean_diff = valid['_diff'].mean()
        sd_diff = valid['_diff'].std()
        t_stat, p_ttest = stats.ttest_rel(valid[col_as], valid[col_bs])
        w_stat, p_wilcox = stats.wilcoxon(valid['_diff'])

        # Figure
        fig_w = 190 / 25.4
        fig_h = fig_w * 0.62
        fig, axes = plt.subplots(2, 3, figsize=(fig_w, fig_h))
        labels_panel = ('(a)', '(b)', '(c)', '(d)', '(e)', '(f)')

        # (a) Overlaid histograms
        ax = axes[0, 0]
        bins = np.linspace(min(as_data.min(), bs_data.min()),
                           max(as_data.max(), bs_data.max()), 35)
        ax.hist(bs_data, bins=bins, color=COLORS['BS'], alpha=0.6,
                edgecolor='black', linewidth=0.4, label=f'BS (n={len(bs_data)})')
        ax.hist(as_data, bins=bins, color=COLORS['AS'], alpha=0.6,
                edgecolor='black', linewidth=0.4, label=f'AS (n={len(as_data)})')
        ax.axvline(bs_data.mean(), color=COLORS['BS'], linestyle='--', linewidth=1.5)
        ax.axvline(as_data.mean(), color=COLORS['AS'], linestyle='--', linewidth=1.5)
        ax.set_xlabel(f'{label} ({unit})', fontweight='bold')
        ax.set_ylabel('Count', fontweight='bold')
        ax.set_title('AS vs BS Distribution', fontweight='bold', fontsize=10, pad=4)
        ax.legend(fontsize=6, loc='upper right')
        ax.tick_params(axis='both', labelsize=8)
        sns.despine(ax=ax)
        self._pub_panel_label(ax, labels_panel[0])

        # (b) Box plot
        ax = axes[0, 1]
        sns.boxplot(x='group', y=col, data=plot_data, ax=ax,
                    hue='group', palette={'AS': COLORS['AS'], 'BS': COLORS['BS']},
                    width=0.5, fliersize=2, linewidth=1.2,
                    order=['BS', 'AS'], legend=False)
        sns.stripplot(x='group', y=col, data=plot_data, ax=ax,
                      hue='group', palette={'AS': COLORS['AS'], 'BS': COLORS['BS']},
                      size=1.5, alpha=0.3, jitter=True, order=['BS', 'AS'], legend=False)
        t, p, n = self._paired_ttest(col)
        if p is not None:
            y_max = plot_data[col].max()
            y_range = y_max - plot_data[col].min()
            by = y_max + y_range * 0.08
            ax.plot([0, 0, 1, 1], [by, by + y_range*0.02, by + y_range*0.02, by],
                    color='black', linewidth=1)
            ax.text(0.5, by + y_range*0.04, _format_p(p),
                    ha='center', va='bottom', fontsize=7, fontweight='bold')
        ax.set_xlabel('')
        ax.set_ylabel(f'{label} ({unit})', fontweight='bold')
        ax.set_title('Paired t-test', fontweight='bold', fontsize=10, pad=4)
        ax.tick_params(axis='both', labelsize=8)
        sns.despine(ax=ax)
        self._pub_panel_label(ax, labels_panel[1])

        # (c) Paired scatter colored by improvement
        ax = axes[0, 2]
        ax.scatter(valid.loc[~improved, col_bs], valid.loc[~improved, col_as],
                   c=COLORS['BS'], s=8, alpha=0.4,
                   label=f'Decreased ({(~improved).sum()})')
        ax.scatter(valid.loc[improved, col_bs], valid.loc[improved, col_as],
                   c=COLORS['AS'], s=8, alpha=0.4,
                   label=f'Improved ({improved.sum()})')
        all_vals = pd.concat([valid[col_bs], valid[col_as]])
        lims = [0, all_vals.max() * 1.05]
        ax.plot(lims, lims, '--', color=COLORS['identity'], linewidth=1)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_xlabel(f'BS — {label} ({unit})', fontweight='bold')
        ax.set_ylabel(f'AS — {label} ({unit})', fontweight='bold')
        ax.set_title('Paired Scatter', fontweight='bold', fontsize=10, pad=4)
        ax.legend(fontsize=5, loc='upper left', markerscale=2)
        ax.tick_params(axis='both', labelsize=8)
        sns.despine(ax=ax)
        self._pub_panel_label(ax, labels_panel[2])

        # (d) % change histogram
        ax = axes[1, 0]
        pct_clipped = valid['_pct_change'].clip(-200, 500)
        ax.hist(pct_clipped, bins=50, color=COLORS['computed'], edgecolor='black',
                linewidth=0.4, alpha=0.8)
        ax.axvline(0, color='red', linestyle='--', linewidth=1.5, label='No change')
        ax.axvline(median_pct, color=COLORS['AS'], linestyle='-', linewidth=1.5,
                   label=f'Median = {median_pct:+.1f}%')
        ax.set_xlabel(f'{label} change (%)', fontweight='bold')
        ax.set_ylabel('Count', fontweight='bold')
        ax.set_title('Per-Donor % Change', fontweight='bold', fontsize=10, pad=4)
        ax.legend(fontsize=6)
        ax.tick_params(axis='both', labelsize=8)
        sns.despine(ax=ax)
        self._pub_panel_label(ax, labels_panel[3])

        # (e) Absolute ΔK histogram
        ax = axes[1, 1]
        ax.hist(valid['_diff'], bins=50, color='#56B4E9', edgecolor='black',
                linewidth=0.4, alpha=0.8)
        ax.axvline(0, color='red', linestyle='--', linewidth=1.5, label='No change')
        ax.axvline(mean_diff, color=COLORS['AS'], linestyle='-', linewidth=1.5,
                   label=f'Mean = {mean_diff:+.4f}')
        ax.set_xlabel(f'$\\Delta${label} ({unit})', fontweight='bold')
        ax.set_ylabel('Count', fontweight='bold')
        ax.set_title('Absolute Change', fontweight='bold', fontsize=10, pad=4)
        ax.legend(fontsize=6)
        ax.tick_params(axis='both', labelsize=8)
        sns.despine(ax=ax)
        self._pub_panel_label(ax, labels_panel[4])

        # (f) Summary box
        ax = axes[1, 2]
        ax.axis('off')
        summary = (
            f"(f)  K IMPROVEMENT SUMMARY\n"
            f"{'─'*32}\n\n"
            f"BS mean:  {bs_data.mean():.4f} {plain_unit}\n"
            f"AS mean:  {as_data.mean():.4f} {plain_unit}\n\n"
            f"Pairs:    {n_total}\n"
            f"Improved: {n_improved} ({n_improved/n_total*100:.1f}%)\n"
            f"Median d: {median_pct:+.1f}%\n"
            f"Mean dK:  {mean_diff:+.4f} {plain_unit}\n"
            f"SD dK:    {sd_diff:.4f} {plain_unit}\n\n"
            f"t-test:   p = {p_ttest:.2e}\n"
            f"Wilcoxon: p = {p_wilcox:.2e}\n"
            f"{'─'*32}"
        )
        ax.text(0.05, 0.5, summary, transform=ax.transAxes, fontsize=8,
                va='center', fontfamily='monospace', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFACD',
                          edgecolor='black', linewidth=0.8, alpha=0.95))

        plt.tight_layout(pad=0.8, h_pad=1.5, w_pad=0.8)
        if save:
            self._pub_save(fig, 'fig3_K_deep_dive')
        plt.show()

    # ==================================================================
    # FIG 4: VALIDATION SCATTER (2×2)
    # ==================================================================

    def pub_validation(self, save=None):
        """Publication-ready 2×2 computed vs device validation scatter."""
        self._pub_style()
        save = save if save is not None else self.save

        fig_w = 190 / 25.4
        fig_h = fig_w * 0.85  # slightly taller for 2×2
        fig, axes = plt.subplots(2, 2, figsize=(fig_w, fig_h))
        axes = axes.flatten()

        labels_panel = ('(a)', '(b)', '(c)', '(d)')

        LABELS_SAFE = [
            ('CD_calc',  'CD_cells_mm_2_', 'CD (cells/mm$^2$)'),
            ('Ave_calc', 'Ave_micrometer_2_', 'Ave ($\\mu m^2$)'),
            ('CV_calc',  'CV',             'CV (%)'),
            ('HEX_calc', 'HEX___',        'HEX (%)'),
        ]

        avail_labels = [(c, m, l) for c, m, l in LABELS_SAFE if c in self.df.columns and m in self.df.columns]

        if not avail_labels:
            fig.text(0.5, 0.5, 'No machine metrics available\n\nValidation requires images processed\nwith is_machine_output=True',
                     ha='center', va='center', fontsize=12, color='#999', fontstyle='italic')
            for ax in axes:
                ax.set_visible(False)
            if save:
                self._pub_save(fig, 'fig4_validation')
            plt.show()
            return

        for j in range(len(avail_labels), len(axes)):
            axes[j].set_visible(False)

        for i, (comp_col, mach_col, label) in enumerate(avail_labels):
            ax = axes[i]
            valid = self.df[[comp_col, mach_col]].dropna()

            if len(valid) < 3:
                ax.text(0.5, 0.5, 'Insufficient data', transform=ax.transAxes,
                        ha='center', fontsize=10)
                ax.set_title(label, fontweight='bold', fontsize=10, pad=4)
                self._pub_panel_label(ax, labels_panel[i])
                continue

            x = valid[mach_col].values.astype(float)
            y = valid[comp_col].values.astype(float)

            ax.scatter(x, y, c=COLORS['computed'], s=8, edgecolor='black',
                       linewidth=0.3, alpha=0.5, zorder=3)

            # Regression
            slope, intercept, r, p_reg, se = stats.linregress(x, y)
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, slope * x_line + intercept, '-',
                    color=COLORS['AS'], linewidth=1.5,
                    label=f'$R^2$ = {r**2:.3f}')

            # Identity line
            all_vals = np.concatenate([x, y])
            lims = [all_vals.min() * 0.95, all_vals.max() * 1.05]
            ax.plot(lims, lims, '--', color=COLORS['identity'], linewidth=1,
                    label='y = x', zorder=1)

            ax.set_xlabel(f'Device — {label}', fontweight='bold')
            ax.set_ylabel(f'Computed — {label}', fontweight='bold')
            ax.set_title(label, fontweight='bold', fontsize=10, pad=4)
            ax.legend(fontsize=6, loc='upper left')
            ax.tick_params(axis='both', labelsize=8)
            sns.despine(ax=ax)
            self._pub_panel_label(ax, labels_panel[i])

        plt.tight_layout(pad=0.8, h_pad=1.5, w_pad=0.8)
        if save:
            self._pub_save(fig, 'fig4_validation')
        plt.show()

    # ==================================================================
    # COLLECTIVE ORDER — STATISTICAL HELPERS
    # ==================================================================

    @staticmethod
    def _pitman_variance_test(x1, x2):
        """Pitman (1939) test for equality of variances in paired samples."""
        m = np.isfinite(x1) & np.isfinite(x2)
        x1, x2 = np.asarray(x1)[m], np.asarray(x2)[m]
        n = len(x1)
        if n < 4:
            return dict(n=n, s1=np.nan, s2=np.nan, r=np.nan, v=np.nan, T=np.nan, p=np.nan)
        s1, s2 = x1.std(ddof=1), x2.std(ddof=1)
        r = np.corrcoef(x1, x2)[0, 1]
        T = np.sqrt(n - 2) * ((s1 / s2) - (s2 / s1)) / (2 * np.sqrt(1 - r ** 2))
        pval = 2 * stats.t.sf(abs(T), df=n - 2)
        return dict(n=n, s1=s1, s2=s2, r=r, v=s2 / s1, T=T, p=pval)

    @staticmethod
    def _marginal_phase(base, change, edges, min_n=3):
        """Bin change by baseline, return bin midpoints and medians."""
        n_bins = len(edges) - 1
        mids, meds = [], []
        for i in range(n_bins):
            m = (base >= edges[i]) & (base < edges[i + 1]) if i < n_bins - 1 \
                else (base >= edges[i]) & (base <= edges[i + 1])
            mids.append((edges[i] + edges[i + 1]) / 2)
            meds.append(np.median(change[m]) if m.sum() >= min_n else np.nan)
        return np.array(mids), np.array(meds)

    @staticmethod
    def _interp_safe(mids, meds):
        """Safe 1D interpolation ignoring NaN bins."""
        from scipy.interpolate import interp1d
        ok = np.isfinite(meds)
        if ok.sum() < 2:
            return lambda x: np.full_like(np.atleast_1d(x), np.nan, dtype=float)
        return interp1d(mids[ok], meds[ok], kind='linear', bounds_error=False,
                        fill_value=(meds[ok][0], meds[ok][-1]))

    @staticmethod
    def _density_mask(X_g, Y_g, x_bs, y_bs, min_neighbors=3, radius_frac=0.15):
        """Mask grid points with too few nearby donors."""
        rx = radius_frac * (x_bs.max() - x_bs.min())
        ry = radius_frac * (y_bs.max() - y_bs.min())
        mask = np.ones(X_g.shape, dtype=bool)
        for i in range(X_g.shape[0]):
            for j in range(X_g.shape[1]):
                dist = ((x_bs - X_g[i, j]) / rx) ** 2 + ((y_bs - Y_g[i, j]) / ry) ** 2
                if np.sum(dist < 1) < min_neighbors:
                    mask[i, j] = False
        return mask

    def _compute_phase_field(self, x_bs, y_bs, dx, dy,
                             n_bins=None, n_grid=None, n_shuf=500, seed=123):
        """Compute null-subtracted phase field from paired baseline/change data."""
        n = len(x_bs)
        if n_bins is None:
            n_bins = max(4, min(10, n // 4))
        if n_grid is None:
            n_grid = max(8, min(15, n // 3))
        x_sd, y_sd = x_bs.std(), y_bs.std()
        dx_z, dy_z = dx / x_sd, dy / y_sd
        x_edges = np.percentile(x_bs, np.linspace(0, 100, n_bins + 1))
        y_edges = np.percentile(y_bs, np.linspace(0, 100, n_bins + 1))
        x_mids, dy_med = self._marginal_phase(x_bs, dy_z, x_edges)
        y_mids, dx_med = self._marginal_phase(y_bs, dx_z, y_edges)
        np.random.seed(seed)
        n = len(x_bs)
        dy_null = np.zeros((n_shuf, len(x_mids)))
        dx_null = np.zeros((n_shuf, len(y_mids)))
        for s in range(n_shuf):
            _, dy_null[s] = self._marginal_phase(
                x_bs[np.random.permutation(n)], dy_z, x_edges)
            _, dx_null[s] = self._marginal_phase(
                y_bs[np.random.permutation(n)], dx_z, y_edges)
        dy_ex = dy_med - np.nanmean(dy_null, 0)
        dx_ex = dx_med - np.nanmean(dx_null, 0)
        f_dy = self._interp_safe(x_mids, dy_ex)
        f_dx = self._interp_safe(y_mids, dx_ex)
        x_grid = np.linspace(x_mids[0], x_mids[-1], n_grid)
        y_grid = np.linspace(y_mids[0], y_mids[-1], n_grid)
        X_g, Y_g = np.meshgrid(x_grid, y_grid)
        return dict(x_bs=x_bs, y_bs=y_bs, x_sd=x_sd, y_sd=y_sd,
                    x_mids=x_mids, y_mids=y_mids,
                    dy_ex=dy_ex, dx_ex=dx_ex,
                    X_g=X_g, K_g=Y_g,
                    U=f_dx(Y_g), V=f_dy(X_g),
                    f_dy=f_dy, f_dx=f_dx)

    # ==================================================================
    # COLLECTIVE ORDER — PANEL PLOTTING HELPERS
    # ==================================================================

    def _fig4_panel_label(self, ax, label):
        """Place a bold panel label (a, b, c, ...) at the top-left of axes."""
        ax.text(-0.06, 1.05, label, transform=ax.transAxes,
                fontweight='bold', fontsize=10, va='bottom', ha='left')

    def _fig4_panel_a(self, fig, subplot_spec, paired, col_K):
        """Panel a: K_ds vs CD scatter with boxplots below."""
        gs_inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=subplot_spec, height_ratios=[4, 1], hspace=0.03)
        ax = fig.add_subplot(gs_inner[0])
        ax_bot = fig.add_subplot(gs_inner[1], sharex=ax)
        C_BS, C_AS = '#4A90D9', '#E8833A'

        bs_cd = paired['CD_calc_BS'].values
        bs_kv = paired[f'{col_K}_BS'].values
        as_cd = paired['CD_calc_AS'].values
        as_kv = paired[f'{col_K}_AS'].values
        all_cd = np.concatenate([bs_cd, as_cd])
        all_kv = np.concatenate([bs_kv, as_kv])
        cd_lo, cd_hi = np.percentile(all_cd, [2, 98])
        kv_lo, kv_hi = np.percentile(all_kv, [2, 98])
        m_bs = (bs_cd >= cd_lo) & (bs_cd <= cd_hi) & (bs_kv >= kv_lo) & (bs_kv <= kv_hi)
        m_as = (as_cd >= cd_lo) & (as_cd <= cd_hi) & (as_kv >= kv_lo) & (as_kv <= kv_hi)
        m_all = (all_cd >= cd_lo) & (all_cd <= cd_hi) & (all_kv >= kv_lo) & (all_kv <= kv_hi)

        ax.scatter(bs_cd[m_bs], bs_kv[m_bs], s=3, c=C_BS, alpha=0.15, edgecolors='none', label='BS')
        ax.scatter(as_cd[m_as], as_kv[m_as], s=3, c=C_AS, alpha=0.15, edgecolors='none', label='AS')
        coeffs = polyfit(all_cd[m_all], all_kv[m_all], 1)
        x_fit = np.linspace(cd_lo, cd_hi, 100)
        ax.plot(x_fit, coeffs[0] + coeffs[1] * x_fit, 'k--', linewidth=0.8, alpha=0.5)
        r_val, _ = pearsonr(all_cd[m_all], all_kv[m_all])
        ax.text(0.95, 0.05, f'R$^2$={r_val**2:.2f}', transform=ax.transAxes,
                fontsize=8, ha='right', va='bottom', fontweight='bold', color='#555')
        ax.set_ylabel('K$_{ds}$ (\u00b5m$^{-2}$)')
        ax.set_xticklabels([])
        ax.legend(fontsize=7, loc='upper left', markerscale=3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self._fig4_panel_label(ax, 'a')

        # Boxplots below
        cd_c, kv_c = all_cd[m_all], all_kv[m_all]
        n_bins = 10
        bed = np.linspace(cd_lo, cd_hi, n_bins + 1)
        bcd = (bed[:-1] + bed[1:]) / 2
        bw = bed[1] - bed[0]
        box_data, box_pos = [], []
        for i in range(n_bins):
            mb = (cd_c >= bed[i]) & (cd_c < bed[i + 1])
            if mb.sum() > 3:
                box_data.append(kv_c[mb])
                box_pos.append(bcd[i])
        if box_data:
            bp = ax_bot.boxplot(box_data, positions=box_pos, widths=bw * 0.6,
                                patch_artist=True, showfliers=False,
                                medianprops=dict(color='#E65100', linewidth=1),
                                whiskerprops=dict(color='#888', linewidth=0.6),
                                capprops=dict(color='#888', linewidth=0.6))
            for patch in bp['boxes']:
                patch.set_facecolor('#FFE0B2')
                patch.set_edgecolor('#888')
                patch.set_linewidth(0.5)
                patch.set_alpha(0.8)
        ax_bot.set_xlabel('CD (cells/mm$^2$)')
        ax_bot.set_ylabel('K range', fontsize=7)
        ax_bot.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1000:.1f}k'))
        ax_bot.tick_params(axis='x', rotation=45)
        plt.setp(ax_bot.get_xticklabels(), ha='right')
        ax_bot.spines['top'].set_visible(False)
        ax_bot.spines['right'].set_visible(False)
        ax_bot.tick_params(axis='both', labelsize=9)
        for _idx, _lbl in enumerate(ax_bot.xaxis.get_ticklabels()):
            if _idx % 2 != 0:
                _lbl.set_visible(False)

    def _fig4_panel_b(self, fig, subplot_spec, paired, col_K):
        """Panel b: K_ds vs HEX scatter with boxplots below."""
        gs_inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=subplot_spec, height_ratios=[4, 1], hspace=0.03)
        ax = fig.add_subplot(gs_inner[0])
        ax_bot = fig.add_subplot(gs_inner[1], sharex=ax)
        C_BS, C_AS = '#4A90D9', '#E8833A'

        bs_hex = paired['HEX_calc_BS'].values
        bs_kv = paired[f'{col_K}_BS'].values
        as_hex = paired['HEX_calc_AS'].values
        as_kv = paired[f'{col_K}_AS'].values
        all_hex = np.concatenate([bs_hex, as_hex])
        all_kv = np.concatenate([bs_kv, as_kv])
        h_lo, h_hi = np.percentile(all_hex, [2, 98])
        kv_lo, kv_hi = np.percentile(all_kv, [2, 98])
        m_bs = (bs_hex >= h_lo) & (bs_hex <= h_hi) & (bs_kv >= kv_lo) & (bs_kv <= kv_hi)
        m_as = (as_hex >= h_lo) & (as_hex <= h_hi) & (as_kv >= kv_lo) & (as_kv <= kv_hi)
        m_all = (all_hex >= h_lo) & (all_hex <= h_hi) & (all_kv >= kv_lo) & (all_kv <= kv_hi)

        ax.scatter(bs_hex[m_bs], bs_kv[m_bs], s=3, c=C_BS, alpha=0.15, edgecolors='none', label='BS')
        ax.scatter(as_hex[m_as], as_kv[m_as], s=3, c=C_AS, alpha=0.15, edgecolors='none', label='AS')
        coeffs = polyfit(all_hex[m_all], all_kv[m_all], 1)
        x_fit = np.linspace(h_lo, h_hi, 100)
        ax.plot(x_fit, coeffs[0] + coeffs[1] * x_fit, 'k--', linewidth=0.8, alpha=0.5)
        r_val, _ = pearsonr(all_hex[m_all], all_kv[m_all])
        ax.text(0.95, 0.05, f'R$^2$={r_val**2:.2f}', transform=ax.transAxes,
                fontsize=8, ha='right', va='bottom', fontweight='bold', color='#555')
        ax.set_ylabel('K$_{ds}$ (\u00b5m$^{-2}$)')
        ax.set_xticklabels([])
        ax.legend(fontsize=7, loc='upper left', markerscale=3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self._fig4_panel_label(ax, 'b')

        # Boxplots below
        hex_c, kv_c = all_hex[m_all], all_kv[m_all]
        n_bins = 10
        bed = np.linspace(h_lo, h_hi, n_bins + 1)
        bmid = (bed[:-1] + bed[1:]) / 2
        bw = bed[1] - bed[0]
        box_data, box_pos = [], []
        for i in range(n_bins):
            mb = (hex_c >= bed[i]) & (hex_c < bed[i + 1])
            if mb.sum() > 3:
                box_data.append(kv_c[mb])
                box_pos.append(bmid[i])
        if box_data:
            bp = ax_bot.boxplot(box_data, positions=box_pos, widths=bw * 0.6,
                                patch_artist=True, showfliers=False,
                                medianprops=dict(color='#E65100', linewidth=1),
                                whiskerprops=dict(color='#888', linewidth=0.6),
                                capprops=dict(color='#888', linewidth=0.6))
            for patch in bp['boxes']:
                patch.set_facecolor('#FFE0B2')
                patch.set_edgecolor('#888')
                patch.set_linewidth(0.5)
                patch.set_alpha(0.8)
        ax_bot.set_xlabel('HEX (%)')
        ax_bot.set_ylabel('K range', fontsize=7)
        ax_bot.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}'))
        ax_bot.tick_params(axis='x', rotation=45)
        plt.setp(ax_bot.get_xticklabels(), ha='right')
        ax_bot.spines['top'].set_visible(False)
        ax_bot.spines['right'].set_visible(False)
        ax_bot.tick_params(axis='both', labelsize=9)
        for _idx, _lbl in enumerate(ax_bot.xaxis.get_ticklabels()):
            if _idx % 2 != 0:
                _lbl.set_visible(False)

    def _fig4_quad_scatter(self, ax, x_pct, y_pct, x_label, y_label,
                           highlight_pair, label, colors=None):
        """Four-quadrant scatter with highlighted quadrants and counts."""
        c1, c2 = colors if colors else ('#882255', '#009E73')
        ax.scatter(x_pct, y_pct, s=3, c='#999', alpha=0.20, edgecolors='none')
        q_tl = (y_pct > 0) & (x_pct < 0)
        q_tr = (y_pct > 0) & (x_pct > 0)
        q_bl = (y_pct < 0) & (x_pct < 0)
        q_br = (y_pct < 0) & (x_pct > 0)
        h1, h2 = highlight_pair
        qmap = {'tl': q_tl, 'tr': q_tr, 'bl': q_bl, 'br': q_br}
        ax.scatter(x_pct[qmap[h1]], y_pct[qmap[h1]], s=4, c=c1, alpha=0.35, edgecolors='none')
        ax.scatter(x_pct[qmap[h2]], y_pct[qmap[h2]], s=4, c=c2, alpha=0.35, edgecolors='none')
        ax.axhline(0, color='black', linewidth=0.5, linestyle=':')
        ax.axvline(0, color='black', linewidth=0.5, linestyle=':')
        x_s = x_label.replace('\u0394', '')
        total = len(x_pct)
        dir_map = {'tl': ('K+', '-'), 'tr': ('K+', '+'), 'bl': ('K-', '-'), 'br': ('K-', '+')}
        for key, q, num, px, py, ha, va in [
            ('tl', q_tl, 'I', 0.03, 0.97, 'left', 'top'),
            ('tr', q_tr, 'II', 0.97, 0.97, 'right', 'top'),
            ('bl', q_bl, 'III', 0.03, 0.03, 'left', 'bottom'),
            ('br', q_br, 'IV', 0.97, 0.03, 'right', 'bottom'),
        ]:
            kd, xd = dir_map[key]
            pct = 100 * q.sum() / total
            ax.text(px, py, f'{num}. {kd} {x_s}{xd}\n{q.sum()} ({pct:.0f}%)',
                    transform=ax.transAxes, fontsize=7, ha=ha, va=va,
                    color='black', fontweight='bold')
        rho, pval = spearmanr(x_pct, y_pct)
        ax.text(0.65, 1.05, f'\u03c1={rho:.2f} (p={pval:.0e})',
                fontsize=7, ha='center', va='bottom', fontweight='bold', color='#333',
                transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7,
                          edgecolor='none'), clip_on=False)
        ax.set_xlabel(f'{x_label} (%)')
        ax.set_ylabel(f'{y_label} (%)')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self._fig4_panel_label(ax, label)

    def _fig4_panel_gr(self, ax, gr_data):
        """Panel e: Population g(r) curves with curvature inset."""
        C_BS, C_AS = '#4A90D9', '#E8833A'
        r = gr_data['r']
        px = gr_data['pixel_size']
        r_um = r * px
        bs_mean = np.mean(gr_data['bs_curves'], axis=0)
        as_mean = np.mean(gr_data['as_curves'], axis=0)
        bs_lo = np.percentile(gr_data['bs_curves'], 25, axis=0)
        bs_hi = np.percentile(gr_data['bs_curves'], 75, axis=0)
        as_lo = np.percentile(gr_data['as_curves'], 25, axis=0)
        as_hi = np.percentile(gr_data['as_curves'], 75, axis=0)

        mask = r_um <= 45
        ax.fill_between(r_um[mask], bs_lo[mask], bs_hi[mask], color=C_BS, alpha=0.15)
        ax.fill_between(r_um[mask], as_lo[mask], as_hi[mask], color=C_AS, alpha=0.15)
        ax.plot(r_um[mask], bs_mean[mask], '-', color=C_BS, lw=1.8, label='BS')
        ax.plot(r_um[mask], as_mean[mask], '-', color=C_AS, lw=1.8, label='AS')
        ax.axhline(1, color='gray', ls='--', lw=0.6, alpha=0.5)
        ax.set_xlabel('r (\u00b5m)')
        ax.set_ylabel('g(r)')
        ax.legend(fontsize=7, loc='upper right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self._fig4_panel_label(ax, 'e')

    def _fig4_panel_paired_K(self, fig, subplot_spec, paired, col_K):
        """Panel f: Paired BS/AS K scatter."""
        C_E1, C_E2 = '#CC3311', '#117733'

        ax = fig.add_subplot(subplot_spec)

        bs_kv = paired[f'{col_K}_BS'].values
        as_kv = paired[f'{col_K}_AS'].values
        improved = as_kv > bs_kv
        n_imp = improved.sum()

        ax.scatter(bs_kv[~improved], as_kv[~improved], s=3, c=C_E1, alpha=0.3,
                   edgecolors='none', label=f'Decreased ({(~improved).sum()})')
        ax.scatter(bs_kv[improved], as_kv[improved], s=3, c=C_E2, alpha=0.3,
                   edgecolors='none', label=f'Improved ({n_imp})')
        lims = [0, max(bs_kv.max(), as_kv.max()) * 1.05]
        ax.plot(lims, lims, '--', color='#999', linewidth=1)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_xlabel('BS K$_{ds}$ (\u00b5m$^{-2}$)')
        ax.set_ylabel('AS K$_{ds}$ (\u00b5m$^{-2}$)')
        ax.legend(fontsize=6, loc='upper left', markerscale=2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self._fig4_panel_label(ax, 'f')

    def _fig4_forest(self, ax, paired, col_K):
        """Panel g: Forest plot of paired % change across metrics."""
        metrics_forest = [
            (col_K, '$K_{ds}$'), ('CD_calc', 'CD'), ('HEX_calc', 'HEX'),
            ('Ave_calc', 'Ave'), ('CV_calc', 'CV'), ('r_0_um', '$r_0$'),
        ]
        # Add mean_F if available
        if 'mean_F_BS' in paired.columns:
            metrics_forest.append(('mean_F', 'mean|F|'))

        y_pos = np.arange(len(metrics_forest))[::-1] * 0.5 + 0.5

        ax.axhspan(0.1, y_pos[0] - 0.15, color='#f0f0f0', alpha=0.5, zorder=0)
        for idx, (col, label) in enumerate(metrics_forest):
            bs_col, as_col = f'{col}_BS', f'{col}_AS'
            if bs_col not in paired.columns or as_col not in paired.columns:
                continue
            bs_v = paired[bs_col].values
            as_v = paired[as_col].values
            valid = np.isfinite(bs_v) & np.isfinite(as_v) & (np.abs(bs_v) > 1e-9)
            pct_ch = (as_v[valid] - bs_v[valid]) / bs_v[valid] * 100
            mean_p = np.mean(pct_ch)
            se = np.std(pct_ch) / np.sqrt(len(pct_ch))
            ci_l, ci_h = mean_p - 1.96 * se, mean_p + 1.96 * se
            _, p_t = ttest_rel(as_v[valid], bs_v[valid])
            sig = '***' if p_t < 0.001 else '**' if p_t < 0.01 else '*' if p_t < 0.05 else 'n.s.'
            y = y_pos[idx]
            clr = '#E65100' if mean_p > 0 else '#1565C0'
            ax.plot([ci_l, ci_h], [y, y], color=clr,
                    linewidth=2 if idx == 0 else 1.5, solid_capstyle='round')
            ax.plot(mean_p, y, 'o', color=clr, markersize=6 if idx == 0 else 5,
                    markeredgecolor='white', markeredgewidth=0.5)
            ax.text(ci_h + 0.3, y, f'{mean_p:+.1f}% {sig}', va='center', fontsize=6,
                    fontweight='bold', color=clr)

        ax.axvline(0, color='black', linewidth=0.8, linestyle='-')
        ax.set_yticks(y_pos[:len(metrics_forest)])
        ax.set_yticklabels([m[1] for m in metrics_forest], fontsize=7, fontweight='bold')
        ax.set_xlabel('Change AS vs BS (%)', fontsize=7)
        ax.text(0.85, 1.14, 'Wilcoxon signed-rank (% change)',
                transform=ax.transAxes, fontsize=7, ha='right', va='bottom', color='#555')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y', length=0)
        self._fig4_panel_label(ax, 'g')

    def _fig4_boxplot_binned(self, ax, paired, col_K, bin_col_bs, change_col_bs,
                             change_col_as, x_label, y_label, panel_label,
                             n_bins=None):
        """Panels h/i: ΔY boxplots binned by baseline X."""
        from scipy.stats import wilcoxon as _wil

        p = paired.dropna(subset=[f'{col_K}_BS', f'{col_K}_AS',
                                  'CD_calc_BS', 'CD_calc_AS']).copy()
        for col in [f'{col_K}_BS', f'{col_K}_AS']:
            p1, p99 = np.percentile(p[col], [1, 99])
            p = p[(p[col] >= p1) & (p[col] <= p99)]

        if change_col_bs not in p.columns or change_col_as not in p.columns:
            ax.text(0.5, 0.5, 'Data not available', transform=ax.transAxes,
                    ha='center', fontsize=9, color='#999')
            return

        # Adaptive bin count: aim for ~5+ samples per bin, min 3 bins
        if n_bins is None:
            n_bins = max(3, min(8, len(p) // 5))

        edges = np.percentile(p[bin_col_bs], np.linspace(0, 100, n_bins + 1))
        data_list, labels, annotations = [], [], []

        for i in range(n_bins):
            mask = (p[bin_col_bs] >= edges[i])
            if i < n_bins - 1:
                mask &= (p[bin_col_bs] < edges[i + 1])
            else:
                mask &= (p[bin_col_bs] <= edges[i + 1])
            sub = p[mask]
            if len(sub) < 3:
                continue
            dy = sub[change_col_as].values - sub[change_col_bs].values
            data_list.append(dy)
            labels.append(f'{edges[i]:.3f}-{edges[i+1]:.3f}')
            try:
                _, p_wil = _wil(dy)
            except ValueError:
                p_wil = 1.0
            annotations.append(p_wil)

        if not data_list:
            return

        C_MAIN = '#663399'
        x = np.arange(len(data_list))
        bp = ax.boxplot(data_list, positions=x, widths=0.5, patch_artist=True,
                        showfliers=False,
                        medianprops=dict(color='#E65100', linewidth=1.2),
                        whiskerprops=dict(color='#555', linewidth=0.8),
                        capprops=dict(color='#555', linewidth=0.8))
        for patch in bp['boxes']:
            patch.set_facecolor(C_MAIN)
            patch.set_alpha(0.6)
            patch.set_edgecolor('#333')
            patch.set_linewidth(0.8)

        ax.axhline(0, color='black', ls=':', lw=0.8)
        medians = [np.median(d) for d in data_list]
        ax.plot(x, medians, 'o-', color='#E65100', markersize=4, linewidth=1.5, zorder=5, label='Median')

        y_max = max(d.max() for d in data_list)
        for i, p_w in enumerate(annotations):
            sig = '*' if p_w < 0.05 else 'ns'
            ax.text(i, y_max + abs(y_max) * 0.03, sig,
                    ha='center', va='bottom', fontsize=7, fontweight='bold')

        for i, d in enumerate(data_list):
            ax.text(i, y_max + abs(y_max) * 0.08, f'n={len(d)}', ha='center',
                    va='bottom', fontsize=9, color='#555', fontweight='bold', rotation=35)

        ax.set_xticks(x)
        display_labels = [lab if i % 2 == 0 else '' for i, lab in enumerate(labels)]
        ax.set_xticklabels(display_labels, fontsize=9, rotation=30, ha='right')
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(fontsize=8, loc='upper left',
                  title='* p<0.05 Wilcoxon', title_fontsize=7,
                  framealpha=0.9, edgecolor='none')
        self._fig4_panel_label(ax, panel_label)

    def _fig4_phase_panel(self, ax, R, xn, yn, x_label, y_label, x_fmt, label):
        """Draw a phase portrait panel (j or k)."""
        from scipy.optimize import brentq
        C_BS, C_AS = '#4A90D9', '#E8833A'

        ax.scatter(R['x_bs'], R['y_bs'], s=1, c='#bbb', alpha=0.15,
                   edgecolors='none', zorder=1, rasterized=True)
        U, V = R['U'].copy(), R['V'].copy()
        dmask = self._density_mask(R['X_g'], R['K_g'], R['x_bs'], R['y_bs'])
        U[~dmask] = np.nan
        V[~dmask] = np.nan
        mag = np.sqrt(np.nan_to_num(U) ** 2 + np.nan_to_num(V) ** 2)
        ax.quiver(R['X_g'], R['K_g'], U * R['x_sd'], V * R['y_sd'], mag,
                  cmap='RdPu', alpha=0.9, angles='xy', scale_units='xy', scale=1,
                  width=0.004, headwidth=4, headlength=5, zorder=3)

        x_null = y_null = None
        try:
            x_null = brentq(R['f_dy'], R['x_mids'][0], R['x_mids'][-1])
            ax.axvline(x_null, color=C_AS, ls='--', lw=1.0, alpha=0.7,
                       label=f'\u0394{yn}=0 ({xn}={x_null:.0f})')
        except ValueError:
            pass
        try:
            y_null = brentq(R['f_dx'], R['y_mids'][0], R['y_mids'][-1])
            ax.axhline(y_null, color=C_BS, ls='--', lw=1.0, alpha=0.7,
                       label=f'\u0394{xn}=0 ({yn}={y_null:.4f})')
        except ValueError:
            pass
        if x_null is not None and y_null is not None:
            fp_mask = self._density_mask(
                np.array([[x_null]]), np.array([[y_null]]), R['x_bs'], R['y_bs'])
            alpha = 1.0 if fp_mask[0, 0] else 0.3
            ax.plot(x_null, y_null, '*', color='#E65100', markersize=12,
                    markeredgecolor='white', markeredgewidth=0.8, zorder=10,
                    alpha=alpha, label='fixed pt')

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        _arrow_key = Line2D([0], [0], color='#9B4A96', lw=1.4,
                            marker='>', markersize=3, label='binned median shift')
        _h, _l = ax.get_legend_handles_labels()
        ax.legend([_arrow_key] + _h, ['binned median shift'] + _l,
                  fontsize=9, loc='lower left', bbox_to_anchor=(0.0, 1.02),
                  framealpha=0.9, edgecolor='none', ncol=2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(x_fmt))
        self._fig4_panel_label(ax, label)

        if x_null is not None and y_null is not None:
            xb, yb = R['x_bs'], R['y_bs']
            for _xl, _yl, _tx, _ty in [
                ('lo', 'hi', 0.25, 0.97), ('hi', 'hi', 0.75, 0.97),
                ('lo', 'lo', 0.25, 0.42), ('hi', 'lo', 0.75, 0.42),
            ]:
                _qm = ((xb < x_null) if _xl == 'lo' else (xb >= x_null)) & \
                      ((yb < y_null) if _yl == 'lo' else (yb >= y_null))
                ax.text(_tx, _ty, f'n={int(_qm.sum())}', transform=ax.transAxes,
                        fontsize=10, ha='center', va='top', color='#555', fontweight='bold')

    # ==================================================================
    # COLLECTIVE ORDER FIGURE (Fig 4)
    # ==================================================================

    def pub_collective_order(self, gr_data=None, save=None):
        """
        Publication Figure 4 — Collective order analysis.

        4-row layout:
          Row 1 (a-d): K orthogonality — K vs CD, K vs HEX, ΔK vs ΔCD, ΔK vs ΔHEX
          Row 2 (e-g): K increases — g(r), paired scatter, forest plot
          Row 3 (h-i): Cross-variable — ΔK boxplots by CD, ΔCD boxplots by K
          Row 4 (j-k): Phase portraits — CD-K, r₀-K

        Parameters
        ----------
        gr_data : dict, optional
            {'r', 'bs_curves', 'as_curves', 'pixel_size'}.
            If None, uses self.gr_data (auto-loaded from NPZ).
        """
        if gr_data is None:
            gr_data = self.gr_data
        save = save if save is not None else self.save
        self._pub_style()

        paired = self.paired.copy()
        col_K = 'K_ds_um'

        # Paired deltas
        dk = paired[f'{col_K}_AS'].values - paired[f'{col_K}_BS'].values
        dcd = paired['CD_calc_AS'].values - paired['CD_calc_BS'].values
        dhex = paired['HEX_calc_AS'].values - paired['HEX_calc_BS'].values
        dk_pct = dk / paired[f'{col_K}_BS'].values * 100
        dcd_pct = dcd / paired['CD_calc_BS'].values * 100
        dhex_pct = dhex / paired['HEX_calc_BS'].values * 100

        def _clip_pct(x, y, pct=2):
            xlo, xhi = np.percentile(x, [pct, 100 - pct])
            ylo, yhi = np.percentile(y, [pct, 100 - pct])
            m = (x >= xlo) & (x <= xhi) & (y >= ylo) & (y <= yhi)
            return x[m], y[m], m

        # ── Figure layout: 190mm × 340mm, 4 rows ──
        fig_w = 190 / 25.4
        fig_h = 340 / 25.4
        fig = plt.figure(figsize=(fig_w, fig_h))

        gs_row1 = fig.add_gridspec(1, 4,
                                    left=0.09, right=0.97, top=0.97, bottom=0.859,
                                    wspace=0.45)
        gs_row2 = fig.add_gridspec(1, 3,
                                    left=0.20, right=0.86, top=0.795, bottom=0.693,
                                    wspace=0.35)
        gs_row3 = fig.add_gridspec(1, 2,
                                    left=0.13, right=0.93, top=0.677, bottom=0.478,
                                    wspace=0.05)
        gs_row4 = fig.add_gridspec(1, 2,
                                    left=0.13, right=0.93, top=0.453, bottom=0.254,
                                    wspace=0.05)

        # ── Row 1: K orthogonality ──
        self._fig4_panel_a(fig, gs_row1[0, 0], paired, col_K)
        self._fig4_panel_b(fig, gs_row1[0, 1], paired, col_K)

        ax_c = fig.add_subplot(gs_row1[0, 2])
        dcd_c, dk_c, _ = _clip_pct(dcd_pct, dk_pct, pct=2)
        self._fig4_quad_scatter(ax_c, dcd_c, dk_c, '\u0394CD', '\u0394K',
                                ('tl', 'br'), 'c', colors=('#882255', '#009E73'))

        ax_d = fig.add_subplot(gs_row1[0, 3])
        dhex_c, dk_d, _ = _clip_pct(dhex_pct, dk_pct, pct=2)
        self._fig4_quad_scatter(ax_d, dhex_c, dk_d, '\u0394HEX', '\u0394K',
                                ('tr', 'bl'), 'd', colors=('#332288', '#DDCC77'))

        # ── Row 2: K increases after stripping ──
        if gr_data is not None:
            ax_e = fig.add_subplot(gs_row2[0, 0])
            self._fig4_panel_gr(ax_e, gr_data)
            _pe = ax_e.get_position()
            ax_e.set_position([_pe.x0 - 0.067, _pe.y0, _pe.width, _pe.height])
        else:
            ax_e = fig.add_subplot(gs_row2[0, 0])
            ax_e.text(0.5, 0.5, 'g(r) data\nnot available', transform=ax_e.transAxes,
                      ha='center', va='center', fontsize=9, color='#999')
            self._fig4_panel_label(ax_e, 'e')

        self._fig4_panel_paired_K(fig, gs_row2[0, 1], paired, col_K)

        ax_g = fig.add_subplot(gs_row2[0, 2])
        self._fig4_forest(ax_g, paired, col_K)

        # ── Row 3: Cross-variable boxplots (h, i) ──
        ax_h = fig.add_subplot(gs_row3[0, 0])
        self._fig4_boxplot_binned(ax_h, paired, col_K,
                                  'CD_calc_BS', 'CD_calc_BS', 'CD_calc_AS',
                                  'BS CD (cells/mm\u00b2)', '\u0394K$_{ds}$ (\u00b5m$^{-2}$)',
                                  'h')
        # Wait — this bins CD, measures ΔK. Fix the change columns:
        # Actually the binned boxplot needs bin_col, then measures change_as - change_bs
        # For panel h: bin on CD_calc_BS, measure K_AS - K_BS
        # Let me fix the call — the helper subtracts change_col_as - change_col_bs
        ax_h.clear()
        self._fig4_boxplot_binned(ax_h, paired, col_K,
                                  'CD_calc_BS', f'{col_K}_BS', f'{col_K}_AS',
                                  'BS CD (cells/mm\u00b2)',
                                  '\u0394K$_{ds}$ (\u00b5m$^{-2}$)', 'h')
        ax_h.set_box_aspect(0.9)
        _p = ax_h.get_position()
        _dw, _dh = _p.width * 0.35 / 2, _p.height * 0.35 / 2
        ax_h.set_position([_p.x0 + _dw, _p.y0 + _dh, _p.width * 0.65, _p.height * 0.65])
        # Move legend outside
        _leg_h = ax_h.get_legend()
        if _leg_h:
            _leg_h.set_bbox_to_anchor((-0.70, 1.02), transform=ax_h.transAxes)
            _leg_h._loc = 3

        ax_i = fig.add_subplot(gs_row3[0, 1])
        self._fig4_boxplot_binned(ax_i, paired, col_K,
                                  f'{col_K}_BS', 'CD_calc_BS', 'CD_calc_AS',
                                  'BS K$_{ds}$ (\u00b5m$^{-2}$)',
                                  '\u0394CD (cells/mm\u00b2)', 'i')
        ax_i.set_box_aspect(0.9)
        _p = ax_i.get_position()
        _dw, _dh = _p.width * 0.35 / 2, _p.height * 0.35 / 2
        ax_i.set_position([_p.x0 + _dw, _p.y0 + _dh, _p.width * 0.65, _p.height * 0.65])

        # ── Row 4: Phase portraits (j, k) ──
        # Prepare phase field data
        p_phase = paired.dropna(subset=[f'{col_K}_BS', f'{col_K}_AS',
                                        'CD_calc_BS', 'CD_calc_AS']).copy()
        for col in [f'{col_K}_BS', f'{col_K}_AS']:
            p1, p99 = np.percentile(p_phase[col], [1, 99])
            p_phase = p_phase[(p_phase[col] >= p1) & (p_phase[col] <= p99)]

        cd_bs = p_phase['CD_calc_BS'].values
        k_bs = p_phase[f'{col_K}_BS'].values
        dcd_ph = p_phase['CD_calc_AS'].values - cd_bs
        dk_ph = p_phase[f'{col_K}_AS'].values - k_bs
        mask_ph = np.isfinite(cd_bs) & np.isfinite(k_bs) & np.isfinite(dcd_ph) & np.isfinite(dk_ph)
        R_cdk = self._compute_phase_field(cd_bs[mask_ph], k_bs[mask_ph],
                                          dcd_ph[mask_ph], dk_ph[mask_ph], seed=123)

        ax_j = fig.add_subplot(gs_row4[0, 0])
        self._fig4_phase_panel(ax_j, R_cdk, 'CD', 'K',
                               'Cell Density (cells/mm\u00b2)',
                               'K$_{ds}$ (\u00b5m$^{-2}$)',
                               lambda x, _: f'{x/1000:.1f}k', 'j')
        ax_j.set_box_aspect(0.9)
        _p = ax_j.get_position()
        _dw, _dh = _p.width * 0.35 / 2, _p.height * 0.35 / 2
        ax_j.set_position([_p.x0 + _dw, _p.y0 + _dh, _p.width * 0.65, _p.height * 0.65])
        _leg_j = ax_j.get_legend()
        if _leg_j:
            _leg_j.set_bbox_to_anchor((-0.30, 1.02), transform=ax_j.transAxes)

        # r₀-K phase portrait (if r₀ available)
        r0_col = 'r_0_um'
        ax_k = fig.add_subplot(gs_row4[0, 1])
        if f'{r0_col}_BS' in p_phase.columns and f'{r0_col}_AS' in p_phase.columns:
            r0_bs = p_phase[f'{r0_col}_BS'].values
            k_bs2 = p_phase[f'{col_K}_BS'].values
            dr0 = p_phase[f'{r0_col}_AS'].values - r0_bs
            dk2 = p_phase[f'{col_K}_AS'].values - k_bs2
            mask_r0 = np.isfinite(r0_bs) & np.isfinite(k_bs2) & np.isfinite(dr0) & np.isfinite(dk2)
            R_r0k = self._compute_phase_field(r0_bs[mask_r0], k_bs2[mask_r0],
                                              dr0[mask_r0], dk2[mask_r0], seed=456)
            self._fig4_phase_panel(ax_k, R_r0k, '$r_0$', 'K',
                                   'r$_0$ (\u00b5m)',
                                   'K$_{ds}$ (\u00b5m$^{-2}$)',
                                   lambda x, _: f'{x:.0f}', 'k')
        else:
            ax_k.text(0.5, 0.5, 'r\u2080 data\nnot available',
                      transform=ax_k.transAxes, ha='center', va='center',
                      fontsize=9, color='#999')
            self._fig4_panel_label(ax_k, 'k')
        ax_k.set_box_aspect(0.9)
        _p = ax_k.get_position()
        _dw, _dh = _p.width * 0.35 / 2, _p.height * 0.35 / 2
        ax_k.set_position([_p.x0 + _dw, _p.y0 + _dh, _p.width * 0.65, _p.height * 0.65])

        if save:
            self._pub_save(fig, 'fig4_collective_order')
        plt.show()


    # ==================================================================
    # MECHANICAL DISEQUILIBRIUM (Fig 5) — Rows 1-2 only (a-h)
    # Row 1: (a) Truss schematic | (b) Low-stress | (c) High-stress | (d) |F| histogram
    # Row 2: (e) ΔF vs ΔCD       | (f) ΔK vs ΔF  | (g) K vs |F|    | (h) CD-K saddle
    # ==================================================================

    def pub_mechanical_disequilibrium(self, image_folder=None, pixel_size=0.58, save=None):
        """
        Publication Figure 5 — Mechanical disequilibrium (2-row version).

        Row 1 (a-d): Spatial stress maps for lowest/highest mean|F| donors.
        Row 2 (e-h): Population-level force–order relationships.

        Parameters
        ----------
        image_folder : str or Path, optional
            Folder with images for Row 1. If None, uses self.image_folder.
        pixel_size : float
            µm/px calibration.
        """
        save = save if save is not None else self.save
        self._pub_style()

        from matplotlib.collections import LineCollection
        from numpy.polynomial.polynomial import polyfit

        paired = self.paired.copy()
        col_K = 'K_ds_um'
        C_BS, C_AS = '#4A90D9', '#E8833A'

        # Check required columns
        need_cols = ['mean_F_BS', 'mean_F_AS']
        if not all(c in paired.columns for c in need_cols):
            print(f"  ⚠ Mechanical columns missing. Need: {need_cols}")
            return

        paired['dK_pct'] = (paired[f'{col_K}_AS'] - paired[f'{col_K}_BS']) / paired[f'{col_K}_BS'] * 100

        def _clip(x, y, pct=2):
            xlo, xhi = np.percentile(x, [pct, 100 - pct])
            ylo, yhi = np.percentile(y, [pct, 100 - pct])
            m = (x >= xlo) & (x <= xhi) & (y >= ylo) & (y <= yhi)
            return x[m], y[m], m

        # ── Figure layout: 190mm × 160mm, 2 rows ──
        fig_w = 190 / 25.4
        fig_h = 160 / 25.4
        fig = plt.figure(figsize=(fig_w, fig_h))

        gs_row1 = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1],
                                    left=0.08, right=0.95, top=0.95, bottom=0.55,
                                    wspace=0.45)
        gs_row2 = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.3],
                                    left=0.08, right=0.95, top=0.50, bottom=0.16,
                                    wspace=0.48)

        # ══════════════════════════════════════════════════════════
        # ROW 1 (a-d): SPATIAL STRESS MAPS
        # ══════════════════════════════════════════════════════════

        img_folder = image_folder or self.image_folder
        res_low, res_high = None, None
        K_low, K_high = None, None

        if img_folder is not None:
            try:
                from cornealia.cornealia import cornealia as Cornealia

                bs_data = self.df[self.df['group'] == 'BS'].copy()
                if 'mean_F' in bs_data.columns:
                    bs_sorted = bs_data.dropna(subset=['mean_F']).sort_values('mean_F')
                    low_name = bs_sorted.iloc[0]['Image_Name'] if len(bs_sorted) > 0 else None
                    high_name = bs_sorted.iloc[-1]['Image_Name'] if len(bs_sorted) > 0 else None
                else:
                    low_name, high_name = None, None

                engine = Cornealia(pixel_size=pixel_size,
                                   is_input_image_machine_output=False, verbose=False)

                for name, label in [(low_name, 'low'), (high_name, 'high')]:
                    if name is None:
                        continue
                    img_path = Path(img_folder) / (name if '.' in name else name + '.png')
                    if not img_path.exists():
                        for ext in ['.png', '.jpg', '.bmp', '.tif', '.tiff']:
                            candidate = Path(img_folder) / (Path(name).stem + ext)
                            if candidate.exists():
                                img_path = candidate
                                break
                    if img_path.exists():
                        r = engine.mechanical_state(str(img_path))
                        rf = r.get('residual_field')
                        if rf is not None:
                            if label == 'low':
                                res_low = rf
                                K_low = r.get('K_ds', r.get('K'))
                                if K_low:
                                    K_low = float(K_low) / (pixel_size ** 2)
                            else:
                                res_high = rf
                                K_high = r.get('K_ds', r.get('K'))
                                if K_high:
                                    K_high = float(K_high) / (pixel_size ** 2)

                engine._ocr_reader = None
                del engine
            except Exception as e:
                print(f"  ⚠ Row 1 failed: {e}")

        vmax = np.percentile(res_high['F_mag'], 95) if res_high is not None else 1.0

        # Panel a: Truss schematic
        ax_a = fig.add_subplot(gs_row1[0, 0])
        if res_low is not None:
            pts = res_low['pts_um']
            edges = res_low['edges']
            d_um = res_low['d_um']
            r0 = res_low['r0']
            segments = [[pts[i], pts[j]] for i, j in edges]
            edge_colors = ['#CC3311' if d_um[k] < r0 else '#0077BB'
                           for k in range(len(edges))]
            ax_a.add_collection(LineCollection(segments, colors=edge_colors,
                                              linewidths=0.3, alpha=0.35, zorder=1))
            ax_a.scatter(pts[:, 0], pts[:, 1], s=2, c='white', edgecolors='#333',
                         linewidths=0.2, zorder=2, alpha=0.8)
            ax_a.set_xlim(pts[:, 0].min(), pts[:, 0].max())
            ax_a.set_ylim(pts[:, 1].max(), pts[:, 1].min())
            ax_a.set_aspect('equal')
        else:
            ax_a.text(0.5, 0.5, 'No image data', transform=ax_a.transAxes,
                      ha='center', va='center', fontsize=9, color='#999')
        ax_a.set_xlabel('x (µm)')
        ax_a.spines['top'].set_visible(False)
        ax_a.spines['right'].set_visible(False)
        self._fig4_panel_label(ax_a, 'a')

        # Panels b, c: Force fields
        for idx, (res, K_val, subtitle, show_cb, label) in enumerate([
            (res_low, K_low, 'Low stress', False, 'b'),
            (res_high, K_high, 'High stress', True, 'c'),
        ]):
            ax = fig.add_subplot(gs_row1[0, idx + 1])
            if res is not None:
                sc = ax.scatter(res['pts_um'][:, 0], res['pts_um'][:, 1],
                                c=res['F_mag'], s=8, cmap='YlOrRd',
                                vmin=0, vmax=vmax, edgecolors='none', zorder=2)
                threshold = np.percentile(res['F_mag'], 70)
                high = res['F_mag'] >= threshold
                if high.any():
                    scale = np.percentile(res['F_mag'][high], 95)
                    ax.quiver(res['pts_um'][high, 0], res['pts_um'][high, 1],
                              res['F_residual'][high, 0], res['F_residual'][high, 1],
                              res['F_mag'][high], cmap='YlOrRd', clim=(0, vmax),
                              scale=scale * 18, width=0.004, headwidth=3,
                              headlength=3.5, alpha=0.75, zorder=3)
                if show_cb:
                    plt.colorbar(sc, ax=ax, shrink=0.55, pad=0.02, aspect=12).set_label(
                        r'$|F_i|$', fontsize=8)
                ax.set_aspect('equal')
                K_str = f'{K_val:.3f}' if K_val is not None else '?'
                ax.text(0.97, 0.03,
                        f'$K_{{ds}}$={K_str}\nmean$|F|$={res["F_mag"].mean():.2f}',
                        transform=ax.transAxes, fontsize=6, fontweight='bold',
                        color='white', ha='right', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='black',
                                  alpha=0.6, edgecolor='none'))
            else:
                ax.text(0.5, 0.5, 'No data', transform=ax.transAxes,
                        ha='center', va='center', fontsize=9, color='#999')
            ax.set_xlabel('x (µm)')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            self._fig4_panel_label(ax, label)
            # Shift panel c a little to the left
            if label == 'c':
                _pc = ax.get_position()
                ax.set_position([_pc.x0 - 0.03, _pc.y0, _pc.width, _pc.height])

        # Panel d: |F| histogram overlay
        ax_d = fig.add_subplot(gs_row1[0, 3])
        ax_d.set_box_aspect(0.75)  # match height of equal-aspect panels a-c
        # Shift panel d a little to the right
        _pd = ax_d.get_position()
        ax_d.set_position([_pd.x0 + 0.03, _pd.y0, _pd.width, _pd.height])
        if res_low is not None and res_high is not None:
            F_lo, F_hi = res_low['F_mag'], res_high['F_mag']
            bins = np.linspace(0, np.percentile(np.concatenate([F_lo, F_hi]), 98), 30)
            ax_d.hist(F_lo, bins=bins, color=C_BS, alpha=0.5, edgecolor='white',
                      lw=0.3, density=True, label='Low stress')
            ax_d.hist(F_hi, bins=bins, color='#CC3311', alpha=0.5, edgecolor='white',
                      lw=0.3, density=True, label='High stress')
            ax_d.axvline(F_lo.mean(), color=C_BS, lw=1.5, ls='--', alpha=0.8)
            ax_d.axvline(F_hi.mean(), color='#CC3311', lw=1.5, ls='--', alpha=0.8)
            ax_d.legend(fontsize=6, loc='upper right')
        else:
            ax_d.text(0.5, 0.5, 'No image data', transform=ax_d.transAxes,
                      ha='center', va='center', fontsize=9, color='#999')
        ax_d.set_xlabel(r'$|F_i|$ (µm$^{-1}$)')
        ax_d.set_ylabel('Density')
        ax_d.spines['top'].set_visible(False)
        ax_d.spines['right'].set_visible(False)
        self._fig4_panel_label(ax_d, 'd')

        # ══════════════════════════════════════════════════════════
        # ROW 2 (e-h): POPULATION FORCE-ORDER RELATIONSHIPS
        # ══════════════════════════════════════════════════════════

        # Panel e: ΔF vs ΔCD hexbin
        ax_e = fig.add_subplot(gs_row2[0, 0])
        dF = (paired['mean_F_AS'] - paired['mean_F_BS']).values
        dCD = (paired['CD_calc_AS'] - paired['CD_calc_BS']).values
        valid_e = np.isfinite(dF) & np.isfinite(dCD)
        dCD_c, dF_c, _ = _clip(dCD[valid_e], dF[valid_e], pct=1)
        hb = ax_e.hexbin(dCD_c, dF_c, gridsize=18, cmap='Greys', mincnt=1, zorder=1)
        cb = plt.colorbar(hb, ax=ax_e, shrink=0.35, pad=0.02, aspect=15)
        cb.ax.set_title('Count', fontsize=7, fontweight='bold', pad=3)
        cb.ax.tick_params(labelsize=6)
        coeffs = polyfit(dCD_c, dF_c, 1)
        x_fit = np.linspace(dCD_c.min(), dCD_c.max(), 100)
        ax_e.plot(x_fit, coeffs[0] + coeffs[1] * x_fit, '--', color='#E65100',
                  linewidth=2.0, alpha=0.8, zorder=3)
        ax_e.axhline(0, color='black', lw=0.8, ls=':', zorder=1)
        ax_e.axvline(0, color='black', lw=0.8, ls=':', zorder=1)
        ax_e.set_xlabel(r'$\Delta$CD (cells/mm$^2$)')
        ax_e.set_ylabel(r'$\Delta$ mean $|F|$ (µm$^{-1}$)')
        ax_e.spines['top'].set_visible(False)
        ax_e.spines['right'].set_visible(False)
        rho_e, p_e = spearmanr(dCD_c, dF_c)
        ax_e.text(0.95, 0.03, f'ρ = {rho_e:.3f}\np = {p_e:.1e}',
                  transform=ax_e.transAxes, fontsize=7, ha='right', va='bottom',
                  fontweight='bold', color='#333',
                  bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                            alpha=0.8, edgecolor='none'))
        ax_e.set_box_aspect(1)
        self._fig4_panel_label(ax_e, 'e')

        # Panel f: ΔK vs ΔF hexbin (co-evolution)
        ax_f = fig.add_subplot(gs_row2[0, 1])
        dK = paired['dK_pct'].values
        valid_f = np.isfinite(dK) & np.isfinite(dF)
        dF_f, dK_f, _ = _clip(dF[valid_f], dK[valid_f], pct=1)
        hb = ax_f.hexbin(dF_f, dK_f, gridsize=18, cmap='Greys', mincnt=1, zorder=1)
        cb = plt.colorbar(hb, ax=ax_f, shrink=0.35, pad=0.02, aspect=15)
        cb.ax.set_title('Count', fontsize=7, fontweight='bold', pad=3)
        cb.ax.tick_params(labelsize=6)
        coeffs = polyfit(dF_f, dK_f, 1)
        x_fit = np.linspace(dF_f.min(), dF_f.max(), 100)
        ax_f.plot(x_fit, coeffs[0] + coeffs[1] * x_fit, '--', color='#E65100',
                  linewidth=2.0, alpha=0.8, zorder=3)
        ax_f.axhline(0, color='black', lw=0.8, ls=':', zorder=1)
        ax_f.axvline(0, color='black', lw=0.8, ls=':', zorder=1)
        ax_f.set_xlabel(r'$\Delta$ mean $|F|$ (µm$^{-1}$)')
        ax_f.set_ylabel(r'$\Delta K_{ds}$ (%)')
        ax_f.spines['top'].set_visible(False)
        ax_f.spines['right'].set_visible(False)
        rho_f, p_f = spearmanr(dF_f, dK_f)
        ax_f.text(0.95, 0.03, f'ρ = {rho_f:.3f}\np = {p_f:.1e}',
                  transform=ax_f.transAxes, fontsize=7, ha='right', va='bottom',
                  fontweight='bold', color='#333',
                  bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                            alpha=0.8, edgecolor='none'))
        ax_f.text(0.03, 0.97, 'F↓ K↑', transform=ax_f.transAxes, fontsize=6,
                  ha='left', va='top', color='#888', fontweight='bold')
        ax_f.text(0.97, 0.97, 'F↑ K↑', transform=ax_f.transAxes, fontsize=6,
                  ha='right', va='top', color='#CC3311', fontweight='bold')
        ax_f.text(0.03, 0.35, 'F↓ K↓', transform=ax_f.transAxes, fontsize=6,
                  ha='left', va='top', color='#CC3311', fontweight='bold')
        ax_f.text(0.97, 0.35, 'F↑ K↓', transform=ax_f.transAxes, fontsize=6,
                  ha='right', va='top', color='#888', fontweight='bold')
        ax_f.set_box_aspect(1)
        self._fig4_panel_label(ax_f, 'f')

        # Panel g: K vs |F| baseline scatter + LOWESS
        ax_g = fig.add_subplot(gs_row2[0, 2])
        K_all = paired[f'{col_K}_BS'].values
        F_all = paired['mean_F_BS'].values
        valid_g = np.isfinite(K_all) & np.isfinite(F_all)
        K_all, F_all = K_all[valid_g], F_all[valid_g]
        p99 = np.percentile(K_all, 99)
        m99 = K_all <= p99
        ax_g.scatter(K_all[m99], F_all[m99], s=4, alpha=0.3, color='#333', edgecolors='none')
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess
            si = np.argsort(K_all[m99])
            lw_fit = lowess(F_all[m99][si], K_all[m99][si], frac=0.4)
            ax_g.plot(lw_fit[:, 0], lw_fit[:, 1], '-', color='#E65100', linewidth=2.5)
        except ImportError:
            pass
        rho_g, p_g = spearmanr(K_all[m99], F_all[m99])
        ax_g.text(0.05, 0.95, f'ρ = {rho_g:.3f}\nn = {len(K_all[m99])}',
                  transform=ax_g.transAxes, fontsize=7, fontweight='bold', va='top',
                  bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                            alpha=0.8, edgecolor='none'))
        ax_g.set_xlabel(r'$K_{ds}$ (µm$^{-2}$)')
        ax_g.set_ylabel(r'mean $|F|$ (µm$^{-1}$)')
        ax_g.spines['top'].set_visible(False)
        ax_g.spines['right'].set_visible(False)
        ax_g.set_box_aspect(1)
        self._fig4_panel_label(ax_g, 'g')
        # Shrink 20% diagonally (center-anchored)
        _pg = ax_g.get_position()
        _dw, _dh = _pg.width * 0.20 / 2, _pg.height * 0.20 / 2
        ax_g.set_position([_pg.x0 + _dw, _pg.y0 + _dh, _pg.width * 0.80, _pg.height * 0.80])

        # Panel h: CD-K saddle colored by baseline |F|
        ax_h = fig.add_subplot(gs_row2[0, 3])
        self._fig5_saddle_panel(ax_h, paired, col_K)
        ax_h.set_box_aspect(1)

        if save:
            self._pub_save(fig, 'fig5_mechanical_disequilibrium')
        plt.show()

    def _fig5_saddle_panel(self, ax, paired, col_K):
        """CD-K phase portrait with donors colored by baseline mean|F|."""
        from scipy.optimize import brentq

        cd_bs = paired['CD_calc_BS'].values
        k_bs = paired[f'{col_K}_BS'].values
        cd_as = paired['CD_calc_AS'].values
        k_as = paired[f'{col_K}_AS'].values
        f_bs = paired['mean_F_BS'].values

        valid = (np.isfinite(cd_bs) & np.isfinite(k_bs) &
                 np.isfinite(cd_as) & np.isfinite(k_as) & np.isfinite(f_bs))
        cd_bs, k_bs = cd_bs[valid], k_bs[valid]
        cd_as, k_as = cd_as[valid], k_as[valid]
        f_bs = f_bs[valid]
        dcd = cd_as - cd_bs
        dk = k_as - k_bs

        lo, hi = np.percentile(k_bs, [1, 99])
        trim = (k_bs >= lo) & (k_bs <= hi)
        cd_bs, k_bs, dcd, dk, f_bs = (cd_bs[trim], k_bs[trim], dcd[trim],
                                        dk[trim], f_bs[trim])

        # Phase field
        R = self._compute_phase_field(cd_bs, k_bs, dcd, dk, seed=999)

        # Scatter colored by |F|
        C_BS, C_AS = '#4A90D9', '#E8833A'
        s_lim = np.percentile(f_bs, 95)
        sc = ax.scatter(cd_bs, k_bs, c=f_bs, s=4, cmap='YlOrRd',
                        vmin=0, vmax=s_lim, alpha=0.5, edgecolors='none',
                        zorder=1, rasterized=True)
        cb = plt.colorbar(sc, ax=ax, shrink=0.5, pad=0.02)
        cb.set_label('mean |F| (µm$^{-1}$)', fontsize=6, fontweight='bold')
        cb.ax.tick_params(labelsize=6)

        # Quiver field
        U, V = R['U'].copy(), R['V'].copy()
        dmask = self._density_mask(R['X_g'], R['K_g'], R['x_bs'], R['y_bs'])
        U[~dmask] = np.nan
        V[~dmask] = np.nan
        mag = np.sqrt(np.nan_to_num(U) ** 2 + np.nan_to_num(V) ** 2)
        ax.quiver(R['X_g'], R['K_g'],
                  U * R['x_sd'], V * R['y_sd'], mag,
                  cmap='cool', alpha=0.7, angles='xy', scale_units='xy', scale=1,
                  width=0.004, headwidth=4, headlength=5, zorder=3)

        # Nullclines + fixed point
        try:
            cd_null = brentq(R['f_dy'], R['x_mids'][0], R['x_mids'][-1])
            ax.axvline(cd_null, color=C_AS, ls='--', lw=1.0, alpha=0.7)
        except ValueError:
            cd_null = None
        try:
            k_null = brentq(R['f_dx'], R['y_mids'][0], R['y_mids'][-1])
            ax.axhline(k_null, color=C_BS, ls='--', lw=1.0, alpha=0.7)
        except ValueError:
            k_null = None
        if cd_null is not None and k_null is not None:
            ax.plot(cd_null, k_null, '*', color='#E65100', markersize=12,
                    markeredgecolor='white', markeredgewidth=0.8, zorder=10)

        ax.set_xlabel('Cell Density (cells/mm²)')
        ax.set_ylabel(r'K$_{ds}$ (µm$^{-2}$)')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1000:.1f}k'))
        self._fig4_panel_label(ax, 'h')


    # ==================================================================
    # ALL AT ONCE
    # ==================================================================

    def all(self, save=None):
        """Run all plot methods in sequence."""
        save = save if save is not None else self.save
        self.pub_boxplots(save=save)
        self.pub_K_deep_dive(save=save)
        self.pub_validation(save=save)
        self.pub_collective_order(save=save)
        self.pub_mechanical_disequilibrium(save=save)
