"""
CellADE — Cell segmentation via Adaptive Diffusion Equations.

Physics-based cell/nucleus segmentation. Zero training, CPU-only.
F1@0.5 = 0.811 on BBBC039, 0.794 on DSB2018.

Usage:
    from cellade import CellADE
    segmenter = CellADE(params={...})
    labels = segmenter.run(image)
"""

from .cellade import CellADE, DEFAULT_PARAMS

__all__ = ['CellADE', 'DEFAULT_PARAMS']
