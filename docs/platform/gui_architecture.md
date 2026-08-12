# CelLAB — GUI Architecture
Keywords: GUI, layout, toolbar, menu, panel, workspace, subtab, module, three-column, viewport

## Layout Hierarchy
```
┌─ Title Bar ──────────────────────────────────────────────────┐
│ C CELLAB — Cellular Analysis Workbench                  v3.1 │
├─ Menu Bar ───────────────────────────────────────────────────┤
│ File  View  Tools  Extensions  Help                          │
├─ Toolbar ────────────────────────────────────────────────────┤
│ [📄📂💾] [🔍🔎🖼↺] [📋 Task Manager] [⏱CelLAB Git] [⚙] [🤖]│
├─ Workspace Tab Bar ──────────────────────────────────────────┤
│ [◈ Main Workspace ×] [◈ Workspace 2 ×] [+]                  │
├─ Subtab Bar ─────────────────────────────────────────────────┤
│ [◈ Schematic] │ [CRNB-4 ▼] [1.Setup] [2.Run] [3.Results]   │
├─ Main Container ─────────────────────────────────────────────┤
│ ┌─Left─┐┌────────Center Viewport────────┐┌──Right──┐        │
│ │Toolbox││                               ││HAN LAB  │        │
│ │      ││  (Schematic / Module View /   ││Properties│        │
│ │FASTIA ││   Task Manager)               ││         │        │
│ │IMMUNIA││                               ││Open     │        │
│ │Cornea ││                               ││Modules  │        │
│ └──────┘└───────────────────────────────┘└─────────┘        │
├─ Console Panel (toggleable) ─────────────────────────────────┤
│ [🐍 Python 1] [📦 Git] [+]              📋 🗑 ⟳ ≡ │ ─ □ ✕ │
│ >>> results['K']                                             │
│ 0.005                                                        │
├─ Status Bar ─────────────────────────────────────────────────┤
│ ● Ready — CELLAB v3.1    Main Workspace │ v3.1 │ Han Lab    │
└──────────────────────────────────────────────────────────────┘
```

## View Modes

### Schematic View (default)
- Pipeline nodes on a canvas with drag-and-drop
- Snap grid, zoom (Ctrl+wheel), pan
- Double-click pipeline box to open its steps as subtabs
- Green ✓ on completed steps

### Module View (three-column)
- **Tree** (25%): Step items, Results tree with Insert Result context menu
- **Settings** (25%): Parameter forms, auto-saved with 800ms debounce
- **Graphics** (50%): Plot images, batch result tables
- Collapsible left panels via ◀ toggle

### Task Manager View
- Activated via toolbar button `[📋 Task Manager]`
- Full-width table, hides left and right panels
- Click button again or any subtab to exit

## Tab System

### Level 1: Workspace Tabs
- Each workspace is an independent analysis environment
- Has its own pipelines, canvas positions, open modules
- Create with [+], close with ×, rename with double-click

### Level 2: Subtabs (grouped)
- Schematic tab: always present, not closeable
- Module tabs: grouped by pipeline (Chrome tab groups style)
- Group header: colored by pipeline type, collapsible ▼
- Each step opens as a separate subtab within its pipeline group

## Toolbar Elements (injected via JS)
These are added dynamically on DOMContentLoaded, no HTML changes needed:
- **CelLAB Git button**: `[⏱ CelLAB Git]` — dark gradient, orange dirty dot
- **System gauges**: Dual-needle speedometers for CPU and RAM
- **Task Manager button**: `[📋 Task Manager]` — highlights when active

## Dropdown Menus
| Menu | Items |
|------|-------|
| File | New, Open, Save, Save As, Close |
| View | Toggle Toolbox, Properties, Console, CelLAB Git, Reset Layout |
| Tools | Python Console (Shared/Isolated), Git Terminal, Task Manager, Package Manager |
| Extensions | Placeholder for future plugins |
| Help | Keyboard Shortcuts, About CelLAB |

## Right-Click Context Menus
- **Results header**: Insert Result → submenu of available plots
- **Result item**: Locate File, Save As (format/DPI), Remove
- **Console +**: Python Shared, Python Isolated, CelLAB Git
