# CellADE — API Reference
Keywords: cellade, CellADE, constructor, run, get_centroids, get_labels, parameters, mode, cornealia, params, sigma, fcm, watershed

## Constructor

```python
from shared_modules.cellade.cellade import CellADE
seg = CellADE(mode='cornealia', params=None)
```

### mode
- Type: str
- Options: `'cornealia'`, `'default'`, or `None`
- Description: Selects a preset parameter configuration. `'cornealia'` is optimized for corneal endothelial cells.

### params
- Type: dict or None
- Description: Override specific parameters. Merged on top of the mode preset.
- Example: `{'use_fft_sigma': True, 'fcm_mode': 'local'}`

## Cornealia Mode Parameters

### Preprocessing
| Parameter | Default | Description |
|-----------|---------|-------------|
| `clahe_clip` | 0.03 | CLAHE contrast clip limit |

### Seed Detection (Blob Detection)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `seeding_method` | 'blob_log' | Seed detection method: 'blob_log' or 'h_maxima' |
| `log_min_sigma` | 6 | Minimum blob scale (pixels) |
| `log_max_sigma` | 18 | Maximum blob scale (pixels) |
| `log_num_sigma` | 15 | Number of scales to test |
| `log_threshold` | 0.01 | Blob detection sensitivity |
| `use_fft_sigma` | False | Enable FFT-based adaptive sigma estimation |

### FFT Sigma Estimation
| Parameter | Default | Description |
|-----------|---------|-------------|
| `fft_margin_factor` | 0.3 | Margin around FFT peak for sigma range |

### Strip-Based ROI (for FFT)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `strip_n_strips` | 5 | Number of vertical strips to test |
| `strip_edge_threshold` | 0.12 | Sobel edge density threshold |
| `strip_jaggedness_threshold` | 0.3 | Jaggedness threshold for strip rejection |
| `strip_min_valid` | 2 | Minimum valid strips required |
| `strip_cell_fraction` | 0.6 | Fraction of width to use for cell region |
| `strip_fft_crop_size` | 256 | FFT analysis crop size (pixels) |

### Foreground Extraction (FCM)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `fcm_mode` | 'local' | FCM strategy: 'global', 'local', or 'global_local' |
| `fcm_n_clusters` | 3 | Number of fuzzy clusters |
| `fcm_fuzziness` | 2 | Fuzziness exponent (m) |
| `fcm_threshold` | 0.5 | Membership threshold for foreground |
| `local_window_factor` | 3.0 | Local FCM window size as multiple of cell size |

### Post-Processing
| Parameter | Default | Description |
|-----------|---------|-------------|
| `use_curvature_merging` | False | Merge over-segmented cells by boundary curvature |
| `use_morphological_smooth` | False | Morphological edge smoothing |
| `use_fft_smooth` | False | FFT boundary smoothing |
| `use_honeycomb_merge` | False | Merge small fragments |
| `use_gap_fill` | True | Fill intercellular gaps |
| `gap_fill_iterations` | 3 | Gap fill dilation/erosion iterations |

## run()

```python
seg.run(image, detail=False)
```

### Parameters
- `image` (ndarray): Input image (grayscale or RGB, any dtype)
- `detail` (bool): If True, return timing and intermediate info dict

### Behavior
Runs the full pipeline: preprocess → seeds → foreground → watershed → post-processing. Results stored internally.

### Returns
- If `detail=False`: None (access results via get_centroids, get_labels)
- If `detail=True`: dict with timing info and intermediate counts

## get_centroids()

```python
centroids = seg.get_centroids()
```

### Returns
- ndarray of shape (N, 2) with (y, x) centroid coordinates
- Empty array if no cells detected

### Note
Coordinates are in (row, col) = (y, x) order. To convert to (x, y) for plotting:
```python
xy = centroids[:, ::-1]  # flip to (x, y)
plt.scatter(xy[:, 0], xy[:, 1])
```

## get_labels()

```python
labels = seg.get_labels()
```

### Returns
- ndarray (H, W) integer label mask. 0 = background, 1..N = cell IDs.

## Internal State
After `run()`, these attributes are available:
| Attribute | Type | Description |
|-----------|------|-------------|
| `seg.enhanced` | ndarray | CLAHE-enhanced image (float, 0-1) |
| `seg.seeds` | ndarray | Detected seed positions |
| `seg.foreground` | ndarray | Binary foreground mask |
| `seg.labels` | ndarray | Watershed label mask |
| `seg.objects` | list | regionprops objects for each cell |
| `seg.estimated_sigma` | float or None | FFT-estimated sigma (if use_fft_sigma) |

## Quick Examples

### Basic Usage
```python
from shared_modules.cellade.cellade import CellADE
import numpy as np
from PIL import Image

img = np.array(Image.open("cornea.png"))
seg = CellADE(mode='cornealia', params={'use_fft_sigma': True})
seg.run(img)
print(f"Detected {len(seg.get_centroids())} cells")
```

### Custom Parameters
```python
seg = CellADE(mode='cornealia', params={
    'use_fft_sigma': False,
    'log_min_sigma': 10,
    'log_max_sigma': 20,
    'fcm_mode': 'global_local',
})
seg.run(img)
```

### With Timing Info
```python
seg = CellADE(mode='cornealia')
info = seg.run(img, detail=True)
print(f"Seeds: {info['n_seeds']}, Cells: {info['n_objects']}")
print(f"Time: {info['total_time']:.1f}s")
```

## Common Issues
- **Too few cells detected**: Increase `log_num_sigma` or widen `[log_min_sigma, log_max_sigma]` range. Enable `use_fft_sigma` for automatic scale.
- **Too many false positives**: Increase `log_threshold` (e.g., 0.02) or increase `fcm_threshold`.
- **Slow on large images**: CellADE processes at full resolution. Downsample if image is >2000px.
- **Cells merged together**: Enable `use_curvature_merging` or decrease `fcm_fuzziness`.
