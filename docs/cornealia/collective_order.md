# Cornealia — collective_order() Detail
Keywords: collective_order, single image, analysis, results, K, g(r), V(r), reliable, morphometry, K_ds, damped sine, quality gate, force field, residual, five methods, RMSE, fitting, step response

## Signature
```python
results = c.collective_order(image_path)
```

## What It Does
Runs the full Cornealia analysis pipeline on a single image:
1. Load image
2. If machine output: OCR extraction + green dot detection + cell area extraction
3. CellADE segmentation (FCM + watershed)
4. Compute cell morphological metrics (CD, Ave, CV, HEX) via both segmentation and Voronoi methods
5. Identify interior cells (exclude border region)
6. Compute g(r) — radial distribution function
7. Smooth g(r) with Savitzky-Golay (for display only)
8. Compute V(r) = -ln(g(r))
9. Quality gate: damped sine fit on g(r)-1
10. If reliable: fit V(r) with Morse potential → extract K, r₀
11. Return comprehensive results dict

## Five K Extraction Methods
All methods extract K = V''(r₀), the curvature of V(r) at its minimum. They differ in how the minimum is located and what function is fitted.

| # | Method | Fitting region | Formula | Code key |
|---|--------|---------------|---------|----------|
| 1 | Quad raw | ±fitting_half_width around argmin(V) | K = 2|a₂| from polyfit deg 2 | `K_quad_raw` |
| 2 | Morse raw | Same as #1 | K = 2·D_e·a² from Morse fit D_e(1-exp(-a(r-r₀)))² | `K_morse_raw` |
| 3 | Quad guided | Quality-gate-derived well boundaries | Same as #1 | `K_quad_guided` |
| 4 | Morse guided | Same as #3 | Same as #2 | `K_morse_guided` |
| 5 | **DS (recommended)** | Full oscillatory region from quality gate | K_ds = V''(r₀) computed analytically from the QG fit — no separate fitting | `K_ds` |

**Why DS is best**: Methods 1-4 fit V(r) = -ln(g(r)), which amplifies noise. DS fits g(r) directly with a damped sine, then derives V analytically from the smooth fit. CV drops from 42-44% to 29%.

## Quality Gate: Step Response Model
The quality gate fits g(r)-1 with a damped step response:

`H(r) × [-A·exp(-(r-r_excl)/ξ)·sin(2π(r-r_excl)/λ + φ)]`

where H(r) is a sigmoid Heaviside at r_excl. Five parameters: A (amplitude), ξ (decay length), λ (wavelength), r_excl (exclusion radius), φ (phase).

**Reliability criteria** (all must hold):
- Form: positive peak + zero crossing + negative trough in fitted oscillation
- Parameter bounds: ξ < 95·px_scale, 8/px_scale < λ < 70·px_scale
- Peak height: g_peak > 1.10
- Either R²(osc) > 0.5, or R²(osc) > 0.2 with white noise (|ACF1| < 0.4) and SNR > 1.2

**Two R² values**: R2_full = fit quality on entire g(r)-1. R2_damped = fit quality on oscillatory region only (r ≥ r_excl). R2_damped is used for the reliability decision.

## K_ds Derivation
K_ds reuses the quality gate fit — no separate fitting step. From the fitted g(r), compute V(r) = -ln(g_fitted) on a dense 1000-point grid from r_excl to r_max. Find r₀ = argmin(V). Compute K_ds = V''(r₀) via double numerical gradient. This gives one fit → two outputs (reliability flag + K_ds).

## Residual Force Field
After collective_order completes, the pipeline computes a per-cell residual force field via Delaunay triangulation.

| Key | Type | Description |
|-----|------|-------------|
| `residual_field` | ndarray | Per-cell force magnitude |F_i| array |
| `mean_F` | float | Mean |F| across all interior cells (µm⁻¹) |
| `frac_compression` | float | Fraction of edges under compression (d < r₀) |
| `spatial_cv` | float | Spatial coefficient of variation of |F_i| |
| `n_hot_spots` | int | Number of high-stress concentrator cells |

## Parameters
- `image_path` (str or Path): Path to the specular microscopy image file

## Returns
Dict with the following keys:

### Core Results
| Key | Type | Description |
|-----|------|-------------|
| `K` | float | Backward-compat alias for K_morse_guided (px⁻²) |
| `K_quad_raw` | float | Quadratic fit on raw V(r) around argmin |
| `K_morse_raw` | float | Morse fit on raw V(r) around argmin |
| `K_quad_guided` | float | Quadratic fit on QG-guided well |
| `K_morse_guided` | float | Morse fit on QG-guided well |
| `K_ds` | float | **Recommended.** From damped sine fit on g(r) |
| `K_Vmin` | float | K × |V_min| |
| `K_gpeak` | float | K × (g_peak - 1) |
| `r0_fit` | float | Equilibrium spacing from Morse fit (px) |
| `v_min` | float | V(r) minimum value |
| `g_peak` | float | g(r) peak value |
| `n_cells` | int | Total cells detected |
| `n_interior` | int | Interior cells used for g(r) |
| `rmse_quad_raw` | float | RMSE of quad raw on guided well |
| `rmse_morse_raw` | float | RMSE of Morse raw on guided well |
| `rmse_quad_guided` | float | RMSE of quad guided on guided well |
| `rmse_morse_guided` | float | RMSE of Morse guided on guided well |
| `rmse_ds` | float | RMSE of DS-derived V(r) on guided well |

