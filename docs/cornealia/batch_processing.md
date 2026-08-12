# Cornealia — Batch Processing
Keywords: batch, collective_order_batch, parallel, workers, CSV, folder, multiprocessing, AS, BS, paired

## Signature
```python
results = c.collective_order_batch(folder_path, n_workers=10, extensions=('.jpg',))
```

## What It Does
Processes all images in a folder using parallel workers. Each image runs `collective_order()` independently. Failed images are caught and logged without stopping the batch. Results are returned as a list of dicts.

## Parameters
### folder_path
- Type: str or Path
- Description: Path to folder containing specular microscopy images
- Behavior: Recursively scans for files matching extensions

### n_workers
- Type: int
- Default: 1
- Description: Number of parallel worker processes. Each worker loads its own EasyOCR model.
- Recommendation: 8-12 for typical machines. `min(n_workers, n_images, cpu_count)` is enforced.
- Memory: Each worker uses ~500MB (EasyOCR model). 10 workers ≈ 5GB RAM.

### extensions
- Type: tuple of str
- Default: ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')
- Description: File extensions to include in the scan

## Returns
List of dicts — one per image. Each dict has the same keys as `collective_order()` return. Failed images have an `'error'` key instead.

## CelLAB GUI Workflow

### Step 1: Batch Setup
Set all parameters in the GUI:
- Image folder path
- pixel_size, fitting_method, fcm_method
- is_input_image_machine_output
- All other constructor parameters

### Step 2: Run Batch
- Configure number of workers
- Click Run → calls `collective_order_batch()`
- Results saved to `batch_results.csv` with columns:
  - `Image_Name` — filename (stripped to basename)
  - `K`, `K_ds`, `r0_fit`, `n_cells`, `reliable`, etc.
  - `K_um`, `K_ds_um`, `r_0_um` — micrometer-converted values
  - `CD_calc`, `Ave_calc`, `CV_calc`, `HEX_calc` — clinical metrics
  - `CD_cells_mm_2_`, `Ave_micrometer_2_`, `CV`, `HEX___` — machine readings (if available)

### Step 3: Results & Export
- Results table in Graphics panel
- 14 plot types available via right-click Insert Result
- CSV download, Save As with custom format/DPI

## CSV Column Reference

### Computed Metrics (from segmentation)
| Column | Unit | Description |
|--------|------|-------------|
| K | px⁻² | Collective order parameter |
| K_um | μm⁻² | K in physical units |
| K_ds | px⁻² | K from damped sine |
| K_ds_um | μm⁻² | K_ds in physical units |
| r0_fit | px | Equilibrium spacing |
| r_0_um | μm | r₀ in physical units |
| CD_calc | cells/mm² | Cell density |
| Ave_calc | μm² | Average cell area |
| CV_calc | % | Coefficient of variation |
| HEX_calc | % | Hexagonality |
| n_cells | count | Total detected cells |
| reliable | bool | Passed quality gate |

### Machine Readings (from OCR, if available)
| Column | Unit | Description |
|--------|------|-------------|
| CD_cells_mm_2_ | cells/mm² | Machine-reported cell density |
| Ave_micrometer_2_ | μm² | Machine-reported average area |
| CV | % | Machine-reported CV |
| HEX___ | % | Machine-reported hexagonality |

### Derived Columns (added by batch plotter)
| Column | Description |
|--------|-------------|
| group | 'AS', 'BS', or None — parsed from Image_Name |
| patient_id | Patient identifier (Image_Name with AS/BS stripped) |

## AS/BS Group Detection
Image names are parsed to detect AS (After Surgery) and BS (Before Surgery) groups:
- `"001-3731L AS.jpg"` → patient_id=`001-3731L`, group=`AS`
- `"001-3731L BS.jpg"` → patient_id=`001-3731L`, group=`BS`
- Patterns tried: `' AS D1'`, `' BS D1'`, `'_AS'`, `'_BS'`, `' AS'`, `' BS'`
- File extension stripped before matching

## Quick Example
```python
from cornealia.cornealia import cornealia

c = cornealia(pixel_size=0.58, fitting_method='morse', verbose=False)
results = c.collective_order_batch(r"C:\cornea_images", n_workers=10)

# Filter reliable results
reliable = [r for r in results if r.get('reliable', False)]
print(f"Reliable: {len(reliable)}/{len(results)}")

# Convert to DataFrame
import pandas as pd
df = pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (np.ndarray, list))} for r in reliable])
df.to_csv("batch_results.csv", index=False)
```

## Performance
- 45 images, 10 workers: ~2 minutes
- 100 images, 12 workers: ~4-5 minutes
- Bottleneck: EasyOCR initialization per worker (first image slow, rest fast)
