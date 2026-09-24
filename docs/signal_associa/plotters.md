# Signal Associa — Plotters
Keywords: plots, signal traces, null distribution, histogram, pair summary, pairs summary grid, coupling matrix, significance matrix, coupling network, insert, results and plots

## How Plots Are Added
Plots are generated **on demand**: right-click **Results & Plots → Insert** and choose the plot. Nothing is drawn until inserted, keeping the results panel light.

## Plot Catalog

### Signal Traces
Keywords: signal traces, raw signal, time series
The input X and Y (or all columns) over time. First check that signals loaded correctly and share a length.

### Null Distributions
Keywords: null distribution, histogram, surrogate, real statistic
One panel per method. For surrogate methods: a **histogram** of the null with the real statistic marked (and the empirical p / exceedance count). For a purely analytic panel: a stat panel instead of a histogram. Read it as "how far into the tail does the real statistic sit" — deep in the tail = significant.

### Pair Summary
Keywords: pair summary, single pair, method table
For one pair: the per-method table (statistic, parametric p, surrogate p, significant) as a compact visual — the same content as the coupling report.

### Pairs Summary Grid (pre-paired mode)
Keywords: pairs summary grid, paired, rows per pair
One row per pair across all methods; coupled pairs highlighted (green), uncoupled gray. The quick read of a pre-paired batch: which pairs lit up.

### Coupling Matrix
Keywords: coupling matrix, statistic matrix, -log10 p
Heatmap over all pairs. Two flavors: the **statistic** matrix (coupling strength) and the **−log₁₀ p** matrix (significance intensity). Bright cells = strong / significant pairs.

### Significance Matrix
Keywords: significance matrix, binary, threshold
Binary (or thresholded) version of the coupling matrix: which pairs pass α. The at-a-glance connectivity map for pairwise batches.

### Coupling Network
Keywords: coupling network, graph, nodes, edges, isolated
Graph of the significance matrix: nodes = signals, edges = significant couplings. Expect connected components for coupled groups and isolated nodes for controls. Edge presence/weight follows the significant statistic.

## Reading Tips
- If null distributions show the real statistic buried inside the null, the pair is not coupled regardless of a large raw statistic.
- Compare the statistic matrix with the significance matrix: a strong statistic that is not significant is likely autocorrelation the surrogate null absorbed.
- In the network, a lone faint edge to an otherwise isolated control is usually a multiple-comparison false positive (consider FDR).
