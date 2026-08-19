# CelLAB — Console Commands
Keywords: console, terminal, python, git, command, help, ls, cd, pwd, load, results, workspaces, namespace, variable

## Console Types
CelLAB has three console types, opened via the bottom panel:
- **Python (shared)** — access to project, results, and all imports
- **CellIntella** — AI chat assistant
- **Git** — version control commands

## Python Console — Shell Aliases

### help
Shows all available commands and examples.

### pwd
Prints current working directory (starts at project root).

### ls / ls <path>
Lists files and folders in current or specified directory. Shows 📁 for folders, 📄 for files.

### cd <path> / cd / cd ..
Change directory. `cd` alone returns to project root. `cd ..` goes up one level.

### workspaces
Lists all workspaces and their pipelines with IDs and types. Example output:
```
📁 Main Workspace (workspace_1)
   └─ Cornealia - 1 (cornealia-1) [cornealia]
   └─ Cornealia Batch - 2 (cornealia_batch-2) [cornealia_batch]
```

### results <workspace_id> <pipeline_id> <step_id>
Shows the results directory contents and sets `results_path` variable. Example:
```
results workspace_1 cornealia-1 morphometry
```

### load <workspace_id> <pipeline_id> <step_id>
Loads `full_results.pkl` (or `analysis_results.json`) into the `data` variable. Example:
```
load workspace_1 cornealia-1 morphometry
data['K_ds']      # access any result key
data.keys()       # see all available keys
```

### clear / cls / clc
Clears the console output.

## Available Variables (Shared Python Console)
| Variable | Type | Description |
|----------|------|-------------|
| `project` | CelLABProject | Current project object |
| `np` | module | NumPy |
| `pd` | module | Pandas |
| `plt` | module | Matplotlib pyplot |
| `os` | module | OS utilities |
| `json` | module | JSON utilities |
| `Path` | class | pathlib.Path |

## Useful project Methods
```python
project.list_workspaces()                              # all workspaces + pipelines
project.get_results_dir('ws_id', 'pipe_id', 'step')   # results path
project.root                                           # project root Path
project.name                                           # project name
```

## Git Console
The Git console runs standard git commands on the project repository:
- `status` — show modified files
- `diff` — show changes
- `commit -m "message"` — commit changes
- `log` — show commit history
- `checkout <file>` — restore a file
