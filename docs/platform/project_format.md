# CelLAB — Project Format (.cellab)
Keywords: project, .cellab, manifest, workspace, pipeline, save, open, archive, directory structure

## Directory Structure
```
MyProject/                          ← project root (user-chosen folder)
├── .cellab/                        ← internal state (hidden)
│   ├── manifest.json               ← master project file
│   └── internal/
│       ├── gui_state.json          ← saved GUI layout, open tabs
│       └── history/
│           ├── log.json            ← commit history
│           ├── commits/
│           │   ├── e6182ba2.json   ← parameter snapshot
│           │   └── a3f91c04.json
│           └── tags/
│               └── v1_baseline.json
├── data/                           ← imported data files (copy mode)
├── workspaces/
│   ├── workspace_1/
│   │   ├── workspace.json          ← workspace metadata
│   │   ├── cornealia-1/
│   │   │   ├── pipeline.json       ← pipeline config + step status
│   │   │   ├── image_import/
│   │   │   │   └── params.json     ← step parameters
│   │   │   ├── cell_segmentation/
│   │   │   │   ├── params.json
│   │   │   │   └── results/
│   │   │   │       ├── full_results.pkl
│   │   │   │       └── plots/
│   │   │   │           ├── 01_segmentation_overview.png
│   │   │   │           └── 05_comprehensive.png
│   │   │   └── morphometry/
│   │   │       ├── params.json
│   │   │       └── results/
│   │   └── cornealia_batch-2/
│   │       ├── pipeline.json
│   │       ├── batch_setup/
│   │       │   └── params.json
│   │       ├── batch_run/
│   │       │   ├── params.json
│   │       │   └── results/
│   │       │       └── batch_results.csv
│   │       └── batch_results/
│   │           ├── params.json
│   │           └── results/
│   │               └── plots/
│   └── workspace_2/
│       └── ...
```

## manifest.json
```json
{
  "cellab_version": "3.1",
  "name": "MyProject",
  "author": "Majid R.",
  "description": "Corneal analysis study",
  "created": "2026-04-10T12:00:00",
  "modified": "2026-04-10T22:04:49",
  "workspaces": [
    {"id": "workspace_1", "name": "Main Workspace"}
  ],
  "active_packages": ["cornealia"],
  "data_references": []
}
```

## pipeline.json
```json
{
  "id": "cornealia-1",
  "type": "cornealia",
  "name": "Cornealia - 1",
  "created": "2026-04-10T12:05:00",
  "canvas_position": {"x": 100, "y": 50},
  "steps": {
    "image_import": {"status": "done", "last_run": "2026-04-10T12:06:00"},
    "cell_segmentation": {"status": "done", "last_run": "2026-04-10T12:07:00"},
    "morphometry": {"status": "idle"}
  }
}
```

## params.json (example: morphometry step)
```json
{
  "pixel_size": 0.58,
  "fitting_method": "morse",
  "exclusion_ratio": 0.15,
  "shell_thickness": 1,
  "fitting_half_width": 10,
  "SAVGOL_WINDOW": 11,
  "SAVGOL_ORDER": 3
}
```

## Step Status Detection
CelLAB detects step completion from the filesystem:
- If `results/full_results.pkl` exists → step is `done`
- If `results/plots/*.png` exist → plots are available
- If `results/batch_results.csv` exists → batch completed
- No separate status database — filesystem IS the state

## Version Control Storage
Commits snapshot all `params.json` files across all workspaces:
```json
{
  "hash": "e6182ba2...",
  "timestamp": "2026-04-10T22:04:49",
  "message": "Initial parameters",
  "author": "console",
  "params": {
    "workspace_1/cornealia-1/morphometry/params.json": {"pixel_size": 0.58, ...},
    "workspace_1/cornealia-1/cell_segmentation/params.json": {...}
  }
}
```

## Data Import Modes
| Mode | Behavior |
|------|----------|
| `copy` | Copies file into `data/` folder inside project |
| `external` | Stores absolute path reference (no copy) |
| `move` | Moves file into `data/` folder |

## Archive (.cellab.zip)
`project.archive()` creates a zip containing the entire project directory. Options:
- `include_results`: Include pkl/csv/plot files (default True)
- `include_input_data`: Include imported data files (default True)
- `include_gui_state`: Include GUI layout state (default True)
