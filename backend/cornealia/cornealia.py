import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
try:
    import easyocr
    _HAS_EASYOCR = True
except Exception:
    _HAS_EASYOCR = False
from collections import defaultdict
from scipy.signal import savgol_filter
from pathlib import Path
from multiprocessing import Pool, freeze_support
import os
import sys
import time

# Auto-configure paths when run as CLI (python cornealia.py)
if __name__ == '__main__' or (not getattr(sys, 'frozen', False) and '__spec__' not in dir()):
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    _backend_dir = os.path.dirname(_this_dir)
    for _p in [_backend_dir, os.path.join(_backend_dir, 'shared_modules'), _this_dir]:
        if _p not in sys.path:
            sys.path.insert(0, _p)

from tqdm import tqdm
from scipy.optimize import curve_fit


from shared_modules.cellade.cellade import CellADE
try:
    from .plotters.cornealia_plotter import cornealia_plotter
except ImportError:
    from plotters.cornealia_plotter import cornealia_plotter


# ═══════════════════════════════════════════════════════════
# Machine profiles — crop regions and calibration for
# different specular microscopes.
# ═══════════════════════════════════════════════════════════

MACHINE_PROFILES = {
    'cellchek_d': {
        'name': 'CellChek D (Konan Medical)',
        'description': 'Crops cell area from machine output image and reads classical metrics (CD, Ave, SD, CV, HEX) via OCR.',
        'cell_area':    {'x1': 24, 'y1': 261, 'x2': 708, 'y2': 775},
        'metrics_area': {'x1': 114, 'y1': 812, 'x2': 307, 'y2': 968},
        'preview_rect': {'x': 24, 'y': 261, 'w': 684, 'h': 514},
        'default_pixel_size': 0.58,
        'green_dot_detection': True,
    },
    # Future machines:
    # 'topcon_sp3000p': { ... },
    # 'tomey_em4000': { ... },
}


# ═══════════════════════════════════════════════════════════
# Pipeline step contract
# ═══════════════════════════════════════════════════════════
# their display names, and which key outputs to surface.
# ═══════════════════════════════════════════════════════════

PIPELINE_STEPS = [
    {'id': 'load',       'name': 'Load Image',       'key_outputs': []},
    {'id': 'preprocess', 'name': 'Preprocess',        'key_outputs': ['machine_CD', 'machine_Ave'], 'optional': True},
    {'id': 'segment',    'name': 'Segmentation',      'key_outputs': ['n_cells']},
    {'id': 'metrics',    'name': 'Classic Metrics',    'key_outputs': ['CD_calc', 'Ave_calc', 'CV_calc', 'HEX_calc']},
    {'id': 'gr',         'name': 'g(r) Computation',   'key_outputs': ['n_interior', 'g_peak']},
    {'id': 'quality',    'name': 'Quality Gate',       'key_outputs': ['reliable', 'R2_damped', 'SNR']},
    {'id': 'fitting',    'name': 'K Fitting',          'key_outputs': ['K', 'K_ds', 'r0_fit']},
    {'id': 'force',      'name': 'Force Field',        'key_outputs': ['mean_F', 'frac_compression', 'n_hot_spots']},
]


class PipelineReporter:
    """
    Tracks pipeline step progress with structured status updates.

    Each step transitions:  idle → running → done | failed

    Usage:
        reporter = PipelineReporter(PIPELINE_STEPS, callback=my_gui_callback)
        reporter.start('segment')
        ...compute...
        reporter.done('segment', {'n_cells': 342})

    The callback receives the full board state on every transition,
    enabling real-time GUI updates. Without a callback, status is printed.
    """

    # Status constants
    IDLE    = 'idle'
    RUNNING = 'running'
    DONE    = 'done'
    FAILED  = 'failed'
    SKIPPED = 'skipped'

    # Status indicators for CLI display
    _ICONS = {
        'idle':    '⚪',
        'running': '🟡',
        'done':    '🟢',
        'failed':  '🔴',
        'skipped': '⚫',
    }

    def __init__(self, steps=None, callback=None, verbose=True):
        """
        Parameters
        ----------
        steps : list of dict
            Step definitions from PIPELINE_STEPS.
        callback : callable or None
            Called with (step_id, status, board) on every transition.
            If None, prints to stdout.
        verbose : bool
            If True and no callback, print status updates.
        """
        self.steps = steps or PIPELINE_STEPS
        self.callback = callback
        self.verbose = verbose

        # Board state: ordered dict of step_id → {status, name, outputs, error, time}
        self.board = {}
        for s in self.steps:
            self.board[s['id']] = {
                'name':        s['name'],
                'status':      self.IDLE,
                'key_outputs': s.get('key_outputs', []),
                'optional':    s.get('optional', False),
                'outputs':     {},
                'error':       None,
                'time':        None,
            }
        self._timers = {}

    def start(self, step_id):
        """Mark step as running."""
        if step_id not in self.board:
            return
        self.board[step_id]['status'] = self.RUNNING
        self.board[step_id]['error'] = None
        self._timers[step_id] = time.time()
        self._emit(step_id)

    def done(self, step_id, outputs=None):
        """Mark step as done with optional key outputs."""
        if step_id not in self.board:
            return
        elapsed = time.time() - self._timers.get(step_id, time.time())
        self.board[step_id]['status'] = self.DONE
        self.board[step_id]['time'] = round(elapsed, 2)
        if outputs:
            # Convert numpy types to Python natives for JSON serialization
            clean = {}
            for k, v in outputs.items():
                if isinstance(v, (np.bool_,)):
                    clean[k] = bool(v)
                elif isinstance(v, (np.integer,)):
                    clean[k] = int(v)
                elif isinstance(v, (np.floating,)):
                    clean[k] = round(float(v), 6)
                else:
                    clean[k] = v
            self.board[step_id]['outputs'] = clean
        self._emit(step_id)

    def fail(self, step_id, error):
        """Mark step as failed with error message."""
        if step_id not in self.board:
            return
        elapsed = time.time() - self._timers.get(step_id, time.time())
        self.board[step_id]['status'] = self.FAILED
        self.board[step_id]['time'] = round(elapsed, 2)
        self.board[step_id]['error'] = str(error)
        self._emit(step_id)

    def skip(self, step_id):
        """Mark optional step as skipped."""
        if step_id not in self.board:
            return
        self.board[step_id]['status'] = self.SKIPPED
        self._emit(step_id)

    def get_board(self):
        """Return full board state for GUI rendering."""
        completed = sum(1 for s in self.board.values() if s['status'] == self.DONE)
        total = sum(1 for s in self.board.values() if not s['optional'])
        return {
            'steps': self.board,
            'completed': completed,
            'total': total,
            'has_failure': any(s['status'] == self.FAILED for s in self.board.values()),
        }

    def _emit(self, step_id):
        """Send update via callback or print."""
        step = self.board[step_id]
        icon = self._ICONS.get(step['status'], '?')

        if self.callback:
            self.callback(step_id, step['status'], self.get_board())
        elif self.verbose:
            out_str = ''
            if step['outputs']:
                out_str = '  ' + '  '.join(f"{k}={v}" for k, v in step['outputs'].items())
            time_str = f"  ({step['time']}s)" if step['time'] is not None else ''
            print(f"  {icon} {step['name']}{time_str}{out_str}")


