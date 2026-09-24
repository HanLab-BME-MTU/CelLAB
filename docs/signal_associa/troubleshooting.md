# Signal Associa — Troubleshooting
Keywords: error, columns, csv, too short, gpu, cupy, fallback, non-significant, common driver, confound, maxlag, embedding, even columns, header

## CSV / Input Errors

### "Single needs exactly 2 columns"
- Cause: the Single pipeline received a file with ≠ 2 columns.
- Fix: use a 2-column CSV for Single; use Batch for 3+ columns.

### "Batch needs 3+ columns" / "Pre-paired needs an even column count"
- Cause: Pairwise got fewer than 3 columns, or Pre-paired got an odd count.
- Fix: Pairwise → 3+ columns; Pre-paired → even count (2, 4, 6, …), consecutive columns forming pairs.

### Header not detected / first row treated as data
- Cause: `has_header` guessed wrong.
- Fix: set `has_header` explicitly. Header must be short numeric-free names; data rows purely numeric.

### Wrong number of pairs
- Cause: wrong `batch_type`. Pairwise = C(N,2) pairs; Pre-paired = N/2 pairs.
- Fix: pick the batch mode that matches how the columns are organized.

## Compute

### GPU not used / CuPy missing
- Behavior: GPU accelerates **CCM surrogate testing only** and **auto-falls back to CPU** if CuPy or a GPU is absent. The run still completes.
- Fix: nothing required; install CuPy + a compatible CUDA toolkit only if you want the CCM speedup.

### Run is slow
- Cause: runtime ≈ pairs × methods × surrogates.
- Fix: raise `n_jobs` (‑1 = all cores); reduce `surr_n` for a quick pass; disable methods you don't need (or use Trichotomy for the core three).

### Signals too short
- Cause: not enough samples for the chosen embedding (CCM `E`, `tau`) or Granger `maxlag`.
- Symptom: NaN statistic, degenerate p, or a method erroring on that pair.
- Fix: use longer signals, lower `gc_maxlag`, or lower CCM `E`/`tau`. As a rule of thumb keep length well above maxlag and the embedding window.

## Interpretation

### Everything non-significant
- This can be correct — the pair genuinely may not be coupled. Check the null-distribution plot: if the real statistic sits inside the null, there is no detectable coupling.
- Also check signal length and that the right stationarizer/method is enabled.

### Significant parametric p but non-significant surrogate p
- The parametric p ignores autocorrelation; the surrogate p corrects for it. Trust the surrogate (empirical) p — this is the autocorrelation false positive the surrogate test is designed to catch.

### Common-driver confound (correlated but not causal)
- Cause: a hidden variable Z drives both X and Y with no direct X–Y coupling. Pearson sees the induced correlation, Granger the induced predictability — both can report significance.
- Key point: **surrogate testing does not fix this** (it controls autocorrelation, not a genuine common cause). CCM can also be fooled under strong shared forcing.
- Reading it: method disagreement (e.g. Pearson/Granger positive, CCM rejecting) is a hint. Ruling out a driver requires experimental control, not statistics alone.

### Granger disagrees with CCM/Pearson
- If Granger is non-significant while CCM/Pearson are significant, the coupling may live in a shared trend/oscillation that stationarization removed (Granger uses the stationary signal; CCM uses raw). This is expected, not a bug.

### Borderline edge to a control signal in the network
- A single faint edge (surrogate p just under alpha) to an otherwise isolated control is multiple-comparison noise across many pairs. Apply an FDR correction for a strictly clean network.
