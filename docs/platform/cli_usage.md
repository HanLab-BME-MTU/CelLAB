# CelLAB — CLI Usage
Keywords: cli, command line, terminal, script, headless, python, cornealia, batch, single, argument, flag

## Overview
CelLAB packages can be run from the command line without the GUI. No PYTHONPATH setup needed — paths auto-configure from the script location.

## Cornealia CLI

### Single Image Analysis
```bash
python backend/cornealia/cornealia.py single --image "path/to/image.png" --pixel-size 0.58 --output C:\results --plot
```

**Arguments:**
| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--image` | Yes | — | Path to specular microscopy image |
| `--pixel-size` | No | 0.58 | Pixel size in µm/px |
| `--output` | No | current dir | Output folder for JSON + plots |
| `--plot` | No | off | Generate diagnostic plots |
| `--no-machine` | No | off | Treat as raw image (no CellChek preprocessing) |
| `--invert` | No | off | Invert image for dark-on-light |

**Output:** JSON results file + optional plot folder.

### Batch Processing
```bash
python backend/cornealia/cornealia.py batch --folder "C:\cornea_images" --output C:\results --pixel-size 0.58 --workers 4
```

**Arguments:**
| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--folder` | Yes | — | Folder containing images |
| `--output` | No | current dir | Output folder for CSV + per-image results |
| `--pixel-size` | No | 0.58 | Pixel size in µm/px |
| `--workers` | No | 1 | Number of parallel CPU workers |
| `--no-machine` | No | off | Raw images without machine overlay |
| `--invert` | No | off | Invert images for dark-on-light |

**Output:** `results.csv` with one row per image, plus summary statistics printed to terminal.

### Example Workflow
```bash
# Single image with full diagnostics
python backend/cornealia/cornealia.py single --image "005-3502L AS.png" --pixel-size 0.58 --plot --output C:\Temp\test

# Batch folder with 8 workers
python backend/cornealia/cornealia.py batch --folder "C:\study_images" --output C:\Temp\batch --pixel-size 0.58 --workers 8

# Cultured cell images (phase-contrast, inverted)
python backend/cornealia/cornealia.py single --image "P0_culture.tiff" --pixel-size 0.34 --no-machine --invert --plot
```

## Running from Any Directory
The CLI auto-configures Python paths from the script's location. No need to set PYTHONPATH or activate a conda environment (beyond having dependencies installed).

## Scripting
For custom workflows, import directly:
```python
from cornealia.cornealia import cornealia
c = cornealia(pixel_size=0.58)
results = c.collective_order("image.png")
```
