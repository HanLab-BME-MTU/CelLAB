# Signal Associa — Surrogate Significance
Keywords: surrogate, iaaft, aaft, shuffle, null distribution, empirical p, parametric p, p_best, effect size, surr_mean, surr_std, alpha, significance

## Why Surrogates
A raw statistic (a correlation, an F-value, a cross-map ρ) does not tell you whether coupling is real. Autocorrelated biological signals produce large statistics by chance. The surrogate test builds an empirical null: generate N synthetic copies of X that keep its statistical properties but destroy any coupling to Y, recompute the method on each, and see where the real statistic falls in that null.

## Surrogate Methods
| Method | Preserves | Notes |
|--------|-----------|-------|
| **IAAFT** (default) | amplitude distribution **and** power spectrum | best control for autocorrelated signals |
| AAFT | amplitude distribution, approximate spectrum | simpler, less exact than IAAFT |
| shuffle | marginal distribution only | destroys all temporal structure; inflates FPR on autocorrelated nulls |

Defaults: `surr_n = 100`, `surr_alpha = 0.05`.

## All Methods Run the Null
Every method — Pearson, Spearman, MI, Granger, CCM, TE — is passed through the surrogate loop. Granger's analytic F-test still produces a parametric p, but Granger's **reported** significance is the empirical p, exactly like the other methods. (Only CCM has a GPU-accelerated batch path for the null; the rest run serially.)

## Parametric vs Surrogate p
- `p_parametric` (`p_value`): analytic p from the method's own test (e.g. Granger's F-distribution). Ignores autocorrelation, so it over-reports significance on time series.
- `p_surrogate` (`p_empirical`): empirical p from the surrogate null.
- **`p_best`**: the empirical p if surrogates ran, else the parametric p. This is what drives the `significant` flag (`p_best < alpha`).

## Empirical p-value
One-sided, with a +1 correction so p is never exactly 0:

```
p = (# surrogates with statistic >= real  + 1) / (N + 1)
```

With N = 100 the smallest achievable p is 1/101 ≈ 0.0099 (the "surrogate floor").

## Effect Size and Null Summary
- `surr_mean`, `surr_std`: mean and standard deviation of the null distribution.
- `effect_size` = (real − surr_mean) / surr_std — how many null standard deviations the real statistic sits above the null (Cohen's-d style). Large positive = strong, well-separated coupling.

## Reading the Result
| p_surrogate | Meaning |
|-------------|---------|
| ≈ 0.0099 (floor) | strongly significant; real statistic beats every surrogate |
| < alpha | significant |
| ≥ alpha | not significant — coupling not distinguishable from the null |

A significant parametric p with a non-significant surrogate p is the classic autocorrelation false positive that surrogate testing catches.
