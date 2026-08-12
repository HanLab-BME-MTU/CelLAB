"""
CelLAB Project Manager
======================
Handles .cellab project creation, saving, loading, and path management.

Architecture:
    - User picks a root folder FIRST before any analysis
    - All paths stored relative to root (portable)
    - .cellab manifest at root is the single entry point
    - GUI state separate from data/analysis state

Project Structure:
    📁 [ROOT]/
    ├── ProjectName.cellab          ← manifest (JSON)
    ├── 📁 .cellab/                 ← internal state
    │   ├── gui_state.json
    │   ├── preferences.json
    │   ├── 📁 CellIntella/
    │   │   ├── conversations.db
    │   │   └── 📁 rag_index/
    │   ├── 📁 history/             ← git-like versioning
    │   │   ├── HEAD
    │   │   ├── 📁 commits/
    │   │   └── 📁 tags/
    │   └── 📁 cache/
    ├── 📁 data/                    ← input data
    │   └── _external_refs.json
    ├── 📁 workspaces/
    │   └── 📁 workspace_1/
    │       ├── workspace.json
    │       └── 📁 FASTIA-1/
    │           ├── pipeline.json
    │           └── 📁 detection/
    │               ├── params.json
    │               └── 📁 results/
    └── 📁 exports/
"""

import json
import os
import shutil
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any, Union


# ═════════════════════════════════════════════════
# CONSTANTS
# ═════════════════════════════════════════════════

CELLAB_VERSION = "3.1.0"
MANIFEST_EXTENSION = ".cellab"
INTERNAL_DIR = ".cellab"
DATA_DIR = "data"
WORKSPACES_DIR = "workspaces"
EXPORTS_DIR = "exports"

EXTERNAL_REFS_FILE = "_external_refs.json"
GUI_STATE_FILE = "gui_state.json"
PREFERENCES_FILE = "preferences.json"
WORKSPACE_FILE = "workspace.json"
PIPELINE_FILE = "pipeline.json"
PARAMS_FILE = "params.json"

# Data import modes
DATA_COPY = "copy"           # Copy into data/ folder (default, portable)
DATA_LINK = "external"       # Keep external, store absolute path
DATA_MOVE = "move"           # Move into data/ folder


# ═════════════════════════════════════════════════
# PROJECT CLASS
# ═════════════════════════════════════════════════

