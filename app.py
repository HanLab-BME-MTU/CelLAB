"""
CelLAB Backend API v3.1
========================
Flask REST API bridging the frontend GUI with the project manager.

Endpoints:
    /api/project/*      — create, open, save, close, archive
    /api/workspace/*    — create, list, delete, rename
    /api/pipeline/*     — create, delete, get, connect
    /api/step/*         — save/load params, get results dir
    /api/data/*         — import, list, resolve references
    /api/version/*      — commit, log, diff, tag, checkout
    /api/gui/*          — save/load GUI state
    /api/packages/*     — list, activate, deactivate
    /api/status          — server health check

All responses: { "success": bool, "data": ..., "error": ... }
"""

# CRITICAL: Set matplotlib backend BEFORE any imports that touch matplotlib
# (cornealia imports matplotlib.pyplot at module level — if TkAgg initializes
# first, switching to Agg later causes a hard crash on Windows)
import matplotlib
matplotlib.use('Agg')

import os
import sys
import json
import traceback
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

# Add backend to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)
# FASTIA internal imports (components/, wrapper_classes/, utils/) need this
FASTIA_DIR = os.path.join(BACKEND_DIR, 'fastia')
if FASTIA_DIR not in sys.path:
    sys.path.insert(0, FASTIA_DIR)
SHARED_UTILS_DIR = os.path.join(BACKEND_DIR, 'shared_modules')
if SHARED_UTILS_DIR not in sys.path:
    sys.path.insert(0, SHARED_UTILS_DIR)

SHARED_TOOLS_DIR = os.path.join(BACKEND_DIR, 'shared_tools')
if SHARED_TOOLS_DIR not in sys.path:
    sys.path.insert(0, SHARED_TOOLS_DIR)

from project_manager import CellabProject, DATA_COPY, DATA_LINK, DATA_MOVE

# ─── CellVisia backend (parametric feature-tree engine) ─────────────────────
# Import the module-level singleton; Flask routes mutate pipelines through it.
# Importing cellvisia also imports operations/*.py which register feature types.
from cellvisia.cellvisia import manager as cv_manager

# Associa — Signal Coupling module
try:
    from signal_associa_manager import AssociaManager
    assoc_manager = AssociaManager()
    print("✅ Associa manager loaded")
except ImportError:
    assoc_manager = None
    print("⚠️ Associa manager not available")

# CellADE — Cell Segmentation module
try:
    from cellade_manager import CellADEManager
    cellade_manager = CellADEManager()
    print("✅ CellADE manager loaded")
except ImportError:
    cellade_manager = None
    print("⚠️ CellADE manager not available")

# CellFADE — FA Detection module
try:
    from cellfade_manager import CellFADEManager
    cellfade_manager = CellFADEManager()
    print("✅ CellFADE manager loaded")
except ImportError:
    cellfade_manager = None
    print("⚠️ CellFADE manager not available")

# AnnotADE — Annotation tool
try:
    from annotade_manager import AnnotADEManager
    annotade_manager = AnnotADEManager()
    print("✅ AnnotADE manager loaded")
except ImportError:
    annotade_manager = None
    print("⚠️ AnnotADE manager not available")

# ═════════════════════════════════════════════
# APP SETUP
# ═════════════════════════════════════════════

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'frontend'),
            static_url_path='/frontend')

# Global project reference (single-project at a time)
_project: CellabProject = None


def get_project() -> CellabProject:
    """Get the current project or raise."""
    if _project is None:
        raise RuntimeError("No project open. Create or open a project first.")
    return _project


def api_response(data=None, error=None, status=200):
    """Standard API response wrapper."""
    return jsonify({
        "success": error is None,
        "data": data,
        "error": str(error) if error else None,
    }), status


def api_error(msg, status=400):
    return api_response(error=msg, status=status)


# ═════════════════════════════════════════════
# SERVE FRONTEND
# ═════════════════════════════════════════════

@app.route('/')
def index():
    """Serve the main workbench HTML."""
    frontend_dir = os.path.join(BASE_DIR, 'frontend')
    return send_from_directory(frontend_dir, 'workbench.html')


@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    """Serve frontend static files (no-cache during development)."""
    frontend_dir = os.path.join(BASE_DIR, 'frontend')
    response = send_from_directory(frontend_dir, filename)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# ═════════════════════════════════════════════
# STATUS
# ═════════════════════════════════════════════

@app.route('/api/status')
def status():
    """Server health check, current project info, and system stats."""
    import psutil

    cpu = psutil.cpu_percent(interval=0)
    mem = psutil.virtual_memory()

    # CelLAB process stats (including child workers)
    proc = psutil.Process()
    total_rss = proc.memory_info().rss
    try:
        proc_cpu = proc.cpu_percent(interval=0)
        # Track children persistently so cpu_percent delta works
        current_children = {}
        for child in proc.children(recursive=True):
            try:
                pid = child.pid
                current_children[pid] = True
                if pid not in _child_procs:
                    _child_procs[pid] = psutil.Process(pid)
                    _child_procs[pid].cpu_percent(interval=0)  # prime it
                else:
                    proc_cpu += _child_procs[pid].cpu_percent(interval=0)
                total_rss += child.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        # Clean up dead children
        dead = [pid for pid in _child_procs if pid not in current_children]
        for pid in dead:
            del _child_procs[pid]
    except:
        proc_cpu = 0.0

    data = {
        "status": "ready",
        "project_open": _project is not None,
        "system": {
            "cpu_percent": cpu,
            "ram_used_gb": round(mem.used / (1024**3), 1),
            "ram_total_gb": round(mem.total / (1024**3), 1),
            "ram_percent": mem.percent,
            "cellab_cpu": round(min(proc_cpu / psutil.cpu_count(), 100), 1),
            "cellab_ram_mb": round(total_rss / (1024**2), 0),
            "cellab_ram_percent": round(total_rss / mem.total * 100, 1),
        },
    }
    if _project:
        data["project_name"] = _project.name
        data["project_root"] = str(_project.root)

    return api_response(data)


# ═════════════════════════════════════════════
# PROJECT ENDPOINTS
# ═════════════════════════════════════════════

@app.route('/api/project/create', methods=['POST'])
def project_create():
    """
    Create a new project.
    Body: { "root": "/path/to/folder", "name": "MyProject",
            "author": "", "description": "" }
    """
    global _project
    try:
        body = request.get_json()
        root = body.get('root')
        name = body.get('name')

        if not root or not name:
            return api_error("'root' and 'name' are required")

        _project = CellabProject.create(
            root=root,
            name=name,
            author=body.get('author', ''),
            description=body.get('description', ''),
        )

        return api_response({
            "project_name": _project.name,
            "project_root": str(_project.root),
            "manifest": str(_project.manifest_path),
        })
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/project/open', methods=['POST'])
def project_open():
    """
    Open an existing project.
    Body: { "path": "/path/to/folder_or_cellab_file" }
    """
    global _project
    try:
        body = request.get_json()
        path = body.get('path')

        if not path:
            return api_error("'path' is required")

        _project = CellabProject.open(path)
        state = _project.get_full_state()

        return api_response(state)
    except FileNotFoundError as e:
        return api_error(str(e), 404)
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/project/save', methods=['POST'])
def project_save():
    """Save current project state."""
    try:
        project = get_project()
        project.save()
        return api_response({"saved": True})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/project/save_as', methods=['POST'])
def project_save_as():
    """
    Save project to a new location.
    Body: { "new_root": "/path/to/new/folder", "new_name": "NewName" }
    """
    global _project
    try:
        project = get_project()
        body = request.get_json()
        new_root = body.get('new_root')
        new_name = body.get('new_name')

        if not new_root:
            return api_error("'new_root' is required")

        project.save_as(new_root, new_name)
        _project = project  # Updated root

        return api_response({
            "project_name": project.name,
            "project_root": str(project.root),
        })
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/project/close', methods=['POST'])
def project_close():
    """Close the current project (saves first)."""
    global _project
    try:
        if _project:
            _project.save()
        _project = None
        return api_response({"closed": True})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/project/state', methods=['GET'])
def project_state():
    """Get full project state for frontend reconstruction."""
    try:
        project = get_project()
        return api_response(project.get_full_state())
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/project/archive', methods=['POST'])
def project_archive():
    """
    Create a zip archive.
    Body: { "output_path": "...", "include_results": true,
            "include_input_data": true, "include_gui_state": true }
    """
    try:
        project = get_project()
        body = request.get_json()

        output = body.get('output_path')
        if not output:
            # Default: save next to project root
            output = str(project.root.parent / f"{project.name}.cellab.zip")

        archive_path = project.archive(
            output_path=output,
            include_results=body.get('include_results', True),
            include_input_data=body.get('include_input_data', True),
            include_gui_state=body.get('include_gui_state', True),
        )

        return api_response({
            "archive_path": str(archive_path),
            "size_bytes": os.path.getsize(archive_path),
        })
    except Exception as e:
        return api_error(str(e), 500)


# ═════════════════════════════════════════════
# WORKSPACE ENDPOINTS
# ═════════════════════════════════════════════

@app.route('/api/workspace/create', methods=['POST'])
def workspace_create():
    """
    Create a new workspace.
    Body: { "name": "My Workspace" }
    """
    try:
        project = get_project()
        body = request.get_json()
        name = body.get('name', 'New Workspace')

        ws_id = project.create_workspace(name, ws_id=body.get('ws_id', ''))

        return api_response({
            "workspace_id": ws_id,
            "name": name,
        })
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/workspace/list', methods=['GET'])
def workspace_list():
    """List all workspaces."""
    try:
        project = get_project()
        return api_response(project.list_workspaces())
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/workspace/<ws_id>/delete', methods=['DELETE'])
def workspace_delete(ws_id):
    """Delete a workspace."""
    try:
        project = get_project()
        project.delete_workspace(ws_id)
        return api_response({"deleted": ws_id})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/workspace/<ws_id>/rename', methods=['POST'])
def workspace_rename(ws_id):
    """
    Rename a workspace.
    Body: { "name": "New Name" }
    """
    try:
        project = get_project()
        body = request.get_json()
        new_name = body.get('name')

        if not new_name:
            return api_error("'name' is required")

        # Update workspace.json
        ws_dir = project.workspaces_dir / ws_id
        ws_file = ws_dir / "workspace.json"
        if not ws_file.exists():
            return api_error(f"Workspace '{ws_id}' not found", 404)

        ws_meta = project._read_json(ws_file)
        ws_meta["name"] = new_name
        project._write_json(ws_file, ws_meta)

        # Update manifest
        for ws in project._manifest.get("workspaces", []):
            if ws["id"] == ws_id:
                ws["name"] = new_name
        project.save()

        return api_response({"workspace_id": ws_id, "name": new_name})
    except Exception as e:
        return api_error(str(e), 500)


# ═════════════════════════════════════════════
# PIPELINE ENDPOINTS
# ═════════════════════════════════════════════

@app.route('/api/pipeline/create', methods=['POST'])
def pipeline_create():
    """
    Create a new pipeline.
    Body: { "workspace_id": "ws_1", "type": "fastia", "name": "" }
    """
    try:
        project = get_project()
        body = request.get_json()
        ws_id = body.get('workspace_id')
        p_type = body.get('type')

        if not ws_id or not p_type:
            return api_error("'workspace_id' and 'type' are required")

        pid = project.create_pipeline(
            ws_id=ws_id,
            pipeline_type=p_type,
            name=body.get('name', ''),
            pipeline_id=body.get('pipeline_id', ''),
        )

        pipeline = project.get_pipeline(ws_id, pid)
        return api_response(pipeline)
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/pipeline/<ws_id>/<pipeline_id>', methods=['GET'])
def pipeline_get(ws_id, pipeline_id):
    """Get pipeline metadata."""
    try:
        project = get_project()
        pipeline = project.get_pipeline(ws_id, pipeline_id)
        return api_response(pipeline)
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/pipeline/<ws_id>/<pipeline_id>/delete', methods=['DELETE'])
def pipeline_delete(ws_id, pipeline_id):
    """Delete a pipeline and all its data, including referenced data files."""
    try:
        project = get_project()

        # --- Collect data file references BEFORE deleting ---
        referenced_files = set()
        try:
            params = project.load_params(ws_id, pipeline_id, 'import') or {}
            for sk, sv in params.items():
                if isinstance(sv, dict) and 'input_file' in sv:
                    referenced_files.add(sv['input_file'])
        except:
            pass

        # --- Delete pipeline (removes workspace dir + params) ---
        project.delete_pipeline(ws_id, pipeline_id)

        # --- Clean orphaned data files ---
        if referenced_files:
            # Check if any OTHER pipeline still references these files
            still_used = set()
            try:
                for ws_dir in (project.root / 'workspaces').iterdir():
                    if not ws_dir.is_dir():
                        continue
                    for p_dir in ws_dir.iterdir():
                        if not p_dir.is_dir():
                            continue
                        # Skip the pipeline we just deleted
                        if ws_dir.name == ws_id and p_dir.name == pipeline_id:
                            continue
                        try:
                            other_params = project.load_params(ws_dir.name, p_dir.name, 'import') or {}
                            for sk, sv in other_params.items():
                                if isinstance(sv, dict) and 'input_file' in sv:
                                    still_used.add(sv['input_file'])
                        except:
                            pass
            except:
                pass

            # Delete files not used by any remaining pipeline
            orphaned = referenced_files - still_used
            deleted_files = []
            for rel_path in orphaned:
                try:
                    abs_path = project.resolve_data_path(rel_path)
                    if abs_path and abs_path.exists():
                        abs_path.unlink()
                        deleted_files.append(rel_path)
                        print(f"[CLEANUP] Deleted orphaned data: {rel_path}")
                except:
                    pass

        # --- Clear in-memory caches for this pipeline ---
        for cache_name in ('_tiff_cache', '_labels_cache', '_mask_cache',
                           '_rendered_cache', '_tracks_cache', '_track_index',
                           '_track_render_cache'):
            cache = getattr(app, cache_name, None)
            if cache and isinstance(cache, dict):
                keys_to_remove = [k for k in cache if pipeline_id in str(k)]
                for k in keys_to_remove:
                    del cache[k]

        return api_response({"deleted": pipeline_id, "orphaned_data_cleaned": len(orphaned) if referenced_files else 0})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/pipeline/<ws_id>/<pipeline_id>/clean_downstream', methods=['POST'])
def pipeline_clean_downstream(ws_id, pipeline_id):
    """
    Clean downstream results when re-importing a new movie.
    Also removes old data file if a new one is specified.
    Body: { "new_file": "data/new_movie.tif" }  (optional)
    """
    try:
        import shutil
        project = get_project()
        body = request.get_json() or {}
        new_file = body.get('new_file')

        cleaned = []

        # --- Remove old data file if different from new ---
        if new_file:
            try:
                params = project.load_params(ws_id, pipeline_id, 'import') or {}
                for sk, sv in params.items():
                    if isinstance(sv, dict) and 'input_file' in sv:
                        old_file = sv['input_file']
                        if old_file and old_file != new_file:
                            abs_path = project.resolve_data_path(old_file)
                            if abs_path and abs_path.exists():
                                abs_path.unlink()
                                cleaned.append(f"Removed old data: {old_file}")
                                print(f"[CLEANUP] Removed old data file: {old_file}")
            except:
                pass

        # --- Clear all downstream result directories ---
        for step in ('detection', 'tracking', 'classification', 'kinetics', 'association'):
            try:
                results_dir = project.get_results_dir(ws_id, pipeline_id, step)
                if results_dir.exists():
                    shutil.rmtree(str(results_dir))
                    results_dir.mkdir(parents=True, exist_ok=True)
                    cleaned.append(f"Cleared {step} results")
                    print(f"[CLEANUP] Cleared {step} results for {pipeline_id}")
            except:
                pass

        # --- Clear in-memory caches ---
        for cache_name in ('_tiff_cache', '_labels_cache', '_mask_cache',
                           '_rendered_cache', '_tracks_cache', '_track_index',
                           '_track_render_cache'):
            cache = getattr(app, cache_name, None)
            if cache and isinstance(cache, dict):
                keys_to_remove = [k for k in cache if pipeline_id in str(k)]
                for k in keys_to_remove:
                    del cache[k]
                if keys_to_remove:
                    cleaned.append(f"Cleared {cache_name} cache ({len(keys_to_remove)} entries)")

        return api_response({"cleaned": cleaned, "n_cleaned": len(cleaned)})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/pipeline/<ws_id>/<pipeline_id>/position', methods=['POST'])
def pipeline_set_position(ws_id, pipeline_id):
    """
    Update pipeline canvas position.
    Body: { "x": 250, "y": 200 }
    """
    try:
        project = get_project()
        body = request.get_json()

        pipeline_path = project.workspaces_dir / ws_id / pipeline_id / "pipeline.json"
        pipeline = project._read_json(pipeline_path)
        pipeline["canvas_position"] = {
            "x": body.get("x", 0),
            "y": body.get("y", 0),
        }
        project._write_json(pipeline_path, pipeline)

        return api_response({"position": pipeline["canvas_position"]})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/pipeline/connect', methods=['POST'])
def pipeline_connect():
    """
    Connect two pipeline steps.
    Body: { "workspace_id": "ws_1",
            "source_pipeline": "FASTIA-1", "source_step": "detection",
            "target_pipeline": "IMMUNIA-1", "target_step": "tracking",
            "output_name": "fa_masks" }
    """
    try:
        project = get_project()
        body = request.get_json()

        project.connect_pipelines(
            ws_id=body['workspace_id'],
            source_pipeline=body['source_pipeline'],
            source_step=body['source_step'],
            target_pipeline=body['target_pipeline'],
            target_step=body['target_step'],
            output_name=body.get('output_name', 'default'),
        )

        return api_response({"connected": True})
    except Exception as e:
        return api_error(str(e), 500)


# ═════════════════════════════════════════════
# PACKAGE RUNNERS
# ═════════════════════════════════════════════

def _run_cornealia(project, ws_id, pipeline_id, step_id, params, results_dir, progress_cb=None):
    """
    Run Cornealia analysis step.
    
    Steps:
      - import: load image, preprocess if machine output, show preview
      - segmentation: runs collective_order_pipeline, saves segmentation plot
      - morphometry: uses existing results, generates analysis plots
      - batch: runs collective_order_pipeline_batch on a folder
    """
    import matplotlib.pyplot as plt
    import json
    import numpy as np
    import pickle
    import cv2

    try:
        # Collect all params from all sections
        all_params = {}
        for key, val in params.items():
            if isinstance(val, dict):
                all_params.update(val)
            else:
                all_params[key] = val

        # ── STEP: IMPORT ──────────────────────────────
        if step_id == 'import':
            from cornealia.cornealia import PipelineReporter, PIPELINE_STEPS

            # Create reporter for import step
            def _import_reporter_cb(step_id_r, status, board):
                if progress_cb:
                    completed = board['completed']
                    total = board['total']
                    step = board['steps'][step_id_r]
                    progress_cb(completed, total, phase=step['name'],
                                message=f"{step['name']}: {status}")
                    with _run_progress_lock:
                        for key, prog in _run_progress.items():
                            if isinstance(prog, dict):
                                prog['pipeline_board'] = board

            reporter = PipelineReporter(PIPELINE_STEPS, callback=_import_reporter_cb)

            input_file = all_params.get('input_file', '')
            if not input_file:
                return {"status": "error", "error_msg": "No image selected. Click Browse to select an image."}

            resolved = project.resolve_data_path(input_file)
            if resolved is None:
                return {"status": "error", "error_msg": f"File not found: {input_file}"}

            image_path = str(resolved)

            # Load image
            reporter.start('load')
            img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                reporter.fail('load', f"Could not load image: {image_path}")
                return {"status": "error", "error_msg": f"Could not load image: {image_path}"}
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            reporter.done('load', {'size': f"{img_rgb.shape[1]}×{img_rgb.shape[0]}"})

            plots_dir = results_dir / "plots"
            plots_dir.mkdir(exist_ok=True)
            outputs = {}

            # Save original preview
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            ax.imshow(img_rgb)
            ax.set_title(f'Loaded: {os.path.basename(image_path)}')
            ax.axis('off')
            plt.tight_layout()
            plt.savefig(str(plots_dir / "original.png"), dpi=150, bbox_inches='tight')
            plt.close()

            is_machine = all_params.get('is_machine_output', 'Yes') == 'Yes'
            outputs['image_size'] = f"{img_rgb.shape[1]} x {img_rgb.shape[0]}"
            outputs['is_machine_output'] = is_machine

            if is_machine:
                reporter.start('preprocess')
                try:
                    from cornealia.cornealia import cornealia as Cornealia
                    engine = Cornealia(
                        is_input_image_machine_output=True,
                        fcm_method=all_params.get('fcm_method', 'local'),
                        verbose=False,
                    )
                    cell_area, machine_metrics, dot_centroids = engine.cleaning_preprocessing(img_rgb)
                    reporter.done('preprocess', {
                        'machine_CD': machine_metrics.get('CD', '?') if machine_metrics else '?',
                    })

                    # Clean up OCR reader immediately
                    engine._ocr_reader = None
                    del engine
                    import gc; gc.collect()

                    # Save cell area preview
                    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
                    axes[0].imshow(img_rgb)
                    axes[0].set_title('Original (Machine Output)')
                    from matplotlib.patches import Rectangle
                    rect = Rectangle((24, 261), 684, 514, linewidth=2, edgecolor='lime', facecolor='none')
                    axes[0].add_patch(rect)
                    axes[0].axis('off')

                    axes[1].imshow(cell_area)
                    axes[1].set_title(f'Extracted Cell Area')
                    if dot_centroids is not None and len(dot_centroids) > 0:
                        axes[1].plot(dot_centroids[:, 0], dot_centroids[:, 1], 'r+', markersize=4, alpha=0.5)
                        axes[1].set_title(f'Cell Area ({len(dot_centroids)} machine dots)')
                    axes[1].axis('off')

                    plt.tight_layout()
                    plt.savefig(str(plots_dir / "import_preview.png"), dpi=150, bbox_inches='tight')
                    plt.close()

                    if machine_metrics:
                        outputs['machine_metrics'] = machine_metrics
                        with open(results_dir / "machine_metrics.json", 'w') as f:
                            json.dump(machine_metrics, f, indent=2)

                except Exception as preprocess_err:
                    reporter.fail('preprocess', str(preprocess_err))
                    outputs['preprocess_warning'] = str(preprocess_err)
            else:
                reporter.skip('preprocess')
                fig, ax = plt.subplots(1, 1, figsize=(8, 6))
                ax.imshow(img_rgb)
                ax.set_title(f'Raw Image ({img_rgb.shape[1]}×{img_rgb.shape[0]})')
                ax.axis('off')
                plt.tight_layout()
                plt.savefig(str(plots_dir / "import_preview.png"), dpi=150, bbox_inches='tight')
                plt.close()

            plt.close('all')
            outputs['plots'] = ['original.png', 'import_preview.png']
            outputs['pipeline_board'] = reporter.get_board()
            return {"status": "done", "outputs": outputs}

        # ── STEP: SEGMENTATION ────────────────────────
        if step_id == 'segmentation':
            # Get input file — check import step params first
            input_file = all_params.get('input_file', '')
            if not input_file:
                # Try loading from import step's saved params
                import_params = project.load_params(ws_id, pipeline_id, 'import')
                for k, v in import_params.items():
                    if isinstance(v, dict):
                        input_file = v.get('input_file', input_file)
                    elif k == 'input_file':
                        input_file = v

            if not input_file:
                return {"status": "error", "error_msg": "No image imported. Run Image Import first."}

            resolved = project.resolve_data_path(input_file)
            if resolved is None:
                return {"status": "error", "error_msg": f"Image not found: {input_file}"}

            # Also get import settings
            import_params = project.load_params(ws_id, pipeline_id, 'import')
            for k, v in import_params.items():
                if isinstance(v, dict):
                    all_params.update(v)

            return _run_cornealia_segmentation(project, results_dir, str(resolved), all_params, progress_cb=progress_cb)

        # ── STEP: MORPHOMETRY ─────────────────────────
        if step_id == 'morphometry':
            input_file = all_params.get('input_file', '')
            if not input_file:
                import_params = project.load_params(ws_id, pipeline_id, 'import')
                for k, v in import_params.items():
                    if isinstance(v, dict):
                        input_file = v.get('input_file', input_file)
                    elif k == 'input_file':
                        input_file = v
                # Also load seg params
                seg_params = project.load_params(ws_id, pipeline_id, 'segmentation')
                for k, v in seg_params.items():
                    if isinstance(v, dict):
                        all_params.update(v)

            if not input_file:
                return {"status": "error", "error_msg": "No image imported. Run Image Import first."}

            resolved = project.resolve_data_path(input_file)
            if resolved is None:
                return {"status": "error", "error_msg": f"Image not found: {input_file}"}

            # Merge import settings
            import_params = project.load_params(ws_id, pipeline_id, 'import')
            for k, v in import_params.items():
                if isinstance(v, dict):
                    all_params.update(v)

            # Load segmentation results from previous step
            seg_results_dir = project.get_results_dir(ws_id, pipeline_id, 'segmentation')
            seg_pickle = seg_results_dir / "segmentation_results.pkl"
            if not seg_pickle.exists():
                return {"status": "error", "error_msg": "Run Cell Segmentation first."}

            return _run_cornealia_morphometry(project, results_dir, str(resolved), all_params, seg_pickle, progress_cb=progress_cb)

        if step_id == 'batch':
            return {"status": "error", "error_msg": "Batch processing: TODO"}

        return {"status": "done", "outputs": {}}

    except Exception as e:
        import traceback
        traceback.print_exc()
        plt.close('all')
        return {"status": "error", "error_msg": str(e)}


def _cornealia_config(all_params):
    """Build Cornealia engine config from GUI params."""
    return {
        'pixel_size': float(all_params.get('pixel_size', 0.58)),
        'is_input_image_machine_output': all_params.get('is_machine_output', 'Yes') == 'Yes',
        'fcm_method': all_params.get('fcm_method', 'local'),
        'fitting_method': all_params.get('fitting_method', 'morse'),
        'min_expansion_shells': int(all_params.get('min_expansion_shells', 5)),
        'exclusion_ratio': float(all_params.get('exclusion_ratio', 0.15)),
        'shell_thickness': int(all_params.get('shell_thickness', 1)),
        'fitting_half_width': int(all_params.get('fitting_half_width', 10)),
        'SAVGOL_WINDOW': int(all_params.get('savgol_window', 11)),
        'SAVGOL_ORDER': int(all_params.get('savgol_order', 3)),
        'verbose': True,
    }


def _extract_safe_results(results):
    """Extract plotter-safe data from Cornealia results (no class instances)."""
    import numpy as np

    segmentor = results.get('segmentor')
    safe_results = {}

    for k, v in results.items():
        if k in ('segmentor', 'objects'):
            continue
        if isinstance(v, (int, float, str, bool)):
            safe_results[k] = v
        elif isinstance(v, (np.integer,)):
            safe_results[k] = int(v)
        elif isinstance(v, (np.floating,)):
            safe_results[k] = float(v)
        elif isinstance(v, np.bool_):
            safe_results[k] = bool(v)
        elif isinstance(v, np.ndarray):
            safe_results[k] = v
        elif isinstance(v, dict):
            safe_results[k] = v

    if segmentor is not None:
        safe_results['_segmentor_data'] = {
            'H': segmentor.H,
            'W': segmentor.W,
            'enhanced_image': segmentor.enhanced_image,
            'labels': segmentor.labels,
            'blobs': segmentor.blobs,
            'global_fg': segmentor.global_fg,
        }

    objects = results.get('objects', [])
    if objects:
        safe_results['_objects_data'] = {
            'centroids': np.array([o.centroid for o in objects]),
            'areas': np.array([o.area for o in objects]),
            'labels': np.array([o.label for o in objects]),
            'count': len(objects),
        }

    for img_key in ('input_image', 'cell_area', 'dot_centroids'):
        if img_key in results and results[img_key] is not None:
            safe_results[img_key] = results[img_key]

    return safe_results


def _run_cornealia_segmentation(project, results_dir, image_path, all_params, progress_cb=None):
    """
    Run segmentation only: detect cell boundaries and centroids.
    Saves segmentation data to pickle for morphometry step.
    """
    import matplotlib.pyplot as plt
    import json
    import numpy as np
    import pickle
    import cv2

    from cornealia.cornealia import cornealia as Cornealia, PipelineReporter, PIPELINE_STEPS

    # Create reporter with GUI callback
    def _reporter_cb(step_id, status, board):
        if progress_cb:
            completed = board['completed']
            total = board['total']
            step = board['steps'][step_id]
            progress_cb(completed, total, phase=step['name'],
                        message=f"{step['name']}: {status}")
            # Also store board in progress for real-time rendering
            with _run_progress_lock:
                for key, prog in _run_progress.items():
                    if isinstance(prog, dict):
                        prog['pipeline_board'] = board

    reporter = PipelineReporter(PIPELINE_STEPS, callback=_reporter_cb)

    config = _cornealia_config(all_params)
    engine = Cornealia(**config)

    # Load and preprocess
    reporter.start('load')
    input_image = engine._load_image(image_path)
    reporter.done('load')

    if config['is_input_image_machine_output']:
        reporter.start('preprocess')
        cell_area, machine_metrics, dot_centroids = engine.cleaning_preprocessing(input_image)
        reporter.done('preprocess')
    else:
        reporter.skip('preprocess')
        cell_area = input_image
        machine_metrics = None
        dot_centroids = None

    if engine.invert_image:
        cell_area = 255 - cell_area

    # Run segmentation
    reporter.start('segment')
    objects, segmentor = engine.segmentation(cell_area)
    n_cells = len(objects)
    reporter.done('segment', {'n_cells': n_cells})

    # Save segmentation results for morphometry step (plain arrays only)
    centroids = np.array([o.centroid for o in objects])
    areas = np.array([o.area for o in objects])
    seg_data = {
        'centroids': centroids,
        'areas': areas,
        'image_dims': (segmentor.H, segmentor.W),
        'input_image': input_image,
        'cell_area': cell_area,
        'machine_metrics': machine_metrics,
        'dot_centroids': dot_centroids,
        'image_path': image_path,
        'n_cells': n_cells,
    }
    with open(results_dir / "segmentation_results.pkl", 'wb') as f:
        pickle.dump(seg_data, f)

    # Generate segmentation preview plot
    plots_dir = results_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    centroids = np.array([o.centroid for o in objects])

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Original / cell area
    axes[0].imshow(cell_area)
    axes[0].set_title(f'Cell Area ({cell_area.shape[1]}×{cell_area.shape[0]})')
    axes[0].axis('off')

    # Segmentation overlay
    axes[1].imshow(cell_area)
    axes[1].imshow(segmentor.labels, alpha=0.3, cmap='nipy_spectral')
    if len(centroids) > 0:
        axes[1].plot(centroids[:, 1], centroids[:, 0], 'r.', markersize=2, alpha=0.5)
    axes[1].set_title(f'Segmentation ({n_cells} cells)')
    axes[1].axis('off')

    plt.tight_layout()
    plt.savefig(str(plots_dir / "segmentation_preview.png"), dpi=150, bbox_inches='tight')
    plt.close('all')

    # Save segmentation data for plotting (matches new result structure)
    safe_seg = {
        'segmentation': {
            'H': segmentor.H,
            'W': segmentor.W,
            'enhanced_image': segmentor.enhanced_image,
            'labels': segmentor.labels,
            'blobs': segmentor.blobs,
            'global_fg': segmentor.global_fg,
            'centroids': centroids,
            'areas': np.array([o.area for o in objects]),
            'cell_labels': np.array([o.label for o in objects]),
            'n_cells': n_cells,
        },
        'input_image': input_image,
        'cell_area': cell_area,
        'metrics_area': cell_area,  # same as cell_area for non-machine; overwritten below for machine
        'n_cells': n_cells,
    }
    # For machine output, metrics_area is a different crop
    if config['is_input_image_machine_output'] and input_image is not None:
        safe_seg['metrics_area'] = input_image[812:968, 114:307]

    with open(results_dir / "full_results.pkl", 'wb') as f:
        pickle.dump(safe_seg, f)

    # Clean up
    engine._ocr_reader = None
    del engine
    import gc
    gc.collect()

    return {
        "status": "done",
        "outputs": {
            "n_cells": n_cells,
            "image_size": f"{cell_area.shape[1]} x {cell_area.shape[0]}",
            "pipeline_board": reporter.get_board(),
        },
    }


def _run_cornealia_morphometry(project, results_dir, image_path, all_params, seg_pickle, progress_cb=None):
    """
    Run morphometric analysis using saved segmentation centroids.
    Computes cell metrics, g(r), V(r), collective order K, and force field.
    """
    import json
    import numpy as np
    import pickle

    from cornealia.cornealia import cornealia as Cornealia, PipelineReporter, PIPELINE_STEPS

    # Create reporter with GUI callback
    def _reporter_cb(step_id, status, board):
        if progress_cb:
            completed = board['completed']
            total = board['total']
            step = board['steps'][step_id]
            progress_cb(completed, total, phase=step['name'],
                        message=f"{step['name']}: {status}")
            # Also store board in progress for real-time rendering
            with _run_progress_lock:
                for key, prog in _run_progress.items():
                    if isinstance(prog, dict):
                        prog['pipeline_board'] = board

    reporter = PipelineReporter(PIPELINE_STEPS, callback=_reporter_cb)

    # Previous steps already completed in segmentation step
    reporter.done('load')
    reporter.done('preprocess')
    reporter.done('segment')

    with open(seg_pickle, 'rb') as f:
        seg_data = pickle.load(f)
    
    reporter.board['segment']['outputs'] = {'n_cells': len(seg_data['centroids'])}

    config = _cornealia_config(all_params)
    engine = Cornealia(**config)

    # Classic metrics
    reporter.start('metrics')
    classic_metrics = engine._compute_classic_metrics(
        seg_data['centroids'], seg_data['areas'],
        seg_data['image_dims'][0], seg_data['image_dims'][1],
        method='segmentation'
    )
    reporter.done('metrics', {
        'CD_calc': round(classic_metrics.get('CD_calc', 0), 1),
        'Ave_calc': round(classic_metrics.get('Ave_calc', 0), 1),
        'HEX_calc': round(classic_metrics.get('HEX_calc', 0), 1),
    })

    # Collective order (g(r) + quality gate + fitting)
    reporter.start('gr')
    results = engine.compute_collective_order(
        centroids=seg_data['centroids'],
        image_dims=seg_data['image_dims'],
    )
    reporter.done('gr', {
        'n_interior': results.get('n_interior'),
        'g_peak': round(results.get('g_peak', 0), 3),
    })
    reporter.done('quality', {
        'reliable': results.get('reliable'),
        'R2_damped': results.get('R2_damped'),
        'SNR': results.get('SNR'),
    })
    reporter.done('fitting', {
        'K': results.get('K'),
        'K_ds': results.get('K_ds'),
        'r0_fit': results.get('r0_fit'),
    })

    # Add image data and segmentation for plotter
    results['input_image'] = seg_data['input_image']
    results['cell_area'] = seg_data['cell_area']
    results['machine_metrics'] = seg_data['machine_metrics']
    results['dot_centroids'] = seg_data['dot_centroids']
    results['image_path'] = image_path
    results.update(classic_metrics)

    # Carry forward segmentation data (needed by comprehensive/pipeline_figure plots)
    results['segmentation'] = {
        'H': seg_data['image_dims'][0],
        'W': seg_data['image_dims'][1],
        'centroids': seg_data['centroids'],
        'n_cells': len(seg_data['centroids']),
        'enhanced_image': None,
        'labels': None,
        'blobs': None,
        'global_fg': None,
    }
    # Load full segmentation data if available
    seg_full_pkl = seg_pickle.parent / "full_results.pkl"
    if seg_full_pkl.exists():
        try:
            with open(seg_full_pkl, 'rb') as f:
                seg_full = pickle.load(f)
            seg_from_full = seg_full.get('segmentation', {})
            for key in ('enhanced_image', 'labels', 'blobs', 'global_fg', 'areas', 'cell_labels'):
                if key in seg_from_full:
                    results['segmentation'][key] = seg_from_full[key]
        except Exception:
            pass

    # Force field
    reporter.start('force')
    rf = engine._compute_residual_field(results)
    results['residual_field'] = rf
    if rf is not None:
        results['mean_F'] = rf['mean_F']
        results['frac_compression'] = rf['frac_compression']
        results['spatial_cv'] = rf['spatial_cv']
        results['n_hot_spots'] = rf['n_hot_spots']
        reporter.done('force', {
            'mean_F': round(rf['mean_F'], 4),
            'n_hot_spots': rf['n_hot_spots'],
        })
    else:
        results['mean_F'] = None
        results['frac_compression'] = None
        results['spatial_cv'] = None
        results['n_hot_spots'] = 0
        reporter.skip('force')

    # Extract safe results
    safe_results = _extract_safe_results(results)
    print("  [DIAG] Safe results extracted")

    # Clean up
    engine._ocr_reader = None
    del engine, results
    import gc
    gc.collect()

    # Save scalar results as JSON
    scalar_results = {k: v for k, v in safe_results.items()
                      if isinstance(v, (int, float, str, bool))}
    with open(results_dir / "analysis_results.json", 'w') as f:
        json.dump(scalar_results, f, indent=2, default=str)

    # Save full results as pickle
    try:
        with open(results_dir / "full_results.pkl", 'wb') as f:
            pickle.dump(safe_results, f)
        print("  [DIAG] Pickle saved OK")
    except Exception as pkl_err:
        print(f"  [DIAG] Pickle error: {pkl_err}")

    available_plots = ['segmentation', 'radial_distribution', 'potential',
                       'fitting', 'mechanical_field', 'comprehensive', 'publication_gr',
                       'publication_vr', 'pipeline_figure']

    return {
        "status": "done",
        "outputs": {
            "n_cells": scalar_results.get('n_cells', 0),
            "K": scalar_results.get('K', 'N/A'),
            "r0_fit": scalar_results.get('r0_fit', 'N/A'),
            "reliable": scalar_results.get('reliable', False),
            "g_peak": scalar_results.get('g_peak', 'N/A'),
            "available_plots": available_plots,
            "CD_calc": scalar_results.get('CD_calc', 'N/A'),
            "Ave_calc": scalar_results.get('Ave_calc', 'N/A'),
            "CV_calc": scalar_results.get('CV_calc', 'N/A'),
            "HEX_calc": scalar_results.get('HEX_calc', 'N/A'),
            "mean_F": scalar_results.get('mean_F', 'N/A'),
            "frac_compression": scalar_results.get('frac_compression', 'N/A'),
            "spatial_cv": scalar_results.get('spatial_cv', 'N/A'),
            "n_hot_spots": scalar_results.get('n_hot_spots', 0),
            "pipeline_board": reporter.get_board(),
        },
    }


def _run_cornealia_batch(project, ws_id, pipeline_id, step_id, params, results_dir):
    """
    Run Cornealia batch processing.
    
    Steps:
      - batch_setup: validates folder, returns image count
      - batch_run: runs collective_order_pipeline_batch, saves CSV + JSON
      - batch_results: no-op (results already saved)
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import json
    import numpy as np
    import pandas as pd

    try:
        # Collect all params
        all_params = {}
        for key, val in params.items():
            if isinstance(val, dict):
                all_params.update(val)
            else:
                all_params[key] = val

        # Also load params from setup step
        setup_params = project.load_params(ws_id, pipeline_id, 'batch_setup')
        for key, val in setup_params.items():
            if isinstance(val, dict):
                all_params.update(val)
            else:
                if key not in all_params:
                    all_params[key] = val

        # ── STEP: BATCH SETUP ─────────────────────────
        if step_id == 'batch_setup':
            folder = all_params.get('batch_folder', '')
            if not folder:
                return {"status": "error", "error_msg": "No folder selected."}

            from pathlib import Path
            p = Path(folder)
            if not p.exists():
                return {"status": "error", "error_msg": f"Folder not found: {folder}"}

            extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')
            image_paths = [f for f in p.rglob('*.*') if f.suffix.lower() in extensions]

            return {
                "status": "done",
                "outputs": {
                    "folder": str(folder),
                    "n_images": len(image_paths),
                    "images": [f.name for f in image_paths[:20]],  # first 20 names
                },
            }

        # ── STEP: BATCH RUN ───────────────────────────
        if step_id == 'batch_run':
            folder = all_params.get('batch_folder', '')
            if not folder:
                return {"status": "error", "error_msg": "No folder configured. Set up batch first."}

            n_workers = int(all_params.get('n_workers', 1))

            from cornealia.cornealia import cornealia as Cornealia

            config = {
                'pixel_size': float(all_params.get('pixel_size', 0.58)),
                'is_input_image_machine_output': all_params.get('is_machine_output', 'Yes') == 'Yes',
                'fcm_method': all_params.get('fcm_method', 'local'),
                'fitting_method': all_params.get('fitting_method', 'morse'),
                'min_expansion_shells': int(all_params.get('min_expansion_shells', 5)),
                'exclusion_ratio': float(all_params.get('exclusion_ratio', 0.15)),
                'shell_thickness': int(all_params.get('shell_thickness', 1)),
                'fitting_half_width': int(all_params.get('fitting_half_width', 10)),
                'SAVGOL_WINDOW': int(all_params.get('savgol_window', 11)),
                'SAVGOL_ORDER': int(all_params.get('savgol_order', 3)),
                'verbose': False,
            }

            print(f"  [BATCH] Starting batch on {folder} with {n_workers} workers")

            engine = Cornealia(**config)
            batch_results = engine.collective_order_batch(
                folder_path=folder,
                n_workers=n_workers,
            )

            # Clean up engine
            engine._ocr_reader = None
            del engine
            import gc
            gc.collect()

            print(f"  [BATCH] Done, {len(batch_results)} results")

            # Separate successes and failures
            successes = [r for r in batch_results if 'error' not in r]
            failures = [r for r in batch_results if 'error' in r]

            # Build DataFrame from scalar results
            if successes:
                # Extract scalar columns
                scalar_keys = [k for k, v in successes[0].items()
                               if isinstance(v, (int, float, str, bool, np.integer, np.floating, np.bool_))]

                rows = []
                for r in successes:
                    row = {}
                    for k in scalar_keys:
                        v = r.get(k)
                        if isinstance(v, (np.integer,)):
                            row[k] = int(v)
                        elif isinstance(v, (np.floating,)):
                            row[k] = float(v)
                        elif isinstance(v, np.bool_):
                            row[k] = bool(v)
                        else:
                            row[k] = v
                    rows.append(row)

                df = pd.DataFrame(rows)

                # Rename image_path → Image_Name
                if 'image_path' in df.columns:
                    import os.path
                    df['Image_Name'] = df['image_path'].apply(lambda p: os.path.basename(p) if isinstance(p, str) else p)
                    df.drop(columns=['image_path'], inplace=True)
                    cols = ['Image_Name'] + [c for c in df.columns if c != 'Image_Name']
                    df = df[cols]

                # Compute micrometer-converted columns for batch plotter
                px = float(all_params.get('pixel_size', 0.58))
                px2 = px * px
                if 'K' in df.columns:
                    df['K_um'] = df['K'] / px2
                if 'K_ds' in df.columns:
                    df['K_ds_um'] = df['K_ds'] / px2
                if 'K_Vmin' in df.columns:
                    df['K_Vmin_um'] = df['K_Vmin'] / px2
                if 'K_gpeak' in df.columns:
                    df['K_gpeak_um'] = df['K_gpeak'] / px2
                if 'K_quad_raw' in df.columns:
                    df['K_quad_raw_um'] = df['K_quad_raw'] / px2
                if 'K_morse_raw' in df.columns:
                    df['K_morse_raw_um'] = df['K_morse_raw'] / px2
                if 'K_quad_guided' in df.columns:
                    df['K_quad_guided_um'] = df['K_quad_guided'] / px2
                if 'K_morse_guided' in df.columns:
                    df['K_morse_guided_um'] = df['K_morse_guided'] / px2
                if 'r0_fit' in df.columns:
                    df['r_0_um'] = df['r0_fit'] * px
                    df['r_0_px'] = df['r0_fit']
                if 'g_peak' in df.columns and 'g_peak' not in df.columns:
                    pass  # already there

                # Save CSV
                csv_path = results_dir / "batch_results.csv"
                df.to_csv(csv_path, index=False)
                print(f"  [BATCH] CSV saved: {csv_path}")

                # Save JSON summary
                summary = {
                    "n_total": len(batch_results),
                    "n_success": len(successes),
                    "n_failed": len(failures),
                    "columns": list(df.columns),
                    "failures": [{"image": r.get('image_path', '?'), "error": r.get('error', '?')} for r in failures],
                }

                # Add basic stats
                for col in ['K', 'n_cells', 'r0_fit', 'g_peak']:
                    if col in df.columns:
                        valid = df[col].dropna()
                        if len(valid) > 0:
                            summary[f"{col}_mean"] = round(float(valid.mean()), 4)
                            summary[f"{col}_std"] = round(float(valid.std()), 4)
                            summary[f"{col}_min"] = round(float(valid.min()), 4)
                            summary[f"{col}_max"] = round(float(valid.max()), 4)

                with open(results_dir / "batch_summary.json", 'w') as f:
                    json.dump(summary, f, indent=2, default=str)

                return {
                    "status": "done",
                    "outputs": {
                        "n_total": len(batch_results),
                        "n_success": len(successes),
                        "n_failed": len(failures),
                        "csv_path": "batch_results.csv",
                        "K_mean": summary.get('K_mean', 'N/A'),
                        "K_std": summary.get('K_std', 'N/A'),
                    },
                }
            else:
                return {
                    "status": "error",
                    "error_msg": f"All {len(failures)} images failed.",
                    "outputs": {
                        "failures": [r.get('error', '?') for r in failures[:5]],
                    },
                }

        # ── STEP: BATCH RESULTS ───────────────────────
        if step_id == 'batch_results':
            # Check if CSV exists
            csv_path = results_dir / "batch_results.csv"
            if not csv_path.exists():
                # Try looking in batch_run step
                batch_run_results = project.get_results_dir(ws_id, pipeline_id, 'batch_run')
                csv_path = batch_run_results / "batch_results.csv"

            if csv_path.exists():
                return {
                    "status": "done",
                    "outputs": {"csv_exists": True, "csv_path": str(csv_path)},
                }
            return {"status": "error", "error_msg": "No batch results found. Run the batch first."}

        return {"status": "done", "outputs": {}}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "error_msg": str(e)}


def _run_fastia(project, ws_id, pipeline_id, step_id, params, results_dir, progress_cb=None, cancel_evt=None):
    """
    Run FASTIA analysis step.

    Steps:
      - import: handled by frontend (load/preview)
      - detection: CellFADE FA detection on selected channel
      - tracking: link detections across frames
      - classification: extract features + classify FA groups
      - kinetics: compute assembly/disassembly rates
      - association: correlation, Granger, CCM analysis
    """
    import json

    # Flatten section params
    all_params = {}
    for section_key, section_val in params.items():
        if isinstance(section_val, dict):
            all_params.update(section_val)
        else:
            all_params[section_key] = section_val

    print(f"[FASTIA] Running step: {step_id}")
    print(f"[FASTIA] Params: {json.dumps(all_params, default=str)[:300]}")

    try:
        if step_id == 'import':
            return {"status": "done", "outputs": {"message": "Import handled by frontend"}}

        elif step_id == 'detection':
            mode = 'stack'  # Run Full Stack always processes all frames
            channel = all_params.get('detection_channel', 'vinculin')
            n_workers = int(all_params.get('n_workers', 1))

            print(f"[FASTIA] Detection — channel: {channel}, mode: {mode}, workers: {n_workers}")

            # Get the movie from import step params
            import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
            file_path = None
            for section_key, section_val in import_params.items():
                if isinstance(section_val, dict) and 'input_file' in section_val:
                    file_path = section_val['input_file']
                    break
            if not file_path:
                return {"status": "error", "error_msg": "No movie loaded. Import a movie first."}

            resolved = project.resolve_data_path(file_path)
            if resolved is None:
                return {"status": "error", "error_msg": f"Movie file not found: {file_path}"}

            # Find which channel index matches the selected channel name
            ch_params = {}
            for sk, sv in import_params.items():
                if isinstance(sv, dict) and 'ch1_name' in sv:
                    ch_params = sv
                    break
            ch_idx = 0
            for i in range(1, 5):
                if ch_params.get(f'ch{i}_name', '').lower() == channel.lower():
                    ch_idx = i - 1
                    break

            try:
                import tifffile
                import pickle
                import numpy as np
                from wrapper_classes.fastia_detector import fastia_detector
                from components.cell_mask import segment_cell_stack as _seg_stack

                # Load from cache
                cache_key = str(resolved)
                if not hasattr(app, '_tiff_cache'):
                    app._tiff_cache = {}
                if cache_key not in app._tiff_cache:
                    app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
                stack = app._tiff_cache[cache_key]

                # Extract the FA detection channel
                if stack.ndim == 4:
                    ch_stack = stack[:, ch_idx, :, :]
                else:
                    ch_stack = stack

                print(f"[FASTIA] Running detection on {ch_stack.shape[0]} frames, channel idx {ch_idx}")

                # --- Step 1: Cell segmentation (runs first to provide masks) ---
                smooth_sigma = float(all_params.get('smooth_sigma', 5))
                global_threshold = str(all_params.get('global_threshold', 'true')).lower() == 'true'
                keep_largest = str(all_params.get('keep_largest', 'true')).lower() == 'true'
                seg_method = all_params.get('seg_method', 'otsu')
                manual_thresh_str = all_params.get('manual_threshold', '')
                manual_thresh = float(manual_thresh_str) if manual_thresh_str else None
                intensity_min_str = all_params.get('intensity_min', '')
                intensity_min = float(intensity_min_str) if intensity_min_str else None
                if intensity_min is not None and intensity_min <= 0:
                    intensity_min = None
                intensity_max_str = all_params.get('intensity_max', '')
                intensity_max = float(intensity_max_str) if intensity_max_str else None
                if intensity_max is not None and intensity_max <= 0:
                    intensity_max = None

                seg_channel_name = all_params.get('seg_channel', channel)
                seg_ch_idx = ch_idx
                for i in range(1, 5):
                    if ch_params.get(f'ch{i}_name', '').lower() == seg_channel_name.lower():
                        seg_ch_idx = i - 1
                        break
                if stack.ndim == 4:
                    seg_stack = stack[:, seg_ch_idx, :, :]
                else:
                    seg_stack = stack

                print(f"[FASTIA] Running cell segmentation — method={seg_method}, sigma={smooth_sigma}, global={global_threshold}, keep_largest={keep_largest}")

                if progress_cb:
                    progress_cb(0, 1, 'cell_seg', 'Running cell segmentation...')

                cell_mask_3d, seg_thresh = _seg_stack(
                    seg_stack, smooth_sigma=smooth_sigma,
                    global_threshold=global_threshold,
                    method=seg_method, manual_threshold=manual_thresh,
                    keep_largest=keep_largest,
                    intensity_min=intensity_min, intensity_max=intensity_max,
                    verbose=True)

                np.save(str(results_dir / 'cell_mask_3d.npy'), cell_mask_3d)
                cell_area_mean = int(np.mean(np.sum(cell_mask_3d, axis=(1, 2))))
                print(f"[FASTIA] Cell segmentation done — mean cell area: {cell_area_mean} px")

                if progress_cb:
                    progress_cb(1, 1, 'cell_seg', f'Cell seg done — {cell_area_mean:,} px avg')

                # Check cancellation before starting detection
                if cancel_evt and cancel_evt.is_set():
                    print("[FASTIA] Cancelled after cell segmentation")
                    return {"status": "cancelled", "outputs": {"message": "Cancelled after cell segmentation"}}

                # --- Step 2: FA detection with cell mask filtering ---
                det_params = {k: v for k, v in all_params.items()
                              if k not in ('detection_channel', 'n_workers',
                                          'smooth_sigma', 'global_threshold',
                                          'keep_largest', 'seg_method',
                                          'manual_threshold', 'intensity_min',
                                          'intensity_max', 'seg_channel')}
                detector = fastia_detector(det_params)

                def _det_progress(current, total):
                    if progress_cb:
                        progress_cb(current, total, 'detection', f'Detecting frame {current}/{total}')

                results = detector.detect_stack(ch_stack, n_workers=n_workers,
                                                cell_masks=cell_mask_3d,
                                                progress_cb=_det_progress,
                                                cancel_evt=cancel_evt)
                all_labels = results['all_labels']
                all_detections = results['detections']
                n_excluded = results.get('n_excluded', 0)
                was_cancelled = results.get('cancelled', False)
                total_fa = sum(len(d) for d in all_detections)
                n_done = len(all_labels)

                if was_cancelled:
                    print(f"[FASTIA] Cancelled after {n_done} frames ({total_fa} FAs detected so far)")
                    # Save partial results
                    if n_done > 0:
                        np.save(str(results_dir / 'all_labels.npy'), np.array(all_labels, dtype=object), allow_pickle=True)
                        with open(str(results_dir / 'detections.pkl'), 'wb') as f:
                            pickle.dump(all_detections, f)
                    return {
                        "status": "cancelled",
                        "outputs": {
                            "n_frames": n_done,
                            "total_fa": total_fa,
                            "message": f"Cancelled after {n_done} frames · {total_fa} FAs detected (partial)"
                        }
                    }

                print(f"[FASTIA] Full stack: {total_fa} FAs inside cell mask ({n_excluded} excluded outside)")

                # Save FA detection results (already filtered)
                np.save(str(results_dir / 'all_labels.npy'), np.array(all_labels, dtype=object), allow_pickle=True)
                with open(str(results_dir / 'detections.pkl'), 'wb') as f:
                    pickle.dump(all_detections, f)

                return {
                    "status": "done",
                    "outputs": {
                        "n_frames": len(all_labels),
                        "total_fa": total_fa,
                        "n_excluded": n_excluded,
                        "cell_area_mean_px": cell_area_mean,
                        "message": f"Detected {total_fa} FAs across {len(all_labels)} frames · {n_excluded} excluded outside cell · Cell mask: {cell_area_mean:,} px avg"
                    }
                }
            except ImportError as ie:
                return {"status": "error", "error_msg": f"FASTIA detector not available: {ie}"}
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {"status": "error", "error_msg": str(e)}

        elif step_id == 'tracking':
            print(f"[FASTIA] Tracking — search_range: {all_params.get('max_search_range', 5)}")

            try:
                import pickle
                import numpy as np
                import time as _time
                from wrapper_classes.fastia_tracker import fastia_tracker

                # Phase 1: Load detection results
                if progress_cb:
                    progress_cb(0, 4, 'loading', 'Loading detection results...')

                det_results_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')
                det_pkl = det_results_dir / 'detections.pkl'
                if not det_pkl.exists():
                    return {"status": "error", "error_msg": "No detection results found. Run detection first."}

                with open(str(det_pkl), 'rb') as f:
                    all_detections = pickle.load(f)

                n_frames = len(all_detections)
                n_dets = sum(len(d) for d in all_detections)
                print(f"[FASTIA] Loaded {n_dets} detections across {n_frames} frames")

                if cancel_evt and cancel_evt.is_set():
                    return {"status": "cancelled", "outputs": {"message": "Cancelled before tracking"}}

                # Phase 2: Run tracking
                if progress_cb:
                    progress_cb(1, 4, 'tracking', f'Linking {n_dets:,} detections across {n_frames} frames...')

                track_params = {
                    'max_search_range': int(all_params.get('max_search_range', 5)),
                    'memory': int(all_params.get('memory', 8)),
                    'w_dist': float(all_params.get('w_dist', 1.0)),
                    'w_size': float(all_params.get('w_size', 0.05)),
                    'w_orient': float(all_params.get('w_orient', 0.3)),
                    'min_track_length': int(all_params.get('min_track_length', 3)),
                }

                print(f"[FASTIA] Tracking params: {track_params}")

                t0 = _time.time()
                tracker = fastia_tracker(track_params)
                tracks = tracker.track(all_detections, analyze_quality=True, verbose=True)
                elapsed = _time.time() - t0

                if cancel_evt and cancel_evt.is_set():
                    return {"status": "cancelled", "outputs": {"message": "Cancelled during tracking"}}

                # Phase 3: Save results
                if progress_cb:
                    progress_cb(3, 4, 'saving', 'Saving tracking results...')

                with open(str(results_dir / 'tracks.pkl'), 'wb') as f:
                    pickle.dump(tracks, f)

                # Save quality/statistics if available
                if tracker.quality_results is not None:
                    with open(str(results_dir / 'track_quality.pkl'), 'wb') as f:
                        pickle.dump(tracker.quality_results, f)
                if tracker.statistics is not None:
                    with open(str(results_dir / 'track_statistics.pkl'), 'wb') as f:
                        pickle.dump(tracker.statistics, f)

                # Compute summary stats
                n_tracks = len(tracks) if isinstance(tracks, list) else 0
                track_lengths = [len(t) for t in tracks] if isinstance(tracks, list) else []
                mean_len = float(np.mean(track_lengths)) if track_lengths else 0
                median_len = float(np.median(track_lengths)) if track_lengths else 0
                max_len = int(np.max(track_lengths)) if track_lengths else 0

                if progress_cb:
                    progress_cb(4, 4, 'done', f'{n_tracks} tracks in {elapsed:.1f}s')

                print(f"[FASTIA] Tracking done — {n_tracks} tracks in {elapsed:.1f}s")

                return {
                    "status": "done",
                    "outputs": {
                        "n_tracks": n_tracks,
                        "n_detections": n_dets,
                        "n_frames": n_frames,
                        "mean_track_length": round(mean_len, 1),
                        "median_track_length": int(median_len),
                        "max_track_length": max_len,
                        "elapsed_s": round(elapsed, 1),
                        "message": f"Linked {n_tracks} tracks · mean {mean_len:.1f} frames · max {max_len} frames · {elapsed:.1f}s"
                    }
                }
            except ImportError as ie:
                return {"status": "error", "error_msg": f"FASTIA tracker not available: {ie}"}
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {"status": "error", "error_msg": str(e)}

        elif step_id == 'classification':
            print(f"[FASTIA] Classification — mode: {all_params.get('class_mode', '9G')}")

            try:
                import pickle
                import numpy as np
                import time as _time
                from wrapper_classes.fastia_class_clus import fastia_class_clus

                # Phase 1: Load required data
                if progress_cb:
                    progress_cb(0, 5, 'loading', 'Loading tracks and detection results...')

                det_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')
                track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')

                tracks_pkl = track_dir / 'tracks.pkl'
                if not tracks_pkl.exists():
                    return {"status": "error", "error_msg": "No tracking results found. Run tracking first."}
                with open(str(tracks_pkl), 'rb') as f:
                    tracks = pickle.load(f)

                labels_path = det_dir / 'all_labels.npy'
                all_labels = list(np.load(str(labels_path), allow_pickle=True)) if labels_path.exists() else None

                cell_mask_path = det_dir / 'cell_mask_3d.npy'
                cell_mask = np.load(str(cell_mask_path)) if cell_mask_path.exists() else None

                if cancel_evt and cancel_evt.is_set():
                    return {"status": "cancelled", "outputs": {"message": "Cancelled before classification"}}

                # Phase 2: Load image stack
                if progress_cb:
                    progress_cb(1, 5, 'loading_stack', 'Loading image stack for feature extraction...')

                import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
                file_path = None
                ch_params_imp = {}
                for sk, sv in import_params.items():
                    if isinstance(sv, dict):
                        if 'input_file' in sv:
                            file_path = sv['input_file']
                        if 'ch1_name' in sv:
                            ch_params_imp = sv

                stack = None
                if file_path:
                    resolved = project.resolve_data_path(file_path)
                    if resolved:
                        import tifffile
                        cache_key = str(resolved)
                        if not hasattr(app, '_tiff_cache'):
                            app._tiff_cache = {}
                        if cache_key not in app._tiff_cache:
                            app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
                        raw = app._tiff_cache[cache_key]
                        det_ch = all_params.get('detection_channel', 'vinculin')
                        c_idx = 0
                        for i in range(1, 5):
                            if ch_params_imp.get(f'ch{i}_name', '').lower() == det_ch.lower():
                                c_idx = i - 1
                                break
                        stack = raw[:, c_idx, :, :] if raw.ndim == 4 else raw

                # Get imaging metadata
                pixel_size_um = None
                t_interval = None
                for sk, sv in import_params.items():
                    if isinstance(sv, dict):
                        if 'pixel_size_um' in sv:
                            try: pixel_size_um = float(sv['pixel_size_um'])
                            except: pass
                        if 't_interval' in sv:
                            try: t_interval = float(sv['t_interval'])
                            except: pass

                if cancel_evt and cancel_evt.is_set():
                    return {"status": "cancelled", "outputs": {"message": "Cancelled before feature extraction"}}

                # Phase 3: Run classification
                mode = all_params.get('class_mode', '9G')
                run_disc = str(all_params.get('run_discriminability', 'true')).lower() == 'true'
                n_tracks = len(tracks) if isinstance(tracks, list) else 0
                print(f"[FASTIA] Classification mode={mode}, tracks={n_tracks}, discriminability={run_disc}")

                if progress_cb:
                    progress_cb(2, 5, 'classifying', f'Extracting features & classifying {n_tracks} tracks ({mode})...')

                class_params = {k: v for k, v in all_params.items()
                                if k not in ('class_mode', 'run_discriminability', 'min_group_size', 'n_workers')}

                n_workers_class = int(all_params.get('n_workers', 0)) or None  # 0 = auto

                # Per-track progress wrapper for feature extraction
                def _class_progress(done, total):
                    if progress_cb:
                        pct = round(done / max(total, 1) * 100, 1)
                        progress_cb(done, total, 'feature_extraction',
                                    f'Feature extraction: {done}/{total} tracks ({pct}%)')

                t0 = _time.time()
                cc = fastia_class_clus(class_params)
                results = cc.classify(
                    mode=mode,
                    tracks=tracks,
                    stack=stack,
                    all_labels=all_labels,
                    cell_mask=cell_mask,
                    df_features=None,
                    feature_names=None,
                    pixel_size_um=pixel_size_um,
                    t_interval_seconds=t_interval,
                    run_discriminability=run_disc,
                    min_group_size=int(all_params.get('min_group_size', 5)),
                    n_workers=n_workers_class,
                    progress_cb=_class_progress,
                    cancel_evt=cancel_evt,
                )
                elapsed = _time.time() - t0

                if cancel_evt and cancel_evt.is_set():
                    return {"status": "cancelled", "outputs": {"message": "Cancelled during classification"}}

                # Phase 4: Save results
                if progress_cb:
                    progress_cb(4, 5, 'saving', 'Saving classification results...')

                import pandas as pd
                import json

                if results.get('df_features') is not None:
                    results['df_features'].to_csv(str(results_dir / 'df_features.csv'), index=False)
                if results.get('feature_matrix') is not None:
                    np.save(str(results_dir / 'feature_matrix.npy'), results['feature_matrix'])
                if results.get('feature_names') is not None:
                    with open(str(results_dir / 'feature_names.json'), 'w') as f:
                        json.dump(results['feature_names'], f)
                if results.get('df_classified') is not None:
                    results['df_classified'].to_csv(str(results_dir / 'df_classified.csv'), index=False)
                if results.get('discriminability') is not None:
                    results['discriminability'].to_csv(str(results_dir / 'discriminability.csv'), index=False)

                n_groups = len(results['df_classified']['group'].unique()) if results.get('df_classified') is not None and 'group' in results['df_classified'].columns else 0
                n_classified = len(results['df_classified']) if results.get('df_classified') is not None else 0
                n_features = len(results.get('feature_names', [])) if results.get('feature_names') else 0

                if progress_cb:
                    progress_cb(5, 5, 'done', f'{n_classified} tracks → {n_groups} groups in {elapsed:.1f}s')

                print(f"[FASTIA] Classification done — {n_classified} tracks into {n_groups} groups ({n_features} features) in {elapsed:.1f}s")

                return {
                    "status": "done",
                    "outputs": {
                        "n_classified": n_classified,
                        "n_groups": n_groups,
                        "n_features": n_features,
                        "mode": mode,
                        "elapsed_s": round(elapsed, 1),
                        "message": f"Classified {n_classified} tracks into {n_groups} groups ({mode}) · {n_features} features · {elapsed:.1f}s"
                    }
                }
            except ImportError as ie:
                return {"status": "error", "error_msg": f"FASTIA classifier not available: {ie}"}
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {"status": "error", "error_msg": str(e)}

        elif step_id == 'kinetics':
            return {
                "status": "error",
                "error_msg": "FASTIA kinetics backend not yet wired."
            }

        elif step_id == 'association':
            try:
                import time as _time
                import numpy as np
                from wrapper_classes.fastia_association import FASTIAAssociation

                # Build config from saved params (includes _run_params from POST body)
                all_params = {}
                for section_key, section_val in params.items():
                    if isinstance(section_val, dict):
                        all_params.update(section_val)

                print(f"[ASSOC] all_params: {list(all_params.keys())}")
                print(f"[ASSOC] run_mode={all_params.get('assoc_run_mode', 'NOT SET')} "
                      f"track={all_params.get('assoc_single_track_id', 'NOT SET')} "
                      f"channels={all_params.get('selected_channels', 'NOT SET')}")

                # Parse method selections
                methods_cfg = {}
                if all_params.get('run_correlation', 'true').lower() == 'true':
                    methods_cfg['pearson'] = {'signal_version': 'raw', 'n_surrogates': 0}
                if all_params.get('run_granger', 'true').lower() == 'true':
                    methods_cfg['granger_causality'] = {
                        'maxlag': int(all_params.get('granger_max_lag', 5)),
                        'signal_version': 'stationary',
                        'n_surrogates': 0,
                    }
                if all_params.get('run_ccm', 'true').lower() == 'true':
                    methods_cfg['ccm'] = {
                        'E': int(all_params.get('ccm_embedding_dim', 2)),
                        'tau': 1,
                        'lags': (-2, -1, 0, 1, 2),
                        'n_boot': 20,
                        'signal_version': 'raw',
                        'n_surrogates': int(all_params.get('n_surrogates', 100)),
                    }

                if not methods_cfg:
                    methods_cfg = {'ccm': {'n_surrogates': 100}, 'granger_causality': {}}

                # Surrogate toggle
                run_surrogates = all_params.get('run_surrogates', 'true').lower() == 'true'
                if not run_surrogates:
                    for m in methods_cfg.values():
                        m['n_surrogates'] = 0

                # Parse stationarizer config
                corr_method = all_params.get('corr_method', 'pearson')
                corr_window = int(all_params.get('corr_window', 10))

                assoc_config = {
                    'min_track_length': int(all_params.get('min_track_length', 10)),
                    'max_tracks': int(all_params.get('max_tracks', 0)),
                    'group_filter': None,
                    'channel_pairs': 'all',
                    'stationarizer': {
                        'method': all_params.get('stationarizer_method', 'bandpass'),
                        'sampling_rate': 0.1,
                        'bandpass_low': 0.008,
                        'bandpass_high': 0.25,
                    },
                    'surrogate': {
                        'method': all_params.get('surrogate_method', 'iaaft'),
                        'n_iterations': 100,
                    },
                    'methods': methods_cfg,
                    'seed': 42,
                }

                # Single track mode
                run_mode = all_params.get('assoc_run_mode', 'all')
                if run_mode == 'single':
                    assoc_config['max_tracks'] = 1
                    single_tid = all_params.get('assoc_single_track_id')
                    if single_tid:
                        try:
                            assoc_config['single_track_id'] = int(float(single_tid))
                        except:
                            pass

                # Channel pair filtering
                sel_ch = all_params.get('selected_channels', 'all')
                if sel_ch and sel_ch != 'all':
                    try:
                        ch_indices = [int(c) for c in sel_ch.split(',') if c.strip()]
                        if len(ch_indices) >= 2:
                            pairs = [(ch_indices[i], ch_indices[j])
                                     for i in range(len(ch_indices))
                                     for j in range(i + 1, len(ch_indices))]
                            assoc_config['channel_pairs'] = pairs
                    except:
                        pass

                if progress_cb:
                    progress_cb(0, 100, 'init', 'Initializing association analysis...')

                # Build cache from app-level caches to avoid reloading
                assoc_cache = {}
                cache_key_tiff = f"tiff_{ws_id}_{pipeline_id}"
                if hasattr(app, '_tiff_cache') and cache_key_tiff in app._tiff_cache:
                    assoc_cache['stack'] = app._tiff_cache[cache_key_tiff]
                    print('[ASSOC] Using cached TIFF stack')

                cache_key_lbl = f"labels:{ws_id}/{pipeline_id}"
                if hasattr(app, '_labels_cache') and cache_key_lbl in app._labels_cache:
                    assoc_cache['all_labels'] = app._labels_cache[cache_key_lbl]
                    print('[ASSOC] Using cached labels')

                cache_key_trk = f"tracks_{ws_id}_{pipeline_id}"
                if hasattr(app, '_tracks_cache') and cache_key_trk in app._tracks_cache:
                    assoc_cache['tracks'] = app._tracks_cache[cache_key_trk]
                    print('[ASSOC] Using cached tracks')

                assoc = FASTIAAssociation(project, ws_id, pipeline_id, assoc_config, cache=assoc_cache)

                # Adapt progress callback — use percentage for smooth updates
                def _assoc_progress(frac, msg):
                    if progress_cb:
                        pct = min(95, int(frac * 95))  # reserve 95-100 for saving
                        progress_cb(pct, 100, 'analyzing', msg)

                t0 = _time.time()
                result = assoc.run(progress_cb=_assoc_progress, cancel_evt=cancel_evt)
                elapsed = _time.time() - t0

                if 'error' in result:
                    return {"status": "error", "error_msg": result['error']}

                if cancel_evt and cancel_evt.is_set():
                    return {"status": "cancelled", "outputs": {"message": "Cancelled"}}

                # Save results
                if progress_cb:
                    progress_cb(96, 100, 'saving', 'Saving association results...')

                assoc.save_results(result)

                # Summary
                n_tracks = result['metadata']['n_tracks_analyzed']
                n_pairs = len(result['metadata']['channel_pairs'])
                n_methods = len(result['metadata']['methods'])

                # Count significant findings
                n_sig = 0
                n_total_tests = 0
                for pair_key, methods in result.get('population', {}).items():
                    for method, stats in methods.items():
                        n_sig += stats.get('n_significant', 0)
                        n_total_tests += stats.get('n_tracks', 0)

                if progress_cb:
                    progress_cb(100, 100, 'done',
                                f'{n_tracks} tracks × {n_pairs} pairs × {n_methods} methods · '
                                f'{n_sig}/{n_total_tests} significant · {elapsed:.1f}s')

                print(f"[FASTIA] Association done — {n_tracks} tracks, {n_pairs} pairs, "
                      f"{n_methods} methods, {n_sig}/{n_total_tests} significant, {elapsed:.1f}s")

                # Print detailed results per track (visible in run log)
                print(f"\n{'─'*60}")
                print(f"DETAILED RESULTS:")
                print(f"{'─'*60}")
                for tid, track_res in result.get('per_track', {}).items():
                    for pair_key, assoc_res in track_res.items():
                        if 'error' in assoc_res:
                            print(f"  Track {tid} · {pair_key}: ERROR — {assoc_res['error']}")
                            continue
                        print(f"\n  Track {tid} · {pair_key}:")
                        for row in assoc_res.get('summary', []):
                            if 'error' in row:
                                print(f"    {row['method']}: ERROR")
                                continue
                            stat = row.get('statistic', float('nan'))
                            p = row.get('p_best', float('nan'))
                            sig = '✓ SIG' if row.get('significant') else '  n.s.'
                            eff = row.get('effect_size', float('nan'))
                            ver = row.get('signal_version', '?')
                            stat_s = f'{stat:+.4f}' if np.isfinite(stat) else 'N/A'
                            p_s = f'{p:.4f}' if np.isfinite(p) else 'N/A'
                            eff_s = f'{eff:+.2f}' if np.isfinite(eff) else '—'
                            print(f"    {row['method']:24s} stat={stat_s:>8s}  p={p_s:>6s}  {sig}  effect={eff_s}  [{ver}]")
                print(f"{'─'*60}")

                # Auto-generate track detail plot for single-track runs
                if run_mode == 'single' and len(result.get('per_track', {})) == 1:
                    try:
                        from plotters.plot_association import fig_assoc_track_detail
                        tid = list(result['per_track'].keys())[0]
                        for pk, ar in result['per_track'][tid].items():
                            fig_detail = fig_assoc_track_detail(ar, tid, pk)
                            detail_path = results_dir / 'plots' / f'assoc_track_{tid}_{pk}.png'
                            detail_path.parent.mkdir(parents=True, exist_ok=True)
                            fig_detail.savefig(str(detail_path), dpi=100, bbox_inches='tight',
                                               facecolor='white', edgecolor='none')
                            plt.close(fig_detail)
                            print(f"[ASSOC] Auto-generated detail plot: {detail_path.name}")
                    except Exception as plot_err:
                        print(f"[ASSOC] Auto-plot failed: {plot_err}")

                return {
                    "status": "done",
                    "outputs": {
                        "n_tracks": n_tracks,
                        "n_pairs": n_pairs,
                        "n_methods": n_methods,
                        "n_significant": n_sig,
                        "n_total_tests": n_total_tests,
                        "elapsed_s": round(elapsed, 1),
                        "message": (f"Analyzed {n_tracks} tracks × {n_pairs} channel pairs × "
                                    f"{n_methods} methods · {n_sig}/{n_total_tests} significant · {elapsed:.1f}s"),
                    }
                }

            except ImportError as ie:
                import traceback
                traceback.print_exc()
                return {"status": "error", "error_msg": f"FASTIA association not available: {ie}"}
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {"status": "error", "error_msg": str(e)}

        else:
            return {"status": "error", "error_msg": f"Unknown FASTIA step: {step_id}"}

    except Exception as e:
        return {"status": "error", "error_msg": str(e)}


# ═════════════════════════════════════════════
# STEP / PARAMS ENDPOINTS
# ═════════════════════════════════════════════

@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/params', methods=['GET'])
def step_get_params(ws_id, pipeline_id, step_id):
    """Get parameters for a pipeline step."""
    try:
        project = get_project()
        params = project.load_params(ws_id, pipeline_id, step_id)
        return api_response(params)
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/params', methods=['POST'])
def step_save_params(ws_id, pipeline_id, step_id):
    """
    Save parameters for a pipeline step.
    Body: { "params": { "section_name": { ... } } }
    Merges with existing params so sections accumulate.
    """
    try:
        project = get_project()
        body = request.get_json()
        new_params = body.get('params', {})

        # Load existing params and merge — sections accumulate, not overwrite
        existing = project.load_params(ws_id, pipeline_id, step_id) or {}
        existing.update(new_params)

        project.save_params(ws_id, pipeline_id, step_id, existing)

        return api_response({"saved": True, "step_id": step_id})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/results/<path:filename>')
def step_get_result_file(ws_id, pipeline_id, step_id, filename):
    """Serve a result file (image, CSV, etc.) for display in frontend."""
    try:
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, step_id)
        return send_from_directory(str(results_dir), filename)
    except Exception as e:
        return api_error(str(e), 404)


@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/run_log', methods=['POST'])
def step_save_run_log(ws_id, pipeline_id, step_id):
    """Save run log HTML for cross-session persistence."""
    import json
    try:
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, step_id)
        body = request.get_json() or {}
        log_html = body.get('log_html', '')
        log_path = results_dir / 'run_log.json'
        with open(str(log_path), 'w') as f:
            json.dump({'log_html': log_html}, f)
        return api_response({"saved": True})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/pipeline/<ws_id>/<pipeline_id>/info', methods=['GET'])
def pipeline_info(ws_id, pipeline_id):
    """
    Return metadata about a pipeline for the Properties panel.
    Includes creation/modification dates, folder size, cache size, paths.
    """
    try:
        import os
        from datetime import datetime

        project = get_project()
        pipeline_dir = project.workspaces_dir / ws_id / pipeline_id
        
        if not pipeline_dir.exists():
            return api_error(f'Pipeline directory not found: {pipeline_id}', 404)

        # Folder size (recursive)
        total_size = 0
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(str(pipeline_dir)):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                    file_count += 1
                except OSError:
                    pass

        # Creation and modification times
        stat = pipeline_dir.stat()
        created = datetime.fromtimestamp(stat.st_ctime).isoformat()
        modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # Find most recent modification across all files
        latest_mod = stat.st_mtime
        for dirpath, dirnames, filenames in os.walk(str(pipeline_dir)):
            for f in filenames:
                try:
                    fp = os.path.join(dirpath, f)
                    mt = os.path.getmtime(fp)
                    if mt > latest_mod:
                        latest_mod = mt
                except OSError:
                    pass
        last_modified = datetime.fromtimestamp(latest_mod).isoformat()

        # TIFF cache size
        cache_size = 0
        cache_files = 0
        if hasattr(app, '_tiff_cache'):
            for k, v in app._tiff_cache.items():
                cache_size += v.nbytes if hasattr(v, 'nbytes') else 0
                cache_files += 1

        # Per-step sizes
        step_sizes = {}
        if pipeline_dir.exists():
            for step_dir in pipeline_dir.iterdir():
                if step_dir.is_dir():
                    s = sum(
                        f.stat().st_size for f in step_dir.rglob('*') if f.is_file()
                    )
                    step_sizes[step_dir.name] = s

        return api_response({
            'pipeline_id': pipeline_id,
            'path': str(pipeline_dir),
            'project_root': str(project.root),
            'created': created,
            'last_modified': last_modified,
            'total_size': total_size,
            'file_count': file_count,
            'cache_size': cache_size,
            'cache_files': cache_files,
            'step_sizes': step_sizes,
        })
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/detection/preview', methods=['GET'])
def fastia_detection_preview(ws_id, pipeline_id):
    """
    Run CellFADE on a single frame and return overlay image.
    Query params: ?frame=0&channel=vinculin
    """
    try:
        import tifffile
        import io
        from PIL import Image, ImageDraw
        import base64
        import numpy as np
        import time

        project = get_project()
        frame_idx = int(request.args.get('frame', 0))
        channel_name = request.args.get('channel', 'vinculin')

        # Load import params to get file path and channel mapping
        import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
        file_path = None
        ch_params = {}
        for sk, sv in import_params.items():
            if isinstance(sv, dict):
                if 'input_file' in sv:
                    file_path = sv['input_file']
                if 'ch1_name' in sv:
                    ch_params = sv

        if not file_path:
            return jsonify({'success': False, 'error': 'No movie loaded. Import a movie first.'})

        resolved = project.resolve_data_path(file_path)
        if resolved is None:
            return jsonify({'success': False, 'error': f'File not found: {file_path}'})

        # Find channel index
        ch_idx = 0
        for i in range(1, 5):
            if ch_params.get(f'ch{i}_name', '').lower() == channel_name.lower():
                ch_idx = i - 1
                break

        # Load from cache
        cache_key = str(resolved)
        if not hasattr(app, '_tiff_cache'):
            app._tiff_cache = {}
        if cache_key not in app._tiff_cache:
            app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
        stack = app._tiff_cache[cache_key]

        # Extract frame
        if stack.ndim == 4:
            frame = stack[min(frame_idx, stack.shape[0]-1), ch_idx]
        elif stack.ndim == 3:
            frame = stack[min(frame_idx, stack.shape[0]-1)]
        else:
            return jsonify({'success': False, 'error': f'Unsupported shape: {stack.shape}'})

        t0 = time.time()

        # Try running CellFADE detection
        try:
            from wrapper_classes.fastia_detector import fastia_detector
            from components.cell_mask import segment_cell_frame
            from skimage.filters import gaussian as _gauss, threshold_otsu as _otsu

            det_params_raw = project.load_params(ws_id, pipeline_id, 'detection') or {}
            det_params = {}
            seg_params = {}
            for sk, sv in det_params_raw.items():
                if isinstance(sv, dict):
                    if 'seg_method' in sv or 'seg_channel' in sv:
                        seg_params.update(sv)
                    else:
                        det_params.update(sv)

            # --- Compute cell mask for this frame ---
            cell_mask = None
            n_excluded = 0
            try:
                seg_ch_name = seg_params.get('seg_channel', channel_name)
                seg_ch_idx = ch_idx
                for i in range(1, 5):
                    if ch_params.get(f'ch{i}_name', '').lower() == seg_ch_name.lower():
                        seg_ch_idx = i - 1
                        break
                if stack.ndim == 4:
                    seg_frame = stack[min(frame_idx, stack.shape[0]-1), seg_ch_idx]
                    seg_ch_stack = stack[:, seg_ch_idx, :, :]
                else:
                    seg_frame = frame
                    seg_ch_stack = stack

                smooth_sigma = float(seg_params.get('smooth_sigma', 5))
                method = seg_params.get('seg_method', 'otsu')
                global_threshold = str(seg_params.get('global_threshold', 'true')).lower() == 'true'
                keep_largest = str(seg_params.get('keep_largest', 'true')).lower() == 'true'
                manual_threshold_str = seg_params.get('manual_threshold', '')
                manual_thresh = float(manual_threshold_str) if manual_threshold_str else None
                i_min_str = seg_params.get('intensity_min', '')
                i_min = float(i_min_str) if i_min_str else None
                if i_min is not None and i_min <= 0: i_min = None
                i_max_str = seg_params.get('intensity_max', '')
                i_max = float(i_max_str) if i_max_str else None
                if i_max is not None and i_max <= 0: i_max = None

                # Compute threshold
                if method == 'manual' and manual_thresh is not None:
                    thresh = manual_thresh
                elif global_threshold:
                    max_proj = np.max(seg_ch_stack.astype(np.float32), axis=0)
                    work = max_proj.copy()
                    if i_min is not None: work[work < i_min] = 0
                    if i_max is not None: work[work > i_max] = i_max
                    thresh = float(_otsu(_gauss(work, sigma=smooth_sigma)))
                else:
                    thresh = None  # per-frame

                cell_mask = segment_cell_frame(
                    seg_frame, threshold=thresh, smooth_sigma=smooth_sigma,
                    keep_largest=keep_largest,
                    intensity_min=i_min, intensity_max=i_max)
            except Exception as seg_err:
                print(f"[FASTIA] Cell seg warning in preview: {seg_err}")
                cell_mask = None

            # --- Run FA detection with cell mask filtering ---
            detector = fastia_detector(det_params)
            labels, detections = detector.detect_frame(frame, cell_mask=cell_mask)
            n_det = len(detections)
            elapsed = round(time.time() - t0, 2)

            # Create overlay: normalize frame + colored FA labels
            frame_f = frame.astype(np.float32)
            p_low = np.percentile(frame_f, 0.5)
            p_high = np.percentile(frame_f, 99.5)
            if p_high > p_low:
                frame_norm = np.clip((frame_f - p_low) / (p_high - p_low) * 255, 0, 255).astype(np.uint8)
            else:
                frame_norm = np.zeros(frame.shape, dtype=np.uint8)

            # Convert to RGB for overlay
            rgb = np.stack([frame_norm, frame_norm, frame_norm], axis=-1).astype(np.float32)

            # Draw each FA body with a unique color
            from scipy import ndimage
            if labels is not None and labels.max() > 0:
                n_labels = int(labels.max())
                # Generate distinct colors using golden ratio hue spacing
                colors = []
                for i in range(n_labels):
                    hue = (i * 0.618033988749895) % 1.0
                    # HSV to RGB (saturation=0.8, value=1.0)
                    h = hue * 6.0
                    c = 0.8
                    x = c * (1 - abs(h % 2 - 1))
                    if h < 1:   r, g, b = c, x, 0
                    elif h < 2: r, g, b = x, c, 0
                    elif h < 3: r, g, b = 0, c, x
                    elif h < 4: r, g, b = 0, x, c
                    elif h < 5: r, g, b = x, 0, c
                    else:       r, g, b = c, 0, x
                    colors.append((int(r*255), int(g*255), int(b*255)))

                # Fill FA bodies with semi-transparent color overlay
                alpha = 0.45
                for label_id in range(1, n_labels + 1):
                    mask = labels == label_id
                    if not mask.any():
                        continue
                    color = colors[(label_id - 1) % len(colors)]
                    for ch_i in range(3):
                        rgb[mask, ch_i] = rgb[mask, ch_i] * (1 - alpha) + color[ch_i] * alpha

                # Draw bright outlines on boundaries
                eroded = ndimage.binary_erosion(labels > 0)
                boundaries = (labels > 0) & ~eroded
                for label_id in range(1, n_labels + 1):
                    boundary_mask = boundaries & (labels == label_id)
                    if not boundary_mask.any():
                        continue
                    color = colors[(label_id - 1) % len(colors)]
                    for ch_i in range(3):
                        rgb[boundary_mask, ch_i] = color[ch_i]

            rgb = np.clip(rgb, 0, 255).astype(np.uint8)

            # Encode
            img = Image.fromarray(rgb)
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=90)
            b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

            return jsonify({
                'success': True,
                'image': f'data:image/jpeg;base64,{b64}',
                'n_detections': n_det,
                'elapsed': elapsed,
                'frame': frame_idx,
            })

        except ImportError as ie:
            # CellFADE not available — return raw frame with message
            frame_f = frame.astype(np.float32)
            p_low = np.percentile(frame_f, 0.5)
            p_high = np.percentile(frame_f, 99.5)
            if p_high > p_low:
                frame_norm = np.clip((frame_f - p_low) / (p_high - p_low) * 255, 0, 255).astype(np.uint8)
            else:
                frame_norm = np.zeros(frame.shape, dtype=np.uint8)

            img = Image.fromarray(frame_norm)
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

            return jsonify({
                'success': True,
                'image': f'data:image/jpeg;base64,{b64}',
                'n_detections': 0,
                'elapsed': round(time.time() - t0, 2),
                'frame': frame_idx,
                'warning': f'CellFADE not available ({ie}). Showing raw frame.',
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/step/<ws_id>/<pipeline_id>/detection/cell_seg_preview', methods=['GET'])
def fastia_cell_seg_preview(ws_id, pipeline_id):
    """
    Run cell segmentation on a single frame and return overlay image.
    Query params: ?frame=0&channel=vinculin&smooth_sigma=5&method=otsu
                  &global_threshold=true&keep_largest=true
                  &manual_threshold=&intensity_min=&intensity_max=
    """
    try:
        import tifffile
        import io
        from PIL import Image
        import base64
        import numpy as np
        import time
        from scipy import ndimage

        project = get_project()
        frame_idx = int(request.args.get('frame', 0))
        channel_name = request.args.get('channel', 'vinculin')
        smooth_sigma = float(request.args.get('smooth_sigma', 5))
        method = request.args.get('method', 'otsu')
        global_threshold = request.args.get('global_threshold', 'true').lower() == 'true'
        keep_largest = request.args.get('keep_largest', 'true').lower() == 'true'

        # Optional params
        manual_threshold = request.args.get('manual_threshold', '')
        manual_threshold = float(manual_threshold) if manual_threshold else None
        intensity_min = request.args.get('intensity_min', '')
        intensity_min = float(intensity_min) if intensity_min else None
        if intensity_min is not None and intensity_min <= 0:
            intensity_min = None
        intensity_max = request.args.get('intensity_max', '')
        intensity_max = float(intensity_max) if intensity_max else None
        if intensity_max is not None and intensity_max <= 0:
            intensity_max = None

        # Load import params to get file path and channel mapping
        import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
        file_path = None
        ch_params = {}
        for sk, sv in import_params.items():
            if isinstance(sv, dict):
                if 'input_file' in sv:
                    file_path = sv['input_file']
                if 'ch1_name' in sv:
                    ch_params = sv

        if not file_path:
            return jsonify({'success': False, 'error': 'No movie loaded. Import a movie first.'})

        resolved = project.resolve_data_path(file_path)
        if resolved is None:
            return jsonify({'success': False, 'error': f'File not found: {file_path}'})

        # Find channel index
        ch_idx = 0
        for i in range(1, 5):
            if ch_params.get(f'ch{i}_name', '').lower() == channel_name.lower():
                ch_idx = i - 1
                break

        # Load from cache
        cache_key = str(resolved)
        if not hasattr(app, '_tiff_cache'):
            app._tiff_cache = {}
        if cache_key not in app._tiff_cache:
            app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
        stack = app._tiff_cache[cache_key]

        # Extract frame and channel stack (for global threshold)
        if stack.ndim == 4:
            frame = stack[min(frame_idx, stack.shape[0]-1), ch_idx]
            ch_stack = stack[:, ch_idx, :, :]
        elif stack.ndim == 3:
            frame = stack[min(frame_idx, stack.shape[0]-1)]
            ch_stack = stack
        else:
            return jsonify({'success': False, 'error': f'Unsupported shape: {stack.shape}'})

        t0 = time.time()

        # --- Call backend component ---
        from components.cell_mask import segment_cell_frame

        if method == 'manual' and manual_threshold is not None:
            # Manual: use threshold directly on this frame
            cell_mask = segment_cell_frame(
                frame, threshold=manual_threshold, smooth_sigma=smooth_sigma,
                keep_largest=keep_largest,
                intensity_min=intensity_min, intensity_max=intensity_max)
            thresh = manual_threshold
        elif global_threshold:
            # Global Otsu: compute threshold from max projection, apply to this frame
            from skimage.filters import gaussian as _gauss, threshold_otsu as _otsu
            max_proj = np.max(ch_stack.astype(np.float32), axis=0)
            work = max_proj.copy()
            if intensity_min is not None:
                work[work < intensity_min] = 0
            if intensity_max is not None:
                work[work > intensity_max] = intensity_max
            smoothed_proj = _gauss(work, sigma=smooth_sigma)
            thresh = float(_otsu(smoothed_proj))
            cell_mask = segment_cell_frame(
                frame, threshold=thresh, smooth_sigma=smooth_sigma,
                keep_largest=keep_largest,
                intensity_min=intensity_min, intensity_max=intensity_max)
        else:
            # Per-frame Otsu
            cell_mask = segment_cell_frame(
                frame, threshold=None, smooth_sigma=smooth_sigma,
                keep_largest=keep_largest,
                intensity_min=intensity_min, intensity_max=intensity_max)
            from skimage.filters import gaussian as _gauss, threshold_otsu as _otsu
            thresh = float(_otsu(_gauss(frame.astype(np.float32), sigma=smooth_sigma)))

        # Count objects before keep-largest (for info display)
        # Re-run without keep_largest to count all components
        from scipy.ndimage import label as _ndi_label
        full_mask = segment_cell_frame(
            frame, threshold=thresh, smooth_sigma=smooth_sigma,
            keep_largest=False,
            intensity_min=intensity_min, intensity_max=intensity_max)
        _, n_objects = _ndi_label(full_mask)

        elapsed = round(time.time() - t0, 3)

        # --- Build overlay: frame + green mask boundary + semi-transparent fill ---
        frame_f = frame.astype(np.float32)
        p_low = np.percentile(frame_f, 0.5)
        p_high = np.percentile(frame_f, 99.5)
        if p_high > p_low:
            frame_norm = np.clip((frame_f - p_low) / (p_high - p_low) * 255, 0, 255).astype(np.uint8)
        else:
            frame_norm = np.zeros(frame.shape, dtype=np.uint8)

        rgb = np.stack([frame_norm, frame_norm, frame_norm], axis=-1).astype(np.float32)

        # Semi-transparent green fill inside cell
        cell_color = (0, 200, 80)  # green
        alpha_fill = 0.2
        for ch_i in range(3):
            rgb[cell_mask, ch_i] = rgb[cell_mask, ch_i] * (1 - alpha_fill) + cell_color[ch_i] * alpha_fill

        # Bright green boundary outline
        eroded = ndimage.binary_erosion(cell_mask, iterations=2)
        boundary = cell_mask & ~eroded
        for ch_i in range(3):
            rgb[boundary, ch_i] = cell_color[ch_i]

        # Dim area outside cell
        outside = ~cell_mask
        rgb[outside] = rgb[outside] * 0.4

        rgb = np.clip(rgb, 0, 255).astype(np.uint8)

        # Encode
        img = Image.fromarray(rgb)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=90)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        cell_area_px = int(np.sum(cell_mask))
        info_parts = [f"{method}"]
        if thresh is not None:
            info_parts.append(f"T={thresh:.1f}")
        info_parts.append(f"Cell: {cell_area_px:,} px")
        if keep_largest and n_objects > 1:
            info_parts.append(f"kept largest of {n_objects}")
        info_parts.append(f"{elapsed}s")
        info_str = ' · '.join(info_parts)

        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{b64}',
            'info': info_str,
            'cell_area_px': cell_area_px,
            'n_objects': n_objects,
            'threshold': float(thresh) if thresh else None,
            'elapsed': elapsed,
            'frame': frame_idx,
            'method': method,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/step/<ws_id>/<pipeline_id>/detection/results_frame', methods=['GET'])
def fastia_detection_results_frame(ws_id, pipeline_id):
    """
    Serve a detection results overlay frame from SAVED results (fast — no re-running).
    Composites: raw frame + cell mask (green tint + boundary) + FA labels (colored).
    Query params: ?frame=0&channel=vinculin
    """
    try:
        import tifffile
        import io, time
        from PIL import Image
        import base64
        import numpy as np
        import pickle
        from scipy import ndimage

        project = get_project()
        frame_idx = int(request.args.get('frame', 0))
        channel_name = request.args.get('channel', 'vinculin')

        # Load import params
        import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
        file_path = None
        ch_params = {}
        for sk, sv in import_params.items():
            if isinstance(sv, dict):
                if 'input_file' in sv: file_path = sv['input_file']
                if 'ch1_name' in sv: ch_params = sv

        if not file_path:
            return jsonify({'success': False, 'error': 'No movie loaded'})

        resolved = project.resolve_data_path(file_path)
        if resolved is None:
            return jsonify({'success': False, 'error': f'File not found: {file_path}'})

        # Channel index
        ch_idx = 0
        for i in range(1, 5):
            if ch_params.get(f'ch{i}_name', '').lower() == channel_name.lower():
                ch_idx = i - 1
                break

        # Load stack from cache
        cache_key = str(resolved)
        if not hasattr(app, '_tiff_cache'):
            app._tiff_cache = {}
        if cache_key not in app._tiff_cache:
            app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
        stack = app._tiff_cache[cache_key]

        if stack.ndim == 4:
            frame = stack[min(frame_idx, stack.shape[0]-1), ch_idx]
        elif stack.ndim == 3:
            frame = stack[min(frame_idx, stack.shape[0]-1)]
        else:
            return jsonify({'success': False, 'error': f'Unsupported shape: {stack.shape}'})

        # --- Load saved results ---
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')

        labels = None
        labels_path = results_dir / 'all_labels.npy'
        if labels_path.exists():
            # Cache labels in memory for fast scrubbing
            cache_lbl_key = f"labels:{ws_id}/{pipeline_id}"
            if not hasattr(app, '_labels_cache'):
                app._labels_cache = {}
            if cache_lbl_key not in app._labels_cache:
                t0 = time.time()
                app._labels_cache[cache_lbl_key] = list(np.load(str(labels_path), allow_pickle=True))
                print(f"[results_frame] Labels loaded in {time.time()-t0:.1f}s")
            all_labels = app._labels_cache[cache_lbl_key]
            if frame_idx < len(all_labels):
                labels = all_labels[frame_idx]

        cell_mask = None
        mask_path = results_dir / 'cell_mask_3d.npy'
        if mask_path.exists():
            cache_mask_key = f"cellmask:{ws_id}/{pipeline_id}"
            if not hasattr(app, '_mask_cache'):
                app._mask_cache = {}
            if cache_mask_key not in app._mask_cache:
                app._mask_cache[cache_mask_key] = np.load(str(mask_path))
            cell_mask_3d = app._mask_cache[cache_mask_key]
            if frame_idx < cell_mask_3d.shape[0]:
                cell_mask = cell_mask_3d[frame_idx]

        if labels is None:
            return jsonify({'success': False, 'error': 'No detection results. Run Full Stack first.'})

        # --- Check rendered frame cache (instant on re-visit) ---
        if not hasattr(app, '_rendered_cache'):
            app._rendered_cache = {}
        render_key = f"{ws_id}/{pipeline_id}/{frame_idx}"
        cached = app._rendered_cache.get(render_key)
        if cached:
            return jsonify(cached)

        _t0 = time.time()

        # --- Build composite overlay ---
        frame_f = frame.astype(np.float32)
        p_low = np.percentile(frame_f, 0.5)
        p_high = np.percentile(frame_f, 99.5)
        if p_high > p_low:
            frame_norm = np.clip((frame_f - p_low) / (p_high - p_low) * 255, 0, 255).astype(np.uint8)
        else:
            frame_norm = np.zeros(frame.shape, dtype=np.uint8)

        rgb = np.stack([frame_norm, frame_norm, frame_norm], axis=-1).astype(np.float32)

        # Layer 1: Cell mask (subtle green tint + boundary)
        if cell_mask is not None:
            # Dim outside cell
            outside = ~cell_mask
            rgb[outside] = rgb[outside] * 0.35

            # Subtle green tint inside
            cell_color = (0, 180, 70)
            alpha_cell = 0.08
            for ch_i in range(3):
                rgb[cell_mask, ch_i] = rgb[cell_mask, ch_i] * (1 - alpha_cell) + cell_color[ch_i] * alpha_cell

            # Cell boundary (thin green line)
            eroded = ndimage.binary_erosion(cell_mask, iterations=1)
            cell_boundary = cell_mask & ~eroded
            for ch_i in range(3):
                rgb[cell_boundary, ch_i] = cell_color[ch_i] * 0.7

        # Layer 2: FA labels (colored bodies + outlines) — VECTORIZED
        n_fa = 0
        if labels is not None and int(labels.max()) > 0:
            n_labels = int(labels.max())
            n_fa = n_labels

            # Build color LUT: shape (n_labels+1, 3), index 0 = background (black)
            lut = np.zeros((n_labels + 1, 3), dtype=np.float32)
            for i in range(1, n_labels + 1):
                hue = ((i - 1) * 0.618033988749895) % 1.0
                h = hue * 6.0
                c = 0.8
                x = c * (1 - abs(h % 2 - 1))
                if h < 1:   r, g, b = c, x, 0
                elif h < 2: r, g, b = x, c, 0
                elif h < 3: r, g, b = 0, c, x
                elif h < 4: r, g, b = 0, x, c
                elif h < 5: r, g, b = x, 0, c
                else:       r, g, b = c, 0, x
                lut[i] = (r * 255, g * 255, b * 255)

            # Vectorized color overlay: one operation for ALL labels at once
            labels_int = labels.astype(np.int32)
            fg_mask = labels_int > 0  # boolean H×W
            alpha = 0.45
            label_colors = lut[labels_int]  # H×W×3 — maps each pixel to its label's color
            rgb[fg_mask] = rgb[fg_mask] * (1 - alpha) + label_colors[fg_mask] * alpha

            # Vectorized boundaries: erode the binary fg mask, XOR for edges
            eroded_fa = ndimage.binary_erosion(fg_mask)
            boundaries_fa = fg_mask & ~eroded_fa
            rgb[boundaries_fa] = label_colors[boundaries_fa]

        rgb = np.clip(rgb, 0, 255).astype(np.uint8)

        img = Image.fromarray(rgb)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85, optimize=False)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        _elapsed = time.time() - _t0

        result = {
            'success': True,
            'image': f'data:image/jpeg;base64,{b64}',
            'frame': frame_idx,
            'n_fa': n_fa,
            'has_cell_mask': cell_mask is not None,
        }

        # Cache for instant replay (limit ~200 frames to avoid memory blow-up)
        if len(app._rendered_cache) < 200:
            app._rendered_cache[render_key] = result

        if _elapsed > 0.5:
            print(f"[results_frame] Frame {frame_idx}: {_elapsed:.2f}s ({n_fa} FAs)")

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})



@app.route('/api/step/<ws_id>/<pipeline_id>/tracking/results_frame', methods=['GET'])
def fastia_tracking_results_frame(ws_id, pipeline_id):
    """
    Serve a tracking trajectory overlay frame from SAVED results.
    Composites: raw frame + track paths up to current frame + current position dots.
    Query params: ?frame=0&channel=vinculin
    """
    try:
        import tifffile
        import io, time
        from PIL import Image, ImageDraw
        import base64
        import numpy as np
        import pickle

        project = get_project()
        frame_idx = int(request.args.get('frame', 0))
        channel_name = request.args.get('channel', 'vinculin')

        # --- Check rendered cache first ---
        if not hasattr(app, '_track_render_cache'):
            app._track_render_cache = {}
        render_key = f"track:{ws_id}/{pipeline_id}/{frame_idx}"
        cached = app._track_render_cache.get(render_key)
        if cached:
            return jsonify(cached)

        t0 = time.time()

        # --- Load stack ---
        import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
        file_path = None
        ch_params = {}
        for sk, sv in import_params.items():
            if isinstance(sv, dict):
                if 'input_file' in sv: file_path = sv['input_file']
                if 'ch1_name' in sv: ch_params = sv

        if not file_path:
            return jsonify({'success': False, 'error': 'No movie loaded'})

        resolved = project.resolve_data_path(file_path)
        if resolved is None:
            return jsonify({'success': False, 'error': f'File not found: {file_path}'})

        ch_idx = 0
        for i in range(1, 5):
            if ch_params.get(f'ch{i}_name', '').lower() == channel_name.lower():
                ch_idx = i - 1
                break

        cache_key = str(resolved)
        if not hasattr(app, '_tiff_cache'):
            app._tiff_cache = {}
        if cache_key not in app._tiff_cache:
            app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
        stack = app._tiff_cache[cache_key]

        if stack.ndim == 4:
            frame = stack[min(frame_idx, stack.shape[0]-1), ch_idx]
        elif stack.ndim == 3:
            frame = stack[min(frame_idx, stack.shape[0]-1)]
        else:
            return jsonify({'success': False, 'error': f'Unsupported shape: {stack.shape}'})

        # --- Load tracks ---
        track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')
        tracks_path = track_dir / 'tracks.pkl'
        if not tracks_path.exists():
            return jsonify({'success': False, 'error': 'No tracking results. Run Tracking first.'})

        cache_trk_key = f"tracks:{ws_id}/{pipeline_id}"
        if not hasattr(app, '_tracks_cache'):
            app._tracks_cache = {}
        if cache_trk_key not in app._tracks_cache:
            with open(str(tracks_path), 'rb') as f:
                app._tracks_cache[cache_trk_key] = pickle.load(f)
        tracks = app._tracks_cache[cache_trk_key]

        # --- Build per-frame track index (cached) ---
        idx_key = f"track_idx:{ws_id}/{pipeline_id}"
        if not hasattr(app, '_track_index'):
            app._track_index = {}
        if idx_key not in app._track_index:
            # For each track, store (track_idx, list of (frame, cx, cy))
            track_paths = []
            for ti, track in enumerate(tracks):
                path = []
                for det in sorted(track, key=lambda d: d['frame']):
                    cy, cx = det['centroid']
                    path.append((int(det['frame']), float(cx), float(cy)))
                track_paths.append(path)
            app._track_index[idx_key] = track_paths
        track_paths = app._track_index[idx_key]

        # --- Normalize raw frame ---
        frame_f = frame.astype(np.float32)
        p_low, p_high = np.percentile(frame_f, [0.5, 99.5])
        if p_high > p_low:
            frame_norm = np.clip((frame_f - p_low) / (p_high - p_low) * 255, 0, 255).astype(np.uint8)
        else:
            frame_norm = np.zeros(frame.shape, dtype=np.uint8)

        # Convert to RGB PIL image
        rgb = np.stack([frame_norm, frame_norm, frame_norm], axis=-1)
        img = Image.fromarray(rgb)
        draw = ImageDraw.Draw(img)

        # --- Draw track paths using PIL (fast) ---
        # Color palette: golden ratio hue spacing
        n_colors = 64
        palette = []
        for i in range(n_colors):
            hue = (i * 0.618033988749895) % 1.0
            h = hue * 6.0
            c = 0.85
            x = c * (1 - abs(h % 2 - 1))
            if h < 1:   r, g, b = c, x, 0
            elif h < 2: r, g, b = x, c, 0
            elif h < 3: r, g, b = 0, c, x
            elif h < 4: r, g, b = 0, x, c
            elif h < 5: r, g, b = x, 0, c
            else:       r, g, b = c, 0, x
            palette.append((int(r*255), int(g*255), int(b*255)))

        n_active = 0
        for ti, path in enumerate(track_paths):
            # Get points up to current frame
            pts = [(cx, cy) for (f, cx, cy) in path if f <= frame_idx]
            if len(pts) < 1:
                continue

            color = palette[ti % n_colors]

            # Draw path line
            if len(pts) >= 2:
                draw.line(pts, fill=color, width=1)

            # Draw current position dot
            last = pts[-1]
            r = 2
            draw.ellipse([last[0]-r, last[1]-r, last[0]+r, last[1]+r],
                         fill=color, outline=(255, 255, 255))
            n_active += 1

        # --- Encode JPEG ---
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85, optimize=False)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        elapsed = time.time() - t0

        result = {
            'success': True,
            'image': f'data:image/jpeg;base64,{b64}',
            'frame': frame_idx,
            'n_active': n_active,
            'n_tracks': len(tracks),
        }

        # Cache (limit 200 frames)
        if len(app._track_render_cache) < 200:
            app._track_render_cache[render_key] = result

        if elapsed > 0.5:
            print(f"[track_frame] Frame {frame_idx}: {elapsed:.2f}s ({n_active} active tracks)")

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/preview_frame', methods=['GET'])
def step_preview_frame(ws_id, pipeline_id, step_id):
    """
    Serve a single frame from a TIFF stack as JPEG for the movie player.
    Query params: ?frame=0&channel=0&channels=0,1,2
    Caches the TIFF stack in memory after first load for fast scrubbing.
    """
    try:
        import tifffile
        import io
        from PIL import Image
        import base64
        import numpy as np

        project = get_project()
        params = project.load_params(ws_id, pipeline_id, step_id) or {}
        print(f"[preview_frame] params keys: {list(params.keys())}")
        print(f"[preview_frame] full params: {json.dumps({k: v for k, v in params.items() if k != '__pycache__'}, default=str)[:500]}")

        # Get file path from saved params — search all sections
        file_path = None
        for section_key, section in params.items():
            if isinstance(section, dict) and 'input_file' in section:
                file_path = section['input_file']
                print(f"[preview_frame] found input_file in section '{section_key}': {file_path}")
                break
            elif section_key == 'input_file':
                file_path = section
                print(f"[preview_frame] found input_file as top-level key: {file_path}")
        if not file_path:
            file_path = params.get('input_file')
            print(f"[preview_frame] fallback get: {file_path}")

        if not file_path:
            return jsonify({'success': False, 'error': 'No movie file loaded. Select a file first.'})

        # Resolve relative path against project root (same as Cornealia)
        resolved = project.resolve_data_path(file_path)
        print(f"[preview_frame] resolved: {resolved}")
        if resolved is None:
            return jsonify({'success': False, 'error': f'File not found: {file_path}'})

        frame_idx = int(request.args.get('frame', 0))
        channel_idx = int(request.args.get('channel', -1))  # -1 = composite
        channels_str = request.args.get('channels', '')  # comma-separated visible channels for composite
        visible_channels = [int(c) for c in channels_str.split(',') if c.strip().isdigit()] if channels_str else None

        # B&C: manual min/max override
        vmin_param = request.args.get('vmin')
        vmax_param = request.args.get('vmax')
        has_manual_bc = vmin_param is not None and vmax_param is not None
        if has_manual_bc:
            vmin_val = float(vmin_param)
            vmax_val = float(vmax_param)

        # Stats mode: return histogram info without frame image
        want_stats = request.args.get('stats') == '1'

        # ── Cache the TIFF stack in memory after first load ──
        cache_key = str(resolved)
        if not hasattr(app, '_tiff_cache'):
            app._tiff_cache = {}
        if cache_key not in app._tiff_cache:
            print(f"[preview_frame] Loading TIFF into cache: {resolved}")
            app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
        stack = app._tiff_cache[cache_key]
        # Handle shapes: [T,H,W], [T,C,H,W], [C,T,H,W]
        if stack.ndim == 3:
            n_frames = stack.shape[0]
            frame_idx = min(frame_idx, n_frames - 1)
            frame = stack[frame_idx]
            n_channels = 1
        elif stack.ndim == 4:
            n_frames = stack.shape[0]
            n_channels = stack.shape[1]
            frame_idx = min(frame_idx, n_frames - 1)
            if channel_idx >= 0 and channel_idx < n_channels:
                # Single channel mode — grayscale
                frame = stack[frame_idx, channel_idx]
            else:
                # Composite: map visible channels to their natural RGB position
                h, w = stack.shape[2], stack.shape[3]
                rgb = np.zeros((h, w, 3), dtype=np.float32)
                ch_indices = visible_channels if visible_channels else list(range(min(n_channels, 4)))
                for ci in ch_indices:
                    if ci >= n_channels:
                        continue
                    ch_data = stack[frame_idx, ci].astype(np.float32)
                    if has_manual_bc:
                        p_low, p_high = vmin_val, vmax_val
                    else:
                        p_low = np.percentile(ch_data, 0.5)
                        p_high = np.percentile(ch_data, 99.5)
                    if p_high > p_low:
                        ch_data = np.clip((ch_data - p_low) / (p_high - p_low), 0, 1)
                    else:
                        ch_data = np.zeros_like(ch_data)
                    if ci < 3:
                        rgb[:, :, ci] = ch_data
                    else:
                        # Channels 3+ rendered as white (add to all RGB)
                        rgb[:, :, 0] += ch_data
                        rgb[:, :, 1] += ch_data
                        rgb[:, :, 2] += ch_data
                rgb = np.clip(rgb, 0, 1)
                frame = (rgb * 255).astype(np.uint8)
        else:
            return jsonify({'success': False, 'error': f'Unsupported array shape: {stack.shape}'})

        # Normalize single-channel to 8-bit
        if frame.ndim == 2:
            frame = frame.astype(np.float32)
            if has_manual_bc:
                p_low, p_high = vmin_val, vmax_val
            else:
                p_low = np.percentile(frame, 0.5)
                p_high = np.percentile(frame, 99.5)
            if p_high > p_low:
                frame = np.clip((frame - p_low) / (p_high - p_low) * 255, 0, 255).astype(np.uint8)
            else:
                frame = np.zeros(frame.shape, dtype=np.uint8)

        # ── Stats mode: return histogram info ──
        stats_data = None
        if want_stats:
            if stack.ndim == 4:
                if channel_idx >= 0 and channel_idx < n_channels:
                    # Single channel stats
                    raw = stack[frame_idx, channel_idx].astype(np.float32)
                elif visible_channels:
                    # Stats across visible channels combined
                    raw = np.stack([stack[frame_idx, ci] for ci in visible_channels if ci < n_channels]).astype(np.float32)
                else:
                    raw = stack[frame_idx, 0].astype(np.float32)
            else:
                raw = stack[frame_idx].astype(np.float32)
            stats_data = {
                'min': float(np.min(raw)),
                'max': float(np.max(raw)),
                'mean': float(np.mean(raw)),
                'p05': float(np.percentile(raw, 0.5)),
                'p995': float(np.percentile(raw, 99.5)),
                'p1': float(np.percentile(raw, 1)),
                'p99': float(np.percentile(raw, 99)),
            }

        # ── JPEG encoding (much faster + smaller than PNG) ──
        img = Image.fromarray(frame)
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85, optimize=False)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{b64}',
            'frame': frame_idx,
            'n_frames': n_frames,
            'n_channels': n_channels,
            'shape': list(stack.shape),
            'stats': stats_data,
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/table', methods=['GET'])
def step_get_table(ws_id, pipeline_id, step_id):
    """Return CSV data as JSON table for frontend display."""
    try:
        import pandas as pd
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, step_id)
        csv_path = results_dir / "batch_results.csv"

        # Also check batch_run step
        if not csv_path.exists():
            batch_run_dir = project.get_results_dir(ws_id, pipeline_id, 'batch_run')
            csv_path = batch_run_dir / "batch_results.csv"

        if not csv_path.exists():
            return api_error("No batch results CSV found", 404)

        df = pd.read_csv(csv_path)

        # Round floats for display
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = df[col].round(4)

        return api_response({
            "columns": list(df.columns),
            "rows": df.to_dict('records'),
            "n_rows": len(df),
        })
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/plot', methods=['POST'])
def step_generate_plot(ws_id, pipeline_id, step_id):
    """
    Generate a specific plot on demand (ANSYS-style Insert Result).
    Body: { "plot_type": "segmentation" }
    """
    import io as _io
    body_raw = request.get_json()
    print(f"[PLOT] Request: {body_raw.get('plot_type','')} for {pipeline_id}/{step_id}")

    # ── CellADE module plots (base64, no project/disk) ──
    if step_id == 'cellade' and cellade_manager:
        try:
            plot_type = body_raw.get('plot_type', '')
            result = cellade_manager.plot(pipeline_id, plot_type)
            return api_response({'url': result['image'], 'filename': f'{plot_type}.png'})
        except Exception as e:
            traceback.print_exc()
            return api_error(str(e))

    # ── CellFADE module plots (base64, no project/disk) ──
    if step_id == 'cellfade' and cellfade_manager:
        try:
            plot_type = body_raw.get('plot_type', '')
            result = cellfade_manager.plot(pipeline_id, plot_type)
            return api_response({'url': result['image'], 'filename': f'{plot_type}.png'})
        except Exception as e:
            traceback.print_exc()
            return api_error(str(e))

    _old_stdout = sys.stdout
    _captured = _io.StringIO()
    sys.stdout = _captured
    try:
        import matplotlib.pyplot as plt
        import pickle

        project = get_project()
        body = body_raw
        plot_type = body.get('plot_type', '')
        print(f"[PLOT] Generating {plot_type} for {pipeline_id}/{step_id}")

        if not plot_type:
            return api_error("'plot_type' is required")

        pipeline = project.get_pipeline(ws_id, pipeline_id)
        p_type = pipeline.get('type', '')
        results_dir = project.get_results_dir(ws_id, pipeline_id, step_id)

        plots_dir = results_dir / "plots"
        plots_dir.mkdir(parents=True, exist_ok=True)
        print(f"Plots will be saved to: {plots_dir}")

        # ── CORNEALIA BATCH PLOTTER (CSV-based, no pickle) ──
        if p_type == 'cornealia_batch':
            batch_run_dir = project.get_results_dir(ws_id, pipeline_id, 'batch_run')
            csv_path = batch_run_dir / "batch_results.csv"

            if not csv_path.exists():
                return api_error("No batch CSV found. Run the batch first.", 404)

            # Ensure CSV has correct columns for batch plotter
            import pandas as pd
            df_check = pd.read_csv(csv_path)
            needs_save = False

            if 'Image_Name' not in df_check.columns and 'image_path' in df_check.columns:
                df_check['Image_Name'] = df_check['image_path'].apply(lambda p: os.path.basename(p) if isinstance(p, str) else p)
                df_check.drop(columns=['image_path'], inplace=True)
                needs_save = True

            if 'K' in df_check.columns and 'K_um' not in df_check.columns:
                try:
                    setup_params = project.load_params(ws_id, pipeline_id, 'batch_setup')
                    px = float(setup_params.get('pixel_size', 0.58))
                except:
                    px = 0.58
                px2 = px * px
                for col_src, col_dst in [('K','K_um'),('K_ds','K_ds_um'),('K_Vmin','K_Vmin_um'),('K_gpeak','K_gpeak_um'),
                                          ('K_quad_raw','K_quad_raw_um'),('K_morse_raw','K_morse_raw_um'),
                                          ('K_quad_guided','K_quad_guided_um'),('K_morse_guided','K_morse_guided_um')]:
                    if col_src in df_check.columns:
                        df_check[col_dst] = df_check[col_src] / px2
                if 'r0_fit' in df_check.columns:
                    df_check['r_0_um'] = df_check['r0_fit'] * px
                    df_check['r_0_px'] = df_check['r0_fit']
                needs_save = True
                print(f"  [BATCH] Added _um columns (pixel_size={px})")

            if needs_save:
                df_check.to_csv(csv_path, index=False)

            from cornealia.plotters.cornealia_batch_plotter import cornealia_batch_plotter

            _original_show = plt.show
            plt.show = lambda *a, **kw: None

            try:
                plotter = cornealia_batch_plotter(
                    str(csv_path), save=True,
                    save_dir=str(plots_dir), formats=('png',)
                )

                batch_plot_map = {
                    'distributions':           ('distributions',           '01_distributions.png'),
                    'histogram':               ('histogram',               '01_K_um_histogram.png'),
                    'as_vs_bs_boxplots':       ('as_vs_bs_boxplots',       '02_as_vs_bs_boxplots.png'),
                    'as_vs_bs_scatter':        ('as_vs_bs_scatter',        '03_as_vs_bs_scatter.png'),
                    'as_vs_bs_histograms':     ('as_vs_bs_histograms',     '04_as_vs_bs_histograms.png'),
                    'validation_scatter':      ('validation_scatter',      '07_validation_scatter.png'),
                    'validation_bland_altman': ('validation_bland_altman', '08_validation_bland_altman.png'),
                    'deep_dive':               ('deep_dive',               '06_K_um_deep_dive.png'),
                    'pub_boxplots':            ('pub_boxplots',            'fig2_as_vs_bs_boxplots.png'),
                    'pub_K_deep_dive':         ('pub_K_deep_dive',         'fig3_K_deep_dive.png'),
                    'pub_validation':          ('pub_validation',          'fig4_validation.png'),
                    'pub_K_independence':      ('pub_K_independence',      'fig6_K_independence.png'),
                    'pub_comprehensive':       ('pub_comprehensive',       None),
                }

                if plot_type not in batch_plot_map:
                    return api_error(f"Unknown batch plot: {plot_type}. Available: {list(batch_plot_map.keys())}")

                method_name, expected_filename = batch_plot_map[plot_type]
                method = getattr(plotter, method_name)
                print(f"Saved: {method_name} → generating...")
                method(save=True)
                plt.close('all')

                if expected_filename is None:
                    pngs = sorted(plots_dir.glob('fig_comprehensive_*.png'), key=lambda p: p.stat().st_mtime)
                    if pngs:
                        expected_filename = pngs[-1].name
                    else:
                        expected_filename = 'comprehensive.png'

                print(f"Saved: {method_name} → {expected_filename}")
                plot_url = f"/api/step/{ws_id}/{pipeline_id}/{step_id}/results/plots/{expected_filename}"

                sys.stdout = _old_stdout
                _log = _captured.getvalue()
                if _log: print(_log, end='')
                return api_response({
                    "plot_type": plot_type,
                    "filename": expected_filename,
                    "url": plot_url,
                    "log": _log,
                })

            except Exception as e:
                import traceback
                traceback.print_exc()
                sys.stdout = _old_stdout
                _log = _captured.getvalue()
                if _log: print(_log, end='')
                return api_error(f"Batch plot error: {str(e)}")
            finally:
                plt.show = _original_show
                plt.close('all')

        # ── FASTIA PLOTTERS ──
        if p_type == 'fastia':
            import numpy as np
            import tifffile

            _original_show = plt.show
            plt.show = lambda *a, **kw: None

            try:
                # Load the image stack
                import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
                file_path = None
                ch_params_plot = {}
                for sk, sv in import_params.items():
                    if isinstance(sv, dict):
                        if 'input_file' in sv: file_path = sv['input_file']
                        if 'ch1_name' in sv: ch_params_plot = sv

                stack = None
                if file_path:
                    resolved = project.resolve_data_path(file_path)
                    if resolved:
                        cache_key = str(resolved)
                        if not hasattr(app, '_tiff_cache'):
                            app._tiff_cache = {}
                        if cache_key not in app._tiff_cache:
                            app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
                        raw = app._tiff_cache[cache_key]

                        # Determine FA channel
                        det_params_all = project.load_params(ws_id, pipeline_id, 'detection') or {}
                        det_ch = 'vinculin'
                        for sk2, sv2 in det_params_all.items():
                            if isinstance(sv2, dict) and 'detection_channel' in sv2:
                                det_ch = sv2['detection_channel']
                        c_idx = 0
                        for i in range(1, 5):
                            if ch_params_plot.get(f'ch{i}_name', '').lower() == det_ch.lower():
                                c_idx = i - 1
                                break
                        stack = raw[:, c_idx, :, :] if raw.ndim == 4 else raw

                # Load detection results (cached for fast individual track inspection)
                det_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')
                if not hasattr(app, '_labels_cache'):
                    app._labels_cache = {}

                labels_cache_key = f"{ws_id}_{pipeline_id}_labels"
                labels_path = det_dir / 'all_labels.npy'
                if labels_cache_key in app._labels_cache:
                    all_labels = app._labels_cache[labels_cache_key]
                elif labels_path.exists():
                    all_labels = list(np.load(str(labels_path), allow_pickle=True))
                    app._labels_cache[labels_cache_key] = all_labels
                else:
                    all_labels = None

                all_detections = None
                det_pkl = det_dir / 'detections.pkl'
                if det_pkl.exists():
                    with open(str(det_pkl), 'rb') as f:
                        all_detections = pickle.load(f)

                cell_mask = None
                mask_path = det_dir / 'cell_mask_3d.npy'
                if mask_path.exists():
                    cell_mask = np.load(str(mask_path))

                plots_dir = results_dir / "plots"
                plots_dir.mkdir(parents=True, exist_ok=True)

                fig = None
                filename = None

                # --- Import step plots ---
                if step_id == 'import':
                    from plotters.plot_import import fig_frame_montage

                    if plot_type == 'frame_montage':
                        ch_name = det_ch if det_ch else 'Channel'
                        fig = fig_frame_montage(stack, channel_name=ch_name)
                        filename = 'frame_montage.png'

                # --- Detection step plots ---
                elif step_id == 'detection':
                    from plotters.plot_detection import (
                        fig_detection_montage, fig_detection_frame,
                        fig_cellmask_montage, fig_cellmask_frame
                    )

                    if plot_type == 'detection_montage':
                        fig = fig_detection_montage(stack, all_labels, all_detections)
                        filename = 'detection_montage.png'

                    elif plot_type == 'detection_frame':
                        frame_n = body.get('frame', 0)
                        fig = fig_detection_frame(stack, all_labels, all_detections,
                                                  frame=frame_n, cell_mask=cell_mask)
                        filename = f'detection_frame_{frame_n}.png'

                    elif plot_type == 'cellmask_montage':
                        if cell_mask is None:
                            return api_error("No cell mask. Run Full Stack first.")
                        fig = fig_cellmask_montage(stack, cell_mask)
                        filename = 'cellmask_montage.png'

                    elif plot_type == 'cellmask_frame':
                        frame_n = body.get('frame', 0)
                        if cell_mask is None:
                            return api_error("No cell mask. Run Full Stack first.")
                        fig = fig_cellmask_frame(stack, cell_mask,
                                                 all_labels=all_labels,
                                                 detections=all_detections,
                                                 frame=frame_n)
                        filename = f'cellmask_frame_{frame_n}.png'

                # --- Tracking step plots ---
                elif step_id == 'tracking':
                    from plotters.plot_tracking import (
                        fig_track_trajectories, fig_track_length_distribution,
                        fig_track_displacement, fig_track_lifetime_map,
                        fig_track_summary
                    )

                    # Load tracks
                    track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')
                    tracks = None
                    tracks_path = track_dir / 'tracks.pkl'
                    if tracks_path.exists():
                        with open(str(tracks_path), 'rb') as f:
                            tracks = pickle.load(f)

                    if tracks is None:
                        return api_error("No tracking results. Run Tracking first.")

                    # Get tracking params for displacement plot
                    track_params_saved = project.load_params(ws_id, pipeline_id, 'tracking') or {}
                    max_sr = None
                    for sk, sv in track_params_saved.items():
                        if isinstance(sv, dict) and 'max_search_range' in sv:
                            try: max_sr = float(sv['max_search_range'])
                            except: pass

                    # Get t_interval from import params
                    t_interval = None
                    for sk, sv in (project.load_params(ws_id, pipeline_id, 'import') or {}).items():
                        if isinstance(sv, dict) and 't_interval' in sv:
                            try: t_interval = float(sv['t_interval'])
                            except: pass

                    if plot_type == 'track_trajectories':
                        frame_n = body.get('frame', 0)
                        if stack is None:
                            return api_error("No image stack loaded.")
                        fig = fig_track_trajectories(stack, tracks, frame=frame_n)
                        filename = f'track_trajectories_{frame_n}.png'

                    elif plot_type == 'track_length_dist':
                        fig = fig_track_length_distribution(tracks, t_interval_seconds=t_interval)
                        filename = 'track_length_distribution.png'

                    elif plot_type == 'track_displacement':
                        fig = fig_track_displacement(tracks, max_search_range=max_sr)
                        filename = 'track_displacement.png'

                    elif plot_type == 'track_lifetime_map':
                        fig = fig_track_lifetime_map(tracks)
                        filename = 'track_lifetime_map.png'

                    elif plot_type == 'track_summary':
                        fig = fig_track_summary(tracks, stack=stack)
                        filename = 'track_summary.png'

                # --- Classification step plots ---
                elif step_id == 'classification':
                    import pandas as pd
                    import json as _json

                    class_dir = project.get_results_dir(ws_id, pipeline_id, 'classification')

                    # Load CSVs
                    df_classified = None
                    df_features = None
                    feature_names = None

                    df_class_path = class_dir / 'df_classified.csv'
                    df_feat_path = class_dir / 'df_features.csv'
                    feat_names_path = class_dir / 'feature_names.json'

                    if df_class_path.exists():
                        df_classified = pd.read_csv(str(df_class_path))
                    if df_feat_path.exists():
                        df_features = pd.read_csv(str(df_feat_path))
                    if feat_names_path.exists():
                        with open(str(feat_names_path)) as f:
                            feature_names = _json.load(f)

                    if df_classified is None:
                        return api_error("No classification results. Run Classification first.")

                    from plotters.plot_classification import (
                        fig_group_distribution,
                        fig_group_feature_boxplots,
                        fig_group_pairwise_stats,
                        fig_group_effect_size_summary,
                    )

                    if plot_type == 'group_distribution':
                        fig = fig_group_distribution(df_classified)
                        filename = 'group_distribution.png'

                    elif plot_type == 'feature_heatmap':
                        fig = fig_group_feature_boxplots(df_classified, feature_names or [])
                        filename = 'feature_heatmap.png'

                    elif plot_type == 'discriminability':
                        fig = fig_group_pairwise_stats(df_classified, feature_names or [])
                        filename = 'discriminability.png'

                    elif plot_type == 'class_summary':
                        fig = fig_group_effect_size_summary(df_classified, feature_names or [])
                        filename = 'class_summary.png'

                # --- Kinetics step plots (reads from classification CSVs) ---
                elif step_id == 'kinetics':
                    import pandas as pd

                    # Load df_classified from classification step
                    class_dir = project.get_results_dir(ws_id, pipeline_id, 'classification')
                    df_class_path = class_dir / 'df_classified.csv'

                    if not df_class_path.exists():
                        return api_error("No classification results. Run Classification first.")

                    df_class = pd.read_csv(str(df_class_path))

                    # Get t_interval from import params
                    t_interval = None
                    for sk, sv in (project.load_params(ws_id, pipeline_id, 'import') or {}).items():
                        if isinstance(sv, dict) and 't_interval' in sv:
                            try: t_interval = float(sv['t_interval'])
                            except: pass

                    from plotters.plot_kinetics import (
                        fig_rate_distributions, fig_rates_by_group,
                        fig_assembly_vs_disassembly, fig_time_to_peak,
                        fig_rate_quality, fig_fa_area_distribution,
                        fig_intensity_spaghetti,
                    )

                    if plot_type == 'rate_distributions':
                        fig = fig_rate_distributions(df_class)
                        filename = 'rate_distributions.png'

                    elif plot_type == 'rates_by_group':
                        fig = fig_rates_by_group(df_class)
                        filename = 'rates_by_group.png'

                    elif plot_type == 'assembly_vs_disassembly':
                        fig = fig_assembly_vs_disassembly(df_class)
                        filename = 'assembly_vs_disassembly.png'

                    elif plot_type == 'time_to_peak':
                        fig = fig_time_to_peak(df_class, t_interval_seconds=t_interval)
                        filename = 'time_to_peak.png'

                    elif plot_type == 'rate_quality':
                        # Get R² threshold from params
                        kin_params = project.load_params(ws_id, pipeline_id, 'kinetics') or {}
                        r2_thresh = 0.5
                        for sk, sv in kin_params.items():
                            if isinstance(sv, dict) and 'kin_min_r2' in sv:
                                try: r2_thresh = float(sv['kin_min_r2'])
                                except: pass
                        fig = fig_rate_quality(df_class, r2_threshold=r2_thresh)
                        filename = 'rate_quality.png'

                    elif plot_type == 'fa_area_distribution':
                        fig = fig_fa_area_distribution(df_class)
                        filename = 'fa_area_distribution.png'

                    elif plot_type in ('intensity_spaghetti', 'intensity_spaghetti_peak'):
                        # Load tracks
                        track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')
                        tracks_path = track_dir / 'tracks.pkl'
                        if not tracks_path.exists():
                            return api_error("No tracking results.")
                        cache_key_trk = f"tracks_{ws_id}_{pipeline_id}"
                        if not hasattr(app, '_tracks_cache'):
                            app._tracks_cache = {}
                        if cache_key_trk not in app._tracks_cache:
                            with open(str(tracks_path), 'rb') as f:
                                app._tracks_cache[cache_key_trk] = pickle.load(f)
                        tracks_list = app._tracks_cache[cache_key_trk]

                        # Load labels
                        det_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')
                        labels_path = det_dir / 'all_labels.npy'
                        cache_key_lbl = f"labels:{ws_id}/{pipeline_id}"
                        if not hasattr(app, '_labels_cache'):
                            app._labels_cache = {}
                        if cache_key_lbl not in app._labels_cache and labels_path.exists():
                            app._labels_cache[cache_key_lbl] = list(np.load(str(labels_path), allow_pickle=True))
                        all_labels = app._labels_cache.get(cache_key_lbl)

                        # Load TIFF stack
                        import tifffile
                        import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
                        file_path = None
                        for sk, sv in import_params.items():
                            if isinstance(sv, dict) and 'input_file' in sv:
                                file_path = sv['input_file']
                        tiff_stack = None
                        cache_key_tiff = f"tiff_{ws_id}_{pipeline_id}"
                        if not hasattr(app, '_tiff_cache'):
                            app._tiff_cache = {}
                        if cache_key_tiff in app._tiff_cache:
                            tiff_stack = app._tiff_cache[cache_key_tiff]
                        elif file_path:
                            resolved = project.resolve_data_path(file_path)
                            if resolved:
                                tiff_stack = tifffile.imread(str(resolved))
                                if tiff_stack.ndim == 3:
                                    tiff_stack = tiff_stack[:, np.newaxis, :, :]
                                app._tiff_cache[cache_key_tiff] = tiff_stack

                        align = 'peak' if plot_type == 'intensity_spaghetti_peak' else 'start'

                        fig = fig_intensity_spaghetti(
                            tracks_list, all_labels=all_labels, stack=tiff_stack,
                            df_classified=df_class,
                            channel_idx=0, channel_name='Intensity',
                            align_to=align,
                        )
                        filename = f'intensity_spaghetti_{align}.png'

                    elif plot_type == 'indiv_track_fit':
                        # Individual track kinetic fit dashboard
                        track_id_req = body.get('track_index', 0)

                        # Load tracks (cached)
                        track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')
                        tracks_path = track_dir / 'tracks.pkl'
                        if not tracks_path.exists():
                            return api_error("No tracking results.")

                        cache_key_trk = f"tracks_{ws_id}_{pipeline_id}"
                        if not hasattr(app, '_tracks_cache'):
                            app._tracks_cache = {}
                        if cache_key_trk not in app._tracks_cache:
                            with open(str(tracks_path), 'rb') as f:
                                app._tracks_cache[cache_key_trk] = pickle.load(f)
                        tracks_list = app._tracks_cache[cache_key_trk]

                        # Build track_id → index lookup (cached)
                        idx_key = cache_key_trk + '_idx'
                        if idx_key not in app._tracks_cache:
                            lookup = {}
                            for ti, t in enumerate(tracks_list):
                                tid = t[0].get('id', ti) if t else ti
                                lookup[tid] = ti
                                lookup[int(float(str(tid)))] = ti  # handle float ids
                            app._tracks_cache[idx_key] = lookup
                        tid_lookup = app._tracks_cache[idx_key]

                        # Find track by track_id
                        list_idx = tid_lookup.get(track_id_req)
                        if list_idx is None:
                            list_idx = tid_lookup.get(int(float(str(track_id_req))))
                        # Fallback: try as direct index
                        if list_idx is None:
                            idx = int(track_id_req)
                            if 0 <= idx < len(tracks_list):
                                list_idx = idx

                        if list_idx is None:
                            return api_error(f"Track {track_id_req} not found")

                        if stack is None or all_labels is None:
                            return api_error("Image stack or labels not available.")

                        from plotters.plot_tracking import fig_track_rates
                        result = fig_track_rates(tracks_list[list_idx], stack, all_labels,
                                                 t_interval_seconds=(t_interval or 10.0))
                        fig = result[0] if isinstance(result, tuple) else result
                        filename = f'indiv_track_{track_id_req}.png'

                # --- Association step plots ---
                elif step_id == 'association':
                    import pickle as _pkl
                    assoc_dir = project.get_results_dir(ws_id, pipeline_id, 'association')
                    pkl_path = assoc_dir / 'association_results.pkl'

                    if not pkl_path.exists():
                        return api_error("No association results. Run Association Analysis first.")

                    with open(str(pkl_path), 'rb') as f:
                        assoc_results = _pkl.load(f)

                    from plotters.plot_association import (
                        fig_assoc_significance, fig_assoc_distributions,
                        fig_assoc_effect_sizes, fig_assoc_track_detail,
                        fig_assoc_method_agreement, fig_assoc_group_coupling,
                    )

                    pop = assoc_results.get('population', {})
                    per_track = assoc_results.get('per_track', {})

                    if plot_type == 'assoc_significance':
                        fig = fig_assoc_significance(pop)
                        filename = 'assoc_significance.png'

                    elif plot_type == 'assoc_distributions':
                        fig = fig_assoc_distributions(pop)
                        filename = 'assoc_distributions.png'

                    elif plot_type == 'assoc_effect_sizes':
                        fig = fig_assoc_effect_sizes(pop)
                        filename = 'assoc_effect_sizes.png'

                    elif plot_type == 'assoc_method_agreement':
                        pair_key = body.get('pair_key', '')
                        if not pair_key and pop:
                            pair_key = list(pop.keys())[0]
                        fig = fig_assoc_method_agreement(per_track, pair_key)
                        filename = f'assoc_method_agreement.png'

                    elif plot_type == 'assoc_group_coupling':
                        pair_key = body.get('pair_key', '')
                        if not pair_key and pop:
                            pair_key = list(pop.keys())[0]
                        class_dir = project.get_results_dir(ws_id, pipeline_id, 'classification')
                        df_class = None
                        df_path = class_dir / 'df_classified.csv'
                        if df_path.exists():
                            import pandas as pd
                            df_class = pd.read_csv(str(df_path))
                        fig = fig_assoc_group_coupling(per_track, pair_key, df_class)
                        filename = f'assoc_group_coupling.png'

                    elif plot_type == 'assoc_track_detail':
                        track_id_assoc = int(body.get('track_id', 0))
                        pair_key = body.get('pair_key', '')
                        track_res = per_track.get(track_id_assoc, {}).get(pair_key, {})
                        if not track_res:
                            track_res = per_track.get(str(track_id_assoc), {}).get(pair_key, {})
                        if not track_res:
                            return api_error(f"No results for track {track_id_assoc} pair {pair_key}")
                        fig = fig_assoc_track_detail(track_res, track_id_assoc, pair_key)
                        filename = f'assoc_track_{track_id_assoc}_{pair_key}.png'

                if fig is None:
                    return api_error(f"Unknown FASTIA plot: {plot_type}")

                # Save and return
                save_path = plots_dir / filename
                fig.savefig(str(save_path), dpi=100, bbox_inches='tight',
                            facecolor='white', edgecolor='none')
                plt.close(fig)

                plot_url = f"/api/step/{ws_id}/{pipeline_id}/{step_id}/results/plots/{filename}"

                sys.stdout = _old_stdout
                _log = _captured.getvalue()
                if _log: print(_log, end='')
                return api_response({
                    "plot_type": plot_type,
                    "filename": filename,
                    "url": plot_url,
                    "log": _log,
                })

            except Exception as e:
                import traceback
                traceback.print_exc()
                sys.stdout = _old_stdout
                _log = _captured.getvalue()
                if _log: print(_log, end='')
                return api_error(f"FASTIA plot error: {str(e)}")
            finally:
                plt.show = _original_show
                plt.close('all')

        # ── IMMUNIA PLOTTERS ──
        if p_type == 'immunia':
            IMMUNIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'immunia')
            if IMMUNIA_DIR not in sys.path:
                sys.path.insert(0, IMMUNIA_DIR)

            if step_id == 'segment':
                from plotters.segmentation_plotter import SegmentationPlotter
                plotter = SegmentationPlotter()
                frame_idx = int(body.get('frame', 0))
                fig = plotter.plot(results_dir, plot_type=plot_type, frame=frame_idx)
                filename = f'{plot_type}.png'

            elif step_id == 'track':
                from plotters.tracking_plotter import TrackingPlotter
                plotter = TrackingPlotter()
                immunia_plots_dir = results_dir / "plots"
                immunia_plots_dir.mkdir(parents=True, exist_ok=True)
                fig = plotter.plot(results_dir, plot_type=plot_type, plots_dir=str(immunia_plots_dir))

                # Animation returns MP4 URL, others return PNG
                if plot_type == 'trajectory_animation':
                    filename = 'trajectory_animation.png'  # static preview
                    fig.savefig(immunia_plots_dir / filename, dpi=150, bbox_inches='tight',
                                facecolor='white', edgecolor='none')
                    plt.close(fig)
                    # Return the MP4 URL (video file), not the PNG
                    mp4_url = f"/api/step/{ws_id}/{pipeline_id}/{step_id}/results/plots/trajectory_animation.mp4"
                    sys.stdout = _old_stdout
                    return api_response({
                        "plot_path": str((immunia_plots_dir / 'trajectory_animation.mp4').relative_to(project.root)),
                        "url": mp4_url,
                        "filename": "trajectory_animation.mp4",
                    })
                else:
                    filename = f'{plot_type}.png'

            elif step_id == 'particle_tracking':
                import importlib
                # Force fresh import every time
                for mod_name in [k for k in sys.modules if 'pt_plotter' in k]:
                    importlib.reload(sys.modules[mod_name])
                from plotters.pt_plotter import ParticleTrackingPlotter
                plotter = ParticleTrackingPlotter()
                # Parse track IDs for MSD curves
                pt_kwargs = {}
                msd_ids_str = body.get('msd_track_ids', '')
                if msd_ids_str:
                    try:
                        pt_kwargs['track_ids'] = [int(x.strip()) for x in msd_ids_str.split(',') if x.strip()]
                    except: pass
                fig = plotter.plot(results_dir, plot_type=plot_type, **pt_kwargs)
                filename = f'{plot_type}.png'

            elif step_id == 'keller_segel':
                import importlib
                for mod_name in [k for k in sys.modules if 'keller_segel_plotter' in k]:
                    importlib.reload(sys.modules[mod_name])
                from plotters.keller_segel_plotter import KellerSegelPlotter
                plotter = KellerSegelPlotter()
                fig = plotter.plot(results_dir, plot_type=plot_type)
                filename = f'{plot_type}.png'

            elif step_id == 'graph_theory':
                import importlib
                for mod_name in [k for k in sys.modules if 'graph_theory_plotter' in k]:
                    importlib.reload(sys.modules[mod_name])
                from plotters.graph_theory_plotter import GraphTheoryPlotter
                plotter = GraphTheoryPlotter()
                gt_plot_map = {
                    'gt_comprehensive': 'comprehensive',
                    'gt_metrics': 'metrics',
                    'gt_regions': 'regions',
                    'gt_boundary': 'boundary',
                    'gt_distance_pairs': 'distance_pairs',
                    'gt_metric_fields': 'metric_fields',
                    'gt_node_distributions': 'node_distributions',
                    'gt_comparative': 'comparative_summary',
                }
                plotter_type = gt_plot_map.get(plot_type, plot_type)
                fig = plotter.plot(results_dir, plot_type=plotter_type)
                filename = f'{plot_type}.png'

            else:
                sys.stdout = _old_stdout
                return api_error(f"No plotter for IMMUNIA step '{step_id}'")

            # Common save + return for all IMMUNIA plots
            immunia_plots_dir = results_dir / "plots"
            immunia_plots_dir.mkdir(parents=True, exist_ok=True)
            # Delete old version to prevent browser caching
            old_file = immunia_plots_dir / filename
            if old_file.exists():
                old_file.unlink()
            fig.savefig(immunia_plots_dir / filename, dpi=150, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            plt.close(fig)

            import time as _time
            cache_bust = int(_time.time())
            plot_url = f"/api/step/{ws_id}/{pipeline_id}/{step_id}/results/plots/{filename}?t={cache_bust}"
            sys.stdout = _old_stdout
            return api_response({
                "plot_path": str((immunia_plots_dir / filename).relative_to(project.root)),
                "url": plot_url,
            })

        # ── CORNEALIA SINGLE-IMAGE PLOTTERS (pickle-based) ──
        # Load saved results
        pkl_path = results_dir / "full_results.pkl"
        if not pkl_path.exists():
            return api_error("No results found. Run the analysis first.", 404)

        with open(pkl_path, 'rb') as f:
            results = pickle.load(f)

        # Reconstruct segmentor-like object from saved arrays
        if '_segmentor_data' in results:
            from types import SimpleNamespace
            seg_data = results.pop('_segmentor_data')
            results['segmentor'] = SimpleNamespace(**seg_data)

        # Reconstruct fake regionprops objects from saved arrays
        if '_objects_data' in results:
            from types import SimpleNamespace
            obj_data = results.pop('_objects_data')
            fake_objects = []
            for i in range(obj_data['count']):
                fake_objects.append(SimpleNamespace(
                    centroid=tuple(obj_data['centroids'][i]),
                    area=int(obj_data['areas'][i]),
                    label=int(obj_data['labels'][i]),
                ))
            results['objects'] = fake_objects

        # Ensure metrics_area exists (plotter checks for it)
        if 'metrics_area' not in results and 'cell_area' in results:
            results['metrics_area'] = results['cell_area']

        plots_dir = results_dir / "plots"
        plots_dir.mkdir(exist_ok=True)

        # ── CORNEALIA PLOTTER ──
        if p_type == 'cornealia':
            from cornealia.plotters.cornealia_plotter import cornealia_plotter

            # Patch plt.show to no-op (plotter calls it, blocks in server)
            _original_show = plt.show
            plt.show = lambda *a, **kw: None

            try:
                plotter = cornealia_plotter(results, save=True, save_dir=str(plots_dir), formats=('png',))

                # Map our plot_type names to plotter methods and actual filenames
                plot_map = {
                    'segmentation':         ('segmentation',         '01_segmentation_overview.png'),
                    'radial_distribution':  ('radial_distribution',  '02_radial_distribution.png'),
                    'potential':            ('potential',             '03_potential_Vr.png'),
                    'fitting':              ('fitting',              None),  # dynamic filename
                    'comprehensive':        ('comprehensive',        '05_comprehensive.png'),
                    'publication_gr':       ('publication_gr',       '06_publication_gr.png'),
                    'publication_vr':       ('publication_vr',       '07_publication_vr.png'),
                    'pipeline_figure':      ('pipeline_figure',      'pipeline_figure.png'),
                    'mechanical_field':     ('mechanical_field',     '08_mechanical_state.png'),
                }

                if plot_type not in plot_map:
                    return api_error(f"Unknown plot type: {plot_type}. Available: {list(plot_map.keys())}")

                method_name, expected_filename = plot_map[plot_type]
                method = getattr(plotter, method_name)
                method(save=True)
                plt.close('all')

                # Find the actual generated file (fitting has dynamic name)
                if expected_filename is None:
                    # Find most recent png in plots_dir
                    pngs = sorted(plots_dir.glob('04_*.png'), key=lambda p: p.stat().st_mtime)
                    if pngs:
                        expected_filename = pngs[-1].name
                    else:
                        expected_filename = 'fitting.png'

                plot_url = f"/api/step/{ws_id}/{pipeline_id}/{step_id}/results/plots/{expected_filename}"

                sys.stdout = _old_stdout
                _log = _captured.getvalue()
                if _log: print(_log, end='')
                return api_response({
                    "plot_type": plot_type,
                    "filename": expected_filename,
                    "url": plot_url,
                    "log": _log,
                })

            finally:
                plt.show = _original_show
                plt.close('all')

        sys.stdout = _old_stdout
        return api_error(f"Plotter not implemented for {p_type}")

    except Exception as e:
        sys.stdout = _old_stdout
        _log = _captured.getvalue() if '_captured' in dir() else ''
        if _log: print(_log, end='')
        import traceback
        traceback.print_exc()
        try: plt.close('all')
        except: pass
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/export-plot', methods=['POST'])
def step_export_plot(ws_id, pipeline_id, step_id):
    """Re-render a plot with custom DPI and format for download."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import pickle

        project = get_project()
        body = request.get_json()
        plot_type = body.get('plot_type', '')
        fmt = body.get('format', 'png')
        dpi = body.get('dpi', 300)

        if not plot_type:
            return api_error("'plot_type' is required")

        pipeline = project.get_pipeline(ws_id, pipeline_id)
        p_type = pipeline.get('type', '')
        results_dir = project.get_results_dir(ws_id, pipeline_id, step_id)

        # Use system temp for exports (keep project dir clean)
        import tempfile, shutil
        global _export_tmp_dir
        if not hasattr(step_export_plot, '_tmp') or not Path(step_export_plot._tmp).exists():
            step_export_plot._tmp = tempfile.mkdtemp(prefix='cellab_export_')
        export_dir = Path(step_export_plot._tmp)
        # Clean old exports
        for f in export_dir.iterdir():
            f.unlink(missing_ok=True)

        filename = f"{plot_type}.{fmt}"

        # For batch plots
        if p_type == 'cornealia_batch':
            batch_run_dir = project.get_results_dir(ws_id, pipeline_id, 'batch_run')
            csv_path = batch_run_dir / "batch_results.csv"
            if not csv_path.exists():
                return api_error("No batch CSV found.", 404)

            from cornealia.plotters.cornealia_batch_plotter import cornealia_batch_plotter

            _orig = plt.show
            plt.show = lambda *a, **kw: None
            try:
                plotter = cornealia_batch_plotter(
                    str(csv_path), save=True,
                    save_dir=str(export_dir), formats=(fmt,)
                )
                # Override DPI
                plt.rcParams['savefig.dpi'] = dpi

                batch_plot_map = {
                    'distributions': 'distributions', 'histogram': 'histogram',
                    'as_vs_bs_boxplots': 'as_vs_bs_boxplots', 'as_vs_bs_scatter': 'as_vs_bs_scatter',
                    'as_vs_bs_histograms': 'as_vs_bs_histograms', 'validation_scatter': 'validation_scatter',
                    'validation_bland_altman': 'validation_bland_altman', 'deep_dive': 'deep_dive',
                    'pub_boxplots': 'pub_boxplots', 'pub_K_deep_dive': 'pub_K_deep_dive',
                    'pub_validation': 'pub_validation', 'pub_K_independence': 'pub_K_independence',
                    'pub_comprehensive': 'pub_comprehensive',
                }
                method_name = batch_plot_map.get(plot_type)
                if method_name:
                    getattr(plotter, method_name)(save=True)
                    plt.close('all')

                # Find the exported file
                exports = sorted(export_dir.glob(f'*.{fmt}'), key=lambda p: p.stat().st_mtime)
                if exports:
                    filename = exports[-1].name
            finally:
                plt.show = _orig
                plt.close('all')

        # For single-image plots
        elif p_type == 'cornealia':
            pkl_path = results_dir / "full_results.pkl"
            if not pkl_path.exists():
                return api_error("No results found.", 404)

            with open(pkl_path, 'rb') as f:
                results = pickle.load(f)

            if '_segmentor_data' in results:
                from types import SimpleNamespace
                results['segmentor'] = SimpleNamespace(**results.pop('_segmentor_data'))
            if '_objects_data' in results:
                from types import SimpleNamespace
                od = results.pop('_objects_data')
                results['objects'] = [SimpleNamespace(centroid=tuple(od['centroids'][i]), area=int(od['areas'][i]), label=int(od['labels'][i])) for i in range(od['count'])]
            if 'metrics_area' not in results and 'cell_area' in results:
                results['metrics_area'] = results['cell_area']

            from cornealia.plotters.cornealia_plotter import cornealia_plotter

            _orig = plt.show
            plt.show = lambda *a, **kw: None
            try:
                plotter = cornealia_plotter(results, save=True, save_dir=str(export_dir), formats=(fmt,))
                plt.rcParams['savefig.dpi'] = dpi

                method = getattr(plotter, plot_type, None)
                if method:
                    method(save=True)
                    plt.close('all')

                exports = sorted(export_dir.glob(f'*.{fmt}'), key=lambda p: p.stat().st_mtime)
                if exports:
                    filename = exports[-1].name
            finally:
                plt.show = _orig
                plt.close('all')

        url = f"/api/step/{ws_id}/{pipeline_id}/{step_id}/results/exports/{filename}"
        return api_response({"url": url, "filename": filename, "format": fmt, "dpi": dpi})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/results/exports/<path:filename>')
def step_get_export_file(ws_id, pipeline_id, step_id, filename):
    """Serve an exported file for download."""
    try:
        export_dir = getattr(step_export_plot, '_tmp', None)
        if not export_dir or not Path(export_dir).exists():
            return api_error("No export available", 404)
        return send_from_directory(str(export_dir), filename, as_attachment=True)
    except Exception as e:
        return api_error(str(e), 404)


@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/results', methods=['GET'])
def step_get_results(ws_id, pipeline_id, step_id):
    """List available results for a step (including plots/ subdirectory)."""
    try:
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, step_id)

        results = []
        if results_dir.exists():
            for f in results_dir.rglob('*'):
                if f.is_file():
                    rel_to_results = f.relative_to(results_dir)
                    rel_str = str(rel_to_results).replace('\\', '/')
                    results.append({
                        "name": f.name,
                        "relative": rel_str,
                        "path": str(f.relative_to(project.root)),
                        "size_bytes": f.stat().st_size,
                        "type": f.suffix,
                        "url": f"/api/step/{ws_id}/{pipeline_id}/{step_id}/results/{rel_str}",
                    })

        return api_response(results)
    except Exception as e:
        return api_error(str(e), 500)


# ═════════════════════════════════════════════
# TASK LOG STREAMING
# ═════════════════════════════════════════════

import threading
import io as _io

_task_logs = {}       # {task_key: StringIO buffer}
_task_logs_lock = threading.Lock()

# ── Async task progress tracking ──
_run_progress = {}    # {task_key: {status, current, total, message, phase}}
_run_results = {}     # {task_key: {status, outputs, error_msg, log, ...}}
_run_cancel = {}      # {task_key: threading.Event}
_run_progress_lock = threading.Lock()

class TeeWriter:
    """Writes to both a StringIO buffer and the original stdout."""
    def __init__(self, buffer, original):
        self.buffer = buffer
        self.original = original
    def write(self, text):
        self.buffer.write(text)
        self.original.write(text)
    def flush(self):
        self.buffer.flush()
        self.original.flush()


@app.route('/api/tasks/log', methods=['POST'])
def get_task_log():
    """Get current log for a running task. Body: { "key": "ws/pipeline/step" }"""
    body = request.get_json()
    key = body.get('key', '')
    with _task_logs_lock:
        buf = _task_logs.get(key)
        if buf:
            return api_response({"log": buf.getvalue()})
    return api_response({"log": ""})


@app.route('/api/tasks/progress', methods=['POST'])
def get_task_progress():
    """Get progress for a running task. Body: { "key": "ws/pipeline/step" }"""
    body = request.get_json()
    key = body.get('key', '')
    with _run_progress_lock:
        progress = _run_progress.get(key)
        result = _run_results.get(key)
    if result:
        # Task completed — return result and clean up
        with _run_progress_lock:
            _run_progress.pop(key, None)
            _run_results.pop(key, None)
            _run_cancel.pop(key, None)
        return api_response({"done": True, "result": result})
    if progress:
        return api_response({"done": False, "progress": progress})
    return api_response({"done": False, "progress": None})


@app.route('/api/tasks/cancel', methods=['POST'])
def cancel_task():
    """Cancel a running task. Body: { "key": "ws/pipeline/step" }"""
    body = request.get_json()
    key = body.get('key', '')
    with _run_progress_lock:
        evt = _run_cancel.get(key)
        if evt:
            evt.set()
            _run_progress[key] = {
                'status': 'cancelling',
                'current': 0, 'total': 1,
                'phase': 'cancelling',
                'message': 'Stopping after current frame...',
                'pct': 0,
            }
            return api_response({"cancelled": True})
    return api_response({"cancelled": False, "error": "No running task found"})



# ═══════════════════════════════════════════════
# IMMUNIA — Run Steps
# ═══════════════════════════════════════════════

def _run_immunia(project, ws_id, pipeline_id, step_id, params, results_dir, progress_cb=None, cancel_evt=None):
    """Run IMMUNIA analysis step."""
    import json
    import numpy as np
    import pickle

    # Flatten section params
    all_params = {}
    for section_key, section_val in params.items():
        if isinstance(section_val, dict):
            all_params.update(section_val)
        else:
            all_params[section_key] = section_val

    print(f"[IMMUNIA] Running step: {step_id}")
    print(f"[IMMUNIA] Params: {json.dumps(all_params, default=str)[:500]}")

    try:
        if step_id == 'import':
            return {"status": "done", "outputs": {"message": "Import handled by frontend"}}

        elif step_id == 'segment':
            import tifffile
            from scipy.ndimage import label as ndlabel, binary_fill_holes, binary_erosion
            from skimage.morphology import remove_small_objects

            # ── Load import params ──
            import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
            ch_setup = {}
            for k, v in import_params.items():
                if isinstance(v, dict):
                    ch_setup.update(v)
                elif k.endswith('_channel_idx') or k.endswith('_channel_name'):
                    ch_setup[k] = v

            # Find movie file
            file_path = None
            for k, v in import_params.items():
                if isinstance(v, dict) and 'input_file' in v:
                    file_path = v['input_file']
                    break
                elif k == 'input_file':
                    file_path = v
            if not file_path:
                return {"status": "error", "error_msg": "No movie loaded. Import a movie first."}

            resolved = project.resolve_data_path(file_path)
            if not resolved:
                return {"status": "error", "error_msg": f"File not found: {file_path}"}

            # Load movie
            if progress_cb:
                progress_cb(0, 5, 'loading', 'Loading movie...')
            print(f"[IMMUNIA] Loading movie: {resolved}")
            stack = tifffile.imread(str(resolved))
            if stack.ndim == 3:
                stack = stack[:, np.newaxis, :, :]  # add channel dim
            n_frames, n_channels = stack.shape[0], stack.shape[1]
            print(f"[IMMUNIA] Movie shape: {stack.shape} — {n_frames} frames, {n_channels} channels")

            # ── Try actual Preprocessor_Segmentor ──
            segmentor = None
            try:
                IMMUNIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'immunia')
                if IMMUNIA_DIR not in sys.path:
                    sys.path.insert(0, IMMUNIA_DIR)
                from components.immunia_preprocessor_segmentor import Preprocessor_Segmentor
                segmentor = Preprocessor_Segmentor()
                print("[IMMUNIA] Using Preprocessor_Segmentor")
            except Exception as e:
                print(f"[IMMUNIA] Preprocessor_Segmentor not available: {e}")

            # ── Define roles ──
            roles = [
                {'key': 'dead',   'label': 'Cytotoxicity', 'default_idx': 0, 'default_factor': 0.8, 'default_min': 10,   'default_method': 'grid',   'separate': False},
                {'key': 'tumor',  'label': 'Target Cells', 'default_idx': 1, 'default_factor': 1.0, 'default_min': 200,  'default_method': 'global', 'separate': True},
                {'key': 'tissue', 'label': 'Substrate',    'default_idx': 2, 'default_factor': 0.7, 'default_min': 1000, 'default_method': 'global', 'separate': False},
                {'key': 'nk',     'label': 'Effector',     'default_idx': 3, 'default_factor': 0.9, 'default_min': 30,   'default_method': 'global', 'separate': True},
            ]

            all_masks = {}
            os.makedirs(results_dir, exist_ok=True)

            for role_i, role in enumerate(roles):
                if cancel_evt and cancel_evt.is_set():
                    return {"status": "cancelled", "outputs": {"message": "Cancelled by user"}}

                rk = role['key']
                ch_idx = int(ch_setup.get(f'{rk}_channel_idx', role['default_idx']))
                ch_name = ch_setup.get(f'{rk}_channel_name', role['label'])

                # Get per-role segmentation params
                threshold_factor = float(all_params.get(f'{rk}_threshold_factor', role['default_factor']))
                min_size = int(all_params.get(f'{rk}_min_size', role['default_min']))
                sigma = float(all_params.get(f'{rk}_gaussian_sigma', 2.0))
                method = all_params.get(f'{rk}_threshold_method', role['default_method'])
                separate = role['separate']  # Fixed per role, not user-configurable
                manual_thresh_str = all_params.get(f'{rk}_manual_threshold', '')
                manual_threshold = float(manual_thresh_str) if manual_thresh_str else None
                imin_str = all_params.get(f'{rk}_intensity_min', '')
                intensity_min = float(imin_str) if imin_str else None
                imax_str = all_params.get(f'{rk}_intensity_max', '')
                intensity_max = float(imax_str) if imax_str else None

                if ch_idx >= n_channels:
                    print(f"[IMMUNIA] ⚠ Skipping {rk}: channel {ch_idx} out of range (max {n_channels-1})")
                    continue

                phase = f'{role["label"]} ({rk})'
                print(f"\n[IMMUNIA] ═══ {phase} — channel {ch_idx} ({ch_name}) ═══")
                print(f"[IMMUNIA]   method={method} factor={threshold_factor} min_size={min_size} σ={sigma} separate={separate}")

                if progress_cb:
                    progress_cb(role_i, 4, phase, f'Segmenting {ch_name} (channel {ch_idx})...')

                channel_data = stack[:, ch_idx, :, :]
                # Use uint16 for labeled channels (separate=True), uint8 for binary
                mask_dtype = np.uint16 if separate else np.uint8
                masks = np.zeros((n_frames, channel_data.shape[1], channel_data.shape[2]), dtype=mask_dtype)

                for f_idx in range(n_frames):
                    if cancel_evt and cancel_evt.is_set():
                        return {"status": "cancelled", "outputs": {"message": "Cancelled by user"}}

                    if segmentor:
                        segmentor.config['gaussian_sigma'] = sigma
                        masks[f_idx] = segmentor.segment_adaptive_threshold(
                            image=channel_data[f_idx],
                            min_size=min_size,
                            threshold_factor=threshold_factor,
                            method=method,
                            separate_objects=separate,
                            manual_threshold=manual_threshold,
                            intensity_min=intensity_min,
                            intensity_max=intensity_max,
                        )
                    else:
                        # Inline fallback (simplified)
                        from scipy.ndimage import gaussian_filter
                        from skimage.filters import threshold_otsu
                        raw = channel_data[f_idx].astype(np.float32)
                        if method == 'manual' and manual_threshold is not None:
                            mask = raw > manual_threshold
                        elif method == 'min_max':
                            imin_v = intensity_min if intensity_min is not None else np.percentile(raw, 1)
                            imax_v = intensity_max if intensity_max is not None else np.percentile(raw, 99)
                            raw[raw < imin_v] = 0
                            raw = np.clip(raw, 0, imax_v)
                            if imax_v > imin_v:
                                raw = (raw - imin_v) / (imax_v - imin_v)
                            raw = gaussian_filter(raw, sigma=sigma)
                            try: t = threshold_otsu(raw[raw > 0]) * threshold_factor if np.any(raw > 0) else 0.5
                            except: t = 0.5
                            mask = raw > t
                        else:
                            img = raw.copy()
                            pmin, pmax = np.percentile(img, (1, 99))
                            if pmax > pmin:
                                img = np.clip((img - pmin) / (pmax - pmin), 0, 1)
                            img = gaussian_filter(img, sigma=sigma)
                            try: t = threshold_otsu(img[img > 0]) * threshold_factor if np.any(img > 0) else 0.5
                            except: t = 0.5
                            mask = img > t
                        mask = binary_fill_holes(mask)
                        mask = remove_small_objects(mask, min_size=min_size)
                        masks[f_idx] = mask.astype(np.uint8)

                    # Progress per frame
                    if progress_cb and f_idx % 10 == 0:
                        pct_within_role = f_idx / max(n_frames, 1)
                        overall = (role_i + pct_within_role) / 4
                        progress_cb(
                            int(overall * 100), 100,
                            phase,
                            f'{ch_name}: frame {f_idx}/{n_frames}'
                        )

                    # Label connected components for channels with separate=True
                    if separate and masks[f_idx].max() <= 1:
                        from skimage.measure import label as sklabel
                        masks[f_idx] = sklabel(masks[f_idx].astype(bool), connectivity=2).astype(np.uint16)

                # Count objects in last frame
                _, n_obj = ndlabel(masks[-1] > 0)
                if separate:
                    n_obj = len(np.unique(masks[-1][masks[-1] > 0]))
                area_pct = round(np.sum(masks[-1] > 0) / masks[-1].size * 100, 1)
                print(f"[IMMUNIA]   ✓ {n_frames} frames — {n_obj} objects in last frame, {area_pct}% area")

                # Create time-averaged mask
                if separate:
                    # For labeled channels: label the thresholded average
                    from skimage.measure import label as sklabel
                    avg_binary = (np.mean(masks > 0, axis=0) > 0.5).astype(bool)
                    avg_mask = sklabel(avg_binary, connectivity=2).astype(np.uint16)
                    n_avg_obj = avg_mask.max()
                    print(f"[IMMUNIA]   avg_mask: {n_avg_obj} labeled regions")
                else:
                    avg_mask = (np.mean(masks, axis=0) > 0.5).astype(np.uint8)

                # Save masks
                np.save(results_dir / f'{rk}_masks.npy', masks)
                np.save(results_dir / f'{rk}_avg_mask.npy', avg_mask)
                all_masks[rk] = {'n_frames': n_frames, 'n_objects': n_obj, 'area_pct': area_pct}

            # ── Save summary ──
            if progress_cb:
                progress_cb(100, 100, 'saving', 'Saving results...')

            summary = {
                'n_frames': n_frames,
                'n_channels': n_channels,
                'movie_shape': list(stack.shape),
                'channel_setup': ch_setup,
                'roles': all_masks,
            }
            import json as _json
            with open(results_dir / 'segmentation_summary.json', 'w') as f:
                _json.dump(summary, f, indent=2, default=str)

            # Build completion message
            msg_parts = []
            for rk, info in all_masks.items():
                msg_parts.append(f"{rk}: {info['n_objects']} obj, {info['area_pct']}%")
            msg = f"Segmentation complete — {n_frames} frames | " + " | ".join(msg_parts)
            print(f"\n[IMMUNIA] ✅ {msg}")

            return {"status": "done", "outputs": {"message": msg}}

        elif step_id == 'track':
            import tifffile
            import pandas as pd

            # ── Load segmentation masks ──
            seg_dir = project.get_results_dir(ws_id, pipeline_id, 'segment')
            track_target = all_params.get('track_target', 'nk')
            masks_path = seg_dir / f'{track_target}_masks.npy'

            if not masks_path.exists():
                return {"status": "error", "error_msg": f"No {track_target} masks found. Run segmentation first."}

            if progress_cb:
                progress_cb(0, 4, 'loading', f'Loading {track_target} masks...')
            print(f"[IMMUNIA] Loading masks: {masks_path}")
            masks = np.load(masks_path)
            n_frames = masks.shape[0]
            print(f"[IMMUNIA] Masks shape: {masks.shape} — {n_frames} frames")

            # ── Build tracker config ──
            use_masks = str(all_params.get('use_masks', 'true')).lower() == 'true'
            tracker_config = {
                'feature_detection': {
                    'diameter': 11,
                    'minmass': 100,
                    'separation': 8,
                },
                'linking': {
                    'search_range': int(all_params.get('search_range', 15)),
                    'memory': int(all_params.get('memory', 3)),
                    'adaptive_stop': int(all_params.get('adaptive_stop', 5)),
                    'adaptive_step': float(all_params.get('adaptive_step', 0.95)),
                },
                'filtering': {
                    'min_frames': int(all_params.get('min_frames', 10)),
                    'max_velocity': float(all_params.get('max_velocity', 50)),
                    'min_velocity': float(all_params.get('min_velocity', 0.1)),
                },
                'analysis': {
                    'pixel_to_um': float(all_params.get('pixel_to_um', 0.65)),
                    'frame_to_min': float(all_params.get('frame_to_min', 3.0)),
                    'compute_msd': True,
                    'compute_velocity': True,
                    'compute_directionality': True,
                },
            }

            print(f"[IMMUNIA] Tracking config: search_range={tracker_config['linking']['search_range']}, "
                  f"memory={tracker_config['linking']['memory']}, min_frames={tracker_config['filtering']['min_frames']}")

            # ── Run tracker ──
            if progress_cb:
                progress_cb(1, 4, 'tracking', 'Detecting features + linking trajectories...')

            try:
                IMMUNIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'immunia')
                if IMMUNIA_DIR not in sys.path:
                    sys.path.insert(0, IMMUNIA_DIR)
                from components.immunia_tracker import Tracker

                tracker = Tracker(config=tracker_config)
                results = tracker.track_cells(nk_masks=masks, use_masks=use_masks)
                print(f"[IMMUNIA] Tracker returned: {list(results.keys())}")
            except Exception as track_err:
                print(f"[IMMUNIA] Tracker import failed: {track_err}, using trackpy fallback")
                import trackpy as tp

                # Fallback: use trackpy directly on labeled masks
                if progress_cb:
                    progress_cb(1, 4, 'tracking', 'Detecting features (trackpy)...')

                from scipy.ndimage import label as ndlabel_t, center_of_mass
                features_list = []
                for f_idx in range(n_frames):
                    labeled, n_obj = ndlabel_t(masks[f_idx])
                    if n_obj == 0:
                        continue
                    centroids = center_of_mass(masks[f_idx], labeled, range(1, n_obj + 1))
                    for c_idx, (cy, cx) in enumerate(centroids):
                        features_list.append({
                            'frame': f_idx, 'x': cx, 'y': cy,
                            'mass': float(np.sum(labeled == (c_idx + 1))),
                        })

                features_df = pd.DataFrame(features_list)
                if len(features_df) == 0:
                    return {"status": "error", "error_msg": "No features detected in masks"}

                if progress_cb:
                    progress_cb(2, 4, 'linking', 'Linking trajectories...')

                sr = int(all_params.get('search_range', 15))
                mem = int(all_params.get('memory', 3))
                linked = tp.link(features_df, search_range=sr, memory=mem)

                min_frames = int(all_params.get('min_frames', 10))
                filtered = tp.filter_stubs(linked, min_frames)

                n_tracks = filtered['particle'].nunique()
                statistics = {}
                for pid in filtered['particle'].unique():
                    track = filtered[filtered['particle'] == pid]
                    dx = np.diff(track['x'].values)
                    dy = np.diff(track['y'].values)
                    velocities = np.sqrt(dx**2 + dy**2)
                    statistics[int(pid)] = {
                        'track_length': len(track),
                        'mean_velocity': float(np.mean(velocities)) if len(velocities) > 0 else 0,
                    }

                results = {
                    'tracks': filtered,
                    'statistics': statistics,
                    'summary': {
                        'n_tracks': n_tracks,
                        'n_frames': n_frames,
                        'total_detections': len(filtered),
                    }
                }

            # ── Save results ──
            if progress_cb:
                progress_cb(3, 4, 'saving', 'Saving tracking results...')

            os.makedirs(results_dir, exist_ok=True)

            tracks_df = results.get('tracks', pd.DataFrame())
            if not tracks_df.empty:
                # trackpy sets 'frame' as index AND column — normalize
                tracks_df = tracks_df.reset_index(drop=True if 'frame' in tracks_df.columns else False)
                tracks_df.to_csv(results_dir / 'tracks.csv', index=False)
                tracks_df.to_pickle(results_dir / 'tracks.pkl')

            statistics = results.get('statistics', {})
            summary = results.get('summary', {})

            import json as _json2
            with open(results_dir / 'tracking_summary.json', 'w') as f:
                _json2.dump({
                    'summary': summary,
                    'config': tracker_config,
                    'track_target': track_target,
                    'n_tracks': summary.get('n_tracks', 0),
                    'n_frames': n_frames,
                }, f, indent=2, default=str)

            # Save statistics
            with open(results_dir / 'track_statistics.pkl', 'wb') as f:
                pickle.dump(statistics, f)

            n_tracks = summary.get('n_tracks', 0)
            avg_len = summary.get('avg_track_length', 0)
            msg = f"Tracking complete — {n_tracks} tracks, {n_frames} frames"
            if isinstance(avg_len, (int, float)) and avg_len > 0:
                msg += f", avg length {avg_len:.1f} frames"
            print(f"\n[IMMUNIA] ✅ {msg}")

            if progress_cb:
                progress_cb(4, 4, 'done', msg)

            return {"status": "done", "outputs": {"message": msg}}

        elif step_id == 'signal_association':
            import pandas as pd

            # ── Load tracks from tracking step ──
            track_dir = project.get_results_dir(ws_id, pipeline_id, 'track')
            tracks_pkl = track_dir / 'tracks.pkl'
            tracks_csv = track_dir / 'tracks.csv'

            if tracks_pkl.exists():
                tracks_df = pd.read_pickle(tracks_pkl)
            elif tracks_csv.exists():
                tracks_df = pd.read_csv(tracks_csv)
            else:
                return {"status": "error", "error_msg": "No tracking results found. Run tracking first."}

            # Fix trackpy frame ambiguity
            if not tracks_df.empty:
                tracks_df = tracks_df.reset_index(drop=True if 'frame' in tracks_df.columns else False)

            if progress_cb:
                progress_cb(0, 100, 'loading', 'Loading tracks...')

            n_tracks = tracks_df['particle'].nunique()
            print(f"[IMMUNIA] Signal association — {n_tracks} tracks loaded")

            # ── Build config ──
            # Resolve n_surrogates: custom input takes priority, then preset dropdown
            n_surr_custom = all_params.get('n_surrogates', '')
            n_surr_preset = all_params.get('n_surrogates_preset', '100')
            n_surrogates = int(n_surr_custom) if n_surr_custom and str(n_surr_custom).isdigit() else int(n_surr_preset)

            assoc_config = {
                'signal_type': all_params.get('signal_type', 'position_pca'),
                'min_overlap': int(all_params.get('min_overlap', 20)),
                'min_signal_length': int(all_params.get('min_signal_length', 20)),
                'method': all_params.get('assoc_method', 'ccm'),
                'n_surrogates': n_surrogates,
                'surrogate_method': all_params.get('surrogate_method', 'iaaft'),
                'stationarize': all_params.get('stationarize', 'bandpass'),
                'alpha': float(all_params.get('alpha', 0.05)),
                # Granger-specific
                'granger_max_lag': int(all_params.get('granger_max_lag', 5)),
                'granger_lag_criterion': all_params.get('granger_lag_criterion', 'aic'),
                # CCM-specific
                'ccm_embedding_dim': int(all_params.get('ccm_embedding_dim', 2)),
                'ccm_n_boot': int(all_params.get('ccm_n_boot', 20)),
            }

            print(f"[IMMUNIA] Config: signal={assoc_config['signal_type']}, "
                  f"method={assoc_config['method']}, surrogates={assoc_config['n_surrogates']}")

            # ── Run association ──
            try:
                IMMUNIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'immunia')
                if IMMUNIA_DIR not in sys.path:
                    sys.path.insert(0, IMMUNIA_DIR)
                from components.immunia_association import IMMUNIAAssociation

                analyzer = IMMUNIAAssociation(config=assoc_config)
                results = analyzer.run(tracks_df, progress_cb=progress_cb, cancel_evt=cancel_evt)

                if 'error' in results:
                    return {"status": "error", "error_msg": results['error']}

                # Save results
                os.makedirs(results_dir, exist_ok=True)
                analyzer.save_results(results, results_dir)

                method = assoc_config['method']
                stats = results.get('statistics', {}).get(method, {})
                n_pairs = stats.get('n_pairs', 0)
                n_sig = stats.get('n_significant', 0)
                n_strong = stats.get('n_strong', 0)
                mean_rho = stats.get('mean', 0)

                msg = (f"Association complete — {n_pairs} pairs, "
                       f"mean ρ={mean_rho:.3f}, {n_sig} significant, {n_strong} strong")
                print(f"\n[IMMUNIA] ✅ {msg}")

                if progress_cb:
                    progress_cb(100, 100, 'done', msg)

                return {"status": "done", "outputs": {"message": msg}}

            except Exception as e:
                import traceback
                traceback.print_exc()
                return {"status": "error", "error_msg": str(e)}

        elif step_id == 'particle_tracking':
            import pickle
            import pandas as pd

            track_dir = project.get_results_dir(ws_id, pipeline_id, 'track')
            seg_dir = project.get_results_dir(ws_id, pipeline_id, 'segment')

            if progress_cb:
                progress_cb(0, 100, 'loading', 'Loading tracking + segmentation...')

            tracks_pkl = track_dir / 'tracks.pkl'
            tracks_csv = track_dir / 'tracks.csv'
            if tracks_pkl.exists():
                tracks_df = pd.read_pickle(tracks_pkl)
            elif tracks_csv.exists():
                tracks_df = pd.read_csv(tracks_csv)
            else:
                return {"status": "error", "error_msg": "No tracking results. Run tracking first."}

            if not tracks_df.empty:
                tracks_df = tracks_df.reset_index(drop=True if 'frame' in tracks_df.columns else False)

            trajectories = []
            track_ids = []
            for pid in tracks_df['particle'].unique():
                t = tracks_df[tracks_df['particle'] == pid].sort_values('frame')
                trajectories.append(t[['x', 'y']].values)
                track_ids.append(int(pid))

            results_input = {
                'tracks_df': tracks_df,
                'trajectories': trajectories,
                'track_ids': track_ids,
                'n_tracks': len(track_ids),
            }

            for rk in ['tumor', 'tissue', 'nk', 'dead']:
                avg_path = seg_dir / f'{rk}_avg_mask.npy'
                if avg_path.exists():
                    results_input[f'{rk}_mask'] = np.load(avg_path)

            # Load association influence matrix if available
            sa_dir = project.get_results_dir(ws_id, pipeline_id, 'signal_association')
            sa_runs = sa_dir / 'runs'
            if sa_runs.exists():
                for run_path in sorted(sa_runs.iterdir(), reverse=True):
                    pkl_path = run_path / 'association_results.pkl'
                    if pkl_path.exists():
                        with open(pkl_path, 'rb') as f:
                            sa_data = pickle.load(f)
                        for m, matrix in sa_data.get('influence_matrices', {}).items():
                            results_input['influence_matrix'] = matrix
                            print(f"[IMMUNIA] PT: loaded influence matrix from {run_path.name}")
                        break

            diff_thresh_str = all_params.get('diff_thresholds', '0.01,0.05,0.1')
            try:
                diff_thresholds = [float(x.strip()) for x in diff_thresh_str.split(',')]
            except:
                diff_thresholds = [0.01, 0.05, 0.1]

            pt_params = {
                'diff_thresholds': diff_thresholds,
                'directed_threshold': float(all_params.get('directed_threshold', 0.7)),
                'min_track_length': int(all_params.get('pt_min_track_length', 4)),
                'pixel_to_um': float(all_params.get('pt_pixel_to_um', 0.65)),
                'frame_to_min': float(all_params.get('pt_frame_to_min', 3.0)),
                'ccm_significance_threshold': float(all_params.get('ccm_significance_threshold', 0.3)),
                'scale_factor': float(all_params.get('scale_factor', 1.3)),
                'max_frame_gap': int(all_params.get('max_frame_gap', 5)),
                'min_samples_for_stats': int(all_params.get('min_samples_for_stats', 5)),
                'msd_fit_fraction': float(all_params.get('msd_fit_fraction', 0.33)),
                'revisit_min_gap': int(all_params.get('revisit_min_gap', 3)),
                'msd_r_squared_threshold': float(all_params.get('msd_r_squared_threshold', 0.7)),
            }

            analysis_mode = all_params.get('pt_analysis_mode', 'auto')
            print(f"[IMMUNIA] Particle Tracking — {len(track_ids)} tracks, mode={analysis_mode}")

            if progress_cb:
                progress_cb(10, 100, 'analyzing', f'Analyzing {len(track_ids)} tracks...')

            try:
                IMMUNIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'immunia')
                if IMMUNIA_DIR not in sys.path:
                    sys.path.insert(0, IMMUNIA_DIR)
                from components.particle_tracking_analyzer import ParticleTrackingAnalyzer

                analyzer = ParticleTrackingAnalyzer()
                pt_results = analyzer.run_analysis(
                    dataset_name='immunia_run',
                    results=results_input,
                    analysis_mode=analysis_mode,
                    params=pt_params,
                )

                if 'error' in pt_results:
                    return {"status": "error", "error_msg": pt_results['error']}

                os.makedirs(results_dir, exist_ok=True)
                with open(results_dir / 'particle_tracking_results.pkl', 'wb') as f:
                    pickle.dump(pt_results, f)

                import json as _json4
                summary = pt_results.get('summary', {})
                with open(results_dir / 'particle_tracking_summary.json', 'w') as f:
                    _json4.dump(summary, f, indent=2, default=str)

                if progress_cb:
                    progress_cb(100, 100, 'done', 'Analysis complete')

                n_analyzed = summary.get('n_tracks_analyzed', len(track_ids))
                msg = f"PT analysis complete — {n_analyzed} tracks analyzed"
                print(f"\n[IMMUNIA] ✅ {msg}")
                return {"status": "done", "outputs": {"message": msg}}

            except Exception as e:
                import traceback
                traceback.print_exc()
                return {"status": "error", "error_msg": str(e)}

        elif step_id == 'graph_theory':
            import pickle
            import pandas as pd

            track_dir = project.get_results_dir(ws_id, pipeline_id, 'track')
            seg_dir = project.get_results_dir(ws_id, pipeline_id, 'segment')
            sa_dir = project.get_results_dir(ws_id, pipeline_id, 'signal_association')

            if progress_cb:
                progress_cb(0, 100, 'loading', 'Loading tracking + segmentation + association data...')

            # ── Load tracking data ──
            tracks_pkl = track_dir / 'tracks.pkl'
            tracks_csv = track_dir / 'tracks.csv'
            if tracks_pkl.exists():
                tracks_df = pd.read_pickle(tracks_pkl)
            elif tracks_csv.exists():
                tracks_df = pd.read_csv(tracks_csv)
            else:
                return {"status": "error", "error_msg": "No tracking results. Run tracking first."}

            if not tracks_df.empty:
                tracks_df = tracks_df.reset_index(drop=True if 'frame' in tracks_df.columns else False)

            trajectories = []
            track_ids = []
            for pid in tracks_df['particle'].unique():
                t = tracks_df[tracks_df['particle'] == pid].sort_values('frame')
                trajectories.append(t[['x', 'y']].values)
                track_ids.append(int(pid))

            # ── Load segmentation masks ──
            seg_data = {}
            for rk in ['tumor', 'tissue']:
                avg_path = seg_dir / f'{rk}_avg_mask.npy'
                if avg_path.exists():
                    seg_data[f'{rk}_mask'] = np.load(avg_path)

            field_shape = seg_data.get('tumor_mask', np.zeros((512, 512))).shape

            # ── Load ALL signal association runs (filtered by user selection) ──
            sa_results = {}
            sa_runs = sa_dir / 'runs'
            selected_runs_str = all_params.get('gt_selected_runs', 'all')
            selected_run_ids = None if selected_runs_str == 'all' else set(selected_runs_str.split(','))

            if sa_runs.exists():
                all_matrices = {}
                all_pairwise = {}
                sa_track_ids = []
                
                for run_path in sorted(sa_runs.iterdir()):
                    if not run_path.is_dir():
                        continue
                    run_id = run_path.name
                    
                    # Filter by user selection
                    if selected_run_ids is not None and run_id not in selected_run_ids:
                        continue
                    
                    pkl_path = run_path / 'association_results.pkl'
                    if not pkl_path.exists():
                        continue
                    with open(pkl_path, 'rb') as f:
                        sa_data = pickle.load(f)
                    
                    for method, matrix in sa_data.get('influence_matrices', {}).items():
                        all_matrices[method] = matrix
                        print(f"[IMMUNIA] GT: loaded {method} matrix ({matrix.shape}) from {run_id}")
                    
                    for method, pw in sa_data.get('pairwise_results', {}).items():
                        all_pairwise[method] = pw
                    
                    if sa_data.get('track_ids'):
                        sa_track_ids = sa_data['track_ids']
                
                if all_matrices:
                    sa_results = {
                        'influence_matrices': all_matrices,
                        'pairwise_results': all_pairwise,
                        'track_ids': sa_track_ids,
                    }
                    print(f"[IMMUNIA] GT: {len(all_matrices)} methods: {list(all_matrices.keys())}")

            # ── Build prepared_data dict ──
            prepared_data = {
                'tracking_data': {
                    'trajectories': trajectories,
                    'track_ids': track_ids,
                    'tracks_df': tracks_df,
                },
                'segmentation_data': {
                    'tumor_mask': seg_data.get('tumor_mask', np.array([])),
                    'tissue_mask': seg_data.get('tissue_mask', np.array([])),
                    'field_shape': field_shape,
                },
            }
            if sa_results:
                prepared_data['signal_association_results'] = sa_results

            # ── Build network types list ──
            network_types = []
            available_methods = list(sa_results.get('influence_matrices', {}).keys()) if sa_results else []
            print(f"[IMMUNIA] GT: available influence matrices: {available_methods}")
            
            if str(all_params.get('gt_use_ccm', 'true')).lower() == 'true' and sa_results:
                if 'ccm' in available_methods:
                    network_types.append('ccm')
                elif 'pearson' in available_methods or 'mutual_information' in available_methods:
                    # Use correlation-based method as CCM substitute
                    for m in ['pearson', 'mutual_information']:
                        if m in available_methods:
                            sa_results['influence_matrices']['ccm'] = sa_results['influence_matrices'][m]
                            network_types.append('ccm')
                            print(f"[IMMUNIA] GT: using '{m}' matrix as CCM input")
                            break
                elif available_methods:
                    # Use first available
                    first = available_methods[0]
                    sa_results['influence_matrices']['ccm'] = sa_results['influence_matrices'][first]
                    network_types.append('ccm')
                    print(f"[IMMUNIA] GT: using '{first}' matrix as CCM input")
            
            if str(all_params.get('gt_use_gc', 'false')).lower() == 'true':
                if 'granger' in available_methods:
                    network_types.append('gc')
                    print(f"[IMMUNIA] GT: Granger causality network enabled")
            
            if str(all_params.get('gt_use_correlation', 'false')).lower() == 'true':
                if 'pearson' in available_methods:
                    network_types.append('correlation')
                elif 'ccm' in available_methods:
                    sa_results['influence_matrices']['pearson'] = sa_results['influence_matrices']['ccm']
                    network_types.append('correlation')
            
            if str(all_params.get('gt_use_spatial', 'false')).lower() == 'true':
                network_types.append('spatial')
            if str(all_params.get('gt_use_temporal', 'false')).lower() == 'true':
                network_types.append('temporal')
            if not network_types:
                if available_methods:
                    first = available_methods[0]
                    sa_results['influence_matrices']['ccm'] = sa_results['influence_matrices'][first]
                    network_types = ['ccm']
                else:
                    network_types = ['spatial']

            # ── Build analysis modes ──
            analysis_modes = []
            if str(all_params.get('gt_do_metrics', 'true')).lower() == 'true':
                analysis_modes.append('metrics')
            if str(all_params.get('gt_do_regions', 'true')).lower() == 'true':
                analysis_modes.append('regions')
            if str(all_params.get('gt_do_boundary', 'true')).lower() == 'true':
                analysis_modes.append('boundary')
            if str(all_params.get('gt_do_distance', 'false')).lower() == 'true':
                analysis_modes.append('distance_pairs')
            if str(all_params.get('gt_do_dynamics', 'false')).lower() == 'true':
                analysis_modes.append('dynamics')
            if str(all_params.get('gt_do_comparative', 'false')).lower() == 'true':
                analysis_modes.append('comparative')

            print(f"[IMMUNIA] Graph Theory — {len(track_ids)} tracks, networks={network_types}, modes={analysis_modes}")

            if progress_cb:
                progress_cb(10, 100, 'building', f'Building {len(network_types)} network types...')

            try:
                IMMUNIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'immunia')
                if IMMUNIA_DIR not in sys.path:
                    sys.path.insert(0, IMMUNIA_DIR)
                from components.graph_theory_analyzer import GraphTheoryAnalyzer

                analyzer = GraphTheoryAnalyzer()

                # Monkey-patch slow methods with vectorized versions
                from scipy.spatial.distance import cdist

                def _fast_min_dist(self, traj1, traj2):
                    """Vectorized min distance — 100x faster than double loop."""
                    return cdist(traj1, traj2).min()
                analyzer._compute_min_trajectory_distance = lambda t1, t2: cdist(t1, t2).min()

                # Pre-compute centroids for early filtering
                centroids = np.array([np.mean(t, axis=0) for t in trajectories])
                centroid_dists = cdist(centroids, centroids)

                # Fast spatial builder with centroid pre-filter
                def _fast_spatial(trajs, tids, radius):
                    import networkx as nx
                    G = nx.Graph()
                    for i, tid in enumerate(tids):
                        G.add_node(tid, index=i)
                    n = len(trajs)
                    checked = 0
                    for i in range(n):
                        for j in range(i+1, n):
                            # Skip if centroids too far (2x radius as safety margin)
                            if centroid_dists[i, j] > 2 * radius:
                                continue
                            min_d = cdist(trajs[i], trajs[j]).min()
                            if min_d < radius:
                                G.add_edge(tids[i], tids[j], weight=1.0/max(min_d, 0.1), distance=min_d)
                        checked += 1
                        if progress_cb and checked % 50 == 0:
                            progress_cb(10 + int(30 * checked / n), 100, 'spatial', f'Spatial: {checked}/{n} tracks')
                    node_m = analyzer._calculate_node_metrics(G)
                    graph_m = analyzer._calculate_graph_metrics(G)
                    return {'graphs': {'aggregated': G},
                            'node_metrics': {0: analyzer._transform_node_metrics_to_frame_format(node_m)},
                            'graph_metrics': {'aggregated': graph_m}}

                # Fast temporal builder
                def _fast_temporal(trajs, tids, window):
                    import networkx as nx
                    G = nx.Graph()
                    for i, tid in enumerate(tids):
                        G.add_node(tid, index=i)
                    n = len(trajs)
                    for i in range(n):
                        for j in range(i+1, n):
                            overlap = min(len(trajs[i]), len(trajs[j]))
                            if overlap >= window:
                                G.add_edge(tids[i], tids[j], weight=overlap, overlap=overlap)
                        if progress_cb and i % 50 == 0:
                            progress_cb(40 + int(20 * i / n), 100, 'temporal', f'Temporal: {i}/{n} tracks')
                    node_m = analyzer._calculate_node_metrics(G)
                    graph_m = analyzer._calculate_graph_metrics(G)
                    return {'graphs': {'aggregated': G},
                            'node_metrics': {0: analyzer._transform_node_metrics_to_frame_format(node_m)},
                            'graph_metrics': {'aggregated': graph_m}}

                analyzer._build_spatial_proximity_graphs = _fast_spatial
                analyzer._build_temporal_cooccurrence_graphs = _fast_temporal
                print(f"[IMMUNIA] GT: using vectorized network builders (cdist)")

                gt_results = analyzer.run_analysis(
                    prepared_data=prepared_data,
                    dataset_name='immunia_run',
                    network_types=network_types,
                    analysis_modes=analysis_modes,
                    ccm_threshold=float(all_params.get('ccm_threshold', 0.3)),
                    gc_threshold=float(all_params.get('gc_threshold', 0.05)),
                    correlation_threshold=float(all_params.get('correlation_threshold', 0.5)),
                    spatial_radius=float(all_params.get('spatial_radius', 100)),
                    temporal_window=int(all_params.get('temporal_window', 10)),
                    min_overlap=int(all_params.get('gt_min_overlap', 20)),
                    distance_mode=all_params.get('distance_mode', 'remote'),
                    min_distance=float(all_params.get('gt_min_distance', 250)),
                    max_distance=float(all_params.get('gt_max_distance', 100)),
                    max_pairs=int(all_params.get('gt_max_pairs', 10)),
                )

                if 'error' in gt_results:
                    return {"status": "error", "error_msg": gt_results['error']}

                # Save to timestamped run folder
                from datetime import datetime
                run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                run_dir = results_dir / 'runs' / run_id
                os.makedirs(run_dir, exist_ok=True)

                with open(run_dir / 'graph_theory_results.pkl', 'wb') as f:
                    pickle.dump(gt_results, f)

                # Save meta.json for discovery
                import json as _json5
                meta = {
                    'run_id': run_id,
                    'network_types': network_types,
                    'analysis_modes': analysis_modes,
                    'n_tracks': len(track_ids),
                    'source_runs': list(selected_run_ids) if selected_run_ids else 'all',
                    'available_methods': list(sa_results.get('influence_matrices', {}).keys()),
                    'timestamp': datetime.now().isoformat(),
                }
                n_nets = len(gt_results.get('networks', {}))
                meta['n_networks'] = n_nets
                meta['label'] = f"{'+'.join(network_types)} · {len(track_ids)} tracks"
                with open(run_dir / 'meta.json', 'w') as f:
                    _json5.dump(meta, f, indent=2, default=str)

                # Also save to main results_dir for backward compat
                os.makedirs(results_dir, exist_ok=True)
                with open(results_dir / 'graph_theory_results.pkl', 'wb') as f:
                    pickle.dump(gt_results, f)

                if progress_cb:
                    progress_cb(100, 100, 'done', 'Graph theory analysis complete')

                n_nets = len(gt_results.get('networks', {}))
                n_tracks = gt_results.get('n_trajectories', 0)
                msg = f"Graph theory complete — {n_tracks} tracks, {n_nets} network types"
                print(f"\n[IMMUNIA] ✅ {msg}")
                return {"status": "done", "outputs": {"message": msg}}

            except Exception as e:
                import traceback
                traceback.print_exc()
                return {"status": "error", "error_msg": str(e)}

        elif step_id == 'keller_segel':
            import pickle
            import pandas as pd

            seg_dir = project.get_results_dir(ws_id, pipeline_id, 'segment')
            track_dir = project.get_results_dir(ws_id, pipeline_id, 'track')

            if progress_cb:
                progress_cb(0, 100, 'loading', 'Loading segmentation + tracking data...')

            seg_data = {}
            # Tumor + tissue: use time-averaged masks (static spatial layout)
            for rk in ['tumor', 'tissue']:
                avg_path = seg_dir / f'{rk}_avg_mask.npy'
                if avg_path.exists():
                    seg_data[f'{rk}_mask'] = np.load(avg_path)
                    print(f"[IMMUNIA] KS: loaded {rk}_avg_mask (time-averaged)")

            # NK: load full stack for cumulative presence calculation
            nk_masks_path = seg_dir / 'nk_masks.npy'
            if nk_masks_path.exists():
                seg_data['nk_masks'] = np.load(nk_masks_path)
                print(f"[IMMUNIA] KS: loaded nk_masks stack {seg_data['nk_masks'].shape}")

            if 'tumor_mask' not in seg_data:
                return {"status": "error", "error_msg": "No tumor mask found. Run segmentation first."}
            if 'tissue_mask' not in seg_data:
                seg_data['tissue_mask'] = np.ones_like(seg_data['tumor_mask'])

            # Label connected components — binary avg_mask → labeled regions
            from scipy.ndimage import label as ndlabel
            tumor_binary = (seg_data['tumor_mask'] > 0).astype(np.uint8)
            tumor_labeled, n_tumors = ndlabel(tumor_binary)
            seg_data['tumor_mask'] = tumor_labeled
            print(f"[IMMUNIA] KS: labeled {n_tumors} tumor regions from binary mask")

            tracks_pkl = track_dir / 'tracks.pkl'
            tracks_csv = track_dir / 'tracks.csv'
            if tracks_pkl.exists():
                tracks_df = pd.read_pickle(tracks_pkl)
            elif tracks_csv.exists():
                tracks_df = pd.read_csv(tracks_csv)
            else:
                return {"status": "error", "error_msg": "No tracking results. Run tracking first."}

            if not tracks_df.empty:
                tracks_df = tracks_df.reset_index(drop=True if 'frame' in tracks_df.columns else False)

            trajectories = []
            for pid in tracks_df['particle'].unique():
                t = tracks_df[tracks_df['particle'] == pid].sort_values('frame')
                trajectories.append(t[['x', 'y']].values)

            tracking_data = {'trajectories': trajectories}
            print(f"[IMMUNIA] Keller-Segel — {len(trajectories)} tracks, tumor: {seg_data['tumor_mask'].shape}")

            source_type = all_params.get('source_type', 'interface')
            analysis_modes = ['steady_state']
            if all_params.get('analysis_modes', 'steady_state') == 'both':
                analysis_modes = ['steady_state', 'transient']

            ks_config = {
                'source_type': source_type,
                'steady': {
                    'D_C': float(all_params.get('D_C', 100)),
                    'mu': float(all_params.get('mu', 0.1)),
                    'chi': float(all_params.get('chi', 5.0)),
                    'D_N': float(all_params.get('D_N', 1.0)),
                    'dx': float(all_params.get('dx', 1.0)),
                    'dt': float(all_params.get('ks_dt', 0.01)),
                    'max_iter': int(all_params.get('max_iter', 50000)),
                    'tolerance': float(all_params.get('tolerance', 1e-6)),
                    'source_strength': float(all_params.get('source_strength', 10)),
                    'enforce_tissue_mask': str(all_params.get('enforce_tissue_mask', 'true')).lower() == 'true',
                    'tumor_expansion_percent': float(all_params.get('tumor_expansion_percent', 10)),
                },
                'transient': {
                    'T_max': int(all_params.get('T_max', 100)),
                    'dt': float(all_params.get('transient_dt', 0.01)),
                },
                'analysis_modes': analysis_modes,
                'save_plots': False,
            }

            print(f"[IMMUNIA] KS: source={source_type}, D_C={ks_config['steady']['D_C']}, "
                  f"chi={ks_config['steady']['chi']}, mu={ks_config['steady']['mu']}")

            if progress_cb:
                progress_cb(10, 100, 'solving', 'Solving Keller-Segel PDE...')

            try:
                IMMUNIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'immunia')
                if IMMUNIA_DIR not in sys.path:
                    sys.path.insert(0, IMMUNIA_DIR)
                from components.keller_segel_analyzer import KellerSegelAnalyzer

                analyzer = KellerSegelAnalyzer()

                # Override _create_initial_distribution based on user's N0 choice
                n0_source = all_params.get('n0_source', 'cumulative')
                _original_create_N0 = analyzer._create_initial_distribution
                def _custom_N0(measurements, params):
                    if n0_source == 'cumulative':
                        N0 = measurements.get('cumulative_presence', np.zeros((10,10))).astype(np.float32)
                        if N0.max() > 0:
                            N0 = N0 / N0.max()
                        print(f"[IMMUNIA] KS N₀: cumulative presence, nonzero={np.sum(N0>0)} px")
                        return N0
                    elif n0_source == 'uniform':
                        tissue = seg_data.get('tissue_mask', np.ones((10,10)))
                        N0 = (tissue > 0).astype(np.float32)
                        print(f"[IMMUNIA] KS N₀: uniform over tissue, area={np.sum(N0>0)} px")
                        return N0
                    else:
                        return _original_create_N0(measurements, params)
                analyzer._create_initial_distribution = _custom_N0

                # Monkey-patch the solver to add progress + cancellation
                _original_solve = analyzer._solve_chemoattractant_pde
                def _solve_with_progress(source, tissue_mask, params):
                    import numpy as _np
                    D_C = params['D_C']
                    mu = params['mu']
                    dx = params['dx']
                    source_strength = params.get('source_strength', 10.0)
                    enforce_tissue_mask = params.get('enforce_tissue_mask', True)
                    S = source.astype(_np.float32) * source_strength
                    dt_max = 0.25 * dx**2 / D_C
                    dt = min(params['dt'], dt_max)
                    print(f"[IMMUNIA] KS solver: dt={dt:.6f} (max={dt_max:.6f}), {params['max_iter']} iterations")
                    C = _np.zeros_like(source, dtype=_np.float32)
                    update_mask = (tissue_mask > 0).astype(_np.float32) if enforce_tissue_mask else _np.ones_like(tissue_mask, dtype=_np.float32)
                    try:
                        from components.keller_segel_analyzer import compute_laplacian_numba
                        compute_lap = compute_laplacian_numba
                        print("[IMMUNIA] KS solver: using numba-parallel Laplacian")
                    except:
                        def compute_lap(C_arr, dx_val):
                            lap = _np.zeros_like(C_arr)
                            lap[1:-1,1:-1] = (C_arr[2:,1:-1]+C_arr[:-2,1:-1]+C_arr[1:-1,2:]+C_arr[1:-1,:-2]-4*C_arr[1:-1,1:-1])/(dx_val**2)
                            return lap
                        print("[IMMUNIA] KS solver: using numpy vectorized Laplacian (numba unavailable)")
                    max_iter = params['max_iter']
                    for iteration in range(max_iter):
                        if cancel_evt and cancel_evt.is_set():
                            print(f"[IMMUNIA] KS solver cancelled at iteration {iteration}")
                            return C
                        lap = compute_lap(C, dx)
                        update = dt * (D_C * lap + S - mu * C)
                        C_new = C + update * update_mask
                        residual = _np.max(_np.abs(C_new - C))
                        if iteration % 500 == 0:
                            if progress_cb:
                                pct = 10 + int(80 * iteration / max_iter)
                                progress_cb(pct, 100, 'solving', f'PDE iteration {iteration}/{max_iter} · residual={residual:.2e}')
                            print(f"[IMMUNIA] KS iter {iteration}, residual={residual:.2e}, C_max={C.max():.2e}")
                        if residual < params['tolerance']:
                            print(f"[IMMUNIA] KS converged at iteration {iteration} (residual={residual:.2e})")
                            break
                        C = C_new
                    return C
                analyzer._solve_chemoattractant_pde = _solve_with_progress

                results = analyzer.run_analysis(
                    dataset_name='immunia_run',
                    tracking_data=tracking_data,
                    segmentation_data=seg_data,
                    config=ks_config,
                )

                os.makedirs(results_dir, exist_ok=True)
                with open(results_dir / 'keller_segel_results.pkl', 'wb') as f:
                    pickle.dump(results, f)

                validation = results.get('validation', {})
                import json as _json3
                summary = {
                    'config': ks_config,
                    'n_tracks': len(trajectories),
                    'validation': {k: float(v) if isinstance(v, (float, int)) else v
                                   for k, v in validation.items() if not isinstance(v, np.ndarray)},
                }
                with open(results_dir / 'keller_segel_summary.json', 'w') as f:
                    _json3.dump(summary, f, indent=2, default=str)

                if progress_cb:
                    progress_cb(100, 100, 'done', 'Keller-Segel analysis complete')

                r2 = validation.get('r_squared', 0)
                corr = validation.get('correlation', 0)
                msg = f"Keller-Segel complete — R²={r2:.3f}, corr={corr:.3f}"
                print(f"\n[IMMUNIA] ✅ {msg}")
                return {"status": "done", "outputs": {"message": msg}}

            except Exception as e:
                import traceback
                traceback.print_exc()
                return {"status": "error", "error_msg": str(e)}

        else:
            return {"status": "error", "error_msg": f"Step '{step_id}' not yet implemented for IMMUNIA"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "error_msg": str(e)}


def _run_step_async(task_key, project, ws_id, pipeline_id, step_id, p_type, params, results_dir, cancel_evt=None):
    """Run a step in a background thread. Updates _run_progress and stores result in _run_results."""
    import io as _io

    _log_buf = _io.StringIO()
    with _task_logs_lock:
        _task_logs[task_key] = _log_buf

    _old_stdout = sys.stdout
    sys.stdout = TeeWriter(_log_buf, _old_stdout)

    try:
        from datetime import datetime
        run_result = {"status": "done", "outputs": {}}

        # Progress callback for long-running steps
        def progress_cb(current, total, phase='', message=''):
            with _run_progress_lock:
                _run_progress[task_key] = {
                    'status': 'running',
                    'current': current,
                    'total': total,
                    'phase': phase,
                    'message': message,
                    'pct': round(current / max(total, 1) * 100, 1),
                }

        if p_type == 'fastia':
            run_result = _run_fastia(project, ws_id, pipeline_id, step_id, params, results_dir,
                                     progress_cb=progress_cb, cancel_evt=cancel_evt)
        elif p_type == 'cornealia':
            run_result = _run_cornealia(project, ws_id, pipeline_id, step_id, params, results_dir,
                                        progress_cb=progress_cb)
        elif p_type == 'cornealia_batch':
            run_result = _run_cornealia_batch(project, ws_id, pipeline_id, step_id, params, results_dir)
        elif p_type == 'immunia':
            run_result = _run_immunia(project, ws_id, pipeline_id, step_id, params, results_dir,
                                      progress_cb=progress_cb, cancel_evt=cancel_evt)

        # Update pipeline status
        pipeline = project.get_pipeline(ws_id, pipeline_id)
        pipeline_path = project.workspaces_dir / ws_id / pipeline_id / "pipeline.json"
        pipeline["steps"][step_id] = {
            "status": run_result.get("status", "done"),
            "last_run": datetime.now().isoformat(),
        }
        project._write_json(pipeline_path, pipeline)

        run_log = _log_buf.getvalue()
        with _run_progress_lock:
            _run_results[task_key] = {
                "status": run_result.get("status", "done"),
                "pipeline": pipeline_id,
                "step": step_id,
                "results_dir": str(results_dir.relative_to(project.root)),
                "outputs": run_result.get("outputs", {}),
                "error_msg": run_result.get("error_msg"),
                "log": run_log,
            }
            _run_progress[task_key] = {
                'status': 'done',
                'current': 1, 'total': 1,
                'phase': 'complete',
                'message': run_result.get("outputs", {}).get("message", "Done"),
                'pct': 100,
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        with _run_progress_lock:
            _run_results[task_key] = {
                "status": "error",
                "error_msg": str(e),
                "log": _log_buf.getvalue(),
            }
    finally:
        sys.stdout = _old_stdout
        with _task_logs_lock:
            _task_logs.pop(task_key, None)


@app.route('/api/step/<ws_id>/<pipeline_id>/<step_id>/run', methods=['POST'])
def step_run(ws_id, pipeline_id, step_id):
    """
    Run analysis for a pipeline step.
    Returns immediately with task_key. Frontend polls /api/tasks/progress for updates.
    Body: { "params": { ... } }  (optional override)
    """
    task_key = f"{ws_id}/{pipeline_id}/{step_id}"

    # Check if already running
    with _run_progress_lock:
        existing = _run_progress.get(task_key)
        if existing and existing.get('status') == 'running':
            return api_response({"status": "already_running", "task_key": task_key})

    try:
        project = get_project()
        body = request.get_json() or {}

        # Save params if provided (nested or flat format)
        if 'params' in body:
            project.save_params(ws_id, pipeline_id, step_id, body['params'])
        elif body:
            # Frontend sends allParams flat — save as a single section
            flat_params = {k: v for k, v in body.items() if isinstance(v, (str, int, float, bool))}
            if flat_params:
                existing = project.load_params(ws_id, pipeline_id, step_id) or {}
                existing['_run_params'] = flat_params
                project.save_params(ws_id, pipeline_id, step_id, existing)

        # Get pipeline info
        pipeline = project.get_pipeline(ws_id, pipeline_id)
        p_type = pipeline.get('type', '')
        params = project.load_params(ws_id, pipeline_id, step_id)
        results_dir = project.get_results_dir(ws_id, pipeline_id, step_id)

        # Initialize progress and cancel event
        cancel_evt = threading.Event()
        with _run_progress_lock:
            _run_progress[task_key] = {
                'status': 'running',
                'current': 0, 'total': 1,
                'phase': 'starting',
                'message': f'Starting {step_id}...',
                'pct': 0,
            }
            _run_results.pop(task_key, None)  # Clear any old result
            _run_cancel[task_key] = cancel_evt

        # Launch in background thread
        t = threading.Thread(
            target=_run_step_async,
            args=(task_key, project, ws_id, pipeline_id, step_id, p_type, params, results_dir, cancel_evt),
            daemon=True
        )
        t.start()

        return api_response({
            "status": "started",
            "task_key": task_key,
        })

    except Exception as e:
        return api_error(str(e), 500)


# ═════════════════════════════════════════════
# DATA ENDPOINTS
# ═════════════════════════════════════════════


# ═════════════════════════════════════════════
# FA EXAMINATION — plot endpoint
# ═════════════════════════════════════════════

@app.route('/api/step/<ws_id>/<pipeline_id>/association/edge_plot', methods=['POST'])
def association_edge_plot(ws_id, pipeline_id):
    """Generate edge-only plots (velocity heatmap, motion map)."""
    import io as _io
    body = request.get_json() or {}
    plot_type = body.get('plot_type', '')
    _old_stdout = sys.stdout
    _captured = _io.StringIO()
    sys.stdout = _captured

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import pickle as _pkl
        import numpy as np

        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'association')
        edge_pkl = results_dir / 'edge_analysis.pkl'

        if not edge_pkl.exists():
            sys.stdout = _old_stdout
            return api_error("No edge analysis. Run Edge Analysis first.")

        with open(str(edge_pkl), 'rb') as f:
            edge_result = _pkl.load(f)

        sys.path.insert(0, os.path.join(BACKEND_DIR, 'fastia'))
        from plotters.plot_association import fig_edge_velocity_heatmap, fig_edge_motion_map

        fig = None
        filename = ''

        if plot_type == 'edge_velocity_heatmap':
            fig = fig_edge_velocity_heatmap(edge_result)
            filename = 'edge_velocity_heatmap.png'

        elif plot_type == 'edge_motion_map':
            import tifffile
            # Load stack for background
            import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
            file_path = None
            for sk, sv in import_params.items():
                if isinstance(sv, dict) and 'input_file' in sv:
                    file_path = sv['input_file']
            tiff_stack = None
            cache_key_tiff = f"tiff_{ws_id}_{pipeline_id}"
            if not hasattr(app, '_tiff_cache'):
                app._tiff_cache = {}
            if cache_key_tiff in app._tiff_cache:
                tiff_stack = app._tiff_cache[cache_key_tiff]
            elif file_path:
                resolved = project.resolve_data_path(file_path)
                if resolved:
                    tiff_stack = tifffile.imread(str(resolved))
                    if tiff_stack.ndim == 3:
                        tiff_stack = tiff_stack[:, np.newaxis, :, :]
                    app._tiff_cache[cache_key_tiff] = tiff_stack

            cell_mask = None
            det_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')
            mask_path = det_dir / 'cell_mask_3d.npy'
            if mask_path.exists():
                masks_3d = np.load(str(mask_path), allow_pickle=True)
                mid = len(masks_3d) // 2
                cell_mask = masks_3d[mid]

            fig = fig_edge_motion_map(edge_result, stack=tiff_stack, cell_mask=cell_mask)
            filename = 'edge_motion_map.png'

        if fig is None:
            sys.stdout = _old_stdout
            return api_error(f"Unknown edge plot: {plot_type}")

        plots_dir = results_dir / 'plots'
        plots_dir.mkdir(parents=True, exist_ok=True)
        save_path = plots_dir / filename
        fig.savefig(str(save_path), dpi=100, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)

        plot_url = f"/api/step/{ws_id}/{pipeline_id}/association/results/plots/{filename}"
        sys.stdout = _old_stdout
        return api_response({'plot_type': plot_type, 'filename': filename, 'url': plot_url})

    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.stdout = _old_stdout
        return api_error(f"Edge plot error: {str(e)}")
    finally:
        plt.close('all')


@app.route('/api/step/<ws_id>/<pipeline_id>/association/edge_analysis', methods=['POST'])
def association_edge_analysis(ws_id, pipeline_id):
    """Run edge analysis for the cell."""
    try:
        project = get_project()
        body = request.get_json() or {}

        import sys as _sys
        _sys.path.insert(0, os.path.join(BACKEND_DIR, 'fastia'))
        from wrapper_classes.fastia_edge_analyzer import FASTIAEdgeAnalyzer

        config = {
            'num_sectors': int(body.get('edge_num_sectors', 24)),
            'velocity_threshold': float(body.get('edge_vel_threshold', 0)),
            'smoothing_window': int(body.get('edge_smooth_window', 3)),
        }

        analyzer = FASTIAEdgeAnalyzer(project, ws_id, pipeline_id, config)
        result = analyzer.run()

        if 'error' in result:
            return api_error(result['error'])

        analyzer.save_results(result)

        summary = {
            'num_sectors': result['num_sectors'],
            'n_protruding': result['sector_class'].count('protruding'),
            'n_retracting': result['sector_class'].count('retracting'),
            'n_steady': result['sector_class'].count('steady'),
            'n_fa_mapped': len(result['fa_edge_map']),
            'velocity_threshold': result.get('velocity_threshold_used', 0),
            'elapsed_s': result['elapsed_s'],
        }

        return api_response(summary)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/association/runs', methods=['GET'])
def association_list_runs(ws_id, pipeline_id):
    """List all association runs with their metadata."""
    try:
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'association')
        runs_dir = results_dir / 'runs'

        if not runs_dir.exists():
            return api_response({'runs': []})

        runs = []
        for run_path in sorted(runs_dir.iterdir(), reverse=True):
            if not run_path.is_dir() or not run_path.name.startswith('run_'):
                continue
            meta_path = run_path / 'meta.json'
            if meta_path.exists():
                with open(str(meta_path)) as f:
                    meta = json.load(f)
                # Check which plots exist
                plots_dir = run_path / 'plots'
                plot_files = []
                if plots_dir.exists():
                    plot_files = [p.name for p in plots_dir.iterdir() if p.suffix == '.png']
                meta['plot_files'] = plot_files
                meta['run_dir'] = run_path.name
                runs.append(meta)
            else:
                runs.append({'run_id': run_path.name, 'label': run_path.name, 'run_dir': run_path.name})

        return api_response({'runs': runs})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/association/runs/<run_id>', methods=['DELETE'])
def association_delete_run(ws_id, pipeline_id, run_id):
    """Delete an association run."""
    try:
        import shutil
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'association')
        run_dir = results_dir / 'runs' / run_id

        if not run_dir.exists():
            return api_error(f"Run {run_id} not found", 404)

        shutil.rmtree(str(run_dir))
        print(f"[ASSOC] Deleted run: {run_id}")
        return api_response({'deleted': run_id})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/association/runs/<run_id>/plot', methods=['POST'])
def association_run_plot(ws_id, pipeline_id, run_id):
    """Generate a plot for a specific association run."""
    import io as _io
    body = request.get_json() or {}
    plot_type = body.get('plot_type', '')
    _old_stdout = sys.stdout
    _captured = _io.StringIO()
    sys.stdout = _captured

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import pickle as _pkl
        import numpy as np

        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'association')
        run_dir = results_dir / 'runs' / run_id

        if not run_dir.exists():
            sys.stdout = _old_stdout
            return api_error(f"Run {run_id} not found", 404)

        pkl_path = run_dir / 'association_results.pkl'
        if not pkl_path.exists():
            sys.stdout = _old_stdout
            return api_error("No results pickle in this run.")

        with open(str(pkl_path), 'rb') as f:
            assoc_results = _pkl.load(f)

        sys.path.insert(0, os.path.join(BACKEND_DIR, 'fastia'))
        from plotters.plot_association import (
            fig_assoc_significance, fig_assoc_distributions,
            fig_assoc_effect_sizes, fig_assoc_track_detail,
            fig_assoc_method_agreement, fig_assoc_group_coupling,
        )

        pop = assoc_results.get('population', {})
        per_track = assoc_results.get('per_track', {})

        fig = None
        filename = ''

        if plot_type == 'assoc_significance':
            fig = fig_assoc_significance(pop)
            filename = 'assoc_significance.png'
        elif plot_type == 'assoc_distributions':
            fig = fig_assoc_distributions(pop)
            filename = 'assoc_distributions.png'
        elif plot_type == 'assoc_effect_sizes':
            fig = fig_assoc_effect_sizes(pop)
            filename = 'assoc_effect_sizes.png'
        elif plot_type == 'assoc_method_agreement':
            pair_key = body.get('pair_key', '')
            if not pair_key and pop:
                pair_key = list(pop.keys())[0]
            fig = fig_assoc_method_agreement(per_track, pair_key)
            filename = 'assoc_method_agreement.png'
        elif plot_type == 'assoc_group_coupling':
            pair_key = body.get('pair_key', '')
            if not pair_key and pop:
                pair_key = list(pop.keys())[0]
            import pandas as pd
            class_dir = project.get_results_dir(ws_id, pipeline_id, 'classification')
            df_class = None
            df_path = class_dir / 'df_classified.csv'
            if df_path.exists():
                df_class = pd.read_csv(str(df_path))
            fig = fig_assoc_group_coupling(per_track, pair_key, df_class)
            filename = 'assoc_group_coupling.png'
        elif plot_type == 'assoc_track_detail':
            track_id_assoc = int(body.get('track_id', 0))
            pair_key = body.get('pair_key', '')
            track_res = per_track.get(track_id_assoc, {}).get(pair_key, {})
            if not track_res:
                track_res = per_track.get(str(track_id_assoc), {}).get(pair_key, {})
            if not track_res:
                sys.stdout = _old_stdout
                return api_error(f"No results for track {track_id_assoc} pair {pair_key}")
            fig = fig_assoc_track_detail(track_res, track_id_assoc, pair_key)
            filename = f'assoc_track_{track_id_assoc}_{pair_key}.png'

        elif plot_type == 'assoc_spatial_coupling':
            from plotters.plot_association import fig_assoc_spatial_coupling
            import pickle as _pkl2
            import tifffile

            pair_key = body.get('pair_key', '')
            if not pair_key and pop:
                pair_key = list(pop.keys())[0]

            # Load tracks
            track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')
            tracks_path = track_dir / 'tracks.pkl'
            if not tracks_path.exists():
                sys.stdout = _old_stdout
                return api_error("No tracking results.")
            cache_key_trk = f"tracks_{ws_id}_{pipeline_id}"
            if not hasattr(app, '_tracks_cache'):
                app._tracks_cache = {}
            if cache_key_trk not in app._tracks_cache:
                with open(str(tracks_path), 'rb') as f:
                    app._tracks_cache[cache_key_trk] = _pkl2.load(f)
            tracks_list = app._tracks_cache[cache_key_trk]

            # Load labels
            det_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')
            labels_path = det_dir / 'all_labels.npy'
            cache_key_lbl = f"labels:{ws_id}/{pipeline_id}"
            if not hasattr(app, '_labels_cache'):
                app._labels_cache = {}
            if cache_key_lbl not in app._labels_cache and labels_path.exists():
                app._labels_cache[cache_key_lbl] = list(np.load(str(labels_path), allow_pickle=True))
            all_labels = app._labels_cache.get(cache_key_lbl)

            # Load stack (for background image)
            import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
            file_path = None
            for sk, sv in import_params.items():
                if isinstance(sv, dict) and 'input_file' in sv:
                    file_path = sv['input_file']
            tiff_stack = None
            cache_key_tiff = f"tiff_{ws_id}_{pipeline_id}"
            if not hasattr(app, '_tiff_cache'):
                app._tiff_cache = {}
            if cache_key_tiff in app._tiff_cache:
                tiff_stack = app._tiff_cache[cache_key_tiff]
            elif file_path:
                resolved = project.resolve_data_path(file_path)
                if resolved:
                    tiff_stack = tifffile.imread(str(resolved))
                    if tiff_stack.ndim == 3:
                        tiff_stack = tiff_stack[:, np.newaxis, :, :]
                    app._tiff_cache[cache_key_tiff] = tiff_stack

            # Load cell mask if available
            cell_mask = None
            mask_path = det_dir / 'cell_mask_3d.npy'
            if mask_path.exists():
                masks_3d = np.load(str(mask_path), allow_pickle=True)
                mid = len(masks_3d) // 2
                cell_mask = masks_3d[mid]

            fig = fig_assoc_spatial_coupling(
                per_track, pair_key, tracks_list, all_labels,
                stack=tiff_stack, cell_mask=cell_mask
            )
            filename = f'assoc_spatial_{pair_key}.png'

        elif plot_type in ('assoc_edge_pie', 'assoc_edge_spatial'):
            from plotters.plot_association import fig_assoc_edge_pie, fig_assoc_edge_spatial
            import tifffile

            pair_key = body.get('pair_key', '')
            if not pair_key and pop:
                pair_key = list(pop.keys())[0]

            # Load edge analysis from pickle
            assoc_dir = project.get_results_dir(ws_id, pipeline_id, 'association')
            edge_pkl = assoc_dir / 'edge_analysis.pkl'
            if not edge_pkl.exists():
                sys.stdout = _old_stdout
                return api_error("No edge analysis. Run Edge Analysis first (🌊 tab).")

            import pickle as _pkl_edge
            with open(str(edge_pkl), 'rb') as f:
                edge_result = _pkl_edge.load(f)

            fa_edge_map = edge_result.get('fa_edge_map', {})

            if plot_type == 'assoc_edge_pie':
                fig = fig_assoc_edge_pie(per_track, pair_key, fa_edge_map)
                filename = f'assoc_edge_pie_{pair_key}.png'
            else:
                # Need tracks, labels, stack for spatial plot
                import pickle as _pkl2
                track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')
                tracks_path = track_dir / 'tracks.pkl'
                cache_key_trk = f"tracks_{ws_id}_{pipeline_id}"
                if not hasattr(app, '_tracks_cache'):
                    app._tracks_cache = {}
                if cache_key_trk not in app._tracks_cache and tracks_path.exists():
                    with open(str(tracks_path), 'rb') as f:
                        app._tracks_cache[cache_key_trk] = _pkl2.load(f)
                tracks_list = app._tracks_cache.get(cache_key_trk, [])

                det_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')
                labels_path = det_dir / 'all_labels.npy'
                cache_key_lbl = f"labels:{ws_id}/{pipeline_id}"
                if not hasattr(app, '_labels_cache'):
                    app._labels_cache = {}
                if cache_key_lbl not in app._labels_cache and labels_path.exists():
                    app._labels_cache[cache_key_lbl] = list(np.load(str(labels_path), allow_pickle=True))
                all_labels = app._labels_cache.get(cache_key_lbl)

                import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
                file_path = None
                for sk, sv in import_params.items():
                    if isinstance(sv, dict) and 'input_file' in sv:
                        file_path = sv['input_file']
                tiff_stack = None
                cache_key_tiff = f"tiff_{ws_id}_{pipeline_id}"
                if not hasattr(app, '_tiff_cache'):
                    app._tiff_cache = {}
                if cache_key_tiff in app._tiff_cache:
                    tiff_stack = app._tiff_cache[cache_key_tiff]
                elif file_path:
                    resolved = project.resolve_data_path(file_path)
                    if resolved:
                        tiff_stack = tifffile.imread(str(resolved))
                        if tiff_stack.ndim == 3:
                            tiff_stack = tiff_stack[:, np.newaxis, :, :]
                        app._tiff_cache[cache_key_tiff] = tiff_stack

                cell_mask = None
                mask_path = det_dir / 'cell_mask_3d.npy'
                if mask_path.exists():
                    masks_3d = np.load(str(mask_path), allow_pickle=True)
                    mid = len(masks_3d) // 2
                    cell_mask = masks_3d[mid]

                fig = fig_assoc_edge_spatial(
                    per_track, pair_key, fa_edge_map, edge_result,
                    tracks_list, all_labels,
                    stack=tiff_stack, cell_mask=cell_mask
                )
                filename = f'assoc_edge_spatial_{pair_key}.png'

        if fig is None:
            sys.stdout = _old_stdout
            return api_error(f"Unknown association plot: {plot_type}")

        plots_dir = run_dir / 'plots'
        plots_dir.mkdir(parents=True, exist_ok=True)
        save_path = plots_dir / filename
        fig.savefig(str(save_path), dpi=100, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)

        plot_url = f"/api/step/{ws_id}/{pipeline_id}/association/results/runs/{run_id}/plots/{filename}"

        sys.stdout = _old_stdout
        return api_response({
            'plot_type': plot_type,
            'filename': filename,
            'url': plot_url,
            'run_id': run_id,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.stdout = _old_stdout
        return api_error(f"Association plot error: {str(e)}")
    finally:
        plt.close('all')


# ═════════════════════════════════════════════
# IMMUNIA — Signal Association Run Endpoints
# ═════════════════════════════════════════════

@app.route('/api/step/<ws_id>/<pipeline_id>/signal_association/runs', methods=['GET'])
def immunia_assoc_list_runs(ws_id, pipeline_id):
    """List all IMMUNIA signal association runs."""
    try:
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'signal_association')
        runs_dir = results_dir / 'runs'

        if not runs_dir.exists():
            return api_response({'runs': []})

        runs = []
        for run_path in sorted(runs_dir.iterdir(), reverse=True):
            if not run_path.is_dir() or not run_path.name.startswith('run_'):
                continue
            meta_path = run_path / 'meta.json'
            if meta_path.exists():
                with open(str(meta_path)) as f:
                    meta = json.load(f)
                plots_dir = run_path / 'plots'
                plot_files = []
                if plots_dir.exists():
                    plot_files = [p.name for p in plots_dir.iterdir()
                                  if p.suffix in ('.png', '.jpg')]
                meta['plot_files'] = plot_files
                meta['run_dir'] = run_path.name
                runs.append(meta)
            else:
                runs.append({'run_id': run_path.name, 'label': run_path.name,
                            'run_dir': run_path.name})

        return api_response({'runs': runs})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/signal_association/runs/<run_id>', methods=['DELETE'])
def immunia_assoc_delete_run(ws_id, pipeline_id, run_id):
    """Delete an IMMUNIA signal association run."""
    try:
        import shutil
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'signal_association')
        run_dir = results_dir / 'runs' / run_id

        if not run_dir.exists():
            return api_error(f"Run {run_id} not found", 404)

        shutil.rmtree(str(run_dir))
        print(f"[IMMUNIA-Assoc] Deleted run: {run_id}")
        return api_response({'deleted': run_id})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/signal_association/runs/<run_id>/plot', methods=['POST'])
def immunia_assoc_run_plot(ws_id, pipeline_id, run_id):
    """Generate a plot for a specific IMMUNIA association run."""
    import io as _io
    body = request.get_json() or {}
    plot_type = body.get('plot_type', 'comprehensive')
    _old_stdout = sys.stdout
    _captured = _io.StringIO()
    sys.stdout = _captured

    try:
        import matplotlib.pyplot as plt
        import pickle

        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'signal_association')
        run_dir = results_dir / 'runs' / run_id

        if not run_dir.exists():
            sys.stdout = _old_stdout
            return api_error(f"Run {run_id} not found", 404)

        pkl_path = run_dir / 'association_results.pkl'
        if not pkl_path.exists():
            sys.stdout = _old_stdout
            return api_error("No results pickle found", 404)

        with open(pkl_path, 'rb') as f:
            assoc_data = pickle.load(f)

        IMMUNIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'immunia')
        if IMMUNIA_DIR not in sys.path:
            sys.path.insert(0, IMMUNIA_DIR)
        from plotters.signal_association_plotter import SignalAssociationPlotter

        plotter = SignalAssociationPlotter()
        method = assoc_data.get('config', {}).get('method', 'ccm')
        fig = plotter.plot(assoc_data, plot_type=plot_type, method=method)

        plots_dir = run_dir / 'plots'
        plots_dir.mkdir(exist_ok=True)
        filename = f'{plot_type}.png'
        fig.savefig(plots_dir / filename, dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)

        # Update meta.json with new plot file
        meta_path = run_dir / 'meta.json'
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
            existing = meta.get('plot_files', [])
            if filename not in existing:
                existing.append(filename)
                meta['plot_files'] = existing
                with open(meta_path, 'w') as f:
                    json.dump(meta, f, indent=2, default=str)

        plot_url = f"/api/step/{ws_id}/{pipeline_id}/signal_association/results/runs/{run_id}/plots/{filename}"
        sys.stdout = _old_stdout
        return api_response({
            'plot_type': plot_type,
            'filename': filename,
            'url': plot_url,
        })

    except Exception as e:
        sys.stdout = _old_stdout
        import traceback
        traceback.print_exc()
        plt.close('all')
        return api_error(str(e), 500)


@app.route('/api/step/<ws_id>/<pipeline_id>/signal_association/results/runs/<run_id>/plots/<path:filename>')
def immunia_assoc_serve_plot(ws_id, pipeline_id, run_id, filename):
    """Serve an IMMUNIA association run plot file."""
    try:
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'signal_association')
        plots_dir = results_dir / 'runs' / run_id / 'plots'
        return send_from_directory(str(plots_dir), filename)
    except Exception as e:
        return api_error(str(e), 404)


# ── GRAPH THEORY RUN ENDPOINTS ──

@app.route('/api/step/<ws_id>/<pipeline_id>/graph_theory/runs', methods=['GET'])
def gt_list_runs(ws_id, pipeline_id):
    """List all graph theory runs."""
    try:
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'graph_theory')
        runs_dir = results_dir / 'runs'
        if not runs_dir.exists():
            return api_response({'runs': []})
        runs = []
        for run_path in sorted(runs_dir.iterdir(), reverse=True):
            if not run_path.is_dir() or not run_path.name.startswith('run_'):
                continue
            meta_path = run_path / 'meta.json'
            if meta_path.exists():
                with open(str(meta_path)) as f:
                    meta = json.load(f)
                plots_dir = run_path / 'plots'
                plot_files = [p.name for p in plots_dir.iterdir() if p.suffix in ('.png', '.jpg')] if plots_dir.exists() else []
                meta['plot_files'] = plot_files
                meta['run_dir'] = run_path.name
                runs.append(meta)
            else:
                runs.append({'run_id': run_path.name, 'label': run_path.name, 'run_dir': run_path.name})
        return api_response({'runs': runs})
    except Exception as e:
        return api_error(str(e), 500)

@app.route('/api/step/<ws_id>/<pipeline_id>/graph_theory/runs/<run_id>', methods=['DELETE'])
def gt_delete_run(ws_id, pipeline_id, run_id):
    """Delete a graph theory run."""
    try:
        import shutil
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'graph_theory')
        run_dir = results_dir / 'runs' / run_id
        if run_dir.exists():
            shutil.rmtree(str(run_dir))
        return api_response({'deleted': run_id})
    except Exception as e:
        return api_error(str(e), 500)

@app.route('/api/step/<ws_id>/<pipeline_id>/graph_theory/runs/<run_id>/plot', methods=['POST'])
def gt_run_plot(ws_id, pipeline_id, run_id):
    """Generate a plot for a specific GT run."""
    try:
        import pickle, matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        project = get_project()
        body = request.get_json() or {}
        plot_type = body.get('plot_type', 'comprehensive')
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'graph_theory')
        run_dir = results_dir / 'runs' / run_id
        pkl_path = run_dir / 'graph_theory_results.pkl'
        if not pkl_path.exists():
            return api_error(f"No results for run {run_id}", 404)

        import importlib, sys
        IMMUNIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'immunia')
        if IMMUNIA_DIR not in sys.path:
            sys.path.insert(0, IMMUNIA_DIR)
        for mod_name in [k for k in sys.modules if 'graph_theory_plotter' in k]:
            importlib.reload(sys.modules[mod_name])
        from plotters.graph_theory_plotter import GraphTheoryPlotter
        plotter = GraphTheoryPlotter()
        fig = plotter.plot(str(run_dir), plot_type=plot_type)

        plots_dir = run_dir / 'plots'
        plots_dir.mkdir(parents=True, exist_ok=True)
        filename = f'{plot_type}.png'
        fig.savefig(plots_dir / filename, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close(fig)

        plot_url = f"/api/step/{ws_id}/{pipeline_id}/graph_theory/results/runs/{run_id}/plots/{filename}"
        return api_response({'url': plot_url, 'filename': filename})
    except Exception as e:
        import traceback; traceback.print_exc()
        return api_error(str(e), 500)

@app.route('/api/step/<ws_id>/<pipeline_id>/graph_theory/results/runs/<run_id>/plots/<path:filename>')
def gt_serve_plot(ws_id, pipeline_id, run_id, filename):
    """Serve a GT run plot file."""
    try:
        project = get_project()
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'graph_theory')
        plots_dir = results_dir / 'runs' / run_id / 'plots'
        return send_from_directory(str(plots_dir), filename)
    except Exception as e:
        return api_error(str(e), 404)


@app.route('/api/step/<ws_id>/<pipeline_id>/examination/plot', methods=['POST'])
def examination_plot(ws_id, pipeline_id):
    """Generate detailed FA analysis figure for a single track."""
    try:
        import pickle
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec

        project = get_project()
        body = request.get_json() or {}
        plot_type = body.get('plot_type', '')
        track_id = int(body.get('track_id', 0))

        if plot_type != 'exam_detailed':
            return api_error(f"Unknown exam plot type: {plot_type}")

        # Results/plots dir
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'examination')
        results_dir.mkdir(parents=True, exist_ok=True)
        plots_dir = results_dir / 'plots'
        plots_dir.mkdir(exist_ok=True)

        # Load tracks (cached)
        track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')
        tracks_path = track_dir / 'tracks.pkl'
        if not tracks_path.exists():
            return api_error("No tracking results.")

        cache_key_trk = f"tracks_{ws_id}_{pipeline_id}"
        if not hasattr(app, '_tracks_cache'):
            app._tracks_cache = {}
        if cache_key_trk not in app._tracks_cache:
            with open(str(tracks_path), 'rb') as f:
                app._tracks_cache[cache_key_trk] = pickle.load(f)
        tracks_list = app._tracks_cache[cache_key_trk]

        # Find track by ID
        idx_key = cache_key_trk + '_idx'
        if idx_key not in app._tracks_cache:
            lookup = {}
            for ti, t in enumerate(tracks_list):
                tid = t[0].get('id', ti) if t else ti
                lookup[int(float(str(tid)))] = ti
            app._tracks_cache[idx_key] = lookup
        tid_lookup = app._tracks_cache[idx_key]

        list_idx = tid_lookup.get(track_id)
        if list_idx is None:
            return api_error(f"Track {track_id} not found")

        track = tracks_list[list_idx]

        # Load stack + labels (cached)
        import tifffile
        import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
        file_path = None
        ch_params_plot = {}
        for sk, sv in import_params.items():
            if isinstance(sv, dict):
                if 'input_file' in sv: file_path = sv['input_file']
                if 'ch1_name' in sv: ch_params_plot = sv

        stack = None
        if file_path:
            resolved = project.resolve_data_path(file_path)
            if resolved:
                cache_key = str(resolved)
                if not hasattr(app, '_tiff_cache'):
                    app._tiff_cache = {}
                if cache_key not in app._tiff_cache:
                    app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
                raw = app._tiff_cache[cache_key]
                det_params_all = project.load_params(ws_id, pipeline_id, 'detection') or {}
                det_ch = 'vinculin'
                for sk2, sv2 in det_params_all.items():
                    if isinstance(sv2, dict) and 'detection_channel' in sv2:
                        det_ch = sv2['detection_channel']
                c_idx = 0
                for i in range(1, 5):
                    if ch_params_plot.get(f'ch{i}_name', '').lower() == det_ch.lower():
                        c_idx = i - 1
                        break
                stack = raw[:, c_idx, :, :] if raw.ndim == 4 else raw

        det_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')
        labels_cache_key = f"{ws_id}_{pipeline_id}_labels"
        if not hasattr(app, '_labels_cache'):
            app._labels_cache = {}
        labels_path = det_dir / 'all_labels.npy'
        if labels_cache_key in app._labels_cache:
            all_labels = app._labels_cache[labels_cache_key]
        elif labels_path.exists():
            all_labels = list(np.load(str(labels_path), allow_pickle=True))
            app._labels_cache[labels_cache_key] = all_labels
        else:
            all_labels = None

        if stack is None or all_labels is None:
            return api_error("Image stack or labels not available.")

        # Load classification info
        class_dir = project.get_results_dir(ws_id, pipeline_id, 'classification')
        df_class_path = class_dir / 'df_classified.csv'
        track_info = {}
        if df_class_path.exists():
            import pandas as pd
            df = pd.read_csv(str(df_class_path))
            row = df[df['track_id'].astype(float).astype(int) == track_id]
            if len(row) > 0:
                track_info = row.iloc[0].to_dict()

        # Get imaging params
        pixel_size_um = 0.108
        t_interval = 10.0
        for sk, sv in import_params.items():
            if isinstance(sv, dict):
                if 'pixel_size_um' in sv:
                    try: pixel_size_um = float(sv['pixel_size_um'])
                    except: pass
                if 't_interval' in sv:
                    try: t_interval = float(sv['t_interval'])
                    except: pass

        # ── Generate 6-panel figure ──
        n_det = len(track)
        frames = [int(d['frame']) for d in track]
        centroids = [(d['centroid'][1], d['centroid'][0]) for d in track]  # (x, y)

        # Extract intensities
        intensities = []
        areas = []
        for det in track:
            f_idx = int(det['frame'])
            label_id = det.get('label_id', 0)
            if label_id > 0 and f_idx < len(all_labels):
                mask = (all_labels[f_idx] == label_id)
                val = np.mean(stack[f_idx][mask]) if np.any(mask) else 0.0
                area = np.sum(mask) * (pixel_size_um ** 2)
            else:
                val = 0.0
                area = 0.0
            intensities.append(val)
            areas.append(area)

        fig = plt.figure(figsize=(18, 12))
        gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

        group = track_info.get('group', '?')
        fig.suptitle(f'FA Detailed Analysis — Track {track_id} · {group} · {n_det} frames',
                     fontsize=14, fontweight='bold', y=0.98)

        # ── Panel 1-3: Zoomed FA crops at start, peak, end ──
        peak_idx = int(np.argmax(intensities))
        key_frames = [
            (0, 'Start', frames[0]),
            (peak_idx, 'Peak', frames[peak_idx]),
            (n_det - 1, 'End', frames[-1])
        ]

        crop_size = 40  # pixels around centroid
        for panel_i, (det_idx, label, frame_num) in enumerate(key_frames):
            ax = fig.add_subplot(gs[0, panel_i])
            cx, cy = centroids[det_idx]
            y0 = max(0, int(cy) - crop_size)
            y1 = min(stack.shape[1], int(cy) + crop_size)
            x0 = max(0, int(cx) - crop_size)
            x1 = min(stack.shape[2], int(cx) + crop_size)

            crop = stack[frame_num, y0:y1, x0:x1].astype(np.float32)
            p_low, p_high = np.percentile(crop, (1, 99))
            if p_high > p_low:
                crop = np.clip((crop - p_low) / (p_high - p_low), 0, 1)

            ax.imshow(crop, cmap='gray', interpolation='bilinear')

            # Draw FA outline from labels
            label_id = track[det_idx].get('label_id', 0)
            if label_id > 0 and frame_num < len(all_labels):
                label_crop = all_labels[frame_num][y0:y1, x0:x1]
                fa_mask = (label_crop == label_id)
                if np.any(fa_mask):
                    from scipy.ndimage import binary_erosion
                    outline = fa_mask & ~binary_erosion(fa_mask)
                    ax.contour(outline, colors=['#00ff88'], linewidths=1.5)

            ax.set_title(f'{label} (f{frame_num})\nI={intensities[det_idx]:.1f}  A={areas[det_idx]:.2f}μm²',
                         fontsize=10)
            ax.axis('off')

        # ── Panel 4: Intensity time series ──
        ax4 = fig.add_subplot(gs[1, :2])
        t_min = np.array(frames) * t_interval / 60.0
        ax4.plot(t_min, intensities, 'o-', color='#3498db', markersize=3, linewidth=1.5, label='Raw')
        ax4.axvline(t_min[peak_idx], color='#e74c3c', ls='--', alpha=0.5, label=f'Peak (f{frames[peak_idx]})')
        ax4.set_xlabel('Time (min)', fontsize=10)
        ax4.set_ylabel('Mean Intensity (a.u.)', fontsize=10)
        ax4.set_title('Intensity Time Series', fontsize=11, fontweight='bold')
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)

        # ── Panel 5: Area time series ──
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.fill_between(t_min, areas, alpha=0.3, color='#2ecc71')
        ax5.plot(t_min, areas, '-', color='#2ecc71', linewidth=1.5)
        ax5.set_xlabel('Time (min)', fontsize=10)
        ax5.set_ylabel('Area (μm²)', fontsize=10)
        ax5.set_title('Area Over Time', fontsize=11, fontweight='bold')
        ax5.grid(True, alpha=0.3)

        # ── Panel 6: Kinetic fit (reuse fig_track_rates logic) ──
        ax6 = fig.add_subplot(gs[2, :2])
        try:
            from components.kinetic_rates import calculate_kinetic_rates
            kr = calculate_kinetic_rates(intensities, t_interval_seconds=t_interval)
            y_smooth = kr.get('y_smooth')
            t_kr = kr.get('t_minutes')
            peak_kr = kr.get('peak_idx', peak_idx)

            if t_kr is not None and y_smooth is not None:
                ax6.plot(t_kr, kr['y_corrected'], 'o', color='#bdc3c7', markersize=2, alpha=0.5, label='Raw')
                ax6.plot(t_kr, y_smooth, '-', color='#3498db', linewidth=2, label='Smoothed')
                ax6.axvline(t_kr[peak_kr], color='#e74c3c', ls='--', alpha=0.6, label='Peak')

                # Assembly phase
                if peak_kr > 1:
                    ax6.fill_betweenx([min(y_smooth), max(y_smooth)], t_kr[0], t_kr[peak_kr],
                                      alpha=0.05, color='#27ae60')
                    ax6.text(t_kr[peak_kr // 2], max(y_smooth) * 0.95, 'Assembly',
                             ha='center', fontsize=8, color='#27ae60')
                # Disassembly phase
                if peak_kr < len(t_kr) - 2:
                    ax6.fill_betweenx([min(y_smooth), max(y_smooth)], t_kr[peak_kr], t_kr[-1],
                                      alpha=0.05, color='#e74c3c')
                    ax6.text(t_kr[(peak_kr + len(t_kr)) // 2], max(y_smooth) * 0.95, 'Disassembly',
                             ha='center', fontsize=8, color='#e74c3c')

            ax6.set_xlabel('Time (min)', fontsize=10)
            ax6.set_ylabel('Intensity', fontsize=10)
            ax6.set_title(f'Kinetic Fit  (k_on={kr["assembly_rate"]:.4f}, k_off={kr["disassembly_rate"]:.4f})',
                          fontsize=11, fontweight='bold')
            ax6.legend(fontsize=8)
            ax6.grid(True, alpha=0.3)
        except Exception as e:
            ax6.text(0.5, 0.5, f'Kinetic fit failed:\n{e}', ha='center', va='center', fontsize=10)
            ax6.axis('off')

        # ── Panel 7: Feature summary table ──
        ax7 = fig.add_subplot(gs[2, 2])
        ax7.axis('off')
        if track_info:
            features = [
                ('Group', group),
                ('Lifetime (frames)', f"{n_det}"),
                ('Frames', f"{frames[0]} → {frames[-1]}"),
                ('Assembly rate', f"{track_info.get('assembly_rate', 'N/A')}"),
                ('Assembly R²', f"{track_info.get('assembly_r_squared', 'N/A')}"),
                ('Disassembly rate', f"{track_info.get('disassembly_rate', 'N/A')}"),
                ('Disassembly R²', f"{track_info.get('disassembly_r_squared', 'N/A')}"),
                ('Mean intensity', f"{np.mean(intensities):.1f}"),
                ('Peak intensity', f"{np.max(intensities):.1f}"),
                ('Mean area (μm²)', f"{np.mean(areas):.3f}"),
                ('Max area (μm²)', f"{np.max(areas):.3f}"),
                ('Edge dist (μm)', f"{track_info.get('mean_edge_distance', 'N/A')}"),
                ('Displacement (μm)', f"{track_info.get('displacement', 'N/A')}"),
                ('Persistence', f"{track_info.get('persistence', 'N/A')}"),
            ]
            table = ax7.table(
                cellText=[[v] for _, v in features],
                rowLabels=[k for k, _ in features],
                colLabels=['Value'],
                cellLoc='center', rowLoc='right',
                loc='center',
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.3)
            for key, cell in table.get_celld().items():
                cell.set_edgecolor('#555')
                if key[0] == 0:
                    cell.set_facecolor('#3498db')
                    cell.set_text_props(color='white', fontweight='bold')
                else:
                    cell.set_facecolor('#1a1a1a' if key[0] % 2 else '#2c3e50')
                    cell.set_text_props(color='white')
            ax7.set_title('Feature Summary', fontsize=11, fontweight='bold')

        # Save
        filename = f'exam_detail_{track_id}.png'
        save_path = plots_dir / filename
        fig.savefig(str(save_path), dpi=100, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)

        plot_url = f"/api/step/{ws_id}/{pipeline_id}/examination/results/plots/{filename}"
        return api_response({
            'plot_type': 'exam_detailed',
            'track_id': track_id,
            'filename': filename,
            'url': plot_url,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return api_error(str(e))


# ═════════════════════════════════════════════
# FA EXAMINATION — dynamic viewer markers (persistence)
# ═════════════════════════════════════════════

@app.route('/api/step/<ws_id>/<pipeline_id>/examination/save_dynamic_marker', methods=['POST'])
def examination_save_dynamic_marker(ws_id, pipeline_id):
    """Save a marker file so dynamic viewers persist across sessions."""
    try:
        project = get_project()
        body = request.get_json() or {}
        track_id = int(body.get('track_id', 0))
        group = body.get('group', '?')

        results_dir = project.get_results_dir(ws_id, pipeline_id, 'examination')
        results_dir.mkdir(parents=True, exist_ok=True)
        plots_dir = results_dir / 'plots'
        plots_dir.mkdir(exist_ok=True)

        marker_path = plots_dir / f'exam_dynamic_{track_id}.json'
        import json
        with open(str(marker_path), 'w') as f:
            json.dump({
                'track_id': track_id,
                'group': group,
                'type': 'dynamic',
                'montage_url': f"/api/step/{ws_id}/{pipeline_id}/examination/results/plots/exam_dynamic_{track_id}_montage_ch0_z4.jpg",
                'timeseries_url': f"/api/step/{ws_id}/{pipeline_id}/examination/results/plots/exam_dynamic_{track_id}_timeseries.jpg",
            }, f)

        return api_response({'saved': True, 'track_id': track_id})
    except Exception as e:
        return api_error(str(e))


# ═════════════════════════════════════════════
# FA EXAMINATION — dynamic panels (montage + timeseries)
# ═════════════════════════════════════════════

@app.route('/api/step/<ws_id>/<pipeline_id>/examination/dynamic_panels', methods=['POST'])
def examination_dynamic_panels(ws_id, pipeline_id):
    """Generate montage + multi-channel timeseries for dynamic viewer. Cached."""
    try:
        import pickle
        import numpy as np
        import io, base64
        from PIL import Image, ImageDraw
        import time as _time

        t0 = _time.time()
        project = get_project()
        body = request.get_json() or {}
        track_id = int(body.get('track_id', 0))
        channel_idx = int(body.get('channel', 0))
        zoom = int(body.get('zoom', 4))

        # Backend cache
        cache_key_panels = f"dynpanel_{ws_id}_{pipeline_id}_{track_id}_{channel_idx}_{zoom}"
        if not hasattr(app, '_dynpanel_cache'):
            app._dynpanel_cache = {}
        if cache_key_panels in app._dynpanel_cache:
            return api_response(app._dynpanel_cache[cache_key_panels])

        # Load tracks (cached)
        cache_key_trk = f"tracks_{ws_id}_{pipeline_id}"
        if not hasattr(app, '_tracks_cache'):
            app._tracks_cache = {}
        if cache_key_trk not in app._tracks_cache:
            track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')
            with open(str(track_dir / 'tracks.pkl'), 'rb') as f:
                app._tracks_cache[cache_key_trk] = pickle.load(f)
        tracks_list = app._tracks_cache[cache_key_trk]

        idx_key = cache_key_trk + '_idx'
        if idx_key not in app._tracks_cache:
            lookup = {}
            for ti, t in enumerate(tracks_list):
                tid = t[0].get('id', ti) if t else ti
                lookup[int(float(str(tid)))] = ti
            app._tracks_cache[idx_key] = lookup
        list_idx = app._tracks_cache[idx_key].get(track_id)
        if list_idx is None:
            return api_error(f"Track {track_id} not found")
        track = tracks_list[list_idx]

        # Load raw stack
        import tifffile
        import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
        file_path = None
        ch_params = {}
        for sk, sv in import_params.items():
            if isinstance(sv, dict):
                if 'input_file' in sv: file_path = sv['input_file']
                if 'ch1_name' in sv: ch_params = sv

        raw_stack = None
        if file_path:
            resolved = project.resolve_data_path(file_path)
            if resolved:
                ck = str(resolved)
                if not hasattr(app, '_tiff_cache'):
                    app._tiff_cache = {}
                if ck not in app._tiff_cache:
                    app._tiff_cache[ck] = tifffile.imread(str(resolved))
                raw_stack = app._tiff_cache[ck]

        if raw_stack is None:
            return api_error("Image stack not available")

        if raw_stack.ndim == 4:
            _, n_channels, imgH, imgW = raw_stack.shape
        elif raw_stack.ndim == 3:
            _, imgH, imgW = raw_stack.shape
            n_channels = 1
            raw_stack = raw_stack[:, np.newaxis, :, :]
        else:
            return api_error(f"Unsupported shape")

        channel_names = []
        for i in range(1, 5):
            nm = ch_params.get(f'ch{i}_name', '')
            if nm: channel_names.append(nm)
        while len(channel_names) < n_channels:
            channel_names.append(f'Ch {len(channel_names)}')

        t_interval = 10.0
        for sk, sv in import_params.items():
            if isinstance(sv, dict) and 't_interval' in sv:
                try: t_interval = float(sv['t_interval'])
                except: pass

        # Labels (cached)
        labels_cache_key = f"{ws_id}_{pipeline_id}_labels"
        if not hasattr(app, '_labels_cache'):
            app._labels_cache = {}
        det_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')
        lp = det_dir / 'all_labels.npy'
        if labels_cache_key in app._labels_cache:
            all_labels = app._labels_cache[labels_cache_key]
        elif lp.exists():
            all_labels = list(np.load(str(lp), allow_pickle=True))
            app._labels_cache[labels_cache_key] = all_labels
        else:
            all_labels = None

        frames = [int(d['frame']) for d in track]
        centroids = [(float(d['centroid'][1]), float(d['centroid'][0])) for d in track]
        n_det = len(frames)

        # ── MONTAGE (PIL — fast) ──
        n_montage = min(10, n_det)
        sample_indices = np.linspace(0, n_det - 1, n_montage, dtype=int)
        crop_half = max(16, min(imgW // 2, imgW // (2 * max(zoom, 1))))
        thumb_size = 100
        n_cols = 5
        n_rows = int(np.ceil(n_montage / n_cols))
        ch = min(channel_idx, n_channels - 1)

        montage_w = n_cols * (thumb_size + 2) + 2
        montage_h = n_rows * (thumb_size + 18) + 24
        montage = Image.new('RGB', (montage_w, montage_h), (26, 26, 26))
        draw = ImageDraw.Draw(montage)
        draw.text((montage_w // 2, 4), f'{channel_names[ch]} — Track {track_id}',
                   fill=(243, 156, 18), anchor='mt')

        for pi, det_i in enumerate(sample_indices):
            row, col = divmod(pi, n_cols)
            f = frames[det_i]
            cx, cy = centroids[det_i]
            y0, y1 = max(0, int(cy) - crop_half), min(imgH, int(cy) + crop_half)
            x0, x1 = max(0, int(cx) - crop_half), min(imgW, int(cx) + crop_half)
            crop = raw_stack[f, ch, y0:y1, x0:x1].astype(np.float32)
            p_lo, p_hi = np.percentile(crop, (1, 99))
            if p_hi > p_lo:
                crop = np.clip((crop - p_lo) / (p_hi - p_lo) * 255, 0, 255).astype(np.uint8)
            else:
                crop = np.zeros_like(crop, dtype=np.uint8)
            thumb = Image.fromarray(crop).resize((thumb_size, thumb_size), Image.BILINEAR)
            px = col * (thumb_size + 2) + 2
            py = row * (thumb_size + 18) + 22
            montage.paste(thumb, (px, py))

            # Draw green circle around FA area
            label_id = track[det_i].get('label_id', 0)
            crop_h, crop_w = y1 - y0, x1 - x0
            scale = thumb_size / max(crop_w, crop_h, 1)
            center_tx = px + int((cx - x0) * scale)
            center_ty = py + int((cy - y0) * scale)
            # Get radius from label mask area
            fa_r = 8  # default
            if label_id > 0 and all_labels is not None and f < len(all_labels):
                fa_pixels = np.sum(all_labels[f][y0:y1, x0:x1] == label_id)
                if fa_pixels > 0:
                    fa_r = max(4, int(np.sqrt(fa_pixels / np.pi) * scale))
            draw.ellipse([center_tx - fa_r, center_ty - fa_r,
                          center_tx + fa_r, center_ty + fa_r],
                         outline=(0, 255, 136), width=2)

            draw.text((px + thumb_size // 2, py + thumb_size + 2), f'f{f}',
                       fill=(180, 180, 180), anchor='mt')

        buf_m = io.BytesIO()
        montage.save(buf_m, format='JPEG', quality=85)
        montage_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf_m.getvalue()).decode()}"

        # ── TIMESERIES (cached per track, channel-independent) ──
        ts_cache_key = f"dynts_{ws_id}_{pipeline_id}_{track_id}"
        if ts_cache_key in app._dynpanel_cache:
            timeseries_b64 = app._dynpanel_cache[ts_cache_key]
        else:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            n_ch_plot = min(n_channels, 3)  # max 3 channels + 1 overlay = 4 panels
            n_panels = n_ch_plot + 1  # +1 for overlay
            n_ts_rows = 2
            n_ts_cols = 2
            fig_t, axes_flat = plt.subplots(n_ts_rows, n_ts_cols,
                                             figsize=(14, 8), sharex=True)
            axes_flat = axes_flat.flatten()
            t_min = np.array(frames) * t_interval / 60.0
            ch_colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']

            all_ch_i = {}
            for ci in range(n_ch_plot):
                vals = []
                for di, det in enumerate(track):
                    fi = frames[di]
                    lid = det.get('label_id', 0)
                    if lid > 0 and all_labels is not None and fi < len(all_labels):
                        mask = (all_labels[fi] == lid)
                        v = float(np.mean(raw_stack[fi, ci][mask])) if np.any(mask) else 0.0
                    else:
                        v = 0.0
                    vals.append(v)
                all_ch_i[ci] = vals
                ax = axes_flat[ci]
                ax.plot(t_min, vals, '-o', color=ch_colors[ci % 4], markersize=3, linewidth=1.5)
                ax.set_ylabel('Intensity', fontsize=9)
                ax.set_title(channel_names[ci], fontsize=11, fontweight='bold', color=ch_colors[ci % 4])
                ax.set_xlabel('Time (min)', fontsize=9)
                ax.grid(True, alpha=0.3)
                ax.tick_params(labelsize=8)

            # Overlay panel (last)
            ax_ov = axes_flat[n_ch_plot]
            for ci in range(n_ch_plot):
                va = np.array(all_ch_i[ci])
                vn, vx = np.nanmin(va), np.nanmax(va)
                norm = (va - vn) / (vx - vn) if vx > vn else np.zeros_like(va)
                ax_ov.plot(t_min, norm, '-', color=ch_colors[ci % 4],
                           linewidth=1.5, label=channel_names[ci], alpha=0.8)
            ax_ov.set_ylabel('Normalized', fontsize=9)
            ax_ov.set_xlabel('Time (min)', fontsize=9)
            ax_ov.set_title('Overlaid (normalized)', fontsize=11, fontweight='bold', color='#f39c12')
            ax_ov.legend(fontsize=8, loc='upper right')
            ax_ov.grid(True, alpha=0.3)
            ax_ov.tick_params(labelsize=8)

            # Hide unused panels
            for pi in range(n_panels, n_ts_rows * n_ts_cols):
                axes_flat[pi].axis('off')

            fig_t.suptitle(f'Multi-Channel Intensity — Track {track_id}',
                           fontsize=12, fontweight='bold', color='white', y=1.0)
            fig_t.patch.set_facecolor('#1a1a1a')
            for ax in axes_flat:
                ax.set_facecolor('#1a1a1a')
                ax.tick_params(colors='#ccc')
                ax.xaxis.label.set_color('#ccc')
                ax.yaxis.label.set_color('#ccc')
                for sp in ax.spines.values(): sp.set_color('#555')
            fig_t.tight_layout()

            buf_t = io.BytesIO()
            fig_t.savefig(buf_t, format='jpeg', dpi=80, bbox_inches='tight',
                          facecolor='#1a1a1a', edgecolor='none')
            plt.close(fig_t)
            timeseries_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf_t.getvalue()).decode()}"
            app._dynpanel_cache[ts_cache_key] = timeseries_b64

        result = {
            'montage': montage_b64,
            'timeseries': timeseries_b64,
            'montage_frames': [int(frames[i]) for i in sample_indices],
            'channel_names': channel_names[:min(n_channels, 4)],
            'n_channels': min(n_channels, 4),
        }
        app._dynpanel_cache[cache_key_panels] = result

        # Save to disk for instant reload after refresh
        results_dir = project.get_results_dir(ws_id, pipeline_id, 'examination')
        results_dir.mkdir(parents=True, exist_ok=True)
        plots_dir = results_dir / 'plots'
        plots_dir.mkdir(exist_ok=True)

        montage_file = plots_dir / f'exam_dynamic_{track_id}_montage_ch{channel_idx}_z{zoom}.jpg'
        ts_file = plots_dir / f'exam_dynamic_{track_id}_timeseries.jpg'

        buf_m.seek(0)
        with open(str(montage_file), 'wb') as f:
            f.write(buf_m.getvalue())

        if not ts_file.exists():
            buf_t.seek(0)
            with open(str(ts_file), 'wb') as f:
                f.write(buf_t.getvalue())

        # Add URLs for direct file access
        result['montage_url'] = f"/api/step/{ws_id}/{pipeline_id}/examination/results/plots/{montage_file.name}"
        result['timeseries_url'] = f"/api/step/{ws_id}/{pipeline_id}/examination/results/plots/{ts_file.name}"

        elapsed = _time.time() - t0
        print(f"[EXAM] dynamic_panels: track {track_id} ch={channel_idx} zoom={zoom} in {elapsed:.1f}s")
        return api_response(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return api_error(str(e))


# ═════════════════════════════════════════════
# FA EXAMINATION — per-track frame data
# ═════════════════════════════════════════════

@app.route('/api/step/<ws_id>/<pipeline_id>/examination/track_frames', methods=['POST'])
def examination_track_frames(ws_id, pipeline_id):
    """Return per-frame stats for a single track (for dynamic viewer)."""
    try:
        import pickle
        import numpy as np

        project = get_project()
        body = request.get_json() or {}
        track_id = int(body.get('track_id', 0))

        # Load tracks (cached)
        cache_key_trk = f"tracks_{ws_id}_{pipeline_id}"
        if not hasattr(app, '_tracks_cache'):
            app._tracks_cache = {}
        if cache_key_trk not in app._tracks_cache:
            track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')
            tracks_path = track_dir / 'tracks.pkl'
            if not tracks_path.exists():
                return api_error("No tracking results.")
            with open(str(tracks_path), 'rb') as f:
                app._tracks_cache[cache_key_trk] = pickle.load(f)
        tracks_list = app._tracks_cache[cache_key_trk]

        # Find track by ID
        idx_key = cache_key_trk + '_idx'
        if idx_key not in app._tracks_cache:
            lookup = {}
            for ti, t in enumerate(tracks_list):
                tid = t[0].get('id', ti) if t else ti
                lookup[int(float(str(tid)))] = ti
            app._tracks_cache[idx_key] = lookup
        list_idx = app._tracks_cache[idx_key].get(track_id)
        if list_idx is None:
            return api_error(f"Track {track_id} not found")

        track = tracks_list[list_idx]

        # Load stack + labels (cached)
        import tifffile
        import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
        file_path = None
        ch_params = {}
        for sk, sv in import_params.items():
            if isinstance(sv, dict):
                if 'input_file' in sv: file_path = sv['input_file']
                if 'ch1_name' in sv: ch_params = sv

        stack = None
        if file_path:
            resolved = project.resolve_data_path(file_path)
            if resolved:
                cache_key = str(resolved)
                if not hasattr(app, '_tiff_cache'):
                    app._tiff_cache = {}
                if cache_key not in app._tiff_cache:
                    app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
                raw = app._tiff_cache[cache_key]
                det_params_all = project.load_params(ws_id, pipeline_id, 'detection') or {}
                det_ch = 'vinculin'
                for sk2, sv2 in det_params_all.items():
                    if isinstance(sv2, dict) and 'detection_channel' in sv2:
                        det_ch = sv2['detection_channel']
                c_idx = 0
                for i in range(1, 5):
                    if ch_params.get(f'ch{i}_name', '').lower() == det_ch.lower():
                        c_idx = i - 1
                        break
                stack = raw[:, c_idx, :, :] if raw.ndim == 4 else raw

        labels_cache_key = f"{ws_id}_{pipeline_id}_labels"
        if not hasattr(app, '_labels_cache'):
            app._labels_cache = {}
        det_dir = project.get_results_dir(ws_id, pipeline_id, 'detection')
        labels_path = det_dir / 'all_labels.npy'
        if labels_cache_key in app._labels_cache:
            all_labels = app._labels_cache[labels_cache_key]
        elif labels_path.exists():
            all_labels = list(np.load(str(labels_path), allow_pickle=True))
            app._labels_cache[labels_cache_key] = all_labels
        else:
            all_labels = None

        pixel_size_um = 0.108
        for sk, sv in import_params.items():
            if isinstance(sv, dict) and 'pixel_size_um' in sv:
                try: pixel_size_um = float(sv['pixel_size_um'])
                except: pass

        # Build per-frame data
        frame_data = []
        for det in track:
            f_idx = int(det['frame'])
            cy, cx = det.get('centroid', (0, 0))
            label_id = det.get('label_id', 0)

            intensity = 0.0
            area_um2 = 0.0
            if label_id > 0 and stack is not None and all_labels is not None and f_idx < len(all_labels):
                mask = (all_labels[f_idx] == label_id)
                if np.any(mask):
                    intensity = float(np.mean(stack[f_idx][mask]))
                    area_um2 = float(np.sum(mask)) * (pixel_size_um ** 2)

            frame_data.append({
                'frame': f_idx,
                'cx': round(float(cx), 1),
                'cy': round(float(cy), 1),
                'intensity': round(intensity, 2),
                'area_um2': round(area_um2, 4),
                'label_id': int(label_id),
            })

        return api_response({
            'track_id': track_id,
            'n_frames': len(frame_data),
            'start_frame': frame_data[0]['frame'] if frame_data else 0,
            'end_frame': frame_data[-1]['frame'] if frame_data else 0,
            'frame_data': frame_data,
            'img_width': stack.shape[2] if stack is not None and stack.ndim >= 3 else 512,
            'img_height': stack.shape[1] if stack is not None and stack.ndim >= 3 else 512,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return api_error(str(e))


# ═════════════════════════════════════════════
# FA EXAMINATION — frame_data endpoint
# ═════════════════════════════════════════════

@app.route('/api/step/<ws_id>/<pipeline_id>/examination/frame_data', methods=['POST'])
def examination_frame_data(ws_id, pipeline_id):
    """
    Return per-frame track positions for the interactive FA examination canvas.
    Precomputes all frames at once — JSON is small (just centroids + IDs).
    """
    try:
        import pickle
        import numpy as np

        project = get_project()

        # Load tracks
        track_dir = project.get_results_dir(ws_id, pipeline_id, 'tracking')
        tracks_path = track_dir / 'tracks.pkl'
        if not tracks_path.exists():
            return api_error("No tracking results. Run tracking first.")

        cache_key_trk = f"tracks_{ws_id}_{pipeline_id}"
        if not hasattr(app, '_tracks_cache'):
            app._tracks_cache = {}
        if cache_key_trk not in app._tracks_cache:
            with open(str(tracks_path), 'rb') as f:
                app._tracks_cache[cache_key_trk] = pickle.load(f)
        tracks_list = app._tracks_cache[cache_key_trk]

        # Load classification data for group assignments
        class_dir = project.get_results_dir(ws_id, pipeline_id, 'classification')
        group_lookup = {}
        lifetime_lookup = {}
        df_class_path = class_dir / 'df_classified.csv'
        if df_class_path.exists():
            import pandas as pd
            df = pd.read_csv(str(df_class_path))
            for _, row in df.iterrows():
                tid = int(float(row.get('track_id', -1)))
                group_lookup[tid] = row.get('group', 'G9')
                lifetime_lookup[tid] = int(float(row.get('track_length', 0)))

        # Build per-frame data
        frame_data = {}
        for t_idx, track in enumerate(tracks_list):
            if not track:
                continue
            tid = track[0].get('id', t_idx)
            try:
                tid = int(float(str(tid)))
            except:
                tid = t_idx
            group = group_lookup.get(tid, 'G9')
            lifetime = lifetime_lookup.get(tid, len(track))

            for det in track:
                f = int(det['frame'])
                cy, cx = det.get('centroid', (0, 0))
                fkey = str(f)
                if fkey not in frame_data:
                    frame_data[fkey] = []
                frame_data[fkey].append({
                    'track_id': tid,
                    'cx': round(float(cx), 1),
                    'cy': round(float(cy), 1),
                    'group': group,
                    'lifetime': lifetime,
                })

        n_frames = max(int(k) for k in frame_data.keys()) + 1 if frame_data else 0

        return api_response({
            'frame_data': frame_data,
            'n_frames': n_frames,
            'n_tracks': len(tracks_list),
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return api_error(str(e))




# ═══════════════════════════════════════════════
# IMMUNIA — Segmentation Preview
# ═══════════════════════════════════════════════

@app.route('/api/immunia/<ws_id>/<pipeline_id>/seg_preview', methods=['POST'])
def immunia_seg_preview(ws_id, pipeline_id):
    """Preview segmentation for a single channel/role on one frame."""
    try:
        import tifffile
        import io
        from PIL import Image
        import base64
        import numpy as np

        body = request.get_json()
        role = body.get('role', '')
        frame_idx = int(body.get('frame', 0))

        project = get_project()

        # Get import params for channel index
        import_params = project.load_params(ws_id, pipeline_id, 'import') or {}
        ch_setup = {}
        for k, v in import_params.items():
            if isinstance(v, dict):
                ch_setup.update(v)
            elif k.endswith('_channel_idx') or k.endswith('_channel_name'):
                ch_setup[k] = v

        ch_idx = int(ch_setup.get(f'{role}_channel_idx', 0))
        ch_name = ch_setup.get(f'{role}_channel_name', role)

        # Get seg params for this role
        seg_params = project.load_params(ws_id, pipeline_id, 'segment') or {}
        role_params = {}
        for k, v in seg_params.items():
            if isinstance(v, dict):
                role_params.update(v)
            elif k.startswith(f'{role}_'):
                role_params[k] = v

        threshold_factor = float(role_params.get(f'{role}_threshold_factor', 0.8))
        min_size = int(role_params.get(f'{role}_min_size', 30))
        sigma = float(role_params.get(f'{role}_gaussian_sigma', 2.0))
        method = role_params.get(f'{role}_threshold_method', 'global')
        separate = str(role_params.get(f'{role}_separate_objects', 'false')).lower() == 'true'
        
        # New params for manual / min_max methods
        manual_thresh_str = role_params.get(f'{role}_manual_threshold', '')
        manual_threshold = float(manual_thresh_str) if manual_thresh_str else None
        imin_str = role_params.get(f'{role}_intensity_min', '')
        intensity_min = float(imin_str) if imin_str else None
        imax_str = role_params.get(f'{role}_intensity_max', '')
        intensity_max = float(imax_str) if imax_str else None

        print(f"[IMMUNIA seg_preview] role={role} ch={ch_idx}({ch_name}) frame={frame_idx} method={method} factor={threshold_factor} min={min_size} sigma={sigma} manual_t={manual_threshold} imin={intensity_min} imax={intensity_max}")

        # Load movie from cache
        file_path = None
        for section_key, section in import_params.items():
            if isinstance(section, dict) and 'input_file' in section:
                file_path = section['input_file']
                break
            elif section_key == 'input_file':
                file_path = section
        if not file_path:
            file_path = import_params.get('input_file')
        if not file_path:
            return jsonify({'success': False, 'error': 'No movie file loaded. Import a movie first.'})

        resolved = project.resolve_data_path(file_path)
        if resolved is None:
            return jsonify({'success': False, 'error': f'File not found: {file_path}'})

        cache_key = str(resolved)
        if not hasattr(app, '_tiff_cache'):
            app._tiff_cache = {}
        if cache_key not in app._tiff_cache:
            app._tiff_cache[cache_key] = tifffile.imread(str(resolved))
        stack = app._tiff_cache[cache_key]

        # Extract single channel frame
        if stack.ndim == 4:
            n_frames, n_channels = stack.shape[0], stack.shape[1]
            frame_idx = min(frame_idx, n_frames - 1)
            if ch_idx >= n_channels:
                return jsonify({'success': False, 'error': f'Channel {ch_idx} out of range (max {n_channels-1})'})
            raw = stack[frame_idx, ch_idx].astype(np.float32)
        elif stack.ndim == 3:
            raw = stack[min(frame_idx, stack.shape[0]-1)].astype(np.float32)
        else:
            return jsonify({'success': False, 'error': f'Unsupported shape: {stack.shape}'})

        # Try actual Preprocessor_Segmentor first
        try:
            IMMUNIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'immunia')
            if IMMUNIA_DIR not in sys.path:
                sys.path.insert(0, IMMUNIA_DIR)
            from components.immunia_preprocessor_segmentor import Preprocessor_Segmentor
            segmentor = Preprocessor_Segmentor()
            segmentor.config['gaussian_sigma'] = sigma
            mask = segmentor.segment_adaptive_threshold(
                image=raw, min_size=min_size, threshold_factor=threshold_factor,
                method=method, separate_objects=separate,
                manual_threshold=manual_threshold,
                intensity_min=intensity_min, intensity_max=intensity_max
            )
            print(f"[IMMUNIA seg_preview] Used Preprocessor_Segmentor")
        except Exception as seg_err:
            print(f"[IMMUNIA seg_preview] Fallback: {seg_err}")
            from scipy.ndimage import gaussian_filter, binary_fill_holes
            from skimage.filters import threshold_otsu
            from skimage.morphology import remove_small_objects

            if method == 'manual':
                # Manual: threshold on raw image directly
                t = float(manual_threshold) if manual_threshold is not None else np.mean(raw)
                mask = raw > t
            elif method == 'min_max':
                # Min/Max: clip range then Otsu
                img = raw.copy()
                imin = float(intensity_min) if intensity_min is not None else np.percentile(img, 1)
                imax = float(intensity_max) if intensity_max is not None else np.percentile(img, 99)
                img[img < imin] = 0
                img = np.clip(img, 0, imax)
                if imax > imin:
                    img = (img - imin) / (imax - imin)
                else:
                    img = np.zeros_like(img)
                img = gaussian_filter(img, sigma=sigma) if sigma > 0 else img
                try: t = threshold_otsu(img[img > 0]) * threshold_factor if np.any(img > 0) else 0.5
                except: t = 0.5
                mask = img > t
            else:
                # Standard methods: normalize + smooth first
                smoothed = gaussian_filter(raw, sigma=sigma) if sigma > 0 else raw.copy()
                pmin, pmax = np.percentile(smoothed, (1, 99))
                if pmax > pmin:
                    smoothed = np.clip((smoothed - pmin) / (pmax - pmin), 0, 1)

                if method == 'global':
                    try: t = threshold_otsu(smoothed[smoothed > 0]) * threshold_factor
                    except: t = 0.5
                    mask = smoothed > t
                elif method == 'grid':
                    h, w = smoothed.shape; gs = 4
                    mask = np.zeros_like(smoothed, dtype=bool)
                    ch2, cw = h // gs, w // gs
                    for gy in range(gs):
                        for gx in range(gs):
                            y0, y1 = gy*ch2, min((gy+1)*ch2, h)
                            x0, x1 = gx*cw, min((gx+1)*cw, w)
                            cell = smoothed[y0:y1, x0:x1]
                            if cell.size == 0 or np.std(cell) < 1e-6: continue
                            try: mask[y0:y1, x0:x1] = cell > threshold_otsu(cell) * threshold_factor
                            except: pass
                elif method == 'adaptive':
                    from skimage.filters import threshold_local
                    lt = threshold_local(smoothed, 51, method='gaussian', offset=-0.02*threshold_factor)
                    mask = smoothed > lt
                elif method == 'clahe_global':
                    from skimage.exposure import equalize_adapthist
                    ic = equalize_adapthist(smoothed, clip_limit=0.03)
                    try: t = threshold_otsu(ic) * threshold_factor
                    except: t = 0.5
                    mask = ic > t
                else:
                    try: t = threshold_otsu(smoothed) * threshold_factor
                    except: t = 0.5
                    mask = smoothed > t

            mask = binary_fill_holes(mask)
            mask = remove_small_objects(mask, min_size=min_size)
            mask = mask.astype(np.uint8)

        # Count objects
        from scipy.ndimage import label as ndlabel2
        labeled, n_obj = ndlabel2(mask)

        # Build overlay
        p_low, p_high = np.percentile(raw, (0.5, 99.5))
        if p_high > p_low:
            display = np.clip((raw - p_low) / (p_high - p_low) * 255, 0, 255).astype(np.uint8)
        else:
            display = np.zeros(raw.shape, dtype=np.uint8)

        rgb = np.stack([display, display, display], axis=-1)
        role_colors = {'dead': (239,83,80), 'tumor': (102,187,106), 'tissue': (66,165,245), 'nk': (255,167,38)}
        color = role_colors.get(role, (255,255,255))

        from scipy.ndimage import binary_erosion
        mask_bool = mask.astype(bool)
        boundary = mask_bool & ~binary_erosion(mask_bool, iterations=2)
        rgb[boundary] = color
        mask_rgb = np.zeros_like(rgb, dtype=np.float32)
        mask_rgb[mask_bool] = color
        rgb = (rgb.astype(np.float32) * 0.7 + mask_rgb * 0.3).astype(np.uint8)

        img = Image.fromarray(rgb)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=90)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        area_pct = round(np.sum(mask_bool) / mask_bool.size * 100, 1)
        info = f"Objects: {n_obj} | Area: {area_pct}% | Method: {method} | Factor: {threshold_factor} | Min: {min_size}px | \u03c3={sigma}"

        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{b64}',
            'info': info, 'n_objects': n_obj, 'area_pct': area_pct,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/data/import', methods=['POST'])
def data_import():
    """
    Import a data file into the project.
    Body: { "source_path": "/abs/path/to/file.tif",
            "mode": "copy|external|move",
            "subfolder": "" }
    """
    try:
        project = get_project()
        body = request.get_json()
        source = body.get('source_path')

        if not source:
            return api_error("'source_path' is required")

        rel_path = project.import_data(
            source_path=source,
            mode=body.get('mode', DATA_COPY),
            subfolder=body.get('subfolder', ''),
        )

        return api_response({
            "relative_path": rel_path,
            "mode": body.get('mode', DATA_COPY),
        })
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/data/clean_unused', methods=['POST'])
def data_clean_unused():
    """
    Remove data files in data/ that are not referenced by any pipeline.
    Returns list of deleted files.
    """
    try:
        project = get_project()
        data_dir = project.root / 'data'
        if not data_dir.exists():
            return api_response({"deleted": [], "n_deleted": 0})

        # Collect ALL data file references across all pipelines
        referenced = set()
        try:
            ws_root = project.root / 'workspaces'
            if ws_root.exists():
                for ws_dir in ws_root.iterdir():
                    if not ws_dir.is_dir():
                        continue
                    for p_dir in ws_dir.iterdir():
                        if not p_dir.is_dir():
                            continue
                        try:
                            params = project.load_params(ws_dir.name, p_dir.name, 'import') or {}
                            for sk, sv in params.items():
                                if isinstance(sv, dict) and 'input_file' in sv:
                                    # Resolve to absolute and store
                                    ref = sv['input_file']
                                    abs_p = project.resolve_data_path(ref)
                                    if abs_p:
                                        referenced.add(str(abs_p))
                        except:
                            pass
        except:
            pass

        # Scan data/ for files not in referenced set
        deleted = []
        for f in data_dir.iterdir():
            if f.is_file() and str(f) not in referenced:
                size_mb = f.stat().st_size / (1024 * 1024)
                f.unlink()
                deleted.append({"name": f.name, "size_mb": round(size_mb, 1)})
                print(f"[CLEANUP] Deleted unused data: {f.name} ({size_mb:.1f} MB)")

        total_mb = sum(d['size_mb'] for d in deleted)
        print(f"[CLEANUP] Cleaned {len(deleted)} unused data files ({total_mb:.0f} MB)")

        return api_response({
            "deleted": deleted,
            "n_deleted": len(deleted),
            "total_mb": round(total_mb, 1),
        })
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/data/list', methods=['GET'])
def data_list():
    """List all data files in the project."""
    try:
        project = get_project()
        return api_response(project._manifest.get("data_references", []))
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/data/resolve', methods=['POST'])
def data_resolve():
    """
    Resolve a data reference to absolute path.
    Body: { "relative_path": "data/movie.tif" }
    """
    try:
        project = get_project()
        body = request.get_json()
        rel = body.get('relative_path')

        resolved = project.resolve_data_path(rel)

        return api_response({
            "relative_path": rel,
            "absolute_path": str(resolved) if resolved else None,
            "exists": resolved is not None,
        })
    except Exception as e:
        return api_error(str(e), 500)


# ═════════════════════════════════════════════
# VERSION / COMMIT ENDPOINTS
# ═════════════════════════════════════════════

@app.route('/api/version/commit', methods=['POST'])
def version_commit():
    """
    Create a commit (snapshot of all params).
    Body: { "message": "Changed threshold", "author": "Majid" }
    """
    try:
        project = get_project()
        body = request.get_json()
        message = body.get('message', 'No message')

        commit_hash = project.commit(
            message=message,
            author=body.get('author', ''),
        )

        return api_response({"hash": commit_hash, "message": message})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/version/log', methods=['GET'])
def version_log():
    """Get commit history."""
    try:
        project = get_project()
        max_entries = request.args.get('max', 50, type=int)
        return api_response(project.log(max_entries))
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/version/diff', methods=['POST'])
def version_diff():
    """
    Diff two commits.
    Body: { "hash_a": "abc123", "hash_b": "def456" }
    """
    try:
        project = get_project()
        body = request.get_json()

        diff = project.diff(body['hash_a'], body['hash_b'])
        return api_response(diff)
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/version/tag', methods=['POST'])
def version_tag():
    """
    Tag a commit.
    Body: { "tag_name": "final_for_paper", "commit_hash": "abc123" }
    """
    try:
        project = get_project()
        body = request.get_json()

        project.tag(
            tag_name=body['tag_name'],
            commit_hash=body.get('commit_hash'),
        )

        return api_response({"tagged": body['tag_name']})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/version/checkout', methods=['POST'])
def version_checkout():
    """
    Checkout a previous commit (revert params).
    Body: { "commit_hash": "abc123" }
    """
    try:
        project = get_project()
        body = request.get_json()

        project.checkout(body['commit_hash'])

        return api_response({"checked_out": body['commit_hash']})
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/version/tags', methods=['GET'])
def version_tags():
    """List all tags."""
    try:
        project = get_project()
        tags_dir = project.internal_dir / "history" / "tags"
        if not tags_dir.exists():
            return api_response([])

        tags = []
        for f in sorted(tags_dir.iterdir()):
            if f.suffix == '.json':
                t = project._read_json(f)
                h = t.get('commit_hash', '') or t.get('hash', '') or t.get('commit', '')
                tags.append({"name": f.stem, "hash": str(h)})

        return api_response(tags)
    except Exception as e:
        return api_error(str(e), 500)


# ═════════════════════════════════════════════
# GUI STATE ENDPOINTS
# ═════════════════════════════════════════════

@app.route('/api/gui/state', methods=['GET'])
def gui_get_state():
    """Get saved GUI state."""
    try:
        project = get_project()
        return api_response(project.load_gui_state())
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/gui/state', methods=['POST'])
def gui_save_state():
    """
    Save GUI state.
    Body: { full GUI state object }
    """
    try:
        project = get_project()
        body = request.get_json()
        project.save_gui_state(body)
        return api_response({"saved": True})
    except Exception as e:
        return api_error(str(e), 500)


# ═════════════════════════════════════════════
# PACKAGE MANAGEMENT ENDPOINTS
# ═════════════════════════════════════════════

@app.route('/api/packages/list', methods=['GET'])
def packages_list():
    """List all available packages and their status."""
    try:
        project = get_project()
        active = project._manifest.get("active_packages", [])

        # Scan backend directory for package folders
        packages = []
        for d in Path(BACKEND_DIR).iterdir():
            if not d.is_dir():
                continue
            manifest_file = d / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file) as f:
                    pkg = json.load(f)
                pkg["enabled"] = d.name in active
                packages.append(pkg)
            elif d.name in ['fastia', 'immunia', 'cornealia',
                            'cellfade', 'migrafiba', 'mrheologia']:
                # Known packages without manifest yet
                packages.append({
                    "name": d.name.upper(),
                    "id": d.name,
                    "version": "0.1.0",
                    "description": f"{d.name} package",
                    "enabled": d.name in active,
                    "has_manifest": False,
                })

        return api_response(packages)
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/packages/<package_id>/toggle', methods=['POST'])
def packages_toggle(package_id):
    """
    Enable or disable a package.
    Body: { "enabled": true/false }
    """
    try:
        project = get_project()
        body = request.get_json()
        enabled = body.get('enabled', True)

        active = project._manifest.get("active_packages", [])

        if enabled and package_id not in active:
            active.append(package_id)
        elif not enabled and package_id in active:
            active.remove(package_id)

        project._manifest["active_packages"] = active
        project.save()

        return api_response({
            "package": package_id,
            "enabled": enabled,
            "active_packages": active,
        })
    except Exception as e:
        return api_error(str(e), 500)


# ═════════════════════════════════════════════
# FILE BROWSER (for the frontend file dialogs)
# ═════════════════════════════════════════════

@app.route('/api/browse', methods=['POST'])
def browse_directory():
    """
    Browse a directory for the frontend file picker.
    Body: { "path": "/some/dir", "filter": ".tif,.nd2,.czi" }
    """
    try:
        body = request.get_json()
        path = Path(body.get('path', os.path.expanduser('~')))
        filter_ext = body.get('filter', '').split(',')
        filter_ext = [e.strip().lower() for e in filter_ext if e.strip()]

        if not path.exists():
            return api_error(f"Path not found: {path}", 404)

        items = []
        try:
            for entry in sorted(path.iterdir()):
                if entry.name.startswith('.'):
                    continue
                item = {
                    "name": entry.name,
                    "path": str(entry),
                    "is_dir": entry.is_dir(),
                }
                if entry.is_file():
                    item["size_bytes"] = entry.stat().st_size
                    item["ext"] = entry.suffix.lower()
                    if filter_ext and item["ext"] not in filter_ext:
                        continue
                items.append(item)
        except PermissionError:
            return api_error("Permission denied", 403)

        return api_response({
            "path": str(path),
            "parent": str(path.parent),
            "items": items,
        })
    except Exception as e:
        return api_error(str(e), 500)


@app.route('/api/browse_save', methods=['POST'])
def browse_save():
    """Open a native save-file or folder dialog.
    Body: { "mode": "file"|"folder", "title": "...", "default_name": "...",
            "filetypes": [["TIFF Files", "*.tif"], ["All", "*.*"]], "initial_dir": "..." }
    Returns: { "success": true, "path": "chosen/path" } or { "success": false } if cancelled.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        body = request.get_json() or {}
        mode = body.get('mode', 'file')
        title = body.get('title', 'Save As')
        initial_dir = body.get('initial_dir', os.path.expanduser('~'))
        default_name = body.get('default_name', '')
        filetypes = body.get('filetypes', [['All Files', '*.*']])

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        if mode == 'folder':
            chosen = filedialog.askdirectory(title=title, initialdir=initial_dir)
        else:
            chosen = filedialog.asksaveasfilename(
                title=title,
                initialdir=initial_dir,
                initialfile=default_name,
                filetypes=[tuple(ft) for ft in filetypes],
            )
        root.destroy()

        if not chosen:
            return jsonify({'success': False, 'error': 'Cancelled'})
        return jsonify({'success': True, 'path': chosen})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/browse_open', methods=['POST'])
def browse_open():
    """Open a native file/folder picker dialog (Windows Explorer).
    Body: { "mode": "file"|"folder", "title": "...",
            "filetypes": [["CelLAB Projects", "*.cellab"], ["All", "*.*"]],
            "initial_dir": "..." }
    Returns: { "success": true, "path": "chosen/path" } or { "success": false } if cancelled.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        body = request.get_json() or {}
        mode = body.get('mode', 'file')
        title = body.get('title', 'Open')
        initial_dir = body.get('initial_dir', os.path.expanduser('~'))
        filetypes = body.get('filetypes', [['All Files', '*.*']])

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        if mode == 'folder':
            chosen = filedialog.askdirectory(title=title, initialdir=initial_dir)
        else:
            chosen = filedialog.askopenfilename(
                title=title,
                initialdir=initial_dir,
                filetypes=[tuple(ft) for ft in filetypes],
            )
        root.destroy()

        if not chosen:
            return jsonify({'success': False, 'error': 'Cancelled'})
        return jsonify({'success': True, 'path': chosen})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ═════════════════════════════════════════════
# CellIntella — AI ASSISTANT
# ═════════════════════════════════════════════

_cellintella = None
_cellintella_loading = False
_cellintella_config = {
    'n_ctx': 4096,
    'n_threads': 10,
    'timeout': 500,
}
_child_procs = {}  # pid → psutil.Process (cached for cpu_percent delta)

# ── Hierarchical Doc Retriever ──────────────

DOCS_DIR = os.path.join(BASE_DIR, 'docs')

def _load_doc(path):
    """Load a markdown doc file, return content or empty string."""
    try:
        fp = os.path.join(DOCS_DIR, path)
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                return f.read()
    except:
        pass
    return ''

def _retrieve_docs(query):
    """
    Hierarchical document retrieval.
    Returns combined context string (~1500-2000 tokens max).
    """
    query_lower = query.lower()

    # Skip doc loading for greetings and identity questions
    skip_patterns = ['hello', 'hi ', 'hey', 'who are you', 'what is your name',
                     'your name', 'thanks', 'thank you', 'bye', 'good morning',
                     'good night', 'how are you']
    if any(p in query_lower for p in skip_patterns):
        return ''

    context_parts = []

    # Keyword matching for packages
    package_matches = []

    cornealia_kw = ['cornea', 'endotheli', 'specular', 'morphometr', 'cell density', 'hexagonal',
                    'g(r)', 'v(r)', 'radial distribution', 'collective order', 'pixel_size',
                    'pixel size', 'k value', 'morse', 'batch', 'as vs bs', 'cd_calc', 'cv_calc',
                    'hex_calc', 'ave_calc', 'cornealia']
    fastia_kw = ['focal adhesion', 'fa ', 'timelapse', 'tracking', 'detection', 'paxillin',
                 'assembly', 'disassembly', 'kinetics', 'fastia']
    immunia_kw = ['immune', 'nk cell', 'natural killer', 'tumor', 'chemotaxis', 'keller-segel',
                  'cytotox', 'immunia']
    platform_kw = ['project', 'workspace', 'pipeline', 'console', 'terminal', 'git', 'commit',
                   'version', 'task manager', 'gui', 'toolbar', 'menu', 'shortcut', 'save',
                   'open', 'cellab', 'layout', 'panel']

    if any(kw in query_lower for kw in cornealia_kw):
        package_matches.append('cornealia')
    if any(kw in query_lower for kw in fastia_kw):
        package_matches.append('fastia')
    if any(kw in query_lower for kw in immunia_kw):
        package_matches.append('immunia')
    if any(kw in query_lower for kw in platform_kw):
        package_matches.append('platform')

    # If no specific match, load platform overview (general question)
    if not package_matches:
        package_matches.append('platform')

    # Level 1: Load OVERVIEW for matched packages
    for pkg in package_matches[:2]:  # max 2 packages
        overview = _load_doc(f'{pkg}/OVERVIEW.md')
        if overview:
            context_parts.append(overview)

    # Level 2: Load detail files if query is specific
    detail_kw = {
        'cornealia': {
            'pixel': 'cornealia/API.md',
            'parameter': 'cornealia/API.md',
            'constructor': 'cornealia/API.md',
            'collective_order': 'cornealia/collective_order.md',
            'batch': 'cornealia/batch_processing.md',
            'plot': 'cornealia/plotters.md',
            'error': 'cornealia/troubleshooting.md',
            'fail': 'cornealia/troubleshooting.md',
            'crash': 'cornealia/troubleshooting.md',
            'reliable': 'cornealia/troubleshooting.md',
        },
        'platform': {
            'project': 'platform/project_format.md',
            '.cellab': 'platform/project_format.md',
            'console': 'platform/console_commands.md',
            'terminal': 'platform/console_commands.md',
            'git': 'platform/console_commands.md',
            'commit': 'platform/console_commands.md',
            'gui': 'platform/gui_architecture.md',
            'layout': 'platform/gui_architecture.md',
            'menu': 'platform/gui_architecture.md',
            'toolbar': 'platform/gui_architecture.md',
        },
    }

    loaded_details = set()
    for pkg in package_matches:
        if pkg in detail_kw:
            for kw, detail_path in detail_kw[pkg].items():
                if kw in query_lower and detail_path not in loaded_details:
                    detail = _load_doc(detail_path)
                    if detail:
                        context_parts.append(detail)
                        loaded_details.add(detail_path)
                    break  # one detail per package is enough

    return '\n\n---\n\n'.join(context_parts) if context_parts else ''


cellintella_SYSTEM_PROMPT = """You are CellIntella (Cell Intelligent Autonomous Interface), the AI assistant built into CelLAB (Cellular Analysis Workbench).
You were created by the Han Mechanobiology Lab at Michigan Tech.

CRITICAL RULES:
- Be CONCISE. Answer in 2-5 sentences unless the user asks for detail.
- Do NOT dump documentation. Summarize in your own words.
- Do NOT repeat the documentation structure (headers, tables, bullet lists).
- If asked a simple question, give a simple answer.
- Give code examples ONLY when the user asks "how to" or "show me code".
- For greetings, respond briefly and warmly.

You help researchers with CelLAB's packages: Cornealia (corneal morphometry), FASTIA (focal adhesion), IMMUNIA (immune cell tracking).
You run locally on Llama 3.2 3B — all conversations are private.
"""


def _collect_scope_context(scope):
    """
    Collect CelLAB project state based on scope level.
    Returns a concise text summary for injection into CellIntella prompt.
    """
    if not scope or scope.get('level') == 'none':
        return ''

    try:
        project = get_project()
    except:
        return ''

    level = scope.get('level', 'none')
    lines = ['[Current CelLAB State]']
    lines.append(f'Project: {project.name}')

    if level == 'pipeline':
        ws_id = scope.get('wsId', '')
        pipeline_id = scope.get('pipelineId', '')
        print(f"[CellIntella scope] Looking for ws={ws_id}, pipeline={pipeline_id}")
        print(f"[CellIntella scope] Available dirs: {[d.name for d in project.workspaces_dir.iterdir() if d.is_dir()]}")

        # Try to find workspace — wsId from frontend might not match backend dirs
        if not ws_id or not (project.workspaces_dir / ws_id / pipeline_id / 'pipeline.json').exists():
            found = False
            for ws_dir in sorted(project.workspaces_dir.iterdir()):
                if ws_dir.is_dir():
                    print(f"[CellIntella scope] Checking {ws_dir.name}: {[p.name for p in ws_dir.iterdir() if p.is_dir()]}")
                    if (ws_dir / pipeline_id / 'pipeline.json').exists():
                        ws_id = ws_dir.name
                        found = True
                        print(f"[CellIntella scope] Found pipeline in {ws_id}")
                        break
            if not found:
                print(f"[CellIntella scope] Pipeline {pipeline_id} NOT FOUND in any workspace")

        if ws_id and pipeline_id:
            try:
                pipeline = project.get_pipeline(ws_id, pipeline_id)
                p_type = pipeline.get('type', '')
                p_name = pipeline.get('name', pipeline_id)
                lines.append(f'Pipeline: {p_name} (type: {p_type})')

                # Scan step directories on disk (pipeline.json may not list all steps)
                pipeline_dir = project.workspaces_dir / ws_id / pipeline_id
                step_dirs = sorted([d for d in pipeline_dir.iterdir() if d.is_dir()])
                steps_json = pipeline.get('steps', {})

                for step_dir in step_dirs:
                    step_id = step_dir.name
                    # Get status from pipeline.json if available
                    step_info = steps_json.get(step_id, {})
                    status = step_info.get('status', 'idle') if isinstance(step_info, dict) else 'idle'

                    # Check for results on disk
                    has_results = (step_dir / 'results').exists() and any((step_dir / 'results').iterdir()) if (step_dir / 'results').exists() else False
                    if has_results and status == 'idle':
                        status = 'done (results on disk)'

                    lines.append(f'  Step "{step_id}": {status}')

                    # Load actual params — flatten nested structure
                    params_file = step_dir / 'params.json'
                    if params_file.exists():
                        try:
                            with open(params_file, 'r') as f:
                                raw = json.loads(f.read())
                            # Extract actual params (skip meta fields like step_id, saved)
                            params_dict = raw.get('params', raw)
                            # Flatten nested groups: {'batch-folder': {'batch_folder': 'X'}} → batch_folder = X
                            for k, v in params_dict.items():
                                if k in ('step_id', 'saved', 'timestamp'):
                                    continue
                                if isinstance(v, dict):
                                    for k2, v2 in v.items():
                                        lines.append(f'    {k2} = {v2}')
                                else:
                                    lines.append(f'    {k} = {v}')
                        except:
                            pass

                print(f"[CellIntella scope] Pipeline {pipeline_id}: {len(step_dirs)} step dirs, context = {len(lines)} lines", flush=True)

                # If batch pipeline, try to include result summary
                if p_type == 'cornealia_batch':
                    csv_path = pipeline_dir / 'batch_run' / 'results' / 'batch_results.csv'
                    if csv_path.exists():
                        try:
                            import pandas as pd
                            df = pd.read_csv(csv_path)
                            n_total = len(df)
                            n_reliable = df['reliable'].sum() if 'reliable' in df.columns else '?'
                            lines.append(f'  Batch Results: {n_total} images ({n_reliable} reliable)')
                            for col in ['K_um', 'K_ds_um', 'CD_calc', 'Ave_calc', 'CV_calc', 'HEX_calc']:
                                if col in df.columns:
                                    vals = df[col].dropna()
                                    if len(vals) > 0:
                                        lines.append(f'    {col}: mean={vals.mean():.4f}, std={vals.std():.4f}, range=[{vals.min():.4f}, {vals.max():.4f}]')
                        except Exception as ex:
                            print(f"[CellIntella scope] CSV read error: {ex}", flush=True)
            except Exception as ex:
                print(f"[CellIntella scope] Error loading pipeline {pipeline_id}: {ex}", flush=True)
                lines.append(f'Pipeline: {pipeline_id} (error loading: {ex})')

    elif level == 'workspace':
        ws_id = scope.get('wsId', '')
        if ws_id:
            try:
                ws_dir = project.workspaces_dir / ws_id
                lines.append(f'Workspace: {ws_id}')
                for p_dir in sorted(ws_dir.iterdir()):
                    p_json = p_dir / 'pipeline.json'
                    if p_json.exists():
                        p_data = project._read_json(p_json)
                        p_name = p_data.get('name', p_dir.name)
                        p_type = p_data.get('type', '?')
                        steps = p_data.get('steps', {})
                        step_summary = ', '.join(f'{s}:{info.get("status","idle") if isinstance(info,dict) else "idle"}' for s, info in steps.items())
                        lines.append(f'  {p_name} ({p_type}): {step_summary}')
            except:
                pass

    elif level == 'project':
        try:
            state = project.get_full_state()
            ws_list = state.get('workspaces', [])
            lines.append(f'Workspaces: {len(ws_list)}')
            for ws in ws_list:
                ws_name = ws.get('name', ws.get('id', '?'))
                pipelines = ws.get('pipelines', [])
                lines.append(f'  {ws_name}: {len(pipelines)} pipelines')
                for p in pipelines[:5]:
                    lines.append(f'    {p.get("name","?")} ({p.get("type","?")})')
        except:
            pass

    return '\n'.join(lines) + '\n'


def _get_cellintella():
    """Lazy-load CellIntella manager."""
    global _cellintella, _cellintella_loading
    if _cellintella is not None:
        return _cellintella
    if _cellintella_loading:
        return None

    _cellintella_loading = True
    try:
        sys.path.insert(0, os.path.join(BACKEND_DIR))
        from cellintella.cellintella_manager import CellIntella as cellintella
        _cellintella = cellintella(mode='local', verbose=True)

        # Override process wrapper settings with our config
        if _cellintella.local_ai is None and not _cellintella.local_ai_attempted:
            from cellintella.cellintella_process_wrapper import CellIntellaProcessWrapper as cellintellaProcessWrapper
            _cellintella.local_ai_attempted = True
            _cellintella.local_ai = cellintellaProcessWrapper(
                n_threads=_cellintella_config['n_threads'],
                n_ctx=_cellintella_config['n_ctx'],
                verbose=True,
                timeout=_cellintella_config['timeout'],
            )

        print(f"✅ CellIntella initialized (n_ctx={_cellintella_config['n_ctx']}, n_threads={_cellintella_config['n_threads']})")
        return _cellintella
    except Exception as e:
        print(f"❌ CellIntella init failed: {e}")
        traceback.print_exc()
        _cellintella_loading = False
        return None


@app.route('/api/cellintella/status', methods=['GET'])
def cellintella_status():
    """Check CellIntella availability."""
    if _cellintella is not None:
        return api_response({
            "available": True,
            "loaded": True,
            "mode": _cellintella.mode,
        })
    return api_response({
        "available": True,
        "loaded": False,
        "mode": "local",
    })


@app.route('/api/cellintella/query', methods=['POST'])
def cellintella_query():
    """
    Send a message to CellIntella with hierarchical doc context.
    Body: { "message": "How do I change pixel size?", "context_type": null }
    """
    body = request.get_json()
    print(f"[CellIntella QUERY] body keys: {list(body.keys())}, scope: {body.get('scope')}", flush=True)
    try:
        body = request.get_json()
        message = body.get('message', '').strip()
        context_type = body.get('context_type', None)
        fresh = body.get('fresh', False)
        scope = body.get('scope', None)
        accumulated_context = body.get('accumulated_context', '')

        # Enrich accumulated context — resolve pipeline references to actual data
        if accumulated_context:
            enriched_items = []
            for line in accumulated_context.split('\n'):
                if 'Pipeline:' in line and 'ID:' in line:
                    # Extract pipeline ID and resolve actual state
                    try:
                        pid = line.split('ID:')[1].strip()
                        project = get_project()
                        # Find workspace
                        for ws_dir in sorted(project.workspaces_dir.iterdir()):
                            if ws_dir.is_dir() and (ws_dir / pid / 'pipeline.json').exists():
                                scope_data = {'level': 'pipeline', 'wsId': ws_dir.name, 'pipelineId': pid}
                                resolved = _collect_scope_context(scope_data)
                                if resolved:
                                    enriched_items.append(resolved)
                                break
                        else:
                            enriched_items.append(line)
                    except:
                        enriched_items.append(line)
                elif line.strip():
                    enriched_items.append(line)
            accumulated_context = '\n'.join(enriched_items)

        if not message:
            return api_error("'message' is required")

        ai = _get_cellintella()
        if ai is None:
            return api_response({
                "response": "CellIntella is loading the Llama model... please wait 2-3 minutes and try again.",
                "mode": "loading",
            })

        # Retrieve relevant docs from our hierarchical system
        doc_context = _retrieve_docs(message)

        # Collect scope context (project/workspace/pipeline state)
        scope_context = _collect_scope_context(scope)
        print(f"[CellIntella] scope={scope}, context_len={len(scope_context)}")
        if scope_context:
            print(f"[CellIntella] State injected:\n{scope_context[:500]}")

        # Build enriched prompt — state first so LLM sees it prominently
        enriched_message = f"[System]\n{cellintella_SYSTEM_PROMPT}\n\n"

        if scope_context:
            enriched_message += f"{scope_context}\n"
            enriched_message += "IMPORTANT: The above state shows the ACTUAL current parameters and step statuses. Use these values to answer the user's question directly. Do NOT tell the user to look up parameters — you already have them.\n\n"

        if accumulated_context:
            enriched_message += f"{accumulated_context}\n"

        if doc_context:
            enriched_message += f"[Reference Documentation]\n{doc_context}\n\n"

        # For fresh mode, add instruction to ignore conversation history
        if fresh:
            enriched_message += "[Note: This is a standalone question. Do not reference any previous conversation.]\n\n"

        enriched_message += f"[User Question]\n{message}"

        response = ai.query(
            user_message=enriched_message,
            context_type=context_type,
        )

        # Handle both string and dict responses
        if isinstance(response, dict):
            text = response.get('response', str(response))
        else:
            text = str(response)

        return api_response({
            "response": text,
            "mode": ai.mode,
        })

    except Exception as e:
        traceback.print_exc()
        return api_response({
            "response": f"Error: {str(e)}. Try rephrasing your question.",
            "mode": "error",
        })


@app.route('/api/cellintella/history', methods=['GET'])
def cellintella_history():
    """Get conversation history."""
    if _cellintella is None:
        return api_response([])
    return api_response(_cellintella.conversation_history)


@app.route('/api/cellintella/clear', methods=['POST'])
def cellintella_clear():
    """Clear conversation history."""
    if _cellintella is not None:
        _cellintella.conversation_history = []
    return api_response({"cleared": True})


@app.route('/api/cellintella/config', methods=['GET'])
def cellintella_config_get():
    """Get current CellIntella config."""
    kv_cache_mb = int(_cellintella_config['n_ctx'] * 28 * 128 * 2 * 2 / 1024 / 1024)
    return api_response({
        "n_ctx": _cellintella_config['n_ctx'],
        "n_threads": _cellintella_config['n_threads'],
        "timeout": _cellintella_config['timeout'],
        "kv_cache_mb": kv_cache_mb,
        "model_mb": 1918,
        "loaded": _cellintella is not None and _cellintella.local_ai is not None,
    })


@app.route('/api/cellintella/config', methods=['POST'])
def cellintella_config_set():
    """
    Update CellIntella config and reload model.
    Body: { "n_ctx": 8192 } or { "n_threads": 12 }
    """
    global _cellintella, _cellintella_loading
    body = request.get_json()

    changed = False
    for key in ('n_ctx', 'n_threads', 'timeout'):
        if key in body:
            new_val = int(body[key])
            if new_val != _cellintella_config[key]:
                _cellintella_config[key] = new_val
                changed = True

    if not changed:
        return api_response({"reloaded": False, "reason": "no changes"})

    # Kill existing model
    print(f"[CellIntella] Reloading with config: {_cellintella_config}", flush=True)
    try:
        if _cellintella and _cellintella.local_ai:
            _cellintella.local_ai.shutdown()
    except:
        pass
    _cellintella = None
    _cellintella_loading = False

    # Reload
    ai = _get_cellintella()

    kv_cache_mb = int(_cellintella_config['n_ctx'] * 28 * 128 * 2 * 2 / 1024 / 1024)
    return api_response({
        "reloaded": True,
        "n_ctx": _cellintella_config['n_ctx'],
        "n_threads": _cellintella_config['n_threads'],
        "kv_cache_mb": kv_cache_mb,
    })


# ═════════════════════════════════════════════
# REPORT GENERATOR
# ═════════════════════════════════════════════

import tempfile
import shutil
from datetime import datetime as _dt

def _generate_cornealia_batch_report(project, ws_id, pipeline_id):
    """Generate markdown report for a Cornealia Batch pipeline."""
    pipeline_dir = project.workspaces_dir / ws_id / pipeline_id
    pipeline = project.get_pipeline(ws_id, pipeline_id)
    p_name = pipeline.get('name', pipeline_id)
    p_type = pipeline.get('type', 'cornealia_batch')

    lines = []
    lines.append(f'# CelLAB Analysis Report')
    lines.append(f'## {p_name}')
    lines.append(f'Generated: {_dt.now().strftime("%Y-%m-%d %H:%M")} | Project: {project.name}')
    lines.append(f'')
    lines.append(f'---')
    lines.append(f'')

    # ── 1. Parameters ──
    lines.append(f'## 1. Parameters')
    lines.append(f'')
    lines.append(f'| Parameter | Value |')
    lines.append(f'|-----------|-------|')
    lines.append(f'| Pipeline Type | {p_type} |')

    for step_dir in sorted(pipeline_dir.iterdir()):
        if not step_dir.is_dir():
            continue
        params_file = step_dir / 'params.json'
        if params_file.exists():
            try:
                with open(params_file, 'r') as f:
                    raw = json.loads(f.read())
                params_dict = raw.get('params', raw)
                for k, v in params_dict.items():
                    if k in ('step_id', 'saved', 'timestamp'):
                        continue
                    if isinstance(v, dict):
                        for k2, v2 in v.items():
                            lines.append(f'| {k2} | {v2} |')
                    else:
                        lines.append(f'| {k} | {v} |')
            except:
                pass

    lines.append(f'')

    # ── 2. Summary Statistics ──
    csv_path = pipeline_dir / 'batch_run' / 'results' / 'batch_results.csv'
    if csv_path.exists():
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            n_total = len(df)
            n_reliable = int(df['reliable'].sum()) if 'reliable' in df.columns else '?'

            lines.append(f'## 2. Summary Statistics')
            lines.append(f'')
            lines.append(f'**Images analyzed:** {n_total}')
            lines.append(f'**Reliable:** {n_reliable}/{n_total} ({100*n_reliable/n_total:.1f}%)')
            lines.append(f'')

            # Metrics table
            metrics = ['K_um', 'K_ds_um', 'r_0_um', 'CD_calc', 'Ave_calc', 'CV_calc', 'HEX_calc']
            available = [m for m in metrics if m in df.columns]

            if available:
                lines.append(f'| Metric | Mean | Std | Min | Max | N |')
                lines.append(f'|--------|------|-----|-----|-----|---|')
                for col in available:
                    vals = df[col].dropna()
                    if len(vals) > 0:
                        lines.append(f'| {col} | {vals.mean():.4f} | {vals.std():.4f} | {vals.min():.4f} | {vals.max():.4f} | {len(vals)} |')
                lines.append(f'')

            # AS vs BS comparison
            if 'group' in df.columns:
                as_df = df[df['group'] == 'AS']
                bs_df = df[df['group'] == 'BS']
                if len(as_df) > 0 and len(bs_df) > 0:
                    lines.append(f'### AS vs BS Comparison')
                    lines.append(f'')
                    lines.append(f'| Metric | AS (n={len(as_df)}) | BS (n={len(bs_df)}) |')
                    lines.append(f'|--------|-----|-----|')
                    for col in available:
                        as_vals = as_df[col].dropna()
                        bs_vals = bs_df[col].dropna()
                        if len(as_vals) > 0 and len(bs_vals) > 0:
                            lines.append(f'| {col} | {as_vals.mean():.4f} ± {as_vals.std():.4f} | {bs_vals.mean():.4f} ± {bs_vals.std():.4f} |')
                    lines.append(f'')
        except Exception as ex:
            lines.append(f'## 2. Summary Statistics')
            lines.append(f'')
            lines.append(f'*Error reading CSV: {ex}*')
            lines.append(f'')
    else:
        lines.append(f'## 2. Summary Statistics')
        lines.append(f'')
        lines.append(f'*No batch results CSV found. Run the batch first.*')
        lines.append(f'')

    # ── 3. Results (Figures) ──
    lines.append(f'## 3. Results')
    lines.append(f'')

    # Collect all plots from all step results
    plot_files = []
    for step_dir in sorted(pipeline_dir.iterdir()):
        plots_dir = step_dir / 'results' / 'plots'
        if plots_dir.exists():
            for img in sorted(plots_dir.glob('*.png')):
                plot_files.append(img)

    if plot_files:
        for i, pf in enumerate(plot_files, 1):
            # Clean up filename for caption
            caption = pf.stem.replace('_', ' ').replace('-', ' ').title()
            lines.append(f'### 3.{i} {caption}')
            lines.append(f'')
            lines.append(f'![{caption}](plots/{pf.name})')
            lines.append(f'')
    else:
        lines.append(f'*No plots generated yet. Use Insert Result to create plots.*')
        lines.append(f'')

    # ── 4. Interpretation Placeholder ──
    lines.append(f'## 4. Interpretation')
    lines.append(f'')
    lines.append(f'<!-- CellIntella placeholder: AI-generated narrative will go here in a future version -->')
    lines.append(f'*No AI interpretation generated. Enable CellIntella narrative in a future version.*')
    lines.append(f'')

    # ── Footer ──
    lines.append(f'---')
    lines.append(f'')
    lines.append(f'*Generated by CelLAB v3.1.10 | Han Mechanobiology Lab | Michigan Tech*')

    return '\n'.join(lines), plot_files


def _generate_report_md(project, ws_id, pipeline_id):
    """Route to the right template based on pipeline type."""
    pipeline = project.get_pipeline(ws_id, pipeline_id)
    p_type = pipeline.get('type', '')

    if p_type == 'cornealia_batch':
        return _generate_cornealia_batch_report(project, ws_id, pipeline_id)
    elif p_type == 'cornealia':
        return _generate_cornealia_batch_report(project, ws_id, pipeline_id)  # reuse for now
    else:
        return f'# Report\n\nReport template not yet available for pipeline type: {p_type}', []


@app.route('/api/report/generate', methods=['POST'])
def report_generate():
    """
    Generate a report for a pipeline.
    Body: { "ws_id": "...", "pipeline_id": "...", "format": "md"|"pdf"|"docx" }
    """
    try:
        project = get_project()
        body = request.get_json()
        ws_id = body.get('ws_id', '')
        pipeline_id = body.get('pipeline_id', '')
        fmt = body.get('format', 'md')

        if not pipeline_id:
            return api_error("'pipeline_id' is required")

        # Find workspace if not provided
        if not ws_id:
            for ws_dir in sorted(project.workspaces_dir.iterdir()):
                if ws_dir.is_dir() and (ws_dir / pipeline_id / 'pipeline.json').exists():
                    ws_id = ws_dir.name
                    break

        if not ws_id:
            return api_error(f"Pipeline '{pipeline_id}' not found")

        pipeline_dir = project.workspaces_dir / ws_id / pipeline_id

        # Generate markdown
        md_content, plot_files = _generate_report_md(project, ws_id, pipeline_id)

        # Create report directory: one folder per pipeline, timestamp on files
        pipeline = project.get_pipeline(ws_id, pipeline_id)
        p_name = pipeline.get('name', pipeline_id).replace(' ', '_')
        timestamp = _dt.now().strftime('%Y%m%d_%H%M%S')

        reports_dir = project.root / 'reports'
        reports_dir.mkdir(exist_ok=True)
        report_dir = reports_dir / p_name
        report_dir.mkdir(exist_ok=True)
        plots_out = report_dir / 'plots'
        plots_out.mkdir(exist_ok=True)

        # Copy plot images
        for pf in plot_files:
            shutil.copy2(pf, plots_out / pf.name)

        if fmt == 'md':
            md_path = report_dir / f'{p_name}_report_{timestamp}.md'
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            return api_response({
                "format": "md",
                "path": str(md_path),
                "dir": str(report_dir),
            })

        elif fmt == 'pdf':
            # Convert markdown to HTML then to PDF
            md_path = report_dir / f'{p_name}_report_{timestamp}.md'
            pdf_path = report_dir / f'{p_name}_report_{timestamp}.pdf'
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            try:
                import markdown
                html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
                # Wrap in styled HTML — use absolute paths for images
                img_html = html_content.replace('src="plots/', f'src="{str(plots_out).replace(chr(92), "/")}/')
                html_full = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@page {{ size: A4; margin: 2cm; }}
body {{ font-family: Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; font-size: 11px; }}
h1 {{ color: #2c3e50; border-bottom: 3px solid #2c3e50; padding-bottom: 8px; font-size: 22px; }}
h2 {{ color: #34495e; border-bottom: 1px solid #ddd; padding-bottom: 4px; margin-top: 24px; font-size: 16px; }}
h3 {{ color: #555; font-size: 13px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 10px; }}
th {{ background: #f0f0f0; font-weight: 700; }}
img {{ max-width: 100%; height: auto; margin: 8px 0; }}
hr {{ border: none; border-top: 2px solid #2c3e50; margin: 16px 0; }}
em {{ color: #888; }}
</style></head><body>
{img_html}
</body></html>"""

                # Save HTML too
                html_path = report_dir / f'{p_name}_report_{timestamp}.html'
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_full)

                # Try browser headless PDF (best quality)
                pdf_created = False
                import subprocess

                # Find Edge or Chrome
                browser_paths = [
                    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
                    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                ]
                browser_exe = None
                for bp in browser_paths:
                    if os.path.exists(bp):
                        browser_exe = bp
                        break

                if browser_exe:
                    try:
                        html_url = 'file:///' + str(html_path).replace('\\', '/')
                        result = subprocess.run(
                            [browser_exe, '--headless', '--disable-gpu', '--run-all-compositor-stages-before-draw',
                             f'--print-to-pdf={str(pdf_path)}', html_url],
                            capture_output=True, timeout=30, cwd=str(report_dir)
                        )
                        if pdf_path.exists() and pdf_path.stat().st_size > 500:
                            pdf_created = True
                            print(f"[Report] PDF created via browser: {pdf_path}", flush=True)
                    except Exception as ex:
                        print(f"[Report] Browser PDF failed: {ex}", flush=True)

                if not pdf_created:
                    return api_response({
                        "format": "html",
                        "path": str(html_path),
                        "dir": str(report_dir),
                        "note": "PDF exported as HTML. Open in browser → Ctrl+P → Save as PDF.",
                    })

                return api_response({
                    "format": "pdf",
                    "path": str(pdf_path),
                    "dir": str(report_dir),
                })
            except ImportError:
                return api_error("'markdown' package not installed. Run: pip install markdown")

        elif fmt == 'docx':
            docx_path = report_dir / f'{p_name}_report_{timestamp}.docx'
            try:
                from docx import Document
                from docx.shared import Inches, Pt, RGBColor
                from docx.enum.text import WD_ALIGN_PARAGRAPH

                doc = Document()

                # Styles
                style = doc.styles['Normal']
                style.font.name = 'Calibri'
                style.font.size = Pt(11)

                # Parse markdown sections
                sections = md_content.split('\n## ')

                # Title from first section
                header_lines = sections[0].strip().split('\n')
                for line in header_lines:
                    if line.startswith('# '):
                        doc.add_heading(line[2:].strip(), level=0)
                    elif line.startswith('## '):
                        doc.add_heading(line[3:].strip(), level=1)
                    elif line.strip() and not line.startswith('---'):
                        p = doc.add_paragraph(line.strip())
                        p.style.font.size = Pt(10)
                        p.style.font.color.rgb = RGBColor(100, 100, 100)

                # Process remaining sections
                for section in sections[1:]:
                    sec_lines = section.strip().split('\n')
                    sec_title = sec_lines[0].strip()
                    doc.add_heading(sec_title, level=1)

                    i = 1
                    while i < len(sec_lines):
                        line = sec_lines[i].strip()

                        # Sub-heading
                        if line.startswith('### '):
                            doc.add_heading(line[4:].strip(), level=2)

                        # Table
                        elif line.startswith('|') and i + 1 < len(sec_lines) and sec_lines[i+1].strip().startswith('|--'):
                            # Parse table
                            headers = [c.strip() for c in line.split('|')[1:-1]]
                            i += 1  # skip separator
                            rows = []
                            while i + 1 < len(sec_lines) and sec_lines[i+1].strip().startswith('|'):
                                i += 1
                                cells = [c.strip() for c in sec_lines[i].split('|')[1:-1]]
                                rows.append(cells)

                            table = doc.add_table(rows=1 + len(rows), cols=len(headers))
                            table.style = 'Light Grid Accent 1'
                            for j, h in enumerate(headers):
                                table.rows[0].cells[j].text = h
                            for r_idx, row in enumerate(rows):
                                for c_idx, cell in enumerate(row):
                                    if c_idx < len(table.columns):
                                        table.rows[r_idx + 1].cells[c_idx].text = cell

                        # Image
                        elif line.startswith('!['):
                            img_name = line.split('(')[-1].rstrip(')')
                            img_path = report_dir / img_name
                            if img_path.exists():
                                doc.add_picture(str(img_path), width=Inches(6))
                                last_paragraph = doc.paragraphs[-1]
                                last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

                        # Bold text
                        elif line.startswith('**'):
                            doc.add_paragraph(line.replace('**', ''), style='Intense Quote')

                        # Regular text
                        elif line and not line.startswith('---') and not line.startswith('<!--'):
                            doc.add_paragraph(line.replace('*', ''))

                        i += 1

                # Footer
                doc.add_paragraph('')
                p = doc.add_paragraph('Generated by CelLAB v3.1.10 | Han Mechanobiology Lab | Michigan Tech')
                p.style.font.size = Pt(9)
                p.style.font.color.rgb = RGBColor(150, 150, 150)

                doc.save(str(docx_path))

                return api_response({
                    "format": "docx",
                    "path": str(docx_path),
                    "dir": str(report_dir),
                })
            except ImportError:
                return api_error("'python-docx' not installed. Run: pip install python-docx")

        else:
            return api_error(f"Unknown format: {fmt}. Use 'md', 'pdf', or 'docx'.")

    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/report/open', methods=['POST'])
def report_open():
    """Open the report directory in the system file explorer."""
    try:
        body = request.get_json()
        path = body.get('path', '')
        dir_path = body.get('dir', '')
        target = dir_path or (str(Path(path).parent) if path else '')

        print(f"[Report] Opening: {target}", flush=True)

        if not target or not os.path.exists(target):
            return api_error(f"Directory not found: {target}")

        if os.name == 'nt':
            import subprocess
            subprocess.Popen(['explorer', target])
        return api_response({"opened": target})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


# ═════════════════════════════════════════════
# ERROR HANDLERS
# ═════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return api_response(error="Endpoint not found", status=404)


@app.errorhandler(500)
def internal_error(e):
    return api_response(error="Internal server error", status=500)


# ═════════════════════════════════════════════
# PYTHON CONSOLE (REPL)
# ═════════════════════════════════════════════

_console_sessions = {}  # {session_id: {namespace: {}, type: 'shared'|'isolated'|'git'}}
_console_next_id = 0

def _create_console_session(session_type='shared'):
    """Create a new console session."""
    global _console_next_id
    _console_next_id += 1
    sid = f"console_{_console_next_id}"

    ns = {'__builtins__': __builtins__, 'os': os, 'json': json, 'Path': Path, 'print': print}

    if session_type == 'shared':
        ns['project'] = _project
        # Grab already-loaded modules
        import sys as _sys
        if 'numpy' in _sys.modules: ns['np'] = _sys.modules['numpy']
        if 'pandas' in _sys.modules: ns['pd'] = _sys.modules['pandas']
        if 'matplotlib.pyplot' in _sys.modules: ns['plt'] = _sys.modules['matplotlib.pyplot']

    elif session_type == 'isolated':
        pass  # bare namespace, user imports what they need

    elif session_type == 'git':
        ns['project'] = _project

    _console_sessions[sid] = {'namespace': ns, 'type': session_type}
    return sid


def _get_git_response(code, project):
    """Handle CelLAB Git commands."""
    parts = code.strip().split()
    if not parts:
        return "", ""

    cmd = parts[0].lower()
    args = parts[1:]

    try:
        if cmd in ('help', '?'):
            return (
                "CelLAB Git Commands:\n"
                "  status          — show project info\n"
                "  commit <msg>    — snapshot all parameters\n"
                "  log [n]         — show commit history (default 10)\n"
                "  diff <a> <b>    — compare two commits\n"
                "  tag <name> [hash] — tag a commit\n"
                "  tags            — list all tags\n"
                "  checkout <hash> — revert params to a commit\n"
                "  help            — show this help\n"
            ), ""

        if cmd == 'status':
            if not project:
                return "", "No project open"
            # Count pipelines across workspaces
            total_pipelines = 0
            pipeline_list = []
            for ws in project._manifest.get('workspaces', []):
                ws_dir = project.workspaces_dir / ws['id']
                if ws_dir.exists():
                    for d in ws_dir.iterdir():
                        if d.is_dir() and (d / 'pipeline.json').exists():
                            p = project._read_json(d / 'pipeline.json')
                            total_pipelines += 1
                            pipeline_list.append(f"    {p.get('name', d.name)} ({p.get('type','')})")

            # Check if params changed since last commit
            last_commit = None
            log_entries = project.log(1)
            if log_entries:
                last_commit = log_entries[0]

            # Count param files and check modification times
            param_files = []
            for ws in project._manifest.get('workspaces', []):
                ws_dir = project.workspaces_dir / ws['id']
                if ws_dir.exists():
                    for p_file in ws_dir.rglob('params.json'):
                        param_files.append(p_file)

            dirty = False
            if last_commit:
                commit_time = last_commit.get('timestamp', '')
                from datetime import datetime
                try:
                    ct = datetime.fromisoformat(commit_time)
                    for pf in param_files:
                        if datetime.fromtimestamp(pf.stat().st_mtime) > ct:
                            dirty = True
                            break
                except:
                    dirty = True
            elif param_files:
                dirty = True  # Never committed but params exist

            lines = [
                f"Project: {project.name}",
                f"Root:    {project.root}",
                f"Workspaces: {len(project._manifest.get('workspaces', []))}",
                f"Pipelines:  {total_pipelines}",
            ]
            for pl in pipeline_list:
                lines.append(pl)

            if last_commit:
                lines.append(f"\nLast commit: {last_commit['hash'][:8]}  {last_commit.get('timestamp','')[:19]}")
                lines.append(f"  \"{last_commit.get('message', '')}\"")
            else:
                lines.append(f"\nNo commits yet")

            if dirty:
                lines.append(f"\n⚠ Parameters modified since last commit")
                lines.append(f"  Use: commit <message>")
            else:
                lines.append(f"\n✓ Clean — no uncommitted changes")

            return '\n'.join(lines) + '\n', ""

        if cmd == 'commit':
            if not project:
                return "", "No project open"
            msg = ' '.join(args) if args else 'Console commit'
            h = project.commit(message=msg, author='console')
            return f"Committed: {h[:8]} — {msg}\n", ""

        if cmd == 'log':
            if not project:
                return "", "No project open"
            n = int(args[0]) if args else 10
            entries = project.log(n)
            if not entries:
                return "No commits yet\n", ""
            lines = []
            for e in entries:
                lines.append(f"  {e['hash'][:8]}  {e.get('timestamp','')[:19]}  {e.get('message','')}")
            return '\n'.join(lines) + '\n', ""

        if cmd == 'diff' and len(args) >= 2:
            if not project:
                return "", "No project open"
            d = project.diff(args[0], args[1])
            return json.dumps(d, indent=2) + '\n', ""

        if cmd == 'tag':
            if not project:
                return "", "No project open"
            if not args:
                return "", "Usage: tag <name> [commit_hash]"
            tag_name = args[0]
            commit_hash = args[1] if len(args) > 1 else None
            project.tag(tag_name=tag_name, commit_hash=commit_hash)
            return f"Tagged: {tag_name}\n", ""

        if cmd == 'tags':
            if not project:
                return "", "No project open"
            tags_dir = project.internal_dir / "history" / "tags"
            if not tags_dir.exists():
                return "No tags\n", ""
            tags = []
            for f in sorted(tags_dir.iterdir()):
                if f.suffix == '.json':
                    t = project._read_json(f)
                    # Try multiple possible key names
                    h = t.get('commit_hash', '') or t.get('hash', '') or t.get('commit', '') or str(list(t.values())[0] if t else '')
                    tags.append(f"  {f.stem}  →  {str(h)[:8]}")
            return '\n'.join(tags) + '\n' if tags else "No tags\n", ""

        if cmd == 'checkout':
            if not project:
                return "", "No project open"
            if not args:
                return "", "Usage: checkout <commit_hash>"
            project.checkout(args[0])
            return f"Checked out: {args[0][:8]}\n", ""

        return "", f"Unknown command: {cmd}. Type 'help' for available commands."

    except Exception as e:
        return "", str(e)


@app.route('/api/console/create', methods=['POST'])
def console_create():
    """Create a new console session. Body: { "type": "shared"|"isolated"|"git" }"""
    body = request.get_json()
    stype = body.get('type', 'shared')
    if stype not in ('shared', 'isolated', 'git'):
        return api_error("type must be 'shared', 'isolated', or 'git'")
    sid = _create_console_session(stype)
    return api_response({"session_id": sid, "type": stype})


@app.route('/api/console/exec', methods=['POST'])
def console_exec():
    """Execute code in a console session. Body: { "session_id": "...", "code": "..." }"""
    import io
    import traceback as tb

    body = request.get_json()
    code = body.get('code', '').strip()
    sid = body.get('session_id', '')

    # Auto-create default shared session if none specified
    if not sid or sid not in _console_sessions:
        if not _console_sessions:
            sid = _create_console_session('shared')
        else:
            sid = list(_console_sessions.keys())[0]

    session = _console_sessions[sid]
    ns = session['namespace']
    stype = session['type']

    if not code:
        return api_response({"stdout": "", "stderr": "", "result": None})

    # Magic commands
    if code in ('clear', 'clc', 'cls'):
        return api_response({"stdout": "", "stderr": "", "result": None, "magic": "clear"})
    if code in ('exit', 'quit'):
        return api_response({"stdout": "Use Ctrl+` to close the console", "stderr": "", "result": None})

    # Always update project reference for shared/git
    if stype in ('shared', 'git'):
        ns['project'] = _project

    # Git terminal — route to git handler
    if stype == 'git':
        stdout, stderr = _get_git_response(code, _project)
        return api_response({"stdout": stdout, "stderr": stderr, "result": None})

    # Python terminals — eval/exec
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = captured_out = io.StringIO()
    sys.stderr = captured_err = io.StringIO()

    result_repr = None

    try:
        try:
            compiled = compile(code, '<console>', 'eval')
            result = eval(compiled, ns, ns)
            if result is not None:
                result_repr = repr(result)
        except SyntaxError:
            compiled = compile(code, '<console>', 'exec')
            exec(compiled, ns, ns)
    except Exception:
        captured_err.write(tb.format_exc())
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return api_response({
        "stdout": captured_out.getvalue(),
        "stderr": captured_err.getvalue(),
        "result": result_repr,
    })


@app.route('/api/console/reset', methods=['POST'])
def console_reset():
    """Reset a console session. Body: { "session_id": "..." }"""
    body = request.get_json()
    sid = body.get('session_id', '')
    if sid in _console_sessions:
        stype = _console_sessions[sid]['type']
        del _console_sessions[sid]
        new_sid = _create_console_session(stype)
        _console_sessions[sid] = _console_sessions.pop(new_sid)
    return api_response({"reset": True})


@app.route('/api/console/namespace', methods=['GET'])
def console_namespace():
    """List names in a console session."""
    sid = request.args.get('session_id', '')
    if sid not in _console_sessions:
        return api_response({})

    ns = _console_sessions[sid]['namespace']
    names = {}
    for k, v in ns.items():
        if k.startswith('_'): continue
        try:
            names[k] = type(v).__name__
        except:
            names[k] = '?'
    return api_response(names)


# ═════════════════════════════════════════════
# CELLVISIA ROUTES
# ═════════════════════════════════════════════
# Thin HTTP layer over cv_manager. The manager owns per-pipeline
# (tree, cache, engine) state; routes translate HTTP intents into
# manager method calls and serialize results for the GUI.

@app.route('/api/cellvisia/<ws_id>/<pipeline_id>/load', methods=['POST'])
def cellvisia_load(ws_id, pipeline_id):
    """Create the full Source chain: Load → ChannelAssignment → ImagingMetadata.

    Body: { "path": "<file path>", "format": "auto" | "tiff" | ... }
    Returns: { success, load_id, channel_id, meta_id, shape, n_frames, n_channels, axes, dtype }
    """
    try:
        body = request.get_json(force=True) or {}
        path = body.get('path')
        if not path:
            return jsonify({'success': False, 'error': 'path is required'}), 400

        try:
            project = get_project()
            resolved = project.resolve_data_path(path)
            if resolved is None:
                return jsonify({'success': False, 'error': f'File not found: {path}'}), 404
            resolved_str = str(resolved)
        except Exception:
            resolved_str = path

        fmt = body.get('format', 'auto')

        cv_manager.destroy_pipeline(pipeline_id)

        load_id = cv_manager.add_feature(pipeline_id, 'load_image_stack',
            params={'path': resolved_str, 'format': fmt}, name='load')
        channel_id = cv_manager.add_feature(pipeline_id, 'channel_assignment',
            params={}, inputs=[load_id], name='channels')
        meta_id = cv_manager.add_feature(pipeline_id, 'imaging_metadata',
            params={}, inputs=[channel_id], name='metadata')

        img = cv_manager.evaluate(pipeline_id, meta_id)

        return jsonify({
            'success': True,
            'load_id': load_id,
            'channel_id': channel_id,
            'meta_id': meta_id,
            'shape': list(img.array.shape),
            'axes': img.axes,
            'n_frames': img.n_frames,
            'n_channels': img.n_channels,
            'dtype': str(img.dtype),
        })
    except FileNotFoundError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except NotImplementedError as e:
        return jsonify({'success': False, 'error': str(e)}), 501
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellvisia/<ws_id>/<pipeline_id>/feature/<feature_id>/params', methods=['POST'])
def cellvisia_set_params(ws_id, pipeline_id, feature_id):
    """Update params on a feature. Body: { ...params }
    Returns: { success }
    """
    try:
        body = request.get_json(force=True) or {}
        if not cv_manager.has_pipeline(pipeline_id):
            return jsonify({'success': False, 'error': 'Pipeline not loaded'}), 404
        cv_manager.set_params(pipeline_id, feature_id, body)
        return jsonify({'success': True})
    except KeyError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellvisia/<ws_id>/<pipeline_id>/add_feature', methods=['POST'])
def cellvisia_add_feature(ws_id, pipeline_id):
    """Add a feature to the pipeline (or update if already exists).

    Body: { feature_type, params, backend_id? }
    If backend_id is provided and exists in the tree, replaces params.
    Otherwise adds a new feature chained after the current terminal.
    Returns: { success, backend_id, mode }
    """
    try:
        body = request.get_json(force=True) or {}
        feature_type = body.get('feature_type')
        params = body.get('params', {})
        backend_id = body.get('backend_id')
        suppressed = bool(body.get('suppressed', False))

        print(f"[CellVisia add_feature] type={feature_type} backend_id={backend_id} suppressed={suppressed} params={params}")

        if not cv_manager.has_pipeline(pipeline_id):
            return jsonify({'success': False, 'error': 'Pipeline not loaded. Load an image first.'}), 404

        state = cv_manager._require(pipeline_id)

        # Update existing feature — REPLACE params (not merge)
        if backend_id and backend_id in state.tree:
            feature = state.tree.get(backend_id)
            feature.params = dict(params)  # full replace
            feature.suppressed = suppressed
            state.engine.mark_dirty(backend_id)
            return jsonify({'success': True, 'backend_id': backend_id, 'mode': 'updated'})

        # Add new — chain after current terminal
        order = state.tree.topological_order()
        terminal_id = order[-1] if order else None
        inputs = [terminal_id] if terminal_id else []

        new_id = cv_manager.add_feature(
            pipeline_id, feature_type, params=params, inputs=inputs)
        if suppressed:
            cv_manager.set_suppressed(pipeline_id, new_id, True)

        return jsonify({'success': True, 'backend_id': new_id, 'mode': 'added'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellvisia/<ws_id>/<pipeline_id>/feature/<fid>/suppress', methods=['POST'])
def cellvisia_suppress_feature(ws_id, pipeline_id, fid):
    """Toggle suppression on a feature. Body: { suppressed: true/false }"""
    try:
        body = request.get_json(force=True) or {}
        suppressed = bool(body.get('suppressed', True))
        if not cv_manager.has_pipeline(pipeline_id):
            return jsonify({'success': False, 'error': 'Pipeline not loaded'}), 404
        state = cv_manager._require(pipeline_id)
        if fid not in state.tree:
            return jsonify({'success': False, 'error': f'Feature {fid} not found'}), 404
        state.engine.set_suppressed(fid, suppressed)
        print(f"[CellVisia suppress] {fid} suppressed={suppressed}")
        return jsonify({'success': True, 'suppressed': suppressed})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellvisia/<ws_id>/<pipeline_id>/feature/<fid>/freeze', methods=['POST'])
def cellvisia_freeze_feature(ws_id, pipeline_id, fid):
    """Freeze or unfreeze a feature. Body: { frozen: true/false }"""
    try:
        body = request.get_json(force=True) or {}
        frozen = bool(body.get('frozen', True))
        if not cv_manager.has_pipeline(pipeline_id):
            return jsonify({'success': False, 'error': 'Pipeline not loaded'}), 404
        state = cv_manager._require(pipeline_id)
        state.engine.set_frozen(fid, frozen)
        return jsonify({'success': True, 'frozen': frozen, 'status': state.tree.get(fid).status})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellvisia/<ws_id>/<pipeline_id>/status_map', methods=['GET'])
def cellvisia_status_map(ws_id, pipeline_id):
    """Return status of all features in the tree."""
    try:
        if not cv_manager.has_pipeline(pipeline_id):
            return jsonify({'success': False, 'error': 'Pipeline not loaded'}), 404
        state = cv_manager._require(pipeline_id)
        return jsonify({'success': True, 'statuses': state.engine.get_status_map()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellvisia/<ws_id>/<pipeline_id>/evaluate', methods=['GET'])
def cellvisia_evaluate(ws_id, pipeline_id):
    """Evaluate the terminal node and return metadata (no image).
    Query: ?feature_id=xxx (optional, defaults to last in topo order)
    Returns: { success, shape, axes, n_frames, n_channels, dtype }
    """
    try:
        if not cv_manager.has_pipeline(pipeline_id):
            return jsonify({'success': False, 'error': 'Pipeline not loaded'}), 404

        state = cv_manager._require(pipeline_id)
        fid = request.args.get('feature_id')
        if fid and fid not in state.tree:
            fid = None  # stale ID
        if not fid:
            order = state.tree.topological_order()
            fid = order[-1] if order else None
        if not fid:
            return jsonify({'success': False, 'error': 'Empty pipeline'}), 400

        img = cv_manager.evaluate(pipeline_id, fid)
        print(f"[CellVisia evaluate] fid={fid} shape={img.array.shape} axes={img.axes}")
        return jsonify({
            'success': True,
            'feature_id': fid,
            'shape': list(img.array.shape),
            'axes': img.axes,
            'n_frames': img.n_frames,
            'n_channels': img.n_channels,
            'dtype': str(img.dtype),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellvisia/<ws_id>/<pipeline_id>/measurements', methods=['GET'])
def cellvisia_measurements(ws_id, pipeline_id):
    """Retrieve measurement results from a feature.
    Query: ?feature_id=xxx
    Returns: { success, measurement: { type, name, columns?, rows?, ... } }
    """
    try:
        if not cv_manager.has_pipeline(pipeline_id):
            return jsonify({'success': False, 'error': 'Pipeline not loaded'}), 404

        fid = request.args.get('feature_id')
        if not fid:
            return jsonify({'success': False, 'error': 'feature_id required'}), 400

        state = cv_manager._require(pipeline_id)
        if fid not in state.tree:
            return jsonify({'success': False, 'error': f'Feature {fid} not found'}), 404

        # Evaluate the feature to populate measurements
        img = cv_manager.evaluate(pipeline_id, fid)
        measurement = img.measurements.get(fid)
        if not measurement:
            return jsonify({'success': False, 'error': 'No measurement data produced'})

        return jsonify({'success': True, 'measurement': measurement, 'measurement_type': state.tree.get(fid).feature_type})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellvisia/<ws_id>/<pipeline_id>/preview_frame', methods=['GET'])
def cellvisia_preview_frame(ws_id, pipeline_id):
    """Serve a single frame as JPEG from the CellVisia engine cache.

    Query params (same convention as FASTIA's preview_frame):
        feature_id  str   which node to evaluate (default: last in topo order)
        frame       int   frame index (default 0)
        channel     int   -1 = composite, 0..N = single channel
        channels    str   comma-separated visible channels for composite
        vmin/vmax   float manual B&C override
        stats       1     return histogram info alongside the image
    """
    try:
        import io, base64
        import numpy as np
        from PIL import Image

        if not cv_manager.has_pipeline(pipeline_id):
            return jsonify({'success': False, 'error': 'Pipeline not loaded'}), 404

        # Which feature to evaluate?
        fid = request.args.get('feature_id')
        state = cv_manager._require(pipeline_id)
        # Validate feature_id — fall back to terminal if stale/missing
        if fid and fid not in state.tree:
            fid = None  # stale ID from before rebuild
        if not fid:
            order = state.tree.topological_order()
            fid = order[-1] if order else None
        if not fid:
            return jsonify({'success': False, 'error': 'Empty pipeline'}), 400

        img_data = cv_manager.evaluate(pipeline_id, fid)
        stack = img_data.array
        axes = img_data.axes

        frame_idx = int(request.args.get('frame', 0))
        channel_idx = int(request.args.get('channel', -1))
        channels_str = request.args.get('channels', '')
        visible_channels = [int(c) for c in channels_str.split(',') if c.strip().isdigit()] if channels_str else None
        vmin_param = request.args.get('vmin')
        vmax_param = request.args.get('vmax')
        has_manual_bc = vmin_param is not None and vmax_param is not None
        if has_manual_bc:
            vmin_val, vmax_val = float(vmin_param), float(vmax_param)
        want_stats = request.args.get('stats') == '1'

        # Extract frame based on axes
        if 'T' in axes and 'C' in axes:
            # TCYX
            n_frames = stack.shape[axes.index('T')]
            n_channels = stack.shape[axes.index('C')]
            frame_idx = min(frame_idx, n_frames - 1)
            frame_data = stack[frame_idx]  # shape: (C, Y, X)

            if channel_idx >= 0 and channel_idx < n_channels:
                frame = frame_data[channel_idx]
            else:
                h, w = frame_data.shape[1], frame_data.shape[2]
                rgb = np.zeros((h, w, 3), dtype=np.float32)
                ch_indices = visible_channels if visible_channels else list(range(min(n_channels, 4)))
                for ci in ch_indices:
                    if ci >= n_channels:
                        continue
                    ch = frame_data[ci].astype(np.float32)
                    if has_manual_bc:
                        p_low, p_high = vmin_val, vmax_val
                    else:
                        p_low, p_high = np.percentile(ch, 0.5), np.percentile(ch, 99.5)
                    if p_high > p_low:
                        ch = np.clip((ch - p_low) / (p_high - p_low), 0, 1)
                    else:
                        ch = np.zeros_like(ch)
                    if ci < 3:
                        rgb[:, :, ci] = ch
                    else:
                        rgb += ch[:, :, np.newaxis]
                rgb = np.clip(rgb, 0, 1)
                frame = (rgb * 255).astype(np.uint8)
        elif 'T' in axes:
            # TYX
            n_frames = stack.shape[axes.index('T')]
            n_channels = 1
            frame_idx = min(frame_idx, n_frames - 1)
            frame = stack[frame_idx]
        else:
            # YX
            n_frames = 1
            n_channels = 1
            frame = stack
            frame_idx = 0

        # Normalize single-channel to 8-bit
        if frame.ndim == 2:
            frame = frame.astype(np.float32)
            if has_manual_bc:
                p_low, p_high = vmin_val, vmax_val
            else:
                p_low, p_high = np.percentile(frame, 0.5), np.percentile(frame, 99.5)
            if p_high > p_low:
                frame = np.clip((frame - p_low) / (p_high - p_low) * 255, 0, 255).astype(np.uint8)
            else:
                frame = np.zeros(frame.shape, dtype=np.uint8)

        # Stats
        stats_data = None
        if want_stats:
            if 'C' in axes and stack.ndim == 4:
                raw = stack[frame_idx, channel_idx if channel_idx >= 0 else 0].astype(np.float32)
            elif 'T' in axes:
                raw = stack[frame_idx].astype(np.float32)
            else:
                raw = stack.astype(np.float32)
            stats_data = {
                'min': float(np.min(raw)), 'max': float(np.max(raw)),
                'mean': float(np.mean(raw)),
                'p05': float(np.percentile(raw, 0.5)), 'p995': float(np.percentile(raw, 99.5)),
            }

        # JPEG encode
        pil_img = Image.fromarray(frame)
        if pil_img.mode not in ('RGB', 'L'):
            pil_img = pil_img.convert('RGB')
        buf = io.BytesIO()
        pil_img.save(buf, format='JPEG', quality=85, optimize=False)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{b64}',
            'frame': frame_idx,
            'n_frames': n_frames,
            'n_channels': n_channels,
            'shape': list(stack.shape),
            'stats': stats_data,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═════════════════════════════════════════════
# CELLADE — Cell Segmentation API
# ═════════════════════════════════════════════

@app.route('/api/cellade/<ws_id>/<pipeline_id>/load', methods=['POST'])
def cellade_load(ws_id, pipeline_id):
    """Load image for CellADE."""
    if not cellade_manager:
        return jsonify({'success': False, 'error': 'CellADE not available'}), 500
    try:
        body = request.get_json()
        result = cellade_manager.load_image(pipeline_id, body.get('file_path', ''))
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellade/<ws_id>/<pipeline_id>/load_gt', methods=['POST'])
def cellade_load_gt(ws_id, pipeline_id):
    """Load ground truth label image."""
    if not cellade_manager:
        return jsonify({'success': False, 'error': 'CellADE not available'}), 500
    try:
        body = request.get_json()
        result = cellade_manager.load_gt(pipeline_id, body.get('file_path', ''))
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellade/<ws_id>/<pipeline_id>/run', methods=['POST'])
def cellade_run(ws_id, pipeline_id):
    """Run CellADE segmentation."""
    if not cellade_manager:
        return jsonify({'success': False, 'error': 'CellADE not available'}), 500
    try:
        body = request.get_json()
        result = cellade_manager.run(pipeline_id, body.get('params', {}))
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellade/<ws_id>/<pipeline_id>/plot/<plot_type>', methods=['POST'])
def cellade_plot(ws_id, pipeline_id, plot_type):
    """Generate a CellADE plot and return as base64 PNG."""
    if not cellade_manager:
        return jsonify({'success': False, 'error': 'CellADE not available'}), 500
    try:
        result = cellade_manager.plot(pipeline_id, plot_type)
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═════════════════════════════════════════════
# CELLFADE — FA Detection API
# ═════════════════════════════════════════════

@app.route('/api/cellfade/<ws_id>/<pipeline_id>/load', methods=['POST'])
def cellfade_load(ws_id, pipeline_id):
    if not cellfade_manager:
        return jsonify({'success': False, 'error': 'CellFADE not available'}), 500
    try:
        body = request.get_json()
        result = cellfade_manager.load(pipeline_id, body.get('fa_path', ''), body.get('boundary_path', ''))
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cellfade/<ws_id>/<pipeline_id>/run', methods=['POST'])
def cellfade_run(ws_id, pipeline_id):
    if not cellfade_manager:
        return jsonify({'success': False, 'error': 'CellFADE not available'}), 500
    try:
        body = request.get_json()
        result = cellfade_manager.run(pipeline_id, body.get('params', {}))
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═════════════════════════════════════════════
# ANNOTADE — Annotation Tool API
# ═════════════════════════════════════════════

@app.route('/api/annotade/<ws_id>/<pipeline_id>/load', methods=['POST'])
def annotade_load(ws_id, pipeline_id):
    if not annotade_manager:
        return jsonify({'success': False, 'error': 'AnnotADE not available'}), 500
    try:
        body = request.get_json()
        result = annotade_manager.load(pipeline_id, body.get('path', ''))
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/annotade/<ws_id>/<pipeline_id>/frame/<int:idx>')
def annotade_frame(ws_id, pipeline_id, idx):
    if not annotade_manager:
        return jsonify({'success': False, 'error': 'AnnotADE not available'}), 500
    try:
        brightness = float(request.args.get('brightness', 0))
        contrast = float(request.args.get('contrast', 1.0))
        result = annotade_manager.get_frame(pipeline_id, idx, brightness, contrast)
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/annotade/<ws_id>/<pipeline_id>/assist', methods=['POST'])
def annotade_assist(ws_id, pipeline_id):
    if not annotade_manager:
        return jsonify({'success': False, 'error': 'AnnotADE not available'}), 500
    try:
        body = request.get_json()
        method = body.pop('method', '')
        frame = body.pop('frame', 0)
        result = annotade_manager.assist(pipeline_id, method, frame, **body)
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/annotade/<ws_id>/<pipeline_id>/clear_labels', methods=['POST'])
def annotade_clear_labels(ws_id, pipeline_id):
    if not annotade_manager:
        return jsonify({'success': False, 'error': 'AnnotADE not available'}), 500
    try:
        body = request.get_json()
        annotade_manager.clear_labels(pipeline_id, body.get('frame', 0))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/annotade/<ws_id>/<pipeline_id>/labels/<int:frame>', methods=['POST'])
def annotade_set_labels(ws_id, pipeline_id, frame):
    if not annotade_manager:
        return jsonify({'success': False, 'error': 'AnnotADE not available'}), 500
    try:
        body = request.get_json()
        annotade_manager.set_labels(pipeline_id, frame, body.get('data', ''))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/annotade/<ws_id>/<pipeline_id>/export', methods=['POST'])
def annotade_export(ws_id, pipeline_id):
    if not annotade_manager:
        return jsonify({'success': False, 'error': 'AnnotADE not available'}), 500
    try:
        result = annotade_manager.export(pipeline_id)
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═════════════════════════════════════════════
# ASSOCIA — Signal Coupling API
# ═════════════════════════════════════════════

@app.route('/api/associa/<ws_id>/<pipeline_id>/load', methods=['POST'])
def associa_load(ws_id, pipeline_id):
    """Load a CSV file for Associa analysis.
    Body: { file_path, has_header: 'auto'|'yes'|'no' }
    Returns: { success, mode, n_signals, n_samples, n_pairs, signal_names }
    """
    if not assoc_manager:
        return jsonify({'success': False, 'error': 'Associa not available'}), 500
    try:
        body = request.get_json()
        file_path = body.get('file_path', '')
        has_header = body.get('has_header', 'auto')
        result = assoc_manager.load_csv(pipeline_id, file_path, has_header)
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/associa/<ws_id>/<pipeline_id>/run', methods=['POST'])
def associa_run(ws_id, pipeline_id):
    """Run Associa analysis on all pairs.
    Body: { config: { stationarizer, methods, surrogate } }
    Returns: { success, run_id, n_pairs, n_significant, summary }
    """
    if not assoc_manager:
        return jsonify({'success': False, 'error': 'Associa not available'}), 500
    try:
        body = request.get_json()
        config = body.get('config', {})
        result = assoc_manager.run(pipeline_id, config)
        return jsonify({'success': True, **result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/associa/<ws_id>/<pipeline_id>/status', methods=['GET'])
def associa_status(ws_id, pipeline_id):
    """Get Associa pipeline state."""
    if not assoc_manager:
        return jsonify({'success': False, 'error': 'Associa not available'}), 500
    state = assoc_manager.get_state(pipeline_id)
    if not state:
        return jsonify({'success': True, 'loaded': False})
    return jsonify({
        'success': True,
        'loaded': bool(state.signals),
        'mode': state.mode,
        'n_signals': len(state.signal_names),
        'n_samples': state.n_samples,
        'n_pairs': len(state.pairs),
        'signal_names': state.signal_names,
        'runs': list(state.runs.keys()),
    })


@app.route('/api/associa/<ws_id>/<pipeline_id>/runs/<run_id>', methods=['GET'])
def associa_get_run(ws_id, pipeline_id, run_id):
    """Get results for a specific run."""
    if not assoc_manager:
        return jsonify({'success': False, 'error': 'Associa not available'}), 500
    state = assoc_manager.get_state(pipeline_id)
    if not state or run_id not in state.runs:
        return jsonify({'success': False, 'error': f'Run {run_id} not found'}), 404
    run_data = state.runs[run_id]
    return jsonify({'success': True, **run_data})


# ═════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════

if __name__ == '__main__':
    import argparse
    import webbrowser
    import threading

    parser = argparse.ArgumentParser(description='CelLAB Backend Server')
    parser.add_argument('--port', type=int, default=5000, help='Port (default: 5000)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    parser.add_argument('--open', type=str, help='Open a .cellab project on startup')

    args = parser.parse_args()

    if args.open:
        try:
            _project = CellabProject.open(args.open)
            print(f"Opened project: {_project.name} at {_project.root}")
        except Exception as e:
            print(f"Failed to open project: {e}")

    print(f"\n  ╔══════════════════════════════════════╗")
    print(f"  ║        CelLAB Workbench v3.1         ║")
    print(f"  ║                                      ║")
    print(f"  ║   Open: http://{args.host}:{args.port}       ║")
    print(f"  ║   Press Ctrl+C to stop               ║")
    print(f"  ╚══════════════════════════════════════╝\n")

    # Auto-open browser after a short delay (so Flask is ready)
    def _open_browser():
        import time
        time.sleep(1.2)
        webbrowser.open(f"http://{args.host}:{args.port}")
    threading.Thread(target=_open_browser, daemon=True).start()

    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False, threaded=True)
