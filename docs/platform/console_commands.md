# CelLAB — Console & Terminal Commands
Keywords: console, terminal, Python, Git, REPL, commands, namespace, clear, commit, log

## Opening the Console
- **Ctrl+`** — toggle console panel
- **Tools → Python Console** — open shared Python tab
- **Tools → Git Terminal** — open Git tab
- **Ctrl+Shift+T** — new Python (shared) tab
- **Ctrl+Shift+G** — new Git tab

## Terminal Types

### 🔵 Python (Shared)
- Color: Blue tab header and prompt
- Prompt: `>>>`
- Namespace: Persistent across commands. Pre-loaded with `project`, `np`, `pd`, `plt`, `Path`, `os`, `json`
- Use: Explore data, run analysis, quick calculations
- Variables survive: `x = 5` then `print(x)` works

### 🟢 Python (Isolated)
- Color: Green tab header and prompt
- Prompt: `>>>`
- Namespace: Fresh per tab. Only `os`, `json`, `Path`, `print`, builtins.
- Use: Testing, experiments without polluting shared namespace
- Each new isolated tab starts empty

### 🟠 CelLAB Git
- Color: Orange tab header and prompt
- Prompt: `$`
- Not Python — interprets CelLAB version control commands
- Use: Parameter version control

## Python Console Commands

### Magic Commands
| Command | Action |
|---------|--------|
| `clear` / `clc` / `cls` | Clear console output |
| `exit` / `quit` | Shows hint to use Ctrl+` |

### Pre-loaded Variables (Shared)
| Name | Type | Description |
|------|------|-------------|
| `project` | CellabProject | Current open project |
| `np` | module | numpy (if already imported by analysis) |
| `pd` | module | pandas (if already imported) |
| `plt` | module | matplotlib.pyplot (if already imported) |
| `Path` | class | pathlib.Path |
| `os` | module | os |
| `json` | module | json |

### Common Python Tasks
```python
# Check project info
project.name
project.root

# Load batch results
import pandas as pd
df = pd.read_csv(str(project.root / 'workspaces/workspace_1/cornealia_batch-2/batch_run/results/batch_results.csv'))
df.head()
df['K_um'].describe()

# Run Cornealia analysis
from cornealia.cornealia import cornealia
c = cornealia(pixel_size=0.58)
results = c.collective_order(r"C:\path\to\image.jpg")
results['K']

# Quick plot
import matplotlib.pyplot as plt
plt.figure()
plt.hist(df['K_um'].dropna(), bins=20)
plt.savefig('test.png')
print('Saved!')
```

## CelLAB Git Commands

### status
```
$ status
Project: test 8
Root:    C:\test 8
Workspaces: 1
Pipelines:  3
    Cornealia - 2 (cornealia)
    Cornealia Batch - 4 (cornealia_batch)
    IMMUNIA - 3 (immunia)

Last commit: e6182ba2  2026-04-10T22:04:49
  "Initial parameters for corneal analysis"

⚠ Parameters modified since last commit
  Use: commit <message>
```

### commit
```
$ commit Changed pixel_size to 0.45
Committed: a3f91c04 — Changed pixel_size to 0.45
```

### log
```
$ log
  a3f91c04  2026-04-10T22:15:30  Changed pixel_size to 0.45
  e6182ba2  2026-04-10T22:04:49  Initial parameters for corneal analysis
$ log 5
```

### tag
```
$ tag v2_revised
Tagged: v2_revised
$ tag final_params a3f91c04
Tagged: final_params
```

### tags
```
$ tags
  v1_baseline  →  e6182ba2
  v2_revised   →  a3f91c04
```

### diff
```
$ diff e6182ba2 a3f91c04
{
  "workspace_1/cornealia-1/morphometry/params.json": {
    "pixel_size": [0.58, 0.45]
  }
}
```

### checkout
```
$ checkout e6182ba2
Checked out: e6182ba2
```
**Warning:** This overwrites current parameters with the snapshot.

### help
```
$ help
CelLAB Git Commands:
  status, commit, log, diff, tag, tags, checkout, help
```

## Console Window Controls
| Button | Action |
|--------|--------|
| 📋 | Copy all console output to clipboard |
| 🗑 | Clear console output |
| ⟳ | Reset namespace (clear all variables) |
| ≡ | Show all variables in namespace |
| ─ | Minimize (collapse to header bar) |
| □ / ❐ | Maximize (70vh) / Restore (30vh) |
| ✕ | Close console panel |
| + | New terminal tab (pick type) |

## Keyboard Shortcuts (in console)
| Key | Action |
|-----|--------|
| ↑ / ↓ | Navigate command history |
| Ctrl+L | Clear console |
| Enter | Execute command |