class cornealia :
    
    def __init__(self, is_input_image_machine_output=True, machine_type='cellchek_d', fcm_method='local', min_expansion_shells=5,min_interior_cells_ratio=0.4,exclusion_ratio=0.15,
                shell_thickness=1,fitting_half_width=10,SAVGOL_WINDOW=11,SAVGOL_ORDER=3, fitting_method='morse',pixel_size=0.58,verbose=True,invert_image=False,cellade_params=None):
        """
        Parameters-only constructor. No image is loaded here.
        All processing methods receive image_path as input and return results as dicts.
        This allows the same configured object to be reused across many images,
        including parallel batch processing via multiprocessing.Pool.
        
        pixel_size   : float or (sx, sy)  μm/px. A tuple gives non-square pixels
                       (sx along columns/x, sy along rows/y). Internally
                       self.pixel_size = s = sqrt(sx*sy) (effective size, s^2 =
                       pixel area) and distances are weighted per axis by
                       ax = sx/s, ay = sy/s, so all lengths are in effective px.
        machine_type : str    Machine profile key (e.g. 'cellchek_d') or 'none'
        verbose      : bool   True → print per-image details; False → silent (used in batch)
        """

        if np.ndim(pixel_size) == 0:
            _sx = _sy = float(pixel_size)
        else:
            _sx, _sy = (float(v) for v in pixel_size)
        self.pixel_size_xy = (_sx, _sy)            # (sx, sy) μm/px as given
        self.pixel_size = float(np.sqrt(_sx * _sy))  # effective s; s^2 = pixel area
        self.ax = _sx / self.pixel_size            # per-axis weights, ax*ay = 1
        self.ay = _sy / self.pixel_size
        self.pixel_size_ref=0.58   # reference pixel size (clinical specular microscopy) # the unit should be  μm/px
        self.is_input_image_machine_output=is_input_image_machine_output
        self.machine_type=machine_type
        self.fcm_method = fcm_method
        self.min_expansion_shells=min_expansion_shells
        self.min_interior_cells_ratio=min_interior_cells_ratio
        self.exclusion_ratio=exclusion_ratio
        self.shell_thickness=shell_thickness
        self.fitting_half_width=fitting_half_width
        self.SAVGOL_WINDOW=SAVGOL_WINDOW
        self.SAVGOL_ORDER=SAVGOL_ORDER
        self.verbose=verbose
        self.fitting_method=fitting_method
        self.invert_image=invert_image
        self.cellade_params=cellade_params or {}

        # EasyOCR reader — lazily initialised on first use (see _get_ocr_reader).
        # Excluded from pickling so multiprocessing workers each create their own.
        self._ocr_reader = None


    # ------------------------------------------------------------------
    # Pickle support — exclude the non-picklable EasyOCR reader
    # ------------------------------------------------------------------
    def __getstate__(self):
        state = self.__dict__.copy()
        state['_ocr_reader'] = None      # drop before pickle
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)       # _ocr_reader arrives as None
        # it will be lazily re-created on first call in the worker

    def _get_ocr_reader(self):
        """Return a cached EasyOCR reader, creating it on first call.
        Stderr is suppressed during creation to hide the GPU warning."""
        if not _HAS_EASYOCR:
            print("⚠️ EasyOCR not available — machine output OCR disabled")
            return None
        if self._ocr_reader is None:
            with open(os.devnull, 'w') as devnull:
                old_stderr = sys.stderr
                sys.stderr = devnull
                self._ocr_reader = easyocr.Reader(['en'])
                sys.stderr = old_stderr
        return self._ocr_reader


    def _load_image(self, image_path):
        """Load image from path and convert BGR → RGB.
        Uses np.fromfile to handle paths with spaces or special characters."""
        img = cv2.imdecode(np.fromfile(str(image_path), dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(f"Could not load image: {image_path}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


    def cleaning_preprocessing(self, input_image):

        # Get crop regions from machine profile
        profile = MACHINE_PROFILES.get(self.machine_type, MACHINE_PROFILES.get('cellchek_d'))
        ca = profile['cell_area']
        ma = profile['metrics_area']

        cell_area = input_image[ca['y1']:ca['y2'], ca['x1']:ca['x2']]
        metrics_area = input_image[ma['y1']:ma['y2'], ma['x1']:ma['x2']]

        # detecting green dots
        HSV = cv2.cvtColor(cell_area, cv2.COLOR_RGB2HSV)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(HSV, lower_green, upper_green)

        # ── Extract dot centroids BEFORE inpainting ──
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        dot_mask = cv2.dilate(mask, kernel, iterations=2)
        dot_mask = cv2.erode(dot_mask, kernel, iterations=1)
        n_labels, _, stats, centroids_cv = cv2.connectedComponentsWithStats(dot_mask)

        dot_centroids = []
        for i in range(1, n_labels):  # skip background
            area = stats[i, cv2.CC_STAT_AREA]
            if 5 <= area <= 500:
                dot_centroids.append([centroids_cv[i, 0], centroids_cv[i, 1]])  # x, y
        dot_centroids = np.array(dot_centroids) if dot_centroids else None

        # removing dots by inpainting
        cell_area = cv2.inpaint(cell_area, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

        # extracting text OCR
        reader = self._get_ocr_reader()
        machine_metrics = None
        if reader is not None:
            gray = cv2.cvtColor(metrics_area, cv2.COLOR_RGB2GRAY)
            enhanced = cv2.convertScaleAbs(gray, alpha=2.0, beta=3)
            enhanced_enlarged = cv2.resize(enhanced, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

            result = reader.readtext(enhanced_enlarged)
            text = [item[1] for item in result]
            numbers = [int(t.replace(',', '')) for t in text if t.replace(',', '').isdigit()]

            machine_metrics = {
                'CD (cells/mm^2)': numbers[0] if len(numbers) > 0 else None,
                'CV':              numbers[1] if len(numbers) > 1 else None,
                'HEX(%)':          numbers[2] if len(numbers) > 2 else None,
                'SD':              numbers[3] if len(numbers) > 3 else None,
                'Ave(micrometer^2)': numbers[4] if len(numbers) > 4 else None,
                'Num':             numbers[5] if len(numbers) > 5 else None,
            }

        return cell_area, machine_metrics, dot_centroids


    def segmentation(self, cell_area):
        
        # Merge default CellADE params with any user overrides
        _cellade_defaults = {'fcm_mode': self.fcm_method, 'use_fft_sigma': True}
        _cellade_defaults.update(self.cellade_params)
        segmentor = CellADE(mode='cornealia', params=_cellade_defaults)
        segmentor.run(cell_area)
        segmentor.enhanced_image = segmentor.enhanced  # backward compat for plotters
        segmentor.blobs = segmentor.seeds               # backward compat for plotters
        segmentor.global_fg = segmentor.foreground       # backward compat for plotters
        return segmentor.objects, segmentor

    def _compute_classic_metrics(self, centroids, areas, H, W, method='segmentation', dot_centroids=None):
        
        """
        Compute morphological metrics from cell data.

        Parameters
        ----------
        centroids : np.ndarray
            (N, 2) array of cell centroids in (row, col) pixel coordinates.
        areas : np.ndarray
            (N,) array of cell areas in pixels.
        H : int
            Image height in pixels.
        W : int
            Image width in pixels.
        method : str
            'voronoi'       – Voronoi from machine's green dot centroids.
            'segmentation'  – From watershed cell regions (scientifically accurate).
        dot_centroids : np.ndarray or None
            (N, 2) array of (x, y) green dot positions. Required for 'voronoi' method.

        Returns
        -------
        dict with CD_calc, Ave_calc, SD_calc, CV_calc, HEX_calc, metrics_method, etc.
        """
        from scipy.spatial import Voronoi, Delaunay, ConvexHull

        px2 = self.pixel_size ** 2

        # ==================================================================
        # METHOD 1: Voronoi from machine green dots (verification)
        # ==================================================================
        if method == 'voronoi':

            if dot_centroids is None or len(dot_centroids) < 10:
                return {
                    'CD_calc': None, 'Ave_calc': None, 'SD_calc': None,
                    'CV_calc': None, 'HEX_calc': None,
                    'metrics_method': 'voronoi', 'n_interior_metrics': 0,
                    'n_dots_detected': 0,
                }

            points = dot_centroids  # (N, 2) in (x, y)
            n = len(points)

            # Build Voronoi with mirror boundaries
            mirror = []
            for px_c, py_c in points:
                mirror.extend([[-px_c, py_c], [2*W - px_c, py_c],
                            [px_c, -py_c], [px_c, 2*H - py_c]])
            vor = Voronoi(np.vstack([points, np.array(mirror)]))

            # Compute area and side count for each dot
            areas_px = np.full(n, np.nan)
            n_sides = np.zeros(n, dtype=int)
            for i in range(n):
                region = vor.regions[vor.point_region[i]]
                if -1 in region or len(region) == 0:
                    continue
                poly = np.clip(vor.vertices[region], [0, 0], [W, H])
                x_p, y_p = poly[:, 0], poly[:, 1]
                areas_px[i] = 0.5 * np.abs(
                    np.dot(x_p, np.roll(y_p, 1)) - np.dot(y_p, np.roll(x_p, 1)))
                n_sides[i] = len(region)

            valid = ~np.isnan(areas_px)
            if valid.sum() == 0:
                return {
                    'CD_calc': None, 'Ave_calc': None, 'SD_calc': None,
                    'CV_calc': None, 'HEX_calc': None,
                    'metrics_method': 'voronoi', 'n_interior_metrics': 0,
                    'n_dots_detected': n,
                }

            # ── Interior selection: 1 round convex hull peel + IQR 1.5 ──
            # Hull peel: remove outermost ring of dots
            mask = valid.copy()
            idx = np.where(mask)[0]
            if len(idx) >= 4:
                hull = ConvexHull(points[idx])
                mask[idx[hull.vertices]] = False

            # IQR filter on polygon areas
            a_masked = areas_px[mask]
            a_valid = a_masked[~np.isnan(a_masked)]
            if len(a_valid) > 0:
                q1, q3 = np.percentile(a_valid, [25, 75])
                iqr = q3 - q1
                mask = mask & (areas_px >= q1 - 1.5 * iqr) & (areas_px <= q3 + 1.5 * iqr)

            interior = mask
            if interior.sum() == 0:
                return {
                    'CD_calc': None, 'Ave_calc': None, 'SD_calc': None,
                    'CV_calc': None, 'HEX_calc': None,
                    'metrics_method': 'voronoi', 'n_interior_metrics': 0,
                    'n_dots_detected': n,
                }

            areas_um2 = areas_px[interior] * px2
            sides = n_sides[interior]
            n_cells = interior.sum()

            Ave_calc = float(np.mean(areas_um2))
            SD_calc  = float(np.std(areas_um2))
            CV_calc  = float(SD_calc / Ave_calc * 100) if Ave_calc > 0 else 0.0
            CD_calc  = 1e6 / Ave_calc
            HEX_calc = float(np.sum(sides == 6) / n_cells * 100)

            return {
                'CD_calc':  round(CD_calc, 6),
                'Ave_calc': round(Ave_calc, 7),
                'SD_calc':  round(SD_calc, 6),
                'CV_calc':  round(CV_calc, 8),
                'HEX_calc': round(HEX_calc, 8),
                'metrics_method': 'voronoi',
                'n_interior_metrics': int(n_cells),
                'n_dots_detected': n,
            }

        # ==================================================================
        # METHOD 2: Segmentation (actual watershed regions)
        # ==================================================================
        else:
            px2_to_mm2 = px2 / 1e6

            # Exclusion zone (effective px; per-axis margin in pixels)
            MAX_R = int(min(H * self.ay, W * self.ax) * self.exclusion_ratio)
            MAX_R_x = MAX_R / self.ax
            MAX_R_y = MAX_R / self.ay
            y_coords = centroids[:, 0]
            x_coords = centroids[:, 1]

            interior_mask = ((y_coords >= MAX_R_y) & (y_coords <= H - MAX_R_y) &
                            (x_coords >= MAX_R_x) & (x_coords <= W - MAX_R_x))

            interior_areas = areas[interior_mask]

            if len(interior_areas) == 0:
                interior_areas = areas
                interior_mask[:] = True

            # Areas from actual pixel counts
            areas_um2 = interior_areas * px2

            Ave_calc = float(np.mean(areas_um2))
            SD_calc  = float(np.std(areas_um2))
            CV_calc  = float(SD_calc / Ave_calc * 100) if Ave_calc > 0 else 0.0

            # CD: direct count over interior area
            interior_H = H - 2 * MAX_R_y
            interior_W = W - 2 * MAX_R_x
            interior_area_mm2 = (interior_H * interior_W) * px2_to_mm2
            CD_calc = len(interior_areas) / interior_area_mm2

            # HEX: Delaunay neighbors from centroids (robust, gap-independent)
            interior_centroids = centroids[interior_mask]
            interior_points = np.column_stack([interior_centroids[:, 1] * self.ax,
                                            interior_centroids[:, 0] * self.ay])  # (x, y), effective px

            n_int = len(interior_areas)
            if n_int >= 4:
                tri = Delaunay(interior_points)
                neighbors = {i: set() for i in range(n_int)}
                for simplex in tri.simplices:
                    for i in simplex:
                        for j in simplex:
                            if i != j:
                                neighbors[i].add(j)

                n_hex = sum(1 for i in range(n_int) if len(neighbors[i]) == 6)
                HEX_calc = float(n_hex / n_int * 100)
            else:
                HEX_calc = 0.0

            return {
                'CD_calc':  round(CD_calc, 6),
                'Ave_calc': round(Ave_calc, 7),
                'SD_calc':  round(SD_calc, 6),
                'CV_calc':  round(CV_calc, 8),
                'HEX_calc': round(HEX_calc, 8),
                'metrics_method': 'segmentation',
                'n_interior_metrics': int(interior_mask.sum()),
                'n_border_excluded': int((~interior_mask).sum()),
            }
    def compute_collective_order(self, centroids, image_dims):
        """
        Compute collective order from cell centroids.

        Computes the radial distribution function g(r), interaction potential
        V(r), quality gate, and collective order parameter K using 5 methods.

        Parameters
        ----------
        centroids : np.ndarray
            (N, 2) array of cell centroids in (row, col) pixel coordinates.
        image_dims : tuple
            (H, W) image dimensions in pixels.

        Returns
        -------
        dict
            Collective order results only:
            - n_cells, n_interior
            - K values (5 methods) + K_Vmin, K_gpeak
            - RMSE values (5 methods)
            - r0_fit, v_min, g_peak
            - Quality gate: reliable, has_peak, has_crossing, has_trough,
              R2_damped, R2_full, A_damped, xi_damped, lambda_damped,
              r_excl_damped, phi_damped, SNR, ACF1
            - Curves: r_values, g_r, g_r_smooth, v_r, r_valid, v_r_valid
            - Fitting regions: r_fit_raw, v_fit_raw, r_fit_guided,
              v_fit_guided, r_fit_ds, v_fit_ds
            - Fit parameters: popt_qc, coeffs_qr, coeffs_qg, popt_mr,
              popt_mg, popt_ds
        """

        cell_H, cell_W = image_dims
        y_coords = centroids[:, 0]
        x_coords = centroids[:, 1]

        MAX_R = int(min(cell_H * self.ay, cell_W * self.ax) * self.exclusion_ratio)  # effective px
        MAX_R_x = MAX_R / self.ax                                 # margin in pixels per axis
        MAX_R_y = MAX_R / self.ay

        interior_region = ((y_coords >= MAX_R_y) & (y_coords <= cell_H - MAX_R_y) &
                        (x_coords >= MAX_R_x) & (x_coords <= cell_W - MAX_R_x))

        # --- Global density and shell settings ---
        global_density = len(y_coords) / (cell_H * cell_W)
        DR = self.shell_thickness

        # --- Fixed bins: same for every cell ---
        bins = np.arange(0, MAX_R, DR)
        r_centers = bins[:-1] + DR / 2

        shell_areas = 2 * np.pi * r_centers * DR
        random_expectation = global_density * shell_areas

        interior_indices = np.where(interior_region)[0]

        # --- g(r) accumulator (vectorized) ---
        # Mathematically identical to averaging per-cell (counts / random_expectation)
        # over all interior cells: because random_expectation is a constant vector,
        # mean_i(counts_i / rand) == (mean_i counts_i) / rand. We therefore accumulate
        # summed bin counts with np.bincount (no per-bin Python loop, no per-cell
        # division, no dict-of-lists) and divide once at the end.
        n_bins = len(r_centers)
        summed_counts = np.zeros(n_bins, dtype=np.float64)

        start = time.time()

        for i in interior_indices:
            x_c, y_c = x_coords[i], y_coords[i]

            dx = x_coords - x_c
            dy = y_coords - y_c
            distances = np.sqrt((self.ax * dx)**2 + (self.ay * dy)**2)  # effective px
            distances[i] = 0

            d = distances[distances > 0]
            # np.histogram(d, bins=bins) semantics: bin k is [bins[k], bins[k+1]),
            # with the final bin closed on the right. Reproduce via digitize+bincount.
            idx = np.digitize(d, bins) - 1
            valid = (idx >= 0) & (idx < n_bins)
            summed_counts += np.bincount(idx[valid], minlength=n_bins)[:n_bins]
            on_last = d == bins[-1]        # values on the closed right edge
            if on_last.any():
                summed_counts[-1] += on_last.sum()

        if self.verbose:
            print(f"Time: {time.time() - start:.2f} seconds")
            print(f"Interior cells: {len(interior_indices)} / {len(y_coords)}")

        # --- Final g(r): average over all interior cells ---
        mean_counts = summed_counts / len(interior_indices)
        r_values = r_centers.copy()
        g_r = mean_counts / random_expectation

        # Savitzky-Golay smoothing — kept for display/plotting only, NOT used for fitting
        g_r_smooth = savgol_filter(g_r, window_length=self.SAVGOL_WINDOW,
                                polyorder=self.SAVGOL_ORDER)

        # --- g(r) first peak height (from raw data) ---
        end_search_peak = len(r_values) // 2
        g_peak = float(np.max(g_r[:end_search_peak])) if end_search_peak > 0 else 1.0


        # =============================================================
        # QUALITY GATE: Step response fit on g(r)
        # Purpose: (1) reliability flag, (2) fitting boundaries for V(r)
        # Model: underdamped step response on g(r)-1
        # 5 parameters: A, ξ, λ, r_excl, φ
        # =============================================================
        signal_gr = g_r - 1.0

        def _step_response(r, A, xi, lam, r_excl, phi):
            """Step response on g(r)-1: Heaviside × underdamped oscillation."""
            H = 1.0 / (1.0 + np.exp(-(r - r_excl) / 0.3))  # fixed transition
            t = np.maximum(r - r_excl, 0.0)
            osc = -A * np.exp(-t / xi) * np.sin(2 * np.pi * t / lam + phi)
            return H * osc + (1.0 - H) * (-1.0)

        def _damped_sine_vr(r, D, xi, lam, r0):
            """Damped sine for V(r): starts at -D at r0, decays toward 0."""
            return -D * np.exp(-(r - r0) / xi) * np.cos(2 * np.pi * (r - r0) / lam)

        def morse_potential(r, D_e, a, r_0, offset):
            """Morse potential for V(r) fitting."""
            return D_e * (1 - np.exp(-a * (r - r_0)))**2 + offset

        # Initial guesses
        _peak_idx = np.argmax(g_r[:end_search_peak]) if end_search_peak > 0 else 0
        _A_guess = max(g_r[_peak_idx] - 1, 0.05) + 1.0
        _r0_guess = r_values[_peak_idx]
        _lam_guess = np.clip(2 * _r0_guess, 10, 70)
        _excl_candidates = np.where(g_r > 0.1)[0]
        _r_excl_guess = r_values[_excl_candidates[0]] if len(_excl_candidates) > 0 else r_values[0]
        _phi_guess = np.arcsin(min(1.0 / max(_A_guess, 1.01), 0.99))
        _A_guess = min(_A_guess, 9.5)  # clamp to stay within bounds

        try:
            _popt_qc, _ = curve_fit(
                _step_response, r_values, signal_gr,
                p0=[_A_guess, 15.0, _lam_guess, _r_excl_guess, _phi_guess],
                bounds=([0.5, 1, 5, r_values[0], -np.pi],
                        [10.0, 100, 80, r_values[-1], np.pi]),
                maxfev=15000,
            )
            _A_fit, _xi_fit, _lam_fit, _r_excl_fit, _phi_fit = _popt_qc
            _fitted_qc = _step_response(r_values, *_popt_qc)

            # R² on FULL curve (for reporting)
            _ss_res_full = np.sum((signal_gr - _fitted_qc)**2)
            _ss_tot_full = np.sum((signal_gr - np.mean(signal_gr))**2)
            _R2_full = 1 - _ss_res_full / _ss_tot_full if _ss_tot_full > 0 else 0.0

            # R² on OSCILLATORY region only (for QC — excludes the rise)
            _osc_mask_qc = r_values >= _r_excl_fit
            _sig_osc = signal_gr[_osc_mask_qc]
            _fit_osc = _fitted_qc[_osc_mask_qc]
            _ss_res_osc = np.sum((_sig_osc - _fit_osc)**2)
            _ss_tot_osc = np.sum((_sig_osc - np.mean(_sig_osc))**2)
            _R2 = 1 - _ss_res_osc / _ss_tot_osc if _ss_tot_osc > 0 else 0.0

            # --- Form check on oscillatory region ---
            _r_dense_qc = np.linspace(_r_excl_fit, r_values[-1], 1000)
            _t_dense = _r_dense_qc - _r_excl_fit
            _fitted_osc = -_A_fit * np.exp(-_t_dense / _xi_fit) * np.sin(
                2 * np.pi * _t_dense / _lam_fit + _phi_fit)

            _half = len(_r_dense_qc) // 2
            _pos_peak_idx = np.argmax(_fitted_osc[:_half])
            _pos_peak_val = _fitted_osc[_pos_peak_idx]
            _has_positive_peak = _pos_peak_val > 0.02

            _after_peak = _fitted_osc[_pos_peak_idx:]
            _zero_crossings_qc = np.where(np.diff(np.sign(_after_peak)))[0]
            _has_zero_crossing = len(_zero_crossings_qc) >= 1

            _has_negative_trough = False
            if _has_zero_crossing:
                _after_cross = _fitted_osc[_pos_peak_idx + _zero_crossings_qc[0]:]
                _neg_trough_val = np.min(_after_cross) if len(_after_cross) > 0 else 0
                _has_negative_trough = _neg_trough_val < -0.01

            _form_ok = _has_positive_peak and _has_zero_crossing and _has_negative_trough

            # Residual analysis on oscillatory region
            _residuals_qc = _sig_osc - _fit_osc
            _res_std = np.std(_residuals_qc) if len(_residuals_qc) > 1 else np.inf
            _SNR = _A_fit / _res_std if _res_std > 0 else 0.0

            if len(_residuals_qc) > 2:
                _res_centered = _residuals_qc - np.mean(_residuals_qc)
                _acf_denom = np.sum(_res_centered**2)
                _acf1 = np.sum(_res_centered[:-1] * _res_centered[1:]) / _acf_denom if _acf_denom > 0 else 1.0
            else:
                _acf1 = 1.0
            _is_white_noise = abs(_acf1) < 0.4

            # Scale spatial thresholds by pixel size relative to the reference
            # pixel size (0.58 µm/px, clinical specular microscopy). This keeps
            # the physical wavelength/decay-length gates unchanged: at px=0.58
            # the thresholds are the original values; at smaller pixel sizes
            # (higher magnification) they scale up proportionally.
            _px_scale = self.pixel_size_ref / self.pixel_size
            _params_ok = (_xi_fit < 95 * _px_scale) and (_lam_fit < 70 * _px_scale) and (_lam_fit > 8 / _px_scale)

            # Peak height gate: g(r) must have a meaningful peak above 1
            _peak_height_ok = g_peak > 1.10

            _reliable = _form_ok and _params_ok and _peak_height_ok and (
                (_R2 > 0.5) or
                (_R2 > 0.2 and _is_white_noise and _SNR > 1.2)
            )

            if self.verbose:
                print(f"    Form check: peak={_has_positive_peak} ({_pos_peak_val:.3f}), "
                      f"crossing={_has_zero_crossing}, trough={_has_negative_trough}")
                print(f"    Peak height: g_peak={g_peak:.3f} (gate={'PASS' if _peak_height_ok else 'FAIL'})")
                print(f"    Residuals: σ={_res_std:.3f}, SNR={_SNR:.2f}, ACF1={_acf1:.3f}, "
                      f"white_noise={_is_white_noise}")
                print(f"    R²(full)={_R2_full:.3f}, R²(osc)={_R2:.3f}")

            # --- Derive V(r) boundaries from QC fit ---
            _g_fitted_qc = 1.0 + _fitted_osc
            _g_fitted_qc = np.maximum(_g_fitted_qc, 1e-10)
            _V_fitted_qc = -np.log(_g_fitted_qc)

            _V_half = len(_V_fitted_qc) // 2
            _V_min_idx_qc = np.argmin(_V_fitted_qc[:_V_half])
            _r0_V_qc = _r_dense_qc[_V_min_idx_qc]

            # K_ds = V''(r₀) from smooth QC-derived V(r)
            _dr_qc = _r_dense_qc[1] - _r_dense_qc[0]
            _Vpp_ds_qc = np.gradient(np.gradient(_V_fitted_qc, _dr_qc), _dr_qc)

            # Left boundary: zero crossing before minimum
            _V_pre = _V_fitted_qc[:_V_min_idx_qc][::-1]
            _V_zc_left = np.where(np.diff(np.sign(_V_pre)))[0]
            _qc_left_r = _r_dense_qc[_V_min_idx_qc - _V_zc_left[0] - 1] if len(_V_zc_left) >= 1 else _r_dense_qc[0]

            # Right boundary: zero crossing after minimum + hump
            _V_post = _V_fitted_qc[_V_min_idx_qc:]
            _V_zc_right = np.where(np.diff(np.sign(_V_post)))[0]
            if len(_V_zc_right) >= 1:
                _right_zc_idx = _V_min_idx_qc + _V_zc_right[0] + 1
                _qc_right_zc_r = _r_dense_qc[min(_right_zc_idx, len(_r_dense_qc) - 1)]
                _V_after_zc = _V_fitted_qc[_right_zc_idx:]
                if len(_V_after_zc) > 2:
                    _hump_idx = _right_zc_idx + np.argmax(_V_after_zc[:len(_V_after_zc)//2])
                    _qc_right_r = _r_dense_qc[min(_hump_idx + 1, len(_r_dense_qc) - 1)]
                else:
                    _qc_right_r = _r_dense_qc[min(_right_zc_idx + 1, len(_r_dense_qc) - 1)]
            else:
                _qc_right_r = _r_dense_qc[-1]
                _qc_right_zc_r = _r_dense_qc[-1]

        except RuntimeError:
            _A_fit = _xi_fit = _lam_fit = _r_excl_fit = _phi_fit = np.nan
            _R2 = 0.0
            _R2_full = 0.0
            _reliable = False
            _form_ok = False
            _peak_height_ok = False
            _has_positive_peak = False
            _has_zero_crossing = False
            _has_negative_trough = False
            _SNR = 0.0
            _acf1 = 1.0
            _is_white_noise = False
            _res_std = np.inf
            _r0_V_qc = np.nan
            _qc_left_r = np.nan
            _qc_right_r = np.nan
            _qc_right_zc_r = np.nan
            _fitted_qc = None
            _popt_qc = None

        if self.verbose:
            status = "RELIABLE" if _reliable else "UNRELIABLE"
            print(f"\n  Quality gate (step response on g(r)):")
            print(f"    R² = {_R2:.3f}, A = {_A_fit:.3f}, ξ = {_xi_fit:.1f}, λ = {_lam_fit:.1f}")
            print(f"    r_excl = {_r_excl_fit:.1f}, φ = {_phi_fit:.2f}")
            print(f"    → {status}")

        # =============================================================
        # V(r) = -ln(g(r)) from RAW g(r)
        # =============================================================
        g_r_safe = g_r.copy()
        g_r_safe[g_r_safe <= 0] = 1e-10
        v_r = -np.log(g_r_safe)
        valid = g_r > 0.05
        r_valid = r_values[valid]
        v_r_valid = v_r[valid]

        g_r_smooth_safe = g_r_smooth.copy()
        g_r_smooth_safe[g_r_smooth_safe <= 0] = 1e-10
        v_r_smooth = -np.log(g_r_smooth_safe)

        end_search_rad = len(r_valid) // 2

        # Guided minimum from QC
        if not np.isnan(_r0_V_qc):
            v_min_index_guided = np.argmin(np.abs(r_valid - _r0_V_qc))
        else:
            v_min_index_guided = np.argmin(v_r_valid[:end_search_rad])
        r_0_guided = r_valid[v_min_index_guided]

        # Raw argmin (Yamamoto)
        v_min_index_raw = np.argmin(v_r_valid[:end_search_rad])
        r_0_raw = r_valid[v_min_index_raw]

        v_min_raw = v_r_valid[v_min_index_guided]

        if self.verbose:
            print(f"\n  V(r) minimum:")
            print(f"    Guided: r_0 = {r_0_guided:.1f} px")
            print(f"    Argmin: r_0 = {r_0_raw:.1f} px (diff = {abs(r_0_guided - r_0_raw):.1f} px)")
            print(f"    V(r_0) raw = {v_min_raw:.4f}")
            print(f"    g(r) peak = {g_peak:.3f}")

        # =============================================================
        # FITTING REGIONS
        # =============================================================
        fitting_half_width = self.fitting_half_width
        _margin_pts = 3

        # Raw region: ±hw around argmin
        _fs_raw = max(0, v_min_index_raw - fitting_half_width)
        _fe_raw = min(v_min_index_raw + fitting_half_width + 1, end_search_rad)
        r_fit_raw = r_valid[_fs_raw:_fe_raw]
        v_fit_raw = v_r_valid[_fs_raw:_fe_raw]

        # Guided well region: left_ZC - margin ... right_ZC + margin
        if not np.isnan(_qc_left_r) and not np.isnan(_qc_right_r):
            _left_idx_g = max(0, np.argmin(np.abs(r_valid - _qc_left_r)) - _margin_pts)
            _right_idx_g = min(len(r_valid), np.argmin(np.abs(r_valid - _qc_right_r)) + _margin_pts + 1)
        else:
            _left_idx_g = max(0, v_min_index_guided - fitting_half_width)
            _right_idx_g = min(v_min_index_guided + fitting_half_width + 1, end_search_rad)
        r_fit_guided = r_valid[_left_idx_g:_right_idx_g]
        v_fit_guided = v_r_valid[_left_idx_g:_right_idx_g]

        if self.verbose:
            print(f"\n  Fitting regions:")
            print(f"    Raw (Yamamoto): [{r_fit_raw[0]:.1f}, {r_fit_raw[-1]:.1f}] px ({len(r_fit_raw)} pts)")
            print(f"    Guided (well):  [{r_fit_guided[0]:.1f}, {r_fit_guided[-1]:.1f}] px ({len(r_fit_guided)} pts)")
            print(f"    DS: determined from V(r) zero crossing (see below)")

        # =============================================================
        # 5 K METHODS — all on V(r)
        # =============================================================

        # --- 1. Quadratic raw (Yamamoto, argmin) ---
        _coeffs_qr = None
        try:
            _coeffs_qr = np.polyfit(r_fit_raw, v_fit_raw, 2)
            K_quad_raw = np.round(2 * np.abs(_coeffs_qr[0]), 6)
        except Exception:
            K_quad_raw = np.nan

        # --- 2. Morse raw (argmin region) ---
        K_morse_raw = np.nan
        _popt_mr = None
        if len(r_fit_raw) >= 5:
            try:
                _popt_mr, _ = curve_fit(
                    morse_potential, r_fit_raw, v_fit_raw,
                    p0=[abs(v_fit_raw.min()), 0.1,
                        np.clip(r_0_raw, r_fit_raw[0], r_fit_raw[-1]),
                        v_fit_raw.min()],
                    bounds=([0, 0, r_fit_raw[0], -np.inf],
                            [np.inf, np.inf, r_fit_raw[-1], np.inf]),
                    maxfev=5000)
                K_morse_raw = np.round(2 * _popt_mr[0] * _popt_mr[1]**2, 6)
            except RuntimeError:
                pass

        # --- 3. Quadratic guided ---
        _coeffs_qg = None
        try:
            _coeffs_qg = np.polyfit(r_fit_guided, v_fit_guided, 2)
            K_quad_guided = np.round(2 * np.abs(_coeffs_qg[0]), 6)
        except Exception:
            K_quad_guided = np.nan

        # --- 4. Morse guided ---
        K_morse_guided = np.nan
        _popt_mg = None
        r0_fit = r_0_guided
        if len(r_fit_guided) >= 5:
            try:
                _popt_mg, _pcov_mg = curve_fit(
                    morse_potential, r_fit_guided, v_fit_guided,
                    p0=[abs(v_fit_guided.min()), 0.1,
                        np.clip(r_0_guided, r_fit_guided[0], r_fit_guided[-1]),
                        v_fit_guided.min()],
                    bounds=([0, 0, r_fit_guided[0], -np.inf],
                            [np.inf, np.inf, r_fit_guided[-1], np.inf]),
                    maxfev=5000)
                D_e_fit, a_fit, r0_fit, offset_fit = _popt_mg
                K_morse_guided = np.round(2 * D_e_fit * a_fit**2, 6)
                r0_fit = np.round(r0_fit, 3)
            except RuntimeError:
                r0_fit = r_0_guided

        # --- 5. K_ds from QC step response (panel a) directly ---
        # The step response already fits g(r) perfectly. Derive K from it:
        # V(r) = -ln(g_fitted) → K_ds = V''(r₀)
        # No separate fitting step — one fit, two outputs (reliability + K).
        K_ds = np.nan
        _popt_ds = _popt_qc  # same fit as QC
        if _popt_qc is not None and not np.isnan(_r0_V_qc):
            try:
                K_ds = float(np.round(_Vpp_ds_qc[_V_min_idx_qc], 6))
                K_ds = max(K_ds, 0.0)
            except Exception:
                K_ds = np.nan

        # For plotter: DS data = g(r)-1 from QC trim point
        if not np.isnan(_r_excl_fit):
            _fc_idx_ds = np.argmin(np.abs(r_values - _r_excl_fit))
        else:
            _fc_idx_ds = 0
        r_fit_ds = r_values[_fc_idx_ds:]
        v_fit_ds = signal_gr[_fc_idx_ds:]

        K = K_morse_guided  # backward compatibility

        if self.verbose:
            print(f"\n  K values (px⁻²):")
            print(f"    1. Quad raw:     {K_quad_raw}")
            print(f"    2. Morse raw:    {K_morse_raw}")
            print(f"    3. Quad guided:  {K_quad_guided}")
            print(f"    4. Morse guided: {K_morse_guided}")
            print(f"    5. DS on V(r):   {K_ds}")
            print(f"    r0_fit = {r0_fit}")

        # =============================================================
        # RMSE: all 5 evaluated on the GUIDED well region
        # =============================================================
        rmse_quad_raw = np.nan
        rmse_morse_raw = np.nan
        rmse_quad_guided = np.nan
        rmse_morse_guided = np.nan
        rmse_ds = np.nan

        if len(r_fit_guided) >= 5:
            _r_eval = r_fit_guided
            _v_eval = v_fit_guided

            if _coeffs_qr is not None:
                try:
                    rmse_quad_raw = float(np.sqrt(np.mean((_v_eval - np.polyval(_coeffs_qr, _r_eval))**2)))
                except: pass
            if _popt_mr is not None:
                try:
                    rmse_morse_raw = float(np.sqrt(np.mean((_v_eval - morse_potential(_r_eval, *_popt_mr))**2)))
                except: pass
            if _coeffs_qg is not None:
                try:
                    rmse_quad_guided = float(np.sqrt(np.mean((_v_eval - np.polyval(_coeffs_qg, _r_eval))**2)))
                except: pass
            if _popt_mg is not None:
                try:
                    rmse_morse_guided = float(np.sqrt(np.mean((_v_eval - morse_potential(_r_eval, *_popt_mg))**2)))
                except: pass
            if _popt_qc is not None:
                try:
                    _g_pred = 1.0 + _step_response(_r_eval, *_popt_qc)
                    _g_pred = np.maximum(_g_pred, 1e-10)
                    _v_pred_ds = -np.log(_g_pred)
                    rmse_ds = float(np.sqrt(np.mean((_v_eval - _v_pred_ds)**2)))
                except: pass

            if self.verbose:
                print(f"\n  RMSE on guided well ({len(_r_eval)} pts):")
                print(f"    Quad raw:     {rmse_quad_raw:.4f}" if not np.isnan(rmse_quad_raw) else "    Quad raw:     N/A")
                print(f"    Morse raw:    {rmse_morse_raw:.4f}" if not np.isnan(rmse_morse_raw) else "    Morse raw:    N/A")
                print(f"    Quad guided:  {rmse_quad_guided:.4f}" if not np.isnan(rmse_quad_guided) else "    Quad guided:  N/A")
                print(f"    Morse guided: {rmse_morse_guided:.4f}" if not np.isnan(rmse_morse_guided) else "    Morse guided: N/A")
                print(f"    DS on V(r):   {rmse_ds:.4f}" if not np.isnan(rmse_ds) else "    DS on V(r):   N/A")

        # --- Normalized collective order metrics (from guided Morse) ---
        K_Vmin = K * abs(v_min_raw) if not np.isnan(K) else np.nan
        K_gpeak = K * (g_peak - 1) if not np.isnan(K) else np.nan

        if self.verbose:
            print(f"  K_Vmin  = K × |V_min| = {K_Vmin:.4f}" if not np.isnan(K_Vmin) else "  K_Vmin  = NaN")
            print(f"  K_gpeak = K × (g_peak-1) = {K_gpeak:.4f}" if not np.isnan(K_gpeak) else "  K_gpeak = NaN")

        return {
            'n_cells':         len(y_coords),
            'n_interior':      len(interior_indices),
            # 5 K values
            'K_quad_raw':      K_quad_raw,
            'K_morse_raw':     K_morse_raw,
            'K_quad_guided':   K_quad_guided,
            'K_morse_guided':  K_morse_guided,
            'K_ds':            K_ds,
            'K':               K,  # backward compat = K_morse_guided
            'K_Vmin':          K_Vmin,
            'K_gpeak':         K_gpeak,
            # 5 RMSE values
            'rmse_quad_raw':      rmse_quad_raw,
            'rmse_morse_raw':     rmse_morse_raw,
            'rmse_quad_guided':   rmse_quad_guided,
            'rmse_morse_guided':  rmse_morse_guided,
            'rmse_ds':            rmse_ds,
            'r0_fit':          r0_fit,
            'v_min':           float(np.round(v_min_raw, 3)),
            'g_peak':          g_peak,
            # quality gate (step response)
            'reliable':        _reliable,
            'has_peak':        _has_positive_peak,
            'has_crossing':    _has_zero_crossing,
            'has_trough':      _has_negative_trough,
            'R2_damped':       round(_R2, 4),
            'R2_full':         round(_R2_full, 4),
            'A_damped':        round(_A_fit, 4) if not np.isnan(_A_fit) else np.nan,
            'xi_damped':       round(_xi_fit, 2) if not np.isnan(_xi_fit) else np.nan,
            'lambda_damped':   round(_lam_fit, 2) if not np.isnan(_lam_fit) else np.nan,
            'r_excl_damped':   round(_r_excl_fit, 2) if not np.isnan(_r_excl_fit) else np.nan,
            'phi_damped':      round(_phi_fit, 4) if not np.isnan(_phi_fit) else np.nan,
            'SNR':             round(_SNR, 3),
            'ACF1':            round(_acf1, 3),
            # curves
            'r_values':        r_values,
            'g_r':             g_r,
            'g_r_smooth':      g_r_smooth,
            'v_r':             v_r,
            'r_valid':         r_valid,
            'v_r_valid':       v_r_valid,
            # fitting regions
            'r_fit_raw':       r_fit_raw,
            'v_fit_raw':       v_fit_raw,
            'r_fit_guided':    r_fit_guided,
            'v_fit_guided':    v_fit_guided,
            'r_fit_ds':        r_fit_ds,
            'v_fit_ds':        v_fit_ds,
            # fit parameters
            'popt_qc':         _popt_qc if _fitted_qc is not None else None,
            'coeffs_qr':       _coeffs_qr,
            'coeffs_qg':       _coeffs_qg,
            'popt_mr':         _popt_mr,
            'popt_mg':         _popt_mg,
            'popt_ds':         _popt_ds,
        }

    def collective_order_pipeline(self, image_path, centroids=None, image_dims=None, reporter=None):
        """
        Full pipeline: load image → segment → classic metrics → collective order.

        Assembles results from all components into one dict.

        Parameters
        ----------
        image_path : str
            Path to the input image.
        centroids : np.ndarray, optional
            Pre-computed centroids (N, 2) for centroid-only mode.
        image_dims : tuple, optional
            (H, W) for centroid-only mode.
        reporter : PipelineReporter, optional
            If provided, emits structured status updates per step.

        Returns
        -------
        dict
            Combined results from all pipeline stages.
        """
        if reporter is None:
            reporter = PipelineReporter(PIPELINE_STEPS, verbose=self.verbose)

        if centroids is not None and image_dims is not None:
            # Centroid-only mode: skip image loading and segmentation
            reporter.skip('load')
            reporter.skip('preprocess')
            reporter.skip('segment')
            reporter.skip('metrics')

            reporter.start('gr')
            try:
                co_results = self.compute_collective_order(centroids, image_dims)
                reporter.done('gr', {'n_interior': co_results.get('n_interior'), 'g_peak': co_results.get('g_peak')})
                reporter.done('quality', {'reliable': co_results.get('reliable'), 'R2_damped': co_results.get('R2_damped'), 'SNR': co_results.get('SNR')})
                reporter.done('fitting', {'K': co_results.get('K'), 'K_ds': co_results.get('K_ds'), 'r0_fit': co_results.get('r0_fit')})
            except Exception as e:
                reporter.fail('gr', e)
                raise

            co_results['image_path'] = str(image_path)
            co_results['_reporter'] = reporter.get_board()
            return co_results

        # --- Normal mode: full pipeline ---

        # 1. Load image
        reporter.start('load')
        try:
            input_image = self._load_image(image_path)
            reporter.done('load')
        except Exception as e:
            reporter.fail('load', e)
            raise

        # 2. Preprocess (if machine output)
        if self.is_input_image_machine_output:
            reporter.start('preprocess')
            try:
                cell_area, machine_metrics, dot_centroids = self.cleaning_preprocessing(input_image)
                reporter.done('preprocess', {
                    'machine_CD': machine_metrics.get('CD', '?') if machine_metrics else '?',
                })
            except Exception as e:
                reporter.fail('preprocess', e)
                raise
        else:
            reporter.skip('preprocess')
            cell_area = input_image
            machine_metrics = None
            dot_centroids = None

        if self.invert_image:
            cell_area = 255 - cell_area

        # 3. Segmentation
        reporter.start('segment')
        try:
            objects, segmentor = self.segmentation(cell_area)
            centroids = np.array([o.centroid for o in objects])
            areas = np.array([o.area for o in objects])
            reporter.done('segment', {'n_cells': len(objects)})
        except Exception as e:
            reporter.fail('segment', e)
            raise

        # 4. Classic metrics
        reporter.start('metrics')
        try:
            classic_metrics_seg = self._compute_classic_metrics(centroids, areas, segmentor.H, segmentor.W, method='segmentation')
            classic_metrics_vor = self._compute_classic_metrics(centroids, areas, segmentor.H, segmentor.W, method='voronoi',
                                                               dot_centroids=dot_centroids)
            reporter.done('metrics', {
                'CD_calc': round(classic_metrics_seg.get('CD_calc', 0), 1),
                'Ave_calc': round(classic_metrics_seg.get('Ave_calc', 0), 1),
                'HEX_calc': round(classic_metrics_seg.get('HEX_calc', 0), 1),
            })
        except Exception as e:
            reporter.fail('metrics', e)
            raise

        # 5. Collective order (g(r) + quality gate + fitting)
        reporter.start('gr')
        try:
            co_results = self.compute_collective_order(centroids, (segmentor.H, segmentor.W))
            reporter.done('gr', {
                'n_interior': co_results.get('n_interior'),
                'g_peak': round(co_results.get('g_peak', 0), 3),
            })
        except Exception as e:
            reporter.fail('gr', e)
            raise

        reporter.done('quality', {
            'reliable': co_results.get('reliable'),
            'R2_damped': co_results.get('R2_damped'),
            'SNR': co_results.get('SNR'),
        })

        reporter.done('fitting', {
            'K': co_results.get('K'),
            'K_ds': co_results.get('K_ds'),
            'r0_fit': co_results.get('r0_fit'),
        })

        # 6. Assemble full results
        results = {
            # image data
            'image_path':      str(image_path),
            'input_image':     input_image,
            'cell_area':       cell_area,
            'machine_metrics': machine_metrics,
            'dot_centroids':   dot_centroids,
            # segmentation data (plain arrays — picklable)
            'segmentation': {
                'H': segmentor.H,
                'W': segmentor.W,
                'labels': segmentor.labels,
                'enhanced_image': segmentor.enhanced_image,
                'blobs': segmentor.blobs,
                'global_fg': segmentor.global_fg,
                'centroids': centroids,
                'areas': areas,
                'cell_labels': np.array([o.label for o in objects]),
                'n_cells': len(objects),
            },
            # classic metrics
            **classic_metrics_seg,
            'voronoi_metrics': classic_metrics_vor,
            # collective order
            **co_results,
            # reporter board
            '_reporter': reporter.get_board(),
        }

        return results

    def _compute_residual_field(self, co_results):
        """
        Build Delaunay truss from collective_order_pipeline results and compute
        per-node residual force vectors from the fitted interaction potential.

        Parameters
        ----------
        co_results : dict
            Output of collective_order_pipeline().

        Returns
        -------
        dict with spatial force field data, or None if insufficient cells.
        """
        from scipy.spatial import Delaunay

        seg = co_results.get('segmentation', {})
        if not seg or seg.get('n_cells', 0) < 10:
            return None

        H, W = seg['H'], seg['W']
        px = self.pixel_size

        # Extract centroids and interior mask
        centroids = seg['centroids']  # (N, 2) row, col
        MAX_R = int(min(H * self.ay, W * self.ax) * self.exclusion_ratio)
        MAX_R_x = MAX_R / self.ax
        MAX_R_y = MAX_R / self.ay
        y, x = centroids[:, 0], centroids[:, 1]
        interior = ((y >= MAX_R_y) & (y <= H - MAX_R_y) &
                     (x >= MAX_R_x) & (x <= W - MAX_R_x))
        pts = centroids[interior]
        if len(pts) < 10:
            return None

        # Convert to (x, y) in µm
        sx, sy = self.pixel_size_xy
        pts_um = np.column_stack([pts[:, 1] * sx, pts[:, 0] * sy])
        n = len(pts_um)

        # Delaunay triangulation → unique edges
        tri = Delaunay(pts_um)
        edge_set = set()
        for s in tri.simplices:
            for i in range(3):
                for j in range(i + 1, 3):
                    edge_set.add((min(s[i], s[j]), max(s[i], s[j])))
        edges = np.array(list(edge_set))

        # Edge vectors and lengths
        p1 = pts_um[edges[:, 0]]
        p2 = pts_um[edges[:, 1]]
        delta = p2 - p1
        d_um = np.sqrt(np.sum(delta**2, axis=1))
        unit = delta / d_um[:, None]

        # Fitted potential parameters (convert pixel → µm)
        A = co_results.get('A_damped', np.nan)
        xi = co_results.get('xi_damped', np.nan) * px
        lam = co_results.get('lambda_damped', np.nan) * px
        r_excl = co_results.get('r_excl_damped', np.nan) * px
        phi = co_results.get('phi_damped', np.nan)

        if any(np.isnan(v) for v in [A, xi, lam, r_excl, phi]):
            return None

        # Reconstruct g(r) and g'(r) analytically
        def _gr(r):
            t = np.maximum(r - r_excl, 0.0)
            Hv = 1.0 / (1.0 + np.exp(-(r - r_excl) / 0.3))
            osc = -A * np.exp(-t / xi) * np.sin(2 * np.pi * t / lam + phi)
            return np.maximum(Hv * (1.0 + osc), 1e-6)

        def _dgdr(r):
            t = np.maximum(r - r_excl, 0.0)
            Hv = 1.0 / (1.0 + np.exp(-(r - r_excl) / 0.3))
            decay = np.exp(-t / xi)
            sin_t = np.sin(2 * np.pi * t / lam + phi)
            cos_t = np.cos(2 * np.pi * t / lam + phi)
            return Hv * A * decay * ((1.0 / xi) * sin_t - (2 * np.pi / lam) * cos_t)

        # Per-edge force: F(r) = g'(r)/g(r), positive = repulsive
        gr = _gr(d_um)
        dgdr = _dgdr(d_um)
        F_scalar = dgdr / gr
        F_scalar[gr < 0.05] = 0.0  # clamp exclusion zone blow-ups

        # Equilibrium distance r0
        r_test = np.linspace(r_excl, r_excl + lam, 500)
        r0 = r_test[np.argmax(_gr(r_test))]

        # Per-node residual force vector and signed strain
        F_residual = np.zeros((n, 2))
        strain_sum = np.zeros(n)
        strain_count = np.zeros(n)
        for k, (i, j) in enumerate(edges):
            f_vec = F_scalar[k] * unit[k]
            F_residual[j] += f_vec
            F_residual[i] -= f_vec
            # Signed strain: (d - r0) / r0 — positive = tension, negative = compression
            s = (d_um[k] - r0) / r0
            strain_sum[i] += s; strain_sum[j] += s
            strain_count[i] += 1; strain_count[j] += 1
        strain_count[strain_count == 0] = 1
        signed_strain = strain_sum / strain_count

        F_mag = np.sqrt(np.sum(F_residual**2, axis=1))
        compressed = d_um < r0

        # Hot spots: top 10% by |F|
        threshold_90 = np.percentile(F_mag, 90)
        hot_spots = F_mag >= threshold_90

        return {
            # Spatial data
            'pts_um':           pts_um,
            'edges':            edges,
            'd_um':             d_um,
            'r0':               float(r0),
            'F_scalar':         F_scalar,
            'F_residual':       F_residual,
            'F_mag':            F_mag,
            'signed_strain':    signed_strain,
            'compressed':       compressed,
            'hot_spots':        hot_spots,
            'threshold_90':     float(threshold_90),
            'n_interior':       n,
            'n_edges':          len(edges),
            # Scalar summaries
            'mean_F':           float(np.mean(F_mag)),
            'std_F':            float(np.std(F_mag)),
            'mean_signed_strain': float(np.mean(signed_strain)),
            'spatial_cv':       float(np.std(F_mag) / np.mean(F_mag)) if np.mean(F_mag) > 1e-8 else 0.0,
            'frac_compression': float(compressed.sum() / len(edges)),
            'n_hot_spots':      int(hot_spots.sum()),
        }

    def mechanical_state(self, image_path, reporter=None):
        """
        Complete mechanical diagnostic of a corneal endothelial image.

        Runs the full pipeline: segmentation → collective order → residual force field.
        Returns everything needed for patient assessment and surgical planning.

        Parameters
        ----------
        image_path : str or Path
            Path to the specular microscopy image.
        reporter : PipelineReporter, optional
            If provided, emits structured status updates per step.

        Returns
        -------
        dict containing:
            - All collective_order_pipeline outputs (K_ds, quality gate, g(r), fitted params, ...)
            - Residual force field (nodes, edges, forces, vectors, hot spots)
            - Scalar summaries (mean_F, frac_compression, spatial_cv)
        """
        if reporter is None:
            reporter = PipelineReporter(PIPELINE_STEPS, verbose=self.verbose)

        # Run collective order (segmentation + fitting + quality gate)
        co = self.collective_order_pipeline(image_path, reporter=reporter)

        # Compute residual field from collective order results
        reporter.start('force')
        try:
            rf = self._compute_residual_field(co)
            co['residual_field'] = rf
            if rf is not None:
                co['mean_F'] = rf['mean_F']
                co['frac_compression'] = rf['frac_compression']
                co['spatial_cv'] = rf['spatial_cv']
                co['n_hot_spots'] = rf['n_hot_spots']
                co['mean_signed_strain'] = rf['mean_signed_strain']
                reporter.done('force', {
                    'mean_F': round(rf['mean_F'], 4),
                    'frac_compression': round(rf['frac_compression'], 2),
                    'n_hot_spots': rf['n_hot_spots'],
                })
            else:
                co['mean_F'] = np.nan
                co['frac_compression'] = np.nan
                co['spatial_cv'] = np.nan
                co['n_hot_spots'] = 0
                co['mean_signed_strain'] = np.nan
                reporter.skip('force')
        except Exception as e:
            reporter.fail('force', e)
            raise

        co['_reporter'] = reporter.get_board()
        return co

    def _build_potential_functions(self, co_results):
        """Build V(r), V'(r), g(r) closures from fitted params (µm units)."""
        px = self.pixel_size
        A = co_results['A_damped']
        xi = co_results['xi_damped'] * px
        lam = co_results['lambda_damped'] * px
        r_excl = co_results['r_excl_damped'] * px
        phi = co_results['phi_damped']

        def _gr(r):
            t = np.maximum(r - r_excl, 0.0)
            Hv = 1.0 / (1.0 + np.exp(-(r - r_excl) / 0.3))
            osc = -A * np.exp(-t / xi) * np.sin(2 * np.pi * t / lam + phi)
            return np.maximum(Hv * (1.0 + osc), 1e-6)

        def _V(r):
            return -np.log(_gr(r))

        def _dVdr(r):
            g = _gr(r)
            t = np.maximum(r - r_excl, 0.0)
            Hv = 1.0 / (1.0 + np.exp(-(r - r_excl) / 0.3))
            decay = np.exp(-t / xi)
            sin_t = np.sin(2 * np.pi * t / lam + phi)
            cos_t = np.cos(2 * np.pi * t / lam + phi)
            dgdr = Hv * A * decay * ((1.0 / xi) * sin_t - (2 * np.pi / lam) * cos_t)
            result = -dgdr / g
            result[g < 0.05] = 0.0
            return result

        r_test = np.linspace(r_excl, r_excl + lam, 500)
        r0 = r_test[np.argmax(_gr(r_test))]

        return _gr, _V, _dVdr, r0, r_excl

    def _collective_order_safe(self, image_path):
        """Wrapper for parallel use — catches exceptions so one failure doesn't kill the pool."""
        try:
            return self.mechanical_state(image_path)
        except Exception as e:
            print(f"  FAILED: {Path(image_path).name} — {e}")
            return {'image_path': str(image_path), 'error': str(e)}


    def collective_order_batch(self, folder_path, n_workers=1,
                           extensions=('.jpg', '.jpeg', '.png', '.tiff', '.bmp'),
                           progress_cb=None, save_full=False):
        """
        Batch process all images in a folder.
        
        Parameters
        ----------
        save_full : bool
            If True, keep full results including centroids, residual_field,
            g(r) curves, and fit parameters. Warning: large memory footprint.
            If False (default), strip heavy data and keep only scalars.
        """
        valid_extensions = extensions
        p = Path(folder_path)
        image_paths = [img_path for img_path in p.rglob('*.*')
                    if img_path.suffix.lower() in valid_extensions]

        print(f"Found {len(image_paths)} images in {folder_path}")

        if not image_paths:
            return []

        cpu_count = os.cpu_count() or 4
        n_workers = min(n_workers, len(image_paths), cpu_count)

        original_verbose = self.verbose
        self.verbose = False

        n_failed = 0
        results = []
        total = len(image_paths)
        pbar = tqdm(total=total, desc="Processing", unit="img",
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} "
                            "[{elapsed}<{remaining}, {rate_fmt}] {postfix}")

        if n_workers <= 1:
            for idx, img_path in enumerate(image_paths):
                pbar.set_postfix_str(img_path.name, refresh=False)
                r = self._collective_order_safe(img_path)
                if 'error' in r:
                    n_failed += 1
                    pbar.set_postfix_str(f"FAILED: {img_path.name}", refresh=False)
                if not save_full:
                    # Strip heavy data — keep only scalars and small dicts
                    for key in ('segmentation', 'cell_area', 'input_image',
                                'dot_centroids', 'residual_field', '_reporter',
                                'g_r_smooth', 'v_r',
                                'r_valid', 'v_r_valid',
                                'r_fit_raw', 'v_fit_raw', 'r_fit_guided', 'v_fit_guided',
                                'r_fit_ds', 'v_fit_ds',
                                'popt_qc', 'coeffs_qr', 'coeffs_qg',
                                'popt_mr', 'popt_mg', 'popt_ds'):
                        r.pop(key, None)
                results.append(r)
                pbar.update(1)
                if progress_cb:
                    progress_cb(idx + 1, total,
                                phase=f"Image {idx+1}/{total}",
                                message=img_path.name,
                                n_failed=n_failed)
        else:
            config = {
                'pixel_size':               self.pixel_size_xy,
                'is_input_image_machine_output': self.is_input_image_machine_output,
                'fcm_method':               self.fcm_method,
                'min_expansion_shells':     self.min_expansion_shells,
                'min_interior_cells_ratio': self.min_interior_cells_ratio,
                'exclusion_ratio':          self.exclusion_ratio,
                'shell_thickness':          self.shell_thickness,
                'fitting_half_width':       self.fitting_half_width,
                'SAVGOL_WINDOW':            self.SAVGOL_WINDOW,
                'SAVGOL_ORDER':             self.SAVGOL_ORDER,
                'fitting_method':           self.fitting_method,
                'verbose':                  False,
                '_save_full':               save_full,
            }

            str_paths = [str(p) for p in image_paths]
            print(f"Launching {n_workers} workers ...")

            idx = 0
            with Pool(processes=n_workers,
                    initializer=_worker_init,
                    initargs=(config,)) as pool:
                for r in pool.imap_unordered(_worker_process_image, str_paths):
                    idx += 1
                    if 'error' in r:
                        n_failed += 1
                        pbar.set_postfix_str(f"FAILED: {Path(r['image_path']).name}",
                                            refresh=False)
                    else:
                        pbar.set_postfix_str(Path(r['image_path']).name, refresh=False)
                    results.append(r)
                    pbar.update(1)
                    if progress_cb:
                        progress_cb(idx, total,
                                    phase=f"Image {idx}/{total}",
                                    message=Path(r['image_path']).name,
                                    n_failed=n_failed)

        pbar.close()
        self.verbose = original_verbose

        n_ok = len(results) - n_failed
        print(f"\nBatch complete: {n_ok}/{len(image_paths)} succeeded")
        return results
    
    def plot(self, results, save=False, save_dir='cornealia_results', formats=('png', 'pdf')):
        return cornealia_plotter(results, save=save, save_dir=save_dir, formats=formats)


# ======================================================================
# Module-level worker for multiprocessing (Windows spawn-safe)
# ======================================================================
# _worker_init  runs ONCE per worker process (Pool initializer).
#               It creates a single cornealia instance that persists for
#               the lifetime of that worker → EasyOCR loaded once per worker.
#
# _worker_process_image  runs per image, reusing the pre-built instance.
#
# Both must be module-level (not methods) so Windows spawn can find them.

_worker_instance = None
_worker_save_full = False

def _worker_init(config):
    """Called once when each worker process starts."""
    global _worker_instance, _worker_save_full
    _worker_save_full = config.pop('_save_full', False)
    _worker_instance = cornealia(**config)
    # Pre-warm the OCR reader so the first image isn't slow
    _worker_instance._get_ocr_reader()

def _worker_process_image(image_path):
    """Process one image using the worker's persistent cornealia instance."""
    try:
        result = _worker_instance.mechanical_state(image_path)

        if not _worker_save_full:
            # Remove heavy data — keep only scalars and small arrays
            # Keep r_values and g_r (small arrays ~76 floats) for g(r) population NPZ
            for key in ('segmentation', 'cell_area', 'input_image',
                         'dot_centroids', 'residual_field', '_reporter',
                         'g_r_smooth', 'v_r',
                         'r_valid', 'v_r_valid',
                         'r_fit_raw', 'v_fit_raw', 'r_fit_guided', 'v_fit_guided',
                         'r_fit_ds', 'v_fit_ds',
                         'popt_qc', 'coeffs_qr', 'coeffs_qg',
                         'popt_mr', 'popt_mg', 'popt_ds'):
                result.pop(key, None)

        return result
    except Exception as e:
        return {'image_path': str(image_path), 'error': str(e)}


# =====================================================================
# CLI
# =====================================================================

def _cli_process_one(args):
    """Worker for CLI batch mode — returns row dict, g(r) curve, centroids."""
    import warnings
    warnings.filterwarnings('ignore')

    img_path_str, pixel_size, invert, cellade_params = args
    img_path = Path(img_path_str)
    _sx, _sy = (pixel_size, pixel_size) if np.ndim(pixel_size) == 0 else pixel_size
    px2 = _sx * _sy                 # pixel area = s^2
    s_eff = float(np.sqrt(px2))     # effective pixel size

    proc = cornealia(
        is_input_image_machine_output=False,
        fitting_method='morse',
        pixel_size=pixel_size,
        invert_image=invert,
        cellade_params=cellade_params if cellade_params else {},
        verbose=False,
    )

    try:
        r = proc.mechanical_state(str(img_path))

        def safe(key, scale=1):
            v = r.get(key, np.nan)
            if v is None or (isinstance(v, float) and np.isnan(v)):
                return np.nan
            return round(v / scale, 6)

        row = {
            'Image_Name':          img_path.stem,
            'n_cells':             r.get('n_cells'),
            'n_interior':          r.get('n_interior'),
            'CD_calc':             r.get('CD_calc'),
            'Ave_calc':            r.get('Ave_calc'),
            'SD_calc':             r.get('SD_calc'),
            'CV_calc':             r.get('CV_calc'),
            'HEX_calc':            r.get('HEX_calc'),
            'K_quad_raw_um':       safe('K_quad_raw', px2),
            'K_morse_raw_um':      safe('K_morse_raw', px2),
            'K_quad_guided_um':    safe('K_quad_guided', px2),
            'K_morse_guided_um':   safe('K_morse_guided', px2),
            'K_ds_um':             safe('K_ds', px2),
            'K_um':                safe('K', px2),
            'K_Vmin_um':           safe('K_Vmin', px2),
            'K_gpeak_um':          safe('K_gpeak', px2),
            'r0_um':               round(r.get('r0_fit', np.nan) * s_eff, 3)
                                   if not np.isnan(r.get('r0_fit', np.nan)) else np.nan,
            'v_min':               r.get('v_min', np.nan),
            'g_peak':              r.get('g_peak', np.nan),
            'mean_F':              r.get('mean_F', np.nan),
            'frac_compression':    r.get('frac_compression', np.nan),
            'spatial_cv':          r.get('spatial_cv', np.nan),
            'n_hot_spots':         r.get('n_hot_spots', 0),
            'reliable':            r.get('reliable', False),
            'R2_damped':           r.get('R2_damped', np.nan),
            'R2_full':             r.get('R2_full', np.nan),
            'A_damped':            r.get('A_damped', np.nan),
            'xi_damped':           r.get('xi_damped', np.nan),
            'lambda_damped':       r.get('lambda_damped', np.nan),
            'r_excl_damped':       r.get('r_excl_damped', np.nan),
            'phi_damped':          r.get('phi_damped', np.nan),
            'SNR':                 r.get('SNR', np.nan),
            'ACF1':                r.get('ACF1', np.nan),
            'rmse_quad_raw':       r.get('rmse_quad_raw', np.nan),
            'rmse_morse_raw':      r.get('rmse_morse_raw', np.nan),
            'rmse_quad_guided':    r.get('rmse_quad_guided', np.nan),
            'rmse_morse_guided':   r.get('rmse_morse_guided', np.nan),
            'rmse_ds':             r.get('rmse_ds', np.nan),
        }

        gr_curve = {
            'r':   r.get('r_values', np.array([])),
            'g_r': r.get('g_r', np.array([])),
        }

        seg = r.get('segmentation', {})
        centroids = seg.get('centroids', np.empty((0, 2)))

        return {'status': 'ok', 'row': row, 'gr': gr_curve, 'centroids': centroids}

    except Exception as e:
        return {'status': 'error', 'image': img_path.name, 'error': str(e)}


def _cli_single(args):
    """Process a single image from CLI."""
    import json
    from pathlib import Path

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image not found: {image_path}")
        return

    pixel_size = args.pixel_size[0] if len(args.pixel_size) == 1 else tuple(args.pixel_size)
    _sx, _sy = (pixel_size, pixel_size) if np.ndim(pixel_size) == 0 else pixel_size
    px2 = _sx * _sy
    cellade_params = json.loads(args.cellade_params) if args.cellade_params else None

    output_dir = Path(args.output) if args.output else image_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Image:   {image_path.name}")
    print(f"Pixel:   {pixel_size} µm/px")
    print(f"Machine: {args.machine}")
    print(f"Output:  {output_dir}")

    engine = cornealia(
        pixel_size=pixel_size,
        is_input_image_machine_output=args.machine,
        invert_image=args.invert,
        cellade_params=cellade_params or {},
        verbose=True,
    )

    results = engine.collective_order_pipeline(str(image_path))

    # Print key results
    print(f"\n{'='*50}")
    print(f"Cells:    {results['n_cells']} ({results['n_interior']} interior)")
    print(f"Reliable: {results['reliable']}")
    print(f"K (px⁻²):  {results['K']}")
    print(f"K (µm⁻²):  {round(results['K'] / px2, 6) if results['K'] is not None else 'N/A'}")
    print(f"K_ds:      {results['K_ds']}")
    print(f"r0 (px):   {results['r0_fit']}")
    print(f"g_peak:    {results['g_peak']:.3f}")
    print(f"CD:        {results.get('CD_calc', 'N/A')} cells/mm²")
    print(f"Ave:       {results.get('Ave_calc', 'N/A')} µm²")
    print(f"CV:        {results.get('CV_calc', 'N/A')}%")
    print(f"HEX:       {results.get('HEX_calc', 'N/A')}%")

    # Save JSON
    scalar_results = {k: v for k, v in results.items()
                      if isinstance(v, (int, float, str, bool))}
    json_path = output_dir / f"{image_path.stem}_results.json"
    with open(json_path, 'w') as f:
        json.dump(scalar_results, f, indent=2, default=str)
    print(f"\nJSON:    {json_path}")

    # Generate plots if requested
    if args.plot:
        plots_dir = output_dir / f"{image_path.stem}_plots"
        plots_dir.mkdir(exist_ok=True)
        engine.plot(results, save=True, save_dir=str(plots_dir), formats=('png',))
        print(f"Plots:   {plots_dir}")

    print("Done.")


def _cli_batch(args):
    """Run batch processing from CLI arguments."""
    import json
    from datetime import datetime
    from concurrent.futures import ProcessPoolExecutor, as_completed

    folder = Path(args.folder)
    pixel_size = args.pixel_size[0] if len(args.pixel_size) == 1 else tuple(args.pixel_size)
    n_workers = args.workers
    invert = args.invert
    cellade_params = json.loads(args.cellade_params) if args.cellade_params else None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(args.output) / f"cornealia_batch_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect images
    exts = args.formats.split(',')
    images = []
    for ext in exts:
        images += sorted(folder.glob(f'*.{ext.strip()}'))
    images = sorted(set(images))

    if not images:
        print(f"No images found in {folder} with extensions {exts}")
        return

    print(f"Images:  {len(images)}")
    print(f"Workers: {n_workers}")
    print(f"Pixel:   {pixel_size} um/px")
    print(f"Invert:  {invert}")
    print(f"Output:  {output_dir}")

    work = [(str(p), pixel_size, invert, cellade_params) for p in images]
    rows, failed, gr_curves, centroids_dict = [], [], {}, {}

    t0 = pd.Timestamp.now()

    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = {executor.submit(_cli_process_one, w): w for w in work}
        done = 0
        for future in as_completed(futures):
            done += 1
            result = future.result()
            if result['status'] == 'ok':
                rows.append(result['row'])
                name = result['row']['Image_Name']
                gr_curves[name] = result['gr']
                centroids_dict[name] = result['centroids']
            else:
                failed.append(result)

            if done % 50 == 0 or done == len(images):
                elapsed = (pd.Timestamp.now() - t0).total_seconds()
                rate = done / elapsed if elapsed > 0 else 0
                eta = (len(images) - done) / rate if rate > 0 else 0
                print(f"\r  [{done}/{len(images)}] {rate:.1f} img/s | "
                      f"ok={len(rows)} fail={len(failed)} | ETA {eta:.0f}s",
                      end='', flush=True)

    print()
    elapsed_total = (pd.Timestamp.now() - t0).total_seconds()

    # Save CSV
    df = pd.DataFrame(rows)
    csv_path = output_dir / 'results.csv'
    df.to_csv(csv_path, index=False)

    # Save g(r) NPZ
    all_r_lens = [len(gr_curves[n]['r']) for n in gr_curves if len(gr_curves[n]['r']) > 0]
    if all_r_lens:
        target_len = max(set(all_r_lens), key=all_r_lens.count)
        r_common = None
        names_out, g_list = [], []
        for n, gr in gr_curves.items():
            if len(gr['r']) == target_len:
                if r_common is None:
                    r_common = gr['r']
                names_out.append(n)
                g_list.append(gr['g_r'])
        g_arr = np.array(g_list) if g_list else np.empty((0, target_len))
        npz_path = output_dir / 'gr_population_data.npz'
        np.savez(npz_path, r=r_common, curves=g_arr,
                 names=np.array(names_out, dtype=object), pixel_size=pixel_size)

    # Save centroids NPZ
    if centroids_dict:
        save_dict = {'names': np.array(list(centroids_dict.keys()), dtype=object)}
        for i, (name, coords) in enumerate(centroids_dict.items()):
            save_dict[f'c{i}'] = coords
        np.savez_compressed(output_dir / 'centroids.npz', **save_dict)

    # Summary
    rel = df[df['reliable'] == True]
    print(f"\n{'='*50}")
    print(f"CSV:      {csv_path} ({len(df)} rows)")
    print(f"Reliable: {len(rel)}/{len(df)} ({100*len(rel)/max(len(df),1):.1f}%)")
    print(f"Failed:   {len(failed)}")
    print(f"Time:     {elapsed_total:.0f}s ({elapsed_total/max(len(images),1):.1f}s/img)")

    if len(rel) > 0:
        v = rel['K_ds_um'].dropna()
        if len(v) > 0:
            print(f"K_ds:     {v.mean():.4f} ± {v.std():.4f} µm⁻² (n={len(v)})")

    if failed:
        for f in failed[:5]:
            print(f"  FAIL: {f['image']}: {f['error']}")

    # Save config
    config = {
        'timestamp': timestamp, 'input_folder': str(folder),
        'pixel_size': pixel_size, 'invert': invert, 'n_workers': n_workers,
        'formats': exts, 'total': len(images), 'processed': len(rows),
        'failed': len(failed), 'reliable': int(len(rel)),
        'elapsed_seconds': round(elapsed_total, 1),
    }
    with open(output_dir / 'run_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print(f"Done. Output: {output_dir}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        prog='cornealia',
        description='Cornealia: Collective order analysis of cell monolayers',
    )
    sub = parser.add_subparsers(dest='command')

    # --- single command ---
    sp = sub.add_parser('single', help='Process a single image')
    sp.add_argument('--image', required=True, help='Path to image file')
    sp.add_argument('--output', default=None, help='Output directory (default: same as image)')
    sp.add_argument('--pixel-size', type=float, nargs='+', default=[0.58], help='Pixel size in µm/px: one value (square) or two values SX SY (default: 0.58)')
    sp.add_argument('--machine', action='store_true', help='Input is machine output (has OCR metrics area)')
    sp.add_argument('--invert', action='store_true', help='Invert image contrast (for bright-field)')
    sp.add_argument('--plot', action='store_true', help='Generate plots')
    sp.add_argument('--cellade-params', default=None, help='JSON string of CellADE params')

    # --- batch command ---
    bp = sub.add_parser('batch', help='Process a folder of images in parallel')
    bp.add_argument('--folder', required=True, help='Path to image folder')
    bp.add_argument('--output', required=True, help='Output root directory')
    bp.add_argument('--pixel-size', type=float, nargs='+', default=[0.58], help='Pixel size in µm/px: one value (square) or two values SX SY (default: 0.58)')
    bp.add_argument('--workers', type=int, default=8, help='Number of parallel workers (default: 8)')
    bp.add_argument('--invert', action='store_true', help='Invert image contrast (for bright-field)')
    bp.add_argument('--formats', default='png,jpg,bmp', help='Comma-separated image extensions (default: png,jpg,bmp)')
    bp.add_argument('--cellade-params', default=None, help='JSON string of CellADE params, e.g. \'{"log_min_sigma":5,"log_max_sigma":8}\'')

    args = parser.parse_args()

    if args.command == 'single':
        _cli_single(args)
    elif args.command == 'batch':
        _cli_batch(args)
    else:
        parser.print_help()
