"""
CellADE Manager — backend orchestrator for the CellADE CelLAB module.

Wraps shared_modules/cellade/ engine. Handles:
  - Image loading (TIFF/PNG/JPG → grayscale float32)
  - Ground truth loading (label image)
  - Run dispatch with params from UI
  - Preview/overlay generation as base64 JPEG

Location: backend/cellade_manager.py
"""

from __future__ import annotations

import base64
import io
import time
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

_cellade_cls = None


def _get_cellade():
    global _cellade_cls
    if _cellade_cls is None:
        import sys
        root = Path(__file__).resolve().parent
        sys.path.insert(0, str(root / 'shared_modules'))
        from cellade.cellade import CellADE
        _cellade_cls = CellADE
    return _cellade_cls


def _image_to_base64(arr_2d, colormap=False):
    """Convert 2D array to base64 JPEG string for frontend display."""
    from PIL import Image
    if colormap:
        from skimage.color import label2rgb
        rgb = (label2rgb(arr_2d, bg_label=0) * 255).astype(np.uint8)
        img = Image.fromarray(rgb)
    else:
        f = arr_2d.astype(np.float64)
        mx = f.max() or 1.0
        img = Image.fromarray((f / mx * 255).astype(np.uint8))
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def _fig_to_base64(fig):
    """Convert matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    import matplotlib.pyplot as plt
    plt.close(fig)
    buf.seek(0)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


class CellADEState:
    """Per-pipeline state."""
    def __init__(self):
        self.image: Optional[np.ndarray] = None
        self.gt_labels: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.info: Optional[Dict] = None
        self.file_path: str = ''
        self.gt_path: str = ''


class CellADEManager:
    """Manages CellADE instances per pipeline."""

    def __init__(self):
        self._states: Dict[str, CellADEState] = {}

    def _require(self, pid: str) -> CellADEState:
        if pid not in self._states:
            self._states[pid] = CellADEState()
        return self._states[pid]

    def load_image(self, pid: str, file_path: str) -> Dict:
        """Load an image file. Returns shape/dtype/preview."""
        from skimage import io as skio

        state = self._require(pid)
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        image = skio.imread(str(path))
        if image.ndim == 3:
            if image.shape[2] == 4:
                image = image[:, :, :3]
            image = np.mean(image, axis=2)
        image = image.astype(np.float32)
        if image.max() > 1:
            image = image / image.max()

        state.image = image
        state.file_path = file_path
        state.labels = None
        state.info = None

        return {
            'shape': f'{image.shape[0]}×{image.shape[1]}',
            'dtype': str(image.dtype),
            'vmin': round(float(image.min()), 4),
            'vmax': round(float(image.max()), 4),
            'preview': _image_to_base64(image),
        }

    def load_gt(self, pid: str, file_path: str) -> Dict:
        """Load ground truth label image."""
        from skimage import io as skio

        state = self._require(pid)
        gt = skio.imread(str(file_path)).astype(np.int32)
        state.gt_labels = gt
        state.gt_path = file_path
        return {'n_cells': int(gt.max())}

    def run(self, pid: str, params: Dict = None) -> Dict:
        """Run CellADE pipeline."""
        state = self._require(pid)
        if state.image is None:
            raise RuntimeError("No image loaded.")

        CellADE = _get_cellade()

        # Merge UI params with defaults
        run_params = {}
        if params:
            for k, v in params.items():
                if isinstance(v, str):
                    # Try to parse as number
                    try:
                        v = float(v)
                        if v == int(v):
                            v = int(v)
                    except (ValueError, TypeError):
                        pass
                if isinstance(v, str) and v in ('true', 'True'):
                    v = True
                elif isinstance(v, str) and v in ('false', 'False'):
                    v = False
                run_params[k] = v

        segmenter = CellADE(params=run_params)
        labels, info = segmenter.run(state.image, detail=True)

        state.labels = labels
        state.info = info

        result = {
            'n_regions': int(labels.max()),
            'elapsed_s': info.get('elapsed_s', 0),
            'overlay': _image_to_base64(labels, colormap=True),
        }

        # Evaluate if GT available
        if state.gt_labels is not None:
            from cellade.evaluation import evaluate
            metrics = evaluate(labels, state.gt_labels)
            result['metrics'] = {
                'F1': float(metrics.get('F1', 0)),
                'mAP': float(metrics.get('mAP', 0)),
                'Dice_FG': float(metrics.get('Dice_FG', 0)),
                'Pred': int(metrics.get('Pred', 0)),
                'GT': int(metrics.get('GT', 0)),
            }

        return result

    def get_state(self, pid: str) -> Optional[CellADEState]:
        return self._states.get(pid)

    def has_pipeline(self, pid: str) -> bool:
        return pid in self._states

    # ─── Plotting ────────────────────────────────────────────────────────────

    def plot(self, pid: str, plot_type: str) -> Dict:
        """Generate a matplotlib plot, return as base64 PNG."""
        state = self._require(pid)
        if state.labels is None:
            raise RuntimeError("Run CellADE first.")

        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from skimage.color import label2rgb
        from skimage.measure import regionprops, find_contours

        if plot_type == 'pipeline':
            return self._plot_pipeline(state, plt, label2rgb, find_contours)
        elif plot_type == 'overlay':
            return self._plot_overlay(state, plt, label2rgb, find_contours)
        elif plot_type == 'stress':
            return self._plot_stress(state, plt)
        elif plot_type == 'metrics':
            return self._plot_metrics(state, plt)
        else:
            raise ValueError(f"Unknown plot type: {plot_type}")

    def _plot_pipeline(self, state, plt, label2rgb, find_contours):
        """Original | Overlay | Boundaries — 3-panel overview."""
        from skimage.measure import regionprops
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.patch.set_facecolor('#1a1a2e')
        for ax in axes:
            ax.set_facecolor('#16213e')
            ax.tick_params(colors='#aaa', labelsize=8)

        image = state.image
        labels = state.labels

        # Panel 1: Original
        axes[0].imshow(image, cmap='gray')
        axes[0].set_title(f'Original ({image.shape[0]}×{image.shape[1]})',
                         color='white', fontsize=11)
        axes[0].axis('off')

        # Panel 2: Colored overlay
        overlay = label2rgb(labels, image=image, bg_label=0, alpha=0.4)
        axes[1].imshow(overlay)
        axes[1].set_title(f'CellADE — {labels.max()} regions',
                         color='white', fontsize=11)
        axes[1].axis('off')

        # Panel 3: Boundaries on image
        axes[2].imshow(image, cmap='gray')
        for region in regionprops(labels):
            mask = labels == region.label
            contours = find_contours(mask.astype(float), 0.5)
            for c in contours:
                axes[2].plot(c[:, 1], c[:, 0], linewidth=0.8, color='#2196f3')
        axes[2].set_title('Cell Boundaries', color='white', fontsize=11)
        axes[2].axis('off')

        # GT overlay if available
        if state.gt_labels is not None:
            from cellade.evaluation import evaluate
            metrics = evaluate(labels, state.gt_labels)
            fig.suptitle(
                f'F1@0.5 = {metrics["F1"]:.3f}  |  mAP = {metrics["mAP"]:.3f}  |  '
                f'Pred: {metrics["Pred"]}  GT: {metrics["GT"]}',
                color='#4caf50', fontsize=12, y=0.02)

        plt.tight_layout()
        return {'image': _fig_to_base64(fig), 'title': 'Pipeline Overview'}

    def _plot_overlay(self, state, plt, label2rgb, find_contours):
        """Full-resolution colored overlay with boundaries."""
        from skimage.measure import regionprops
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#16213e')

        overlay = label2rgb(state.labels, image=state.image, bg_label=0, alpha=0.35)
        ax.imshow(overlay)

        # Draw boundaries
        for region in regionprops(state.labels):
            mask = state.labels == region.label
            contours = find_contours(mask.astype(float), 0.5)
            for c in contours:
                ax.plot(c[:, 1], c[:, 0], linewidth=0.6, color='white', alpha=0.7)
            # Label centroid
            y, x = region.centroid
            ax.text(x, y, str(region.label), fontsize=6, color='white',
                    ha='center', va='center', alpha=0.8,
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='black', alpha=0.4))

        ax.set_title(f'Segmentation — {state.labels.max()} cells', color='white', fontsize=12)
        ax.axis('off')
        plt.tight_layout()
        return {'image': _fig_to_base64(fig), 'title': 'Segmentation Overlay'}

    def _plot_stress(self, state, plt):
        """Stress heatmap for all regions above min size."""
        from cellade.operations.stress import solve_poisson, compute_stress
        from skimage.measure import regionprops

        labels = state.labels
        stress_map = np.zeros_like(labels, dtype=np.float64)

        for region in regionprops(labels):
            if region.area < 50:
                continue
            mask = (labels == region.label)
            try:
                w = solve_poisson(mask)
                stress = compute_stress(w, mask)
                stress_map[mask] = stress[mask]
            except Exception:
                pass

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#1a1a2e')
        for ax in axes:
            ax.set_facecolor('#16213e')

        axes[0].imshow(state.image, cmap='gray')
        axes[0].set_title('Original', color='white', fontsize=11)
        axes[0].axis('off')

        im = axes[1].imshow(stress_map, cmap='hot', interpolation='nearest')
        axes[1].imshow(state.image, cmap='gray', alpha=0.3)
        axes[1].set_title('Von Mises Stress (neck = high stress)', color='white', fontsize=11)
        axes[1].axis('off')
        plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)

        plt.tight_layout()
        return {'image': _fig_to_base64(fig), 'title': 'Stress Analysis'}

    def _plot_metrics(self, state, plt):
        """Bar chart of evaluation metrics."""
        if state.gt_labels is None:
            raise RuntimeError("Load ground truth first for metrics plot.")

        from cellade.evaluation import evaluate
        metrics = evaluate(state.labels, state.gt_labels)

        fig, ax = plt.subplots(1, 1, figsize=(8, 5))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#16213e')

        names = ['F1@0.5', 'mAP', 'Dice FG']
        values = [metrics.get('F1', 0), metrics.get('mAP', 0), metrics.get('Dice_FG', 0)]
        colors = ['#4caf50', '#2196f3', '#ff9800']

        bars = ax.bar(names, values, color=colors, width=0.5, edgecolor='white', linewidth=0.5)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{val:.3f}', ha='center', va='bottom', color='white', fontsize=12, fontweight='bold')

        ax.set_ylim(0, 1.1)
        ax.set_ylabel('Score', color='white', fontsize=11)
        ax.tick_params(colors='white', labelsize=10)
        ax.set_title(f'CellADE — Pred: {metrics["Pred"]} | GT: {metrics["GT"]}',
                     color='white', fontsize=12)
        ax.spines['bottom'].set_color('#555')
        ax.spines['left'].set_color('#555')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        return {'image': _fig_to_base64(fig), 'title': 'Evaluation Metrics'}
