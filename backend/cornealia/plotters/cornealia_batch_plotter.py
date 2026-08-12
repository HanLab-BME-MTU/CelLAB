"""
cornealia_batch_plotter.py

Reads batch CSVs produced by run_batch.py and generates:
  Category 1 — Distribution histograms
  Category 2 — AS vs BS comparisons (box plots, paired scatter, histograms)
               with paired t-tests and p-values
  Category 3 — Computed vs Machine validation (scatter + R², Bland-Altman)

Usage:
    from cornealia.plotters.cornealia_batch_plotter import cornealia_batch_plotter

    bp = cornealia_batch_plotter('batch_results')
    bp.distributions()
    bp.as_vs_bs_boxplots()
    bp.as_vs_bs_scatter()
    bp.as_vs_bs_histograms()
    bp.validation_scatter()
    bp.validation_bland_altman()
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

    def histogram(self, metric='K_um', save=None):
        """Standalone histogram for a single metric."""
        save = save if save is not None else self.save

        col, label, unit = COMPUTED_METRICS[metric]
        data = self.df[col].dropna()

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(data, bins=30, color=COLORS['neutral'], edgecolor='black',
                linewidth=0.8, alpha=0.85)
        mean_val = data.mean()
        std_val = data.std()
        ax.axvline(mean_val, color=COLORS['AS'], linestyle='--', linewidth=2.5,
                   label=f'Mean = {mean_val:.2f} ± {std_val:.2f}')
        ax.set_xlabel(f'{label} ({unit})', fontsize=16, fontweight='bold')
        ax.set_ylabel('Count', fontsize=16, fontweight='bold')
        ax.set_title(f'Distribution of {label}', fontsize=18, fontweight='bold', pad=15)
        ax.legend(fontsize=12, loc='upper right')
        ax.tick_params(axis='both', labelsize=14)
        sns.despine(ax=ax)
        plt.tight_layout()
        if save:
            self._save_fig(fig, f'01_{metric}_histogram')
        plt.show()

    # ==================================================================
    # CATEGORY 2 — AS vs BS
    # ==================================================================

    def as_vs_bs_boxplots(self, save=None):
        """2×3 box plots comparing AS vs BS for each metric, with paired t-test."""
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
            plot_data = self.df[self.df['group'].isin(['AS', 'BS'])]

            sns.boxplot(x='group', y=col, data=plot_data, ax=ax,
                        hue='group', palette={'AS': COLORS['AS'], 'BS': COLORS['BS']},
                        width=0.5, fliersize=3, linewidth=1.5,
                        order=['BS', 'AS'], legend=False)
            sns.stripplot(x='group', y=col, data=plot_data, ax=ax,
                          hue='group', palette={'AS': COLORS['AS'], 'BS': COLORS['BS']},
                          size=3, alpha=0.4, jitter=True, order=['BS', 'AS'], legend=False)

            # Paired t-test
            t, p, n = self._paired_ttest(col)
            if p is not None:
                # Draw bracket
                y_max = plot_data[col].max()
                y_range = plot_data[col].max() - plot_data[col].min()
                bracket_y = y_max + y_range * 0.08
                ax.plot([0, 0, 1, 1], [bracket_y, bracket_y + y_range * 0.02,
                         bracket_y + y_range * 0.02, bracket_y],
                        color='black', linewidth=1.5)
                ax.text(0.5, bracket_y + y_range * 0.04, _format_p(p),
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

            ax.set_xlabel('', fontsize=12)
            ax.set_ylabel(f'{label} ({unit})', fontsize=11, fontweight='bold')
            ax.set_title(f'{label}', fontsize=13, fontweight='bold')
            ax.tick_params(axis='both', labelsize=10)
            sns.despine(ax=ax)

        plt.suptitle('AS vs BS Comparison (paired t-test)',
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        if save:
            self._save_fig(fig, '02_as_vs_bs_boxplots')
        plt.show()

    def as_vs_bs_scatter(self, save=None):
        """2×3 paired scatter plots: each dot = one patient (BS on x, AS on y)."""
        save = save if save is not None else self.save

        if len(self.paired) == 0:
            print("No paired AS/BS data available for scatter plots.")
            return

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
            col_as = f'{col}_AS'
            col_bs = f'{col}_BS'

            if col_as not in self.paired.columns:
                ax.set_visible(False)
                continue

            valid = self.paired[[col_bs, col_as]].dropna()
            ax.scatter(valid[col_bs], valid[col_as],
                       c=COLORS['computed'], s=40, edgecolor='black',
                       linewidth=0.5, alpha=0.7, zorder=3)

            # Identity line
            all_vals = pd.concat([valid[col_bs], valid[col_as]])
            lims = [all_vals.min() * 0.95, all_vals.max() * 1.05]
            ax.plot(lims, lims, '--', color=COLORS['identity'], linewidth=2,
                    label='y = x', zorder=1)
            ax.set_xlim(lims)
            ax.set_ylim(lims)

            # Paired t-test
            t, p, n = self._paired_ttest(col)
            if p is not None:
                ax.text(0.05, 0.95, f'{_format_p(p)}\nn = {n}',
                        transform=ax.transAxes, fontsize=9, fontweight='bold',
                        va='top', ha='left',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                  edgecolor='black', alpha=0.9))

            ax.set_xlabel(f'BS — {label} ({unit})', fontsize=11, fontweight='bold')
            ax.set_ylabel(f'AS — {label} ({unit})', fontsize=11, fontweight='bold')
            ax.set_title(f'{label}', fontsize=13, fontweight='bold')
            ax.set_aspect('equal')
            ax.legend(fontsize=9, loc='lower right')
            ax.tick_params(axis='both', labelsize=10)
            sns.despine(ax=ax)

        plt.suptitle('AS vs BS Paired Scatter (each dot = one patient)',
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        if save:
            self._save_fig(fig, '03_as_vs_bs_scatter')
        plt.show()

    def as_vs_bs_histograms(self, save=None):
        """2×3 overlaid histograms: AS vs BS for each metric, with paired t-test."""
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
            as_data = self.df.loc[self.df['group'] == 'AS', col].dropna()
            bs_data = self.df.loc[self.df['group'] == 'BS', col].dropna()

            bins = np.linspace(
                min(as_data.min(), bs_data.min()),
                max(as_data.max(), bs_data.max()),
                25)

            ax.hist(bs_data, bins=bins, color=COLORS['BS'], alpha=0.6,
                    edgecolor='black', linewidth=0.5,
                    label=f'BS (n={len(bs_data)})')
            ax.hist(as_data, bins=bins, color=COLORS['AS'], alpha=0.6,
                    edgecolor='black', linewidth=0.5,
                    label=f'AS (n={len(as_data)})')

            # Paired t-test
            t, p, n = self._paired_ttest(col)
            if p is not None:
                ax.text(0.95, 0.95, f'{_format_p(p)}\nn = {n} pairs',
                        transform=ax.transAxes, fontsize=9, fontweight='bold',
                        va='top', ha='right',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                  edgecolor='black', alpha=0.9))

            ax.set_xlabel(f'{label} ({unit})', fontsize=11, fontweight='bold')
            ax.set_ylabel('Count', fontsize=11, fontweight='bold')
            ax.set_title(f'{label}', fontsize=13, fontweight='bold')
            ax.legend(fontsize=9, loc='upper left')
            ax.tick_params(axis='both', labelsize=10)
            sns.despine(ax=ax)

        plt.suptitle('AS vs BS Distributions (paired t-test)',
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        if save:
            self._save_fig(fig, '04_as_vs_bs_histograms')
        plt.show()

    # ==================================================================
    # CATEGORY 3 — COMPUTED vs MACHINE (VALIDATION)
    # ==================================================================

    def validation_scatter(self, save=None):
        """2×2 scatter plots: computed metric vs machine metric with R² and regression."""
        save = save if save is not None else self.save

        fig, axes = plt.subplots(2, 2, figsize=(11, 10))
        axes = axes.flatten()

        avail_pairs = [(c, m, l) for c, m, l in VALIDATION_PAIRS if c in self.df.columns and m in self.df.columns]
        for j in range(len(avail_pairs), len(axes)):
            axes[j].set_visible(False)


        for i, (comp_col, mach_col, label) in enumerate(avail_pairs):
            ax = axes[i]
            valid = self.df[[comp_col, mach_col]].dropna()

            if len(valid) < 3:
                ax.text(0.5, 0.5, 'Insufficient data', transform=ax.transAxes,
                        ha='center', fontsize=12)
                ax.set_title(label, fontsize=13, fontweight='bold')
                continue

            x = valid[mach_col].values.astype(float)
            y = valid[comp_col].values.astype(float)

            ax.scatter(x, y, c=COLORS['computed'], s=30, edgecolor='black',
                       linewidth=0.5, alpha=0.6, zorder=3)

            # Regression
            slope, intercept, r, p, se = stats.linregress(x, y)
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, slope * x_line + intercept, '-',
                    color=COLORS['AS'], linewidth=2.5,
                    label=f'$R^2$ = {r**2:.3f}')

            # Identity line
            all_vals = np.concatenate([x, y])
            lims = [all_vals.min() * 0.95, all_vals.max() * 1.05]
            ax.plot(lims, lims, '--', color=COLORS['identity'], linewidth=1.5,
                    label='y = x', zorder=1)

            ax.set_xlabel(f'Machine — {label}', fontsize=11, fontweight='bold')
            ax.set_ylabel(f'Computed — {label}', fontsize=11, fontweight='bold')
            ax.set_title(label, fontsize=13, fontweight='bold')
            ax.legend(fontsize=10, loc='upper left')
            ax.tick_params(axis='both', labelsize=10)
            sns.despine(ax=ax)

        plt.suptitle('Computed vs Machine Metrics',
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        if save:
            self._save_fig(fig, '07_validation_scatter')
        plt.show()

    def validation_bland_altman(self, save=None):
        """2×2 Bland-Altman plots: difference vs mean for each paired metric."""
        save = save if save is not None else self.save

        fig, axes = plt.subplots(2, 2, figsize=(11, 10))
        axes = axes.flatten()

        avail_pairs = [(c, m, l) for c, m, l in VALIDATION_PAIRS if c in self.df.columns and m in self.df.columns]
        for j in range(len(avail_pairs), len(axes)):
            axes[j].set_visible(False)


        for i, (comp_col, mach_col, label) in enumerate(avail_pairs):
            ax = axes[i]
            valid = self.df[[comp_col, mach_col]].dropna()

            if len(valid) < 3:
                ax.text(0.5, 0.5, 'Insufficient data', transform=ax.transAxes,
                        ha='center', fontsize=12)
                ax.set_title(label, fontsize=13, fontweight='bold')
                continue

            comp = valid[comp_col].values.astype(float)
            mach = valid[mach_col].values.astype(float)

            mean_vals = (comp + mach) / 2
            diff_vals = comp - mach
            mean_diff = np.mean(diff_vals)
            std_diff = np.std(diff_vals)

            ax.scatter(mean_vals, diff_vals, c=COLORS['computed'], s=30,
                       edgecolor='black', linewidth=0.5, alpha=0.6)

            # Mean difference line
            ax.axhline(mean_diff, color=COLORS['AS'], linestyle='-',
                       linewidth=2, label=f'Mean diff = {mean_diff:.1f}')

            # ±1.96 SD limits of agreement
            ax.axhline(mean_diff + 1.96 * std_diff, color=COLORS['identity'],
                       linestyle='--', linewidth=1.5,
                       label=f'+1.96 SD = {mean_diff + 1.96 * std_diff:.1f}')
            ax.axhline(mean_diff - 1.96 * std_diff, color=COLORS['identity'],
                       linestyle='--', linewidth=1.5,
                       label=f'−1.96 SD = {mean_diff - 1.96 * std_diff:.1f}')

            ax.axhline(0, color='black', linestyle=':', linewidth=1)

            ax.set_xlabel(f'Mean of Computed & Machine', fontsize=11, fontweight='bold')
            ax.set_ylabel(f'Computed − Machine', fontsize=11, fontweight='bold')
            ax.set_title(label, fontsize=13, fontweight='bold')
            ax.legend(fontsize=8, loc='upper right')
            ax.tick_params(axis='both', labelsize=10)
            sns.despine(ax=ax)

        plt.suptitle('Bland-Altman: Computed vs Machine',
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        if save:
            self._save_fig(fig, '08_validation_bland_altman')
        plt.show()

    # ==================================================================
    # CATEGORY 2b — AS vs BS IMPROVEMENT ANALYSIS
    # ==================================================================

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

    def deep_dive(self, metric='K_um', save=None):
        """
        3x2 comprehensive panel for a single metric:
          [0,0] Distribution histogram (all data)
          [0,1] AS vs BS box plot with paired t-test
          [1,0] AS vs BS overlaid histograms
          [1,1] Paired scatter (colored by improvement)
          [2,0] Histogram of % change
          [2,1] Summary statistics box

        Parameters
        ----------
        metric : str
            Key from COMPUTED_METRICS (default 'K_um')
        """
        save = save if save is not None else self.save

        col, label, unit = COMPUTED_METRICS[metric]
        plain_label, plain_unit = PLAIN_LABELS[metric]
        col_as = f'{col}_AS'
        col_bs = f'{col}_BS'

        # --- Prepare data ---
        all_data = self.df[col].dropna()
        as_data = self.df.loc[self.df['group'] == 'AS', col].dropna()
        bs_data = self.df.loc[self.df['group'] == 'BS', col].dropna()
        plot_data = self.df[self.df['group'].isin(['AS', 'BS'])]

        # Paired data
        paired = self.paired.copy()
        has_paired = col_as in paired.columns and col_bs in paired.columns
        if has_paired:
            paired['_diff'] = paired[col_as] - paired[col_bs]
            threshold = paired[col_bs].quantile(0.01) if paired[col_bs].quantile(0.01) > 0 else 1e-6
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

        # --- Figure ---
        fig, axes = plt.subplots(3, 2, figsize=(14, 16))

        # ------ [0,0] Distribution histogram (all data) ------
        ax = axes[0, 0]
        ax.hist(all_data, bins=40, color=COLORS['neutral'], edgecolor='black',
                linewidth=0.5, alpha=0.85)
        mean_val = all_data.mean()
        std_val = all_data.std()
        ax.axvline(mean_val, color=COLORS['AS'], linestyle='--', linewidth=2.5,
                   label=f'Mean = {mean_val:.4f}')
        ax.axvline(mean_val - std_val, color=COLORS['identity'], linestyle=':', linewidth=1.5)
        ax.axvline(mean_val + std_val, color=COLORS['identity'], linestyle=':', linewidth=1.5,
                   label=f'SD = {std_val:.4f}')
        ax.set_xlabel(f'{label} ({unit})', fontsize=12, fontweight='bold')
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title(f'Overall Distribution (n = {len(all_data)})',
                     fontsize=13, fontweight='bold')
        ax.legend(fontsize=9, loc='upper right')
        ax.tick_params(axis='both', labelsize=10)
        sns.despine(ax=ax)

        # ------ [0,1] AS vs BS box plot ------
        ax = axes[0, 1]
        sns.boxplot(x='group', y=col, data=plot_data, ax=ax,
                    hue='group', palette={'AS': COLORS['AS'], 'BS': COLORS['BS']},
                    width=0.5, fliersize=3, linewidth=1.5,
                    order=['BS', 'AS'], legend=False)
        sns.stripplot(x='group', y=col, data=plot_data, ax=ax,
                      hue='group', palette={'AS': COLORS['AS'], 'BS': COLORS['BS']},
                      size=3, alpha=0.3, jitter=True, order=['BS', 'AS'], legend=False)

        # Bracket with p-value
        t, p, n = self._paired_ttest(col)
        if p is not None:
            y_max = plot_data[col].max()
            y_range = plot_data[col].max() - plot_data[col].min()
            bracket_y = y_max + y_range * 0.08
            ax.plot([0, 0, 1, 1], [bracket_y, bracket_y + y_range * 0.02,
                     bracket_y + y_range * 0.02, bracket_y],
                    color='black', linewidth=1.5)
            ax.text(0.5, bracket_y + y_range * 0.04, _format_p(p),
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_xlabel('', fontsize=12)
        ax.set_ylabel(f'{label} ({unit})', fontsize=12, fontweight='bold')
        ax.set_title(f'AS vs BS (paired t-test, n = {n} pairs)',
                     fontsize=13, fontweight='bold')
        ax.tick_params(axis='both', labelsize=10)
        sns.despine(ax=ax)

        # ------ [1,0] AS vs BS overlaid histograms ------
        ax = axes[1, 0]
        bins = np.linspace(
            min(as_data.min(), bs_data.min()),
            max(as_data.max(), bs_data.max()), 35)
        ax.hist(bs_data, bins=bins, color=COLORS['BS'], alpha=0.6,
                edgecolor='black', linewidth=0.5,
                label=f'BS (n={len(bs_data)}, mean={bs_data.mean():.4f})')
        ax.hist(as_data, bins=bins, color=COLORS['AS'], alpha=0.6,
                edgecolor='black', linewidth=0.5,
                label=f'AS (n={len(as_data)}, mean={as_data.mean():.4f})')
        ax.axvline(bs_data.mean(), color=COLORS['BS'], linestyle='--', linewidth=2)
        ax.axvline(as_data.mean(), color=COLORS['AS'], linestyle='--', linewidth=2)
        ax.set_xlabel(f'{label} ({unit})', fontsize=12, fontweight='bold')
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('AS vs BS Distributions', fontsize=13, fontweight='bold')
        ax.legend(fontsize=9, loc='upper right')
        ax.tick_params(axis='both', labelsize=10)
        sns.despine(ax=ax)

        # ------ [1,1] Paired scatter colored by improvement ------
        ax = axes[1, 1]
        if has_paired and n_total > 0:
            ax.scatter(valid.loc[~improved, col_bs], valid.loc[~improved, col_as],
                       c=COLORS['BS'], s=20, alpha=0.4,
                       label=f'Decreased ({(~improved).sum()})')
            ax.scatter(valid.loc[improved, col_bs], valid.loc[improved, col_as],
                       c=COLORS['AS'], s=20, alpha=0.4,
                       label=f'Improved ({improved.sum()})')
            all_vals = pd.concat([valid[col_bs], valid[col_as]])
            lims = [0, all_vals.max() * 1.05]
            ax.plot(lims, lims, '--', color=COLORS['identity'], linewidth=1.5)
            ax.set_xlim(lims)
            ax.set_ylim(lims)
            ax.text(0.05, 0.95, f'{_format_p(p_ttest)}\nn = {n_total}',
                    transform=ax.transAxes, fontsize=9, fontweight='bold',
                    va='top', ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='black', alpha=0.9))
        ax.set_xlabel(f'BS - {label} ({unit})', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'AS - {label} ({unit})', fontsize=12, fontweight='bold')
        ax.set_title('Paired Scatter (colored by improvement)',
                     fontsize=13, fontweight='bold')
        ax.legend(fontsize=9, loc='upper left')
        ax.tick_params(axis='both', labelsize=10)
        sns.despine(ax=ax)

        # ------ [2,0] Histogram of % change ------
        ax = axes[2, 0]
        if has_paired and n_total > 0:
            pct_clipped = valid['_pct_change'].clip(-200, 500)
            ax.hist(pct_clipped, bins=50, color=COLORS['computed'], edgecolor='black',
                    linewidth=0.5, alpha=0.8)
            ax.axvline(0, color='red', linestyle='--', linewidth=2, label='No change')
            ax.axvline(median_pct, color=COLORS['AS'], linestyle='-', linewidth=2,
                       label=f'Median = {median_pct:+.1f}%')
            ax.set_xlabel(f'{label} change (%)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Count', fontsize=12, fontweight='bold')
            ax.set_title('Per-Patient % Change (AS vs BS)',
                         fontsize=13, fontweight='bold')
            ax.legend(fontsize=9)
        ax.tick_params(axis='both', labelsize=10)
        sns.despine(ax=ax)

        # ------ [2,1] Summary box ------
        ax = axes[2, 1]
        ax.axis('off')

        if has_paired and n_total > 0:
            summary = (
                f"{'='*44}\n"
                f"   {plain_label.upper()} COMPREHENSIVE SUMMARY\n"
                f"{'='*44}\n\n"
                f"  Overall (n={len(all_data)}):\n"
                f"    Mean:  {mean_val:.4f} {plain_unit}\n"
                f"    SD:    {std_val:.4f} {plain_unit}\n\n"
                f"  BS (n={len(bs_data)}):  mean = {bs_data.mean():.4f}\n"
                f"  AS (n={len(as_data)}):  mean = {as_data.mean():.4f}\n\n"
                f"  Paired analysis (n={n_total}):\n"
                f"    Improved:   {n_improved} ({n_improved/n_total*100:.1f}%)\n"
                f"    Decreased:  {n_total-n_improved} ({(n_total-n_improved)/n_total*100:.1f}%)\n"
                f"    Median d%:  {median_pct:+.1f}%\n"
                f"    Mean delta: {mean_diff:+.4f} {plain_unit}\n\n"
                f"  Paired t-test:  p = {p_ttest:.2e}\n"
                f"  Wilcoxon:       p = {p_wilcox:.2e}\n"
                f"{'='*44}"
            )
        else:
            summary = (
                f"{'='*44}\n"
                f"   {plain_label.upper()} SUMMARY\n"
                f"{'='*44}\n\n"
                f"  Overall (n={len(all_data)}):\n"
                f"    Mean: {mean_val:.4f} {plain_unit}\n"
                f"    SD:   {std_val:.4f} {plain_unit}\n\n"
                f"  No paired data available.\n"
                f"{'='*44}"
            )

        ax.text(0.05, 0.5, summary, transform=ax.transAxes, fontsize=11,
                verticalalignment='center', fontfamily='monospace', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFACD',
                          edgecolor='black', linewidth=1.5, alpha=0.95))

        plt.suptitle(f'{label} — Comprehensive Analysis',
                     fontsize=18, fontweight='bold', y=1.01)
        plt.tight_layout()
        if save:
            self._save_fig(fig, f'06_{metric}_deep_dive')
        plt.show()
        
    
    

    # ------------------------------------------------------------------
    # PUBLICATION STYLE HELPER
    # ------------------------------------------------------------------

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
        k_metric : str
            Which K column to use: 'K_ds_um', 'K_um', etc.
        """
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
            if mb.sum() > 5:
                box_data.append(kv_c[mb])
                box_pos.append(bcd[i])
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
        bk_h, dkp_h, _ = _clip(bs_kv_h, dk_pct, pct=2)
        hb2 = ax_h.hexbin(bk_h, dkp_h, gridsize=20, cmap='YlOrRd', mincnt=1)
        if lowess is not None:
            si = np.argsort(bk_h)
            lw_fit = lowess(dkp_h[si], bk_h[si], frac=0.3)
            ax_h.plot(lw_fit[:, 0], lw_fit[:, 1], 'k-', linewidth=2.5, label='LOWESS')
            crossings = np.where(np.diff(np.sign(lw_fit[:, 1])))[0]
            if len(crossings) > 0:
                sp = lw_fit[crossings[0], 0]
                ax_h.axvline(sp, color='cyan', linewidth=1.5, linestyle='--',
                             label=f'Setpoint ~ {sp:.3f}')
        ax_h.axhline(0, color='black', linewidth=0.5, linestyle='--')
        ax_h.set_xlabel('Baseline K_ds (um$^{-2}$)', fontsize=6)
        ax_h.set_ylabel('DK (%)', fontsize=7)
        ax_h.set_title('(h) Homeostatic setpoint', fontsize=8)
        ax_h.legend(fontsize=4, loc='upper right')
        plt.colorbar(hb2, ax=ax_h, shrink=0.7, label='Count')
        ax_h.spines['top'].set_visible(False)
        ax_h.spines['right'].set_visible(False)
        ax_h.set_box_aspect(1)

        if save:
            self._pub_save(fig, f'fig_comprehensive_{k_metric}')
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
    # ALL AT ONCE
    # ==================================================================

    def all(self, save=None):
        """Run all plot methods in sequence."""
        save = save if save is not None else self.save
        self.distributions(save=save)
        self.as_vs_bs_boxplots(save=save)
        self.as_vs_bs_scatter(save=save)
        self.as_vs_bs_histograms(save=save)
        self.as_vs_bs_improvement(metric='K_um', save=save)
        self.as_vs_bs_improvement(metric='r_0_um', save=save)
        self.deep_dive(metric='K_um', save=save)
        self.deep_dive(metric='r_0_um', save=save)
        self.validation_scatter(save=save)
        self.validation_bland_altman(save=save)
