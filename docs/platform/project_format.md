# CelLAB — Project Format
Keywords: project, .cellab, workspace, pipeline, manifest, folder, structure, save, open, create, archive, format

## Project Structure
A CelLAB project is a folder containing:
```
My Project/
├── My Project.cellab          # manifest file (JSON)
├── .cellab/                   # internal metadata
├── data/                      # imported images and data files
├── exports/                   # exported results (CSV, plots)
└── workspaces/
    ├── workspace_1/
    │   ├── workspace.json     # workspace metadata
    │   ├── cornealia-1/
    │   │   ├── pipeline.json  # pipeline config and params
    │   │   ├── import/
    │   │   │   └── results/   # import step results
    │   │   ├── segmentation/
    │   │   │   └── results/   # segmentation results
    │   │   └── morphometry/
    │   │       └── results/
    │   │           ├── full_results.pkl    # complete results dict
    │   │           ├── analysis_results.json
    │   │           ├── run_log.json
    │   │           ├── run_report.md
    │   │           └── plots/             # generated plots
    │   └── cornealia_batch-2/
    │       ├── pipeline.json
    │       ├── batch_setup/
    │       │   └── results/
    │       └── batch_run/
    │           └── results/
    │               └── results.csv        # batch CSV output
    └── ws-2/
        └── ...
```

## Key Files

### .cellab manifest
JSON file at project root. Contains project name, version, creation date, and workspace/pipeline registry. This is what CelLAB opens when you load a project.

### pipeline.json
Stores all parameters for a pipeline instance. Updated when you change parameters in the GUI config panel. Contains step definitions, parameter values, and run history.

### full_results.pkl
Python pickle containing the complete results dictionary from an analysis step. Load in the console with: `load workspace_1 cornealia-1 morphometry`

### results.csv
Batch processing output. One row per image with all computed metrics. See cornealia/batch_processing.md for column reference.

### run_report.md
Human-readable summary of a completed analysis step — parameters used, timing, key results.

## Project Operations

### Create
Toolbar → New Project, or `project.create("path/to/folder")`. Creates the folder structure and manifest.

### Open
Toolbar → Open, select a folder or .cellab file. CelLAB reads the manifest and restores all workspaces and pipelines.

### Save
Toolbar → Save, or auto-saves on parameter changes. Writes manifest and all pipeline.json files.

### Archive
File → Archive creates a `.cellab.zip` containing the entire project for sharing or backup.

## Accessing Results Programmatically
```python
# In the Python console:
project.list_workspaces()
project.get_results_dir('workspace_1', 'cornealia-1', 'morphometry')
load workspace_1 cornealia-1 morphometry
data['K_ds']
```
