# CellADE — Algorithm Details
Keywords: cellade, algorithm, pipeline, FFT, sigma, strip ROI, blob detection, LoG, fuzzy c-means, FCM, watershed, gap filling, preprocessing, CLAHE

## Pipeline Architecture
CellADE uses a sequential pipeline of classical image processing steps. No machine learning is involved. Each step has physically interpretable parameters.

## Step 1: Preprocessing
- Convert to grayscale (if RGB)
- Normalize intensity to [0, 1]
- Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) with `clahe_clip` parameter
- Store as `self.enhanced`

## Step 2: Seed Detection
Two sub-modes depending on `use_fft_sigma`:

### Standard Mode (use_fft_sigma=False)
- Apply Laplacian-of-Gaussian (LoG) blob detection
- Scale range: `[log_min_sigma, log_max_sigma]` with `log_num_sigma` scales
- Threshold: `log_threshold`
- Each detected blob = one seed (cell center candidate)

### FFT Mode (use_fft_sigma=True) — Two-Stage Detection
1. **Strip Analysis**: Divide image into vertical strips, compute Sobel edge density per strip. Reject strips with low edge density (empty regions) or high jaggedness (artifacts). The valid strips define the cell-containing region.
2. **FFT Sigma Estimation**: Extract a crop from the cell region centroid. Compute 2D FFT power spectrum. Find the dominant radial frequency peak → convert to cell diameter → set sigma range as `[peak * (1 - margin), peak * (1 + margin)]`.
3. **Final LoG**: Run blob detection with the FFT-derived sigma range.
4. **Seed Exclusion**: Reject seeds that fall outside the strip-defined cell region.

### Why FFT Mode Matters
Clinical specular microscopy images vary in magnification, cell size, and field coverage. Manual sigma tuning fails across diverse datasets. FFT sigma estimation adapts automatically to each image's cell size, improving robustness from F1=0.434 (fixed sigma) to F1=0.504 (FFT sigma) on the Daniel benchmark.

## Step 3: Foreground Extraction (Fuzzy C-Means)
Separate cell interiors from boundaries/background using fuzzy clustering:

### Global Mode (fcm_mode='global')
- Cluster entire image into `fcm_n_clusters` groups
- Assign pixels with membership > `fcm_threshold` to foreground

### Local Mode (fcm_mode='local')
- For each seed, extract a local window (size = `local_window_factor × estimated_cell_size`)
- Run FCM within each window
- Merge local foreground maps

### Global+Local Mode (fcm_mode='global_local')
- Run both global and local FCM
- Combine: foreground = global AND local agreement

## Step 4: Initial Segmentation (Watershed)
- Seeds become markers
- Distance transform of foreground mask
- Marker-controlled watershed on the distance transform
- Each watershed basin = one cell

## Step 5-9: Post-Processing (Optional)
| Step | Parameter | Purpose |
|------|-----------|---------|
| 5 | `use_curvature_merging` | Merge over-segmented cells by analyzing boundary curvature |
| 6 | `use_morphological_smooth` | Smooth cell boundaries with morphological opening/closing |
| 7 | `use_fft_smooth` | Frequency-domain boundary smoothing |
| 8 | `use_honeycomb_merge` | Merge small fragments into neighbors |
| 9 | `use_gap_fill` | Close intercellular gaps via dilation → erosion (default ON in cornealia) |

## Cornealia Preset Specifics
The cornealia mode sets:
- `seeding_method`: 'blob_log'
- `log_min_sigma`: 6, `log_max_sigma`: 18 (overridden by FFT if enabled)
- `fcm_mode`: 'local'
- `use_gap_fill`: True
- All other post-processing: off
- Strip ROI parameters tuned for specular microscopy partial-coverage fields

## Design Philosophy
- **Transparency**: Every parameter maps to a physical quantity (cell size range, contrast, threshold). No black-box learned features.
- **Robustness**: Works on any specular microscope without retraining. FFT sigma adapts to image-specific cell sizes.
- **CPU-only**: No GPU dependencies. Runs on clinical workstations, laptops, cloud VMs.
- **Centroid accuracy**: Optimized for centroid detection (needed for g(r) computation) rather than pixel-precise boundary delineation.
