# Cornealia — API Reference
Keywords: cornealia, constructor, parameters, collective_order, batch, pixel_size, fitting_method, fcm_method, invert_image, cellade_params, machine_type, residual_field, force field, pipeline

## Constructor

### cornealia()
Signature: `cornealia(pixel_size=0.58, fitting_method='morse', is_input_image_machine_output=True, fcm_method='local', verbose=True, ...)`

Creates a configured analyzer instance. No image is loaded — the same instance can process multiple images.

### pixel_size
- Type: float
- Default: 0.58
- Unit: μm/pixel
- Description: Physical size of one pixel in the specular microscope image
- Affects: K_um, K_ds_um, r_0_um, Ave_calc (all micrometer-converted outputs)
- Common values: 0.45 (Topcon SP-1P), 0.58 (Konan CellChek), 0.34 (Heidelberg HRT)

### fitting_method
- Type: str
- Default: 'morse'
- Options: 'morse'
- Description: Potential model used to fit V(r) and extract K. Morse potential: D_e(1-exp(-a(r-r₀)))²
- Affects: K, r0_fit, fitting curve shape

### machine_type
- Type: str
- Default: 'cellchek_d'
- Options: 'cellchek_d', 'none'
- Description: Machine profile key defining crop coordinates for cell area and metrics area. Use 'none' for raw images without machine overlay.
- Affects: Preprocessing crop regions

### invert_image
- Type: bool
- Default: False
- Description: Invert image intensity before segmentation. Use for dark-on-light images (e.g. some phase-contrast).
- Affects: Segmentation input

### cellade_params
- Type: dict
- Default: {} (empty — use CellADE defaults)
- Description: Pass-through parameters to the CellADE segmentation engine. Keys override CellADE's own defaults.
- Example: `{'sigma': 2.5, 'min_cell_area': 50}`

### is_input_image_machine_output
- Type: bool
- Default: True
- Description: Whether the image includes machine overlay (green dots, text). If True, OCR extracts machine metrics and green dots are detected for Voronoi verification. If False, treats image as raw cell area.
- Affects: machine_metrics, dot_centroids, voronoi_metrics

### fcm_method
- Type: str
- Default: 'local'
- Options: 'local', 'global'
- Description: Fuzzy C-Means clustering method for CellADE segmentation
- Affects: Segmentation quality, number of detected cells

### min_expansion_shells
- Type: int
- Default: 5
- Description: Minimum watershed expansion iterations for CellADE
- Affects: Cell boundary detection

### min_interior_cells_ratio
- Type: float
- Default: 0.4
- Description: Minimum fraction of cells that must be interior (not touching border) for analysis to proceed
- Affects: Whether analysis is attempted

### exclusion_ratio
- Type: float
- Default: 0.15
- Description: Fraction of image border excluded from interior cell selection. MAX_R = min(H,W) * exclusion_ratio
- Affects: Number of interior cells, g(r) range

### shell_thickness
- Type: int
- Default: 1
- Unit: pixels
- Description: Width of radial shells for g(r) computation (DR parameter)
- Affects: g(r) resolution, smoothness

### fitting_half_width
- Type: int
- Default: 10
- Description: Half-width of the fitting window around V(r) minimum
- Affects: Morse/LJ fit quality, K accuracy

### SAVGOL_WINDOW
- Type: int
- Default: 11
- Description: Savitzky-Golay smoothing window for g(r) display (odd integer)
- Affects: g(r) plot smoothness (NOT used for fitting)

### SAVGOL_ORDER
- Type: int
- Default: 3
- Description: Savitzky-Golay polynomial order
- Affects: g(r) plot smoothness

### verbose
- Type: bool
- Default: True
- Description: Print per-image analysis details. Set False for batch processing.
- Affects: Console output only

## Methods

### collective_order()
Signature: `collective_order(image_path) → dict`
Full single-image analysis. See: cornealia/collective_order.md

### collective_order_pipeline()
Signature: `collective_order_pipeline(image_path, centroids=None, image_dims=None, reporter=None) → dict`
Full pipeline used by the GUI. Wraps preprocessing + segmentation + classic metrics + collective_order + residual force field into one call. Returns a merged results dict with all outputs. If `centroids` and `image_dims` are provided, skips image loading and segmentation (useful for re-analysis).

### collective_order_batch()
Signature: `collective_order_batch(folder_path, n_workers=1, extensions=('.jpg','.jpeg','.png','.tiff','.bmp')) → list[dict]`
Parallel batch processing. See: cornealia/batch_processing.md

### plot()
Signature: `plot(results, save=False, save_dir='cornealia_results', formats=('png','pdf')) → cornealia_plotter`
Create plotter object. See: cornealia/plotters.md

### Internal Methods (not typically called directly)
- `_load_image(image_path)` — load image via cv2, handle special characters in path
- `cleaning_preprocessing(input_image)` — crop via machine profile, detect green dots (HSV), remove by inpainting, OCR extract metrics
- `segmentation(cell_area)` — CellADE segmentation → objects, segmentor
- `_compute_classic_metrics(centroids, areas, H, W, method, dot_centroids)` — CD, Ave, CV, HEX via segmentation or Voronoi method
- `_compute_residual_field(co_results)` — Delaunay truss construction, per-cell force |F_i| = |Σ -V'(d) · û|, returns mean_F, frac_compression, spatial_cv, n_hot_spots
- `_collective_order_safe(image_path)` — exception-safe wrapper for parallel use
