"""
Associa — Surrogate Generator Module
======================================
Generates null-hypothesis surrogate signals for statistical significance testing.

Methods:
    1. iaaft    — Iterative Amplitude Adjusted Fourier Transform
                  Preserves amplitude distribution + power spectrum (autocorrelation).
                  Gold standard for autocorrelated signals (random walks, biological traces).
    2. shuffle  — Random permutation. Destroys all temporal structure.
                  Weakest null hypothesis. Fast.
    3. circular — Circular time shift. Preserves autocorrelation, destroys cross-correlation.
                  Good compromise between realism and null hypothesis.
    4. block_bootstrap — Resample contiguous blocks. Preserves short-range autocorrelation.
                  Configurable block length.

Modes:
    generate_one(signal)          → single surrogate  (CPU parallel Strategy A)
    generate_batch(signal, n)     → (n, T) array      (CPU batch)
    generate_batch_gpu(signal, n) → CuPy (n, T) array (GPU vectorized Strategy B)

Author: CelLAB / Han Mechanobiology Lab
"""

import numpy as np
from typing import Optional, Dict


# ═════════════════════════════════════════════════════════════
# SURROGATE GENERATOR
# ═════════════════════════════════════════════════════════════

class SurrogateGenerator:
    """
    Generates surrogate signals for null-hypothesis significance testing.

    Usage:
        sg = SurrogateGenerator({'method': 'iaaft', 'n_iterations': 100})

        # Single surrogate (for CPU pair-parallel)
        s = sg.generate_one(signal)

        # Batch of N surrogates (for CPU batch or pre-GPU)
        batch = sg.generate_batch(signal, n=100)  # shape: (100, len(signal))

        # GPU batch (stays on GPU for vectorized CCM testing)
        batch_gpu = sg.generate_batch_gpu(signal, n=100)  # CuPy array
    """

    METHODS = ['iaaft', 'shuffle', 'circular', 'block_bootstrap']

    def __init__(self, config: Optional[Dict] = None):
        self.config = {
            'method': 'iaaft',
            'n_iterations': 100,      # IAAFT convergence iterations
            'block_length': None,     # block_bootstrap: None = auto (sqrt(T))
            'seed': None,             # reproducibility
        }
        if config:
            self.config.update(config)

        method = self.config['method']
        if method not in self.METHODS:
            raise ValueError(f"Unknown method '{method}'. Choose from: {self.METHODS}")

    # ─── PUBLIC API ──────────────────────────────────────────

    def generate_one(self, signal: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        """
        Generate a single surrogate signal.

        Parameters
        ----------
        signal : 1-D numpy array
        seed   : optional RNG seed for this surrogate

        Returns
        -------
        1-D numpy array, same length as input.
        """
        y = np.asarray(signal, dtype=np.float64).ravel()
        rng = np.random.RandomState(seed)
        return self._dispatch(y, rng)

    def generate_batch(self, signal: np.ndarray, n: int = 100,
                       seed: Optional[int] = None) -> np.ndarray:
        """
        Generate N surrogates on CPU.

        Parameters
        ----------
        signal : 1-D numpy array
        n      : number of surrogates
        seed   : base seed (each surrogate gets seed+i)

        Returns
        -------
        (n, T) numpy array.
        """
        y = np.asarray(signal, dtype=np.float64).ravel()
        T = len(y)
        out = np.empty((n, T), dtype=np.float64)

        for i in range(n):
            s = seed + i if seed is not None else None
            rng = np.random.RandomState(s)
            out[i] = self._dispatch(y, rng)

        return out

    def generate_batch_gpu(self, signal: np.ndarray, n: int = 100,
                           seed: Optional[int] = None):
        """
        Generate N surrogates on GPU. Returns CuPy array (n, T).
        Falls back to CPU if CuPy unavailable.

        Only IAAFT and shuffle have GPU-optimized paths.
        Other methods generate on CPU then transfer.
        """
        try:
            import cupy as cp
        except ImportError:
            # Fallback: generate on CPU, return numpy
            return self.generate_batch(signal, n, seed)

        method = self.config['method']

        if method == 'iaaft':
            return _iaaft_batch_gpu(signal, n,
                                    n_iter=self.config['n_iterations'],
                                    chunk_size=min(20, n),
                                    seed=seed)
        elif method == 'shuffle':
            return _shuffle_batch_gpu(signal, n, seed=seed)
        else:
            # No GPU path — generate on CPU, transfer
            cpu_batch = self.generate_batch(signal, n, seed)
            return cp.asarray(cpu_batch, dtype=cp.float64)

    # ─── DISPATCH ────────────────────────────────────────────

    def _dispatch(self, y: np.ndarray, rng: np.random.RandomState) -> np.ndarray:
        method = self.config['method']
        if method == 'iaaft':
            return _iaaft_cpu(y, rng, n_iter=self.config['n_iterations'])
        elif method == 'shuffle':
            return _shuffle_cpu(y, rng)
        elif method == 'circular':
            return _circular_cpu(y, rng)
        elif method == 'block_bootstrap':
            return _block_bootstrap_cpu(y, rng, self.config['block_length'])
        else:
            raise ValueError(f"Unknown method: {method}")


# ═════════════════════════════════════════════════════════════
# CPU IMPLEMENTATIONS
# ═════════════════════════════════════════════════════════════

def _iaaft_cpu(signal: np.ndarray, rng: np.random.RandomState,
               n_iter: int = 100) -> np.ndarray:
    """
    IAAFT (Iterative Amplitude Adjusted Fourier Transform) surrogate.

    Preserves both amplitude distribution AND power spectrum (autocorrelation).
    Gold standard for testing coupling in autocorrelated time series.

    Algorithm:
        1. Compute target power spectrum and sorted amplitudes
        2. Start with a random permutation of the signal
        3. Iterate:
           a. Rank-match to original amplitudes (preserves distribution)
           b. FFT → replace magnitudes with original → IFFT (preserves spectrum)
        4. Converges to a surrogate with correct distribution + spectrum
           but randomized phase (destroyed cross-correlation)
    """
    from scipy.fft import rfft, irfft

    n = len(signal)
    sorted_amplitudes = np.sort(signal)
    original_fft = rfft(signal)
    original_power = np.abs(original_fft)

    # Start with random permutation
    surrogate = rng.permutation(signal).astype(np.float64)

    for iteration in range(n_iter):
        # Step A: match amplitude distribution via rank ordering
        ranks = np.argsort(np.argsort(surrogate))
        surrogate = sorted_amplitudes[ranks]

        # Step B: match power spectrum (preserve autocorrelation)
        surr_fft = rfft(surrogate)
        phases = np.angle(surr_fft)
        surr_fft = original_power * np.exp(1j * phases)
        surrogate = irfft(surr_fft, n=n).real

        # Early convergence check
        if iteration > 10 and iteration % 10 == 0:
            error = np.mean((np.sort(surrogate) - sorted_amplitudes) ** 2)
            if error < 1e-10:
                break

    return surrogate


def _shuffle_cpu(signal: np.ndarray, rng: np.random.RandomState) -> np.ndarray:
    """
    Random permutation surrogate.
    Destroys all temporal structure. Weakest null hypothesis.
    """
    return rng.permutation(signal).astype(np.float64)


def _circular_cpu(signal: np.ndarray, rng: np.random.RandomState) -> np.ndarray:
    """
    Circular time-shift surrogate.
    Preserves autocorrelation structure, destroys cross-correlation.
    Good compromise for paired tests.
    """
    shift = rng.randint(1, len(signal))
    return np.roll(signal, shift)


def _block_bootstrap_cpu(signal: np.ndarray, rng: np.random.RandomState,
                         block_length: Optional[int] = None) -> np.ndarray:
    """
    Block bootstrap surrogate.
    Resamples contiguous blocks, preserving short-range autocorrelation.
    Block length controls the preserved temporal scale.
    """
    n = len(signal)
    if block_length is None:
        block_length = max(2, int(np.sqrt(n)))

    n_blocks = int(np.ceil(n / block_length))
    # Random start indices for each block
    starts = rng.randint(0, n - block_length + 1, size=n_blocks)

    blocks = [signal[s:s + block_length] for s in starts]
    surrogate = np.concatenate(blocks)[:n]

    return surrogate


# ═════════════════════════════════════════════════════════════
# GPU IMPLEMENTATIONS (CuPy — optional dependency)
# ═════════════════════════════════════════════════════════════

def _iaaft_batch_gpu(signal: np.ndarray, n_surr: int,
                     n_iter: int = 100, chunk_size: int = 20,
                     seed: Optional[int] = None):
    """
    Batch IAAFT on GPU. Generates n_surr surrogates in parallel.

    Processes in chunks to manage GPU memory.
    Returns CuPy array of shape (n_surr, T).

    From BatchCCMGPU.py (Rostami 2025), refactored for Associa.
    """
    import cupy as cp
    from cupyx.scipy.fft import rfft, irfft

    s = cp.asarray(signal, dtype=cp.float64)
    n = len(s)

    s_sorted = cp.sort(s)
    fft_s = rfft(s)
    mag_target = cp.abs(fft_s)

    all_surrogates = []
    n_chunks = int(np.ceil(n_surr / chunk_size))

    for chunk_idx in range(n_chunks):
        actual_chunk = min(chunk_size, n_surr - chunk_idx * chunk_size)

        if seed is not None:
            cp.random.seed(seed + chunk_idx)

        # Initialize with random permutations
        Y = cp.empty((actual_chunk, n), dtype=cp.float64)
        for i in range(actual_chunk):
            Y[i] = cp.random.permutation(s)

        # IAAFT iterations (all surrogates in parallel)
        for _ in range(n_iter):
            # Step A: rank-match to original amplitudes
            ranks = cp.argsort(cp.argsort(Y, axis=1), axis=1)
            Y = s_sorted[ranks]

            # Step B: match power spectrum
            Y_fft = rfft(Y, axis=1)
            phases = cp.angle(Y_fft)
            Y_fft = mag_target[None, :] * cp.exp(1j * phases)
            Y = irfft(Y_fft, n=n, axis=1).astype(cp.float64)

        all_surrogates.append(Y)

    return cp.vstack(all_surrogates)


def _shuffle_batch_gpu(signal: np.ndarray, n_surr: int,
                       seed: Optional[int] = None):
    """Batch shuffle on GPU. Returns CuPy array (n_surr, T)."""
    import cupy as cp

    s = cp.asarray(signal, dtype=cp.float64)
    n = len(s)

    if seed is not None:
        cp.random.seed(seed)

    out = cp.empty((n_surr, n), dtype=cp.float64)
    for i in range(n_surr):
        out[i] = cp.random.permutation(s)

    return out
