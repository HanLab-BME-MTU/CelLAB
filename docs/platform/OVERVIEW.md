# CelLAB — Platform Overview
Keywords: cellab, platform, workbench, workspace, pipeline, package, feature, about, what is

## What Is CelLAB
CelLAB (Cellular Analysis Workbench) is an open-source desktop platform for quantitative cell biology image analysis. It follows the workbench paradigm: specialized analysis pipelines share a common project system, interactive GUI, and reusable computational engines. No programming experience required — all analysis runs through a graphical interface with structured workflows.

## Analysis Packages
| Package | Purpose | Image Types |
|---------|---------|-------------|
| **Cornealia** | Corneal endothelial morphometry and collective order | Specular microscopy, phase-contrast |
| **FASTIA** | Focal adhesion dynamics (detection, tracking, kinetics) | Timelapse fluorescence |
| **IMMUNIA** | Immune cell migration and tumor-cell interactions | Timelapse brightfield/fluorescence |
| **CellADE** | Training-free cell segmentation engine | Any cell images |
| **CellFADE** | Focal adhesion detection engine | Fluorescence |
| **AnnotADE** | Annotation and ground truth tools | Any |

## Core Concepts

### Projects
A CelLAB project is a folder with a `.cellab` manifest file. It contains workspaces, each with pipelines. Projects can be saved, opened, archived as .cellab.zip, and version-controlled with built-in Git.

### Workspaces
Workspaces group related analyses. Each workspace contains one or more pipelines. Create multiple workspaces to organize experiments (e.g., "Donor Study", "Culture Conditions").

### Pipelines
A pipeline is a sequence of analysis steps. Each package defines its own pipeline type (e.g., cornealia, cornealia_batch, fastia, immunia). Steps have parameters, run buttons, and results.

### Steps
Each pipeline step has: parameters (left config panel), a run button, and results displayed in the graphics panel. Steps execute sequentially — later steps may depend on earlier ones.

## Key Features
- Multi-workspace, multi-pipeline project system
- Docked configuration panels with per-step parameters
- Interactive image viewer with zoom, brightness, contrast
- Real-time visualization and result overlays
- Export to CSV, PNG, PDF with custom DPI
- Built-in Python console with project access
- Built-in Git version control
- CellIntella AI assistant (local Llama 3.2 3B, fully private)
- Task manager for monitoring long-running analyses
- No GPU required — all computation runs on CPU
