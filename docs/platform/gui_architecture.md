# CelLAB — GUI Architecture
Keywords: gui, layout, panel, toolbar, menu, shortcut, button, workspace tab, graphics, config, navigation, task manager, keyboard

## Main Layout
CelLAB uses a three-panel layout:

### Left Panel — Configuration
Contains per-step parameters for the active pipeline. Each step has collapsible parameter groups with input fields, dropdowns, and sliders. Parameters are saved automatically when modified.

### Center Panel — Graphics
Displays images, plots, results tables, and overlays. Supports zoom (scroll wheel), pan (click-drag), brightness/contrast adjustment, and image export. Results from analysis steps appear here as interactive visualizations.

### Right Panel — Properties & Modules
Shows properties of the selected item and lists open modules/pipelines.

## Toolbar Buttons (left to right)
| Button | Action | Description |
|--------|--------|-------------|
| New | `newProject()` | Create a new project |
| Open | `openProject()` | Open existing project or .cellab file |
| Save | `saveProject()` | Save current project state |
| Zoom In | `zoomIn()` | Zoom into graphics panel |
| Zoom Out | `zoomOut()` | Zoom out of graphics panel |
| Fit | `fitToWindow()` | Fit image to window |
| Reset Layout | `resetLayout()` | Reset panel sizes to defaults |
| Task Manager | `openTaskManager()` | View running/completed analyses |
| Version Control | `toggleVersionPanel()` | Open Git panel (Ctrl+Shift+H) |
| CellIntella | `toggleCellIntellaPanel()` | Open AI assistant panel |
| Aristolia | `openAristolia()` | Open interactive learning module |

## Workspace Tabs
Workspace tabs appear below the toolbar. Each workspace is a tab containing its pipelines. Click `+` to create a new workspace. Right-click a tab to rename or delete.

## Pipeline Navigation
Within a workspace, pipelines appear as grouped tabs. Each pipeline has sequential steps (e.g., Image Import → Segmentation → Analysis). Click a step to load its config panel on the left and its results in the center.

### Step Controls
Each analysis step has:
- **▶ Run** — execute this step
- **⏹ Stop** — cancel running analysis
- **Reset** — restore default parameters
- **Browse** — select input files/folders

## Console Panel (Bottom)
Toggle with backtick (`) key. Three tab types:
- **+ Python** — shared Python console
- **+ CellIntella** — AI assistant
- **+ Git** — version control

## Task Manager
Monitors all running and completed analyses. Shows progress bars, elapsed time, and status. Access via toolbar button or status bar.

## Image Viewer Controls
- **Scroll wheel** — zoom in/out
- **Click + drag** — pan
- **⚡ Auto** — auto brightness/contrast
- **↺ Reset** — reset to original brightness
- Right-click results in graphics panel to insert specific plot types
