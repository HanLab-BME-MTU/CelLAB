"""
CellADE plotter — boundary smoothing debug visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage.color import label2rgb
from skimage.measure import regionprops

def plot_smoothing_debug(image, labels_original, labels_smoothed, smoothing_info, 
                         n_cols=4, max_regions=16):
    """
    Visualize FFT smoothing results for multiple regions.
    
    Shows original vs smoothed boundaries for each region.
    """
    # Get regions that were smoothed
    smoothed_regions = [rid for rid in smoothing_info.keys() 
                        if smoothing_info[rid].get('contour_smoothed') is not None]
    
    if len(smoothed_regions) == 0:
        print("No regions were smoothed")
        return
    
    # Limit number of regions to show
    regions_to_show = smoothed_regions[:max_regions]
    n_regions = len(regions_to_show)
    n_rows = (n_regions + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 5 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    axes = axes.flatten()
    
    for idx, region_id in enumerate(regions_to_show):
        ax = axes[idx]
        info = smoothing_info[region_id]
        
        orig_mask = info.get('original_mask')
        smooth_mask = info.get('smoothed_mask')
        contour_orig = info.get('contour_original')
        contour_smooth = info.get('contour_smoothed')
        
        if orig_mask is None:
            ax.set_title(f'Region {region_id}\n(no data)')
            ax.axis('off')
            continue
        
        # Get bounding box
        ys, xs = np.where(orig_mask)
        if len(ys) == 0:
            ax.axis('off')
            continue
            
        margin = 10
        y0, y1 = max(0, ys.min() - margin), min(orig_mask.shape[0], ys.max() + margin)
        x0, x1 = max(0, xs.min() - margin), min(orig_mask.shape[1], xs.max() + margin)
        
        # Show image background
        if image is not None:
            ax.imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.5)
        
        # Show original mask (light blue)
        orig_vis = np.zeros((y1-y0, x1-x0, 4))
        orig_vis[orig_mask[y0:y1, x0:x1], :] = [0, 0, 1, 0.2]
        ax.imshow(orig_vis)
        
        # Show smoothed mask (light green)
        if smooth_mask is not None:
            smooth_vis = np.zeros((y1-y0, x1-x0, 4))
            smooth_vis[smooth_mask[y0:y1, x0:x1], :] = [0, 1, 0, 0.2]
            ax.imshow(smooth_vis)
        
        # Show contours
        if contour_orig is not None:
            ax.plot(contour_orig[:, 1] - x0, contour_orig[:, 0] - y0, 
                   'r-', linewidth=1.5, alpha=0.8, label='original')
        
        if contour_smooth is not None:
            ax.plot(contour_smooth[:, 1] - x0, contour_smooth[:, 0] - y0, 
                   'g-', linewidth=2, label='smoothed')
        
        # Title with area change
        orig_area = info.get('original_area', 0)
        smooth_area = info.get('smoothed_area', 0)
        area_change = info.get('area_change', 0)
        
        ax.set_title(f'R{region_id}: {orig_area}→{smooth_area} ({area_change:+d})')
        ax.set_xlim(0, x1 - x0)
        ax.set_ylim(y1 - y0, 0)
        ax.axis('off')
    
    # Clear unused axes
    for idx in range(n_regions, len(axes)):
        axes[idx].axis('off')
    
    # Add legend to first plot
    if n_regions > 0:
        axes[0].legend(loc='upper right', fontsize=8)
    
    plt.suptitle('FFT Boundary Smoothing: Red=Original, Green=Smoothed', fontsize=14)
    plt.tight_layout()
    plt.show()
    
    # Also show full image comparison
    fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))
    
    # Original boundaries
    axes2[0].imshow(image, cmap='gray')
    orig_fg = labels_original > 0
    orig_bounds = orig_fg ^ binary_erosion(orig_fg)
    orig_bound_vis = np.zeros((*image.shape, 4))
    orig_bound_vis[orig_bounds, :] = [1, 0, 0, 0.8]
    axes2[0].imshow(orig_bound_vis)
    axes2[0].set_title(f'Original Boundaries\n({labels_original.max()} regions)')
    axes2[0].axis('off')
    
    # Smoothed boundaries
    axes2[1].imshow(image, cmap='gray')
    smooth_fg = labels_smoothed > 0
    smooth_bounds = smooth_fg ^ binary_erosion(smooth_fg)
    smooth_bound_vis = np.zeros((*image.shape, 4))
    smooth_bound_vis[smooth_bounds, :] = [0, 1, 0, 0.8]
    axes2[1].imshow(smooth_bound_vis)
    axes2[1].set_title(f'Smoothed Boundaries\n({labels_smoothed.max()} regions)')
    axes2[1].axis('off')
    
    # Overlay comparison
    axes2[2].imshow(image, cmap='gray')
    axes2[2].imshow(orig_bound_vis)
    smooth_bound_vis2 = np.zeros((*image.shape, 4))
    smooth_bound_vis2[smooth_bounds, :] = [0, 1, 0, 0.8]
    axes2[2].imshow(smooth_bound_vis2)
    axes2[2].set_title('Comparison\nRed=Original, Green=Smoothed')
    axes2[2].axis('off')
    
    plt.tight_layout()
    plt.show()

