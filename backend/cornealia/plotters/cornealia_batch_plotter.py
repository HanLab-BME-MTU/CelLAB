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
from scipy.spatial import Voronoi
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

    # ==================================================================
    # CATEGORY 1 — DISTRIBUTIONS
    # ==================================================================

    def distributions(self, save=None):
        """2×3 grid of histograms for all computed metrics."""
        save = save if save is not None else self.save

        avail = {k: v for k, v in COMPUTED_METRICS.items() if v[0] in self.df.columns}
        n = len(avail)
        ncols = 3
        nrows = max(1, (n + ncols - 1) // ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(15, nrows * 4.5))
        if nrows * ncols > 1:
            axes = axes.flatten()
        else:
            axes = [axes]
        for j in range(n, len(axes)):
            axes[j].set_visible(False)

        for i, (key, (col, label, unit)) in enumerate(avail.items()):
            ax = axes[i]
            data = self.df[col].dropna()
            ax.hist(data, bins=30, color=COLORS['neutral'], edgecolor='black',
                    linewidth=0.8, alpha=0.85)
            mean_val = data.mean()
            ax.axvline(mean_val, color=COLORS['AS'], linestyle='--', linewidth=2,
                       label=f'Mean = {mean_val:.2f}')
            ax.set_xlabel(f'{label} ({unit})', fontsize=12, fontweight='bold')
            ax.set_ylabel('Count', fontsize=12, fontweight='bold')
            ax.set_title(f'{label}', fontsize=13, fontweight='bold')
            ax.legend(fontsize=9, loc='upper right')
            ax.tick_params(axis='both', labelsize=10)
            sns.despine(ax=ax)

        plt.suptitle(f'Distribution of Computed Metrics (n = {len(self.df)})',
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        if save:
            self._save_fig(fig, '01_distributions')
        plt.show()

    def as_vs_bs_improvement(self, metric='K_um', save=None):
        """
        2×2 panel analysing per-patient improvement for a single metric:
          - histogram of % change
          - histogram of absolute change
          - scatter colored by improvement
          - summary stats box

        Parameters
        ----------
        metric : str
            Key from COMPUTED_METRICS (default 'K_um')
        save : bool or None
        """
        save = save if save is not None else self.save

        if len(self.paired) == 0:
            print("No paired AS/BS data available.")
            return

        col, label, unit = COMPUTED_METRICS[metric]
        col_as = f'{col}_AS'
        col_bs = f'{col}_BS'

        if col_as not in self.paired.columns:
            print(f"Column {col_as} not found in paired data.")
            return

        paired = self.paired.copy()
        paired['_diff'] = paired[col_as] - paired[col_bs]

        # Filter valid pairs (BS > small threshold to avoid division by zero)
        threshold = paired[col_bs].quantile(0.01) if paired[col_bs].quantile(0.01) > 0 else 1e-6
        valid = paired[paired[col_bs] > threshold].copy()
        valid['_pct_change'] = (valid[col_as] - valid[col_bs]) / valid[col_bs] * 100

        # --- Stats ---
        improved = valid['_diff'] > 0
        n_improved = improved.sum()
        n_total = len(valid)
        median_pct = valid['_pct_change'].median()
        mean_diff = valid['_diff'].mean()
        sd_diff = valid['_diff'].std()

        t_stat, p_ttest = stats.ttest_rel(valid[col_as], valid[col_bs])
        w_stat, p_wilcox = stats.wilcoxon(valid['_diff'])

        plain_label, plain_unit = PLAIN_LABELS[metric]
        print(f"\n{plain_label} Improvement Analysis ({plain_unit})")
        print(f"  Valid pairs: {n_total}")
        print(f"  Improved (AS > BS): {n_improved}/{n_total} ({n_improved/n_total*100:.1f}%)")
        print(f"  Median delta%: {median_pct:+.1f}%")
        print(f"  Mean delta: {mean_diff:+.4f} +/- {sd_diff:.4f} {plain_unit}")
        print(f"  Paired t-test: t = {t_stat:.3f}, p = {p_ttest:.2e}")
        print(f"  Wilcoxon: p = {p_wilcox:.2e}")

        # --- Figure: 2×2 ---
        fig, axes = plt.subplots(2, 2, figsize=(13, 10))

        # 1. Histogram of % change
        ax = axes[0, 0]
        pct_clipped = valid['_pct_change'].clip(-200, 500)
        ax.hist(pct_clipped, bins=50, color=COLORS['BS'], edgecolor='black',
                linewidth=0.5, alpha=0.8)
        ax.axvline(0, color='red', linestyle='--', linewidth=2, label='No change')
        ax.axvline(median_pct, color=COLORS['AS'], linestyle='-', linewidth=2,
                   label=f'Median = {median_pct:+.1f}%')
        ax.set_xlabel(f'{label} change (%)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Count', fontsize=13, fontweight='bold')
        ax.set_title(f'Distribution of {label} Change (AS vs BS)',
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.tick_params(axis='both', labelsize=11)
        sns.despine(ax=ax)

        # 2. Histogram of absolute difference
        ax = axes[0, 1]
        ax.hist(valid['_diff'], bins=50, color=COLORS['computed'], edgecolor='black',
                linewidth=0.5, alpha=0.8)
        ax.axvline(0, color='red', linestyle='--', linewidth=2, label='No change')
        ax.axvline(mean_diff, color=COLORS['AS'], linestyle='-', linewidth=2,
                   label=f'Mean = {mean_diff:+.4f}')
        ax.set_xlabel(r'$\Delta$' + f'{label} = AS - BS ({unit})', fontsize=13, fontweight='bold')
        ax.set_ylabel('Count', fontsize=13, fontweight='bold')
        ax.set_title(f'Distribution of Absolute {label} Change',
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.tick_params(axis='both', labelsize=11)
        sns.despine(ax=ax)

        # 3. Scatter colored by improvement
        ax = axes[1, 0]
        ax.scatter(valid.loc[~improved, col_bs], valid.loc[~improved, col_as],
                   c=COLORS['BS'], s=20, alpha=0.4,
                   label=f'Decreased ({(~improved).sum()})')
        ax.scatter(valid.loc[improved, col_bs], valid.loc[improved, col_as],
                   c=COLORS['AS'], s=20, alpha=0.4,
                   label=f'Improved ({improved.sum()})')
        all_vals = pd.concat([valid[col_bs], valid[col_as]])
        lims = [0, all_vals.max() * 1.05]
        ax.plot(lims, lims, '--', color=COLORS['identity'], linewidth=1.5)
        ax.set_xlabel(f'BS — {label} ({unit})', fontsize=13, fontweight='bold')
        ax.set_ylabel(f'AS — {label} ({unit})', fontsize=13, fontweight='bold')
        ax.set_title(f'Paired Scatter (colored by improvement)',
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=10, loc='upper left')
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.tick_params(axis='both', labelsize=11)
        sns.despine(ax=ax)

        # 4. Summary text box
        ax = axes[1, 1]
        ax.axis('off')
        plain_label, plain_unit = PLAIN_LABELS[metric]
        summary = (
            f"{'='*44}\n"
            f"   {plain_label.upper()} IMPROVEMENT ANALYSIS\n"
            f"{'='*44}\n\n"
            f"  Valid pairs:        {n_total}\n"
            f"  Improved (AS > BS): {n_improved} ({n_improved/n_total*100:.1f}%)\n"
            f"  Decreased:          {n_total - n_improved} ({(n_total-n_improved)/n_total*100:.1f}%)\n\n"
            f"  Median delta%:      {median_pct:+.1f}%\n"
            f"  Mean delta:         {mean_diff:+.4f} {plain_unit}\n"
            f"  SD delta:           {sd_diff:.4f} {plain_unit}\n\n"
            f"  Paired t-test:      p = {p_ttest:.2e}\n"
            f"  Wilcoxon:           p = {p_wilcox:.2e}\n"
            f"{'='*44}"
        )
        ax.text(0.05, 0.5, summary, transform=ax.transAxes, fontsize=12,
                verticalalignment='center', fontfamily='monospace', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFACD',
                          edgecolor='black', linewidth=1.5, alpha=0.95))

        plt.suptitle(f'AS vs BS: {label} Improvement Analysis',
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        if save:
            self._save_fig(fig, f'05_{metric}_improvement')
        plt.show()

    def as_vs_bs_improvement_all(self, save=None):
        """Run improvement analysis for all computed metrics."""
        save = save if save is not None else self.save
        for key, (col, _, _) in COMPUTED_METRICS.items():
            if col in self.df.columns:
                self.as_vs_bs_improvement(metric=key, save=save)

    # ==================================================================
    # CATEGORY 5 — COMPREHENSIVE SINGLE-METRIC DEEP DIVE
    # ==================================================================

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
    # FIG 6: K INDEPENDENCE FROM CLASSICAL METRICS (2×2)
    # ==================================================================

    def pub_K_independence(self, save=None):
        """Publication-ready 2×2 showing K captures orthogonal information.

        (a) ΔK% vs ΔCD% — K improves even when CD drops
        (b) ΔK% vs ΔHEX% — K improves even when HEX drops
        (c) Baseline BS K vs ΔK% — does starting K predict improvement?
        (d) K vs CD scatter (all data) — weak correlation = independent info
        """
        self._pub_style()
        save = save if save is not None else self.save

        col_K = 'K_um'
        col_K_as, col_K_bs = f'{col_K}_AS', f'{col_K}_BS'

        # Prepare paired % changes
        paired = self.paired.copy()
        metrics_for_change = {
            'K_um':     ('$\\Delta K$',  '%'),
            'CD_calc':  ('$\\Delta$CD',  '%'),
            'HEX_calc': ('$\\Delta$HEX', '%'),
        }

        for m in metrics_for_change:
            col_as = f'{m}_AS'
            col_bs = f'{m}_BS'
            if col_as in paired.columns and col_bs in paired.columns:
                threshold = max(paired[col_bs].quantile(0.01), 1e-6)
                paired[f'{m}_pct'] = np.where(
                    paired[col_bs] > threshold,
                    (paired[col_as] - paired[col_bs]) / paired[col_bs] * 100,
                    np.nan
                )

        valid = paired.dropna(subset=['K_um_pct', 'CD_calc_pct', 'HEX_calc_pct'])

        fig_w = 190 / 25.4
        fig_h = fig_w * 0.85
        fig, axes = plt.subplots(2, 2, figsize=(fig_w, fig_h))
        labels_panel = ('(a)', '(b)', '(c)', '(d)')

        # ---- (a) ΔK% vs ΔCD% ----
        ax = axes[0, 0]
        # Clip for display
        x = valid['CD_calc_pct'].clip(-50, 50)
        y = valid['K_um_pct'].clip(-200, 500)
        colors = np.where(y > 0, COLORS['AS'], COLORS['BS'])
        ax.scatter(x, y, c=colors, s=6, alpha=0.4, edgecolor='none')
        ax.axhline(0, color='black', linestyle=':', linewidth=0.8)
        ax.axvline(0, color='black', linestyle=':', linewidth=0.8)

        # Quadrant labels
        ax.text(0.97, 0.97, 'K↑ CD↑', transform=ax.transAxes, fontsize=8,
                ha='right', va='top', fontweight='bold', color='#444444')
        ax.text(0.03, 0.97, 'K↑ CD↓', transform=ax.transAxes, fontsize=8,
                ha='left', va='top', fontweight='bold', color='#444444')
        ax.text(0.97, 0.03, 'K↓ CD↑', transform=ax.transAxes, fontsize=8,
                ha='right', va='bottom', fontweight='bold', color='#444444')
        ax.text(0.03, 0.03, 'K↓ CD↓', transform=ax.transAxes, fontsize=8,
                ha='left', va='bottom', fontweight='bold', color='#444444')

        ax.set_xlabel('$\\Delta$CD (%)', fontweight='bold')
        ax.set_ylabel('$\\Delta K$ (%)', fontweight='bold')
        ax.set_title('$\\Delta K$ vs $\\Delta$CD', fontweight='bold', fontsize=10, pad=4)
        ax.tick_params(axis='both', labelsize=8)
        sns.despine(ax=ax)
        self._pub_panel_label(ax, labels_panel[0])

        # ---- (b) ΔK% vs ΔHEX% ----
        ax = axes[0, 1]
        x = valid['HEX_calc_pct'].clip(-80, 80)
        y = valid['K_um_pct'].clip(-200, 500)
        colors = np.where(y > 0, COLORS['AS'], COLORS['BS'])
        ax.scatter(x, y, c=colors, s=6, alpha=0.4, edgecolor='none')
        ax.axhline(0, color='black', linestyle=':', linewidth=0.8)
        ax.axvline(0, color='black', linestyle=':', linewidth=0.8)

        # Quadrant labels
        ax.text(0.97, 0.97, 'K↑ HEX↑', transform=ax.transAxes, fontsize=8,
                ha='right', va='top', fontweight='bold', color='#444444')
        ax.text(0.03, 0.97, 'K↑ HEX↓', transform=ax.transAxes, fontsize=8,
                ha='left', va='top', fontweight='bold', color='#444444')
        ax.text(0.97, 0.03, 'K↓ HEX↑', transform=ax.transAxes, fontsize=8,
                ha='right', va='bottom', fontweight='bold', color='#444444')
        ax.text(0.03, 0.03, 'K↓ HEX↓', transform=ax.transAxes, fontsize=8,
                ha='left', va='bottom', fontweight='bold', color='#444444')

        ax.set_xlabel('$\\Delta$HEX (%)', fontweight='bold')
        ax.set_ylabel('$\\Delta K$ (%)', fontweight='bold')
        ax.set_title('$\\Delta K$ vs $\\Delta$HEX', fontweight='bold', fontsize=10, pad=4)
        ax.tick_params(axis='both', labelsize=8)
        sns.despine(ax=ax)
        self._pub_panel_label(ax, labels_panel[1])

        # ---- (c) Baseline K vs ΔK% — hexbin + LOWESS ----
        ax = axes[1, 0]
        bs_k = valid[col_K_bs]
        dk_pct = valid['K_um_pct'].clip(-200, 500)

        # Hexbin density background
        hb = ax.hexbin(bs_k, dk_pct, gridsize=30, cmap='YlOrRd', mincnt=1)
        cb = plt.colorbar(hb, ax=ax, shrink=0.8, pad=0.02)
        cb.set_label('Count', fontsize=7, fontweight='bold')
        cb.ax.tick_params(labelsize=6)
        ax.axhline(0, color='black', linestyle='--', linewidth=1)

        # LOWESS smooth curve
        from statsmodels.nonparametric.smoothers_lowess import lowess
        smooth = lowess(dk_pct.values, bs_k.values, frac=0.3, it=3)
        ax.plot(smooth[:, 0], smooth[:, 1], '-', color='black', linewidth=2,
                label='LOWESS')
        ax.legend(fontsize=6, loc='upper right')

        ax.set_xlabel('Baseline $K$ (BS, $\\mu m^{-2}$)', fontweight='bold')
        ax.set_ylabel('$\\Delta K$ (%)', fontweight='bold')
        ax.set_title('Baseline $K$ vs Improvement', fontweight='bold', fontsize=10, pad=4)
        ax.tick_params(axis='both', labelsize=8)
        self._pub_panel_label(ax, labels_panel[2])

        # ---- (d) K vs CD — hexbin density (all data) ----
        ax = axes[1, 1]
        merged = self.df[['K_um', 'CD_calc', 'group']].dropna()

        hb = ax.hexbin(merged['CD_calc'], merged['K_um'], gridsize=30,
                        cmap='YlOrRd', mincnt=1)
        cb = plt.colorbar(hb, ax=ax, shrink=0.8, pad=0.02)
        cb.set_label('Count', fontsize=7, fontweight='bold')
        cb.ax.tick_params(labelsize=6)

        ax.text(0.05, 0.95, f'n = {len(merged)}',
                transform=ax.transAxes, fontsize=7, fontweight='bold',
                va='top', ha='left',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='black', alpha=0.9))

        ax.set_xlabel('CD (cells/mm$^2$)', fontweight='bold')
        ax.set_ylabel('$K$ ($\\mu m^{-2}$)', fontweight='bold')
        ax.set_title('$K$ vs CD (all images)', fontweight='bold', fontsize=10, pad=4)
        ax.tick_params(axis='both', labelsize=8)
        self._pub_panel_label(ax, labels_panel[3])

        plt.tight_layout(pad=0.8, h_pad=1.5, w_pad=0.8)
        if save:
            self._pub_save(fig, 'fig6_K_independence')
        plt.show()

    # ==================================================================
    # COMPREHENSIVE FIGURE: K + METRICS + INDEPENDENCE (4×3)
    # ==================================================================

    def pub_comprehensive(self, gr_data=None, save=None, k_metric='K_ds_um'):
        """Publication-ready Figure 3: K analysis with quadrant and conditional analysis.

        Layout:
          Top row:
            Col 1: (a) g(r) + Dg(r) + g''(r)
            Col 2: (b) Paired K scatter + improvement bars | (c) Correlation matrix
            Col 3: (d) K vs CD + boxplots | (e) Forest plot
          Bottom row:
            (f) DK vs DCD + pie | (g) DK vs DHEX + pie | (h) Homeostatic setpoint

        Parameters
        ----------
        gr_data : dict, optional
            {'r': array, 'bs_curves': array, 'as_curves': array, 'pixel_size': float}
            If None, auto-loaded from NPZ if available.
        k_metric : str
            Which K column to use: 'K_ds_um', 'K_um', etc.
        """
        if gr_data is None:
            gr_data = self.gr_data
        import matplotlib.gridspec as gridspec
        from scipy.stats import ttest_rel, spearmanr, pearsonr
        from scipy.ndimage import uniform_filter1d
        from numpy import gradient as np_gradient
        from numpy.polynomial.polynomial import polyfit
        from matplotlib.patches import Rectangle, ConnectionPatch

        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess
        except ImportError:
            lowess = None

        self._pub_style()
        save = save if save is not None else self.save

        col_K = k_metric
        paired = self.paired.copy()
        plot_data = self.df[self.df['group'].isin(['AS', 'BS'])]
        n_pairs = len(paired)
        c_bs, c_as = COLORS['BS'], COLORS['AS']

        # --- Paired deltas ---
        dk = paired[f'{col_K}_AS'].values - paired[f'{col_K}_BS'].values
        dcd = paired['CD_calc_AS'].values - paired['CD_calc_BS'].values
        dhex = paired['HEX_calc_AS'].values - paired['HEX_calc_BS'].values
        dcv = paired['CV_calc_AS'].values - paired['CV_calc_BS'].values
        dave = paired['Ave_calc_AS'].values - paired['Ave_calc_BS'].values
        dr0 = paired['r_0_um_AS'].values - paired['r_0_um_BS'].values

        dk_pct = dk / paired[f'{col_K}_BS'].values * 100
        dcd_pct = dcd / paired['CD_calc_BS'].values * 100
        dhex_pct = dhex / paired['HEX_calc_BS'].values * 100

        # --- Helpers ---
        def _clip(x, y, pct=2):
            xlo, xhi = np.percentile(x, [pct, 100-pct])
            ylo, yhi = np.percentile(y, [pct, 100-pct])
            m = (x >= xlo) & (x <= xhi) & (y >= ylo) & (y <= yhi)
            return x[m], y[m], m

        def _quad_scatter(ax, x_pct, y_pct, x_label, y_label, highlight_pair):
            ax.scatter(x_pct, y_pct, s=3, c='#999', alpha=0.25, edgecolors='none')
            q_tl = (y_pct > 0) & (x_pct < 0)
            q_tr = (y_pct > 0) & (x_pct > 0)
            q_bl = (y_pct < 0) & (x_pct < 0)
            q_br = (y_pct < 0) & (x_pct > 0)
            h1, h2 = highlight_pair
            qmap = {'tl': q_tl, 'tr': q_tr, 'bl': q_bl, 'br': q_br}
            ax.scatter(x_pct[qmap[h1]], y_pct[qmap[h1]], s=4, c='#E65100', alpha=0.4, edgecolors='none')
            ax.scatter(x_pct[qmap[h2]], y_pct[qmap[h2]], s=4, c='#1565C0', alpha=0.4, edgecolors='none')
            ax.axhline(0, color='black', linewidth=0.5, linestyle=':')
            ax.axvline(0, color='black', linewidth=0.5, linestyle=':')
            x_s = x_label.replace('D', '').replace('d', '')
            quad_info = [('tl', q_tl, 'I', 0.03, 0.97, 'left', 'top'),
                         ('tr', q_tr, 'II', 0.97, 0.97, 'right', 'top'),
                         ('bl', q_bl, 'III', 0.03, 0.03, 'left', 'bottom'),
                         ('br', q_br, 'IV', 0.97, 0.03, 'right', 'bottom')]
            dir_map = {'tl': ('K+ ', '-'), 'tr': ('K+ ', '+'), 'bl': ('K- ', '-'), 'br': ('K- ', '+')}
            quad_colors = {}
            for key, q, num, px, py, ha, va in quad_info:
                col = '#E65100' if key == h1 else ('#1565C0' if key == h2 else '#888')
                quad_colors[key] = col
                kd, xd = dir_map[key]
                ax.text(px, py, f'{num}. {kd}{x_s}{xd}\n{q.sum()}', transform=ax.transAxes,
                        fontsize=4.5, ha=ha, va=va, color=col, fontweight='bold')
            rho, pval = spearmanr(x_pct, y_pct)
            ax.text(0.5, 0.03, f'rho={rho:.2f} (p={pval:.0e})', transform=ax.transAxes,
                    fontsize=5, ha='center', va='bottom', fontweight='bold')
            ax.set_xlabel(f'{x_label} (%)', fontsize=7)
            ax.set_ylabel(f'{y_label} (%)', fontsize=7)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            # Pie inset
            pie_order = ['tl', 'tr', 'br', 'bl']
            counts = [qmap[k].sum() for k in pie_order]
            pie_cols = [quad_colors[k] for k in pie_order]
            pie_nums = ['I', 'II', 'IV', 'III']
            ax_pie = ax.inset_axes([0.60, 0.60, 0.38, 0.38])
            wedges, _ = ax_pie.pie(counts, colors=pie_cols, startangle=90,
                                    wedgeprops=dict(linewidth=0.5, edgecolor='white', alpha=0.8))
            ax_pie.set_aspect('equal')
            total = sum(counts)
            for wedge, cnt, num in zip(wedges, counts, pie_nums):
                angle = (wedge.theta2 + wedge.theta1) / 2
                pct = 100 * cnt / total
                xp = 0.55 * np.cos(np.radians(angle))
                yp = 0.55 * np.sin(np.radians(angle))
                if pct > 8:
                    ax_pie.text(xp, yp, f'{num}\n{pct:.0f}%', ha='center', va='center',
                                fontsize=3.5, fontweight='bold', color='white')

        # =====================================================================
        # FIGURE
        # =====================================================================
        fig_w = 190 / 25.4
        fig_h = 220 / 25.4
        fig = plt.figure(figsize=(fig_w, fig_h))
        gs_main = gridspec.GridSpec(2, 3, figure=fig,
                                    height_ratios=[1.2, 0.55],
                                    hspace=0.15, wspace=0.35,
                                    left=0.07, right=0.97, top=0.97, bottom=0.04)

        # ===== (a) g(r) — 3 sub-rows =====
        gs_a = gridspec.GridSpecFromSubplotSpec(3, 1, subplot_spec=gs_main[0, 0],
                                                 hspace=0.25, height_ratios=[0.7, 0.5, 0.5])
        if gr_data is not None:
            pixel_size = gr_data.get('pixel_size', 0.58)
            r = gr_data['r'] * pixel_size
            bs_curves = gr_data['bs_curves']
            as_curves = gr_data['as_curves']
            bs_mean = np.mean(bs_curves, axis=0)
            as_mean = np.mean(as_curves, axis=0)
            bs_std = np.std(bs_curves, axis=0)
            as_std = np.std(as_curves, axis=0)

            r_min_z, r_max_z = 10, 30
            mask_peak = (r >= r_min_z) & (r <= r_max_z)
            r_z = r[mask_peak]

            # a1: full g(r)
            ax_a1 = fig.add_subplot(gs_a[0])
            ax_a1.fill_between(r, bs_mean - bs_std, bs_mean + bs_std, color=c_bs, alpha=0.12)
            ax_a1.fill_between(r, as_mean - as_std, as_mean + as_std, color=c_as, alpha=0.12)
            ax_a1.plot(r, bs_mean, color=c_bs, linewidth=1.5, label=f'BS (n={len(bs_curves)})')
            ax_a1.plot(r, as_mean, color=c_as, linewidth=1.5, label=f'AS (n={len(as_curves)})')
            ax_a1.axhline(1.0, color='gray', linewidth=0.5, linestyle='--')
            ax_a1.set_ylabel('g(r)', fontsize=7)
            ax_a1.set_xlabel('r (um)', fontsize=6)
            ax_a1.set_title('(a) Population g(r)', fontsize=8)
            ax_a1.legend(fontsize=5, loc='upper right')
            ax_a1.spines['top'].set_visible(False)
            ax_a1.spines['right'].set_visible(False)

            y_lo_box = min(bs_mean[mask_peak].min(), as_mean[mask_peak].min()) - 0.05
            y_hi_box = max(bs_mean[mask_peak].max(), as_mean[mask_peak].max()) + 0.05
            rect = Rectangle((r_min_z, y_lo_box), r_max_z - r_min_z, y_hi_box - y_lo_box,
                              linewidth=1, edgecolor='#999', facecolor='#f0f0f0', alpha=0.15, linestyle='--')
            ax_a1.add_patch(rect)

            # a2: Dg(r)
            ax_a2 = fig.add_subplot(gs_a[1])
            delta_smooth = uniform_filter1d(as_mean - bs_mean, size=5)
            n_boot = 1000
            boot_d = np.zeros((n_boot, len(r)))
            for b in range(n_boot):
                bs_s = bs_curves[np.random.choice(len(bs_curves), len(bs_curves), replace=True)]
                as_s = as_curves[np.random.choice(len(as_curves), len(as_curves), replace=True)]
                boot_d[b] = uniform_filter1d(np.mean(as_s, 0) - np.mean(bs_s, 0), size=5)
            ci_lo_a = np.percentile(boot_d, 2.5, axis=0)
            ci_hi_a = np.percentile(boot_d, 97.5, axis=0)
            ax_a2.fill_between(r_z, ci_lo_a[mask_peak], ci_hi_a[mask_peak], color='#ddd', alpha=0.5)
            ax_a2.plot(r_z, delta_smooth[mask_peak], color='#333', linewidth=1.2)
            ax_a2.axhline(0, color='black', linewidth=0.4, linestyle='--')
            sig_pos = ci_lo_a[mask_peak] > 0
            sig_neg = ci_hi_a[mask_peak] < 0
            if sig_pos.any():
                ax_a2.fill_between(r_z, ci_lo_a[mask_peak], ci_hi_a[mask_peak], where=sig_pos, color=c_as, alpha=0.4)
            if sig_neg.any():
                ax_a2.fill_between(r_z, ci_lo_a[mask_peak], ci_hi_a[mask_peak], where=sig_neg, color=c_bs, alpha=0.4)
            ax_a2.set_ylabel('Dg(r)', fontsize=6)
            ax_a2.set_xlim(r_min_z, r_max_z)
            ax_a2.set_xticklabels([])
            ax_a2.spines['top'].set_visible(False)
            ax_a2.spines['right'].set_visible(False)
            ax_a2.tick_params(axis='both', labelsize=5)
            ax_a2.text(0.02, 0.95, 'AS - BS', transform=ax_a2.transAxes, fontsize=5,
                       va='top', fontstyle='italic', color='#555')
            con = ConnectionPatch(xyA=(r_min_z, y_lo_box), coordsA=ax_a1.transData,
                                  xyB=(r_min_z, ax_a2.get_ylim()[1]), coordsB=ax_a2.transData,
                                  arrowstyle='->', color='#999', linewidth=0.8, linestyle='--')
            fig.add_artist(con)

            # a3: g''(r)
            ax_a3 = fig.add_subplot(gs_a[2])
            bs_sm = uniform_filter1d(bs_mean, size=7)
            as_sm = uniform_filter1d(as_mean, size=7)
            dr = np.mean(np.diff(r)) if len(r) > 1 else 1
            bs_d2 = np_gradient(np_gradient(bs_sm, dr), dr)
            as_d2 = np_gradient(np_gradient(as_sm, dr), dr)
            mask_curv = (r >= 16) & (r <= 21)
            r_curv = r[mask_curv]
            ax_a3.plot(r_curv, bs_d2[mask_curv], color=c_bs, linewidth=1.2, label='BS')
            ax_a3.plot(r_curv, as_d2[mask_curv], color=c_as, linewidth=1.2, label='AS')
            ax_a3.axhline(0, color='black', linewidth=0.4, linestyle='--')
            peak_idx = np.argmax(bs_sm[mask_peak]) + np.where(mask_peak)[0][0]
            ax_a3.axvline(r[peak_idx], color='#999', linewidth=0.4, linestyle=':')
            ax_a3.set_xlim(16, 21)
            ax_a3.set_xlabel('r (um)', fontsize=7)
            ax_a3.set_ylabel("g''(r)", fontsize=6)
            ax_a3.legend(fontsize=4, loc='lower right')
            ax_a3.spines['top'].set_visible(False)
            ax_a3.spines['right'].set_visible(False)
            ax_a3.tick_params(axis='both', labelsize=5)
            ax_a3.text(0.02, 0.95, 'curvature', transform=ax_a3.transAxes, fontsize=5,
                       va='top', fontstyle='italic', color='#555')

        # ===== Column 2: (b) Paired K + bars, (c) Corr matrix =====
        gs_bc = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_main[0, 1], hspace=0.12)

        # (b) Paired K scatter with bottom improvement bars
        gs_b_outer = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_bc[0],
                                                       height_ratios=[4, 1], hspace=0.03)
        ax_b = fig.add_subplot(gs_b_outer[0])
        bs_k = paired[f'{col_K}_BS'].values
        as_k = paired[f'{col_K}_AS'].values
        bs_kc, as_kc, mask_kc = _clip(bs_k, as_k, pct=2)
        dcd_p = paired['CD_calc_AS'].values - paired['CD_calc_BS'].values
        dcd_cl = dcd_p[mask_kc]
        cd_dn, cd_up_m = dcd_cl < 0, dcd_cl >= 0
        ax_b.scatter(bs_kc[cd_up_m], as_kc[cd_up_m], s=4, c=c_bs, alpha=0.25,
                     edgecolors='none', label=f'CD+ ({cd_up_m.sum()})')
        ax_b.scatter(bs_kc[cd_dn], as_kc[cd_dn], s=4, c=c_as, alpha=0.25,
                     edgecolors='none', label=f'CD- ({cd_dn.sum()})')
        lim_k = max(bs_kc.max(), as_kc.max()) * 1.05
        ax_b.plot([0, lim_k], [0, lim_k], 'k--', linewidth=0.5, alpha=0.4)
        ax_b.set_ylabel('AS -- K (um$^{-2}$)', fontsize=7)
        ax_b.set_title('(b) Paired K scatter', fontsize=8)
        ax_b.legend(fontsize=4, loc='upper left')
        ax_b.set_box_aspect(1)
        ax_b.set_xticklabels([])
        ax_b.spines['top'].set_visible(False)
        ax_b.spines['right'].set_visible(False)
        above = as_kc > bs_kc
        ax_b.text(0.95, 0.05, f'K+ : {above.sum()} ({100*above.mean():.0f}%)',
                  transform=ax_b.transAxes, fontsize=5, ha='right', va='bottom',
                  color=c_as, fontweight='bold')

        # Bottom bars: % improved by baseline K
        ax_b_bot = fig.add_subplot(gs_b_outer[1], sharex=ax_b)
        n_bins = 15
        bin_edges = np.linspace(bs_kc.min(), bs_kc.max(), n_bins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        bin_w = bin_edges[1] - bin_edges[0]
        dk_vals = as_kc - bs_kc
        frac_up = []
        for i in range(n_bins):
            mb = (bs_kc >= bin_edges[i]) & (bs_kc < bin_edges[i+1])
            frac_up.append(100 * (dk_vals[mb] > 0).sum() / mb.sum() if mb.sum() > 0 else 50)
        bar_cols = ['#E65100' if f > 55 else ('#1565C0' if f < 45 else '#aaa') for f in frac_up]
        ax_b_bot.bar(bin_centers, frac_up, width=bin_w * 0.85,
                     color=bar_cols, alpha=0.7, edgecolor='white', linewidth=0.3)
        ax_b_bot.axhline(50, color='black', linewidth=0.6, linestyle='--', alpha=0.5)
        ax_b_bot.set_xlabel('BS -- K (um$^{-2}$)', fontsize=7)
        ax_b_bot.set_ylabel('% improved', fontsize=5)
        ax_b_bot.set_xlim(0, lim_k)
        ax_b_bot.set_ylim(0, 85)
        ax_b_bot.set_yticks([0, 25, 50, 75])
        ax_b_bot.set_yticklabels(['0', '25', '50', '75'], fontsize=4)
        ax_b_bot.spines['top'].set_visible(False)
        ax_b_bot.spines['right'].set_visible(False)
        ax_b_bot.tick_params(axis='both', labelsize=5)

        # (c) Correlation matrix
        ax_c = fig.add_subplot(gs_bc[1])
        deltas = pd.DataFrame({'DK': dk, 'DCD': dcd, 'DHEX': dhex, 'DCV': dcv, 'DAve': dave, 'Dr0': dr0})
        corr = deltas.corr(method='spearman')
        im = ax_c.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='equal')
        lc = corr.columns.tolist()
        ax_c.set_xticks(range(len(lc)))
        ax_c.set_xticklabels(lc, fontsize=5, rotation=45, ha='right')
        ax_c.set_yticks(range(len(lc)))
        ax_c.set_yticklabels(lc, fontsize=5)
        ax_c.set_title('(c) Correlation matrix', fontsize=8)
        for ii in range(len(lc)):
            for jj in range(len(lc)):
                v = corr.iloc[ii, jj]
                ax_c.text(jj, ii, f'{v:.2f}', ha='center', va='center', fontsize=4.5,
                          color='white' if abs(v) > 0.5 else 'black', fontweight='bold')
        plt.colorbar(im, ax=ax_c, shrink=0.6, label='Spearman rho', pad=0.02)

        # ===== Column 3: (d) K vs CD + boxplots, (e) Forest =====
        gs_de = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_main[0, 2],
                                                  hspace=0.18, height_ratios=[1, 1.2])

        # (d) K vs CD scatter + bottom boxplots
        gs_d_outer = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_de[0],
                                                       height_ratios=[4, 1], hspace=0.03)
        ax_d = fig.add_subplot(gs_d_outer[0])
        bs_cd = paired['CD_calc_BS'].values
        bs_kv = paired[f'{col_K}_BS'].values
        as_cd = paired['CD_calc_AS'].values
        as_kv = paired[f'{col_K}_AS'].values
        all_cd = np.concatenate([bs_cd, as_cd])
        all_kv = np.concatenate([bs_kv, as_kv])
        cd_lo, cd_hi = np.percentile(all_cd, [2, 98])
        kv_lo, kv_hi = np.percentile(all_kv, [2, 98])
        m_all = (all_cd >= cd_lo) & (all_cd <= cd_hi) & (all_kv >= kv_lo) & (all_kv <= kv_hi)
        m_bs = (bs_cd >= cd_lo) & (bs_cd <= cd_hi) & (bs_kv >= kv_lo) & (bs_kv <= kv_hi)
        m_as = (as_cd >= cd_lo) & (as_cd <= cd_hi) & (as_kv >= kv_lo) & (as_kv <= kv_hi)
        ax_d.scatter(bs_cd[m_bs], bs_kv[m_bs], s=3, c=c_bs, alpha=0.15, edgecolors='none', label='BS')
        ax_d.scatter(as_cd[m_as], as_kv[m_as], s=3, c=c_as, alpha=0.15, edgecolors='none', label='AS')
        coeffs = polyfit(all_cd[m_all], all_kv[m_all], 1)
        x_fit = np.linspace(cd_lo, cd_hi, 100)
        ax_d.plot(x_fit, coeffs[0] + coeffs[1] * x_fit, 'k--', linewidth=0.8, alpha=0.5)
        r_val, _ = pearsonr(all_cd[m_all], all_kv[m_all])
        ax_d.text(0.95, 0.05, f'R$^2$={r_val**2:.2f}', transform=ax_d.transAxes,
                  fontsize=6, ha='right', va='bottom', fontweight='bold', color='#555')
        ax_d.set_ylabel('K_ds (um$^{-2}$)', fontsize=7)
        ax_d.set_title('(d) K vs CD', fontsize=8)
        ax_d.set_xticklabels([])
        ax_d.legend(fontsize=5, loc='upper left', markerscale=3)
        ax_d.spines['top'].set_visible(False)
        ax_d.spines['right'].set_visible(False)

        ax_d_bot = fig.add_subplot(gs_d_outer[1], sharex=ax_d)
        n_bins_d = 10
        bed = np.linspace(cd_lo, cd_hi, n_bins_d + 1)
        bcd = (bed[:-1] + bed[1:]) / 2
        bw = bed[1] - bed[0]
        cd_c, kv_c = all_cd[m_all], all_kv[m_all]
        box_data, box_pos = [], []
        for i in range(n_bins_d):
            mb = (cd_c >= bed[i]) & (cd_c < bed[i+1])
            if mb.sum() > 3:
                box_data.append(kv_c[mb])
                box_pos.append(bcd[i])
        if box_data:
            bp = ax_d_bot.boxplot(box_data, positions=box_pos, widths=bw * 0.6,
                                   patch_artist=True, showfliers=False,
                                   medianprops=dict(color='#E65100', linewidth=1),
                                   whiskerprops=dict(color='#888', linewidth=0.6),
                                   capprops=dict(color='#888', linewidth=0.6))
            for patch in bp['boxes']:
                patch.set_facecolor('#FFE0B2')
                patch.set_edgecolor('#888')
                patch.set_linewidth(0.5)
                patch.set_alpha(0.8)
        ax_d_bot.set_xlabel('CD (x1000 cells/mm$^2$)', fontsize=6)
        ax_d_bot.set_ylabel('K range', fontsize=5)
        ax_d_bot.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1000:.1f}'))
        ax_d_bot.spines['top'].set_visible(False)
        ax_d_bot.spines['right'].set_visible(False)
        ax_d_bot.tick_params(axis='both', labelsize=4)
        ax_d_bot.text(0.03, 0.92, 'Same CD, different K', transform=ax_d_bot.transAxes,
                      fontsize=4, va='top', fontstyle='italic', color='#555')

        # (e) Forest plot
        ax_e = fig.add_subplot(gs_de[1])
        metrics_forest = [
            (col_K, '$K_{ds}$'), ('CD_calc', 'CD'), ('HEX_calc', 'HEX'),
            ('Ave_calc', 'Ave'), ('CV_calc', 'CV'), ('r_0_um', '$r_0$'),
        ]
        y_pos = np.array([3.2, 2.5, 2.0, 1.5, 1.0, 0.5])
        ax_e.axhspan(0.1, 2.8, color='#f0f0f0', alpha=0.5, zorder=0)
        ax_e.text(0.02, 0.62, 'Classical metrics', transform=ax_e.transAxes,
                  fontsize=5, color='#999', fontstyle='italic', va='top', ha='left')
        k_ds_pct_val = None
        for idx, (col, label) in enumerate(metrics_forest):
            bs_v = paired[f'{col}_BS'].values
            as_v = paired[f'{col}_AS'].values
            pct_ch = (as_v - bs_v) / bs_v * 100
            mean_p = np.mean(pct_ch)
            se = np.std(pct_ch) / np.sqrt(len(pct_ch))
            ci_l, ci_h = mean_p - 1.96 * se, mean_p + 1.96 * se
            _, p_t = ttest_rel(as_v, bs_v)
            sig = '***' if p_t < 0.001 else '**' if p_t < 0.01 else '*' if p_t < 0.05 else 'n.s.'
            y = y_pos[idx]
            clr = '#E65100' if mean_p > 0 else '#1565C0'
            ax_e.plot([ci_l, ci_h], [y, y], color=clr, linewidth=2 if idx == 0 else 1.5, solid_capstyle='round')
            ax_e.plot(mean_p, y, 'o', color=clr, markersize=6 if idx == 0 else 5,
                      markeredgecolor='white', markeredgewidth=0.5)
            ax_e.text(ci_h + 0.3, y, f'{mean_p:+.1f}% {sig}', va='center', fontsize=6,
                      fontweight='bold', color=clr)
            if idx == 0:
                k_ds_pct_val = abs(mean_p)
            elif k_ds_pct_val and abs(mean_p) > 0.01:
                ratio = k_ds_pct_val / abs(mean_p)
                if ratio > 1.5:
                    ax_e.text(mean_p, y - 0.3, f'{ratio:.1f}x', va='top', ha='center',
                              fontsize=4.5, color='#888', fontstyle='italic')
        ax_e.axvline(0, color='black', linewidth=0.8, linestyle='-')
        ax_e.set_yticks(y_pos)
        ax_e.set_yticklabels([m[1] for m in metrics_forest], fontsize=7, fontweight='bold')
        ax_e.set_ylim(0.0, 3.6)
        ax_e.set_xlabel('Change AS vs BS (%)', fontsize=7)
        ax_e.set_title('(e) Paired % change (95% CI)', fontsize=7, pad=-10)
        ax_e.spines['top'].set_visible(False)
        ax_e.spines['right'].set_visible(False)
        ax_e.spines['left'].set_visible(False)
        ax_e.tick_params(axis='y', length=0)

        # ===== Bottom row =====
        # (f) DK vs DCD
        ax_f = fig.add_subplot(gs_main[1, 0])
        dcd_c, dk_c, _ = _clip(dcd_pct, dk_pct, pct=2)
        _quad_scatter(ax_f, dcd_c, dk_c, 'DCD', 'DK', ('tl', 'br'))
        ax_f.set_title('(f) DK vs DCD', fontsize=8)
        ax_f.set_box_aspect(1)

        # (g) DK vs DHEX
        ax_g = fig.add_subplot(gs_main[1, 1])
        dhex_c, dk_e, _ = _clip(dhex_pct, dk_pct, pct=2)
        _quad_scatter(ax_g, dhex_c, dk_e, 'DHEX', 'DK', ('tr', 'bl'))
        ax_g.set_title('(g) DK vs DHEX', fontsize=8)
        ax_g.set_box_aspect(1)

        # (h) Homeostatic setpoint
        ax_h = fig.add_subplot(gs_main[1, 2])
        bs_kv_h = paired[f'{col_K}_BS'].values
        dk_pct_h = dk_pct.clip(-200, 500)
        hb2 = ax_h.hexbin(bs_kv_h, dk_pct_h, gridsize=20, cmap='YlOrRd', mincnt=1)
        if lowess is not None:
            si = np.argsort(bs_kv_h)
            lw_fit = lowess(dk_pct_h[si], bs_kv_h[si], frac=0.3)
            ax_h.plot(lw_fit[:, 0], lw_fit[:, 1], '-', color='#E65100', linewidth=2.5, label='LOWESS', zorder=3)
            crossings = np.where(np.diff(np.sign(lw_fit[:, 1])))[0]
            if len(crossings) > 0:
                sp = lw_fit[crossings[0], 0]
                ax_h.axvline(sp, color='#0072B2', linewidth=2.0, linestyle='--',
                             alpha=0.8, zorder=2, label=f'K* ≈ {sp:.3f}')
                ax_h.text(sp, ax_h.get_ylim()[1] * 0.85, f'K* = {sp:.3f}',
                          fontsize=7, fontweight='bold', color='#0072B2',
                          ha='left', va='top',
                          bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                                    alpha=0.8, edgecolor='none'))
        ax_h.axhline(0, color='black', linewidth=0.5, linestyle='--')
        ax_h.set_xlabel('Baseline K$_{ds}$ (µm$^{-2}$)', fontsize=8)
        ax_h.set_ylabel('$\\Delta$K (%)', fontsize=8)
        ax_h.set_title('(h) Homeostatic setpoint', fontsize=8)
        ax_h.legend(fontsize=5, loc='upper right', framealpha=0.8)
        plt.colorbar(hb2, ax=ax_h, shrink=0.7, label='Count')
        ax_h.spines['top'].set_visible(False)
        ax_h.spines['right'].set_visible(False)
        ax_h.set_box_aspect(1)

        if save:
            self._pub_save(fig, f'fig_comprehensive_{k_metric}')
        plt.show()

    # ==================================================================
    # COLLECTIVE ORDER FIGURE (Fig 4)
    # Row 1: (a) K vs CD, (b) DK vs DCD, (c) DK vs DHEX
    # Row 2: (d) g(r) stack, (e) Paired scatter, (f) Forest plot
    # Row 3: (g) Homeostatic setpoint, (h) Convergence arrows
    # ==================================================================

    def pub_collective_order(self, gr_data=None, save=None):
        """
        Publication Figure 4 — Collective order analysis.

        Parameters
        ----------
        gr_data : dict, optional
            {'r': array, 'bs_curves': 2D array, 'as_curves': 2D array, 'pixel_size': float}
            If None, auto-loaded from NPZ if available.
        """
        if gr_data is None:
            gr_data = self.gr_data
        save = save if save is not None else self.save
        self._pub_style()

        from scipy.stats import ttest_rel, spearmanr, pearsonr
        from numpy.polynomial.polynomial import polyfit
        from matplotlib.lines import Line2D

        paired = self.paired
        col_K = 'K_ds_um'
        C_BS, C_AS = '#4A90D9', '#E8833A'
        C_B1, C_B2 = '#882255', '#009E73'
        C_C1, C_C2 = '#332288', '#DDCC77'
        C_E1, C_E2 = '#CC3311', '#117733'

        fig_w = 190 / 25.4
        fig_h = 250 / 25.4
        fig = plt.figure(figsize=(fig_w, fig_h))

        gs_row1 = fig.add_gridspec(1, 3, left=0.09, right=0.97, top=0.97, bottom=0.82, wspace=0.35)
        gs_row2 = fig.add_gridspec(1, 3, left=0.09, right=0.97, top=0.74, bottom=0.40, wspace=0.35)
        gs_row3 = fig.add_gridspec(1, 2, width_ratios=[1.2, 1.2],
                                    left=0.09, right=0.97, top=0.32, bottom=0.03, wspace=0.12)

        def _clip_pct(x, y, pct=2):
            xlo, xhi = np.percentile(x, [pct, 100-pct])
            ylo, yhi = np.percentile(y, [pct, 100-pct])
            m = (x >= xlo) & (x <= xhi) & (y >= ylo) & (y <= yhi)
            return x[m], y[m], m

        def _quad_scatter(ax, x_pct, y_pct, x_label, y_label, highlight_pair, label, colors=None):
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
                ('tl', q_tl, 'I',  0.03, 0.97, 'left',  'top'),
                ('tr', q_tr, 'II', 0.97, 0.97, 'right', 'top'),
                ('bl', q_bl, 'III',0.03, 0.03, 'left',  'bottom'),
                ('br', q_br, 'IV', 0.97, 0.03, 'right', 'bottom'),
            ]:
                kd, xd = dir_map[key]
                pct = 100 * q.sum() / total
                ax.text(px, py, f'{num}. {kd} {x_s}{xd}\n{q.sum()} ({pct:.0f}%)',
                        transform=ax.transAxes, fontsize=7, ha=ha, va=va, color='black', fontweight='bold')
            rho, pval = spearmanr(x_pct, y_pct)
            ax.text(0.65, 1.05, f'\u03c1={rho:.2f} (p={pval:.0e})', fontsize=7, ha='center', va='bottom',
                    fontweight='bold', color='#333', transform=ax.transAxes,
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'), clip_on=False)
            ax.set_xlabel(f'{x_label} (%)')
            ax.set_ylabel(f'{y_label} (%)')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            self._pub_panel_label(ax, label)

        # ── Panel a: K vs CD ──
        gs_a = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_row1[0, 0], height_ratios=[4, 1], hspace=0.03)
        ax_a = fig.add_subplot(gs_a[0])
        ax_a_bot = fig.add_subplot(gs_a[1], sharex=ax_a)
        bs_cd, bs_kv = paired['CD_calc_BS'].values, paired[f'{col_K}_BS'].values
        as_cd, as_kv = paired['CD_calc_AS'].values, paired[f'{col_K}_AS'].values
        all_cd, all_kv = np.concatenate([bs_cd, as_cd]), np.concatenate([bs_kv, as_kv])
        cd_lo, cd_hi = np.percentile(all_cd, [2, 98])
        kv_lo, kv_hi = np.percentile(all_kv, [2, 98])
        m_bs = (bs_cd >= cd_lo) & (bs_cd <= cd_hi) & (bs_kv >= kv_lo) & (bs_kv <= kv_hi)
        m_as = (as_cd >= cd_lo) & (as_cd <= cd_hi) & (as_kv >= kv_lo) & (as_kv <= kv_hi)
        m_all = (all_cd >= cd_lo) & (all_cd <= cd_hi) & (all_kv >= kv_lo) & (all_kv <= kv_hi)
        ax_a.scatter(bs_cd[m_bs], bs_kv[m_bs], s=3, c=C_BS, alpha=0.15, edgecolors='none', label='BS')
        ax_a.scatter(as_cd[m_as], as_kv[m_as], s=3, c=C_AS, alpha=0.15, edgecolors='none', label='AS')
        coeffs = polyfit(all_cd[m_all], all_kv[m_all], 1)
        x_fit = np.linspace(cd_lo, cd_hi, 100)
        ax_a.plot(x_fit, coeffs[0] + coeffs[1] * x_fit, 'k--', linewidth=0.8, alpha=0.5)
        r_val, _ = pearsonr(all_cd[m_all], all_kv[m_all])
        ax_a.text(0.95, 0.05, f'R$^2$={r_val**2:.2f}', transform=ax_a.transAxes, fontsize=8, ha='right', va='bottom', fontweight='bold', color='#555')
        ax_a.set_ylabel('K$_{ds}$ (\u00b5m$^{-2}$)')
        ax_a.set_xticklabels([])
        ax_a.legend(fontsize=7, loc='upper left', markerscale=3)
        ax_a.spines['top'].set_visible(False); ax_a.spines['right'].set_visible(False)
        self._pub_panel_label(ax_a, 'a')
        cd_c, kv_c = all_cd[m_all], all_kv[m_all]
        n_bins = 10
        bed = np.linspace(cd_lo, cd_hi, n_bins + 1)
        bcd = (bed[:-1] + bed[1:]) / 2
        bw = bed[1] - bed[0]
        box_data, box_pos = [], []
        for i in range(n_bins):
            mb = (cd_c >= bed[i]) & (cd_c < bed[i+1])
            if mb.sum() > 3:
                box_data.append(kv_c[mb]); box_pos.append(bcd[i])
        if box_data:
            bp = ax_a_bot.boxplot(box_data, positions=box_pos, widths=bw * 0.6, patch_artist=True, showfliers=False,
                                  medianprops=dict(color='#E65100', linewidth=1), whiskerprops=dict(color='#888', linewidth=0.6),
                                  capprops=dict(color='#888', linewidth=0.6))
            for patch in bp['boxes']:
                patch.set_facecolor('#FFE0B2'); patch.set_edgecolor('#888'); patch.set_linewidth(0.5); patch.set_alpha(0.8)
        ax_a_bot.set_xlabel('CD (cells/mm$^2$)')
        ax_a_bot.set_ylabel('K range', fontsize=7)
        ax_a_bot.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1000:.1f}k'))
        ax_a_bot.tick_params(axis='x', rotation=45)
        plt.setp(ax_a_bot.get_xticklabels(), ha='right')
        ax_a_bot.spines['top'].set_visible(False); ax_a_bot.spines['right'].set_visible(False)
        ax_a_bot.tick_params(axis='both', labelsize=7)

        # ── Panel b: DK vs DCD ──
        ax_b = fig.add_subplot(gs_row1[0, 1])
        dk = paired[f'{col_K}_AS'].values - paired[f'{col_K}_BS'].values
        dcd = paired['CD_calc_AS'].values - paired['CD_calc_BS'].values
        dk_pct = dk / paired[f'{col_K}_BS'].values * 100
        dcd_pct = dcd / paired['CD_calc_BS'].values * 100
        dcd_c, dk_c, _ = _clip_pct(dcd_pct, dk_pct, pct=2)
        _quad_scatter(ax_b, dcd_c, dk_c, '\u0394CD', '\u0394K', ('tl', 'br'), 'b', colors=(C_B1, C_B2))
        ax_b.set_box_aspect(1)

        # ── Panel c: DK vs DHEX ──
        ax_c = fig.add_subplot(gs_row1[0, 2])
        dhex = paired['HEX_calc_AS'].values - paired['HEX_calc_BS'].values
        dhex_pct = dhex / paired['HEX_calc_BS'].values * 100
        dhex_c, dk_c2, _ = _clip_pct(dhex_pct, dk_pct, pct=2)
        _quad_scatter(ax_c, dhex_c, dk_c2, '\u0394HEX', '\u0394K', ('tr', 'bl'), 'c', colors=(C_C1, C_C2))
        ax_c.set_box_aspect(1)

        # ── Panel d: g(r) with zoomed inset ──
        ax_d = fig.add_subplot(gs_row2[0, 0])
        if gr_data is not None:
            from matplotlib.patches import Rectangle
            from scipy.ndimage import uniform_filter1d
            pixel_size = gr_data.get('pixel_size', 0.58)
            r = gr_data['r'] * pixel_size
            bs_curves, as_curves = gr_data['bs_curves'], gr_data['as_curves']
            bs_mean, as_mean = np.mean(bs_curves, axis=0), np.mean(as_curves, axis=0)
            bs_iqr_lo, bs_iqr_hi = np.percentile(bs_curves, 25, axis=0), np.percentile(bs_curves, 75, axis=0)
            as_iqr_lo, as_iqr_hi = np.percentile(as_curves, 25, axis=0), np.percentile(as_curves, 75, axis=0)
            r_start = 8
            r_mask = r >= r_start
            ax_d.fill_between(r[r_mask], bs_iqr_lo[r_mask], bs_iqr_hi[r_mask], color=C_BS, alpha=0.10)
            ax_d.fill_between(r[r_mask], as_iqr_lo[r_mask], as_iqr_hi[r_mask], color=C_AS, alpha=0.10)
            ax_d.plot(r[r_mask], bs_mean[r_mask], color=C_BS, linewidth=1.5, label=f'BS (n={len(bs_curves)})')
            ax_d.plot(r[r_mask], as_mean[r_mask], color=C_AS, linewidth=1.5, label=f'AS (n={len(as_curves)})')
            ax_d.set_xlim(r_start, r.max())
            ax_d.set_xlabel('r (\u00b5m)'); ax_d.set_ylabel('g(r)')
            ax_d.set_box_aspect(1); ax_d.legend(fontsize=7, loc='upper right')
            ax_d.spines['top'].set_visible(False); ax_d.spines['right'].set_visible(False)
            r_z1, r_z2 = 16, 21
            mask_zoom = (r >= r_z1) & (r <= r_z2)
            y_lo = min(bs_mean[mask_zoom].min(), as_mean[mask_zoom].min()) - 0.05
            y_hi = max(bs_mean[mask_zoom].max(), as_mean[mask_zoom].max()) + 0.05
            rect = Rectangle((r_z1, y_lo), r_z2 - r_z1, y_hi - y_lo, linewidth=0.8, edgecolor='#888',
                              facecolor='#f5f5f5', alpha=0.2, linestyle='--', zorder=0)
            ax_d.add_patch(rect)
            ax_inset = ax_d.inset_axes([0.22, 0.12, 0.62, 0.38])
            ax_inset.set_facecolor('#F5F5F0')
            bs_sm = uniform_filter1d(bs_mean, size=7)
            as_sm = uniform_filter1d(as_mean, size=7)
            dr = np.mean(np.diff(r))
            bs_d2 = np.gradient(np.gradient(bs_sm, dr), dr)
            as_d2 = np.gradient(np.gradient(as_sm, dr), dr)
            ax_inset.plot(r[mask_zoom], bs_d2[mask_zoom], color=C_BS, linewidth=1.5)
            ax_inset.plot(r[mask_zoom], as_d2[mask_zoom], color=C_AS, linewidth=1.5)
            ax_inset.axhline(0, color='black', linewidth=0.4, linestyle='--')
            bs_pi = np.argmin(bs_d2[mask_zoom]); as_pi = np.argmin(as_d2[mask_zoom])
            mi = (bs_pi + as_pi) // 2
            r_curv = r[mask_zoom]
            ax_inset.annotate('', xy=(r_curv[mi], as_d2[mask_zoom][mi]), xytext=(r_curv[mi], bs_d2[mask_zoom][mi]),
                              arrowprops=dict(arrowstyle='<->', color='#E65100', lw=1.2))
            ax_inset.text(r_curv[mi] + 1.0, (as_d2[mask_zoom][mi] + bs_d2[mask_zoom][mi]) / 2,
                          '\u0394K', fontsize=7, color='#E65100', fontweight='bold', va='center')
            ax_inset.set_xlim(r_z1, r_z2); ax_inset.set_ylim(None, -0.05)
            ax_inset.text(0.0, 1.05, "Curvature g''(r)", fontsize=6, fontweight='bold', color='#555',
                          transform=ax_inset.transAxes, ha='left', va='bottom')
            ax_inset.tick_params(axis='both', labelsize=6)
            ax_inset.spines['top'].set_visible(False); ax_inset.spines['right'].set_visible(False)
            for sp in ax_inset.spines.values(): sp.set_linewidth(0.8); sp.set_edgecolor('#999')
        else:
            ax_d.text(0.5, 0.5, 'g(r) data not provided', transform=ax_d.transAxes, ha='center', va='center', fontsize=9, color='#999')
            ax_d.spines['top'].set_visible(False); ax_d.spines['right'].set_visible(False)
        self._pub_panel_label(ax_d, 'd')

        # ── Panel e: Paired K scatter + improvement bars ──
        gs_e = gridspec.GridSpecFromSubplotSpec(3, 1, subplot_spec=gs_row2[0, 1], height_ratios=[2.5, 1, 1], hspace=0.03)
        ax_e = fig.add_subplot(gs_e[0])
        ax_e_pct = fig.add_subplot(gs_e[1], sharex=ax_e)
        ax_e_cnt = fig.add_subplot(gs_e[2], sharex=ax_e)
        bs_k, as_k = paired[f'{col_K}_BS'].values, paired[f'{col_K}_AS'].values
        bs_kc, as_kc, mask_kc = _clip_pct(bs_k, as_k, pct=2)
        dcd_p = paired['CD_calc_AS'].values - paired['CD_calc_BS'].values
        dcd_cl = dcd_p[mask_kc]
        cd_up = dcd_cl >= 0; cd_dn = dcd_cl < 0
        ax_e.scatter(bs_kc[cd_up], as_kc[cd_up], s=4, c=C_E2, alpha=0.20, edgecolors='none', label=f'CD+ ({cd_up.sum()})')
        ax_e.scatter(bs_kc[cd_dn], as_kc[cd_dn], s=4, c=C_E1, alpha=0.20, edgecolors='none', label=f'CD\u2212 ({cd_dn.sum()})')
        lim_k = max(bs_kc.max(), as_kc.max()) * 1.05
        ax_e.plot([0, lim_k], [0, lim_k], 'k--', linewidth=0.5, alpha=0.4)
        ax_e.set_ylabel('AS K$_{ds}$ (\u00b5m$^{-2}$)')
        ax_e.legend(fontsize=7, loc='upper left'); ax_e.set_xticklabels([])
        ax_e.spines['top'].set_visible(False); ax_e.spines['right'].set_visible(False)
        above = as_kc > bs_kc
        ax_e.text(0.95, 0.05, f'K+ : {above.sum()} ({100*above.mean():.0f}%)', transform=ax_e.transAxes,
                  fontsize=8, ha='right', va='bottom', color=C_E1, fontweight='bold')
        self._pub_panel_label(ax_e, 'e')
        n_bins_e = 15
        bin_edges_e = np.linspace(bs_kc.min(), bs_kc.max(), n_bins_e + 1)
        bin_centers_e = (bin_edges_e[:-1] + bin_edges_e[1:]) / 2
        bin_w_e = bin_edges_e[1] - bin_edges_e[0]
        dk_vals = as_kc - bs_kc
        frac_up, count_up, count_down = [], [], []
        for i in range(n_bins_e):
            mb = (bs_kc >= bin_edges_e[i]) & (bs_kc < bin_edges_e[i+1])
            n_tot = mb.sum(); n_up = (dk_vals[mb] > 0).sum() if n_tot > 0 else 0
            frac_up.append(100 * n_up / n_tot if n_tot > 0 else 50)
            count_up.append(n_up); count_down.append(n_tot - n_up)
        bar_cols = [C_E1 if f > 55 else (C_E2 if f < 45 else '#aaa') for f in frac_up]
        ax_e_pct.bar(bin_centers_e, frac_up, width=bin_w_e * 0.85, color=bar_cols, alpha=0.7, edgecolor='white', linewidth=0.3)
        ax_e_pct.axhline(50, color='black', linewidth=0.6, linestyle='--', alpha=0.5)
        ax_e_pct.set_ylabel('% impr.', fontsize=7); ax_e_pct.set_xlim(0, lim_k); ax_e_pct.set_ylim(0, 85)
        ax_e_pct.set_yticks([0, 50]); ax_e_pct.set_yticklabels(['0', '50'], fontsize=7); ax_e_pct.set_xticklabels([])
        ax_e_pct.spines['top'].set_visible(False); ax_e_pct.spines['right'].set_visible(False)
        ax_e_pct.tick_params(axis='both', labelsize=7)
        half_w = bin_w_e * 0.40
        ax_e_cnt.bar(np.array(bin_centers_e) - half_w/2, count_up, width=half_w, color=C_E1, alpha=0.7, edgecolor='white', linewidth=0.3, label='Improved')
        ax_e_cnt.bar(np.array(bin_centers_e) + half_w/2, count_down, width=half_w, color=C_E2, alpha=0.7, edgecolor='white', linewidth=0.3, label='Decreased')
        ax_e_cnt.set_xlabel('BS K$_{ds}$ (\u00b5m$^{-2}$)'); ax_e_cnt.set_ylabel('Count', fontsize=7)
        ax_e_cnt.set_xlim(0, lim_k); ax_e_cnt.legend(fontsize=6, loc='upper right', frameon=False)
        ax_e_cnt.spines['top'].set_visible(False); ax_e_cnt.spines['right'].set_visible(False)
        ax_e_cnt.tick_params(axis='both', labelsize=7)

        # ── Panel f: Forest plot ──
        ax_f = fig.add_subplot(gs_row2[0, 2])
        metrics_forest = [(col_K, 'K$_{ds}$'), ('CD_calc', 'CD'), ('HEX_calc', 'HEX'), ('Ave_calc', 'Ave'), ('CV_calc', 'CV')]
        for r0_col in ['r_0_um', 'r0_um', 'r0']:
            if f'{r0_col}_BS' in paired.columns:
                metrics_forest.append((r0_col, 'r$_0$')); break
        n_met = len(metrics_forest)
        y_pos = np.linspace(n_met * 0.5, 0.5, n_met)
        ax_f.axhspan(y_pos[0] - 0.25, y_pos[0] + 0.3, color='#FFF3E0', alpha=0.8, zorder=0)
        if n_met > 1:
            ax_f.axhspan(y_pos[-1] - 0.3, y_pos[1] + 0.3, color='#f5f5f5', alpha=0.5, zorder=0)
        k_ds_pct_val = None; valid_labels = []; valid_ypos = []
        for idx, (col, label) in enumerate(metrics_forest):
            bs_col, as_col = f'{col}_BS', f'{col}_AS'
            if bs_col not in paired.columns or as_col not in paired.columns: continue
            bs_v, as_v = paired[bs_col].values, paired[as_col].values
            pct_ch = (as_v - bs_v) / bs_v * 100
            mean_p = np.nanmean(pct_ch)
            se = np.nanstd(pct_ch) / np.sqrt(np.sum(np.isfinite(pct_ch)))
            ci_l, ci_h = mean_p - 1.96 * se, mean_p + 1.96 * se
            fin = np.isfinite(pct_ch)
            _, p_t = ttest_rel(as_v[fin], bs_v[fin])
            sig = '***' if p_t < 0.001 else '**' if p_t < 0.01 else '*' if p_t < 0.05 else 'n.s.'
            y = y_pos[idx]; clr = '#E65100' if mean_p > 0 else '#1565C0'
            is_kds = (idx == 0); valid_labels.append(label); valid_ypos.append(y)
            ax_f.plot([ci_l, ci_h], [y, y], color=clr, linewidth=3 if is_kds else 1.5, solid_capstyle='round')
            ax_f.plot(mean_p, y, 'D' if is_kds else 'o', color=clr, markersize=8 if is_kds else 5,
                      markeredgecolor='white', markeredgewidth=0.8)
            if is_kds:
                ax_f.text(mean_p, y + 0.15, f'{mean_p:+.1f}% {sig}', va='bottom', ha='center', fontsize=9, fontweight='bold', color=clr)
            else:
                ax_f.text(ci_h + 0.3, y, f'{mean_p:+.1f}% {sig}', va='center', fontsize=8, fontweight='bold', color=clr)
            if idx == 0: k_ds_pct_val = abs(mean_p)
            elif k_ds_pct_val and abs(mean_p) > 0.01:
                ratio = k_ds_pct_val / abs(mean_p)
                if ratio > 1.5:
                    ax_f.text(ci_h + 0.3, y - 0.22, f'{ratio:.1f}\u00d7', va='top', ha='left', fontsize=8, color='#555', fontweight='bold')
        ax_f.axvline(0, color='black', linewidth=0.8, linestyle='-')
        ax_f.set_yticks(valid_ypos); ax_f.set_yticklabels(valid_labels, fontsize=9, fontweight='bold')
        ax_f.set_ylim(min(valid_ypos) - 0.4, max(valid_ypos) + 0.4)
        ax_f.set_xlabel('Change AS vs BS (%)', fontsize=8); ax_f.set_ylabel('')
        ax_f.spines['top'].set_visible(False); ax_f.spines['right'].set_visible(False)
        ax_f.spines['left'].set_visible(False); ax_f.tick_params(axis='y', length=0)
        self._pub_panel_label(ax_f, 'f')

        # ── Panel g: Homeostatic setpoint ──
        ax_g = fig.add_subplot(gs_row3[0, 0])
        dk_g = paired[f'{col_K}_AS'].values - paired[f'{col_K}_BS'].values
        dk_pct_g = np.clip(dk_g / paired[f'{col_K}_BS'].values * 100, -200, 500)
        bs_kv_g = paired[f'{col_K}_BS'].values
        hb = ax_g.hexbin(bs_kv_g, dk_pct_g, gridsize=20, cmap='Greys', mincnt=1, zorder=1)
        plt.colorbar(hb, ax=ax_g, shrink=0.6, label='Count', pad=0.02)
        K_star = None
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess
            si = np.argsort(bs_kv_g)
            lw_fit = lowess(dk_pct_g[si], bs_kv_g[si], frac=0.3)
            ax_g.plot(lw_fit[:, 0], lw_fit[:, 1], '-', color='#E65100', linewidth=3.5, label='LOWESS', zorder=3)
            crossings = np.where(np.diff(np.sign(lw_fit[:, 1])))[0]
            if len(crossings) > 0:
                K_star = lw_fit[crossings[0], 0]
                ax_g.axvline(K_star, color='#0072B2', linewidth=2.5, linestyle='--', alpha=0.8, zorder=2, label=f'K* \u2248 {K_star:.3f}')
                ax_g.text(K_star, ax_g.get_ylim()[1] * 0.85, f'K* = {K_star:.3f}', fontsize=7, fontweight='bold', color='#0072B2',
                          ha='left', va='top', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))
        except ImportError:
            pass
        ax_g.axhline(0, color='black', linewidth=0.5, linestyle='--', zorder=1)
        ax_g.set_xlabel('Baseline K$_{ds}$ (\u00b5m$^{-2}$)'); ax_g.set_ylabel('\u0394K$_{ds}$ (%)')
        ax_g.legend(fontsize=7, loc='upper right', framealpha=0.8)
        ax_g.spines['top'].set_visible(False); ax_g.spines['right'].set_visible(False)
        self._pub_panel_label(ax_g, 'g')

        # ── Panel h: Convergence arrows ──
        gs_h = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_row3[0, 1], width_ratios=[1, 3], wspace=0.02)
        ax_h_hist = fig.add_subplot(gs_h[0])
        ax_h = fig.add_subplot(gs_h[1], sharey=ax_h_hist)
        if K_star is not None:
            as_kv_h = paired[f'{col_K}_AS'].values
            n_bins_h = 25
            p2, p98 = np.percentile(bs_kv_g, [2, 98])
            bin_edges_h = np.linspace(p2, p98, n_bins_h + 1)
            bin_counts_h = []
            for i in range(n_bins_h):
                mask = (bs_kv_g >= bin_edges_h[i]) & (bs_kv_g < bin_edges_h[i+1])
                count = mask.sum(); bin_counts_h.append(count)
                if count < 3: continue
                mean_bs = np.mean(bs_kv_g[mask]); mean_as = np.mean(as_kv_h[mask])
                toward = (mean_bs < K_star and mean_as > mean_bs) or (mean_bs > K_star and mean_as < mean_bs)
                color = C_AS if toward else '#bbb'
                alpha = 0.8 if toward else 0.4
                ax_h.annotate('', xy=(mean_as, i), xytext=(mean_bs, i),
                              arrowprops=dict(arrowstyle='->', color=color, lw=1.8 if toward else 1.0, alpha=alpha))
                ax_h.plot(mean_bs, i, 'o', color=C_BS, markersize=4, markeredgecolor='white', markeredgewidth=0.3, zorder=4)
                ax_h.plot(mean_as, i, 'o', color=color, markersize=4, markeredgecolor='white', markeredgewidth=0.3, zorder=4)
            ax_h.axvline(K_star, color='#0072B2', linewidth=2.5, linestyle='--', alpha=0.7, zorder=1)
            ax_h.text(K_star + 0.002, n_bins_h + 0.5, f'K* = {K_star:.3f}', fontsize=8, fontweight='bold', color='#0072B2', ha='left', va='bottom')
            kstar_bin = (K_star - p2) / (p98 - p2) * n_bins_h
            ax_h.axhline(kstar_bin, color='#0072B2', linewidth=1.0, linestyle=':', alpha=0.5)
            ax_h_hist.axhline(kstar_bin, color='#0072B2', linewidth=1.0, linestyle=':', alpha=0.5)
            ax_h.set_xlabel('K$_{ds}$ (\u00b5m$^{-2}$)')
            ax_h.set_ylim(-1, n_bins_h + 1); ax_h.set_yticks([])
            ax_h.spines['top'].set_visible(False); ax_h.spines['right'].set_visible(False); ax_h.spines['left'].set_visible(False)
            legend_h = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor=C_BS, markersize=4, markeredgecolor='white', label='BS', linewidth=0),
                Line2D([0], [0], marker='o', color='w', markerfacecolor=C_AS, markersize=4, markeredgecolor='white', label='AS', linewidth=0),
                Line2D([0], [0], marker='>', color=C_AS, markersize=5, label='Toward K*', linewidth=0),
                Line2D([0], [0], marker='>', color='#bbb', markersize=5, label='Away from K*', linewidth=0),
            ]
            ax_h.legend(handles=legend_h, fontsize=7, loc='lower right', framealpha=0.8)
            y_positions = np.arange(n_bins_h)
            bar_colors = [C_BS if c >= 3 else '#ddd' for c in bin_counts_h]
            ax_h_hist.barh(y_positions, bin_counts_h, height=0.8, color=bar_colors, alpha=0.5, edgecolor='white', linewidth=0.3)
            ax_h_hist.set_xlim(max(bin_counts_h) * 1.1, 0)
            ax_h_hist.set_xlabel('n', fontsize=8); ax_h_hist.set_yticks([])
            ax_h_hist.spines['top'].set_visible(False); ax_h_hist.spines['right'].set_visible(False); ax_h_hist.spines['left'].set_visible(False)
            ax_h_hist.tick_params(axis='x', labelsize=7)
        else:
            ax_h.text(0.5, 0.5, 'K* not found', transform=ax_h.transAxes, ha='center', va='center', fontsize=10, color='#ccc')
        self._pub_panel_label(ax_h, 'h')

        plt.tight_layout()
        if save:
            self._pub_save(fig, 'fig4_collective_order')
        plt.show()

    # ==================================================================
    # REPRESENTATIVE DONORS: Voronoi + g(r) (merged Fig 3+4)
    # ==================================================================

    @staticmethod
    def _compute_voronoi(results):
        """Compute Voronoi polygons, NN distances, and coordination numbers."""
        try:
            from shapely.geometry import Polygon as ShapelyPolygon, box as shapely_box
        except ImportError:
            raise ImportError("shapely is required for pub_representative: pip install shapely")

        centroids = np.array([o.centroid for o in results['objects']])
        y_c, x_c = centroids[:, 0], centroids[:, 1]
        points = np.column_stack([x_c, y_c])
        H, W = results['segmentor'].H, results['segmentor'].W

        margin_pts = []
        for p in points:
            if p[0] < W * 0.15: margin_pts.append([-p[0], p[1]])
            if p[0] > W * 0.85: margin_pts.append([2 * W - p[0], p[1]])
            if p[1] < H * 0.15: margin_pts.append([p[0], -p[1]])
            if p[1] > H * 0.85: margin_pts.append([p[0], 2 * H - p[1]])
        all_pts = np.vstack([points, np.array(margin_pts)]) if margin_pts else points
        n_real = len(points)
        vor = Voronoi(all_pts)

        neighbors = defaultdict(set)
        for (i, j) in vor.ridge_points:
            if i < n_real: neighbors[i].add(j)
            if j < n_real: neighbors[j].add(i)

        nn_dist = np.full(n_real, np.nan)
        n_neighbors = np.zeros(n_real, dtype=int)
        for i in range(n_real):
            nbrs = list(neighbors[i])
            n_neighbors[i] = len(nbrs)
            if nbrs:
                dists = np.sqrt((all_pts[nbrs, 0] - points[i, 0]) ** 2 +
                                (all_pts[nbrs, 1] - points[i, 1]) ** 2)
                nn_dist[i] = np.min(dists)

        bounding = shapely_box(0, 0, W, H)
        polygons = []
        for i in range(n_real):
            region_idx = vor.point_region[i]
            region = vor.regions[region_idx]
            if -1 in region or len(region) == 0:
                polygons.append(None); continue
            try:
                poly = ShapelyPolygon(vor.vertices[region]).intersection(bounding)
                polygons.append(poly if not poly.is_empty and poly.area > 1 else None)
            except:
                polygons.append(None)

        return {
            'points': points, 'nn_dist': nn_dist, 'n_neighbors': n_neighbors,
            'polygons': polygons, 'H': H, 'W': W, 'n_real': n_real,
        }

    @staticmethod
    def _draw_nn_panel(ax, met, cmap, norm):
        H, W = met['H'], met['W']
        ax.set_xlim(0, W); ax.set_ylim(H, 0)
        ax.set_facecolor('#222222')
        for i, poly in enumerate(met['polygons']):
            if poly is None: continue
            geoms = [poly] if poly.geom_type == 'Polygon' else list(poly.geoms)
            for g in geoms:
                coords = np.array(g.exterior.coords)
                fc = cmap(norm(met['nn_dist'][i])) if not np.isnan(met['nn_dist'][i]) else '#333'
                ax.add_patch(plt.Polygon(coords, closed=True, facecolor=fc,
                                         edgecolor='black', linewidth=0.15, alpha=0.85))
        ax.axis('off')

    @staticmethod
    def _draw_coord_panel(ax, met):
        H, W = met['H'], met['W']
        ax.set_xlim(0, W); ax.set_ylim(H, 0)
        ax.set_facecolor('#222222')
        coord_colors = {3: '#999', 4: '#999', 5: '#E74C3C', 6: '#27AE60',
                        7: '#2980B9', 8: '#999', 9: '#999'}
        for i, poly in enumerate(met['polygons']):
            if poly is None: continue
            color = coord_colors.get(met['n_neighbors'][i], '#999')
            geoms = [poly] if poly.geom_type == 'Polygon' else list(poly.geoms)
            for g in geoms:
                coords = np.array(g.exterior.coords)
                ax.add_patch(plt.Polygon(coords, closed=True, facecolor=color,
                                         edgecolor='black', linewidth=0.15, alpha=0.8))
        ax.axis('off')

    def pub_representative(self, image_folder, pixel_size=0.58, save=None):
        """Publication-ready 4×5: NN(BS,AS) + Coord(BS,AS) + g(r) for 4 representative donors.

        Auto-selects: large increase, modest increase, near-zero, decrease.
        Requires running Cornealia on 8 individual images.

        Parameters
        ----------
        image_folder : str
            Path to the original CellChek-D images.
        pixel_size : float
            μm/pixel calibration.
        """
        from cornealia.cornealia import cornealia as Cornealia

        self._pub_style()
        save = save if save is not None else self.save

        processor = Cornealia(is_input_image_machine_output=False,
                              pixel_size=pixel_size, verbose=False)

        # --- Select donors: 95th, 65th, 45th, 10th percentile of ΔK% ---
        paired = self.paired.copy()
        col_as, col_bs = 'K_ds_um_AS', 'K_ds_um_BS'
        paired = paired[(paired[col_bs] > 0.005) & (paired[col_as] > 0.005)].copy()
        paired['pct_change'] = (paired[col_as] - paired[col_bs]) / paired[col_bs] * 100
        paired_sorted = paired.sort_values('pct_change').reset_index(drop=True)
        nr = len(paired_sorted)

        targets = [
            ('Large increase', 0.95),
            ('Modest increase', 0.65),
            ('Near zero', 0.45),
            ('Decrease', 0.10),
        ]
        donors = []
        for label, q in targets:
            row = paired_sorted.iloc[int(nr * q)]
            donors.append({'label': label, 'row': row})

        print("\nSelected representative donors:")
        for d in donors:
            r = d['row']
            print(f"  {d['label']:18s}  {r['patient_id']:15s}  "
                  f"K: {r[col_bs]:.4f} → {r[col_as]:.4f}  ({r['pct_change']:+.1f}%)")

        # --- Process images ---
        all_nn = []
        donor_data = []

        for d in donors:
            r = d['row']
            pid = r['patient_id']
            bs_name = r['Image_Name_BS']
            as_name = r['Image_Name_AS']

            bs_path = self._find_image(image_folder, bs_name)
            as_path = self._find_image(image_folder, as_name)
            if bs_path is None or as_path is None:
                print(f"  WARNING: images not found for {pid}"); continue

            print(f"  Processing {pid}...")
            res_bs = processor.collective_order(bs_path)
            res_as = processor.collective_order(as_path)
            met_bs = self._compute_voronoi(res_bs)
            met_as = self._compute_voronoi(res_as)

            all_nn.extend(met_bs['nn_dist'][~np.isnan(met_bs['nn_dist'])])
            all_nn.extend(met_as['nn_dist'][~np.isnan(met_as['nn_dist'])])

            donor_data.append({
                'pid': pid, 'label': d['label'], 'pct': r['pct_change'],
                'K_bs': res_bs.get('K_ds', res_bs['K']),
                'K_as': res_as.get('K_ds', res_as['K']),
                'res_bs': res_bs, 'res_as': res_as,
                'met_bs': met_bs, 'met_as': met_as,
            })

        all_nn = np.array(all_nn)
        cmap_nn = plt.cm.viridis
        norm_nn = Normalize(vmin=np.percentile(all_nn, 5), vmax=np.percentile(all_nn, 95))

        n = len(donor_data)

        # --- Layout: [NN pair | Coord pair | g(r)] ---
        fig_w = 190 / 25.4
        img_aspect = 514 / 684
        panel_w = fig_w / 5.5
        row_h = panel_w * img_aspect
        fig_h = row_h * n + 0.4

        fig = plt.figure(figsize=(fig_w, fig_h))
        outer = gridspec.GridSpec(1, 3, figure=fig,
                                  width_ratios=[2, 2, 1.4], wspace=0.18,
                                  left=0.12, right=0.98, top=0.94, bottom=0.08)
        gs_nn  = gridspec.GridSpecFromSubplotSpec(n, 2, subplot_spec=outer[0, 0],
                                                   wspace=0.01, hspace=0.12)
        gs_hex = gridspec.GridSpecFromSubplotSpec(n, 2, subplot_spec=outer[0, 1],
                                                   wspace=0.01, hspace=0.12)
        gs_gr  = gridspec.GridSpecFromSubplotSpec(n, 1, subplot_spec=outer[0, 2],
                                                   hspace=0.12)

        fig.text(0.30, 0.96, 'Nearest-Neighbor Distance', ha='center',
                 fontsize=8, fontweight='bold')
        fig.text(0.64, 0.96, 'Coordination Number', ha='center',
                 fontsize=8, fontweight='bold')
        fig.text(0.90, 0.96, '$g(r)$', ha='center',
                 fontsize=8, fontweight='bold')

        for i, dd in enumerate(donor_data):
            hex_bs = (dd['met_bs']['n_neighbors'] == 6).sum() / dd['met_bs']['n_real'] * 100
            hex_as = (dd['met_as']['n_neighbors'] == 6).sum() / dd['met_as']['n_real'] * 100
            K_bs_um = dd['K_bs'] / (pixel_size ** 2)
            K_as_um = dd['K_as'] / (pixel_size ** 2)
            pct = dd['pct']

            # NN BS
            ax = fig.add_subplot(gs_nn[i, 0])
            self._draw_nn_panel(ax, dd['met_bs'], cmap_nn, norm_nn)
            ax.set_title('BS' if i == 0 else '', fontsize=6, fontweight='bold', pad=1)
            ax.text(-0.08, 0.5, f"{dd['label']}\n$\\Delta K$={pct:+.0f}%",
                    transform=ax.transAxes, fontsize=5.5, fontweight='bold',
                    va='center', ha='right', rotation=90)

            # NN AS
            ax = fig.add_subplot(gs_nn[i, 1])
            self._draw_nn_panel(ax, dd['met_as'], cmap_nn, norm_nn)
            ax.set_title('AS' if i == 0 else '', fontsize=6, fontweight='bold', pad=1)

            # Coord BS
            ax = fig.add_subplot(gs_hex[i, 0])
            self._draw_coord_panel(ax, dd['met_bs'])
            ax.set_title(f'BS HEX={hex_bs:.0f}%' if i == 0 else f'HEX={hex_bs:.0f}%',
                          fontsize=5.5, fontweight='bold', pad=1)

            # Coord AS
            ax = fig.add_subplot(gs_hex[i, 1])
            self._draw_coord_panel(ax, dd['met_as'])
            ax.set_title(f'AS HEX={hex_as:.0f}%' if i == 0 else f'HEX={hex_as:.0f}%',
                          fontsize=5.5, fontweight='bold', pad=1)

            # g(r)
            ax = fig.add_subplot(gs_gr[i, 0])
            zoom = 80
            r_bs = dd['res_bs']['r_values']
            r_as = dd['res_as']['r_values']
            mask_bs, mask_as = r_bs <= zoom, r_as <= zoom


            ax.plot(r_bs[mask_bs] * pixel_size, dd['res_bs']['g_r'][mask_bs],
                    '.', color=COLORS['BS'], markersize=3, alpha=0.4, label='BS')
            ax.plot(r_as[mask_as] * pixel_size, dd['res_as']['g_r'][mask_as],
                    '.', color=COLORS['AS'], markersize=3, alpha=0.4, label='AS')

            # Overlay damped sine fits as smooth curves
            for res, clr in [(dd['res_bs'], COLORS['BS']), (dd['res_as'], COLORS['AS'])]:
                A = res.get('A_damped', np.nan)
                xi = res.get('xi_damped', np.nan)
                lam = res.get('lambda_damped', np.nan)
                r0_ds = res.get('r0_fit', 30.0)
                if not np.isnan(A) and not np.isnan(xi) and not np.isnan(lam):
                    r_excl = res.get('r_excl_damped', 15.0)
                    phi = res.get('phi_damped', 0.0)
                    r_dense = np.linspace(res['r_values'][0], zoom, 300)
                    H = 1.0 / (1.0 + np.exp(-(r_dense - r_excl) / 0.3))
                    t = np.maximum(r_dense - r_excl, 0.0)
                    osc = -A * np.exp(-t / xi) * np.sin(2 * np.pi * t / lam + phi)
                    g_fit = 1.0 + H * osc + (1.0 - H) * (-1.0)
                    ax.plot(r_dense * pixel_size, g_fit, '-', color=clr, lw=1.5, alpha=0.9)

            ax.axhline(1, color='gray', ls='--', lw=0.8, alpha=0.5)

            ax.text(0.97, 0.95,
                    f"$K_{{ds,BS}}$={K_bs_um:.3f}\n$K_{{ds,AS}}$={K_as_um:.3f}\n$\\Delta$={pct:+.0f}%",
                    transform=ax.transAxes, fontsize=5, fontweight='bold',
                    va='top', ha='right',
                    bbox=dict(facecolor='white', edgecolor='black',
                              alpha=0.9, pad=1.5, boxstyle='round,pad=0.2'))

            ax.set_xlim(0, zoom * pixel_size)
            y_max = max(dd['res_bs']['g_r'][mask_bs].max(),
                        dd['res_as']['g_r'][mask_as].max())
            ax.set_ylim(0, y_max * 1.15)
            ax.set_ylabel('', fontsize=7, fontweight='bold')
            if i == n - 1:
                ax.set_xlabel('$r$ ($\\mu$m)', fontsize=7, fontweight='bold')
            else:
                ax.set_xticklabels([])
            ax.tick_params(axis='both', labelsize=6)
            if i == 0:
                ax.legend(fontsize=5.5, loc='upper left', framealpha=0.9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        # NN colorbar — aligned under NN columns
        cb_ax = fig.add_axes([0.12, 0.02, 0.28, 0.012])
        sm = ScalarMappable(cmap=cmap_nn, norm=norm_nn)
        sm.set_array([])
        cb = plt.colorbar(sm, cax=cb_ax, orientation='horizontal')
        cb.set_label('NN Distance (px)', fontsize=6, fontweight='bold')
        cb.ax.tick_params(labelsize=5)

        # Coordination legend — bottom left, next to colorbar
        legend_patches = [
            mpatches.Patch(color='#27AE60', label='6 (hex)'),
            mpatches.Patch(color='#E74C3C', label='5'),
            mpatches.Patch(color='#2980B9', label='7'),
            mpatches.Patch(color='#999', label='Other'),
        ]
        fig.legend(handles=legend_patches, loc='lower left',
                   bbox_to_anchor=(0.45, 0.005), fontsize=5.5, ncol=4,
                   frameon=True, fancybox=True, framealpha=0.9,
                   edgecolor='black', title='Neighbors', title_fontsize=6)

        if save:
            self._pub_save(fig, 'fig_representative')
        plt.show()

    @staticmethod
    def _find_image(folder, name):
        folder = Path(folder)
        for ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            m = list(folder.rglob(f"{name}{ext}"))
            if m: return str(m[0])
            m = list(folder.rglob(f"*{name}*{ext}"))
            if m: return str(m[0])
        return None

    # ==================================================================
    # SPATIAL ORDER: NN-deviation Voronoi maps (Figure 5)
    # ==================================================================

    @staticmethod
    def _compute_voronoi_deviation(results, pixel_size):
        """Compute per-cell |NN_dist - r0| / r0 and clipped Voronoi polygons."""
        from scipy.spatial import Voronoi, cKDTree
        from matplotlib.patches import Polygon as MplPolygon

        centroids = np.array([o.centroid for o in results['objects']])
        y_c, x_c = centroids[:, 0], centroids[:, 1]
        points = np.column_stack([x_c, y_c])
        H, W = results['segmentor'].labels.shape

        # NN distances
        tree = cKDTree(points)
        dd, _ = tree.query(points, k=2)
        nn_dist = dd[:, 1] * pixel_size

        # r0 from the fit
        r0 = results.get('r0_px', 30) * pixel_size

        # Deviation: |NN - r0| / r0
        deviation = np.abs(nn_dist - r0) / r0

        # Voronoi polygons
        vor = Voronoi(points)
        polygons = []
        valid_idx = []
        for i, region_idx in enumerate(vor.point_region):
            region = vor.regions[region_idx]
            if -1 in region or len(region) == 0:
                continue
            verts = vor.vertices[region]
            if np.any(verts < -10) or np.any(verts[:, 0] > W + 10) or np.any(verts[:, 1] > H + 10):
                continue
            verts = np.clip(verts, 0, [W, H])
            polygons.append(verts)
            valid_idx.append(i)

        return {
            'polygons': polygons,
            'deviation': deviation[valid_idx],
            'nn_dist': nn_dist[valid_idx],
            'r0': r0,
            'shape': (H, W),
        }

    def pub_spatial_order(self, image_folder, pixel_size=0.58, save=None):
        """Publication-ready Figure 5: NN-deviation Voronoi maps for 4 donors.

        Each Voronoi cell is colored by |NN_distance - r0| / r0:
          - Blue  = cell at equilibrium spacing (ordered)
          - Red   = cell far from equilibrium (disordered)

        Layout: 4 rows × 2 columns (BS | AS), shared horizontal colorbar.
        """
        from cornealia.cornealia import cornealia as Cornealia
        from matplotlib.collections import PatchCollection
        from matplotlib.patches import Polygon as MplPolygon
        from matplotlib.colors import Normalize

        self._pub_style()
        save = save if save is not None else self.save

        processor = Cornealia(is_input_image_machine_output=False,
                              pixel_size=pixel_size, verbose=False)

        # --- Select 4 donors spanning the response spectrum ---
        paired = self.paired.copy()
        col_as, col_bs = 'K_ds_um_AS', 'K_ds_um_BS'
        paired = paired[(paired[col_bs] > 0.005) & (paired[col_as] > 0.005)].copy()
        paired['pct_change'] = (paired[col_as] - paired[col_bs]) / paired[col_bs] * 100
        paired_sorted = paired.sort_values('pct_change').reset_index(drop=True)
        nr = len(paired_sorted)

        targets = [
            ('Large increase', 0.95),
            ('Modest increase', 0.65),
            ('Near zero', 0.45),
            ('Decrease', 0.10),
        ]
        donors = []
        for label, q in targets:
            row = paired_sorted.iloc[int(nr * q)]
            donors.append({'label': label, 'row': row})

        print("\nSelected donors for spatial order:")
        for d in donors:
            r = d['row']
            print(f"  {d['label']:18s}  {r['patient_id']:15s}  "
                  f"ΔK={r['pct_change']:+.1f}%")

        # --- Process all donors ---
        donor_data = []
        all_devs = []

        for d in donors:
            r = d['row']
            pid = r['patient_id']
            bs_path = self._find_image(image_folder, r['Image_Name_BS'])
            as_path = self._find_image(image_folder, r['Image_Name_AS'])
            if bs_path is None or as_path is None:
                print(f"  WARNING: images not found for {pid}")
                continue

            print(f"  Processing {pid}...")
            res_bs = processor.collective_order(bs_path)
            res_as = processor.collective_order(as_path)

            met_bs = self._compute_voronoi_deviation(res_bs, pixel_size)
            met_as = self._compute_voronoi_deviation(res_as, pixel_size)

            K_bs = res_bs.get('K_ds', 0) / (pixel_size ** 2)
            K_as = res_as.get('K_ds', 0) / (pixel_size ** 2)

            all_devs.extend(met_bs['deviation'])
            all_devs.extend(met_as['deviation'])

            donor_data.append({
                'label': d['label'],
                'pct': r['pct_change'],
                'met_bs': met_bs, 'met_as': met_as,
                'K_bs': K_bs, 'K_as': K_as,
                'res_bs': res_bs, 'res_as': res_as,
            })

        if not donor_data:
            print("  ERROR: no donors processed.")
            return

        # --- Figure: 4 rows × 3 cols (BS | AS | g(r)) ---
        all_devs = np.array(all_devs)
        vmin, vmax = 0, np.percentile(all_devs, 95)
        cmap = plt.cm.RdYlBu_r
        norm = Normalize(vmin=vmin, vmax=vmax)

        n = len(donor_data)
        fig_w = 190 / 25.4
        fig_h = fig_w * 1.0
        fig = plt.figure(figsize=(fig_w, fig_h))
        import matplotlib.gridspec as gridspec
        gs = gridspec.GridSpec(n, 3, figure=fig, width_ratios=[1, 1, 0.9],
                               hspace=0.03, wspace=0.08,
                               left=0.12, right=0.97, top=0.95, bottom=0.06)

        for row, dd in enumerate(donor_data):
            # --- Voronoi panels (cols 0, 1) ---
            for col, side in enumerate(['bs', 'as']):
                ax = fig.add_subplot(gs[row, col])
                met = dd[f'met_{side}']
                polys = met['polygons']
                devs = met['deviation']
                shape = met['shape']

                patches = [MplPolygon(p, closed=True) for p in polys]
                pc = PatchCollection(patches, cmap=cmap, norm=norm,
                                     edgecolors='black', linewidths=0.3, alpha=0.85)
                pc.set_array(devs)
                ax.add_collection(pc)
                ax.set_xlim(0, shape[1])
                ax.set_ylim(shape[0], 0)
                ax.set_aspect('equal')
                ax.axis('off')

                side_label = 'BS' if side == 'bs' else 'AS'
                K_val = dd[f'K_{side}']
                mean_dev = np.mean(devs)
                ax.set_title(f'{side_label}  K={K_val:.3f}  dev={mean_dev:.2f}',
                             fontsize=7, fontweight='bold', pad=2)

                if col == 0:
                    ax.text(-0.02, 0.5, f"{dd['label']}\n$\\Delta$K={dd['pct']:+.0f}%",
                            transform=ax.transAxes, fontsize=7, fontweight='bold',
                            ha='right', va='center', rotation=90)

            # --- g(r) panel (col 2) ---
            ax_gr = fig.add_subplot(gs[row, 2])
            res_bs_d = dd['res_bs']
            res_as_d = dd['res_as']

            r_bs = np.array(res_bs_d.get('r', res_bs_d.get('r_values', []))) * pixel_size
            g_bs = np.array(res_bs_d.get('g_r', res_bs_d.get('g_r_values', [])))
            r_as = np.array(res_as_d.get('r', res_as_d.get('r_values', []))) * pixel_size
            g_as = np.array(res_as_d.get('g_r', res_as_d.get('g_r_values', [])))

            if len(r_bs) > 0 and len(g_bs) > 0:
                ax_gr.scatter(r_bs, g_bs, s=3, c=COLORS['BS'], alpha=0.3, edgecolors='none')
            if len(r_as) > 0 and len(g_as) > 0:
                ax_gr.scatter(r_as, g_as, s=3, c=COLORS['AS'], alpha=0.3, edgecolors='none')

            # DS fit overlay
            def _step_response(r, A, xi, lam, r_excl, phi):
                H = 1.0 / (1.0 + np.exp(-(r - r_excl) / 0.3))
                t = np.maximum(r - r_excl, 0.0)
                return -A * np.exp(-t / xi) * np.sin(2 * np.pi * t / lam + phi)

            for res_d, color, lbl in [(res_bs_d, COLORS['BS'], 'BS'),
                                       (res_as_d, COLORS['AS'], 'AS')]:
                popt = res_d.get('popt_qc', None)
                if popt is not None:
                    r_fit = np.linspace(1, max(len(r_bs), len(r_as)), 500)
                    g_fit = 1.0 + _step_response(r_fit, *popt)
                    ax_gr.plot(r_fit * pixel_size, g_fit, color=color, linewidth=1.5,
                               label=lbl)

            ax_gr.axhline(1.0, color='gray', linewidth=0.4, linestyle='--')
            ax_gr.set_ylim(0, None)
            ax_gr.set_xlim(0, 50)
            ax_gr.set_box_aspect(0.65)
            ax_gr.spines['top'].set_visible(False)
            ax_gr.spines['right'].set_visible(False)
            ax_gr.tick_params(labelsize=6)

            # K annotation
            ax_gr.text(0.97, 0.97,
                       f'K$_{{ds,BS}}$={dd["K_bs"]:.3f}\n'
                       f'K$_{{ds,AS}}$={dd["K_as"]:.3f}\n'
                       f'$\\Delta$={dd["pct"]:+.0f}%',
                       transform=ax_gr.transAxes, fontsize=5, fontweight='bold',
                       ha='right', va='top',
                       bbox=dict(facecolor='white', alpha=0.8, edgecolor='#ccc',
                                 boxstyle='round,pad=0.3'))

            if row == 0:
                ax_gr.legend(fontsize=7, loc='upper left', frameon=False)
                ax_gr.set_title('g(r)', fontsize=8, fontweight='bold', pad=2)
            if row == n - 1:
                ax_gr.set_xlabel(r'r ($\mu$m)', fontsize=7, fontweight='bold')
            else:
                ax_gr.set_xticklabels([])

        # Column headers
        fig.axes[0].text(0.5, 1.12, 'Before Stripping', transform=fig.axes[0].transAxes,
                         fontsize=9, fontweight='bold', ha='center')
        fig.axes[1].text(0.5, 1.12, 'After Stripping', transform=fig.axes[1].transAxes,
                         fontsize=9, fontweight='bold', ha='center')

        # Colorbar at bottom
        cbar_ax = fig.add_axes([0.12, 0.02, 0.55, 0.012])
        cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap),
                          cax=cbar_ax, orientation='horizontal')
        cb.set_label(r'|NN distance $-$ r$_0$| / r$_0$', fontsize=8, fontweight='bold')

        if save:
            self._pub_save(fig, 'fig_spatial_order')
        plt.show()

    # ==================================================================
    # MECHANICAL DISEQUILIBRIUM (Fig 5)
    # Row 1: (a) Truss network, (b) Force field, (c) |F| histogram
    # Row 2: (d) ΔK vs Δ|F| hexbin, (e) Convergence arrows, (f) Co-evolution
    # Row 3: (g) Local release, (h) Potential wells, (i) K vs V(r₀)
    # Row 4: (j) K vs CD by |F|, (k) spatial_cv vs K, (l) hot_spots vs ΔK
    # ==================================================================

    def pub_mechanical_disequilibrium(self, image_folder=None, pixel_size=0.58, save=None):
        """
        Publication Figure 5 — Mechanical disequilibrium.

        Row 1 (a-d): Spatial stress maps — auto-picks lowest/highest mean_F donors
        Row 2 (e-h): Population hexbin, convergence arrows, co-evolution, K vs |F|
        Row 3 (l):   Potential wells U(K) and U(F)

        Parameters
        ----------
        image_folder : str or Path, optional
            Folder with images. If None, uses self.image_folder from CSV.
        pixel_size : float
            µm/px for reprocessing representative images.
        """
        save = save if save is not None else self.save
        self._pub_style()

        from scipy.stats import spearmanr
        from matplotlib.collections import LineCollection
        from matplotlib.lines import Line2D
        from matplotlib.transforms import blended_transform_factory
        from numpy.polynomial.polynomial import polyfit

        paired = self.paired
        col_K = 'K_ds_um'
        C_BS, C_AS = '#4A90D9', '#E8833A'

        # Check required columns
        need_cols = ['mean_F_BS', 'mean_F_AS']
        if not all(c in paired.columns for c in need_cols):
            print(f"  ⚠ Mechanical columns missing. Need: {need_cols}")
            return

        # Resolve image folder
        img_folder = image_folder or self.image_folder

        # Compute ΔK%
        paired = paired.copy()
        paired['dK_pct'] = (paired[f'{col_K}_AS'] - paired[f'{col_K}_BS']) / paired[f'{col_K}_BS'] * 100

        def _clip(x, y, pct=2):
            xlo, xhi = np.percentile(x, [pct, 100-pct])
            ylo, yhi = np.percentile(y, [pct, 100-pct])
            m = (x >= xlo) & (x <= xhi) & (y >= ylo) & (y <= yhi)
            return x[m], y[m], m

        fig_w = 190 / 25.4
        fig_h = 250 / 25.4
        fig = plt.figure(figsize=(fig_w, fig_h))

        gs_row1 = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1],
                                    left=0.08, right=0.95, top=0.97, bottom=0.78, wspace=0.45)
        gs_row2 = fig.add_gridspec(1, 4, width_ratios=[1.1, 1.3, 1.0, 0.8],
                                    left=0.04, right=0.96, top=0.68, bottom=0.40, wspace=0.35)
        gs_row3 = fig.add_gridspec(1, 2, width_ratios=[1, 1],
                                    left=0.10, right=0.90, top=0.30, bottom=0.04, wspace=0.45)

        # ══════════════════════════════════════════════════════════
        # ROW 1 (a-d): SPATIAL STRESS MAPS
        # ══════════════════════════════════════════════════════════

        res_low, res_high = None, None
        K_low, K_high = None, None

        if img_folder is not None:
            try:
                from cornealia.cornealia import cornealia as Cornealia

                # Auto-pick lowest and highest mean_F donors
                bs_data = self.df[self.df['group'] == 'BS'].copy()
                if 'mean_F' in bs_data.columns:
                    bs_sorted = bs_data.dropna(subset=['mean_F']).sort_values('mean_F')
                    low_name = bs_sorted.iloc[0]['Image_Name'] if len(bs_sorted) > 0 else None
                    high_name = bs_sorted.iloc[-1]['Image_Name'] if len(bs_sorted) > 0 else None
                else:
                    low_name, high_name = None, None

                engine = Cornealia(pixel_size=pixel_size, is_input_image_machine_output=False, verbose=False)

                for name, label in [(low_name, 'low'), (high_name, 'high')]:
                    if name is None:
                        continue
                    img_path = Path(img_folder) / (name if '.' in name else name + '.png')
                    if not img_path.exists():
                        # Try common extensions
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
                                if K_low: K_low = float(K_low) / (pixel_size**2)
                            else:
                                res_high = rf
                                K_high = r.get('K_ds', r.get('K'))
                                if K_high: K_high = float(K_high) / (pixel_size**2)

                engine._ocr_reader = None
                del engine
            except Exception as e:
                print(f"  ⚠ Row 1 failed: {e}")

        # Shared vmax for panels b and c
        vmax = np.percentile(res_high['F_mag'], 95) if res_high is not None else 1.0

        # Panel a: Truss schematic (low-stress donor with image background)
        ax_a = fig.add_subplot(gs_row1[0, 0])
        if res_low is not None:
            pts = res_low['pts_um']
            edges = res_low['edges']
            d_um = res_low['d_um']
            r0 = res_low['r0']

            # Try loading raw image
            if low_name and img_folder:
                import matplotlib.image as mpimg
                img_path = Path(img_folder) / (low_name if '.' in low_name else low_name + '.png')
                try:
                    img = mpimg.imread(str(img_path))
                    H_px, W_px = img.shape[:2]
                    extent_um = [0, W_px * pixel_size, H_px * pixel_size, 0]
                    ax_a.imshow(img, extent=extent_um, aspect='auto',
                                cmap='gray' if img.ndim == 2 else None, alpha=0.6, zorder=0)
                except Exception:
                    pass

            segments = [[pts[i], pts[j]] for i, j in edges]
            edge_colors = ['#CC3311' if d_um[k] < r0 else '#0077BB' for k in range(len(edges))]
            ax_a.add_collection(LineCollection(segments, colors=edge_colors, linewidths=0.3, alpha=0.35, zorder=1))
            ax_a.scatter(pts[:, 0], pts[:, 1], s=2, c='white', edgecolors='#333', linewidths=0.2, zorder=2, alpha=0.8)
            ax_a.set_xlim(pts[:, 0].min(), pts[:, 0].max())
            ax_a.set_ylim(pts[:, 1].max(), pts[:, 1].min())
            ax_a.set_aspect('equal')

            # Zoom inset
            from matplotlib.patches import Rectangle
            cx, cy = np.median(pts[:, 0]), np.median(pts[:, 1])
            cn = np.argmin(np.sqrt((pts[:, 0] - cx)**2 + (pts[:, 1] - cy)**2))
            zx, zy = pts[cn]
            zr = r0 * 2.2
            rect = Rectangle((zx - zr, zy - zr), 2*zr, 2*zr, lw=1.2, edgecolor='#009E73', facecolor='none', zorder=5)
            ax_a.add_patch(rect)

            ax_in = ax_a.inset_axes([0.55, 0.02, 0.43, 0.55])
            ax_in.set_facecolor('#F8F8F5')
            nmask = (edges[:, 0] == cn) | (edges[:, 1] == cn)
            ring1 = set()
            for i, j in edges[nmask]: ring1.add(i); ring1.add(j)
            ring2 = set()
            for nn in ring1:
                nm2 = (edges[:, 0] == nn) | (edges[:, 1] == nn)
                for i, j in edges[nm2]: ring2.add(i); ring2.add(j)
            for k, (i, j) in enumerate(edges):
                if i in ring2 and j in ring2:
                    xi, yi = pts[i]; xj, yj = pts[j]
                    if zx-zr < xi < zx+zr and zx-zr < xj < zx+zr and zy-zr < yi < zy+zr and zy-zr < yj < zy+zr:
                        color = '#CC3311' if d_um[k] < r0 else '#0077BB'
                        lw = 1.5 if (i in ring1 and j in ring1) else 0.5
                        alpha = 0.9 if (i in ring1 and j in ring1) else 0.25
                        ax_in.plot([xi, xj], [yi, yj], '-', color=color, linewidth=lw, alpha=alpha)
            ax_in.add_patch(plt.Circle((zx, zy), r0, fill=False, color='#009E73', lw=1.5, ls='--', alpha=0.9))
            ax_in.set_xlim(zx-zr, zx+zr); ax_in.set_ylim(zy+zr, zy-zr)
            ax_in.set_aspect('equal'); ax_in.set_xticks([]); ax_in.set_yticks([])
            for sp in ax_in.spines.values(): sp.set_edgecolor('#009E73'); sp.set_linewidth(1.2)

            legend_el = [
                Line2D([0], [0], color='#CC3311', lw=1.5, label=r'd < r$_0$'),
                Line2D([0], [0], color='#0077BB', lw=1.5, label=r'd > r$_0$'),
                Line2D([0], [0], color='#009E73', lw=1.5, ls='--', label=f'r₀={r0:.1f} µm'),
            ]
            ax_a.legend(handles=legend_el, fontsize=5, loc='upper center', ncol=3, framealpha=0.9)
        else:
            ax_a.text(0.5, 0.5, 'No image folder', transform=ax_a.transAxes, ha='center', va='center', fontsize=9, color='#999')
        ax_a.set_xlabel('x (µm)'); ax_a.set_ylabel('y (µm)')
        ax_a.spines['top'].set_visible(False); ax_a.spines['right'].set_visible(False)
        self._pub_panel_label(ax_a, 'a')

        # Panel b: Low-stress force field
        ax_b = fig.add_subplot(gs_row1[0, 1])
        sc_b = self._plot_force_panel(ax_b, res_low, K_low, 'Low stress', vmax, 'b', show_cbar=False)

        # Panel c: High-stress force field
        ax_c = fig.add_subplot(gs_row1[0, 2])
        sc_c = self._plot_force_panel(ax_c, res_high, K_high, 'High stress', vmax, 'c', show_cbar=False)

        # Shared colorbar beneath b and c
        if sc_c is not None:
            bb_b = gs_row1[0, 1].get_position(fig)
            bb_c = gs_row1[0, 2].get_position(fig)
            cbar_ax = fig.add_axes([bb_b.x0 + bb_b.width*0.1, bb_b.y0 - 0.025,
                                    bb_c.x0 + bb_c.width*0.9 - bb_b.x0 - bb_b.width*0.1, 0.01])
            cb = fig.colorbar(sc_c, cax=cbar_ax, orientation='horizontal')
            cb.set_label(r'$|F_i|$ (µm$^{-1}$)', fontsize=8, fontweight='bold')
            cb.ax.tick_params(labelsize=7)

        # Panel d: |F| histogram overlay
        ax_d = fig.add_subplot(gs_row1[0, 3])
        if res_low is not None and res_high is not None:
            F_lo, F_hi = res_low['F_mag'], res_high['F_mag']
            bins = np.linspace(0, np.percentile(np.concatenate([F_lo, F_hi]), 98), 30)
            ax_d.hist(F_lo, bins=bins, color=C_BS, alpha=0.5, edgecolor='white', lw=0.3, density=True, label='Low stress')
            ax_d.hist(F_hi, bins=bins, color='#CC3311', alpha=0.5, edgecolor='white', lw=0.3, density=True, label='High stress')
            ax_d.axvline(F_lo.mean(), color=C_BS, lw=1.5, ls='--', alpha=0.8)
            ax_d.axvline(F_hi.mean(), color='#CC3311', lw=1.5, ls='--', alpha=0.8)
            ax_d.legend(fontsize=6, loc='upper right')
        else:
            ax_d.text(0.5, 0.5, 'No image data', transform=ax_d.transAxes, ha='center', va='center', fontsize=9, color='#999')
        ax_d.set_xlabel(r'$|F_i|$ (µm$^{-1}$)'); ax_d.set_ylabel('Density')
        ax_d.spines['top'].set_visible(False); ax_d.spines['right'].set_visible(False)
        self._pub_panel_label(ax_d, 'd')

        # ══════════════════════════════════════════════════════════
        # ROW 2 (e-h): POPULATION
        # ══════════════════════════════════════════════════════════

        # Panel e: Hexbin mean|F| vs ΔK%
        ax_e = fig.add_subplot(gs_row2[0, 0])
        F_star = self._plot_hexbin_lowess(ax_e, paired, 'mean_F_BS', 'dK_pct',
                                           r'Baseline mean $|F|$ (µm$^{-1}$)', 'e')

        # Panel f: Convergence arrows by mean|F|
        self._plot_convergence_arrows(fig, gs_row2[0, 1], paired, 'mean_F_BS', F_star, 'f',
                                       r'Bins by mean $|F|$')

        # Panel g: Co-evolution ΔK vs Δ|F|
        ax_g = fig.add_subplot(gs_row2[0, 2])
        dK_v = paired['dK_pct'].values
        dF_v = (paired['mean_F_AS'] - paired['mean_F_BS']).values
        valid = np.isfinite(dK_v) & np.isfinite(dF_v)
        dF_c, dK_c, _ = _clip(dF_v[valid], dK_v[valid], pct=1)
        hb = ax_g.hexbin(dF_c, dK_c, gridsize=18, cmap='Greys', mincnt=1, zorder=1)
        plt.colorbar(hb, ax=ax_g, shrink=0.6, pad=0.02).set_label('Count', fontsize=7)
        ax_g.axhline(0, color='black', lw=0.8, ls=':', zorder=1)
        ax_g.axvline(0, color='black', lw=0.8, ls=':', zorder=1)
        coeffs = polyfit(dF_c, dK_c, 1)
        x_fit = np.linspace(dF_c.min(), dF_c.max(), 100)
        ax_g.plot(x_fit, coeffs[0] + coeffs[1] * x_fit, '--', color='#E65100', lw=2.0, alpha=0.8)
        rho, p = spearmanr(dF_c, dK_c)
        ax_g.text(0.95, 0.03, f'ρ = {rho:.3f}\np = {p:.1e}', transform=ax_g.transAxes,
                  fontsize=7, ha='right', va='bottom', fontweight='bold', color='#333',
                  bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))
        ax_g.set_xlabel(r'$\Delta$ mean $|F|$ (µm$^{-1}$)'); ax_g.set_ylabel(r'$\Delta K_{ds}$ (%)')
        ax_g.text(0.03, 0.97, 'F↓ K↑', transform=ax_g.transAxes, fontsize=6, ha='left', va='top', color='#888', fontweight='bold')
        ax_g.text(0.97, 0.97, 'F↑ K↑', transform=ax_g.transAxes, fontsize=6, ha='right', va='top', color='#CC3311', fontweight='bold')
        ax_g.text(0.03, 0.35, 'F↓ K↓', transform=ax_g.transAxes, fontsize=6, ha='left', va='top', color='#CC3311', fontweight='bold')
        ax_g.text(0.97, 0.35, 'F↑ K↓', transform=ax_g.transAxes, fontsize=6, ha='right', va='top', color='#888', fontweight='bold')
        ax_g.spines['top'].set_visible(False); ax_g.spines['right'].set_visible(False)
        self._pub_panel_label(ax_g, 'g')

        # Panel h: Cross-sectional K vs |F|
        ax_h = fig.add_subplot(gs_row2[0, 3])
        K_all = paired[f'{col_K}_BS'].values
        F_all = paired['mean_F_BS'].values
        valid_h = np.isfinite(K_all) & np.isfinite(F_all)
        K_all, F_all = K_all[valid_h], F_all[valid_h]
        p99 = np.percentile(K_all, 99)
        m99 = K_all <= p99
        ax_h.scatter(K_all[m99], F_all[m99], s=4, alpha=0.3, color='#333', edgecolors='none')
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess
            si = np.argsort(K_all[m99])
            lw_fit = lowess(F_all[m99][si], K_all[m99][si], frac=0.4)
            ax_h.plot(lw_fit[:, 0], lw_fit[:, 1], '-', color='#E65100', linewidth=2.5)
        except ImportError:
            pass
        rho_h, p_h = spearmanr(K_all[m99], F_all[m99])
        ax_h.text(0.05, 0.95, f'ρ = {rho_h:.3f}\nn = {len(K_all[m99])}', transform=ax_h.transAxes,
                  fontsize=7, fontweight='bold', va='top',
                  bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))
        ax_h.set_xlabel(r'$K_{ds}$ (µm$^{-2}$)'); ax_h.set_ylabel(r'mean $|F|$ (µm$^{-1}$)')
        ax_h.spines['top'].set_visible(False); ax_h.spines['right'].set_visible(False)
        self._pub_panel_label(ax_h, 'h')

        # ══════════════════════════════════════════════════════════
        # ROW 3 (l): POTENTIAL WELLS U(K) and U(F)
        # ══════════════════════════════════════════════════════════

        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess as lowess_fn

            def _make_potential(x_bs, x_as, frac=0.4):
                valid = np.isfinite(x_bs) & np.isfinite(x_as)
                xb, xa = x_bs[valid], x_as[valid]
                dx = xa - xb
                p2, p98 = np.percentile(xb, [2, 98])
                m = (xb >= p2) & (xb <= p98)
                xb, dx = xb[m], dx[m]
                si = np.argsort(xb)
                lw = lowess_fn(dx[si], xb[si], frac=frac)
                crossings = np.where(np.diff(np.sign(lw[:, 1])))[0]
                x_star = None
                if len(crossings) > 0:
                    i = crossings[0]
                    x0, x1 = lw[i, 0], lw[i+1, 0]
                    y0, y1 = lw[i, 1], lw[i+1, 1]
                    x_star = x0 - y0 * (x1 - x0) / (y1 - y0) if y1 != y0 else x0
                ddx = np.diff(lw[:, 0])
                mid_v = (lw[:-1, 1] + lw[1:, 1]) / 2
                U = np.concatenate([[0], np.cumsum(-mid_v * ddx)])
                U -= U.min()
                return lw[:, 0], U, x_star

            # U(K)
            ax_l1 = fig.add_subplot(gs_row3[0, 0])
            xK, UK, K_star = _make_potential(paired[f'{col_K}_BS'].values, paired[f'{col_K}_AS'].values)
            ax_l1.fill_between(xK, UK, alpha=0.15, color='#4A90D9')
            ax_l1.plot(xK, UK, '-', color='#4A90D9', linewidth=2)
            if K_star:
                U_s = np.interp(K_star, xK, UK)
                ax_l1.plot(K_star, U_s, 'o', color='#0072B2', markersize=6, markeredgecolor='white', markeredgewidth=1.2, zorder=5)
                ax_l1.axvline(K_star, color='#0072B2', lw=1, ls='--', alpha=0.4)
                ax_l1.text(K_star, UK.max() * 0.75, f'  $K^*$={K_star:.3f}', fontsize=7, fontweight='bold', color='#0072B2', va='center')
            ax_l1.set_xlabel(r'$K_{ds}$ (µm$^{-2}$)'); ax_l1.set_ylabel(r'$U(K)$')
            ax_l1.spines['top'].set_visible(False); ax_l1.spines['right'].set_visible(False)
            self._pub_panel_label(ax_l1, 'i')

            # U(F)
            ax_l2 = fig.add_subplot(gs_row3[0, 1])
            xF, UF, F_star_w = _make_potential(paired['mean_F_BS'].values, paired['mean_F_AS'].values)
            ax_l2.fill_between(xF, UF, alpha=0.15, color='#CC3311')
            ax_l2.plot(xF, UF, '-', color='#CC3311', linewidth=2)
            if F_star_w:
                U_s = np.interp(F_star_w, xF, UF)
                ax_l2.plot(F_star_w, U_s, 'o', color='#CC3311', markersize=6, markeredgecolor='white', markeredgewidth=1.2, zorder=5)
                ax_l2.axvline(F_star_w, color='#CC3311', lw=1, ls='--', alpha=0.4)
                ax_l2.text(F_star_w, UF.max() * 0.75, f'  $|F|^*$={F_star_w:.3f}', fontsize=7, fontweight='bold', color='#CC3311', va='center')
            ax_l2.set_xlabel(r'mean $|F|$ (µm$^{-1}$)'); ax_l2.set_ylabel(r'$U(|F|)$')
            ax_l2.spines['top'].set_visible(False); ax_l2.spines['right'].set_visible(False)

        except ImportError:
            ax_l1 = fig.add_subplot(gs_row3[0, 0])
            ax_l1.text(0.5, 0.5, 'statsmodels required\nfor potential wells', transform=ax_l1.transAxes,
                      ha='center', va='center', fontsize=9, color='#999')
            self._pub_panel_label(ax_l1, 'i')

        plt.tight_layout()
        if save:
            self._pub_save(fig, 'fig5_mechanical_disequilibrium')
        plt.show()

    # ── Helpers for mechanical disequilibrium ──

    def _plot_force_panel(self, ax, result, K_ds, subtitle, vmax, label, show_cbar=False):
        """Force field panel: edges + heatmap + vectors."""
        if result is None:
            ax.text(0.5, 0.5, 'No data', transform=ax.transAxes, ha='center', va='center', fontsize=9, color='#999')
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            self._pub_panel_label(ax, label)
            return None

        from matplotlib.collections import LineCollection
        pts = result['pts_um']; edges = result['edges']
        d_um = result['d_um']; r0 = result['r0']
        F_res = result['F_residual']; F_mag = result['F_mag']

        segments = [[pts[i], pts[j]] for i, j in edges]
        edge_colors = ['#E8CCCC' if d_um[k] < r0 else '#CCE0F0' for k in range(len(edges))]
        ax.add_collection(LineCollection(segments, colors=edge_colors, linewidths=0.25, alpha=0.3))

        sc = ax.scatter(pts[:, 0], pts[:, 1], c=F_mag, s=8, cmap='YlOrRd',
                        vmin=0, vmax=vmax, edgecolors='none', zorder=2)

        threshold = np.percentile(F_mag, 70)
        high = F_mag >= threshold
        if high.any():
            scale = np.percentile(F_mag[high], 95)
            ax.quiver(pts[high, 0], pts[high, 1], F_res[high, 0], F_res[high, 1],
                      F_mag[high], cmap='YlOrRd', clim=(0, vmax),
                      scale=scale*18, width=0.004, headwidth=3, headlength=3.5, alpha=0.75, zorder=3)

        if show_cbar:
            plt.colorbar(sc, ax=ax, shrink=0.75, pad=0.02).set_label(r'$|F_i|$', fontsize=8)

        ax.set_aspect('equal')
        ax.set_xlabel('x (µm)')
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

        K_str = f'{K_ds:.3f}' if K_ds is not None else '?'
        ax.text(0.97, 0.03, f'$K_{{ds}}$={K_str}\nmean$|F|$={F_mag.mean():.2f}',
                transform=ax.transAxes, fontsize=6, fontweight='bold', color='white',
                ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.6, edgecolor='none'))
        ax.set_title(f'{label}   {subtitle}', fontweight='bold', fontsize=9, loc='left', pad=4)
        return sc

    def _plot_hexbin_lowess(self, ax, paired, metric_col, dk_col, xlabel, label, lowess_frac=0.45):
        """Hexbin of baseline metric vs ΔK% with LOWESS fit. Returns crossing value."""
        from matplotlib.transforms import blended_transform_factory

        x = paired[metric_col].to_numpy(dtype=float)
        y = paired[dk_col].to_numpy(dtype=float)
        valid = np.isfinite(x) & np.isfinite(y)
        x, y = x[valid], y[valid]
        xlo, xhi = np.percentile(x, [1, 99])
        ylo, yhi = np.percentile(y, [1, 99])
        m = (x >= xlo) & (x <= xhi) & (y >= ylo) & (y <= yhi)
        xc, yc = x[m], y[m]

        hb = ax.hexbin(xc, yc, gridsize=18, cmap='Greys', mincnt=1, zorder=1)
        plt.colorbar(hb, ax=ax, shrink=0.6, pad=0.02).set_label('Count', fontsize=7)

        crossing_val = None
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess
            si = np.argsort(xc)
            lw_fit = lowess(yc[si], xc[si], frac=lowess_frac)
            ax.plot(lw_fit[:, 0], lw_fit[:, 1], '-', color='#E65100', linewidth=3.0, label='LOWESS', zorder=3)
            crossings = np.where(np.diff(np.sign(lw_fit[:, 1])))[0]
            if len(crossings) > 0:
                i = crossings[0]
                x0, x1, y0, y1 = lw_fit[i, 0], lw_fit[i+1, 0], lw_fit[i, 1], lw_fit[i+1, 1]
                crossing_val = x0 - y0 * (x1 - x0) / (y1 - y0) if y1 != y0 else x0
                ax.axvline(crossing_val, color='#0072B2', lw=2.0, ls='--', alpha=0.9, zorder=2)
                trans = blended_transform_factory(ax.transData, ax.transAxes)
                ax.text(crossing_val, 0.80, f'  $|F|^*$', transform=trans, fontsize=7,
                        fontweight='bold', color='#0072B2', va='top', ha='left')
        except ImportError:
            pass

        ax.axhline(0, color='black', lw=0.8, ls=':', zorder=1)
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_ylabel(r'$\Delta K_{ds}$ (%)', fontsize=9)
        if ax.get_legend_handles_labels()[0]:
            ax.legend(fontsize=6, loc='upper right', framealpha=0.9)
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

        from scipy.stats import spearmanr
        rho, p = spearmanr(xc, yc)
        ax.text(0.95, 0.03, f'ρ = {rho:.3f}\np = {p:.1e}', transform=ax.transAxes,
                fontsize=7, ha='right', va='bottom', fontweight='bold', color='#333',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))
        self._pub_panel_label(ax, label)
        return crossing_val

    def _plot_convergence_arrows(self, fig, subplot_spec, paired, metric_col, crossing_val, label, y_label_text):
        """Binned arrow plot: metric bins → K_ds direction."""
        from matplotlib.transforms import blended_transform_factory
        from matplotlib.lines import Line2D

        col_K = 'K_ds_um'
        C_BS, C_AS = '#4A90D9', '#E8833A'

        gs_inner = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=subplot_spec,
                                                     width_ratios=[1, 4], wspace=0.04)
        ax_hist = fig.add_subplot(gs_inner[0])
        ax = fig.add_subplot(gs_inner[1], sharey=ax_hist)

        bs_metric = paired[metric_col].to_numpy(dtype=float)
        bs_kv = paired[f'{col_K}_BS'].to_numpy(dtype=float)
        as_kv = paired[f'{col_K}_AS'].to_numpy(dtype=float)
        valid = np.isfinite(bs_metric) & np.isfinite(bs_kv) & np.isfinite(as_kv)
        bs_metric, bs_kv, as_kv = bs_metric[valid], bs_kv[valid], as_kv[valid]

        if crossing_val is None:
            ax.text(0.5, 0.5, 'Crossing not found', transform=ax.transAxes, ha='center', va='center')
            self._pub_panel_label(ax, label); return

        n_bins = 15
        p1, p99 = np.percentile(bs_metric, [1, 99])
        bin_edges = np.linspace(p1, p99, n_bins + 1)
        bin_counts = []

        for i in range(n_bins):
            hi_op = (bs_metric <= bin_edges[i+1]) if i == n_bins-1 else (bs_metric < bin_edges[i+1])
            mask = (bs_metric >= bin_edges[i]) & hi_op
            count = int(mask.sum()); bin_counts.append(count)
            if count < 3: continue
            mean_bs_k = np.mean(bs_kv[mask]); mean_as_k = np.mean(as_kv[mask])
            mean_m = np.mean(bs_metric[mask])
            dk_mean = mean_as_k - mean_bs_k
            expected = (dk_mean > 0) if (mean_m < crossing_val) else (dk_mean < 0)
            color = C_AS if expected else '#bbb'
            alpha = 0.85 if expected else 0.40
            ax.annotate('', xy=(mean_as_k, i), xytext=(mean_bs_k, i),
                        arrowprops=dict(arrowstyle='->', color=color, lw=1.8 if expected else 1.0, alpha=alpha))
            ax.plot(mean_bs_k, i, 'o', color=C_BS, markersize=4, markeredgecolor='white', markeredgewidth=0.3, zorder=4)
            ax.plot(mean_as_k, i, 'o', color=color, markersize=4, markeredgecolor='white', markeredgewidth=0.3, zorder=4)

        cross_bin = (crossing_val - p1) / (p99 - p1) * n_bins
        ax.axhline(cross_bin, color='#0072B2', lw=1.0, ls=':', alpha=0.5)
        ax_hist.axhline(cross_bin, color='#0072B2', lw=1.0, ls=':', alpha=0.5)

        ax.set_xlabel(r'$K_{ds}$ (µm$^{-2}$)', fontsize=9)
        ax.set_ylim(-1, n_bins); ax.set_yticks([])
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.spines['left'].set_visible(False)

        legend_el = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor=C_BS, markersize=4, label='BS', linewidth=0),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=C_AS, markersize=4, label='AS', linewidth=0),
            Line2D([0], [0], color=C_AS, lw=1.5, label='Expected'),
            Line2D([0], [0], color='#bbb', lw=1.0, label='Opposite'),
        ]
        ax.legend(handles=legend_el, fontsize=6, loc='lower right', framealpha=0.9)
        self._pub_panel_label(ax, label)

        y_pos = np.arange(n_bins)
        bar_colors = [C_BS if c >= 3 else '#ddd' for c in bin_counts]
        ax_hist.barh(y_pos, bin_counts, height=0.75, color=bar_colors, alpha=0.4, edgecolor='white', linewidth=0.3)
        ax_hist.set_xlim(max(max(bin_counts, default=0), 1) * 1.15, 0)
        ax_hist.set_xlabel('n', fontsize=7); ax_hist.set_yticks([])
        ax_hist.spines['top'].set_visible(False); ax_hist.spines['right'].set_visible(False); ax_hist.spines['left'].set_visible(False)
        ax_hist.tick_params(axis='x', labelsize=6)

    # ==================================================================
    # ALL AT ONCE
    # ==================================================================

    def all(self, save=None):
        """Run all plot methods in sequence."""
        save = save if save is not None else self.save
        self.distributions(save=save)
        self.as_vs_bs_improvement_all(save=save)
        self.pub_boxplots(save=save)
        self.pub_K_deep_dive(save=save)
        self.pub_validation(save=save)
        self.pub_K_independence(save=save)
        self.pub_comprehensive(save=save)
        self.pub_collective_order(save=save)
        self.pub_mechanical_disequilibrium(save=save)
