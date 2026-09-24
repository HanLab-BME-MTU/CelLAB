# Signal Associa — Methods
Keywords: methods, ccm, convergent cross mapping, granger, pearson, spearman, mutual information, transfer entropy, trichotomy, nonlinear, linear, directional, common driver, embedding, VAR, F-test

## The Six Methods
Each returns a `statistic`, a parametric p (`p_value`), and — when surrogates run — an empirical p (`p_empirical`). Significance is the empirical p if surrogates ran, else the parametric p.

### CCM — Convergent Cross Mapping
- **Detects:** nonlinear, deterministic, state-dependent coupling.
- **Stationarity:** agnostic — uses the **raw** signal.
- **Directional:** yes (cross-map skill of X's manifold recovering Y vs the reverse).
- **Idea:** reconstruct each signal's attractor by time-delay embedding; if X influences Y, Y's manifold can recover X's states.
- **Params:** `E = 2` (embedding dimension), `τ = 1` (delay), `n_boot = 20` (bootstraps).
- **Best on:** nonlinear coupling where correlation and Granger are blind (e.g. bell-shaped / non-monotonic drive). Conservative in purely linear regimes.

### Granger causality
- **Detects:** linear predictive coupling in the stochastic dynamics.
- **Stationarity:** **required** — uses the **stationary** signal version.
- **Directional:** yes (does X's past improve prediction of Y).
- **Idea:** fit a vector autoregression (VAR); F-test whether X's lags reduce Y's prediction error.
- **Params:** `maxlag = 5`, `criterion` = `aic` or `bic`.
- **Note:** the analytic F-test gives a parametric p, **and** Granger is also run through the surrogate null like every other method — its reported significance is the surrogate (empirical) p.
- **Best on:** linear, directional coupling. Blind when the coupling lives in shared trends/oscillations that stationarization removes.

### Pearson
- **Detects:** linear co-variation. **Stationarity:** no. **Directional:** no.
- Fast baseline; misses non-monotonic coupling; inflated by shared drivers.

### Spearman
- **Detects:** monotonic association (rank correlation). **Stationarity:** no. **Directional:** no.
- Robust to monotone nonlinearity; still blind to non-monotonic (even) coupling.

### Mutual Information
- **Detects:** general (nonlinear) statistical dependence. **Stationarity:** no. **Directional:** no.
- Captures dependence correlation misses; needs enough samples to estimate reliably.

### Transfer Entropy
- **Detects:** directed information transfer. **Stationarity:** no. **Directional:** yes.
- Information-theoretic analog of Granger; can be sensitive at estimation limits.

## Trichotomical Analysis Option
Keywords: trichotomy, ccm granger pearson, mandatory set, regime
The **Trichotomy** toggle locks on a mandatory set of three complementary methods: **CCM + Granger + Pearson**. These span the three coupling regimes:
- **Pearson** → linear co-variation.
- **Granger** → linear predictive / directional coupling in stochastic dynamics.
- **CCM** → nonlinear / deterministic coupling.

Reading their agreement/disagreement classifies the coupling regime rather than relying on any single measure.

## Which Method Wins Where
| Situation | Expected winner |
|-----------|-----------------|
| Linear, directional (stochastic) | Granger (Pearson often too) |
| Nonlinear / non-monotonic | CCM (correlation & Granger blind) |
| Monotonic linear co-variation | Pearson / Spearman |
| **Common driver** (hidden Z drives X and Y) | **All can false-positive** |

## Common-Driver Caveat
Keywords: common driver, confound, false positive, hidden variable
When a hidden variable Z drives both X and Y (no direct X–Y coupling), the signals are correlated and mutually predictable but **not causally coupled**. Pearson sees the induced correlation; Granger sees the induced predictability — both may report significance. Surrogate testing controls autocorrelation but **does not remove a genuine common driver**. CCM can also be fooled under strong shared forcing. Method disagreement here is itself informative; ruling out a driver needs experimental control, not statistics alone.
