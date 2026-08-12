"""
CellADE plotter — stress analysis visualization (single + all regions).
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage.color import label2rgb
from skimage.measure import regionprops

from ..operations.stress import solve_poisson, compute_stress, compute_z_scores, compute_neck_score

def plot_stress_analysis(image, labels, region_id, params):
    """Plot stress concentration analysis for a single region."""
    mask = (labels == region_id)
    
    cut_peak_to_mean = params.get('cut_peak_to_mean', 2.0)
    cut_max_z = params.get('cut_max_z', 2.5)
    
    w = solve_poisson(mask)
    stress = compute_stress(w, mask)
    stress_smooth = gaussian(stress, sigma=2)
    z, stats = compute_z_scores(stress_smooth, mask)
    
    # Find hot pixels
    hot_mask = (z > cut_max_z) & mask
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    ys, xs = np.where(mask)
    margin = 15
    y0, y1 = max(0, ys.min() - margin), min(labels.shape[0], ys.max() + margin)
    x0, x1 = max(0, xs.min() - margin), min(labels.shape[1], xs.max() + margin)
    
    # Row 1
    axes[0, 0].imshow(image[y0:y1, x0:x1], cmap='gray')
    axes[0, 0].imshow(mask[y0:y1, x0:x1], cmap='Reds', alpha=0.3)
    axes[0, 0].set_title(f'Region {region_id} (size={mask.sum()})')
    axes[0, 0].axis('off')
    
    stress_display = np.zeros_like(stress)
    stress_display[mask] = stress_smooth[mask]
    im1 = axes[0, 1].imshow(stress_display[y0:y1, x0:x1], cmap='hot')
    axes[0, 1].set_title(f'Stress Field\npeak/mean={stats["peak_to_mean"]:.2f}')
    axes[0, 1].axis('off')
    plt.colorbar(im1, ax=axes[0, 1], fraction=0.046)
    
    z_display = np.zeros_like(z)
    z_display[mask] = z[mask]
    im2 = axes[0, 2].imshow(z_display[y0:y1, x0:x1], cmap='hot')
    axes[0, 2].set_title(f'Z-Score\nmax_z={stats["max_z"]:.2f}')
    axes[0, 2].axis('off')
    plt.colorbar(im2, ax=axes[0, 2], fraction=0.046)
    
    # Row 2
    axes[1, 0].imshow(mask[y0:y1, x0:x1], cmap='gray')
    axes[1, 0].imshow(hot_mask[y0:y1, x0:x1], cmap='Reds', alpha=0.6)
    axes[1, 0].set_title(f'Hot Pixels (z>{cut_max_z})\n{hot_mask.sum()} pixels to erode')
    axes[1, 0].axis('off')
    
    # Try erosion split
    split_labeled, n_parts, eroded_pixels = split_region_erosion(mask, params)
    
    axes[1, 1].imshow(image[y0:y1, x0:x1], cmap='gray')
    axes[1, 1].imshow(mask[y0:y1, x0:x1], cmap='Blues', alpha=0.3)
    # Show eroded pixels
    if eroded_pixels:
        eroded_mask = np.zeros_like(mask, dtype=bool)
        for (ey, ex) in eroded_pixels:
            eroded_mask[ey, ex] = True
        axes[1, 1].imshow(eroded_mask[y0:y1, x0:x1], cmap='Reds', alpha=0.8)
    axes[1, 1].set_title(f'Eroded Pixels\n{len(eroded_pixels)} total')
    axes[1, 1].axis('off')
    
    # Result
    axes[1, 2].imshow(split_labeled[y0:y1, x0:x1], cmap='nipy_spectral')
    part_sizes = [((split_labeled == i).sum()) for i in range(1, n_parts + 1)]
    axes[1, 2].set_title(f'Result: {n_parts} parts\nSizes: {part_sizes}')
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    plt.show()


def plot_all_regions_stress(image, labels, params, min_size=50):
    """Plot stress field for all regions in a grid with erosion analysis."""
    
    cut_peak_to_mean = params.get('cut_peak_to_mean', 2.0)
    cut_max_z = params.get('cut_max_z', 2.5)
    
    region_ids = []
    for rid in range(1, labels.max() + 1):
        mask = (labels == rid)
        if mask.sum() >= min_size:
            region_ids.append(rid)
    
    n_regions = len(region_ids)
    if n_regions == 0:
        print("No regions large enough")
        return
    
    print(f"Plotting {n_regions} regions...")
    print(f"Cut thresholds: peak/mean > {cut_peak_to_mean}, max_z > {cut_max_z}")
    
    n_cols = 5
    n_rows = (n_regions + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 4 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    axes = axes.flatten()
    
    for idx, region_id in enumerate(region_ids):
        ax = axes[idx]
        
        mask = (labels == region_id)
        
        ys, xs = np.where(mask)
        margin = 5
        y0, y1 = max(0, ys.min() - margin), min(labels.shape[0], ys.max() + margin)
        x0, x1 = max(0, xs.min() - margin), min(labels.shape[1], xs.max() + margin)
        
        w = solve_poisson(mask)
        stress = compute_stress(w, mask)
        stress_smooth = gaussian(stress, sigma=2)
        z, stats = compute_z_scores(stress_smooth, mask)
        
        peak_to_mean = stats.get('peak_to_mean', 0)
        max_z = stats.get('max_z', 0)
        
        log_stress = np.zeros_like(stress_smooth)
        log_stress[mask] = np.log1p(stress_smooth[mask])
        
        # Hot pixels to erode
        hot_mask = (z > cut_max_z) & mask
        
        ax.imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
        ax.imshow(log_stress[y0:y1, x0:x1], cmap='hot', alpha=0.7)
        
        # Show hot pixels in green
        if hot_mask.sum() > 0:
            hot_vis = np.zeros((y1-y0, x1-x0, 4))
            hot_vis[hot_mask[y0:y1, x0:x1], :] = [0, 1, 0, 0.6]
            ax.imshow(hot_vis)
        
        # Show max stress point
        stress_masked = stress_smooth.copy()
        stress_masked[~mask] = 0
        if stress_masked.max() > 0:
            max_idx = np.argmax(stress_masked)
            max_y, max_x = np.unravel_index(max_idx, stress_smooth.shape)
            ax.plot(max_x - x0, max_y - y0, 'y*', markersize=12)
        
        should_cut = (peak_to_mean > cut_peak_to_mean) and (max_z > cut_max_z)
        marker = " ***" if should_cut else ""
        ax.set_title(f'R{region_id} (n={mask.sum()})\np/m={peak_to_mean:.1f}, z={max_z:.1f}{marker}')
        ax.axis('off')
    
    for idx in range(len(region_ids), len(axes)):
        axes[idx].axis('off')
    
    plt.suptitle(f'Raw Stress Fields (green=hot pixels, yellow*=max) | Thresholds: p/m>{cut_peak_to_mean}, z>{cut_max_z}', y=1.02)
    plt.tight_layout()
    plt.show()


def plot_all_regions_neck_score(image, labels, params, min_size=50):
    """Plot neck_score field for all regions in a grid - shows filtered stress that suppresses edge artifacts."""
    
    cut_peak_to_mean = params.get('cut_peak_to_mean', 2.0)
    cut_max_z = params.get('cut_max_z', 2.5)
    
    region_ids = []
    for rid in range(1, labels.max() + 1):
        mask = (labels == rid)
        if mask.sum() >= min_size:
            region_ids.append(rid)
    
    n_regions = len(region_ids)
    if n_regions == 0:
        print("No regions large enough")
        return
    
    print(f"Plotting neck_score for {n_regions} regions...")
    
    n_cols = 5
    n_rows = (n_regions + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 4 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    axes = axes.flatten()
    
    for idx, region_id in enumerate(region_ids):
        ax = axes[idx]
        
        mask = (labels == region_id)
        
        ys, xs = np.where(mask)
        margin = 5
        y0, y1 = max(0, ys.min() - margin), min(labels.shape[0], ys.max() + margin)
        x0, x1 = max(0, xs.min() - margin), min(labels.shape[1], xs.max() + margin)
        
        # Compute raw stress first
        w = solve_poisson(mask)
        stress = compute_stress(w, mask)
        
        # Compute neck_score
        neck_score, z, stats, debug_info = compute_neck_score_z(stress, mask, sigma_smooth=2)
        
        peak_to_mean = stats.get('peak_to_mean', 0)
        max_z = stats.get('max_z', 0)
        
        # Log transform for visualization
        log_neck_score = np.zeros_like(neck_score)
        log_neck_score[mask] = np.log1p(neck_score[mask])
        
        # Hot pixels based on neck_score z-scores
        hot_mask = (z > cut_max_z) & mask
        
        ax.imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
        ax.imshow(log_neck_score[y0:y1, x0:x1], cmap='hot', alpha=0.7)
        
        # Show hot pixels in green
        if hot_mask.sum() > 0:
            hot_vis = np.zeros((y1-y0, x1-x0, 4))
            hot_vis[hot_mask[y0:y1, x0:x1], :] = [0, 1, 0, 0.6]
            ax.imshow(hot_vis)
        
        # Show max neck_score point
        neck_score_masked = neck_score.copy()
        neck_score_masked[~mask] = 0
        if neck_score_masked.max() > 0:
            max_idx = np.argmax(neck_score_masked)
            max_y, max_x = np.unravel_index(max_idx, neck_score.shape)
            ax.plot(max_x - x0, max_y - y0, 'y*', markersize=12)
        
        should_cut = (peak_to_mean > cut_peak_to_mean) and (max_z > cut_max_z)
        marker = " ***" if should_cut else ""
        ax.set_title(f'R{region_id} (n={mask.sum()})\np/m={peak_to_mean:.1f}, z={max_z:.1f}{marker}')
        ax.axis('off')
    
    for idx in range(len(region_ids), len(axes)):
        axes[idx].axis('off')
    
    plt.suptitle(f'Neck Score (edge artifacts suppressed) | Thresholds: p/m>{cut_peak_to_mean}, z>{cut_max_z}', y=1.02)
    plt.tight_layout()
    plt.show()