### Quality Gate
| Key | Type | Description |
|-----|------|-------------|
| `reliable` | bool | Whether analysis passed reliability check |
| `has_peak` | bool | g(r) has a positive peak |
| `has_crossing` | bool | g(r)-1 crosses zero |
| `has_trough` | bool | g(r) has a trough after peak |
| `R2_damped` | float | R² on oscillatory region (used for QC) |
| `R2_full` | float | R² on full g(r)-1 curve |
| `A_damped` | float | Amplitude of damped sine |
| `xi_damped` | float | Decay length ξ (pixels) |
| `lambda_damped` | float | Wavelength λ (pixels) |
| `r_excl_damped` | float | Exclusion radius from fit (pixels) |
| `phi_damped` | float | Phase φ (radians) |
| `SNR` | float | Signal-to-noise ratio (A / residual σ) |
| `ACF1` | float | Autocorrelation lag-1 of residuals |

### Clinical Metrics (Segmentation Method)
| Key | Type | Description |
|-----|------|-------------|
| `CD_calc` | float | Cell density (cells/mm²) |
| `Ave_calc` | float | Average cell area (μm²) |
| `SD_calc` | float | Standard deviation of cell area |
| `CV_calc` | float | Coefficient of variation (%) |
| `HEX_calc` | float | Hexagonality (%) |

### Raw Data (for plotting)
| Key | Type | Description |
|-----|------|-------------|
| `r_values` | ndarray | Radial distances (pixels) |
| `g_r` | ndarray | Raw g(r) values |
| `g_r_smooth` | ndarray | Smoothed g(r) (Savgol, display only) |
| `v_r` | ndarray | V(r) = -ln(g(r)) |
| `r_valid` | ndarray | r where g(r) > 0.05 |
| `v_r_valid` | ndarray | V(r) at valid points |
| `r_fit_raw` | ndarray | Fitting region for raw methods |
| `v_fit_raw` | ndarray | V(r) in raw fitting region |
| `r_fit_guided` | ndarray | Fitting region for guided methods |
| `v_fit_guided` | ndarray | V(r) in guided fitting region |
| `r_fit_ds` | ndarray | g(r)-1 from r_excl onward (DS region) |
| `v_fit_ds` | ndarray | g(r)-1 values in DS region |

### Fit Parameters
| Key | Type | Description |
|-----|------|-------------|
| `popt_qc` | tuple | Quality gate fit: (A, ξ, λ, r_excl, φ) |
| `coeffs_qr` | ndarray | Quadratic raw: polyfit coefficients |
| `coeffs_qg` | ndarray | Quadratic guided: polyfit coefficients |
| `popt_mr` | tuple | Morse raw: (D_e, a, r₀, offset) |
| `popt_mg` | tuple | Morse guided: (D_e, a, r₀, offset) |
| `popt_ds` | tuple | Same as popt_qc (DS reuses QG fit) |

### Image/Segmentation Data
Also returns: `image_path`, `input_image`, `cell_area`, `segmentor` (CellADE instance), `objects` (regionprops), `machine_metrics` (OCR dict or None), `dot_centroids` (ndarray or None), `voronoi_metrics` (dict).

## Quick Example
```python
from cornealia.cornealia import cornealia

c = cornealia(pixel_size=0.58, fitting_method='morse')
results = c.collective_order("path/to/image.jpg")

print(f"K = {results['K']:.4f}")
print(f"Cells: {results['n_cells']}")
print(f"Reliable: {results['reliable']}")
print(f"CD = {results['CD_calc']:.0f} cells/mm²")
```

## Full Example with Plotting
```python
from cornealia.cornealia import cornealia

c = cornealia(pixel_size=0.58, fitting_method='morse', verbose=True)
results = c.collective_order("001-3731L AS.jpg")

# Check reliability first
if results['reliable']:
    print(f"K = {results['K']:.4f} px⁻²")
    print(f"K_um = {results['K'] / 0.58**2:.4f} μm⁻²")
    print(f"r₀ = {results['r0_fit']:.1f} px = {results['r0_fit'] * 0.58:.1f} μm")
else:
    print("Image failed reliability check — K is unreliable")

# Plot
plotter = c.plot(results, save=True, save_dir='my_results')
plotter.comprehensive()
```

## Common Issues
- **"0 interior cells"**: Image too small or exclusion_ratio too large. Try `exclusion_ratio=0.10`.
- **"Not reliable"**: Low cell count, poor image quality, or non-endothelial tissue. Check `R2_damped` and `n_interior`.
- **K = 0 or NaN**: Morse fit failed. Check V(r) shape — may need different `fitting_half_width`.
