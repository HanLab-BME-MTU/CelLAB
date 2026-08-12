# Cornealia — collective_order() Detail
Keywords: collective_order, single image, analysis, results, K, g(r), V(r), reliable, morphometry

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

## Parameters
- `image_path` (str or Path): Path to the specular microscopy image file

## Returns
Dict with the following keys:

### Core Results
| Key | Type | Description |
|-----|------|-------------|
| `K` | float | Collective order parameter (pixel units) |
| `K_Vmin` | float | K × |V_min| |
| `K_gpeak` | float | K × (g_peak - 1) |
| `K_ds` | float | K from damped sine fit |
| `r0_fit` | float | Equilibrium spacing from Morse fit (pixels) |
| `v_min` | float | V(r) minimum value |
| `g_peak` | float | g(r) peak value |
| `n_cells` | int | Total cells detected |
| `n_interior` | int | Interior cells used for g(r) |

### Quality Gate
| Key | Type | Description |
|-----|------|-------------|
| `reliable` | bool | Whether analysis passed reliability check |
| `has_peak` | bool | g(r) has a positive peak |
| `has_crossing` | bool | g(r)-1 crosses zero |
| `has_trough` | bool | g(r) has a trough after peak |
| `R2_damped` | float | R² of damped sine fit |
| `A_damped` | float | Amplitude of damped sine |
| `xi_damped` | float | Decay length of damped sine |
| `lambda_damped` | float | Wavelength of damped sine |
| `SNR` | float | Signal-to-noise ratio |
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
| `g_r_smooth` | ndarray | Smoothed g(r) |
| `v_r` | ndarray | V(r) = -ln(g(r)) |
| `r_valid` | ndarray | r values in fitting range |
| `v_r_valid` | ndarray | V(r) in fitting range |

### Image/Segmentation Data
| Key | Type | Description |
|-----|------|-------------|
| `image_path` | str | Input image path |
| `input_image` | ndarray | Original loaded image |
| `cell_area` | ndarray | Extracted cell region |
| `segmentor` | CellADE | Segmentation engine instance |
| `objects` | list | Detected cell objects (regionprops) |
| `machine_metrics` | dict or None | OCR-extracted machine readings |
| `dot_centroids` | ndarray or None | Green dot positions |
| `voronoi_metrics` | dict | Voronoi-based metrics for verification |

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
