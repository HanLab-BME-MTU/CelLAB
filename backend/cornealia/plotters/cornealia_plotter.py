import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from matplotlib.colors import ListedColormap
from scipy.optimize import curve_fit
from pathlib import Path
import random
import os


# ============================================================================
# PUBLICATION STYLE
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
    'raw':       '#0072B2',   # Blue
    'smooth':    '#D55E00',   # Vermillion
    'fit':       '#009E73',   # Green
    'reference': '#CC79A7',   # Pink
    'highlight': '#F0E442',   # Yellow
    'interior':  '#56B4E9',   # Light blue
    'edge':      '#999999',   # Gray
    'neutral':   '#4A4A4A',   # Dark gray
}


# ============================================================================
# PLOTTER CLASS
# ============================================================================

class cornealia_plotter:

    def __init__(self, results, save=False, save_dir='cornealia_plots', formats=('png', 'pdf')):
        # results is now a dict returned by collective_order()
        # wrap it in a simple namespace so self.c.xxx still works throughout
        from types import SimpleNamespace
        self.c = SimpleNamespace(**results)
        
        # also expose segmentation sub-attributes directly on self.c
        seg = results.get('segmentation')
        if seg is not None:
            self.c.H = seg['H']
            self.c.W = seg['W']
            self.c.enhanced_image = seg['enhanced_image']
            self.c.seg_labels = seg['labels']
            self.c.seg_blobs = seg['blobs']
            self.c.seg_global_fg = seg['global_fg']
            self.c.metrics_area = results.get('cell_area')
        else:
            self.c.H = None
            self.c.W = None
            self.c.enhanced_image = None
            self.c.seg_labels = None
            self.c.seg_blobs = None
            self.c.seg_global_fg = None
            self.c.metrics_area = None

        # config defaults (no longer echoed in results, but plotter labels need them)
        if not hasattr(self.c, 'fcm_method'):
            self.c.fcm_method = 'auto'
        if not hasattr(self.c, 'SAVGOL_WINDOW'):
            self.c.SAVGOL_WINDOW = 11
        if not hasattr(self.c, 'shell_thickness'):
            self.c.shell_thickness = 1
        if not hasattr(self.c, 'exclusion_ratio'):
            self.c.exclusion_ratio = 0.15
        if not hasattr(self.c, 'fitting_half_width'):
            self.c.fitting_half_width = 10

        # convenience: expose centroids and n_cells at top level
        if seg is not None:
            self.c.seg_centroids = seg['centroids']
            self.c.seg_n_cells = seg['n_cells']
        else:
            self.c.seg_centroids = None
            self.c.seg_n_cells = 0
        
        self.save = save
        self.save_dir = save_dir
        self.formats = formats
    
        if self.save:
            os.makedirs(self.save_dir, exist_ok=True)
            print(f"Plots will be saved to: {os.path.abspath(self.save_dir)}")
    
        set_publication_style()
    
    def _check_attr(self, *attrs):
        """Check required keys exist in results namespace."""
        for attr in attrs:
            if not hasattr(self.c, attr):
                raise AttributeError(
                    f"Results dict missing '{attr}'. "
                    f"Make sure collective_order() completed successfully."
                )

    # -----------------------------------------------------------------------
    # INTERNAL HELPERS
    # -----------------------------------------------------------------------

    def _save_fig(self, fig, filename):
        """Save figure in all requested formats."""
        if self.save:
            for fmt in self.formats:
                path = os.path.join(self.save_dir, f'{filename}.{fmt}')
                fig.savefig(path, dpi=600, bbox_inches='tight')
            print(f"Saved: {filename} → {', '.join(self.formats)}")

    def _check_attr(self, *attrs):
        """Raise informative error if required attributes are missing."""
        for attr in attrs:
            if not hasattr(self.c, attr):
                raise AttributeError(
                    f"cornealia object missing '{attr}'. "
                    f"Make sure you have called the required methods first."
                )

    # -----------------------------------------------------------------------
    # FIT-CURVE HELPER (dispatches on fitting_method)
    # -----------------------------------------------------------------------

    def _compute_fit_curve(self):
        """
        Recompute the fitted curve for plotting.

        Returns a dict with:
          r_fit, v_fit       – data points used for plotting (window for quadratic, full for Morse)
          r_dense, v_curve   – smooth fitted curve for overlay
          fit_label          – legend string, e.g. 'Quadratic fit' or 'Morse fit'
          title_label        – title string with K value
          method             – 'quadratic' or 'morse'
        """
        c = self.c
        r_v = c.r_valid
        v = c.v_r_valid
        method = getattr(c, 'fitting_method', 'quadratic')

        # Common: find minimum and window (needed for quadratic, and for data display in Morse)
        end_search = len(r_v) // 2
        v_min_idx = np.argmin(v[:end_search])
        hw = c.fitting_half_width
        fit_start = max(0, v_min_idx - hw)
        fit_end = min(v_min_idx + hw + 1, end_search)
        r_window = r_v[fit_start:fit_end]
        v_window = v[fit_start:fit_end]
        v_min = v[v_min_idx]

        if method == 'morse':
            def morse_potential(r, D_e, a, r_0, offset):
                return D_e * (1 - np.exp(-a * (r - r_0)))**2 + offset

            # --- Smoothed V(r) for range finding only ---
            g_smooth_safe = c.g_r_smooth.copy()
            g_smooth_safe[g_smooth_safe <= 0] = 1e-10
            v_smooth = -np.log(g_smooth_safe)
            valid_s = c.g_r_smooth > 0.05
            r_vs = c.r_values[valid_s]
            v_vs = v_smooth[valid_s]
            end_s = len(r_vs) // 2
            vmi_s = np.argmin(v_vs[:end_s])

            # Right boundary (from smoothed)
            post_s = v_vs[vmi_s:]
            sc = np.where(np.diff(np.sign(post_s)))[0]
            if len(sc) >= 1:
                root1_s = vmi_s + sc[0] + 1
                post_r1 = v_vs[root1_s:]
                sc2 = np.where(np.diff(np.sign(post_r1)))[0]
                root2_s = root1_s + sc2[0] + 1 if len(sc2) >= 1 else len(v_vs)
                seg = v_vs[root1_s:root2_s]
                ri_s = root1_s + np.argmax(seg) + 1 if len(seg) > 0 else root1_s + 1
            else:
                ri_s = vmi_s + np.argmax(post_s) + 1
            ri_s = min(ri_s, len(r_vs))
            r_right = r_vs[ri_s - 1]

            # Left boundary (from smoothed)
            pre_s = v_vs[:vmi_s][::-1]
            scl = np.where(np.diff(np.sign(pre_s)))[0]
            if len(scl) >= 1:
                li_s = vmi_s - (scl[0] + 1)
            else:
                li_s = 0
            li_s = max(li_s, 0)
            r_left = r_vs[li_s]

            # Map to raw indices
            left_idx = np.argmin(np.abs(r_v - r_left))
            right_idx = np.argmin(np.abs(r_v - r_right)) + 1
            right_idx = min(right_idx, len(r_v))

            r_fit_morse = r_v[left_idx:right_idx]
            v_fit_morse = v[left_idx:right_idx]

            D_e_guess = abs(v_min)
            a_guess = 0.1
            r_0_guess = r_v[v_min_idx]
            offset_guess = v_min

            try:
                popt, _ = curve_fit(
                    morse_potential, r_fit_morse, v_fit_morse,
                    p0=[D_e_guess, a_guess, r_0_guess, offset_guess],
                    bounds=([0, 0, r_fit_morse[0], -np.inf],
                            [np.inf, np.inf, r_fit_morse[-1], np.inf]),
                    maxfev=5000
                )
                D_e_fit, a_fit, r0_fit, offset_fit = popt
                r_dense = np.linspace(r_fit_morse[0], r_fit_morse[-1], 300)
                v_curve = morse_potential(r_dense, *popt)

                return {
                    'r_fit': r_fit_morse, 'v_fit': v_fit_morse,
                    'r_window': r_window, 'v_window': v_window,
                    'r_dense': r_dense, 'v_curve': v_curve,
                    'fit_label': 'Morse fit',
                    'title_label': r'Morse Fit: K = ' + f'{c.K:.3f} ' + r'px$^{-2}$',
                    'method': 'morse',
                    'popt': popt,
                    'cut_idx': right_idx,
                }
            except RuntimeError:
                # fallback to quadratic if Morse fails
                method = 'quadratic'

        # Quadratic (default or fallback)
        coeffs = np.polyfit(r_window, v_window, 2)
        r_dense = np.linspace(r_window[0], r_window[-1], 100)
        v_curve = np.polyval(coeffs, r_dense)

        return {
            'r_fit': r_window, 'v_fit': v_window,
            'r_window': r_window, 'v_window': v_window,
            'r_dense': r_dense, 'v_curve': v_curve,
            'fit_label': 'Quadratic fit',
            'title_label': r'Quadratic Fit: K = ' + f'{c.K:.3f} ' + r'px$^{-2}$',
            'method': 'quadratic',
            'coeffs': coeffs,
        }

    # -----------------------------------------------------------------------
    # 1. SEGMENTATION OVERVIEW
    # -----------------------------------------------------------------------

    def segmentation(self, save=None):
        """
        2x3 panel showing:
        input image | cell area | metrics area
        blobs       | fg mask   | watershed labels
        """
        self._check_attr('input_image', 'cell_area', 'metrics_area',
                         'enhanced_image', 'seg_labels')

        save = save if save is not None else self.save

        n = self.c.seg_labels.max()
        colors = ['black'] + [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(n)]
        cmap = ListedColormap(colors)

        fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(14, 9))
        axs = axs.flatten()

        axs[0].imshow(self.c.input_image)
        axs[0].set_title('Input Image', fontweight='bold')
        axs[0].axis('off')

        axs[1].imshow(self.c.cell_area)
        axs[1].set_title('Cell Area', fontweight='bold')
        axs[1].axis('off')

        axs[2].imshow(self.c.metrics_area)
        axs[2].set_title('Metrics Area', fontweight='bold')
        axs[2].axis('off')

        axs[3].imshow(self.c.enhanced_image, cmap='gray')
        axs[3].scatter(self.c.seg_blobs[:, 1], self.c.seg_blobs[:, 0],
                       c='red', s=10, label=f'{len(self.c.seg_blobs)} blobs')
        axs[3].set_title('Blob Detection', fontweight='bold')
        axs[3].legend(fontsize=9, loc='upper right')
        axs[3].axis('off')

        axs[4].imshow(self.c.seg_global_fg, cmap='gray')
        axs[4].set_title(f'Foreground Mask ({self.c.fcm_method} FCM)', fontweight='bold')
        axs[4].axis('off')

        axs[5].imshow(self.c.seg_labels, cmap=cmap)
        axs[5].set_title(f'Watershed Labels ({n} cells)', fontweight='bold')
        axs[5].axis('off')

        plt.suptitle('Segmentation Overview', fontsize=16, fontweight='bold')
        plt.tight_layout()
        if save:
            self._save_fig(fig, '01_segmentation_overview')
        plt.show()

    # -----------------------------------------------------------------------
    # 2. RADIAL DISTRIBUTION FUNCTION g(r)
    # -----------------------------------------------------------------------

    def radial_distribution(self, save=None, zoom_max=80):
        """
        Two-panel: full g(r) | zoomed g(r)
        """
        self._check_attr('r_values', 'g_r', 'g_r_smooth')
        save = save if save is not None else self.save

        c = self.c
        r = c.r_values
        zoom = r <= zoom_max

        # find first peak in smoothed g(r) for annotation
        peak_idx = np.argmax(c.g_r_smooth)
        r_peak = r[peak_idx]
        g_peak = c.g_r_smooth[peak_idx]

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # --- Full range ---
        ax = axes[0]
        ax.plot(r, c.g_r, '.', color=COLORS['raw'], markersize=3, alpha=0.4, label='Raw')
        ax.plot(r, c.g_r_smooth, '-', color=COLORS['smooth'], linewidth=2.5,
                label=f'Savitzky-Golay (w={c.SAVGOL_WINDOW})')
        ax.axhline(y=1, color=COLORS['neutral'], linestyle='--', linewidth=2, label='g(r) = 1')
        ax.plot(r_peak, g_peak, 'o', color=COLORS['fit'], markersize=12,
                markeredgecolor='black', markeredgewidth=1.5, zorder=5,
                label=f'Peak: r = {r_peak:.0f} px')
        ax.set_xlabel('r (pixels)', fontsize=14, fontweight='bold')
        ax.set_ylabel('g(r)', fontsize=14, fontweight='bold')
        ax.set_title('Radial Distribution Function g(r)', fontsize=15, fontweight='bold', pad=12)
        ax.set_xlim(0, r.max())
        ax.set_ylim(0, max(2.5, c.g_r_smooth.max() * 1.1))
        ax.tick_params(axis='both', labelsize=12)
        ax.legend(fontsize=10, loc='upper right', framealpha=0.95)
        ax.yaxis.grid(True, alpha=0.3, linewidth=0.8)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        # --- Zoomed ---
        ax = axes[1]
        ax.plot(r[zoom], c.g_r[zoom], '.', color=COLORS['raw'], markersize=5, alpha=0.5, label='Raw')
        ax.plot(r[zoom], c.g_r_smooth[zoom], '-', color=COLORS['smooth'], linewidth=2.5, label='Smoothed')
        ax.axhline(y=1, color=COLORS['neutral'], linestyle='--', linewidth=2)
        if r_peak <= zoom_max:
            ax.plot(r_peak, g_peak, 'o', color=COLORS['fit'], markersize=14,
                    markeredgecolor='black', markeredgewidth=1.5, zorder=5)
        ax.set_xlabel('r (pixels)', fontsize=14, fontweight='bold')
        ax.set_ylabel('g(r)', fontsize=14, fontweight='bold')
        ax.set_title(f'g(r) Zoomed (r < {zoom_max} px)', fontsize=15, fontweight='bold', pad=12)
        ax.set_xlim(0, zoom_max)
        ax.set_ylim(0, max(2.5, c.g_r_smooth[zoom].max() * 1.1))
        ax.tick_params(axis='both', labelsize=12)
        ax.legend(fontsize=10, loc='upper right', framealpha=0.95)
        ax.yaxis.grid(True, alpha=0.3, linewidth=0.8)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        plt.tight_layout()
        if save:
            self._save_fig(fig, '02_radial_distribution')
        plt.show()

    # -----------------------------------------------------------------------
    # 3. EFFECTIVE POTENTIAL V(r)
    # -----------------------------------------------------------------------

    def potential(self, save=None, zoom_max=80):
        """
        Two-panel: full V(r) | zoomed V(r)
        """
        self._check_attr('r_valid', 'v_r_valid', 'r0_fit', 'K')
        save = save if save is not None else self.save

        c = self.c
        r = c.r_valid
        v = c.v_r_valid
        zoom = r <= zoom_max

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # --- Full range ---
        ax = axes[0]
        ax.plot(r, v, '-', color=COLORS['smooth'], linewidth=2.5, label='V(r) = -ln(g(r))')
        ax.axhline(y=0, color=COLORS['neutral'], linestyle='--', linewidth=2)
        ax.plot(c.r0_fit, np.min(v[:len(v)//2]), 'o', color=COLORS['fit'], markersize=12,
                markeredgecolor='black', markeredgewidth=1.5, zorder=5,
                label=r'Min: r$_0$ = ' + f'{c.r0_fit:.1f} px')
        ax.set_xlabel('r (pixels)', fontsize=14, fontweight='bold')
        ax.set_ylabel('V(r)', fontsize=14, fontweight='bold')
        ax.set_title('Effective Potential V(r) = -ln(g(r))', fontsize=15, fontweight='bold', pad=12)
        ax.set_xlim(0, r.max())
        ax.set_ylim(-1.5, 3)
        ax.tick_params(axis='both', labelsize=12)
        ax.legend(fontsize=10, loc='upper right', framealpha=0.95)
        ax.yaxis.grid(True, alpha=0.3, linewidth=0.8)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        # --- Zoomed ---
        ax = axes[1]
        ax.plot(r[zoom], v[zoom], '-', color=COLORS['smooth'], linewidth=2.5, label='V(r)')
        ax.axhline(y=0, color=COLORS['neutral'], linestyle='--', linewidth=2)
        ax.axvline(x=c.r0_fit, color=COLORS['fit'], linestyle=':', linewidth=2,
                   label=r'r$_0$ = ' + f'{c.r0_fit:.1f} px')
        ax.set_xlabel('r (pixels)', fontsize=14, fontweight='bold')
        ax.set_ylabel('V(r)', fontsize=14, fontweight='bold')
        ax.set_title(f'V(r) Zoomed (r < {zoom_max} px)', fontsize=15, fontweight='bold', pad=12)
        ax.set_xlim(0, zoom_max)
        ax.set_ylim(-1.5, 2)
        ax.tick_params(axis='both', labelsize=12)
        ax.legend(fontsize=10, loc='upper right', framealpha=0.95)
        ax.yaxis.grid(True, alpha=0.3, linewidth=0.8)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        plt.tight_layout()
        if save:
            self._save_fig(fig, '03_potential_Vr')
        plt.show()

    # -----------------------------------------------------------------------
    # 4. CURVE FIT (adapts to fitting_method)
    # -----------------------------------------------------------------------

    def fitting(self, save=None):
        """
        Two-panel: V(r) with fit region highlighted | fitted curve zoomed.
        Automatically adapts to quadratic or Morse based on fitting_method.
        """
        self._check_attr('r_valid', 'v_r_valid', 'r0_fit', 'K')
        save = save if save is not None else self.save

        c = self.c
        r = c.r_valid
        v = c.v_r_valid
        fc = self._compute_fit_curve()

        # find minimum for marker
        end_search = len(r) // 2
        v_min_idx = np.argmin(v[:end_search])

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # --- V(r) with fit region ---
        ax = axes[0]
        zoom = r <= 80
        ax.plot(r[zoom], v[zoom], '-', color=COLORS['smooth'], linewidth=2.5, label='V(r)')
        ax.axhline(y=0, color=COLORS['neutral'], linestyle='--', linewidth=1.5)
        if fc['method'] == 'quadratic':
            ax.axvspan(fc['r_window'][0], fc['r_window'][-1], alpha=0.25,
                       color=COLORS['highlight'], label='Fit window')
        else:
            ax.axvspan(fc['r_fit'][0], fc['r_fit'][-1], alpha=0.15,
                       color=COLORS['highlight'], label='Fit region')
        ax.plot(r[v_min_idx], v[v_min_idx], 'o', color=COLORS['fit'], markersize=12,
                markeredgecolor='black', markeredgewidth=1.5, zorder=5)
        ax.set_xlabel('r (pixels)', fontsize=14, fontweight='bold')
        ax.set_ylabel('V(r)', fontsize=14, fontweight='bold')
        ax.set_title('V(r) with Fit Region', fontsize=15, fontweight='bold', pad=12)
        ax.set_xlim(0, 80)
        ax.set_ylim(-1.2, 1.5)
        ax.tick_params(axis='both', labelsize=12)
        ax.legend(fontsize=10, loc='upper right', framealpha=0.95)
        ax.yaxis.grid(True, alpha=0.3, linewidth=0.8)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        # --- Fitted curve ---
        ax = axes[1]
        if fc['method'] == 'morse':
            # Show well-region data + Morse curve (not the full tail)
            ax.plot(fc['r_fit'], fc['v_fit'], 'o', color=COLORS['raw'], markersize=4,
                    alpha=0.5, markeredgecolor='none', label='V(r) data (well region)')
            ax.plot(fc['r_dense'], fc['v_curve'], '-',
                    color=COLORS['smooth'], linewidth=3, label=fc['fit_label'])
        else:
            ax.plot(fc['r_fit'], fc['v_fit'], 'o', color=COLORS['raw'], markersize=8,
                    markeredgecolor='black', markeredgewidth=1, label='Data (smoothed)')
            ax.plot(fc['r_dense'], fc['v_curve'], '-',
                    color=COLORS['smooth'], linewidth=3, label=fc['fit_label'])
        ax.axhline(y=0, color=COLORS['neutral'], linestyle='--', linewidth=2)
        ax.axvline(x=c.r0_fit, color=COLORS['fit'], linestyle=':', linewidth=2.5,
                   label=r'r$_0$ = ' + f'{c.r0_fit:.1f} px')
        ax.set_xlabel('r (pixels)', fontsize=14, fontweight='bold')
        ax.set_ylabel('V(r)', fontsize=14, fontweight='bold')
        ax.set_title(fc['title_label'], fontsize=15, fontweight='bold', pad=12)
        ax.tick_params(axis='both', labelsize=12)
        ax.legend(fontsize=11, loc='upper right', framealpha=0.95)
        ax.yaxis.grid(True, alpha=0.3, linewidth=0.8)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        plt.tight_layout()
        method_tag = fc['method']
        if save:
            self._save_fig(fig, f'04_{method_tag}_fit')
        plt.show()

    # -----------------------------------------------------------------------
    # 5. COMPREHENSIVE 3x3
    # -----------------------------------------------------------------------

    def comprehensive(self, save=None):
        """
        4x3 panel covering all analysis steps:
        Row 1: centroids | g(r) raw | g(r) smoothed
        Row 2: V(r) full | V(r) zoomed | Morse fit
        Row 3: seg labels | CLAHE image | summary box
        Row 4: damped sine fit | residuals | quality gate
        """
        self._check_attr('r_values', 'g_r', 'g_r_smooth',
                         'r_valid', 'v_r_valid', 'r0_fit', 'K', 'seg_labels')
        save = save if save is not None else self.save

        c = self.c
        r = c.r_values
        r_v = c.r_valid
        v = c.v_r_valid

        # centroids
        centroids = c.seg_centroids
        y_coords = centroids[:, 0]
        x_coords = centroids[:, 1]
        cell_H, cell_W = c.H, c.W
        MAX_R = int(min(cell_H, cell_W) * c.exclusion_ratio)
        interior_mask = ((y_coords >= MAX_R) & (y_coords <= cell_H - MAX_R) &
                         (x_coords >= MAX_R) & (x_coords <= cell_W - MAX_R))

        # fit
        end_search = len(r_v) // 2
        v_min_idx = np.argmin(v[:end_search])
        fc = self._compute_fit_curve()

        # peak
        peak_idx = np.argmax(c.g_r_smooth)
        r_peak = r[peak_idx]
        g_peak = c.g_r_smooth[peak_idx]

        fig, axes = plt.subplots(4, 3, figsize=(17, 19))

        # --- Row 1 ---

        # 1.1 Centroids
        ax = axes[0, 0]
        ax.scatter(x_coords[~interior_mask], y_coords[~interior_mask],
                   s=10, c=COLORS['edge'], alpha=0.5, edgecolor='none',
                   label=f'Edge ({(~interior_mask).sum()})')
        ax.scatter(x_coords[interior_mask], y_coords[interior_mask],
                   s=12, c=COLORS['interior'], alpha=0.7, edgecolor='none',
                   label=f'Interior ({interior_mask.sum()})')
        rect = plt.Rectangle((MAX_R, MAX_R), cell_W - 2*MAX_R, cell_H - 2*MAX_R,
                              fill=False, edgecolor=COLORS['smooth'], linestyle='--', linewidth=2)
        ax.add_patch(rect)
        ax.set_xlim(0, cell_W)
        ax.set_ylim(cell_H, 0)
        ax.set_xlabel('X (pixels)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Y (pixels)', fontsize=12, fontweight='bold')
        ax.set_title(f'Step 1: Cell Centroids\n(N = {c.seg_n_cells} total)', fontsize=13, fontweight='bold', pad=8)
        ax.tick_params(axis='both', labelsize=10)
        ax.legend(fontsize=9, loc='upper right', framealpha=0.95)
        ax.set_aspect('equal')
        sns.despine(ax=ax)

        # 1.2 Raw g(r)
        ax = axes[0, 1]
        ax.plot(r, c.g_r, '.', color=COLORS['raw'], markersize=3, alpha=0.5)
        ax.axhline(y=1, color=COLORS['smooth'], linestyle='--', linewidth=2, label='g(r) = 1')
        ax.set_xlabel('r (pixels)', fontsize=12, fontweight='bold')
        ax.set_ylabel('g(r)', fontsize=12, fontweight='bold')
        ax.set_title(f'Step 2: Raw g(r)\n(DR = {c.shell_thickness} px)', fontsize=13, fontweight='bold', pad=8)
        ax.set_xlim(0, r.max())
        ax.set_ylim(0, max(2.5, c.g_r.max() * 1.1))
        ax.tick_params(axis='both', labelsize=10)
        ax.legend(fontsize=9, loc='upper right')
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        # 1.3 Smoothed g(r)
        ax = axes[0, 2]
        ax.plot(r, c.g_r, '.', color=COLORS['raw'], markersize=3, alpha=0.3, label='Raw')
        ax.plot(r, c.g_r_smooth, '-', color=COLORS['smooth'], linewidth=2,
                label=f'Savitzky-Golay (w={c.SAVGOL_WINDOW})')
        ax.axhline(y=1, color=COLORS['neutral'], linestyle='--', linewidth=1.5)
        ax.plot(r_peak, g_peak, 'o', color=COLORS['fit'], markersize=10,
                markeredgecolor='black', markeredgewidth=1.5, zorder=5,
                label=f'Peak: r = {r_peak:.0f} px')
        ax.set_xlabel('r (pixels)', fontsize=12, fontweight='bold')
        ax.set_ylabel('g(r)', fontsize=12, fontweight='bold')
        ax.set_title('Step 3: g(r) Smoothed', fontsize=13, fontweight='bold', pad=8)
        ax.set_xlim(0, r.max())
        ax.set_ylim(0, max(2.5, c.g_r_smooth.max() * 1.1))
        ax.tick_params(axis='both', labelsize=10)
        ax.legend(fontsize=9, loc='upper right')
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        # --- Row 2 ---

        # 2.1 V(r) full
        ax = axes[1, 0]
        ax.plot(r_v, v, '-', color=COLORS['smooth'], linewidth=2, label='V(r) = -ln(g)')
        ax.axhline(y=0, color=COLORS['neutral'], linestyle='--', linewidth=1.5)
        ax.plot(r_v[v_min_idx], v[v_min_idx], 'o', color=COLORS['fit'], markersize=10,
                markeredgecolor='black', markeredgewidth=1.5, zorder=5,
                label=r'Min: r$_0$ = ' + f'{c.r0_fit:.0f} px')
        ax.set_xlabel('r (pixels)', fontsize=12, fontweight='bold')
        ax.set_ylabel('V(r)', fontsize=12, fontweight='bold')
        ax.set_title('Step 4: V(r) = -ln(g(r))', fontsize=13, fontweight='bold', pad=8)
        ax.set_xlim(0, r_v.max())
        ax.set_ylim(-1.5, 3)
        ax.tick_params(axis='both', labelsize=10)
        ax.legend(fontsize=9, loc='upper right')
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        # 2.2 V(r) zoomed
        ax = axes[1, 1]
        zoom = r_v <= 80
        ax.plot(r_v[zoom], v[zoom], '-', color=COLORS['smooth'], linewidth=2, label='V(r)')
        ax.axhline(y=0, color=COLORS['neutral'], linestyle='--', linewidth=1.5)
        if fc['method'] == 'quadratic':
            ax.axvspan(fc['r_window'][0], fc['r_window'][-1], alpha=0.25,
                       color=COLORS['highlight'], label='Fit window')
        else:
            ax.axvspan(fc['r_fit'][0], fc['r_fit'][-1], alpha=0.15,
                       color=COLORS['highlight'], label='Fit region')
        ax.set_xlabel('r (pixels)', fontsize=12, fontweight='bold')
        ax.set_ylabel('V(r)', fontsize=12, fontweight='bold')
        ax.set_title('Step 5: V(r) Zoomed + Fit Region', fontsize=13, fontweight='bold', pad=8)
        ax.set_xlim(0, 80)
        ax.set_ylim(-1.2, 1.5)
        ax.tick_params(axis='both', labelsize=10)
        ax.legend(fontsize=9, loc='upper right')
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        # 2.3 Curve fit (adapts to method)
        ax = axes[1, 2]
        if fc['method'] == 'morse':
            ax.plot(fc['r_fit'], fc['v_fit'], 'o', color=COLORS['raw'], markersize=4,
                    alpha=0.5, markeredgecolor='none', label='V(r) data (well region)')
            ax.plot(fc['r_dense'], fc['v_curve'], '-',
                    color=COLORS['smooth'], linewidth=2.5, label=fc['fit_label'])
        else:
            ax.plot(fc['r_fit'], fc['v_fit'], 'o', color=COLORS['raw'], markersize=8,
                    markeredgecolor='black', markeredgewidth=1, label='Data (smoothed)')
            ax.plot(fc['r_dense'], fc['v_curve'], '-',
                    color=COLORS['smooth'], linewidth=2.5, label=fc['fit_label'])
        ax.axhline(y=0, color=COLORS['neutral'], linestyle='--', linewidth=1.5)
        ax.axvline(x=c.r0_fit, color=COLORS['fit'], linestyle=':', linewidth=2.5,
                   label=r'r$_0$ = ' + f'{c.r0_fit:.1f} px')
        ax.set_xlabel('r (pixels)', fontsize=12, fontweight='bold')
        ax.set_ylabel('V(r)', fontsize=12, fontweight='bold')
        ax.set_title(f'Step 6: {fc["title_label"]}',
                     fontsize=13, fontweight='bold', pad=8)
        ax.tick_params(axis='both', labelsize=10)
        ax.legend(fontsize=9, loc='upper right')
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

        # --- Row 3 ---

        # 3.1 Segmentation labels
        n_labels = self.c.seg_labels.max()
        colors_seg = ['black'] + [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(n_labels)]
        cmap_seg = ListedColormap(colors_seg)
        ax = axes[2, 0]
        ax.imshow(self.c.seg_labels, cmap=cmap_seg)
        ax.set_title(f'Step 7: Watershed Labels\n({n_labels} cells)', fontsize=13, fontweight='bold', pad=8)
        ax.axis('off')

        # 3.2 CLAHE-enhanced image (input to segmentation)
        ax = axes[2, 1]
        ax.imshow(c.enhanced_image, cmap='gray')
        ax.set_title('CLAHE Enhanced Image', fontsize=13, fontweight='bold', pad=8)
        ax.axis('off')

        # 3.3 Summary box
        ax = axes[2, 2]
        ax.axis('off')
        plateau_mean = np.mean(c.g_r_smooth[int(len(c.g_r_smooth) * 0.7):])
        method_name = fc['method'].capitalize()
        K_Vmin = getattr(c, 'K_Vmin', np.nan)
        K_gpeak = getattr(c, 'K_gpeak', np.nan)
        K_ds_val = getattr(c, 'K_ds', np.nan)
        g_peak_val = getattr(c, 'g_peak', np.nan)
        _reliable = getattr(c, 'reliable', None)
        _R2 = getattr(c, 'R2_damped', np.nan)
        _A_ds = getattr(c, 'A_damped', np.nan)
        _xi_ds = getattr(c, 'xi_damped', np.nan)
        _lam_ds = getattr(c, 'lambda_damped', np.nan)
        _flag = "✅ RELIABLE" if _reliable else "❌ UNRELIABLE" if _reliable is not None else "N/A"
        _box_color = '#FFFACD' if _reliable or _reliable is None else '#FFD0D0'
        summary_text = (
            f"{'━'*42}\n"
            f"    COLLECTIVE ORDER RESULTS\n"
            f"{'━'*42}\n\n"
            f"Cells:\n"
            f"  Total:    {c.seg_n_cells}\n"
            f"  Interior: {interior_mask.sum()}\n\n"
            f"Parameters:\n"
            f"  DR (shell) = {c.shell_thickness} px\n"
            f"  MAX_R      = {int(min(cell_H, cell_W) * c.exclusion_ratio)} px\n"
            f"  Fit method = {method_name}\n"
            f"  V(r) smooth = SG(w={c.SAVGOL_WINDOW}) range only\n\n"
            f"Results:\n"
            f"  r_0     = {c.r0_fit:.3f} px\n"
            f"  V(r_0)  = {c.v_min:.3f}\n"
            f"  g_peak  = {g_peak_val:.3f}\n"
            f"  K       = {c.K:.4f} px⁻²\n"
            f"  K_Vmin  = {K_Vmin:.4f}\n"
            f"  K_gpeak = {K_gpeak:.4f}\n"
            f"  K_ds    = {K_ds_val:.4f}\n\n"
            f"Quality gate (damped sine):\n"
            f"  R² = {_R2:.3f}  {_flag}\n"
            f"  A={_A_ds:.3f} ξ={_xi_ds:.1f} λ={_lam_ds:.1f}\n\n"
            f"{'━'*42}"
        )
        ax.text(0.05, 0.5, summary_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='center', fontfamily='monospace', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=_box_color,
                          edgecolor='black', linewidth=1.5, alpha=0.95))

        # --- Row 4: Damped sine quality gate ---

        _reliable = getattr(c, 'reliable', None)
        _R2_val = getattr(c, 'R2_damped', np.nan)
        _A_ds_val = getattr(c, 'A_damped', np.nan)
        _xi_ds_val = getattr(c, 'xi_damped', np.nan)
        _lam_ds_val = getattr(c, 'lambda_damped', np.nan)

        signal_gr = c.g_r - 1.0

        def _step_response_plot(r_arr, A, xi, lam, r_excl, phi):
            H = 1.0 / (1.0 + np.exp(-(r_arr - r_excl) / 0.3))
            t = np.maximum(r_arr - r_excl, 0.0)
            osc = -A * np.exp(-t / xi) * np.sin(2 * np.pi * t / lam + phi)
            return H * osc + (1.0 - H) * (-1.0)

        # Use stored QC fit parameters
        _popt_p = getattr(c, 'popt_qc', None)
        if _popt_p is not None:
            _fitted_curve = _step_response_plot(r, *_popt_p)
            _residuals = signal_gr - _fitted_curve
        else:
            _fitted_curve = None
            _residuals = None

        # 4.1 Damped sine fit on g(r)-1
        ax = axes[3, 0]
        ax.plot(r, signal_gr, '.', color='steelblue', markersize=4, alpha=0.5, label='g(r)−1')
        if _fitted_curve is not None:
            ax.plot(r, _fitted_curve, '-', color='red', lw=2.5,
                    label=f'Step response (R²={_R2_val:.3f})')
            # envelope (from oscillatory component)
            A_p, xi_p, lam_p, r_excl_p, phi_p = _popt_p
            r_dense = np.linspace(r_excl_p, r[-1], 300)
            t_dense = r_dense - r_excl_p
            env_upper = A_p * np.exp(-t_dense / xi_p)
            env_lower = -A_p * np.exp(-t_dense / xi_p)
            ax.plot(r_dense, env_upper, '--', color='red', alpha=0.3)
            ax.plot(r_dense, env_lower, '--', color='red', alpha=0.3)
        ax.axhline(0, color='k', ls='--', alpha=0.3)
        ax.set_xlabel('r (pixels)', fontsize=12, fontweight='bold')
        ax.set_ylabel('g(r) − 1', fontsize=12, fontweight='bold')
        ax.set_title('Step 8: Damped Sine Fit (Quality Gate)',
                     fontsize=13, fontweight='bold', pad=8)
        ax.legend(fontsize=9, loc='upper right')
        ax.set_xlim(0, r.max())
        sns.despine(ax=ax)

        # 4.2 Residuals
        ax = axes[3, 1]
        if _residuals is not None:
            ax.plot(r, _residuals, '.', color='gray', markersize=4, alpha=0.5)
            res_std = np.std(_residuals)
            ax.axhspan(-res_std, res_std, alpha=0.15, color='green', label=f'±σ = {res_std:.3f}')
            ax.axhspan(-2*res_std, 2*res_std, alpha=0.05, color='green')
        ax.axhline(0, color='k', ls='--', alpha=0.3)
        ax.set_xlabel('r (pixels)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Residual', fontsize=12, fontweight='bold')
        ax.set_title('Step 9: Damped Sine Residuals',
                     fontsize=13, fontweight='bold', pad=8)
        ax.legend(fontsize=9)
        ax.set_xlim(0, r.max())
        sns.despine(ax=ax)

        # 4.3 Quality gate verdict
        ax = axes[3, 2]
        ax.axis('off')
        _flag_text = "✅ RELIABLE" if _reliable else "❌ UNRELIABLE" if _reliable is not None else "N/A"
        _verdict_color = '#2ECC71' if _reliable else '#E74C3C'
        _has_peak = getattr(c, 'has_peak', False)
        _has_cross = getattr(c, 'has_crossing', False)
        _has_trough = getattr(c, 'has_trough', False)
        _snr_val = getattr(c, 'SNR', 0.0)
        _acf1_val = getattr(c, 'ACF1', 1.0)
        verdict_text = (
            f"{'━'*42}\n"
            f"    QUALITY GATE VERDICT\n"
            f"{'━'*42}\n\n"
            f"  {_flag_text}\n\n"
            f"Damped sine params:\n"
            f"  R²={_R2_val:.3f} A={_A_ds_val:.3f}\n"
            f"  ξ={_xi_ds_val:.1f}px λ={_lam_ds_val:.1f}px\n\n"
            f"Form: peak={'Y' if _has_peak else 'N'}"
            f" cross={'Y' if _has_cross else 'N'}"
            f" trough={'Y' if _has_trough else 'N'}\n"
            f"Params: ξ<95 {'Y' if _xi_ds_val<95 else 'N'}"
            f" λ<50 {'Y' if _lam_ds_val<50 else 'N'}\n\n"
            f"Noise analysis:\n"
            f"  SNR  = {_snr_val:.2f}\n"
            f"  ACF1 = {_acf1_val:.3f}\n"
            f"  White noise: {'Y' if abs(_acf1_val)<0.4 else 'N'}\n\n"
            f"Gate: form+params AND\n"
            f"  (R²>0.5 OR\n"
            f"   R²>0.2+white+SNR>1.2)\n\n"
            f"{'━'*42}"
        )
        _vbox_color = '#D5F5E3' if _reliable else '#FADBD8'
        ax.text(0.05, 0.5, verdict_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='center', fontfamily='monospace', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=_vbox_color,
                          edgecolor=_verdict_color, linewidth=2.5, alpha=0.95))

        plt.suptitle('Complete Collective Order Analysis', fontsize=16, fontweight='bold', y=1.01)
        plt.tight_layout()
        if save:
            self._save_fig(fig, '05_comprehensive')
        plt.show()

    # -----------------------------------------------------------------------
    # 6. PUBLICATION SINGLE PANELS
    # -----------------------------------------------------------------------

    def publication_gr(self, save=None):
        """Single-panel publication-quality g(r) plot."""
        self._check_attr('r_values', 'g_r', 'g_r_smooth')
        save = save if save is not None else self.save

        c = self.c
        r = c.r_values
        peak_idx = np.argmax(c.g_r_smooth)
        r_peak = r[peak_idx]
        g_peak = c.g_r_smooth[peak_idx]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(r, c.g_r, '.', color=COLORS['raw'], markersize=4, alpha=0.4, label='Raw data')
        ax.plot(r, c.g_r_smooth, '-', color=COLORS['smooth'], linewidth=3,
                label='Savitzky-Golay filter')
        ax.axhline(y=1, color=COLORS['neutral'], linestyle='--', linewidth=2.5, label='g(r) = 1')
        ax.plot(r_peak, g_peak, 'o', color=COLORS['fit'], markersize=14,
                markeredgecolor='black', markeredgewidth=2, zorder=5,
                label=f'First peak: r = {r_peak:.0f} px')
        ax.set_xlabel('r (pixels)', fontsize=16, fontweight='bold')
        ax.set_ylabel('g(r)', fontsize=16, fontweight='bold')
        ax.set_title('Radial Distribution Function', fontsize=18, fontweight='bold', pad=15)
        ax.set_xlim(0, r.max())
        ax.set_ylim(0, max(2.2, c.g_r_smooth.max() * 1.1))
        ax.tick_params(axis='both', labelsize=14)
        ax.legend(fontsize=12, loc='upper right', framealpha=0.95)
        ax.yaxis.grid(True, alpha=0.3, linewidth=0.8)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)
        plt.tight_layout()
        if save:
            self._save_fig(fig, '06_publication_gr')
        plt.show()

    def publication_vr(self, save=None, zoom_max=80):
        """Single-panel publication-quality V(r) with fit."""
        self._check_attr('r_valid', 'v_r_valid', 'r0_fit', 'K')
        save = save if save is not None else self.save

        c = self.c
        r_v = c.r_valid
        v = c.v_r_valid
        zoom = r_v <= zoom_max
        fc = self._compute_fit_curve()

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(r_v[zoom], v[zoom], '-', color=COLORS['smooth'], linewidth=3, label='Smoothed V(r)')

        # Overlay fitted curve (clipped to zoom range)
        fit_zoom = fc['r_dense'] <= zoom_max
        ax.plot(fc['r_dense'][fit_zoom], fc['v_curve'][fit_zoom], '-',
                color=COLORS['fit'], linewidth=3, label=fc['fit_label'])

        ax.axhline(y=0, color=COLORS['neutral'], linestyle='--', linewidth=2.5)
        ax.axvline(x=c.r0_fit, color=COLORS['reference'], linestyle=':', linewidth=2.5,
                   label=r'r$_0$ = ' + f'{c.r0_fit:.1f} px')

        # Marker at minimum of the fitted curve
        v_at_r0 = np.min(v[:len(v)//2])
        ax.plot(c.r0_fit, v_at_r0, 'o', color=COLORS['fit'],
                markersize=14, markeredgecolor='black', markeredgewidth=2, zorder=5)

        ax.set_xlabel('r (pixels)', fontsize=16, fontweight='bold')
        ax.set_ylabel('V(r) = -ln(g(r))', fontsize=16, fontweight='bold')
        method_name = fc['method'].capitalize()
        ax.set_title(f'Effective Potential — {method_name} (K = {c.K:.3f} ' + r'px$^{-2}$)',
                     fontsize=18, fontweight='bold', pad=15)
        ax.set_xlim(0, zoom_max)
        ax.set_ylim(-1.2, 1.5)
        ax.tick_params(axis='both', labelsize=14)
        ax.legend(fontsize=11, loc='upper right', framealpha=0.95)
        ax.yaxis.grid(True, alpha=0.3, linewidth=0.8)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)
        plt.tight_layout()
        if save:
            self._save_fig(fig, '07_publication_vr')
        plt.show()

    # -----------------------------------------------------------------------
    # PUBLICATION: Pipeline Figure (for paper)
    # -----------------------------------------------------------------------
    # Usage:
    #   plotter = processor.plot(results, save=True, save_dir='figures')
    #   plotter.pipeline_figure()
    #
    # Layout: 2 rows × 3 columns, 190 mm wide, 600 DPI
    # (a) Raw specular image  (b) Segmentation overlay  (c) Centroids + interior window
    # (d) g(r)                (e) V(r)                  (f) Quadratic fit → K, r₀

    def _add_scale_bar(self, ax, pixel_size, bar_um=50, color='white',
                       fontsize=7, loc='lower right', pad=10, height=4):
        """Draw a scale bar on an image axis.

        Parameters
        ----------
        ax : matplotlib Axes
        pixel_size : float – µm per pixel
        bar_um : float – desired bar length in µm
        color : str – bar and text color
        loc : str – 'lower right' or 'lower left'
        pad : int – padding from edge in pixels
        height : int – bar thickness in pixels
        """
        bar_px = bar_um / pixel_size
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        if 'right' in loc:
            x0 = xlim[1] - pad - bar_px
        else:
            x0 = xlim[0] + pad
        y0 = max(ylim) - pad  # near bottom

        ax.add_patch(plt.Rectangle((x0, y0 - height), bar_px, height,
                                    facecolor=color, edgecolor='none', zorder=10))
        ax.text(x0 + bar_px / 2, y0 - height - 4, f'{bar_um} µm',
                color=color, fontsize=fontsize, fontweight='bold',
                ha='center', va='bottom', zorder=10)

    def pipeline_figure(self, save=None, zoom_gr=80):
        """Publication-quality pipeline figure (3×3, 190 mm wide, 600 DPI).

        Row 1: (a) Raw image    | (b) Segmentation  | (c) Centroids
        Row 2: (d) g(r) + fit   | (e) V(r) + range  | (f) Form check
        Row 3: (g) Raw V(r) fit | (h) Guided V(r)   | (i) All 5 methods
        """
        self._check_attr('r_values', 'g_r', 'g_r_smooth',
                         'r_valid', 'v_r_valid', 'r0_fit', 'K',
                         'seg_labels', 'cell_area')
        save = save if save is not None else self.save

        c = self.c
        px = c.exclusion_ratio

        # --- Publication style overrides ---
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
        })

        # 190 mm wide → inches
        fig_w = 190 / 25.4
        fig_h = fig_w * 0.85
        fig = plt.figure(figsize=(fig_w, fig_h))

        # Two independent GridSpec blocks for precise vertical control
        # Row 1: images (top 45% of figure)
        gs_top = fig.add_gridspec(1, 3,
                                  left=0.08, right=0.97, top=0.97, bottom=0.55,
                                  wspace=0.35)
        # Rows 2-3: plots (bottom 50% of figure, with internal gap)
        gs_bot = fig.add_gridspec(2, 3,
                                  height_ratios=[1, 1],
                                  left=0.08, right=0.97, top=0.609, bottom=0.189,
                                  hspace=0.45, wspace=0.35)

        axes = np.empty((3, 3), dtype=object)
        for j in range(3):
            axes[0, j] = fig.add_subplot(gs_top[0, j])
            axes[1, j] = fig.add_subplot(gs_bot[0, j])
            axes[2, j] = fig.add_subplot(gs_bot[1, j])

        # --- Precompute ---
        centroids = c.seg_centroids
        y_coords, x_coords = centroids[:, 0], centroids[:, 1]
        cell_H, cell_W = c.H, c.W
        MAX_R = int(min(cell_H, cell_W) * px)
        interior = ((y_coords >= MAX_R) & (y_coords <= cell_H - MAX_R) &
                     (x_coords >= MAX_R) & (x_coords <= cell_W - MAX_R))

        r = c.r_values
        r_v = c.r_valid
        v = c.v_r_valid

        end_search = len(r_v) // 2
        v_min_idx = np.argmin(v[:end_search])
        fc = self._compute_fit_curve()

        # Colors
        C_RAW = '#0072B2'
        C_SMOOTH = '#D55E00'
        C_FIT = '#009E73'
        C_GRAY = '#999999'
        C_DARK = '#4A4A4A'
        C_INT = '#56B4E9'
        C_YELLOW = '#F0E442'
        C_RED = '#E74C3C'

        labels = [chr(97+i) for i in range(9)]

        def _panel_label(ax, label):
            ax.set_title('', loc='center')
            ax.set_title(label, fontweight='bold', fontsize=10, loc='left', pad=4)

        # =====================================================================
        # ROW 1: Image processing
        # =====================================================================

        # (a) Raw specular microscopy image (brightness-stretched for print)
        ax = axes[0, 0]
        img_a = c.cell_area.astype(float)
        p2, p98 = np.percentile(img_a, (2, 98))
        img_a_stretched = np.clip((img_a - p2) / (p98 - p2 + 1e-8), 0, 1)
        ax.imshow(img_a_stretched, cmap='gray')
        ax.axis('off')
        _panel_label(ax, labels[0])

        # (b) Segmentation (overlay on raw image)
        ax = axes[0, 1]
        seg_labels = c.seg_labels
        n_labels = seg_labels.max()
        # Darken the base image so colored cells pop
        ax.imshow(c.cell_area, cmap='gray', vmax=np.percentile(c.cell_area, 99) * 0.6)
        masked_labels = np.ma.masked_where(seg_labels == 0, seg_labels)
        # Shuffle colormap to avoid adjacent cells sharing a hue
        rng = np.random.default_rng(42)
        n_colors = max(n_labels, 20)
        base_colors = plt.cm.hsv(np.linspace(0, 1, n_colors, endpoint=False))
        base_colors[:, 3] = 1.0  # full opacity in the map
        idx = np.arange(n_colors); rng.shuffle(idx)
        shuffled_cmap = ListedColormap(base_colors[idx])
        ax.imshow(masked_labels, cmap=shuffled_cmap, alpha=0.55, interpolation='nearest')
        ax.axis('off')
        _panel_label(ax, labels[1])

        # (c) Centroids + interior window + g(r) annuli illustration
        ax = axes[0, 2]
        ax.imshow(img_a_stretched, cmap='gray')
        ax.scatter(x_coords[~interior], y_coords[~interior],
                   s=6, c=C_GRAY, alpha=0.6, edgecolor='none')
        ax.scatter(x_coords[interior], y_coords[interior],
                   s=8, c=C_INT, alpha=0.9, edgecolor='black', linewidths=0.3)
        rect = plt.Rectangle((MAX_R, MAX_R), cell_W - 2*MAX_R, cell_H - 2*MAX_R,
                              fill=False, edgecolor=C_SMOOTH, linestyle='--',
                              linewidth=0.8, alpha=0.5)
        ax.add_patch(rect)

        # --- g(r) annuli: show how pair correlation is computed ---
        from matplotlib.patches import Annulus
        r0_px = c.r0_fit  # equilibrium distance in pixels
        dr = r0_px * 0.35  # annulus width
        ring_radii = [r0_px, 3 * r0_px]  # wider separation between shells
        ring_colors = ['#FF8C00', '#FF2200']  # bright orange, bright red
        ring_alphas = [0.35, 0.30]

        # Select 2 well-separated interior cells, away from center
        int_idx = np.where(interior)[0]
        int_x, int_y = x_coords[int_idx], y_coords[int_idx]

        # Cell 1: offset from center toward upper-left quadrant
        img_cx, img_cy = cell_W * 0.3, cell_H * 0.3
        d_target1 = np.sqrt((int_x - img_cx)**2 + (int_y - img_cy)**2)
        c1_loc = np.argmin(d_target1)
        c1_idx = int_idx[c1_loc]

        # Cell 2: offset toward lower-right, at least 6×r₀ from cell 1
        img_cx2, img_cy2 = cell_W * 0.7, cell_H * 0.7
        d_target2 = np.sqrt((int_x - img_cx2)**2 + (int_y - img_cy2)**2)
        d_to_c1 = np.sqrt((int_x - int_x[c1_loc])**2 + (int_y - int_y[c1_loc])**2)
        far = d_to_c1 > 6 * r0_px
        if far.any():
            c2_loc = np.where(far)[0][np.argmin(d_target2[far])]
        else:
            c2_loc = np.argmax(d_to_c1)
        c2_idx = int_idx[c2_loc]

        # Draw annuli and highlight cells for each reference cell
        label_angles = [50, -130]
        for ci, cidx in enumerate([c1_idx, c2_idx]):
            cx_c, cy_c = x_coords[cidx], y_coords[cidx]

            # Green center marker
            ax.scatter(cx_c, cy_c, s=45, c='#009E73', edgecolor='white',
                       linewidths=1.2, zorder=10)

            for ri, (radius, col, alph) in enumerate(zip(ring_radii, ring_colors, ring_alphas)):
                # Filled annulus with bright edge
                ann = Annulus((cx_c, cy_c), radius + dr/2, dr,
                              facecolor=col, alpha=alph,
                              edgecolor=col, linewidth=1.5, zorder=6)
                ax.add_patch(ann)

                # Find and highlight cells in this shell
                dists = np.sqrt((x_coords - cx_c)**2 + (y_coords - cy_c)**2)
                in_ring = (dists >= radius - dr/2) & (dists <= radius + dr/2)
                n_ring = int(in_ring.sum())
                if n_ring > 0:
                    ax.scatter(x_coords[in_ring], y_coords[in_ring],
                               s=14, c=col, edgecolor='white',
                               linewidths=0.4, zorder=8)

                # Count label
                ang = np.radians(label_angles[ci] + ri * 50)
                lx = cx_c + (radius + dr * 1.2) * np.cos(ang)
                ly = cy_c + (radius + dr * 1.2) * np.sin(ang)
                ax.text(lx, ly, f'n={n_ring}', fontsize=6.5,
                        fontweight='bold', color=col, ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.12', facecolor='white',
                                  alpha=0.8, edgecolor='none'), zorder=9)

        ax.set_xlim(0, cell_W)
        ax.set_ylim(cell_H, 0)
        ax.axis('off')
        _panel_label(ax, labels[2])

        # Scale bars on image panels
        pixel_size = getattr(c, 'pixel_size', 0.58)
        self._add_scale_bar(axes[0, 0], pixel_size, bar_um=50, color='white')
        self._add_scale_bar(axes[0, 1], pixel_size, bar_um=50, color='white')
        self._add_scale_bar(axes[0, 2], pixel_size, bar_um=50, color='white')

        # =====================================================================
        # ROW 2: Quality gate on g(r)
        # =====================================================================
        pixel_size = getattr(c, 'pixel_size', 0.58)
        px2 = pixel_size ** 2
        signal_gr = c.g_r - 1.0
        popt_qc = getattr(c, 'popt_qc', None)
        _R2_val = getattr(c, 'R2_damped', np.nan)
        _R2_full = getattr(c, 'R2_full', np.nan)
        _reliable = getattr(c, 'reliable', False)
        _K_ds = getattr(c, 'K_ds', np.nan)
        _snr = getattr(c, 'SNR', 0.0)
        _acf1 = getattr(c, 'ACF1', 1.0)

        def _step_response_fig(r_arr, A, xi, lam, r_excl, phi):
            H = 1.0 / (1.0 + np.exp(-(r_arr - r_excl) / 0.3))
            t = np.maximum(r_arr - r_excl, 0.0)
            osc = -A * np.exp(-t / xi) * np.sin(2 * np.pi * t / lam + phi)
            return H * osc + (1.0 - H) * (-1.0)

        def morse_fig(r_arr, D_e, a, r_0, offset):
            return D_e * (1 - np.exp(-a * (r_arr - r_0)))**2 + offset

        # (d) g(r) + step response fit
        ax = axes[1, 0]
        zoom = r <= zoom_gr
        ax.plot(r[zoom], c.g_r[zoom], '.', color=C_RAW, markersize=2, alpha=0.4)
        if popt_qc is not None:
            r_dense = np.linspace(r[0], zoom_gr, 500)
            g_fit = 1.0 + _step_response_fig(r_dense, *popt_qc)
            ax.plot(r_dense, g_fit, '-', color=C_RED, lw=2,
                    label=f'Step response (R$^2_{{osc}}$={_R2_val:.2f})')
        ax.axhline(y=1, color=C_DARK, linestyle='--', linewidth=1)
        ax.set_xlabel('r (px)', fontweight='bold')
        ax.set_ylabel('g(r)', fontweight='bold')
        ax.set_xlim(0, zoom_gr)
        ax.set_ylim(0, max(2.2, c.g_r[zoom].max() * 1.1))
        ax.legend(fontsize=6, loc='upper right', framealpha=0.9)
        ax.yaxis.grid(True, alpha=0.2, linewidth=0.5)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)
        _panel_label(ax, labels[3])

        # (e) Smooth V(r) from step response + boundaries
        ax = axes[1, 1]
        zoom_v = r_v <= zoom_gr
        ax.plot(r_v[zoom_v], v[zoom_v], '-', color=C_GRAY, linewidth=0.8, alpha=0.5, label='V(r) raw')
        if popt_qc is not None:
            r_dense_v = np.linspace(r[0], zoom_gr, 500)
            g_smooth = 1.0 + _step_response_fig(r_dense_v, *popt_qc)
            g_smooth = np.maximum(g_smooth, 1e-10)
            V_smooth = -np.log(g_smooth)
            ax.plot(r_dense_v, V_smooth, '-', color=C_RED, lw=2, label='V(r) from fit')
            # Show guided boundaries
            r_fit_guided = getattr(c, 'r_fit_guided', np.array([]))
            if len(r_fit_guided) > 0:
                ax.axvspan(r_fit_guided[0], min(r_fit_guided[-1], zoom_gr),
                           alpha=0.1, color=C_FIT, label='Guided region')
            # K_ds minimum — offset right so it doesn't blend into the curve
            V_min_idx = np.argmin(V_smooth[:len(V_smooth)//2])
            ax.plot(r_dense_v[V_min_idx] + 4, V_smooth[V_min_idx], 'o',
                    color=C_FIT, markersize=7, markeredgecolor='black',
                    markeredgewidth=1, zorder=5)
            K_ds_um = _K_ds / px2 if not np.isnan(_K_ds) else np.nan
            if not np.isnan(K_ds_um):
                ax.text(r_dense_v[V_min_idx] + 8, V_smooth[V_min_idx] + 0.08,
                        f'$K_{{ds}}$={K_ds_um:.4f}', fontsize=7, fontweight='bold',
                        color=C_FIT)
        ax.axhline(y=0, color=C_DARK, linestyle='--', linewidth=1)
        ax.set_xlabel('r (px)', fontweight='bold')
        ax.set_ylabel('V(r)', fontweight='bold')
        ax.set_xlim(0, zoom_gr)
        ax.set_ylim(-1.2, 1.5)
        ax.legend(fontsize=6, loc='upper right', framealpha=0.9)
        ax.yaxis.grid(True, alpha=0.2, linewidth=0.5)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)
        _panel_label(ax, labels[4])

        # (f) Oscillatory form check — visual quality gate
        ax = axes[1, 2]
        if popt_qc is not None:
            A_val, xi_val, lam_val, r_excl_val, phi_val = popt_qc
            r_start = max(0, r_excl_val - 3)
            r_osc = np.linspace(r_excl_val + 0.5, zoom_gr, 500)
            g_osc = _step_response_fig(r_osc, *popt_qc)  # this is g(r)-1

            ax.fill_between(r_osc, 0, g_osc, where=(g_osc > 0),
                            alpha=0.15, color=C_FIT, interpolate=True)
            ax.fill_between(r_osc, 0, g_osc, where=(g_osc < 0),
                            alpha=0.15, color=C_RED, interpolate=True)
            ax.plot(r_osc, g_osc, '-', color=C_DARK, lw=1.8)
            ax.axhline(y=0, color=C_DARK, linestyle='--', linewidth=0.8)

            # Find form check features
            peak_idx = np.argmax(g_osc)
            trough_idx = np.argmin(g_osc[peak_idx:]) + peak_idx

            # Zero crossing between peak and trough
            sign_change = np.where(np.diff(np.sign(g_osc[peak_idx:trough_idx])))[0]
            if len(sign_change) > 0:
                zc_idx = sign_change[0] + peak_idx
            else:
                zc_idx = (peak_idx + trough_idx) // 2

            peak_ok = g_osc[peak_idx] > 0.02
            trough_ok = g_osc[trough_idx] < -0.01
            zc_ok = len(sign_change) > 0
            form_ok = peak_ok and zc_ok and trough_ok

            # Annotate peak
            ax.plot(r_osc[peak_idx], g_osc[peak_idx], 'v', color=C_FIT,
                    markersize=8, markeredgecolor='black', markeredgewidth=0.8, zorder=6)
            tick_p = '\u2713' if peak_ok else '\u2717'
            ax.annotate(f'Peak {tick_p}', xy=(r_osc[peak_idx], g_osc[peak_idx]),
                        xytext=(5, 6), textcoords='offset points',
                        fontsize=6.5, fontweight='bold', color=C_FIT)

            # Annotate zero crossing
            ax.axvline(x=r_osc[zc_idx], color=C_GRAY, linestyle=':', linewidth=1, zorder=3)
            tick_z = '\u2713' if zc_ok else '\u2717'
            ax.annotate(f'Zero {tick_z}', xy=(r_osc[zc_idx], 0),
                        xytext=(4, -4), textcoords='offset points',
                        fontsize=6.5, fontweight='bold', color=C_DARK)

            # Annotate trough
            ax.plot(r_osc[trough_idx], g_osc[trough_idx], '^', color=C_RED,
                    markersize=8, markeredgecolor='black', markeredgewidth=0.8, zorder=6)
            tick_t = '\u2713' if trough_ok else '\u2717'
            ax.annotate(f'Trough {tick_t}', xy=(r_osc[trough_idx], g_osc[trough_idx]),
                        xytext=(-8, -14), textcoords='offset points',
                        fontsize=6.5, fontweight='bold', color=C_RED)

            # --- Compute all four quality gate checks ---
            params_ok = (xi_val < 95) and (8 < lam_val < 70)
            peak_height = np.max(c.g_r)
            peak_h_ok = peak_height > 1.10
            fit_ok = (_R2_val > 0.5) or (_R2_val > 0.2 and _snr > 1.2 and abs(_acf1) < 0.4)

            # 4-row checklist at top right
            checks = [
                ('Form',   f'pk\u2192zero\u2192tr',              form_ok),
                ('Params', f'\u03be={xi_val:.1f} \u03bb={lam_val:.1f}', params_ok),
                ('Peak',   f'max={peak_height:.2f}',             peak_h_ok),
                ('Fit',    f'R\u00b2={_R2_val:.2f} SNR={_snr:.1f}', fit_ok),
            ]
            checklist_lines = []
            for name, val, ok in checks:
                tick = '\u2713' if ok else '\u2717'
                checklist_lines.append(f'{name:6s} {val}  {tick}')
            checklist_text = '\n'.join(checklist_lines)

            # Overall verdict
            all_pass = form_ok and params_ok and peak_h_ok and fit_ok
            verdict = 'PASS' if all_pass else 'FAIL'
            v_color = C_FIT if all_pass else C_RED

            ax.text(0.97, 0.97, f'{verdict}\n' + checklist_text,
                    transform=ax.transAxes, fontsize=5.5, fontfamily='monospace',
                    fontweight='bold', color=C_DARK,
                    ha='right', va='top', zorder=10,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor=v_color, linewidth=1.5, alpha=0.9))

            ax.set_xlim(r_start, zoom_gr)
        else:
            ax.set_xlim(0, zoom_gr)

        ax.set_xlabel('r (px)', fontweight='bold')
        ax.set_ylabel('g(r) \u2212 1', fontweight='bold')
        ax.yaxis.grid(True, alpha=0.2, linewidth=0.5)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)
        _panel_label(ax, labels[5])

        # =====================================================================
        # ROW 3: V(r) fitting — 5 methods comparison (panels g, h, i)
        # =====================================================================
        # Colorblind-friendly palette (Okabe-Ito) — locked for reuse in Fig. 3
        C_QR = '#0072B2'    # quad raw - blue
        C_MR = '#56B4E9'    # morse raw - sky blue
        C_QG = '#009E73'    # quad guided - green
        C_MG = '#E69F00'    # morse guided - amber
        C_DS = '#CC79A7'    # DS (ours) - reddish purple

        coeffs_qr = getattr(c, 'coeffs_qr', None)
        coeffs_qg = getattr(c, 'coeffs_qg', None)
        popt_mr = getattr(c, 'popt_mr', None)
        popt_mg = getattr(c, 'popt_mg', None)
        r_fit_raw = getattr(c, 'r_fit_raw', np.array([]))
        v_fit_raw = getattr(c, 'v_fit_raw', np.array([]))
        r_fit_guided = getattr(c, 'r_fit_guided', np.array([]))
        v_fit_guided = getattr(c, 'v_fit_guided', np.array([]))

        K_qr = getattr(c, 'K_quad_raw', np.nan)
        K_mr = getattr(c, 'K_morse_raw', np.nan)
        K_qg = getattr(c, 'K_quad_guided', np.nan)
        K_mg = getattr(c, 'K_morse_guided', np.nan)
        K_ds_px = getattr(c, 'K_ds', np.nan)

        # (g) Raw region: Quad raw + Morse raw
        ax = axes[2, 0]
        ax.plot(r_v[zoom_v], v[zoom_v], '-', color=C_GRAY, lw=0.8, alpha=0.4)
        if len(r_fit_raw) > 0:
            ax.axvspan(r_fit_raw[0], r_fit_raw[-1], alpha=0.08, color=C_QR)
            ax.plot(r_fit_raw, v_fit_raw, 'o', color=C_QR, markersize=3, alpha=0.5)
        if coeffs_qr is not None:
            rd = np.linspace(r_fit_raw[0], r_fit_raw[-1], 200)
            ax.plot(rd, np.polyval(coeffs_qr, rd), '-', color=C_QR, lw=2,
                    label=f'Quad ({K_qr/px2:.4f})')
        if popt_mr is not None and len(r_fit_raw) > 0:
            rd = np.linspace(r_fit_raw[0], r_fit_raw[-1], 200)
            ax.plot(rd, morse_fig(rd, *popt_mr), '-', color=C_MR, lw=2,
                    label=f'Morse ({K_mr/px2:.4f})')
        ax.axhline(0, color=C_DARK, ls='--', lw=0.8)
        ax.set_xlabel('r (px)', fontweight='bold')
        ax.set_ylabel('V(r)', fontweight='bold')
        ax.set_xlim(0, zoom_gr)
        ax.set_ylim(-1.2, 1.5)
        ax.legend(fontsize=6, loc='upper right', framealpha=0.9)
        ax.yaxis.grid(True, alpha=0.2, linewidth=0.5)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)
        _panel_label(ax, labels[6])

        # (h) Guided region: Quad guided + Morse guided
        ax = axes[2, 1]
        ax.plot(r_v[zoom_v], v[zoom_v], '-', color=C_GRAY, lw=0.8, alpha=0.4)
        if len(r_fit_guided) > 0:
            ax.axvspan(r_fit_guided[0], min(r_fit_guided[-1], zoom_gr),
                       alpha=0.08, color=C_QG)
            ax.plot(r_fit_guided, v_fit_guided, 'o', color=C_QG, markersize=3, alpha=0.5)
        if coeffs_qg is not None:
            rd = np.linspace(r_fit_guided[0], r_fit_guided[-1], 200)
            ax.plot(rd, np.polyval(coeffs_qg, rd), '-', color=C_QG, lw=2,
                    label=f'Quad ({K_qg/px2:.4f})')
        if popt_mg is not None and len(r_fit_guided) > 0:
            rd = np.linspace(r_fit_guided[0], min(r_fit_guided[-1], zoom_gr), 200)
            ax.plot(rd, morse_fig(rd, *popt_mg), '-', color=C_MG, lw=2,
                    label=f'Morse ({K_mg/px2:.4f})')
        ax.axhline(0, color=C_DARK, ls='--', lw=0.8)
        ax.set_xlabel('r (px)', fontweight='bold')
        ax.set_ylabel('V(r)', fontweight='bold')
        ax.set_xlim(0, zoom_gr)
        ax.set_ylim(-1.2, 1.5)
        ax.legend(fontsize=6, loc='upper right', framealpha=0.9)
        ax.yaxis.grid(True, alpha=0.2, linewidth=0.5)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)
        _panel_label(ax, labels[7])

        # (i) All 5 overlaid
        ax = axes[2, 2]
        ax.plot(r_v[zoom_v], v[zoom_v], '-', color=C_GRAY, lw=0.8, alpha=0.3)
        if popt_qc is not None:
            r_dense_all = np.linspace(r[0], zoom_gr, 500)
            g_ds_all = 1.0 + _step_response_fig(r_dense_all, *popt_qc)
            g_ds_all = np.maximum(g_ds_all, 1e-10)
            v_ds_all = -np.log(g_ds_all)
            ax.plot(r_dense_all, v_ds_all, '-', color=C_DS, lw=2.5, label=f'DS ({K_ds_px/px2:.4f})')
        if coeffs_qr is not None and len(r_fit_raw) > 0:
            rd = np.linspace(r_fit_raw[0], r_fit_raw[-1], 200)
            ax.plot(rd, np.polyval(coeffs_qr, rd), '-', color=C_QR, lw=1.2, alpha=0.7,
                    label=f'QR ({K_qr/px2:.4f})')
        if popt_mr is not None and len(r_fit_raw) > 0:
            rd = np.linspace(r_fit_raw[0], r_fit_raw[-1], 200)
            ax.plot(rd, morse_fig(rd, *popt_mr), '-', color=C_MR, lw=1.2, alpha=0.7,
                    label=f'MR ({K_mr/px2:.4f})')
        if coeffs_qg is not None and len(r_fit_guided) > 0:
            rd = np.linspace(r_fit_guided[0], r_fit_guided[-1], 200)
            ax.plot(rd, np.polyval(coeffs_qg, rd), '-', color=C_QG, lw=1.2, alpha=0.7,
                    label=f'QG ({K_qg/px2:.4f})')
        if popt_mg is not None and len(r_fit_guided) > 0:
            rd = np.linspace(r_fit_guided[0], min(r_fit_guided[-1], zoom_gr), 200)
            ax.plot(rd, morse_fig(rd, *popt_mg), '-', color=C_MG, lw=1.2, alpha=0.7,
                    label=f'MG ({K_mg/px2:.4f})')
        ax.axhline(0, color=C_DARK, ls='--', lw=0.8)
        ax.set_xlabel('r (px)', fontweight='bold')
        ax.set_ylabel('V(r)', fontweight='bold')
        ax.set_xlim(0, zoom_gr)
        ax.set_ylim(-1.2, 1.5)
        ax.legend(fontsize=5, loc='upper right', framealpha=0.9)
        ax.yaxis.grid(True, alpha=0.2, linewidth=0.5)
        ax.set_axisbelow(True)
        sns.despine(ax=ax)
        _panel_label(ax, labels[8])

        # =====================================================================
        # Final layout
        # =====================================================================
        # Layout already set via GridSpec
        if save:
            self._save_fig(fig, 'pipeline_figure')
        plt.show()

    # -----------------------------------------------------------------------
    # DIAGNOSTIC: All methods comparison for a single image
    # -----------------------------------------------------------------------
    def diagnostic(self, save=None, zoom_gr=80):
        """Diagnostic: all 5 K methods compared for a single image.

        Layout 2×4:
          (a) g(r) + step response QC
          (b) V(r) + Quad raw (Yamamoto)
          (c) V(r) + Morse raw
          (d) V(r) + Quad guided
          (e) V(r) + Morse guided
          (f) V(r) + DS on V(r)
          (g) All 5 overlaid
          (h) Summary: K values + RMSE
        """
        self._check_attr('r_values', 'g_r', 'r_valid', 'v_r_valid')
        save = save if save is not None else self.save
        c = self.c
        r = c.r_values
        g = c.g_r
        r_v = c.r_valid
        v = c.v_r_valid
        pixel_size = getattr(c, 'pixel_size', 0.58)
        px2 = pixel_size ** 2

        img_name = Path(c.image_path).stem if hasattr(c, 'image_path') else 'Unknown'

        # Colors
        C_RAW = '#999999'
        C_QR = '#2196F3'    # quad raw - blue
        C_MR = '#03A9F4'    # morse raw - light blue
        C_QG = '#4CAF50'    # quad guided - green
        C_MG = '#FF9800'    # morse guided - orange
        C_DS = '#E91E63'    # DS - pink
        C_DATA = '#90CAF9'
        C_QC = '#9C27B0'    # step response - purple

        fig, axes = plt.subplots(2, 4, figsize=(20, 8))

        # --- Helper functions ---
        def _step_response_plot(r_arr, A, xi, lam, r_excl, phi):
            H = 1.0 / (1.0 + np.exp(-(r_arr - r_excl) / 0.3))
            t = np.maximum(r_arr - r_excl, 0.0)
            osc = -A * np.exp(-t / xi) * np.sin(2 * np.pi * t / lam + phi)
            return H * osc + (1.0 - H) * (-1.0)

        def _damped_sine_vr_plot(r_arr, A, xi, lam, r0):
            """DS on g(r)-1 — same model, displayed on g(r)-1 or derived to V(r)."""
            return A * np.exp(-(r_arr - r0) / xi) * np.cos(2 * np.pi * (r_arr - r0) / lam)

        def morse_plot(r_arr, D_e, a, r_0, offset):
            return D_e * (1 - np.exp(-a * (r_arr - r_0)))**2 + offset

        # --- Get stored fit params ---
        popt_qc = getattr(c, 'popt_qc', None)
        coeffs_qr = getattr(c, 'coeffs_qr', None)
        coeffs_qg = getattr(c, 'coeffs_qg', None)
        popt_mr = getattr(c, 'popt_mr', None)
        popt_mg = getattr(c, 'popt_mg', None)
        popt_ds = getattr(c, 'popt_ds', None)

        r_fit_raw = getattr(c, 'r_fit_raw', np.array([]))
        v_fit_raw = getattr(c, 'v_fit_raw', np.array([]))
        r_fit_guided = getattr(c, 'r_fit_guided', np.array([]))
        v_fit_guided = getattr(c, 'v_fit_guided', np.array([]))
        r_fit_ds = getattr(c, 'r_fit_ds', np.array([]))
        v_fit_ds = getattr(c, 'v_fit_ds', np.array([]))

        K_qr = getattr(c, 'K_quad_raw', np.nan) / px2 if hasattr(c, 'K_quad_raw') and not np.isnan(getattr(c, 'K_quad_raw', np.nan)) else np.nan
        K_mr = getattr(c, 'K_morse_raw', np.nan) / px2 if hasattr(c, 'K_morse_raw') and not np.isnan(getattr(c, 'K_morse_raw', np.nan)) else np.nan
        K_qg = getattr(c, 'K_quad_guided', np.nan) / px2 if hasattr(c, 'K_quad_guided') and not np.isnan(getattr(c, 'K_quad_guided', np.nan)) else np.nan
        K_mg = getattr(c, 'K_morse_guided', np.nan) / px2 if hasattr(c, 'K_morse_guided') and not np.isnan(getattr(c, 'K_morse_guided', np.nan)) else np.nan
        K_ds = getattr(c, 'K_ds', np.nan) / px2 if hasattr(c, 'K_ds') and not np.isnan(getattr(c, 'K_ds', np.nan)) else np.nan

        R2_qc = getattr(c, 'R2_damped', np.nan)
        reliable = getattr(c, 'reliable', False)
        snr = getattr(c, 'SNR', 0)
        acf1 = getattr(c, 'ACF1', 1)

        rmse_qr = getattr(c, 'rmse_quad_raw', np.nan)
        rmse_mr = getattr(c, 'rmse_morse_raw', np.nan)
        rmse_qg = getattr(c, 'rmse_quad_guided', np.nan)
        rmse_mg = getattr(c, 'rmse_morse_guided', np.nan)
        rmse_ds_val = getattr(c, 'rmse_ds', np.nan)

        zoom_v = r_v <= zoom_gr
        mask_r = r <= zoom_gr

        # ===== (a) g(r) + step response QC =====
        ax = axes[0, 0]
        ax.plot(r[mask_r], g[mask_r], '.', color=C_DATA, markersize=3, alpha=0.5)
        if popt_qc is not None:
            r_dense = np.linspace(r[0], zoom_gr, 500)
            g_fit = 1.0 + _step_response_plot(r_dense, *popt_qc)
            ax.plot(r_dense, g_fit, '-', color=C_QC, lw=2,
                    label=f'Step resp (R²={R2_qc:.2f})')
        ax.axhline(1, color='gray', ls='--', lw=0.8)
        ax.set_xlabel('r (px)'); ax.set_ylabel('g(r)')
        ax.set_title('(a) QC: Step Response', fontweight='bold', fontsize=9)
        ax.set_xlim(0, zoom_gr); ax.legend(fontsize=6)
        sns.despine(ax=ax)

        # ===== (b) V(r) + Quad raw =====
        ax = axes[0, 1]
        ax.plot(r_v[zoom_v], v[zoom_v], '-', color=C_RAW, lw=0.8, alpha=0.5)
        if len(r_fit_raw) > 0:
            ax.axvspan(r_fit_raw[0], r_fit_raw[-1], alpha=0.1, color=C_QR)
            ax.plot(r_fit_raw, v_fit_raw, 'o', color=C_QR, markersize=4, alpha=0.6)
        if coeffs_qr is not None:
            rd = np.linspace(r_fit_raw[0], r_fit_raw[-1], 200)
            ax.plot(rd, np.polyval(coeffs_qr, rd), '-', color=C_QR, lw=2.5,
                    label=f'Quad raw K={K_qr:.4f}')
        ax.axhline(0, color='gray', ls='--', lw=0.5)
        ax.set_xlabel('r (px)'); ax.set_ylabel('V(r)')
        ax.set_title('(b) Quad Raw (Yamamoto)', fontweight='bold', fontsize=9)
        ax.set_xlim(0, zoom_gr); ax.set_ylim(-1.2, 1.5); ax.legend(fontsize=6)
        sns.despine(ax=ax)

        # ===== (c) V(r) + Morse raw =====
        ax = axes[0, 2]
        ax.plot(r_v[zoom_v], v[zoom_v], '-', color=C_RAW, lw=0.8, alpha=0.5)
        if len(r_fit_raw) > 0:
            ax.axvspan(r_fit_raw[0], r_fit_raw[-1], alpha=0.1, color=C_MR)
            ax.plot(r_fit_raw, v_fit_raw, 'o', color=C_MR, markersize=4, alpha=0.6)
        if popt_mr is not None:
            rd = np.linspace(r_fit_raw[0], r_fit_raw[-1], 200)
            ax.plot(rd, morse_plot(rd, *popt_mr), '-', color=C_MR, lw=2.5,
                    label=f'Morse raw K={K_mr:.4f}')
        ax.axhline(0, color='gray', ls='--', lw=0.5)
        ax.set_xlabel('r (px)'); ax.set_ylabel('V(r)')
        ax.set_title('(c) Morse Raw', fontweight='bold', fontsize=9)
        ax.set_xlim(0, zoom_gr); ax.set_ylim(-1.2, 1.5); ax.legend(fontsize=6)
        sns.despine(ax=ax)

        # ===== (d) V(r) + Quad guided =====
        ax = axes[0, 3]
        ax.plot(r_v[zoom_v], v[zoom_v], '-', color=C_RAW, lw=0.8, alpha=0.5)
        if len(r_fit_guided) > 0:
            ax.axvspan(r_fit_guided[0], r_fit_guided[-1], alpha=0.1, color=C_QG)
            ax.plot(r_fit_guided, v_fit_guided, 'o', color=C_QG, markersize=4, alpha=0.6)
        if coeffs_qg is not None:
            rd = np.linspace(r_fit_guided[0], r_fit_guided[-1], 200)
            ax.plot(rd, np.polyval(coeffs_qg, rd), '-', color=C_QG, lw=2.5,
                    label=f'Quad guided K={K_qg:.4f}')
        ax.axhline(0, color='gray', ls='--', lw=0.5)
        ax.set_xlabel('r (px)'); ax.set_ylabel('V(r)')
        ax.set_title('(d) Quad Guided', fontweight='bold', fontsize=9)
        ax.set_xlim(0, zoom_gr); ax.set_ylim(-1.2, 1.5); ax.legend(fontsize=6)
        sns.despine(ax=ax)

        # ===== (e) V(r) + Morse guided =====
        ax = axes[1, 0]
        ax.plot(r_v[zoom_v], v[zoom_v], '-', color=C_RAW, lw=0.8, alpha=0.5)
        if len(r_fit_guided) > 0:
            ax.axvspan(r_fit_guided[0], r_fit_guided[-1], alpha=0.1, color=C_MG)
            ax.plot(r_fit_guided, v_fit_guided, 'o', color=C_MG, markersize=4, alpha=0.6)
        if popt_mg is not None:
            rd = np.linspace(r_fit_guided[0], r_fit_guided[-1], 200)
            ax.plot(rd, morse_plot(rd, *popt_mg), '-', color=C_MG, lw=2.5,
                    label=f'Morse guided K={K_mg:.4f}')
        ax.axhline(0, color='gray', ls='--', lw=0.5)
        ax.set_xlabel('r (px)'); ax.set_ylabel('V(r)')
        ax.set_title('(e) Morse Guided', fontweight='bold', fontsize=9)
        ax.set_xlim(0, zoom_gr); ax.set_ylim(-1.2, 1.5); ax.legend(fontsize=6)
        sns.despine(ax=ax)

        # ===== (f) DS = QC step response on g(r)-1 =====
        ax = axes[1, 1]
        ax.plot(r[mask_r], g[mask_r] - 1, '.', color=C_DATA, markersize=3, alpha=0.5)
        if popt_qc is not None:
            rd = np.linspace(r[0], zoom_gr, 500)
            ax.plot(rd, _step_response_plot(rd, *popt_qc), '-', color=C_DS, lw=2.5,
                    label=f'DS K={K_ds:.4f}')
        ax.axhline(0, color='gray', ls='--', lw=0.5)
        ax.set_xlabel('r (px)'); ax.set_ylabel('g(r)$-$1')
        ax.set_title('(f) DS on g(r)$-$1 → K from V(r)', fontweight='bold', fontsize=9)
        ax.set_xlim(0, zoom_gr); ax.legend(fontsize=6)
        sns.despine(ax=ax)

        # ===== (g) All 5 overlaid =====
        ax = axes[1, 2]
        ax.plot(r_v[zoom_v], v[zoom_v], '-', color=C_RAW, lw=0.8, alpha=0.3)
        if coeffs_qr is not None and len(r_fit_raw) > 0:
            rd = np.linspace(r_fit_raw[0], r_fit_raw[-1], 200)
            ax.plot(rd, np.polyval(coeffs_qr, rd), '-', color=C_QR, lw=1.5, label=f'QR ({K_qr:.4f})')
        if popt_mr is not None and len(r_fit_raw) > 0:
            rd = np.linspace(r_fit_raw[0], r_fit_raw[-1], 200)
            ax.plot(rd, morse_plot(rd, *popt_mr), '-', color=C_MR, lw=1.5, label=f'MR ({K_mr:.4f})')
        if coeffs_qg is not None and len(r_fit_guided) > 0:
            rd = np.linspace(r_fit_guided[0], r_fit_guided[-1], 200)
            ax.plot(rd, np.polyval(coeffs_qg, rd), '-', color=C_QG, lw=1.5, label=f'QG ({K_qg:.4f})')
        if popt_mg is not None and len(r_fit_guided) > 0:
            rd = np.linspace(r_fit_guided[0], r_fit_guided[-1], 200)
            ax.plot(rd, morse_plot(rd, *popt_mg), '-', color=C_MG, lw=1.5, label=f'MG ({K_mg:.4f})')
        if popt_qc is not None:
            rd = np.linspace(r[0], zoom_gr, 500)
            g_ds = 1.0 + _step_response_plot(rd, *popt_qc)
            g_ds = np.maximum(g_ds, 1e-10)
            v_ds = -np.log(g_ds)
            ax.plot(rd, v_ds, '-', color=C_DS, lw=1.5, label=f'DS ({K_ds:.4f})')
        ax.axhline(0, color='gray', ls='--', lw=0.5)
        ax.set_xlabel('r (px)'); ax.set_ylabel('V(r)')
        ax.set_title('(g) All 5 Overlaid', fontweight='bold', fontsize=9)
        ax.set_xlim(0, zoom_gr); ax.set_ylim(-1.2, 1.5)
        ax.legend(fontsize=5, loc='upper right')
        sns.despine(ax=ax)

        # ===== (h) Summary =====
        ax = axes[1, 3]
        ax.axis('off')
        flag = 'RELIABLE' if reliable else 'UNRELIABLE'
        txt = (
            f"K (um-2)         RMSE\n"
            f"{'='*30}\n"
            f"QR:  {K_qr:7.4f}    {rmse_qr:.4f}\n"
            f"MR:  {K_mr:7.4f}    {rmse_mr:.4f}\n"
            f"QG:  {K_qg:7.4f}    {rmse_qg:.4f}\n"
            f"MG:  {K_mg:7.4f}    {rmse_mg:.4f}\n"
            f"DS:  {K_ds:7.4f}    {rmse_ds_val:.4f}\n"
            f"{'='*30}\n"
            f"R2={R2_qc:.3f} SNR={snr:.2f}\n"
            f"ACF1={acf1:.3f}\n"
            f"{'-'*30}\n"
            f"{flag}"
        )
        box_color = '#D5F5E3' if reliable else '#FADBD8'
        edge_color = '#2ECC71' if reliable else '#E74C3C'
        ax.text(0.05, 0.5, txt, transform=ax.transAxes, fontsize=8,
                va='center', fontfamily='monospace', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=box_color,
                          edgecolor=edge_color, linewidth=2, alpha=0.95))

        fig.suptitle(img_name, fontweight='bold', fontsize=10, y=0.995)
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        if save:
            self._save_fig(fig, f'diagnostic_{img_name}')
        plt.show()

    # 7. MECHANICAL FIELD (3-panel: network, magnitude, vectors)
    # -----------------------------------------------------------------------

    def mechanical_field(self, save=None):
        """Combined truss network + force field visualization.
        Left: raw image with Delaunay edges (red=compressed, blue=tension) + r₀ zoom inset
        Right: |F| heatmap on nodes + force vectors on high-stress nodes + histogram inset
        """
        from matplotlib.collections import LineCollection
        from matplotlib.lines import Line2D
        from matplotlib.patches import Rectangle

        rf = getattr(self.c, 'residual_field', None)
        if rf is None:
            print("No residual_field data — call mechanical_state() instead of collective_order_pipeline().")
            return

        save = save if save is not None else self.save
        set_publication_style()

        pts = rf['pts_um']
        edges = rf['edges']
        d_um = rf['d_um']
        r0 = rf['r0']
        F_res = rf['F_residual']
        F_mag = rf['F_mag']
        mean_F = F_mag.mean()
        frac_c = rf.get('frac_compression', (d_um < r0).sum() / len(edges))

        # Shared spatial limits
        pad = 5
        xl = (pts[:, 0].min() - pad, pts[:, 0].max() + pad)
        yl = (pts[:, 1].min() - pad, pts[:, 1].max() + pad)
        vmax = np.percentile(F_mag, 95)

        fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 7))

        # ── LEFT: Truss network with image background ──
        # Try to show cell_area as background
        cell_area = getattr(self.c, 'cell_area', None)
        if cell_area is not None:
            pixel_size = getattr(self.c, 'pixel_size', 0.58) if hasattr(self.c, 'pixel_size') else 0.58
            H_px, W_px = cell_area.shape[:2]
            extent_um = [0, W_px * pixel_size, H_px * pixel_size, 0]
            ax_left.imshow(cell_area, extent=extent_um, aspect='auto',
                          cmap='gray' if cell_area.ndim == 2 else None,
                          alpha=0.5, zorder=0)

        # Delaunay edges
        segments = [[pts[i], pts[j]] for i, j in edges]
        edge_colors = ['#CC3311' if d_um[k] < r0 else '#0077BB' for k in range(len(edges))]
        ax_left.add_collection(LineCollection(segments, colors=edge_colors,
                                              linewidths=0.4, alpha=0.4, zorder=1))

        # Centroids
        ax_left.scatter(pts[:, 0], pts[:, 1], s=3, c='white', edgecolors='#333',
                        linewidths=0.2, zorder=2, alpha=0.8)

        ax_left.set_xlim(xl); ax_left.set_ylim(yl)
        ax_left.set_aspect('equal')
        ax_left.set_xlabel('x (µm)'); ax_left.set_ylabel('y (µm)')
        n_comp = (d_um < r0).sum()
        ax_left.set_title(f'Truss Network  ({n_comp}/{len(edges)} compressed)',
                          fontsize=10, fontweight='bold')

        # Zoom inset around center node
        cx, cy = np.median(pts[:, 0]), np.median(pts[:, 1])
        center_node = np.argmin(np.sqrt((pts[:, 0] - cx)**2 + (pts[:, 1] - cy)**2))
        zoom_cx, zoom_cy = pts[center_node]
        zoom_r = r0 * 2.2

        rect = Rectangle((zoom_cx - zoom_r, zoom_cy - zoom_r),
                           2 * zoom_r, 2 * zoom_r,
                           linewidth=1.2, edgecolor='#009E73', facecolor='none', zorder=5)
        ax_left.add_patch(rect)

        ax_in = ax_left.inset_axes([0.58, 0.02, 0.40, 0.50])
        ax_in.set_facecolor('#F8F8F5')
        x_lo, x_hi = zoom_cx - zoom_r, zoom_cx + zoom_r
        y_lo, y_hi = zoom_cy - zoom_r, zoom_cy + zoom_r

        # 1st-ring neighbors
        neighbor_mask = (edges[:, 0] == center_node) | (edges[:, 1] == center_node)
        ring1 = set()
        for i, j in edges[neighbor_mask]:
            ring1.add(i); ring1.add(j)
        ring2 = set()
        for nn in ring1:
            nn_mask = (edges[:, 0] == nn) | (edges[:, 1] == nn)
            for i, j in edges[nn_mask]:
                ring2.add(i); ring2.add(j)

        for k, (i, j) in enumerate(edges):
            if i in ring2 and j in ring2:
                xi, yi = pts[i]; xj, yj = pts[j]
                if x_lo < xi < x_hi and x_lo < xj < x_hi and \
                   y_lo < yi < y_hi and y_lo < yj < y_hi:
                    color = '#CC3311' if d_um[k] < r0 else '#0077BB'
                    lw = 1.5 if (i in ring1 and j in ring1) else 0.5
                    alpha = 0.9 if (i in ring1 and j in ring1) else 0.25
                    ax_in.plot([xi, xj], [yi, yj], '-', color=color, linewidth=lw, alpha=alpha)

        circle = plt.Circle((zoom_cx, zoom_cy), r0, fill=False,
                              color='#009E73', linewidth=1.5, linestyle='--', alpha=0.9)
        ax_in.add_patch(circle)

        for idx in ring2:
            xi, yi = pts[idx]
            if not (x_lo < xi < x_hi and y_lo < yi < y_hi):
                continue
            if idx == center_node:
                ax_in.plot(xi, yi, 'o', color='#333', markersize=6,
                           markeredgecolor='white', markeredgewidth=0.8, zorder=5)
            elif idx in ring1:
                ax_in.plot(xi, yi, 'o', color='#666', markersize=4,
                           markeredgecolor='white', markeredgewidth=0.5, zorder=4)
            else:
                ax_in.plot(xi, yi, 'o', color='#bbb', markersize=2.5, zorder=3)

        ax_in.set_xlim(x_lo, x_hi); ax_in.set_ylim(y_hi, y_lo)
        ax_in.set_aspect('equal'); ax_in.set_xticks([]); ax_in.set_yticks([])
        for spine in ax_in.spines.values():
            spine.set_edgecolor('#009E73'); spine.set_linewidth(1.2)

        legend_el = [
            Line2D([0], [0], color='#CC3311', lw=1.5, label=r'd < r$_0$'),
            Line2D([0], [0], color='#0077BB', lw=1.5, label=r'd > r$_0$'),
            Line2D([0], [0], color='#009E73', lw=1.5, linestyle='--',
                   label=f'r₀ = {r0:.1f} µm'),
        ]
        ax_left.legend(handles=legend_el, fontsize=7, loc='upper center', ncol=3,
                       framealpha=0.9)

        # ── RIGHT: Force field heatmap + vectors ──
        # Subtle edges
        ax_right.add_collection(LineCollection(segments,
                                colors=['#E8CCCC' if d_um[k]<r0 else '#CCE0F0'
                                        for k in range(len(edges))],
                                linewidths=0.25, alpha=0.3))

        sc = ax_right.scatter(pts[:, 0], pts[:, 1], c=F_mag, s=8, cmap='YlOrRd',
                              vmin=0, vmax=vmax, edgecolors='none', zorder=2)

        # Force vectors (top 30%)
        threshold = np.percentile(F_mag, 70)
        high = F_mag >= threshold
        if high.any():
            scale = np.percentile(F_mag[high], 95)
            ax_right.quiver(pts[high, 0], pts[high, 1], F_res[high, 0], F_res[high, 1],
                            F_mag[high], cmap='YlOrRd', clim=(0, vmax),
                            scale=scale * 18, width=0.004, headwidth=3, headlength=3.5,
                            alpha=0.75, zorder=3)

        cb = plt.colorbar(sc, ax=ax_right, shrink=0.75, pad=0.02)
        cb.set_label(r'$|F_i|$ (µm$^{-1}$)', fontsize=9, fontweight='bold')

        ax_right.set_xlim(xl); ax_right.set_ylim(yl)
        ax_right.set_aspect('equal')
        ax_right.set_xlabel('x (µm)')
        ax_right.set_title('Force Field', fontsize=10, fontweight='bold')

        # Stats annotation
        ax_right.text(0.97, 0.03,
                      f'mean|F| = {mean_F:.3f}\ncompression = {frac_c:.0%}\n'
                      f'hot spots = {rf.get("n_hot_spots", "?")}',
                      transform=ax_right.transAxes, fontsize=7, fontweight='bold',
                      color='white', ha='right', va='bottom',
                      bbox=dict(boxstyle='round,pad=0.3', facecolor='black',
                                alpha=0.6, edgecolor='none'))

        # Histogram inset
        ax_hist = ax_right.inset_axes([0.02, 0.65, 0.30, 0.30])
        ax_hist.hist(F_mag, bins=25, color='#E8833A', alpha=0.7, edgecolor='white', linewidth=0.3)
        ax_hist.axvline(mean_F, color='#CC3311', linewidth=1.5, linestyle='--', alpha=0.8)
        ax_hist.set_xlabel(r'$|F_i|$', fontsize=6); ax_hist.set_ylabel('n', fontsize=6)
        ax_hist.tick_params(labelsize=5)
        ax_hist.set_facecolor('#F8F8F5')

        fig.suptitle(f'Mechanical State  (K = {getattr(self.c, "K", "?")},  '
                     f'mean|F| = {mean_F:.3f},  {frac_c:.0%} compressed)',
                     fontweight='bold', fontsize=11, y=1.01)
        plt.tight_layout()
        if save:
            self._save_fig(fig, '08_mechanical_state')
        plt.show()

    # 8. HOT SPOTS (2-panel: network + histogram)
    # -----------------------------------------------------------------------

    def hot_spots(self, save=None):
        """Hot spot identification: top 10% nodes by |F| on Delaunay network."""
        from matplotlib.collections import LineCollection

        rf = getattr(self.c, 'residual_field', None)
        if rf is None:
            print("No residual_field data — call mechanical_state() instead of collective_order().")
            return

        save = save if save is not None else self.save
        set_publication_style()

        pts = rf['pts_um']
        edges = rf['edges']
        d_um = rf['d_um']
        r0 = rf['r0']
        F_mag = rf['F_mag']
        hot = rf['hot_spots']
        threshold_90 = rf['threshold_90']

        fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

        # Panel 1: network with hot spots
        ax = axes[0]
        segments, colors = [], []
        for k, (i, j) in enumerate(edges):
            segments.append([pts[i], pts[j]])
            colors.append('#CC3311' if d_um[k] < r0 else '#0077BB')
        lc = LineCollection(segments, colors=colors, linewidths=0.3, alpha=0.3)
        ax.add_collection(lc)
        ax.scatter(pts[~hot, 0], pts[~hot, 1], c='#ccc', s=3, edgecolors='none', zorder=2)
        ax.scatter(pts[hot, 0], pts[hot, 1], c='#CC3311', s=25, edgecolors='black',
                   linewidths=0.5, zorder=3, label=f'Hot spots ({hot.sum()} nodes)')
        ax.set_xlim(pts[:, 0].min(), pts[:, 0].max())
        ax.set_ylim(pts[:, 1].min(), pts[:, 1].max())
        ax.set_aspect('equal')
        ax.set_xlabel('x (µm)'); ax.set_ylabel('y (µm)')
        ax.set_title('Truss Network + Hot Spots\n(red nodes = top 10% |F|)', fontsize=9, fontweight='bold')
        ax.legend(fontsize=7, loc='upper right')
        sns.despine(ax=ax)

        # Panel 2: histogram
        ax = axes[1]
        ax.hist(F_mag, bins=30, color='#4A90D9', alpha=0.7, edgecolor='white', linewidth=0.3)
        ax.axvline(threshold_90, color='#CC3311', linewidth=2, linestyle='--',
                   label=f'90th pctl = {threshold_90:.3f}')
        ax.set_xlabel('|F_residual|'); ax.set_ylabel('Count')
        ax.set_title('Force Distribution', fontsize=9, fontweight='bold')
        ax.legend(fontsize=8)
        sns.despine(ax=ax)

        spatial_cv = getattr(self.c, 'spatial_cv', np.nan)
        fig.suptitle(f'Hot Spot Analysis  (spatial CV={spatial_cv:.2f}, {hot.sum()} hot spots)',
                     fontweight='bold', fontsize=10, y=1.02)
        plt.tight_layout()
        if save:
            self._save_fig(fig, 'hot_spots')
        plt.show()

    # 9. VIRTUAL SURGERY (2 figures: before state + after comparison)
    # -----------------------------------------------------------------------

    # 10. ALL PLOTS AT ONCE
    # -----------------------------------------------------------------------

    def all(self, save=None):
        """Run all plots in sequence."""
        save = save if save is not None else self.save
        self.segmentation(save=save)
        self.radial_distribution(save=save)
        self.potential(save=save)
        self.fitting(save=save)
        self.comprehensive(save=save)
        self.publication_gr(save=save)
        self.publication_vr(save=save)
        # Mechanical field plots (only if residual_field data is present)
        if getattr(self.c, 'residual_field', None) is not None:
            self.mechanical_field(save=save)
            self.hot_spots(save=save)
