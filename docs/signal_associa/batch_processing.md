# Signal Associa — Batch Processing
Keywords: batch, pairwise, all pairs, pre-paired, paired columns, significance matrix, coupling network, pairs summary, n_jobs, joblib, parallel, gpu, cupy, csv rules, even columns

## Two Batch Modes (chosen at import)

### Pairwise (all C(N,2) pairs)
Keywords: pairwise, all pairs, network, significance matrix
Every unordered pair of the N columns is tested. For 6 signals that is C(6,2) = 15 pairs. Produces:
- a **significance matrix** (which pairs are coupled),
- a **coupling network** graph (nodes = signals, edges = significant couplings).
Use when the columns are a set of signals whose connectivity you want to map. Needs **3+ columns**.

### Pre-paired columns
Keywords: pre-paired, paired, consecutive columns, pairs summary, even count
Consecutive columns are treated as independent pairs: columns 1&2 = pair 1, 3&4 = pair 2, and so on. Produces a combined **Pairs Summary** (one row per pair). Use when each pair is a separate measurement (e.g. `Cell1_X, Cell1_Y, Cell2_X, Cell2_Y, ...`). Needs an **even column count**.

## CSV Rules
| Mode | Columns |
|------|---------|
| Single pipeline | exactly 2 |
| Batch → Pairwise | 3 or more |
| Batch → Pre-paired | even count (2, 4, 6, …) |

All modes: header row of short names, then numeric rows only (no index column, no blanks, no units in the data). Discard burn-in before saving.

## Parallel Compute
Keywords: n_jobs, joblib, workers, serial, live board
Pairs are distributed across CPU workers with joblib:
- `n_jobs = 1` — serial, with a per-method **live board** showing progress pair by pair.
- `n_jobs = -1` — use all cores.
- `n_jobs = k` — use k cores.
Each pair runs the full method set + surrogate null, so runtime scales with (pairs × methods × surrogates).

## GPU Acceleration
Keywords: gpu, cupy, ccm, fallback
GPU (CuPy) accelerates **CCM surrogate testing only**. If CuPy is missing or no GPU is present, it **auto-falls back to CPU** — the run still completes, just slower for CCM. Other methods are CPU-only.

## Expected Output Shapes
- **Pairwise:** a symmetric significance/coupling matrix + a network graph. A clean design has some connected pairs and at least one isolated control signal.
- **Pre-paired:** a Pairs Summary grid, one row per pair, coupled pairs highlighted.

## Multiple Comparisons
Across many pairs × methods, an occasional borderline false positive (surrogate p just under alpha) is expected. For a strictly clean network, apply an FDR correction over all tested pairs.
