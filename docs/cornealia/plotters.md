# Cornealia — Plotters Reference
Keywords: plot, plotter, visualization, g(r), V(r), segmentation, publication, batch, boxplot, scatter, validation

## Single Image Plotter (cornealia_plotter)

### Usage
```python
from cornealia.plotters.cornealia_plotter import cornealia_plotter
plotter = cornealia_plotter(results, save=True, save_dir='plots', formats=('png',))
plotter.comprehensive()  # or any specific method
```

### Available Methods

#### segmentation
- Output: `01_segmentation_overview.png`
- Shows: Original image, cell area, segmentation overlay, cell boundaries
- Use when: Checking segmentation quality

#### radial_distribution
- Output: `02_radial_distribution.png`
- Shows: g(r) raw and smoothed, with damped sine fit overlay
- Use when: Examining spatial cell distribution

#### potential
- Output: `03_potential_Vr.png`
- Shows: V(r) = -ln(g(r)) with Morse/LJ fit overlay
- Use when: Examining cell interaction potential

#### fitting
- Output: `04_fitting_*.png`
- Shows: Detailed fitting diagnostics — fit window, residuals, parameter uncertainties
- Use when: Debugging K values or fit quality

#### comprehensive
- Output: `05_comprehensive.png`
- Shows: 6-panel overview: segmentation + g(r) + V(r) + fitting + metrics summary
- Use when: Quick overview of entire analysis

#### publication_gr
- Output: `06_publication_gr.png`
- Shows: Publication-ready g(r) plot with proper formatting
- Use when: Preparing figures for papers

#### publication_vr
- Output: `07_publication_vr.png`
- Shows: Publication-ready V(r) plot
- Use when: Preparing figures for papers

#### pipeline_figure
- Output: `pipeline_figure.png`
- Shows: Full pipeline visualization from raw image to final results
- Use when: Method papers, presentations

#### all
- Runs all above methods sequentially
- Use when: Generating complete visualization suite

## Batch Plotter (cornealia_batch_plotter)

### Usage
```python
from cornealia.plotters.cornealia_batch_plotter import cornealia_batch_plotter
plotter = cornealia_batch_plotter('batch_results.csv', save=True, save_dir='plots')
plotter.distributions()
```

### Available Methods (14 total)

#### Category 1: Distributions
| Method | Description |
|--------|-------------|
| `distributions()` | Histograms for all computed metrics (dynamic grid) |
| `histogram(metric='K_um')` | Single metric distribution with stats |

#### Category 2: AS vs BS Comparisons
| Method | Description |
|--------|-------------|
| `as_vs_bs_boxplots()` | Box plots comparing AS vs BS with paired t-test |
| `as_vs_bs_scatter()` | Paired scatter plots (BS on x, AS on y) |
| `as_vs_bs_histograms()` | Overlaid histograms for each group |

#### Category 3: Validation (Computed vs Machine)
| Method | Description |
|--------|-------------|
| `validation_scatter()` | Scatter: computed metric vs machine reading with R² |
| `validation_bland_altman()` | Bland-Altman agreement plots |

#### Category 4: Improvement Analysis
| Method | Description |
|--------|-------------|
| `as_vs_bs_improvement(metric)` | Per-patient improvement panel for one metric |
| `as_vs_bs_improvement_all()` | Improvement analysis for all metrics |

#### Category 5: Deep Dive
| Method | Description |
|--------|-------------|
| `deep_dive(metric)` | 6-panel comprehensive analysis for one metric |

#### Category 6: Publication-Ready
| Method | Description |
|--------|-------------|
| `pub_boxplots()` | Publication-ready AS vs BS boxplots with violin |
| `pub_K_deep_dive()` | Publication-ready K analysis (6 panels) |
| `pub_validation()` | Publication-ready validation scatter |
| `pub_K_independence()` | K independence from image quality factors |
| `pub_comprehensive()` | Full publication figure (requires gr_data) |
| `pub_representative()` | Representative images with Voronoi overlays |

#### all
- Runs all methods sequentially

### Computed Metrics (COMPUTED_METRICS dict)
The batch plotter uses dynamic grids that adapt to available columns:
- K_um, K_ds_um, r_0_um — order parameters in physical units
- CD_calc, Ave_calc, CV_calc, HEX_calc — clinical metrics
- K_Vmin_um, K_gpeak_um — alternative K formulations

Methods skip missing columns gracefully — no crashes on incomplete data.
