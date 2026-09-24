"""
Associa — Stationarizer Module
================================
Makes time-series signals stationary for downstream coupling analysis.

Methods (ordered by gentleness — how much biology they preserve):
    1. bandpass       — Butterworth bandpass filter (best for FA signals)
    2. detrend        — Polynomial detrending (linear, quadratic, auto)
    3. lazy           — Lazy cycle separation via Takens embedding
    4. difference     — First/second differencing (last resort)
    5. bandpass_diff  — Bandpass then difference if still non-stationary
    6. lazy_diff      — Lazy separation then difference if still non-stationary

Each method returns a StationarityResult with full before/after diagnostics.

Author: CelLAB / Han Mechanobiology Lab
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
import numpy as np
import warnings


# ═════════════════════════════════════════════════════════════
# DATA STRUCTURE
# ═════════════════════════════════════════════════════════════

@dataclass
class StationarityDiagnostics:
    """Full stationarity diagnostic battery for a single signal."""
    adf_statistic: float = np.nan
    adf_pvalue: float = np.nan
    kpss_statistic: float = np.nan
    kpss_pvalue: float = np.nan
    pp_pvalue: float = np.nan
    mean: float = np.nan
    std: float = np.nan
    rolling_var_ratio: float = np.nan     # max/min of rolling variance
    spectral_concentration: float = np.nan  # fraction of power in top 3 bins
    has_dominant_cycles: bool = False      # True if spectral_concentration > 0.5
    is_stationary: bool = False
    confidence: str = 'low'               # 'low', 'moderate', 'high'


@dataclass
class StationarityResult:
    """Complete result of a stationarization attempt."""
    signal_in: np.ndarray                 # original input signal
    signal_out: np.ndarray                # transformed signal
    method_used: str                      # e.g. 'bandpass', 'lazy_diff'
    is_stationary: bool = False
    diagnostics_before: StationarityDiagnostics = None
    diagnostics_after: StationarityDiagnostics = None
    warnings: List[str] = field(default_factory=list)
    details: Dict = field(default_factory=dict)   # method-specific extras


# ═════════════════════════════════════════════════════════════
# STATIONARITY DIAGNOSTICS
# ═════════════════════════════════════════════════════════════

def run_diagnostics(signal: np.ndarray, alpha: float = 0.05) -> StationarityDiagnostics:
    """
    Run full stationarity diagnostic battery on a signal.

    Tests:
        - ADF (Augmented Dickey-Fuller): null = unit root (non-stationary)
        - KPSS: null = stationary (opposite of ADF)
        - Phillips-Perron: null = unit root (non-stationary)
        - Rolling variance ratio: detects heteroscedasticity

    Stationarity verdict:
        high:     ADF < α AND KPSS > α AND PP < α AND variance stable
        moderate: ADF < α AND (KPSS > α OR PP < α) AND variance stable
        low:      anything else
    """
    from statsmodels.tsa.stattools import adfuller, kpss as kpss_test

    # Suppress statsmodels FutureWarning about verbose deprecation
    warnings.filterwarnings('ignore', category=FutureWarning, module='statsmodels')

    diag = StationarityDiagnostics()
    y = np.asarray(signal, dtype=np.float64)

    if len(y) < 10:
        diag.warnings = ['Signal too short for stationarity tests']
        return diag

    diag.mean = float(np.mean(y))
    diag.std = float(np.std(y))

    # ADF test
    try:
        adf_result = adfuller(y)
        diag.adf_statistic = float(adf_result[0])
        diag.adf_pvalue = float(adf_result[1])
    except Exception:
        diag.adf_pvalue = 1.0

    # KPSS test
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            stat, p, *_ = kpss_test(y, regression='c', nlags='auto')
            diag.kpss_statistic = float(stat)
            diag.kpss_pvalue = float(p)
            # statsmodels caps KPSS p-value at 0.1 — if warning says "greater than",
            # the actual p is above 0.1 (i.e. supports stationarity).
            # If warning says "smaller than", p is below 0.01 (rejects stationarity).
            for warning in w:
                msg = str(warning.message)
                if "p-value is greater than" in msg:
                    pass  # p > 0.1, good for stationarity — keep as-is
                elif "p-value is smaller than" in msg:
                    diag.kpss_pvalue = 0.0
    except Exception:
        diag.kpss_pvalue = 0.0

    # Phillips-Perron test
    try:
        from arch.unitroot import PhillipsPerron
        diag.pp_pvalue = float(PhillipsPerron(y).pvalue)
    except ImportError:
        # arch not available — skip PP, rely on ADF + KPSS
        diag.pp_pvalue = np.nan
    except Exception:
        diag.pp_pvalue = 1.0

    # Rolling variance test
    diag.rolling_var_ratio = _rolling_variance_ratio(y)
    fails_var = diag.rolling_var_ratio > 2.0

    # Spectral concentration test — detects deterministic cycles
    # that ADF/KPSS miss (e.g., sine waves pass ADF)
    diag.spectral_concentration = _spectral_concentration(y)
    diag.has_dominant_cycles = diag.spectral_concentration > 0.50

    # Verdict
    adf_ok = diag.adf_pvalue < alpha
    kpss_ok = diag.kpss_pvalue > alpha
    pp_ok = diag.pp_pvalue < alpha if np.isfinite(diag.pp_pvalue) else False

    high = (adf_ok and kpss_ok and (pp_ok or np.isnan(diag.pp_pvalue))
            and not fails_var and not diag.has_dominant_cycles)
    moderate = (adf_ok and (kpss_ok or pp_ok)
                and not fails_var and not diag.has_dominant_cycles)

    diag.is_stationary = high or moderate
    diag.confidence = 'high' if high else 'moderate' if moderate else 'low'

    return diag


def _rolling_variance_ratio(y: np.ndarray, window: int = 50, min_window: int = 10) -> float:
    """Ratio of max to min rolling standard deviation. >1.5 suggests non-stationarity."""
    w = min(window, len(y) // 3)
    if w < min_window:
        return 1.0
    stds = np.array([np.std(y[i:i + w]) for i in range(len(y) - w)])
    if len(stds) == 0 or np.min(stds) < 1e-12:
        return 1.0
    return float(np.max(stds) / np.min(stds))


def _spectral_concentration(y: np.ndarray, top_k: int = 2) -> float:
    """
    Fraction of total spectral power in the top-k frequency bins.

    A stationary stochastic signal has power spread across many
    frequencies (low concentration). A signal with deterministic
    cycles concentrates power in a few bins (high concentration).

    Returns a value in [0, 1]. Values > 0.5 indicate dominant cycles.
    """
    from scipy.fft import rfft

    n = len(y)
    if n < 10:
        return 0.0

    fft_vals = rfft(y)
    power = np.abs(fft_vals)**2
    # Skip DC component
    power[0] = 0
    total = np.sum(power)
    if total < 1e-12:
        return 0.0

    top_power = np.sum(np.sort(power)[-top_k:])
    return float(top_power / total)


# ═════════════════════════════════════════════════════════════
# STATIONARIZER CLASS
# ═════════════════════════════════════════════════════════════

class Stationarizer:
    """
    Makes a signal stationary using a configurable method.

    Usage:
        s = Stationarizer({'method': 'bandpass', 'sampling_rate': 0.1})
        result = s.transform(signal)
        print(result.is_stationary, result.method_used)

    Each transform() call processes ONE signal. The master class (Associa)
    calls this twice — once for X, once for Y.
    """

    METHODS = ['auto', 'bandpass', 'detrend', 'lazy', 'difference',
               'bandpass_diff', 'lazy_diff']

    def __init__(self, config: Optional[Dict] = None):
        self.config = {
            'method': 'auto',
            # Bandpass parameters
            'bandpass_low': 0.008,        # Hz — removes slow drift
            'bandpass_high': 0.25,        # Hz — removes high-freq noise
            'bandpass_order': 4,          # Butterworth filter order
            'sampling_rate': 0.1,         # Hz (= 1/t_interval_seconds)
            # Detrend parameters
            'detrend_order': 'auto',      # 'auto', 1 (linear), 2 (quadratic)
            'detrend_r2_threshold': 0.05, # min R² to apply detrending
            # Decycle (FFT) parameters
            'decycle_max_components': 3,   # max spectral peaks to remove
            'decycle_min_power_ratio': 0.05,  # min relative power to count
            # Lazy cycle separation parameters
            'lazy_embedding_dim': 3,
            'lazy_time_delay': 1,
            'lazy_radius': None,          # None = auto (15th percentile of distances)
            'lazy_max_iterations': 10,
            # Difference parameters
            'difference_order': 1,        # 1 = first diff, 2 = second diff
            # Diagnostics
            'run_diagnostics': True,
            'alpha': 0.05,                # significance level for tests
        }
        if config:
            self.config.update(config)

    def transform(self, signal: np.ndarray) -> StationarityResult:
        """
        Apply stationarization to a 1-D signal.

        Parameters
        ----------
        signal : 1-D numpy array

        Returns
        -------
        StationarityResult with transformed signal and full diagnostics.
        """
        y = np.asarray(signal, dtype=np.float64).ravel()
        method = self.config['method']

        if method not in self.METHODS:
            raise ValueError(f"Unknown method '{method}'. Choose from: {self.METHODS}")

        # Before diagnostics
        diag_before = run_diagnostics(y, self.config['alpha']) if self.config['run_diagnostics'] else None

        # Dispatch
        result = getattr(self, f'_apply_{method}')(y)

        # After diagnostics
        if self.config['run_diagnostics']:
            result.diagnostics_before = diag_before
            result.diagnostics_after = run_diagnostics(result.signal_out, self.config['alpha'])
            result.is_stationary = result.diagnostics_after.is_stationary

        return result

    # ─── AUTO: SEQUENTIAL PIPELINE (Fig 1) ──────────────────

    def _apply_auto(self, y: np.ndarray) -> StationarityResult:
        """
        Sequential stationarization following Fig 1:
        X(t) = T(t) + C(t) + S(t) + ε(t)

        Step 0: Check if already stationary → return as-is
        Step 1: Detrend (remove T(t)) → check stationarity
        Step 2: Decycle via FFT (remove C(t)) → check stationarity
        Step 3: If still non-stationary, difference as last resort
        """
        alpha = self.config['alpha']
        steps = []
        current = y.copy()
        details = {}

        # Step 0: Check if already stationary
        diag = run_diagnostics(current, alpha)
        if diag.is_stationary:
            return StationarityResult(
                signal_in=y, signal_out=current,
                method_used='auto (already stationary)',
                is_stationary=True,
                diagnostics_before=diag, diagnostics_after=diag,
                details={'steps': ['none_needed']})

        # Step 1: Detrend
        trend = self._estimate_trend(current)
        if trend is not None:
            current = current - trend
            steps.append('detrend')
            details['trend'] = trend
            diag = run_diagnostics(current, alpha)
            if diag.is_stationary:
                return StationarityResult(
                    signal_in=y, signal_out=current,
                    method_used='auto (detrend)',
                    is_stationary=True,
                    details={'steps': steps, **details})

        # Step 2: Decycle (FFT-based)
        cycles = self._estimate_cycles(current)
        if cycles is not None:
            current = current - cycles
            steps.append('decycle')
            details['cycles'] = cycles
            diag = run_diagnostics(current, alpha)
            if diag.is_stationary:
                return StationarityResult(
                    signal_in=y, signal_out=current,
                    method_used=f'auto ({"+".join(steps)})',
                    is_stationary=True,
                    details={'steps': steps, **details})

        # Step 3: Last resort — difference
        diff_out = np.diff(current)
        steps.append('difference')

        return StationarityResult(
            signal_in=y, signal_out=diff_out,
            method_used=f'auto ({"+".join(steps)})',
            details={'steps': steps, **details},
            warnings=['Applied differencing as last resort.'])

    def _estimate_trend(self, y: np.ndarray) -> Optional[np.ndarray]:
        """
        Fit polynomial trend. Returns trend array or None if R² too low.
        Uses auto order selection: quadratic only if >5% R² improvement.
        """
        t = np.arange(len(y), dtype=np.float64)
        threshold = self.config.get('detrend_r2_threshold', 0.05)

        # Linear fit
        coeffs1 = np.polyfit(t, y, 1)
        trend1 = np.polyval(coeffs1, t)
        ss_tot = np.sum((y - np.mean(y))**2)
        if ss_tot < 1e-12:
            return None
        r2_1 = 1 - np.sum((y - trend1)**2) / ss_tot

        # Quadratic fit
        coeffs2 = np.polyfit(t, y, 2)
        trend2 = np.polyval(coeffs2, t)
        r2_2 = 1 - np.sum((y - trend2)**2) / ss_tot

        # Pick best
        if r2_2 - r2_1 > 0.05:
            trend, r2 = trend2, r2_2
        else:
            trend, r2 = trend1, r2_1

        # Only detrend if trend explains meaningful variance
        if r2 < threshold:
            return None
        return trend

    def _estimate_cycles(self, y: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect and reconstruct dominant cycles via FFT.
        Returns cycle array or None if no significant cycles found.

        Finds the top spectral peaks above a power threshold and
        reconstructs only those frequency components.
        """
        from scipy.fft import rfft, irfft

        n = len(y)
        max_components = self.config.get('decycle_max_components', 3)
        min_power_ratio = self.config.get('decycle_min_power_ratio', 0.05)

        fft_vals = rfft(y)
        power = np.abs(fft_vals)**2

        # Skip DC component
        power[0] = 0
        total_power = np.sum(power)
        if total_power < 1e-12:
            return None

        # Find dominant peaks above threshold
        sorted_idx = np.argsort(power)[::-1]
        cycle_fft = np.zeros_like(fft_vals)
        n_added = 0

        for idx in sorted_idx:
            if n_added >= max_components:
                break
            if power[idx] / total_power < min_power_ratio:
                break
            cycle_fft[idx] = fft_vals[idx]
            n_added += 1

        if n_added == 0:
            return None

        cycles = irfft(cycle_fft, n=n).real
        return cycles

    # ─── BANDPASS ────────────────────────────────────────────

    def _apply_bandpass(self, y: np.ndarray) -> StationarityResult:
        """
        Zero-phase Butterworth bandpass filter.

        From the Rostami investigation (2025): bandpass at 0.008–0.25 Hz removes
        slow variance drift physically (not mathematically), preserving the
        oscillatory biology that matters for coupling analysis.
        """
        fs = self.config['sampling_rate']
        low = self.config['bandpass_low']
        high = self.config['bandpass_high']
        order = self.config['bandpass_order']
        ws = []

        # Nyquist check
        nyquist = fs / 2.0
        if high >= nyquist:
            high = nyquist * 0.95
            ws.append(f'bandpass_high clamped to {high:.4f} Hz (Nyquist = {nyquist:.4f})')

        # Signal length check — need at least ~2 full cycles of lowest frequency
        min_samples = int(2.0 / low * fs)
        if len(y) < min_samples:
            ws.append(f'Signal too short ({len(y)}) for bandpass at {low} Hz '
                      f'(need ~{min_samples}). Falling back to detrend.')
            return self._apply_detrend(y)

        from scipy.signal import butter, filtfilt

        # Normalize frequencies to Nyquist
        low_n = low / nyquist
        high_n = high / nyquist

        b, a = butter(order, [low_n, high_n], btype='band')

        # Mirror-pad to reduce edge artifacts (reflect signal at boundaries)
        pad_len = min(3 * max(len(a), len(b)), len(y) - 1)
        y_filtered = filtfilt(b, a, y, padlen=pad_len)

        return StationarityResult(
            signal_in=y,
            signal_out=y_filtered,
            method_used='bandpass',
            details={
                'low_hz': low, 'high_hz': high,
                'order': order, 'sampling_rate': fs,
            },
            warnings=ws,
        )

    # ─── DETREND ─────────────────────────────────────────────

    def _apply_detrend(self, y: np.ndarray) -> StationarityResult:
        """
        Polynomial detrending. 'auto' picks the best order (1 or 2)
        based on R² improvement.
        """
        order = self.config['detrend_order']
        t = np.arange(len(y), dtype=np.float64)

        if order == 'auto':
            # Try linear and quadratic, pick better
            res_1 = y - np.polyval(np.polyfit(t, y, 1), t)
            r2_1 = 1.0 - np.var(res_1) / (np.var(y) + 1e-12)

            res_2 = y - np.polyval(np.polyfit(t, y, 2), t)
            r2_2 = 1.0 - np.var(res_2) / (np.var(y) + 1e-12)

            if r2_2 - r2_1 > 0.05:
                chosen, chosen_order, r2 = res_2, 2, r2_2
            else:
                chosen, chosen_order, r2 = res_1, 1, r2_1
        else:
            order = int(order)
            chosen = y - np.polyval(np.polyfit(t, y, order), t)
            chosen_order = order
            r2 = 1.0 - np.var(chosen) / (np.var(y) + 1e-12)

        return StationarityResult(
            signal_in=y,
            signal_out=chosen,
            method_used='detrend',
            details={'polynomial_order': chosen_order, 'r_squared': float(r2)},
        )

    # ─── LAZY CYCLE SEPARATION ───────────────────────────────

    def _apply_lazy(self, y: np.ndarray) -> StationarityResult:
        """
        Lazy cycle separation via Takens delay embedding.

        Embeds the signal into phase space, applies distance-weighted
        local averaging (smooths regular/deterministic patterns),
        reconstructs via least-squares, and returns the stochastic
        residual as the "stationary-ish" signal.

        From gc_pipeline_v13 (Rostami 2025).
        """
        dim = self.config['lazy_embedding_dim']
        tau = self.config['lazy_time_delay']
        radius = self.config['lazy_radius']
        max_iter = self.config['lazy_max_iterations']
        ws = []

        min_len = (dim - 1) * tau + 2
        if len(y) < min_len:
            ws.append(f'Signal too short ({len(y)}) for Lazy embedding '
                      f'(need {min_len}). Returning original.')
            return StationarityResult(
                signal_in=y, signal_out=y.copy(), method_used='lazy',
                warnings=ws, details={'converged': False},
            )

        stochastic, deterministic = _lazy_cycle_separation(
            y, embedding_dim=dim, time_delay=tau,
            radius=radius, max_iterations=max_iter,
        )

        return StationarityResult(
            signal_in=y,
            signal_out=stochastic,
            method_used='lazy',
            details={
                'embedding_dim': dim, 'time_delay': tau,
                'deterministic_component': deterministic,
            },
            warnings=ws,
        )

    # ─── DIFFERENCE ──────────────────────────────────────────

    def _apply_difference(self, y: np.ndarray) -> StationarityResult:
        """
        First or second differencing.

        Warning: differencing destroys low-frequency biology and inflates
        high-frequency noise. Creates lag-1 autocorrelation artifacts.
        Use only when gentler methods fail.
        """
        order = self.config['difference_order']
        ws = ['Differencing may destroy low-frequency biological signal. '
              'Consider bandpass or lazy instead.']

        out = y.copy()
        for _ in range(order):
            if len(out) < 2:
                ws.append('Signal too short to difference further.')
                break
            out = np.diff(out)

        return StationarityResult(
            signal_in=y,
            signal_out=out,
            method_used=f'difference_d{order}',
            details={'order': order, 'length_reduction': len(y) - len(out)},
            warnings=ws,
        )

    # ─── COMBO: BANDPASS + DIFFERENCE ────────────────────────

    def _apply_bandpass_diff(self, y: np.ndarray) -> StationarityResult:
        """Bandpass first, then difference only if still non-stationary."""
        bp_result = self._apply_bandpass(y)

        # Check if bandpass alone achieved stationarity
        bp_diag = run_diagnostics(bp_result.signal_out, self.config['alpha'])
        if bp_diag.is_stationary:
            bp_result.method_used = 'bandpass_diff (bandpass sufficient)'
            return bp_result

        # Difference the bandpassed signal
        diff_out = np.diff(bp_result.signal_out)

        return StationarityResult(
            signal_in=y,
            signal_out=diff_out,
            method_used='bandpass_diff',
            details={
                'bandpass_details': bp_result.details,
                'needed_differencing': True,
                'length_reduction': len(y) - len(diff_out),
            },
            warnings=bp_result.warnings + ['Applied 1st difference after bandpass.'],
        )

    # ─── COMBO: LAZY + DIFFERENCE ────────────────────────────

    def _apply_lazy_diff(self, y: np.ndarray) -> StationarityResult:
        """Lazy separation first, then difference only if still non-stationary."""
        lazy_result = self._apply_lazy(y)

        # Check if lazy alone achieved stationarity
        lazy_diag = run_diagnostics(lazy_result.signal_out, self.config['alpha'])
        if lazy_diag.is_stationary:
            lazy_result.method_used = 'lazy_diff (lazy sufficient)'
            return lazy_result

        # First difference
        diff1 = np.diff(lazy_result.signal_out)
        diff1_diag = run_diagnostics(diff1, self.config['alpha'])
        if diff1_diag.is_stationary:
            return StationarityResult(
                signal_in=y,
                signal_out=diff1,
                method_used='lazy_diff (lazy + 1st diff)',
                details={
                    'lazy_details': lazy_result.details,
                    'difference_order': 1,
                },
                warnings=lazy_result.warnings,
            )

        # Second difference
        if len(diff1) > 1:
            diff2 = np.diff(diff1)
            return StationarityResult(
                signal_in=y,
                signal_out=diff2,
                method_used='lazy_diff (lazy + 2nd diff)',
                details={
                    'lazy_details': lazy_result.details,
                    'difference_order': 2,
                },
                warnings=lazy_result.warnings + ['Needed 2nd difference after lazy.'],
            )

        return StationarityResult(
            signal_in=y,
            signal_out=diff1,
            method_used='lazy_diff (failed)',
            is_stationary=False,
            details={'lazy_details': lazy_result.details},
            warnings=lazy_result.warnings + ['Could not achieve stationarity.'],
        )


