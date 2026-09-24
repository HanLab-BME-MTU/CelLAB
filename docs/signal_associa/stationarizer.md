# Signal Associa — Stationarizer
Keywords: stationariz, stationary, auto, none, bandpass, difference, detrend, trend, cycle, granger, ccm, signal version, bp_low, bp_high

## Why Stationarity Matters
Some methods assume the signal's statistical properties (mean, variance, autocorrelation) do not drift over time. **Granger causality requires stationarity** — a trend or slow oscillation violates the VAR assumptions and inflates false positives. Other methods do not: **CCM uses the raw signal**, because trends and cycles are part of the deterministic structure its manifold reconstruction exploits.

The stationarizer therefore produces a **stationary version** of each signal, and the engine routes each method to the version it needs (Granger → stationary, CCM/Pearson/Spearman/MI/TE → raw by default).

## Modes
| Mode | What it does | When |
|------|--------------|------|
| **auto** (default) | picks and applies an appropriate transform per signal, judged by stationarity diagnostics | general use; safe default |
| none | leaves the signal unchanged | already stationary, or you want raw for all |
| bandpass | keeps a frequency band `bp_low`–`bp_high` (Hz), removing slow trend and high-frequency noise | oscillatory signals with drift |
| difference | first difference X(t) − X(t−1) | remove a linear/stochastic trend |
| detrend | subtract a fitted polynomial trend | smooth deterministic trend |

Bandpass defaults: `bp_low = 0.008` Hz, `bp_high = 0.25` Hz (with `sampling_rate` setting the time base).

## Key Point for Interpretation
A coupling that lives **in a shared trend or oscillation** is removed by stationarization. So Granger, operating on the stationary version, will be **blind** to it, while CCM and correlation, on the raw signal, can still detect it. This is why the two methods disagree on shared-non-stationary coupling — the disagreement is diagnostic, not an error.

## Practical Notes
- `auto` is recommended unless you have a specific reason to fix the transform.
- If Granger is unexpectedly non-significant while CCM/Pearson are significant, suspect coupling in the non-stationary component that stationarization stripped.
- The raw and stationary versions are both retained per run so results record which version each method used.
