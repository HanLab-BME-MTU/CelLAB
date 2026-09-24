# Signal Associa — Overview
Keywords: signal associa, coupling, causal, causality, ccm, convergent cross, granger, transfer entropy, mutual information, pearson, spearman, surrogate, iaaft, aaft, stationariz, coupling network, significance matrix, pairwise, pre-paired, trichotomy, time series, empirical p, effect size

## What It Does
Signal Associa tests whether two time series are genuinely **coupled** — and, where possible, in which direction — while guarding against the ways naive correlation misleads (shared drivers, non-stationarity, autocorrelation, method blind spots). It is **semantic-agnostic**: it does not know whether the signals are focal-adhesion intensities, cell trajectories, or anything else. Pipelines provide the signals and interpret the results.

It runs six coupling methods, tests each against a surrogate null, and reports a per-method significance decision plus interpretable statistics. Two GUI pipelines share one engine:

| Pipeline | Input | Purpose |
|----------|-------|---------|
| **Single** | 2-column CSV (one pair) | Test one X–Y pair, see all methods side by side |
| **Batch** | multi-signal CSV (3+ columns) | Test many pairs → significance matrix + coupling network |

## Key Concepts

### The Six Coupling Methods
Keywords: pearson, spearman, mutual information, granger, ccm, transfer entropy, method choice
Each method sees coupling under different conditions, and each fails silently outside its regime. Reading the **pattern of agreement and disagreement** across methods is the core idea.

| Method | Detects | Needs stationarity? | Directional? |
|--------|---------|--------------------|--------------|
| Pearson | linear co-variation | no | no |
| Spearman | monotonic (rank) | no | no |
| Mutual Information | nonlinear dependence | no | no |
| Granger causality | linear predictive coupling | yes (uses stationary signal) | yes |
| CCM | nonlinear / deterministic / state-dependent | no (uses raw) | yes |
| Transfer Entropy | directed information transfer | no | yes |

Rule of thumb: **CCM wins on nonlinear coupling**, **Granger wins on linear/directional coupling in stochastic dynamics**, and **no single-pair method escapes the common-driver confound** (see below).

### Surrogate Significance
Keywords: surrogate, iaaft, empirical p, parametric p, null distribution, alpha
Significance is judged against a **surrogate null**: N synthetic copies of X that preserve its statistical properties but destroy coupling. The method is recomputed on each surrogate to build a null distribution, and an empirical p-value follows. IAAFT is the default (preserves amplitude distribution + power spectrum). **All methods, including Granger, run the surrogate null.** The reported significance is the empirical (surrogate) p when surrogates ran, otherwise the parametric p. Defaults: N = 100 surrogates, α = 0.05.

### Stationarizer
Keywords: stationariz, auto, bandpass, difference, detrend, stationary version
Some methods (Granger) require stationary signals; others (CCM) work on raw signals. The stationarizer produces a stationary version of each signal, and each method is routed to the version it needs. Modes: `auto` (default), `none`, `bandpass`, `difference`, `detrend`.

### The Two Batch Modes
Keywords: pairwise, all pairs, pre-paired, significance matrix, coupling network, pairs summary
Chosen at import:
- **Pairwise** — all C(N,2) pairs of the columns are tested → significance matrix + coupling network. Needs 3+ columns.
- **Pre-paired columns** — consecutive columns are independent pairs (1&2, 3&4, …) → combined Pairs Summary. Needs an even column count.

### Parallel / GPU Compute
Keywords: n_jobs, joblib, parallel, gpu, cupy, cpu fallback
Pairs are processed in parallel with joblib (`n_jobs`: 1 = serial with a per-method live board, -1 = all cores). GPU acceleration (CuPy) exists **for CCM surrogate testing only** and auto-falls back to CPU when CuPy is unavailable.

### Outputs
Keywords: results, pkl, summary, plots, coupling network, significance matrix
Each run writes a results pickle, summary tables (CSV/JSON), metadata, and plots (signal traces, null distributions, coupling/significance matrices, coupling network). Plots are inserted on demand from the Results & Plots panel.

## When To Use
- Testing whether two measured signals are coupled, and how.
- Screening a set of signals for a coupling network (which are connected, which are isolated).
- Distinguishing linear from nonlinear coupling, and flagging likely common-driver confounds.

## API Summary
| Object / call | Purpose | See |
|---------------|---------|-----|
| `Associa(config)` | Construct the engine with method/stationarizer/surrogate config | API.md |
| `engine.run(x, y)` | Analyze one pair → results dict (statistics, p-values, null) | API.md, methods.md |
| Batch runner | Iterate pairs (pairwise or pre-paired), aggregate → matrices/network | batch_processing.md |
| Plotters | Signal traces, null distributions, matrices, network | plotters.md |

## Pipeline Steps (in CelLAB GUI)

### Single Pipeline (type: signal_associa)
1. **Load CSV** — 2 columns = one pair; header auto-detected.
2. **Configure** — pick methods (or Trichotomy), stationarizer, surrogate method + N + α, compute options.
3. **Run** — engine computes each method + surrogate null.
4. **Results & Plots** — coupling report table; insert null distributions, signal traces on demand.

### Batch Pipeline (type: signal_associa_batch)
1. **Import** — select CSV, choose batch mode (Pairwise or Pre-paired), set n_jobs.
2. **Configure** — same method/surrogate/stationarizer settings.
3. **Run** — parallel over pairs; live board when n_jobs = 1.
4. **Results & Plots** — significance matrix, coupling network (pairwise) or Pairs Summary grid (pre-paired); export.