# ═════════════════════════════════════════════════════════════
# LAZY CYCLE SEPARATION (from gc_pipeline_v13)
# ═════════════════════════════════════════════════════════════

def _lazy_cycle_separation(
    time_series: np.ndarray,
    embedding_dim: int = 3,
    time_delay: int = 1,
    radius: Optional[float] = None,
    max_iterations: int = 10,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Separate stochastic from deterministic cycles via Lazy averaging
    in Takens delay-embedded phase space.

    Algorithm:
        1. Embed signal into m-dimensional phase space (Takens theorem)
        2. Iteratively apply distance-weighted local averaging
           (regular/predictable patterns get smoothed more)
        3. Reconstruct deterministic component via least-squares
        4. Stochastic = original - deterministic

    Parameters
    ----------
    time_series : 1-D array
    embedding_dim : int
        Phase space dimension (default 3)
    time_delay : int
        Delay τ for embedding (default 1)
    radius : float or None
        Neighborhood radius. None = auto (15th percentile of distances)
    max_iterations : int
        Max Lazy averaging iterations

    Returns
    -------
    stochastic : 1-D array (same length as input)
    deterministic : 1-D array (same length as input)
    """
    from scipy.spatial.distance import pdist, squareform

    y = np.asarray(time_series, dtype=np.float64)
    n = len(y)
    m = embedding_dim
    tau = time_delay

    # Embed
    N = n - (m - 1) * tau
    if N <= 0:
        return y.copy(), np.zeros_like(y)

    embedded = np.zeros((N, m))
    for i in range(N):
        for j in range(m):
            embedded[i, j] = y[i + j * tau]

    # Auto radius
    if radius is None:
        dists = squareform(pdist(embedded))
        non_zero = dists[dists > 0]
        radius = np.percentile(non_zero, 15) if len(non_zero) > 0 else 1.0

    # Iterative Lazy averaging
    current = embedded.copy()
    for iteration in range(max_iterations):
        dists = squareform(pdist(current))
        new_states = current.copy()

        for i in range(N):
            neighbors = np.where((dists[i] <= radius) & (dists[i] > 0))[0]
            if len(neighbors) > 0:
                w = 1.0 / (dists[i, neighbors] + 1e-10)
                w /= w.sum()
                new_states[i] = np.sum(w[:, None] * current[neighbors], axis=0)

        change = np.mean(np.linalg.norm(new_states - current, axis=1))
        if change < 1e-6:
            break
        current = new_states

    # Reconstruct deterministic component via least-squares
    deterministic = _inverse_embedding_lstsq(current, m, tau, n)
    stochastic = y - deterministic

    return stochastic, deterministic


def _inverse_embedding_lstsq(
    embedded: np.ndarray,
    embedding_dim: int,
    time_delay: int,
    original_length: int,
) -> np.ndarray:
    """Reconstruct 1-D signal from embedded states using least-squares."""
    N = len(embedded)
    m = embedding_dim
    tau = time_delay

    A = np.zeros((N * m, original_length))
    b = embedded.flatten()

    for i in range(N):
        for j in range(m):
            t_idx = i + j * tau
            if t_idx < original_length:
                A[i * m + j, t_idx] = 1

    x, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    return x
