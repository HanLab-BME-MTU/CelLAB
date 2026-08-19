# Cornealia — Overview
Keywords: corneal, endothelium, specular microscopy, morphometry, collective order, g(r), V(r), K, K_ds, cell density, hexagonality, batch, CellADE, force, delaunay, truss, mean_F, residual, homeostatic, setpoint, attractor, K_star, interior, exclusion, border, machine, cellchek, preprocessing, green dot, OCR, pixel_size, calibration, culture, passage, phase contrast, noise, damped sine

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

### The Noise Problem and Why DS Works
V(r) = -ln(g(r)) amplifies small fluctuations in g(r) into large distortions in the potential landscape. This means biologically similar tissues can yield different K estimates from noise alone. The DS method avoids this by fitting g(r) directly with a damped sine, then deriving K analytically from the fitted parameters — never passing through the noisy -ln transform.

### Residual Force Field and mean|F|
Keywords: force, delaunay, truss, mechanical, stress, mean_F, residual, disequilibrium
Cornealia models the monolayer as a Delaunay truss connecting neighboring cell centroids. Each edge carries a residual force F = -V'(d) where d is the edge length and V(r) is the interaction potential. The per-cell force magnitude |F_i| is the vector sum of all edge forces at that node. The tissue-level summary mean|F| predicts the direction and magnitude of collective order change (ρ = -0.471) and co-evolves with K_ds (ρ = 0.896).

### Homeostatic Setpoint K*
Keywords: setpoint, homeostatic, attractor, convergence, equilibrium, K_star
Analysis of 776 paired donor images reveals that K_ds converges toward a homeostatic setpoint K* ≈ 0.050 μm⁻². Tissues with low initial K increase their order after stripping; tissues with high initial K decrease. Data-derived potential wells U(K) confirm the setpoint as a true attractor with parabolic (harmonic) restoring dynamics. No functional form is assumed — the attractor emerges entirely from the data.

### Interior Cells and Exclusion Zone
Keywords: interior, border, exclusion, edge effect, exclusion_ratio
Only interior cells contribute to g(r) computation. Border cells within exclusion_ratio × min(H,W) of the image edge are excluded because their neighbor shells are truncated by the field of view. Default exclusion_ratio = 0.15 (15%). The min_interior_cells_ratio parameter (default 0.4) ensures enough interior cells remain for a meaningful g(r).

### Machine Preprocessing (CellChek D)
Keywords: machine, cellchek, preprocessing, green dot, OCR, inpainting, crop
When is_input_image_machine_output=True, Cornealia crops the CellChek D output into a cell area and a metrics area using predefined pixel coordinates. Green dots (machine-placed cell markers) are detected via HSV masking, their centroids recorded, and the dots removed by inpainting. Machine-reported metrics (CD, CV, HEX, SD, Ave, Num) are extracted from the metrics panel via OCR (EasyOCR).

### Pixel Size and Scaling
Keywords: pixel_size, pixel, calibration, scale, micrometer, µm/px
pixel_size (µm/px) converts pixel measurements to physical units. Default 0.58 µm/px matches clinical specular microscopy (CellChek D). All K values are reported in both px⁻² and µm⁻² (K_um = K_px / pixel_size²). Quality gate spatial thresholds (ξ, λ bounds) scale automatically with pixel_size_ref/pixel_size so the physical gates remain constant across magnifications.

### Cultured Cells and Passage Tracking
Keywords: culture, passage, phase contrast, in vitro, P0, P1, P2, P4, exponential decay
Cornealia extends from specular microscopy to phase-contrast images of cultured corneal endothelial cells. K_ds decays exponentially with serial passage (K_ds = 0.057·exp(-0.46P), R²=0.9965), providing a quantitative readout of culture quality. K_ds distinguishes growth factor conditions (EGF vs EGF+Dual Inhibitor, p=0.001) where cell density and hexagonality show no difference.

### AS/BS Groups
For longitudinal studies: AS = After Stripping (surgery), BS = Before Stripping. Image names containing "AS" or "BS" are grouped for paired statistical comparisons.

### Clinical Findings (776 pairs, Singapore Eye Centre)
K_ds increased +10.3% after stripping (p=0.047) despite cell density decrease. K_ds is 2-4× more sensitive than CD/HEX/CV. 69% of pairs show discordant K vs CD changes. Independently replicated on 227 pairs from Lions VisionGift (different device, continent).

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
