# Signal Associa — API
Keywords: api, parameters, defaults, config, ccm_E, gc_maxlag, surr_method, surr_n, batch_type, n_jobs, results schema, p_best, effect_size, outputs, pkl, summary, meta

## GUI Parameters (saved config, with defaults)
| Param | Default | Meaning |
|-------|---------|---------|
| `m_ccm` | bool | enable CCM |
| `m_granger` | bool | enable Granger |
| `m_pearson` | bool | enable Pearson |
| `m_mi` | bool | enable Mutual Information |
| `m_te` | bool | enable Transfer Entropy |
| `trichotomy` | bool | lock on CCM + Granger + Pearson (mandatory set) |
| `ccm_E` | 2 | CCM embedding dimension |
| `ccm_tau` | 1 | CCM time delay |
| `ccm_n_boot` | 20 | CCM bootstraps |
| `gc_maxlag` | 5 | Granger max lag |
| `gc_criterion` | aic | Granger lag-selection criterion (aic/bic) |
| `stat_method` | auto | stationarizer mode (auto/none/bandpass/difference/detrend) |
| `bp_low` | 0.008 | bandpass low cutoff (Hz) |
| `bp_high` | 0.25 | bandpass high cutoff (Hz) |
| `surr_method` | iaaft | surrogate method (iaaft/aaft/shuffle) |
| `surr_n` | 100 | number of surrogates |
| `surr_alpha` | 0.05 | significance threshold |
| `sampling_rate` | 1 | samples per unit time (sets bandpass time base) |
| `has_header` | auto | CSV header detection |
| `batch_type` | all_pairs \| paired | pairwise vs pre-paired |
| `n_jobs` | 1 | CPU workers (1 = serial + live board, -1 = all cores) |

## Per-Pair, Per-Method Results Schema
Each method entry in a pair's result carries:
| Field | Meaning |
|-------|---------|
| `statistic` | the raw method statistic (ρ, F, MI, etc.) |
| `p_parametric` | analytic p from the method's own test |
| `sig_parametric` | `p_parametric < alpha` |
| `p_surrogate` | empirical p from the surrogate null |
| `sig_surrogate` | `p_surrogate < alpha` |
| `surr_mean` | mean of the null distribution |
| `surr_std` | std of the null distribution |
| `p_best` | empirical p if surrogates ran, else parametric |
| `significant` | `p_best < alpha` (the reported decision) |
| `effect_size` | (statistic − surr_mean) / surr_std |

## On-Disk Outputs
Written per run:
| File | Contents |
|------|----------|
| `associa_results.pkl` | full results object (all pairs, all methods, null distributions) |
| `summary.csv` | flat table: one row per pair × method with p-values and significance |
| `summary.json` | same summary as JSON |
| `meta.json` | run metadata (config, timing, versions) |
| `README.md` | human-readable run description |
| `plots/` | inserted plot images |
| `runs/<run_id>/` | per-run folder grouping the above |

## Minimal Engine Usage
```python
from signal_associa.signal_associa import Associa

engine = Associa({
    'stationarizer': {'method': 'auto'},
    'surrogate': {'method': 'iaaft', 'n_iterations': 100},
    'methods': {
        'pearson':           {'n_surrogates': 100},
        'granger_causality': {'maxlag': 5, 'n_surrogates': 100},
        'ccm':               {'E': 2, 'tau': 1, 'n_surrogates': 100},
    },
    'seed': 0,
})
result = engine.run(x, y)          # x, y: 1-D numpy arrays
for row in result['summary']:
    print(row['method'], row['p_best'], row['significant'])
```

Note: pass `n_surrogates` to **every** method you want surrogate-tested, **including Granger** — the engine default for Granger is 0 (parametric only), so the GUI/batch must set it to the surrogate N to match the analysis.
