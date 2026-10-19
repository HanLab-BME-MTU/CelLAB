# Cel²LAB™ — Cellular Analysis Workbench

Cel²LAB™ (CelLAB) is an open-source desktop platform for quantitative cell biology image analysis. It follows the workbench paradigm of engineering software: specialized analysis pipelines share a common project system, an interactive GUI that runs in your web browser, and reusable computational engines. All computation runs locally on the CPU; no GPU or internet connection is needed.

## Modules

### Cornealia™ — collective order of corneal endothelium

Automated collective order analysis of corneal endothelial cell images from specular microscopy.

- **Collective order:** radial distribution function g(r), effective interaction potential V(r), and the spring constant **K_ds**, fitted to the full g(r) curve.
- **Effective intercellular forces** on a Delaunay truss: mean residual force, compression fraction, hot spot detection.
- **CellADE**, a training-free segmentation algorithm, with a signal-processing **quality gate** for automated reliability assessment.
- **Instruments:** CellChek D (Konan Medical) machine output, with automatic cropping and OCR of the device metrics, and standalone images from any specular microscope, including **non-square pixels** (`pixel_size=(sx, sy)`).
- Single-image and parallel batch processing, CLI and GUI workflows, publication-ready figures.

### Signal Associa — coupling and causality between time series

Convergent cross mapping, Granger causality, Pearson and Spearman correlation, mutual information and transfer entropy, with surrogate-based significance testing (IAAFT, AAFT, shuffle), automatic stationarization, pairwise and pre-paired batch modes, and per-run provenance.

### CellIntella (beta, experimental) — local AI assistant

A privacy-preserving assistant (Llama 3.2 3B via llama.cpp, running locally on CPU) that answers questions about the modules, their parameters and the platform. No data leaves your machine. Responses should be checked against the bundled documentation.

## Getting started

**Ready-to-run packages** (no installation; extract and run) for Windows, Linux and macOS (Apple Silicon), with and without CellIntella, are available on Zenodo: https://doi.org/10.5281/zenodo.22018616

**From source:**

```bash
# Linux / macOS
./setup.sh
# Windows (PowerShell)
./setup.ps1
```

Core dependencies are listed in `requirements_core.txt`; the full set, including CellIntella, in `requirements_full.txt`.

**Python API (Cornealia™):**

```python
from cornealia import cornealia

processor = cornealia(
    is_input_image_machine_output=True,   # CellChek D screenshot; False for a plain image
    pixel_size=0.58,                      # µm/px; use (sx, sy) for non-square pixels
)
results = processor.mechanical_state("image.jpg")
K_ds_um = results["K_ds"] / 0.58**2                # K_ds is returned in px^-2; divide by the pixel area for µm^-2
print(K_ds_um, results["reliable"])
```

## System requirements

- 4 GB RAM (8 GB recommended with CellIntella)
- Windows 10+ (64-bit), Ubuntu 20.04+ (64-bit), or macOS 13+ (Apple Silicon)

## Citation

If you use Cornealia™, please cite:

> Rostami, M. *et al.* Cornealia™: automated collective order analysis reveals density-dependent reorganization of donor corneal endothelium (submitted).

and the software release: https://doi.org/10.5281/zenodo.22018616

## License and trademarks

The source code is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0); see `LICENSE`. Commercial licenses are available on request. The CellIntella model weights remain subject to the Llama 3.2 Community License.

Cel²LAB™ and Cornealia™ are trademarks of [OWNER]. Use of the names does not imply endorsement.

## Contact

Han Lab, Department of Biomedical Engineering, Michigan Technological University — sjhan@mtu.edu
