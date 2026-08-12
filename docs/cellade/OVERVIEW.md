# CellADE — Overview
Keywords: cellade, segmentation, training-free, CPU, cell detection, centroids, watershed, blob detection, cornealia, corneal endothelium, specular microscopy

## What It Does
CellADE (Cell Adaptive Detection Engine) is a training-free, CPU-only cell segmentation algorithm. It detects cell centroids and boundaries in microscopy images without requiring GPU hardware, pre-trained models, or labeled training data. All parameters have direct physical interpretations (scale range, contrast, foreground threshold), making it transparent and adjustable by domain experts.

## Key Concepts

### Training-Free Design
Unlike deep learning methods (Cellpose, StarDist, CellSAM), CellADE uses classical image processing: CLAHE enhancement → blob detection → fuzzy C-means → watershed. No neural networks, no training data, no GPU required.

### Modes
CellADE has preset parameter configurations for different cell types:
- **cornealia**: Corneal endothelial cells from specular microscopy. Includes FFT-based adaptive scale estimation and strip-based ROI detection.
- **default**: General-purpose cell segmentation with conservative parameters.
- Custom modes can be created by passing a params dict.

### FFT Sigma Estimation
In cornealia mode, CellADE estimates the cell size automatically from the image's frequency content. The FFT power spectrum reveals the dominant spatial frequency, which maps to cell diameter. This removes the need to manually set the blob detection scale range.

### Pipeline Steps
1. **Preprocess** — grayscale → normalize → CLAHE contrast enhancement
2. **Detect seeds** — Laplacian-of-Gaussian blob detection (with optional FFT sigma)
3. **Extract foreground** — Fuzzy C-means clustering (global, local, or both)
4. **Initial segmentation** — marker-controlled watershed
5. **Merge by curvature** — fix over-segmentation (optional)
6. **Smooth morphological** — edge filing (optional)
7. **Smooth FFT** — frequency-domain boundary filter (optional)
8. **Merge honeycomb** — small fragment merging (optional)
9. **Gap filling** — close intercellular gaps (optional)

### Performance
- ~3 seconds per image on a single CPU core
- Comparable speed to Cellpose-SAM on GPU (~8 seconds)
- No GPU memory requirements
- No model download or initialization overhead

## When To Use
- Segmenting corneal endothelial cells from specular microscopy images
- Any scenario where GPU hardware is unavailable
- When transparency and parameter interpretability are required
- When the downstream task needs centroids rather than pixel-perfect masks
- As a preprocessing step for collective order (K) computation in Cornealia

## Benchmark Results (Daniel et al. dataset, 385 images)
| Method | n | Precision | Recall | F1 |
|--------|---|-----------|--------|----|
| CellADE | 324 | 0.471 | 0.579 | 0.504 |
| Cellpose-SAM | 385 | 0.546 | 0.395 | 0.421 |
| StarDist | 385 | 0.058 | 0.006 | 0.009 |

CellADE achieves higher F1 with lower variance and generalizes to clinical data where deep learning methods fail or require retraining. On 1,607 clinical images, CellADE detected a median of 379 cells/image vs Cellpose's 305.

## API Summary
| Method | Purpose | See |
|--------|---------|-----|
| `CellADE(mode, params)` | Constructor — set mode and override parameters | cellade/API.md#constructor |
| `run(image)` | Run full segmentation pipeline | cellade/API.md#run |
| `get_centroids()` | Return (N, 2) array of (y, x) centroids | cellade/API.md#get-centroids |
| `get_labels()` | Return labeled segmentation mask | cellade/API.md#get-labels |

## Integration with Cornealia
CellADE is the segmentation engine inside Cornealia. When you call `cornealia.collective_order(image_path)`, it internally creates a CellADE instance in cornealia mode and runs segmentation. The centroids are then used to compute g(r), V(r), and K.

```python
# Standalone usage
from shared_modules.cellade.cellade import CellADE
seg = CellADE(mode='cornealia', params={'use_fft_sigma': True})
seg.run(image)
centroids = seg.get_centroids()  # (N, 2) array of (y, x)

# Inside Cornealia (automatic)
from cornealia.cornealia import cornealia
c = cornealia(pixel_size=0.58)
results = c.collective_order("image.png")  # CellADE runs internally
```