class CellabProject:
    """
    Represents a CelLAB project rooted at a user-chosen directory.

    All paths within the project are stored relative to root.
    The .cellab manifest file is the entry point for opening a project.
    """

    def __init__(self, root: Union[str, Path]):
        self.root = Path(root).resolve()
        self._manifest = {}
        self._gui_state = {}
        self._preferences = {}
        self._external_refs = {}

    # ─── Properties ───────────────────────────────

    @property
    def name(self) -> str:
        return self._manifest.get("name", self.root.name)

    @property
    def manifest_path(self) -> Path:
        return self.root / f"{self.name}{MANIFEST_EXTENSION}"

    @property
    def internal_dir(self) -> Path:
        return self.root / INTERNAL_DIR

    @property
    def data_dir(self) -> Path:
        return self.root / DATA_DIR

    @property
    def workspaces_dir(self) -> Path:
        return self.root / WORKSPACES_DIR

    @property
    def exports_dir(self) -> Path:
        return self.root / EXPORTS_DIR

    @property
    def history_dir(self) -> Path:
        return self.internal_dir / "history"

    @property
    def CellIntella_dir(self) -> Path:
        return self.internal_dir / "CellIntella"

    # ─── Relative Path Helpers ────────────────────

    def to_relative(self, absolute_path: Union[str, Path]) -> str:
        """Convert an absolute path to a project-relative path string."""
        abs_path = Path(absolute_path).resolve()
        try:
            return str(abs_path.relative_to(self.root))
        except ValueError:
            # Path is outside project root — cannot be made relative
            raise ValueError(
                f"Path '{abs_path}' is outside project root '{self.root}'. "
                f"Use import_data() with mode='copy' to bring it inside."
            )

    def to_absolute(self, relative_path: str) -> Path:
        """Convert a project-relative path to an absolute Path."""
        return (self.root / relative_path).resolve()

    def path_exists(self, relative_path: str) -> bool:
        """Check if a project-relative path exists on disk."""
        return self.to_absolute(relative_path).exists()

    # ═════════════════════════════════════════════
    # PROJECT CREATION
    # ═════════════════════════════════════════════

    @classmethod
    def create(cls, root: Union[str, Path], name: str,
               author: str = "", description: str = "") -> 'CellabProject':
        """
        Create a new CelLAB project.

        This is the FIRST action — user picks a root folder and project name
        before any analysis can happen.

        Args:
            root: Directory where the project will live
            name: Project name (used for .cellab manifest filename)
            author: Author name (optional)
            description: Project description (optional)

        Returns:
            CellabProject instance ready for use
        """
        root = Path(root).resolve()

        # Validate
        if not root.exists():
            root.mkdir(parents=True, exist_ok=True)

        project = cls(root)

        # Create directory structure
        project.internal_dir.mkdir(exist_ok=True)
        project.data_dir.mkdir(exist_ok=True)
        project.workspaces_dir.mkdir(exist_ok=True)
        project.exports_dir.mkdir(exist_ok=True)
        (project.internal_dir / "cache").mkdir(exist_ok=True)
        project.history_dir.mkdir(exist_ok=True)
        (project.history_dir / "commits").mkdir(exist_ok=True)
        (project.history_dir / "tags").mkdir(exist_ok=True)
        project.CellIntella_dir.mkdir(exist_ok=True)

        # Create manifest
        project._manifest = {
            "cellab_version": CELLAB_VERSION,
            "name": name,
            "author": author,
            "description": description,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "project_id": str(uuid.uuid4()),
            "workspaces": [],
            "active_packages": ["fastia", "immunia", "cornealia"],
            "data_references": [],
        }

        # Initialize GUI state
        project._gui_state = {
            "active_workspace": None,
            "window_size": [1400, 900],
            "left_panel_width": 240,
            "right_panel_width": 200,
            "workspace_states": {},
        }

        # Initialize preferences
        project._preferences = {
            "theme": "light",
            "auto_save_interval": 0,  # 0 = manual only
            "CellIntella_model": "llama-3.1-8b-instruct",
            "CellIntella_enabled": True,
            "default_data_import_mode": DATA_COPY,
        }

        # Initialize external refs
        project._external_refs = {}

        # Write everything to disk
        project.save()

        # Create default workspace
        project.create_workspace("Main Workspace")

        return project

    # ═════════════════════════════════════════════
    # PROJECT LOADING
    # ═════════════════════════════════════════════

    @classmethod
    def open(cls, path: Union[str, Path]) -> 'CellabProject':
        """
        Open an existing CelLAB project.

        Args:
            path: Path to a .cellab file OR a folder containing one

        Returns:
            CellabProject with full state loaded

        Raises:
            FileNotFoundError: if no .cellab manifest found
            ValueError: if manifest is invalid
        """
        path = Path(path).resolve()

        # If given a directory, find the .cellab file inside it
        if path.is_dir():
            cellab_files = [
                f for f in path.glob(f"*{MANIFEST_EXTENSION}")
                if f.is_file()
            ]
            if not cellab_files:
                raise FileNotFoundError(
                    f"No {MANIFEST_EXTENSION} file found in '{path}'"
                )
            manifest_path = cellab_files[0]
            root = path
        elif path.suffix == MANIFEST_EXTENSION:
            manifest_path = path
            root = path.parent
        else:
            raise ValueError(f"Expected a {MANIFEST_EXTENSION} file or directory")

        project = cls(root)

        # Load manifest
        with open(manifest_path, 'r', encoding='utf-8') as f:
            project._manifest = json.load(f)

        # Validate
        if "cellab_version" not in project._manifest:
            raise ValueError("Invalid .cellab manifest — missing cellab_version")

        # Load GUI state
        gui_path = project.internal_dir / GUI_STATE_FILE
        if gui_path.exists():
            with open(gui_path, 'r', encoding='utf-8') as f:
                project._gui_state = json.load(f)

        # Load preferences
        prefs_path = project.internal_dir / PREFERENCES_FILE
        if prefs_path.exists():
            with open(prefs_path, 'r', encoding='utf-8') as f:
                project._preferences = json.load(f)

        # Load external refs
        refs_path = project.data_dir / EXTERNAL_REFS_FILE
        if refs_path.exists():
            with open(refs_path, 'r', encoding='utf-8') as f:
                project._external_refs = json.load(f)

        # Verify data references
        project._verify_data_references()

        # Update modified time
        project._manifest["modified"] = datetime.now().isoformat()

        return project

    # ═════════════════════════════════════════════
    # SAVING
    # ═════════════════════════════════════════════

    def save(self):
        """Save all project state to disk (metadata only, lightweight)."""
        self._manifest["modified"] = datetime.now().isoformat()

        # Manifest
        manifest_path = self.root / f"{self.name}{MANIFEST_EXTENSION}"
        self._write_json(manifest_path, self._manifest)

        # GUI state
        self._write_json(self.internal_dir / GUI_STATE_FILE, self._gui_state)

        # Preferences
        self._write_json(self.internal_dir / PREFERENCES_FILE, self._preferences)

        # External refs
        if self._external_refs:
            self._write_json(
                self.data_dir / EXTERNAL_REFS_FILE, self._external_refs
            )

    def save_as(self, new_root: Union[str, Path], new_name: Optional[str] = None):
        """
        Save project to a new location (full copy).

        Args:
            new_root: New directory for the project
            new_name: Optional new project name
        """
        new_root = Path(new_root).resolve()

        if new_root == self.root:
            self.save()
            return

        # Copy entire tree
        shutil.copytree(self.root, new_root, dirs_exist_ok=True)

        # Update references
        if new_name:
            # Rename manifest file
            old_manifest = new_root / f"{self.name}{MANIFEST_EXTENSION}"
            new_manifest = new_root / f"{new_name}{MANIFEST_EXTENSION}"
            if old_manifest.exists():
                old_manifest.rename(new_manifest)
            self._manifest["name"] = new_name

        self.root = new_root
        self._manifest["project_id"] = str(uuid.uuid4())  # New ID for copy
        self.save()

    def archive(self, output_path: Union[str, Path],
                include_results: bool = True,
                include_input_data: bool = True,
                include_gui_state: bool = True):
        """
        Create a .cellab.zip archive of the project.

        Args:
            output_path: Where to save the zip file
            include_results: Include analysis results (CSVs, masks, plots)
            include_input_data: Include the data/ folder
            include_gui_state: Include .cellab/ internal state
        """
        import zipfile

        output_path = Path(output_path)
        if not output_path.suffix:
            output_path = output_path.with_suffix('.cellab.zip')

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.root.rglob('*'):
                if not file_path.is_file():
                    continue

                rel = file_path.relative_to(self.root)
                rel_str = str(rel)

                # Skip cache always
                if "cache" in rel.parts:
                    continue

                # Conditional includes
                if not include_input_data and rel_str.startswith(DATA_DIR + os.sep):
                    continue
                if not include_gui_state and rel_str.startswith(INTERNAL_DIR + os.sep):
                    # But always include the manifest-relevant bits
                    if GUI_STATE_FILE not in rel_str and PREFERENCES_FILE not in rel_str:
                        continue
                if not include_results and "results" in rel.parts:
                    continue

                zf.write(file_path, rel)

        return output_path

    # ═════════════════════════════════════════════
    # DATA MANAGEMENT
    # ═════════════════════════════════════════════

    def import_data(self, source_path: Union[str, Path],
                    mode: str = DATA_COPY,
                    subfolder: str = "") -> str:
        """
        Import a data file into the project.

        Args:
            source_path: Absolute path to the source file
            mode: DATA_COPY (copy into data/), DATA_LINK (external ref),
                  DATA_MOVE (move into data/)
            subfolder: Optional subfolder within data/

        Returns:
            Project-relative path to the data file
        """
        source = Path(source_path).resolve()

        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        if mode == DATA_COPY or mode == DATA_MOVE:
            # Determine destination
            dest_dir = self.data_dir
            if subfolder:
                dest_dir = dest_dir / subfolder
                dest_dir.mkdir(parents=True, exist_ok=True)

            dest = dest_dir / source.name

            # Handle name collision
            if dest.exists():
                stem = source.stem
                suffix = source.suffix
                counter = 1
                while dest.exists():
                    dest = dest_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

            if mode == DATA_COPY:
                shutil.copy2(source, dest)
            else:  # DATA_MOVE
                shutil.move(str(source), str(dest))

            rel_path = str(dest.relative_to(self.root))

        elif mode == DATA_LINK:
            # Store external reference
            rel_path = f"data/{source.name}"  # Virtual relative path
            self._external_refs[rel_path] = str(source)
            self._write_json(
                self.data_dir / EXTERNAL_REFS_FILE, self._external_refs
            )

        else:
            raise ValueError(f"Unknown import mode: {mode}")

        # Track in manifest
        ref_entry = {
            "relative_path": rel_path,
            "original_path": str(source),
            "mode": mode,
            "imported": datetime.now().isoformat(),
            "size_bytes": source.stat().st_size if source.exists() else 0,
        }

        if "data_references" not in self._manifest:
            self._manifest["data_references"] = []
        self._manifest["data_references"].append(ref_entry)

        return rel_path

    def resolve_data_path(self, relative_path: str) -> Optional[Path]:
        """
        Resolve a data reference to an absolute path.
        Handles both local (copied) and external (linked) files.

        Returns:
            Absolute Path if found, None if missing
        """
        # Check local first
        local = self.to_absolute(relative_path)
        if local.exists():
            return local

        # Check external refs
        if relative_path in self._external_refs:
            ext = Path(self._external_refs[relative_path])
            if ext.exists():
                return ext

        return None

    def _verify_data_references(self) -> List[Dict[str, str]]:
        """
        Verify all data references exist. Returns list of missing ones.
        """
        missing = []
        for ref in self._manifest.get("data_references", []):
            resolved = self.resolve_data_path(ref["relative_path"])
            if resolved is None:
                missing.append({
                    "relative_path": ref["relative_path"],
                    "original_path": ref.get("original_path", ""),
                    "mode": ref.get("mode", "unknown"),
                })

        if missing:
            print(f"WARNING: {len(missing)} data file(s) not found:")
            for m in missing:
                print(f"  - {m['relative_path']} (was: {m['original_path']})")

        return missing

    # ═════════════════════════════════════════════
    # WORKSPACE MANAGEMENT
    # ═════════════════════════════════════════════

    def create_workspace(self, name: str, ws_id: str = "") -> str:
        """
        Create a new workspace within the project.

        Returns:
            Workspace ID (folder name)
        """
        if not ws_id:
            ws_id = f"workspace_{len(self.list_workspaces()) + 1}"
        ws_dir = self.workspaces_dir / ws_id
        ws_dir.mkdir(parents=True, exist_ok=True)

        ws_meta = {
            "id": ws_id,
            "name": name,
            "created": datetime.now().isoformat(),
            "pipelines": [],
        }
        self._write_json(ws_dir / WORKSPACE_FILE, ws_meta)

        # Track in manifest
        self._manifest["workspaces"].append({
            "id": ws_id,
            "name": name,
        })

        # Set as active if first workspace
        if self._gui_state.get("active_workspace") is None:
            self._gui_state["active_workspace"] = ws_id

        self.save()
        return ws_id

    def list_workspaces(self) -> List[Dict[str, Any]]:
        """List all workspaces in the project."""
        workspaces = []
        if self.workspaces_dir.exists():
            for ws_dir in sorted(self.workspaces_dir.iterdir()):
                ws_file = ws_dir / WORKSPACE_FILE
                if ws_file.exists():
                    with open(ws_file, 'r', encoding='utf-8') as f:
                        workspaces.append(json.load(f))
        return workspaces

    def delete_workspace(self, ws_id: str):
        """Delete a workspace and all its contents."""
        ws_dir = self.workspaces_dir / ws_id
        if ws_dir.exists():
            shutil.rmtree(ws_dir)
        self._manifest["workspaces"] = [
            w for w in self._manifest["workspaces"] if w["id"] != ws_id
        ]
        self.save()

    # ═════════════════════════════════════════════
    # PIPELINE MANAGEMENT
    # ═════════════════════════════════════════════

    def create_pipeline(self, ws_id: str, pipeline_type: str,
                        name: str = "", pipeline_id: str = "") -> str:
        """
        Create a new pipeline instance within a workspace.

        Args:
            ws_id: Workspace ID
            pipeline_type: e.g., 'fastia', 'immunia', 'cornealia'
            name: Display name (auto-generated if empty)
            pipeline_id: Explicit ID (if empty, auto-generated)

        Returns:
            Pipeline ID (folder name)
        """
        ws_dir = self.workspaces_dir / ws_id
        if not ws_dir.exists():
            # Create workspace dir if it doesn't exist yet
            ws_dir.mkdir(parents=True, exist_ok=True)
            ws_meta = {"id": ws_id, "name": ws_id, "created": datetime.now().isoformat(), "pipelines": []}
            self._write_json(ws_dir / WORKSPACE_FILE, ws_meta)

        if not pipeline_id:
            # Auto-generate
            existing = [d.name for d in ws_dir.iterdir() if d.is_dir()]
            counter = sum(1 for d in existing if d.lower().startswith(pipeline_type.lower())) + 1
            pipeline_id = f"{pipeline_type}-{counter}"

        if not name:
            name = f"{pipeline_type.upper()} - {pipeline_id.split('-')[-1]}"

        pipeline_dir = ws_dir / pipeline_id
        pipeline_dir.mkdir(parents=True, exist_ok=True)

        # Create pipeline metadata
        pipeline_meta = {
            "id": pipeline_id,
            "type": pipeline_type,
            "name": name,
            "created": datetime.now().isoformat(),
            "steps": {},
            "canvas_position": {"x": 0, "y": 0},
            "connections_in": [],   # inputs from other pipelines
            "connections_out": [],  # outputs to other pipelines
        }

        self._write_json(pipeline_dir / PIPELINE_FILE, pipeline_meta)

        # Update workspace metadata
        ws_meta = self._read_json(ws_dir / WORKSPACE_FILE)
        ws_meta["pipelines"].append({
            "id": pipeline_id,
            "type": pipeline_type,
            "name": name,
        })
        self._write_json(ws_dir / WORKSPACE_FILE, ws_meta)

        return pipeline_id

    def get_pipeline(self, ws_id: str, pipeline_id: str) -> Dict[str, Any]:
        """Read pipeline metadata."""
        path = self.workspaces_dir / ws_id / pipeline_id / PIPELINE_FILE
        return self._read_json(path)

    def delete_pipeline(self, ws_id: str, pipeline_id: str):
        """Delete a pipeline and all its data."""
        pipeline_dir = self.workspaces_dir / ws_id / pipeline_id
        if pipeline_dir.exists():
            shutil.rmtree(pipeline_dir)

        # Update workspace metadata
        ws_file = self.workspaces_dir / ws_id / WORKSPACE_FILE
        ws_meta = self._read_json(ws_file)
        ws_meta["pipelines"] = [
            p for p in ws_meta["pipelines"] if p["id"] != pipeline_id
        ]
        self._write_json(ws_file, ws_meta)

    # ═════════════════════════════════════════════
    # STEP / PARAMS MANAGEMENT
    # ═════════════════════════════════════════════

    def get_step_dir(self, ws_id: str, pipeline_id: str, step_id: str) -> Path:
        """Get or create the directory for a pipeline step."""
        step_dir = self.workspaces_dir / ws_id / pipeline_id / step_id
        step_dir.mkdir(parents=True, exist_ok=True)
        (step_dir / "results").mkdir(exist_ok=True)
        return step_dir

    def save_params(self, ws_id: str, pipeline_id: str, step_id: str,
                    params: Dict[str, Any]):
        """Save parameters for a pipeline step."""
        step_dir = self.get_step_dir(ws_id, pipeline_id, step_id)
        self._write_json(step_dir / PARAMS_FILE, {
            "step_id": step_id,
            "saved": datetime.now().isoformat(),
            "params": params,
        })

        # Update pipeline metadata
        pipeline_path = self.workspaces_dir / ws_id / pipeline_id / PIPELINE_FILE
        pipeline_meta = self._read_json(pipeline_path)
        pipeline_meta["steps"][step_id] = {
            "status": "configured",
            "last_params_save": datetime.now().isoformat(),
        }
        self._write_json(pipeline_path, pipeline_meta)

    def load_params(self, ws_id: str, pipeline_id: str,
                    step_id: str) -> Dict[str, Any]:
        """Load parameters for a pipeline step."""
        step_dir = self.workspaces_dir / ws_id / pipeline_id / step_id
        params_file = step_dir / PARAMS_FILE
        if params_file.exists():
            data = self._read_json(params_file)
            return data.get("params", {})
        return {}

    def get_results_dir(self, ws_id: str, pipeline_id: str,
                        step_id: str) -> Path:
        """Get the results directory for a step (creates if needed)."""
        results_dir = self.get_step_dir(ws_id, pipeline_id, step_id) / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        return results_dir

    # ═════════════════════════════════════════════
    # GUI STATE
    # ═════════════════════════════════════════════

    def save_gui_state(self, gui_state: Dict[str, Any]):
        """Save the current GUI state (tabs, positions, etc.)."""
        self._gui_state = gui_state
        self._write_json(self.internal_dir / GUI_STATE_FILE, self._gui_state)

    def load_gui_state(self) -> Dict[str, Any]:
        """Load the saved GUI state."""
        return self._gui_state.copy()

    # ═════════════════════════════════════════════
    # VERSION / COMMIT SYSTEM
    # ═════════════════════════════════════════════

    def commit(self, message: str, author: str = "") -> str:
        """
        Create a versioning commit — snapshot of all parameters and pipeline
        configurations. Lightweight (only JSON, not result data).

        Args:
            message: Commit message describing what changed
            author: Who made this commit

        Returns:
            Commit hash (short UUID)
        """
        # Collect all params across all workspaces/pipelines/steps
        snapshot = {
            "workspaces": {},
        }

        for ws in self.list_workspaces():
            ws_id = ws["id"]
            ws_dir = self.workspaces_dir / ws_id
            ws_snapshot = {"name": ws["name"], "pipelines": {}}

            for pipeline_entry in ws.get("pipelines", []):
                pid = pipeline_entry["id"]
                pipeline_dir = ws_dir / pid
                pipeline_file = pipeline_dir / PIPELINE_FILE

                if pipeline_file.exists():
                    pipeline_meta = self._read_json(pipeline_file)
                    pipeline_snapshot = {
                        "type": pipeline_meta.get("type"),
                        "name": pipeline_meta.get("name"),
                        "steps": {},
                    }

                    # Collect params from each step
                    for step_dir in pipeline_dir.iterdir():
                        if step_dir.is_dir():
                            params_file = step_dir / PARAMS_FILE
                            if params_file.exists():
                                pipeline_snapshot["steps"][step_dir.name] = \
                                    self._read_json(params_file)

                    ws_snapshot["pipelines"][pid] = pipeline_snapshot

            snapshot["workspaces"][ws_id] = ws_snapshot

        # Generate commit hash
        content_str = json.dumps(snapshot, sort_keys=True)
        commit_hash = hashlib.sha1(content_str.encode()).hexdigest()[:8]

        # Read current HEAD
        head_file = self.history_dir / "HEAD"
        parent = None
        if head_file.exists():
            parent = head_file.read_text().strip()

        # Write commit
        commit_dir = self.history_dir / "commits" / commit_hash
        commit_dir.mkdir(parents=True, exist_ok=True)

        commit_meta = {
            "hash": commit_hash,
            "message": message,
            "author": author,
            "timestamp": datetime.now().isoformat(),
            "parent": parent,
            "cellab_version": CELLAB_VERSION,
        }

        self._write_json(commit_dir / "commit.json", commit_meta)
        self._write_json(commit_dir / "project_state.json", snapshot)

        # Update HEAD
        head_file.write_text(commit_hash)

        return commit_hash

    def log(self, max_entries: int = 50) -> List[Dict[str, Any]]:
        """
        Get commit history (newest first).

        Returns:
            List of commit metadata dicts
        """
        head_file = self.history_dir / "HEAD"
        if not head_file.exists():
            return []

        commits = []
        current = head_file.read_text().strip()

        while current and len(commits) < max_entries:
            commit_dir = self.history_dir / "commits" / current
            meta_file = commit_dir / "commit.json"

            if not meta_file.exists():
                break

            meta = self._read_json(meta_file)
            commits.append(meta)
            current = meta.get("parent")

        return commits

    def diff(self, hash_a: str, hash_b: str) -> Dict[str, Any]:
        """
        Compare two commits. Returns parameter differences.

        Returns:
            Dict with added, removed, and changed parameters
        """
        state_a = self._read_json(
            self.history_dir / "commits" / hash_a / "project_state.json"
        )
        state_b = self._read_json(
            self.history_dir / "commits" / hash_b / "project_state.json"
        )

        return self._deep_diff(state_a, state_b)

    def tag(self, tag_name: str, commit_hash: Optional[str] = None):
        """
        Tag a commit with a human-readable name.

        Args:
            tag_name: e.g., 'final_for_paper', 'before_threshold_change'
            commit_hash: Which commit to tag (default: HEAD)
        """
        if commit_hash is None:
            head_file = self.history_dir / "HEAD"
            if not head_file.exists():
                raise ValueError("No commits to tag")
            commit_hash = head_file.read_text().strip()

        tag_file = self.history_dir / "tags" / f"{tag_name}.json"
        self._write_json(tag_file, {
            "tag": tag_name,
            "commit": commit_hash,
            "created": datetime.now().isoformat(),
        })

    def checkout(self, commit_hash: str):
        """
        Restore all parameters to a previous commit's state.
        Does NOT delete result files — only reverts parameter JSONs.
        """
        state = self._read_json(
            self.history_dir / "commits" / commit_hash / "project_state.json"
        )

        for ws_id, ws_data in state.get("workspaces", {}).items():
            for pid, p_data in ws_data.get("pipelines", {}).items():
                for step_id, step_params in p_data.get("steps", {}).items():
                    step_dir = self.get_step_dir(ws_id, pid, step_id)
                    self._write_json(step_dir / PARAMS_FILE, step_params)

    # ═════════════════════════════════════════════
    # CONNECTIONS (inter-pipeline wiring)
    # ═════════════════════════════════════════════

    def connect_pipelines(self, ws_id: str,
                          source_pipeline: str, source_step: str,
                          target_pipeline: str, target_step: str,
                          output_name: str = "default"):
        """
        Create a connection from one pipeline's step output
        to another pipeline's step input.

        Args:
            ws_id: Workspace ID
            source_pipeline: Source pipeline ID
            source_step: Source step ID (the one producing output)
            target_pipeline: Target pipeline ID
            target_step: Target step ID (the one consuming input)
            output_name: Name of the output to connect
        """
        connection = {
            "id": str(uuid.uuid4())[:8],
            "source_pipeline": source_pipeline,
            "source_step": source_step,
            "target_pipeline": target_pipeline,
            "target_step": target_step,
            "output_name": output_name,
            "created": datetime.now().isoformat(),
        }

        # Add to source's connections_out
        src_meta = self.get_pipeline(ws_id, source_pipeline)
        src_meta.setdefault("connections_out", []).append(connection)
        self._write_json(
            self.workspaces_dir / ws_id / source_pipeline / PIPELINE_FILE,
            src_meta
        )

        # Add to target's connections_in
        tgt_meta = self.get_pipeline(ws_id, target_pipeline)
        tgt_meta.setdefault("connections_in", []).append(connection)
        self._write_json(
            self.workspaces_dir / ws_id / target_pipeline / PIPELINE_FILE,
            tgt_meta
        )

    # ═════════════════════════════════════════════
    # FULL PROJECT STATE (for frontend)
    # ═════════════════════════════════════════════

    def get_full_state(self) -> Dict[str, Any]:
        """
        Return the complete project state for the frontend.
        Used when opening a project to reconstruct the entire UI.
        """
        state = {
            "project": {
                "name": self.name,
                "root": str(self.root),
                "author": self._manifest.get("author", ""),
                "description": self._manifest.get("description", ""),
                "created": self._manifest.get("created"),
                "modified": self._manifest.get("modified"),
                "active_packages": self._manifest.get("active_packages", []),
            },
            "gui_state": self._gui_state,
            "preferences": self._preferences,
            "workspaces": [],
            "data_references": self._manifest.get("data_references", []),
            "missing_files": self._verify_data_references(),
        }

        for ws in self.list_workspaces():
            ws_id = ws["id"]
            ws_dir = self.workspaces_dir / ws_id
            ws_data = {
                "id": ws_id,
                "name": ws["name"],
                "pipelines": [],
            }

            for p_entry in ws.get("pipelines", []):
                pid = p_entry["id"]
                pipeline_file = ws_dir / pid / PIPELINE_FILE
                if pipeline_file.exists():
                    p_meta = self._read_json(pipeline_file)

                    # Collect all step params
                    steps_data = {}
                    pipeline_dir = ws_dir / pid
                    for step_dir in pipeline_dir.iterdir():
                        if step_dir.is_dir() and step_dir.name != "results":
                            params_file = step_dir / PARAMS_FILE
                            if params_file.exists():
                                steps_data[step_dir.name] = \
                                    self._read_json(params_file)

                            # Auto-detect step status from results on disk
                            results_dir = step_dir / "results"
                            if step_dir.name not in p_meta.get("steps", {}):
                                if not p_meta.get("steps"):
                                    p_meta["steps"] = {}
                            step_info = p_meta["steps"].get(step_dir.name, {})
                            if results_dir.exists():
                                has_pkl = any(results_dir.glob("*.pkl"))
                                has_plots = any((results_dir / "plots").glob("*.png")) if (results_dir / "plots").exists() else False
                                if has_pkl or has_plots:
                                    if step_info.get("status") != "done":
                                        step_info["status"] = "done"
                                    p_meta["steps"][step_dir.name] = step_info
                                elif any(results_dir.iterdir()):
                                    if not step_info.get("status"):
                                        step_info["status"] = "configured"
                                    p_meta["steps"][step_dir.name] = step_info

                    p_meta["step_params"] = steps_data
                    ws_data["pipelines"].append(p_meta)

            state["workspaces"].append(ws_data)

        return state

    # ═════════════════════════════════════════════
    # INTERNAL HELPERS
    # ═════════════════════════════════════════════

    @staticmethod
    def _write_json(path: Path, data: Dict):
        """Write JSON with consistent formatting."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _read_json(path: Path) -> Dict:
        """Read a JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def _deep_diff(a: Any, b: Any, path: str = "") -> Dict[str, Any]:
        """Recursively diff two nested dicts."""
        changes = {"changed": [], "added": [], "removed": []}

        if isinstance(a, dict) and isinstance(b, dict):
            all_keys = set(a.keys()) | set(b.keys())
            for key in sorted(all_keys):
                key_path = f"{path}.{key}" if path else key
                if key not in a:
                    changes["added"].append({
                        "path": key_path, "value": b[key]
                    })
                elif key not in b:
                    changes["removed"].append({
                        "path": key_path, "value": a[key]
                    })
                elif a[key] != b[key]:
                    if isinstance(a[key], dict) and isinstance(b[key], dict):
                        sub = CellabProject._deep_diff(a[key], b[key], key_path)
                        changes["changed"].extend(sub["changed"])
                        changes["added"].extend(sub["added"])
                        changes["removed"].extend(sub["removed"])
                    else:
                        changes["changed"].append({
                            "path": key_path,
                            "old": a[key],
                            "new": b[key],
                        })
        elif a != b:
            changes["changed"].append({
                "path": path, "old": a, "new": b
            })

        return changes

    def __repr__(self):
        return (
            f"CellabProject(name='{self.name}', "
            f"root='{self.root}', "
            f"workspaces={len(self.list_workspaces())})"
        )
