# Cornealia — Overview
Keywords: corneal, endothelium, specular microscopy, morphometry, collective order, g(r), V(r), K, K_ds, cell density, hexagonality, batch, CellADE

## What It Does
Cornealia analyzes corneal endothelial cell images from specular microscopy. It computes the radial distribution function g(r), interaction potential V(r), and a collective order parameter K that quantifies how ordered the cell mosaic is. It also computes standard clinical metrics: cell density (CD), average cell area (Ave), coefficient of variation (CV), and hexagonality (HEX).

## Key Concepts

### Collective Order Parameter (K)
K measures the strength of cell-cell spatial interactions. Five extraction methods are available, but K_ds (damped-sine derived) is recommended. It achieves the lowest coefficient of variation (CV=29%) and highest sensitivity to biological changes among all methods.

### Five K Extraction Methods
| Method | Key | Description | CV |
|--------|-----|-------------|----|
| Quad raw | K_quad_raw_um | Quadratic fit on raw V(r) around argmin | 42% |
| Morse raw | K_morse_raw_um | Morse potential fit on raw V(r) around argmin | 42% |
| Quad guided | K_quad_guided_um | Quadratic fit on quality-gate-guided V(r) region | 44% |
| Morse guided | K_morse_guided_um | Morse potential fit on guided V(r) region | 43% |
| **DS (recommended)** | **K_ds_um** | **Damped sine fit on g(r), K derived analytically** | **29%** |

### Radial Distribution Function g(r)
g(r) measures the probability of finding a cell center at distance r from another cell center, normalized by random expectation. g(r) > 1 means cells prefer that spacing; g(r) < 1 means they avoid it.

### Interaction Potential V(r)
V(r) = -ln(g(r)). Converts the statistical distribution into a pseudo-potential. The minimum of V(r) gives the preferred cell spacing r₀.

### Damped Sine Fit (DS Method)
The recommended K extraction fits g(r)-1 with a damped oscillatory function: A·exp(-r/ξ)·sin(2πr/λ + φ). K_ds is computed analytically from the fitted parameters at the potential minimum. This avoids noise amplification from the V(r) = -ln(g(r)) transform.

### Quality Gate (Reliability Check)
A damped sine fit on g(r)-1 determines if the image has sufficient order for reliable analysis. Checks: R², amplitude, peak presence, zero crossing, trough presence, SNR. Specificity ≥98.5% (almost never accepts noise as signal). On clinical data: 99.5% of images pass.

### AS/BS Groups
For longitudinal studies: AS = After Stripping (surgery), BS = Before Stripping. Image names containing "AS" or "BS" are grouped for paired statistical comparisons.

### Clinical Findings (776 pairs, Singapore Eye Centre)
- K_ds increased by +10.3% after stripping (p=0.047, paired t-test)
- K_ds is 2-4× more sensitive than classical metrics (CD, HEX, CV)
- 69% of pairs show discordant K vs CD changes (K captures information CD misses)
- Homeostatic setpoint at K* ≈ 0.050 μm⁻²: low-K tissues improve, high-K tissues decline

## When To Use
- Analyzing specular microscopy images of corneal endothelium
- Quantifying cell mosaic order before/after surgery
- Batch processing clinical datasets (hundreds to thousands of images)
- Computing the collective order biomarker K_ds for research or clinical studies

## Segmentation Engine
Cornealia uses CellADE (Cell Adaptive Detection Engine) for segmentation. CellADE is training-free and CPU-only. See cellade/OVERVIEW.md for details.

## API Summary
| Method | Purpose | See |
|--------|---------|-----|
| `cornealia(...)` | Constructor — set all parameters | cornealia/API.md#constructor |
| `collective_order(image_path)` | Analyze single image → full results dict | cornealia/collective_order.md |
| `collective_order_batch(folder, n_workers)` | Parallel batch processing → list of results | cornealia/batch_processing.md |
| `plot(results)` | Create plotter object for visualization | cornealia/plotters.md |

## Pipeline Steps (in CelLAB GUI)

### Single Image Pipeline (type: cornealia)
1. **Image Import** — select image, configure machine output setting, preview
2. **Cell Segmentation** — CellADE with FFT sigma estimation → segment
3. **Morphometric Analysis** — compute g(r), V(r), K via all 5 methods

### Batch Pipeline (type: cornealia_batch)
1. **Batch Setup** — select folder, set all parameters, validate
2. **Run Batch** — parallel workers → CSV results
3. **Results & Export** — table view, publication plots, export
