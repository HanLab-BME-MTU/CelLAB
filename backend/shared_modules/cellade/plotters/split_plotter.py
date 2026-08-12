"""
CellADE plotter — split result visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage.color import label2rgb

def plot_split_result_chunk(image, original_mask, split_labeled, n_parts, cut_lines, region_id):
    """Plot the result of a chunk-tracking split."""
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    
    ys, xs = np.where(original_mask)
    margin = 10
    y0, y1 = max(0, ys.min() - margin), min(original_mask.shape[0], ys.max() + margin)
    x0, x1 = max(0, xs.min() - margin), min(original_mask.shape[1], xs.max() + margin)
    
    # Original
    axes[0].imshow(image[y0:y1, x0:x1], cmap='gray')
    axes[0].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
    axes[0].set_title(f'Original Region {region_id}\n({original_mask.sum()} pixels)')
    axes[0].axis('off')
    
    # Cut lines
    axes[1].imshow(image[y0:y1, x0:x1], cmap='gray')
    axes[1].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.3)
    for cut_info in cut_lines:
        cut_mask = cut_info.get('mask')
        if cut_mask is not None:
            cut_vis = np.zeros((y1-y0, x1-x0, 4))
            cut_vis[cut_mask[y0:y1, x0:x1], :] = [1, 0, 0, 0.8]
            axes[1].imshow(cut_vis)
            endpoints = cut_info.get('endpoints')
            if endpoints:
                e1, e2 = endpoints
                axes[1].plot([e1[1] - x0, e2[1] - x0], [e1[0] - y0, e2[0] - y0], 'r-', linewidth=2)
    axes[1].set_title(f'Cut Lines\n({len(cut_lines)} lines)')
    axes[1].axis('off')
    
    # Final labeled result
    axes[2].imshow(split_labeled[y0:y1, x0:x1], cmap='nipy_spectral')
    part_sizes = [((split_labeled == i).sum()) for i in range(1, n_parts + 1)]
    axes[2].set_title(f'Final: {n_parts} parts\nSizes: {part_sizes}')
    axes[2].axis('off')
    
    # Overlay on original image
    axes[3].imshow(image[y0:y1, x0:x1], cmap='gray')
    for i in range(1, n_parts + 1):
        part_mask = (split_labeled == i)
        if part_mask.sum() > 0:
            part_boundary = part_mask ^ binary_erosion(part_mask)
            color_overlay = np.zeros((y1-y0, x1-x0, 4))
            color = plt.cm.tab10(i / 10)
            color_overlay[part_boundary[y0:y1, x0:x1], :] = [color[0], color[1], color[2], 0.8]
            axes[3].imshow(color_overlay)
    axes[3].set_title('Result overlay')
    axes[3].axis('off')
    
    plt.tight_layout()
    plt.show()


