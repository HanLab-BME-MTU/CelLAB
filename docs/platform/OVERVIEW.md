# CelLAB Platform — Overview
Keywords: platform, project, workspace, pipeline, GUI, Flask, API, version control, console, task manager

## What It Is
CelLAB (CELLular Analysis Workbench) is a unified platform for cell biology analysis, inspired by ANSYS Workbench, COMSOL Multiphysics, and VS Code. It provides a graphical interface over multiple analysis packages with parameter version control, a Python console, task management, and an AI assistant.

## Architecture
- **Backend:** Python Flask server (`app.py`, ~2200 lines)
- **Frontend:** HTML + CSS + JS (`workbench.html/css/js`, ~4500 lines total)
- **Communication:** REST API with JSON responses
- **Project format:** `.cellab` directory with manifest, workspaces, version history

## Key Features

### Project System
- `.cellab` format: manifest.json + workspaces/ + .cellab/internal/
- Create, open, save, save-as, close, archive (.zip)
- Portable across machines
- See: platform/project_format.md

### GUI Layout
- Title bar → Menu bar → Toolbar → Workspace tabs → Subtab bar → Main viewport
- Three-column module view: Tree | Settings | Graphics (flex 1:1:2)
- Collapsible panels, resizable
- See: platform/gui_architecture.md

### Version Control (CelLAB Git)
- Commit: snapshots all params.json files
- Log, diff, tag, checkout (revert parameters)
- GUI panel with timeline + commit box
- Terminal commands via Git console tab
- Parameters only — results are reproducible, not versioned

### Python Console
- Multi-tab: Shared (persistent namespace), Isolated (fresh), Git (commands)
- Pre-loaded: np, pd, plt, Path, project
- VS Code-style terminal panel, resizable

### Task Manager
- Tracks every run and plot task
- Live log streaming during execution
- Expandable rows with captured stdout
- Stop and Retry actions

### Keyboard Shortcuts
- Ctrl+S save, Ctrl+` console, F5 run, Ctrl+Shift+H history
- Full list via Ctrl+Shift+/ or Help menu

## API Endpoints (summary)
| Prefix | Purpose |
|--------|---------|
| /api/project/* | Create, open, save, close, archive |
| /api/workspace/* | Create, list, delete, rename |
| /api/pipeline/* | Create, delete, position, connect |
| /api/step/*/params | Save/load parameters |
| /api/step/*/run | Execute analysis step |
| /api/step/*/plot | Generate plot on demand |
| /api/step/*/export-plot | Export with custom DPI/format |
| /api/version/* | Commit, log, diff, tag, checkout, tags |
| /api/console/* | Create, exec, reset, namespace |
| /api/tasks/log | Live log for running tasks |
| /api/browse | File browser for frontend |
| /api/status | Server health + system stats |

## Running CelLAB
```bash
cd CelLAB
python app.py                        # start server
python app.py --open "C:\my_project" # open existing project
```
Then open http://127.0.0.1:5000 in Chrome/Edge.
