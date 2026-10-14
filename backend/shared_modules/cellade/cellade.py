"""
CellADE — Cell Adaptive Detection Engine
Unified segmentation pipeline with mode presets.

Usage:
    from cellade import CellADE

    # Collective order analysis (fast, centroid-accurate)
    seg = CellADE(mode='cornealia')
    labels = seg.run(image)

    # Benchmark evaluation (full post-processing, boundary-accurate)
    seg = CellADE(mode='benchmark')
    labels, info = seg.run(image, detail=True)

    # Corneal clinical (tuned for specular microscopy)
    seg = CellADE(mode='corneal')
    labels = seg.run(image)

    # Phase contrast (auto-inversion + dual-pass FCM halo recovery)
    seg = CellADE(mode='phase_contrast')
    labels = seg.run(image)   # pass ORIGINAL image, inversion is automatic

    # Custom: override any parameter
    seg = CellADE(mode='phase_contrast', params={'log_min_sigma': 5, 'min_area': 50})
    labels = seg.run(image)
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.ndimage import distance_transform_edt
from skimage import exposure
from skimage.feature import blob_log
from skimage.measure import regionprops, label as relabel
from skimage.segmentation import watershed
import cv2

try:
    from skfuzzy import cmeans
except ImportError:
    cmeans = None  # deferred error if FCM is actually called

# Benchmark operations (available when full package is installed)
try:
    from .operations.base_segmentation import run_cellade_v2
    from .operations.boundary_smoothing import (
        morphological_smooth_all_regions, smooth_all_regions)
    from .operations.curvature import analyze_region_boundary
    from .operations.merging import (
        find_merge_candidates, apply_merges, honeycomb_merge,
        remove_small_fragments)
    from .operations.splitting import apply_splits_chunk_tracking
    from .utils import find_neighbors
    _HAS_OPERATIONS = True
except ImportError:
    try:
        from operations.base_segmentation import run_cellade_v2
        from operations.boundary_smoothing import (
            morphological_smooth_all_regions, smooth_all_regions)
        from operations.curvature import analyze_region_boundary
        from operations.merging import (
            find_merge_candidates, apply_merges, honeycomb_merge,
            remove_small_fragments)
        from operations.splitting import apply_splits_chunk_tracking
        from utils import find_neighbors
        _HAS_OPERATIONS = True
    except ImportError:
        _HAS_OPERATIONS = False


# =================================================================
# PRESETS
# =================================================================

PRESET_CORNEALIA = {
    # Seed detection
    'seeding_method': 'blob_log',
    'log_min_sigma': 6,
    'log_max_sigma': 30,
    'log_num_sigma': 15,
    'log_threshold': 0.01,
    # FFT adaptive sigma estimation
    'use_fft_sigma': True,
    'fft_crop_frac': 0.35,
    'fft_tile_repeats': 4,
    'fft_lowpass_n': 5,             # number of dominant frequencies to keep (overall trend)
    'fft_sigma_range_factor': 0.5,  # min = sigma * (1 - factor), max = sigma * (1 + factor)
    'fft_sigma_max_clamp': 20,      # above this, fall back to calibrated range
    'fft_calibrated_range': (4.5, 11.7),  # data-driven from GT (p5–p95 of 42k cells)
    # Strip-based ROI for FFT
    'fft_n_strips': 8,
    'fft_strip_abs_thresh': 0.002,   # absolute jaggedness floor
    'fft_strip_rel_thresh': 0.4,     # relative to max jaggedness
    'fft_strip_trim_frac': 0.10,     # trim 10% from top/bottom
    'fft_min_coverage': 0.75,        # skip FFT if cell strips < 75%
    # Foreground
    'fcm_mode': 'local',
    'fcm_clusters': 2,
    'fcm_threshold': 0.4,
    # Preprocessing
    'clahe_clip': 0.03,
    # Post-processing — all off except gap fill
    'use_curvature_merging': False,
    'use_morphological_smoothing': False,
    'use_fft_smoothing': False,
    'use_honeycomb_merging': False,
    'use_fragment_removal': False,
    'use_stress_splitting': False,
    'use_intercellular_fill': True,
    # Dark object exclusion (for intercellular fill)
    'use_dark_object_exclusion': True,
    'dob_opening_radius': 5,
    # General
    'min_area': 30,
}

PRESET_BENCHMARK = {
    # Seed detection
    'seeding_method': 'h_maxima',
    'h_maxima_h': 0.05,
    'seed_min_dist': 5,
    'max_radius': 100,
    # Foreground
    'fcm_mode': 'global+local',
    'fcm_clusters': 2,
    'fcm_min_sep': 0.1,
    'fcm_threshold': 0.4,
    'local_fcm_sep': 0.08,
    # Preprocessing
    'clahe_clip': 0.01,
    # Post-processing — all on
    'use_curvature_merging': True,
    'use_morphological_smoothing': True,
    'use_fft_smoothing': True,
    'use_honeycomb_merging': True,
    'use_fragment_removal': True,
    'use_stress_splitting': True,
    'use_intercellular_fill': False,
    # Morphological smoothing
    'morphological_base_radius': 2,
    'morphological_aggressiveness': 1.5,
    # FFT smoothing
    'fft_n_points': 256,
    'fft_min_wavelength': 6,
    'fft_amplitude_threshold': 0.1,
    # Honeycomb
    'honeycomb_small_threshold': 0.5,
    'honeycomb_min_merged_size': 0.3,
    'honeycomb_max_merged_size': 30.0,
    'honeycomb_adjacency_radius': 5,
    # Fragment removal
    'fragment_min_size': 50,
    # Splitting
    'z_threshold': 2.5,
    'cut_peak_to_mean': 1.5,
    'cut_max_z': 2.8,
    'cut_min_region_size': 100,
    'chunk_merge_threshold': 0.10,
    'max_split_iterations': 5,
    'use_neck_score': True,
    'use_cluster_detection': True,
    'min_cluster_size': 5,
    'cluster_max_aspect_ratio': 4.0,
    'sigma_scale': 0.15,
    'z_threshold_low_ratio': 0.5,
    'single_cluster_extend': 0.3,
    'poly_min_area_ratio': 0.15,
    'cut_exclusion_radius': 10,
    # General
    'min_area': 50,
}

PRESET_CORNEAL = {
    # Seed detection
    'seeding_method': 'blob_log',
    'log_min_sigma': 6,
    'log_max_sigma': 30,
    'log_num_sigma': 15,
    'log_threshold': 0.01,
    # Foreground
    'fcm_mode': 'local',
    'fcm_clusters': 2,
    'fcm_threshold': 0.4,
    # Preprocessing
    'clahe_clip': 0.03,
    # Post-processing — selective
    'use_curvature_merging': True,
    'use_morphological_smoothing': True,
    'use_fft_smoothing': False,
    'use_honeycomb_merging': True,
    'use_fragment_removal': True,
    'use_stress_splitting': False,
    'use_intercellular_fill': True,
    # Dark object exclusion (for intercellular fill)
    'use_dark_object_exclusion': True,
    'dob_opening_radius': 5,
    # Morphological smoothing
    'morphological_base_radius': 2,
    'morphological_aggressiveness': 1.5,
    # Honeycomb
    'honeycomb_small_threshold': 0.5,
    'honeycomb_min_merged_size': 0.3,
    'honeycomb_max_merged_size': 30.0,
    'honeycomb_adjacency_radius': 5,
    # Fragment removal
    'fragment_min_size': 30,
    # General
    'min_area': 30,
}

PRESET_PHASE_CONTRAST = {
    # Seed detection
    'seeding_method': 'blob_log',
    'log_min_sigma': 3,
    'log_max_sigma': 15,
    'log_num_sigma': 10,
    'log_threshold': 0.04,
    # FFT adaptive sigma — off by default, user enables per dataset
    'use_fft_sigma': False,
    # Foreground
    'fcm_mode': 'local',
    'fcm_clusters': 2,
    'fcm_threshold': 0.4,
    # Phase-contrast specific: image inversion + halo recovery
    'invert_image': True,
    'use_halo_recovery': True,
    'halo_ring_width_factor': 0.8,   # ring width = factor × sigma
    'halo_ring_min_width': 3,        # minimum ring width in pixels
    'halo_ring_max_width': 15,       # maximum ring width in pixels
    'halo_fcm_threshold': 0.4,       # FCM threshold for halo pass
    'halo_min_ring_pixels': 10,      # skip ring if fewer pixels
    # Patch shape: 'circular' (default, fast) or 'elliptical' (Hessian-guided)
    'fcm_patch_shape': 'elliptical',
    'hessian_max_aspect': 4.0,       # clamp ellipse aspect ratio
    # Preprocessing
    'clahe_clip': 0.03,
    # Post-processing — minimal for speed
    'use_curvature_merging': False,
    'use_morphological_smoothing': False,
    'use_fft_smoothing': False,
    'use_honeycomb_merging': False,
    'use_fragment_removal': False,
    'use_stress_splitting': False,
    'use_intercellular_fill': False,
    # General
    'min_area': 30,
}

# ── IMMUNIA: fluorescent immune cell imaging ──
# Two usage paths controlled by separate_objects at call time:
#   separate_objects=True  → full pipeline (seeds → FCM → watershed → labeled)
#   separate_objects=False → FCM foreground only (binary mask)
PRESET_IMMUNIA = {
    # Seed detection (for NK cells and tumor — small bright blobs)
    'seeding_method': 'blob_log',
    'log_min_sigma': 2,
    'log_max_sigma': 15,
    'log_num_sigma': 10,
    'log_threshold': 0.02,
    # No FFT sigma — fluorescent cells have consistent size
    'use_fft_sigma': False,
    # Foreground
    'fcm_mode': 'local',
    'fcm_clusters': 2,
    'fcm_threshold': 0.4,
    # Preprocessing
    'clahe_clip': 0.03,
    # Post-processing — all off for fluorescent images
    'use_curvature_merging': False,
    'use_morphological_smoothing': False,
    'use_fft_smoothing': False,
    'use_honeycomb_merging': False,
    'use_fragment_removal': False,
    'use_stress_splitting': False,
    'use_intercellular_fill': False,
    'use_dark_object_exclusion': False,
    # Spaghetti removal (optional): drop mesh-like objects whose total
    # boundary (outer + internal hole edges) is much longer than the
    # perimeter of a circle with the same enclosed (hole-filled) area.
    'remove_spaghetti': False,
    'spaghetti_max_ratio': 3.0,
    'spaghetti_min_area': 20,
    # General
    'min_area': 5,
}

PRESETS = {
    'cornealia': PRESET_CORNEALIA,
    'benchmark': PRESET_BENCHMARK,
    'corneal': PRESET_CORNEAL,
    'phase_contrast': PRESET_PHASE_CONTRAST,
    'immunia': PRESET_IMMUNIA,
}

# Verbose keys (all default False)
_VERBOSE_KEYS = [
    'verbose_cellade', 'verbose_merge', 'verbose_filing',
    'verbose_smooth', 'verbose_honeycomb', 'verbose_cleanup',
    'verbose_split',
]


# =================================================================
# CellADE CLASS
# =================================================================

class CellADE:
    """
    Cell Adaptive Detection Engine.

    Pipeline:
        1. preprocess          — grayscale → normalize → CLAHE (+ inversion for phase contrast)
        2. detect_seeds        — blob_log or h_maxima (with optional FFT sigma)
        3. extract_foreground  — FCM (global / local / global+local)
       3b. recover_halo        — dual-pass FCM on original polarity (phase contrast only)
        5. initial_segmentation — markers → distance → watershed
        6. merge_by_curvature  — fix over-segmentation (optional)
        7. smooth_morphological — edge filing (optional)
        8. smooth_fft          — FFT boundary filter (optional)
        9. merge_honeycomb     — small fragment merging (optional)
       10. remove_fragments    — size-based cleanup (optional)
       11. split_by_stress     — Poisson/Von Mises neck cut (optional)
       12. fill_intercellular_gaps — watershed expansion into thin gaps (optional)
       13. extract_properties  — regionprops + min_area filter
    """

    def __init__(self, mode: Optional[str] = None,
                 params: Optional[Dict] = None):
        """
        Args:
            mode: 'cornealia', 'benchmark', 'corneal', 'phase_contrast', or None.
            params: Override dict — applied on top of mode preset.
        """
        # Start from preset or empty
        if mode is not None:
            if mode not in PRESETS:
                raise ValueError(
                    f"Unknown mode '{mode}'. Choose from {list(PRESETS)}")
            self.params = {**PRESETS[mode]}
        else:
            self.params = {**PRESET_BENCHMARK}  # default fallback

        # Set verbose keys to False unless overridden
        for k in _VERBOSE_KEYS:
            self.params.setdefault(k, False)

        # User overrides
        if params:
            self.params.update(params)

        # Store mode name for reporting
        self._mode_name = mode or 'custom'

        # Internal state (populated during run)
        self.image_raw = None
        self.enhanced = None
        self.enhanced_original = None  # original-polarity enhanced (phase contrast)
        self.seeds = None
        self._seed_geometry = None     # (a, b, theta) per seed (elliptical mode)
        self.foreground = None
        self.labels = None
        self.objects = None

    # =============================================================
    # STEP 1: PREPROCESSING
    # =============================================================

    def preprocess(self, image: np.ndarray) -> None:
        """Grayscale conversion, normalization, CLAHE enhancement.
        
        For phase-contrast mode (invert_image=True): stores the enhanced
        original-polarity image for halo recovery, then inverts before
        CLAHE so the pipeline sees bright-on-dark.
        """
        self.image_raw = image.copy()

        # Grayscale
        if image.ndim == 3:
            if image.shape[2] == 4:
                image = image[:, :, :3]
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        img = image.astype(np.float32)

        # Normalize to [0, 1]
        img = (img - img.min()) / (img.max() - img.min() + 1e-8)
        self.normalized = img.copy()  # store pre-CLAHE for strip analysis

        # Phase-contrast: enhance ORIGINAL polarity first (for halo pass),
        # then invert for the main pipeline
        clip = self.params.get('clahe_clip', 0.03)
        if self.params.get('invert_image', False):
            self.enhanced_original = exposure.equalize_adapthist(
                img, clip_limit=clip)
            img = 1.0 - img  # invert
            # Re-normalize after inversion
            img = (img - img.min()) / (img.max() - img.min() + 1e-8)
        else:
            self.enhanced_original = None

        # CLAHE
        self.enhanced = exposure.equalize_adapthist(img, clip_limit=clip)
        self.H, self.W = self.enhanced.shape

    # =============================================================
    # STEP 2: SEED DETECTION
    # =============================================================

    def detect_seeds(self) -> None:
        """Detect cell centers via blob_log or h_maxima."""
        method = self.params.get('seeding_method', 'blob_log')

        if method == 'blob_log' and self.params.get('use_fft_sigma', False):
            self._detect_seeds_two_stage()
        elif method == 'blob_log':
            self._detect_seeds_blob_log()
        elif method == 'h_maxima':
            self._detect_seeds_h_maxima()
        else:
            raise ValueError(f"Unknown seeding_method: '{method}'")

    def _detect_seeds_two_stage(self) -> None:
        """Two-stage seed detection: strip jaggedness ROI → FFT → final LoG."""
        from scipy.ndimage import uniform_filter1d

        # Stage 1: Strip jaggedness on normalized image (pre-CLAHE)
        raw = self.normalized

        n_strips = self.params.get('fft_n_strips', 8)
        trim_frac = self.params.get('fft_strip_trim_frac', 0.10)
        abs_thresh = self.params.get('fft_strip_abs_thresh', 0.002)
        rel_thresh_frac = self.params.get('fft_strip_rel_thresh', 0.4)

        H, W = raw.shape
        strip_width = W // n_strips
        trim = int(H * trim_frac)

        jaggedness = []
        strip_centers = []
        for i in range(n_strips):
            x0 = i * strip_width
            x1 = min((i + 1) * strip_width, W)
            profile = raw[trim:H - trim, x0:x1].mean(axis=1)
            d1 = np.diff(profile)
            jag = float(np.mean(np.abs(d1)))
            jaggedness.append(jag)
            strip_centers.append((x0 + x1) / 2)

        max_jag = max(jaggedness) if jaggedness else 0
        rel_thresh = max_jag * rel_thresh_frac
        thresh = max(abs_thresh, rel_thresh)
        has_cells = [j > thresh for j in jaggedness]

        cell_strip_count = sum(has_cells)
        coverage = cell_strip_count / n_strips

        # Store diagnostics
        self._strip_info = {
            'jaggedness': jaggedness,
            'has_cells': has_cells,
            'coverage': float(coverage),
            'threshold': float(thresh),
            'abs_thresh': float(abs_thresh),
            'rel_thresh': float(rel_thresh),
        }

        # Decision: FFT or skip?
        min_coverage = self.params.get('fft_min_coverage', 0.75)
        if coverage < min_coverage:
            # Partial image — skip FFT, use defaults
            self._fft_sigma_estimate = {
                'source': 'default',
                'reason': f'low_coverage_{coverage:.0%}',
                'coverage': float(coverage),
            }
            self._detect_seeds_blob_log()
        else:
            # Stage 2: FFT on cell region centroid
            cell_x = [strip_centers[i] for i in range(n_strips) if has_cells[i]]
            centroid_x = np.mean(cell_x)
            centroid_y = H / 2  # vertical center

            frac = self.params.get('fft_crop_frac', 0.35)
            ch = int(H * np.sqrt(frac))
            cw = int(W * np.sqrt(frac))
            y0 = int(np.clip(centroid_y - ch / 2, 0, H - ch))
            x0 = int(np.clip(centroid_x - cw / 2, 0, W - cw))

            self._estimate_sigma_fft(crop_box=(y0, x0, ch, cw))

            # Stage 3: LoG with FFT-derived range
            self._detect_seeds_blob_log()

        # Stage 4: Remove seeds in empty strips
        if any(not hc for hc in has_cells):
            empty_ranges = [(i * strip_width, min((i + 1) * strip_width, W))
                            for i in range(n_strips) if not has_cells[i]]
            keep = np.ones(len(self.seeds), dtype=bool)
            for j, (sy, sx, ss) in enumerate(self.seeds):
                for ex0, ex1 in empty_ranges:
                    if ex0 <= sx < ex1:
                        keep[j] = False
                        break
            n_removed = (~keep).sum()
            self.seeds = self.seeds[keep]
            self._seed_coords = self._seed_coords[keep]
            self._strip_info['seeds_removed'] = int(n_removed)

    def _estimate_sigma_fft(self, crop_box=None) -> None:
        """Estimate cell sigma from FFT of enhanced image.
        If crop_box is given as (y0, x0, h, w), use that region.
        Otherwise fall back to center crop.
        Updates log_min_sigma and log_max_sigma in self.params."""

        img = self.enhanced
        H, W = img.shape

        if crop_box is not None:
            y0, x0, ch, cw = crop_box
            cropped = img[y0:y0+ch, x0:x0+cw]
        else:
            # Center crop (fallback)
            frac = self.params.get('fft_crop_frac', 0.35)
            ch, cw = int(H * np.sqrt(frac)), int(W * np.sqrt(frac))
            y0, x0 = (H - ch) // 2, (W - cw) // 2
            cropped = img[y0:y0+ch, x0:x0+cw]

        if cropped.size < 100:
            self._fft_sigma_estimate = {'source': 'default', 'reason': 'crop_too_small'}
            return

        # Mirror tile
        tile_n = self.params.get('fft_tile_repeats', 4)
        row = cropped
        for i in range(1, tile_n):
            row = np.concatenate([row, cropped[:, ::-1] if i % 2 else cropped], axis=1)
        tiled = row
        for i in range(1, tile_n):
            tiled = np.concatenate([tiled, row[::-1, :] if i % 2 else row], axis=0)

        tH, tW = tiled.shape

        # 2D FFT → radial profile
        F = np.fft.fftshift(np.abs(np.fft.fft2(tiled - tiled.mean())))
        cy, cx = tH // 2, tW // 2
        Y, X = np.ogrid[:tH, :tW]
        r = np.sqrt((Y - cy)**2 + (X - cx)**2).astype(int)
        max_r = min(cy, cx)
        radial = np.zeros(max_r)
        for ri in range(max_r):
            mask = r == ri
            if mask.any():
                radial[ri] = F[mask].mean()

        # Whiten: remove 1/f trend
        min_fi = max(3, int(max_r * 0.01))
        freqs = np.arange(min_fi, len(radial))
        log_f = np.log(freqs + 1)
        log_p = np.log(radial[min_fi:] + 1e-8)
        coeffs = np.polyfit(log_f, log_p, 1)
        trend = np.exp(np.polyval(coeffs, log_f))
        whitened = radial[min_fi:] / (trend + 1e-8)

        # Low-pass: keep only n dominant frequencies for overall trend
        W_fft = np.fft.rfft(whitened)
        n_keep = self.params.get('fft_lowpass_n', 3)
        W_fft[n_keep:] = 0
        smoothed = np.fft.irfft(W_fft, n=len(whitened))

        # Skip initial rise, find peak
        median_val = np.median(smoothed)
        search_start = 0
        for i in range(len(smoothed)):
            if smoothed[i] >= median_val:
                search_start = i
                break
        peak_local = search_start + np.argmax(smoothed[search_start:])
        peak_idx = peak_local + min_fi
        peak_freq = peak_idx / max(tH, tW)

        # Convert to sigma
        cell_spacing = 1.0 / (peak_freq + 1e-8)
        median_radius = cell_spacing / 2.0
        estimated_sigma = median_radius / np.sqrt(2)

        # Store diagnostics
        self._fft_sigma_estimate = {
            'estimated_sigma': float(estimated_sigma),
            'peak_idx': int(peak_idx),
            'cell_spacing': float(cell_spacing),
        }

        # Decide: use FFT estimate or fall back to calibrated range
        max_clamp = self.params.get('fft_sigma_max_clamp', 20)
        cal_range = self.params.get('fft_calibrated_range', None)

        if estimated_sigma <= max_clamp:
            # FFT gave a reasonable value — use it
            self._fft_sigma_estimate['source'] = 'fft'
            self._fft_sigma_estimate['used_sigma'] = float(estimated_sigma)
            factor = self.params.get('fft_sigma_range_factor', 0.5)
            self.params['log_min_sigma'] = max(2, estimated_sigma * (1 - factor))
            self.params['log_max_sigma'] = estimated_sigma * (1 + factor)
        elif cal_range is not None:
            # FFT outlier — fall back to calibrated data-driven range directly
            self._fft_sigma_estimate['source'] = 'calibrated'
            self._fft_sigma_estimate['used_sigma'] = float((cal_range[0] + cal_range[1]) / 2)
            self.params['log_min_sigma'] = max(2, cal_range[0])
            self.params['log_max_sigma'] = cal_range[1]
        else:
            # No calibration available — keep defaults
            self._fft_sigma_estimate['source'] = 'default'

    def _detect_seeds_blob_log(self) -> None:
        """Multi-scale Laplacian-of-Gaussian blob detection."""
        blobs = blob_log(
            self.enhanced,
            min_sigma=self.params.get('log_min_sigma', 5),
            max_sigma=self.params.get('log_max_sigma', 30),
            num_sigma=self.params.get('log_num_sigma', 15),
            threshold=self.params.get('log_threshold', 0.01),
            overlap=self.params.get('log_overlap', 0.5),
        )
        # blobs: (y, x, sigma) — store as (N, 3)
        self.seeds = blobs
        self._seed_coords = blobs[:, :2].astype(int)  # (y, x)

    def _detect_seeds_h_maxima(self) -> None:
        """H-maxima seed detection (from benchmark pipeline)."""
        from skimage.morphology import reconstruction
        from skimage.feature import peak_local_max

        h = self.params.get('h_maxima_h', 0.05)
        min_dist = self.params.get('seed_min_dist', 5)

        # H-maxima: suppress peaks lower than h
        h_max = self.enhanced - reconstruction(
            self.enhanced - h, self.enhanced, method='dilation')

        coords = peak_local_max(
            h_max, min_distance=min_dist, threshold_abs=0,
            exclude_border=True)

        # Store as (N, 3) with sigma=0 for consistency
        self.seeds = np.column_stack(
            [coords, np.zeros(len(coords))]) if len(coords) > 0 \
            else np.empty((0, 3))
        self._seed_coords = coords  # (y, x)

    # =============================================================
    # STEP 3: FOREGROUND EXTRACTION
    # =============================================================

    def extract_foreground(self) -> None:
        """Fuzzy C-Means foreground segmentation."""
        mode = self.params.get('fcm_mode', 'local')

        if cmeans is None:
            raise ImportError("scikit-fuzzy is required: pip install scikit-fuzzy")

        if mode == 'global':
            self._fcm_global()
        elif mode == 'local':
            self._fcm_local()
        elif mode == 'global+local':
            self._fcm_global()
            self._fcm_local_refine()
        else:
            raise ValueError(f"Unknown fcm_mode: '{mode}'")

    def _fcm_global(self) -> None:
        """Single FCM on the full image."""
        data = self.enhanced.reshape(-1, 1).T.astype(np.float64)
        cntr, u, *_ = cmeans(
            data=data, c=self.params.get('fcm_clusters', 2),
            m=2, error=0.005, maxiter=100, init=None)
        fg_idx = np.argmax(cntr.flatten())
        threshold = self.params.get('fcm_threshold', 0.4)
        self.foreground = (u[fg_idx] > threshold).reshape(self.H, self.W)

    def _fcm_local(self) -> None:
        """Per-seed patch FCM — circular or elliptical (Hessian-guided)."""
        H, W = self.H, self.W
        sqrt2 = np.sqrt(2)
        threshold = self.params.get('fcm_threshold', 0.4)
        use_ellipse = self.params.get('fcm_patch_shape', 'circular') == 'elliptical'
        fg = np.zeros((H, W), dtype=bool)

        # Precompute Hessian geometry for all seeds if elliptical
        if use_ellipse:
            self._seed_geometry = self._compute_hessian_geometry()

        for i in range(len(self.seeds)):
            y, x = int(self.seeds[i, 0]), int(self.seeds[i, 1])
            sigma = self.seeds[i, 2] if self.seeds.shape[1] > 2 else 10

            if use_ellipse and i < len(self._seed_geometry):
                a, b, theta = self._seed_geometry[i]
                bbox_r = int(max(a, b)) + 1
            else:
                a = b = sigma * sqrt2 * 1.5
                theta = 0.0
                bbox_r = int(a) + 1

            y0, y1 = max(0, y - bbox_r), min(H, y + bbox_r)
            x0, x1 = max(0, x - bbox_r), min(W, x + bbox_r)

            yy, xx = np.ogrid[y0:y1, x0:x1]
            patch_mask = self._ellipse_mask(yy, xx, y, x, a, b, theta)

            patch = np.where(patch_mask, self.enhanced[y0:y1, x0:x1], 0)
            data = patch.reshape(-1, 1).T.astype(np.float64)

            try:
                cntr, u, *_ = cmeans(
                    data=data, c=self.params.get('fcm_clusters', 2),
                    m=2, error=0.005, maxiter=100, init=None)

                fg_idx = np.argmax(cntr.flatten())
                patch_fg = (u[fg_idx] > threshold).reshape(patch.shape)
                fg[y0:y1, x0:x1] |= (patch_fg & patch_mask)
            except Exception:
                continue

        self.foreground = fg

    def _compute_hessian_geometry(self):
        """Compute ellipse parameters (a, b, theta) per seed from image Hessian.

        At each seed location, the Hessian matrix of the Gaussian-smoothed
        image encodes the local curvature along two principal axes.
        The eigenvalue ratio gives the aspect ratio; eigenvectors give
        orientation.  This turns each circular LoG seed into an oriented
        elliptical neighborhood that follows the cell's actual shape.

        Returns:
            List of (semi_major, semi_minor, angle_rad) per seed.
        """
        from scipy.ndimage import gaussian_filter
        sqrt2 = np.sqrt(2)
        scale_factor = sqrt2 * 1.5  # same as circular radius / sigma
        max_aspect = self.params.get('hessian_max_aspect', 4.0)
        geometry = []

        for i in range(len(self.seeds)):
            y, x = int(self.seeds[i, 0]), int(self.seeds[i, 1])
            sigma = self.seeds[i, 2] if self.seeds.shape[1] > 2 else 10
            base_radius = sigma * scale_factor

            # Smooth at the seed's scale
            s = max(sigma, 1.0)
            smoothed = gaussian_filter(self.enhanced, sigma=s)

            # Compute Hessian components at (y, x)
            # Use a small window to estimate second derivatives
            H, W = self.H, self.W
            dy = max(1, int(s * 0.5))

            if (y - dy < 0 or y + dy >= H or x - dy < 0 or x + dy >= W):
                # Near border — fall back to circular
                geometry.append((base_radius, base_radius, 0.0))
                continue

            Iyy = (smoothed[y+dy, x] - 2*smoothed[y, x] + smoothed[y-dy, x]) / (dy**2)
            Ixx = (smoothed[y, x+dy] - 2*smoothed[y, x] + smoothed[y, x-dy]) / (dy**2)
            Ixy = (smoothed[y+dy, x+dy] - smoothed[y+dy, x-dy]
                   - smoothed[y-dy, x+dy] + smoothed[y-dy, x-dy]) / (4 * dy**2)

            # Eigenvalues and eigenvectors of Hessian
            hess = np.array([[Iyy, Ixy], [Ixy, Ixx]])
            eigvals, eigvecs = np.linalg.eigh(hess)

            # Both eigenvalues should be negative for bright blobs (after inversion)
            # Use absolute values — ratio gives aspect ratio
            abs_eigs = np.abs(eigvals)
            if abs_eigs.min() < 1e-10:
                geometry.append((base_radius, base_radius, 0.0))
                continue

            ratio = np.sqrt(abs_eigs.max() / abs_eigs.min())
            ratio = min(ratio, max_aspect)  # clamp

            # Semi-axes: preserve approximate area (a*b ≈ r²)
            semi_major = base_radius * np.sqrt(ratio)
            semi_minor = base_radius / np.sqrt(ratio)

            # Angle: eigenvector of the SMALLER |eigenvalue| = major axis direction
            # (less curvature = more extent along that axis)
            minor_eig_idx = np.argmax(abs_eigs)  # more curvature = minor axis
            major_eig_idx = 1 - minor_eig_idx
            theta = np.arctan2(eigvecs[0, major_eig_idx],
                               eigvecs[1, major_eig_idx])

            geometry.append((semi_major, semi_minor, theta))

        return geometry

    @staticmethod
    def _ellipse_mask(yy, xx, cy, cx, a, b, theta):
        """Create a boolean ellipse mask on an ogrid.

        Args:
            yy, xx: ogrid arrays
            cy, cx: center coordinates
            a: semi-major axis length
            b: semi-minor axis length
            theta: rotation angle in radians

        Returns:
            Boolean mask of the same shape as the ogrid region.
        """
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        dy = yy - cy
        dx = xx - cx
        # Rotate coordinates into ellipse frame
        u = cos_t * dx + sin_t * dy
        v = -sin_t * dx + cos_t * dy
        return (u**2 / (a**2 + 1e-8) + v**2 / (b**2 + 1e-8)) <= 1.0

    def _fcm_local_refine(self) -> None:
        """Refine existing global foreground with per-seed local FCM."""
        H, W = self.H, self.W
        sqrt2 = np.sqrt(2)
        sep = self.params.get('local_fcm_sep', 0.08)

        for i in range(len(self.seeds)):
            y, x = int(self.seeds[i, 0]), int(self.seeds[i, 1])
            sigma = self.seeds[i, 2] if self.seeds.shape[1] > 2 else 10
            radius = int(sigma * sqrt2 * 1.5)

            y0, y1 = max(0, y - radius), min(H, y + radius)
            x0, x1 = max(0, x - radius), min(W, x + radius)

            yy, xx = np.ogrid[y0:y1, x0:x1]
            circle = (yy - y)**2 + (xx - x)**2 <= radius**2

            patch = np.where(circle, self.enhanced[y0:y1, x0:x1], 0)
            data = patch.reshape(-1, 1).T.astype(np.float64)

            cntr, u, *_ = cmeans(
                data=data, c=2, m=2, error=0.005, maxiter=100, init=None)

            c_sorted = np.sort(cntr.flatten())
            if (c_sorted[1] - c_sorted[0]) < sep:
                continue  # ambiguous — skip refinement

            fg_idx = np.argmax(cntr.flatten())
            patch_fg = (u[fg_idx] > self.params.get('fcm_threshold', 0.4)
                        ).reshape(patch.shape)
            self.foreground[y0:y1, x0:x1] |= (patch_fg & circle)

    # =============================================================
    # STEP 3b: HALO RECOVERY (phase-contrast mode)
    # =============================================================

    def recover_halo(self) -> None:
        """Dual-pass FCM halo recovery for phase-contrast images.

        Phase-contrast optics produce a bright halo ring around dark cell
        bodies.  After image inversion the core becomes bright (captured
        by pass-1 FCM), but the halo ring becomes dark and is excluded.

        This second pass searches an annular region around each seed —
        starting just outside the pass-1 foreground — and runs FCM on the
        **original** (non-inverted) enhanced image.  In original polarity
        the halo is brighter than the gray background, so the bright
        cluster correctly captures the halo pixels.

        The ring shape (circular or elliptical) matches the FCM patch shape,
        and width scales with the seed's LoG sigma.
        """
        if self.enhanced_original is None:
            return  # not a phase-contrast run

        H, W = self.H, self.W
        fg_core = self.foreground.copy()
        fg_expanded = self.foreground.copy()

        width_factor = self.params.get('halo_ring_width_factor', 0.8)
        min_width = self.params.get('halo_ring_min_width', 3)
        max_width = self.params.get('halo_ring_max_width', 15)
        halo_thresh = self.params.get('halo_fcm_threshold', 0.4)
        min_ring_px = self.params.get('halo_min_ring_pixels', 10)
        use_ellipse = self.params.get('fcm_patch_shape', 'circular') == 'elliptical'

        n_recovered = 0
        sqrt2 = np.sqrt(2)

        for i in range(len(self.seeds)):
            y, x = int(self.seeds[i, 0]), int(self.seeds[i, 1])
            sigma = self.seeds[i, 2] if self.seeds.shape[1] > 2 else 5.0

            halo_width = int(np.clip(
                sigma * width_factor, min_width, max_width))

            if use_ellipse and hasattr(self, '_seed_geometry') and i < len(self._seed_geometry):
                a_inner, b_inner, theta = self._seed_geometry[i]
                a_outer = a_inner + halo_width
                b_outer = b_inner + halo_width
                bbox_r = int(max(a_outer, b_outer)) + 1
            else:
                radius_inner = int(sigma * sqrt2 * 1.5)
                a_inner = b_inner = float(radius_inner)
                a_outer = b_outer = float(radius_inner + halo_width)
                theta = 0.0
                bbox_r = int(a_outer) + 1

            # Bounding box
            y0, y1 = max(0, y - bbox_r), min(H, y + bbox_r)
            x0, x1 = max(0, x - bbox_r), min(W, x + bbox_r)

            yy, xx = np.ogrid[y0:y1, x0:x1]
            outer_mask = self._ellipse_mask(yy, xx, y, x, a_outer, b_outer, theta)

            # Ring mask: within outer ellipse, outside existing foreground
            ring = outer_mask & ~fg_core[y0:y1, x0:x1]

            if ring.sum() < min_ring_px:
                continue

            # FCM on ORIGINAL enhanced intensity within the ring
            ring_pixels = self.enhanced_original[y0:y1, x0:x1][ring]
            data = ring_pixels.reshape(1, -1).astype(np.float64)

            try:
                cntr, u, *_ = cmeans(
                    data=data, c=2, m=2, error=0.005,
                    maxiter=50, init=None)
                # Bright cluster = halo in original polarity
                bright_idx = np.argmax(cntr.flatten())
                halo_pixels = u[bright_idx] > halo_thresh

                # Map accepted halo pixels back to image coordinates
                ring_coords = np.where(ring)
                for idx in range(len(halo_pixels)):
                    if halo_pixels[idx]:
                        ry, rx = ring_coords[0][idx], ring_coords[1][idx]
                        fg_expanded[y0 + ry, x0 + rx] = True
                        n_recovered += 1
            except Exception:
                continue  # FCM failed on this patch — skip

        self.foreground = fg_expanded
        self._halo_info = {
            'pixels_recovered': n_recovered,
            'core_area': int(fg_core.sum()),
            'expanded_area': int(fg_expanded.sum()),
        }

    # =============================================================
    # STEP 4: INITIAL SEGMENTATION
    # =============================================================

    def initial_segmentation(self) -> None:
        """Marker-controlled watershed on distance transform."""
        markers = np.zeros((self.H, self.W), dtype=np.int32)
        for i, (y, x) in enumerate(self._seed_coords):
            y, x = int(y), int(x)
            if 0 <= y < self.H and 0 <= x < self.W:
                markers[y, x] = i + 1

        seed_mask = markers > 0
        dist = distance_transform_edt(~seed_mask)
        self.labels = watershed(dist, markers=markers, mask=self.foreground)

    # =============================================================
    # STEP 5: CURVATURE-BASED MERGING
    # =============================================================

    def merge_by_curvature(self) -> None:
        """Merge over-segmented regions based on boundary curvature."""
        self._require_operations('merge_by_curvature')
        verbose = self.params.get('verbose_merge', False)

        neighbors, shared_boundaries = find_neighbors(self.labels)
        analyses = {}
        for rid in range(1, self.labels.max() + 1):
            analyses[rid] = analyze_region_boundary(
                self.labels, rid, debug=verbose)

        pairs = find_merge_candidates(
            self.labels, analyses, neighbors, shared_boundaries,
            verbose=verbose)

        if pairs:
            self.labels = apply_merges(self.labels, pairs)

    # =============================================================
    # STEP 6: MORPHOLOGICAL SMOOTHING
    # =============================================================

    def smooth_morphological(self) -> None:
        """Morphological open/close smoothing of region boundaries."""
        self._require_operations('smooth_morphological')
        self.labels = morphological_smooth_all_regions(
            self.labels, self.params)

    # =============================================================
    # STEP 7: FFT BOUNDARY SMOOTHING
    # =============================================================

    def smooth_fft(self) -> None:
        """FFT-based boundary smoothing per region."""
        self._require_operations('smooth_fft')
        self.labels, _ = smooth_all_regions(self.labels, self.params)

    # =============================================================
    # STEP 8: HONEYCOMB MERGING
    # =============================================================

    def merge_honeycomb(self) -> None:
        """Merge small adjacent fragments (honeycomb pattern)."""
        self._require_operations('merge_honeycomb')
        self.labels = honeycomb_merge(self.labels, self.params)

    # =============================================================
    # STEP 9: FRAGMENT REMOVAL
    # =============================================================

    def remove_fragments(self) -> None:
        """Remove regions below size threshold."""
        self._require_operations('remove_fragments')
        self.labels = remove_small_fragments(self.labels, self.params)

    # =============================================================
    # STEP 10: STRESS-BASED SPLITTING
    # =============================================================

    def split_by_stress(self) -> None:
        """Poisson → Von Mises → neck detection → iterative cut."""
        self._require_operations('split_by_stress')
        self.labels, split_info, snapshots = apply_splits_chunk_tracking(
            self.labels, self.params)
        self._split_info = split_info
        self._split_snapshots = snapshots

    # =============================================================
    # STEP 11: FILL INTERCELLULAR GAPS
    # =============================================================

    def fill_intercellular_gaps(self) -> None:
        """
        Expand existing cell labels into thin dark inter-cell spaces
        via watershed flooding. Optionally exclude large dark regions
        (guttae, background gaps) using morphological opening.

        Key insight: thin inter-cell boundaries (1-3 px) vanish under
        morphological opening with a disk larger than their width,
        while large dark areas (guttae) survive.

        Flow:
            1. bg_mask = ~foreground
            2. dob_mask = opening(bg_mask, disk(r)) — only large dark areas remain
            3. permissible = ~dob_mask
            4. Watershed from existing labels into permissible area
        """
        from skimage.morphology import binary_opening, disk as disk_elem

        if self.labels.max() == 0:
            return

        if self.params.get('use_dark_object_exclusion', False):
            bg_mask = ~self.foreground
            radius = self.params.get('dob_opening_radius', 5)
            dob_mask = binary_opening(bg_mask, disk_elem(radius))

            # Remove small objects from DOB mask:
            # anything smaller than 0.8 × mean cell area is not a real
            # dark object (guttae) — just a gap artifact from opening
            props = regionprops(self.labels)
            if len(props) > 0:
                mean_area = np.mean([p.area for p in props])
                cutoff = self.params.get('dob_min_area_ratio', 0.8) * mean_area
                from skimage.morphology import remove_small_objects
                dob_mask = remove_small_objects(dob_mask, min_size=int(cutoff))

            permissible = ~dob_mask
            self._dob_mask = dob_mask
        else:
            permissible = np.ones((self.H, self.W), dtype=bool)

        # Watershed expansion from existing labels
        markers = self.labels.copy()
        dist = distance_transform_edt(markers == 0)
        expanded = watershed(dist, markers=markers, mask=permissible)

        self.labels = expanded.astype(np.int32)

    # =============================================================
    # OPTIONAL: SPAGHETTI REMOVAL
    # =============================================================

    def spaghetti_ratios(self, labels: np.ndarray) -> Dict[int, float]:
        """
        Per object: total perimeter (outer boundary + all internal hole
        boundaries) divided by the perimeter of a circle with the same
        enclosed area (holes filled), 2*sqrt(pi*A_filled).
        Solid cells give ~1-1.5; mesh-like 'spaghetti' gives much more.
        Objects smaller than spaghetti_min_area (filled) are skipped.
        """
        min_a = self.params.get('spaghetti_min_area', 20)
        ratios = {}
        for o in regionprops(labels):
            a_filled = getattr(o, 'area_filled', None)
            if a_filled is None:
                a_filled = o.filled_area
            if a_filled < min_a:
                continue
            ratios[o.label] = float(o.perimeter / (2.0 * np.sqrt(np.pi * a_filled)))
        return ratios

    def remove_spaghetti(self) -> None:
        """Remove objects whose spaghetti ratio exceeds spaghetti_max_ratio."""
        max_r = self.params.get('spaghetti_max_ratio', 3.0)
        self.spaghetti_info = self.spaghetti_ratios(self.labels)
        bad = [lab for lab, r in self.spaghetti_info.items() if r > max_r]
        self.spaghetti_removed_ids = bad
        self.spaghetti_removed = np.isin(self.labels, bad) if bad else np.zeros_like(self.labels, bool)
        if bad:
            self.labels = np.where(self.spaghetti_removed, 0, self.labels)

    # =============================================================
    # STEP 12: EXTRACT PROPERTIES
    # =============================================================

    def extract_properties(self) -> None:
        """Compute regionprops and filter by min_area."""
        min_area = self.params.get('min_area', 30)
        all_props = regionprops(self.labels)
        self.objects = [o for o in all_props if o.area >= min_area]

        # Rebuild labels keeping only valid regions
        if len(self.objects) < len(all_props):
            valid_ids = set(o.label for o in self.objects)
            mask = np.isin(self.labels, list(valid_ids))
            self.labels = self.labels * mask

    # =============================================================
    # ORCHESTRATOR
    # =============================================================

    def run(self, image: np.ndarray, detail: bool = False,
            progress_cb=None) -> Tuple[np.ndarray, Optional[Dict]]:
        """
        Run full CellADE pipeline.

        Args:
            image:       Input image (grayscale or RGB, any dtype).
            detail:      If True, return (labels, info_dict).
            progress_cb: Optional callback(fraction, message).

        Returns:
            labels:  Integer label image.
            info:    Per-step metrics (only if detail=True).
        """
        p = self.params
        info = {} if detail else None
        t0 = time.time()

        def _step(frac, msg):
            if progress_cb:
                progress_cb(frac, msg)

        # --- Core pipeline (always runs) ---

        _step(0.00, 'Preprocessing...')
        self.preprocess(image)

        _step(0.05, 'Detecting seeds...')
        self.detect_seeds()
        if detail:
            info['n_seeds'] = len(self.seeds)

        _step(0.10, 'Extracting foreground...')
        self.extract_foreground()

        if p.get('use_halo_recovery', False):
            _step(0.13, 'Recovering halo...')
            self.recover_halo()
            if detail and hasattr(self, '_halo_info'):
                info['halo'] = self._halo_info

        _step(0.15, 'Initial segmentation...')
        self.initial_segmentation()
        if detail:
            info['n_initial'] = int(self.labels.max())

        # --- Post-processing (conditional on flags) ---

        if p.get('use_curvature_merging', False):
            _step(0.25, 'Curvature-based merging...')
            self.merge_by_curvature()

        if p.get('use_morphological_smoothing', False):
            _step(0.35, 'Morphological smoothing...')
            self.smooth_morphological()

        if p.get('use_fft_smoothing', False):
            _step(0.45, 'FFT boundary smoothing...')
            self.smooth_fft()

        if p.get('use_honeycomb_merging', False):
            _step(0.55, 'Honeycomb merging...')
            self.merge_honeycomb()

        if p.get('use_fragment_removal', False):
            _step(0.65, 'Fragment removal...')
            self.remove_fragments()

        if p.get('use_stress_splitting', False):
            _step(0.70, 'Stress-based splitting...')
            self.split_by_stress()

        if p.get('use_intercellular_fill', False):
            _step(0.85, 'Filling intercellular gaps...')
            self.fill_intercellular_gaps()

        if p.get('remove_spaghetti', False):
            _step(0.88, 'Removing spaghetti objects...')
            self.remove_spaghetti()

        # --- Final extraction ---

        _step(0.90, 'Extracting properties...')
        self.extract_properties()

        _step(1.0, f'Done — {len(self.objects)} cells')

        if detail:
            info['n_final'] = len(self.objects)
            info['elapsed_s'] = round(time.time() - t0, 2)
            info['mode'] = self._mode_name
            return self.labels, info

        return self.labels

    def run_foreground_only(self, image: np.ndarray) -> np.ndarray:
        """
        Run FCM foreground extraction only — no seeds, no watershed.
        Returns a binary mask (uint8). Use for channels that don't
        need individual object separation (dead cells, tissue).
        Uses global FCM (no seeds required).
        """
        self.preprocess(image)

        # Force global FCM — local needs seeds which we skip
        original_mode = self.params.get('fcm_mode', 'local')
        self.params['fcm_mode'] = 'global'
        self.extract_foreground()
        self.params['fcm_mode'] = original_mode

        # Clean up: (optional spaghetti removal), fill holes, remove small objects
        from scipy import ndimage as ndi
        from skimage import morphology
        fg = self.foreground
        if self.params.get('remove_spaghetti', False):
            self.labels = relabel(fg > 0)
            self.remove_spaghetti()
            fg = self.labels > 0
        mask = ndi.binary_fill_holes(fg)
        min_area = self.params.get('min_area', 5)
        mask = morphology.remove_small_objects(mask, min_size=min_area)

        return mask.astype(np.uint8)

    # =============================================================
    # UTILITIES
    # =============================================================

    def get_centroids(self) -> np.ndarray:
        """Return (N, 2) array of (y, x) centroids from detected objects."""
        if self.objects is None:
            raise RuntimeError("Call run() first.")
        return np.array([o.centroid for o in self.objects])

    def get_summary(self) -> Dict:
        """Return summary dict: n_cells, mean_area, total_area, etc."""
        if self.objects is None:
            raise RuntimeError("Call run() first.")
        areas = np.array([o.area for o in self.objects])
        return {
            'n_cells': len(self.objects),
            'mean_area': float(areas.mean()) if len(areas) > 0 else 0,
            'std_area': float(areas.std()) if len(areas) > 0 else 0,
            'total_area': int(areas.sum()),
            'image_size': (self.H, self.W),
        }

    def plot_steps(self) -> None:
        """Visual debug: input → enhanced → seeds+fg → labels."""
        import matplotlib.pyplot as plt
        from skimage.color import label2rgb

        fig, axes = plt.subplots(1, 4, figsize=(16, 4))

        # Input
        axes[0].imshow(self.image_raw, cmap='gray')
        axes[0].set_title('Input')

        # Enhanced
        axes[1].imshow(self.enhanced, cmap='gray')
        axes[1].set_title('Enhanced')

        # Foreground + seeds
        axes[2].imshow(self.foreground, cmap='gray')
        if self.seeds is not None:
            for s in self.seeds:
                axes[2].plot(s[1], s[0], 'r+', markersize=4)
        axes[2].set_title(f'FG + Seeds ({len(self.seeds)})')

        # Labels
        axes[3].imshow(label2rgb(
            self.labels, image=self.enhanced, bg_label=0))
        n = len(self.objects) if self.objects else int(self.labels.max())
        axes[3].set_title(f'Segmented ({n} cells)')

        for ax in axes:
            ax.axis('off')
        plt.tight_layout()
        plt.show()

    # =============================================================
    # INTERNAL HELPERS
    # =============================================================

    @staticmethod
    def _require_operations(step_name: str) -> None:
        """Raise if operations/ submodules are not available."""
        if not _HAS_OPERATIONS:
            raise ImportError(
                f"Step '{step_name}' requires the operations/ submodules. "
                f"Install the full CellADE package or use mode='cornealia'.")

# Backward compatibility
DEFAULT_PARAMS = PRESET_BENCHMARK
