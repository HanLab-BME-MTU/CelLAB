"""
CellADE plotter — pipeline overview and final results comparison.
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage.color import label2rgb
from skimage.measure import regionprops

def plot_pipeline_steps(image, gt_labels, pipeline_data, figsize=(24, 12)):
    """
    Visualize all steps of the segmentation pipeline.
    
    Parameters:
        image: Original input image
        gt_labels: Ground truth labels
        pipeline_data: Dictionary containing all intermediate results:
            - img_enh: CLAHE enhanced image
            - fg_mask_raw: Raw foreground mask from FCM
            - fg_mask: Foreground mask after hole filling
            - seeds: Detected seed points
            - labels_initial: Initial segmentation (after radial expansion)
            - labels_merged: After boundary-based merging
            - labels_filed: After morphological filing
            - labels_smoothed: After FFT smoothing
            - labels_honeycomb: After honeycomb merging
            - labels_cleaned: After fragment removal
            - labels_split: Final result after splitting
            - metrics: Dictionary of metrics for each stage
    """
    from skimage.color import label2rgb
    
    # Extract data
    img_enh = pipeline_data.get('img_enh')
    fg_mask_raw = pipeline_data.get('fg_mask_raw')
    fg_mask = pipeline_data.get('fg_mask')
    seeds = pipeline_data.get('seeds')
    labels_initial = pipeline_data.get('labels_initial')
    labels_merged = pipeline_data.get('labels_merged')
    labels_filed = pipeline_data.get('labels_filed')
    labels_smoothed = pipeline_data.get('labels_smoothed')
    labels_honeycomb = pipeline_data.get('labels_honeycomb')
    labels_cleaned = pipeline_data.get('labels_cleaned')
    labels_split = pipeline_data.get('labels_split')
    metrics = pipeline_data.get('metrics', {})
    
    # Create figure with 2 rows, 7 columns
    fig, axes = plt.subplots(2, 7, figsize=figsize)
    
    # Row 1: Early stages (image processing and initial segmentation)
    # Panel 1: Original image
    axes[0, 0].imshow(image, cmap='gray')
    axes[0, 0].set_title('1. Original Image')
    axes[0, 0].axis('off')
    
    # Panel 2: CLAHE enhanced
    if img_enh is not None:
        axes[0, 1].imshow(img_enh, cmap='gray')
        axes[0, 1].set_title('2. CLAHE Enhanced')
    axes[0, 1].axis('off')
    
    # Panel 3: FCM foreground mask (raw)
    if fg_mask_raw is not None:
        axes[0, 2].imshow(fg_mask_raw, cmap='gray')
        axes[0, 2].set_title(f'3. FCM Raw\n({fg_mask_raw.sum()} px)')
    elif fg_mask is not None:
        axes[0, 2].imshow(fg_mask, cmap='gray')
        axes[0, 2].set_title(f'3. FCM Foreground')
    axes[0, 2].axis('off')
    
    # Panel 4: FCM foreground mask (holes filled)
    if fg_mask is not None:
        axes[0, 3].imshow(fg_mask, cmap='gray')
        filled_px = fg_mask.sum() - (fg_mask_raw.sum() if fg_mask_raw is not None else fg_mask.sum())
        axes[0, 3].set_title(f'4. Holes Filled\n(+{filled_px} px)')
    axes[0, 3].axis('off')
    
    # Panel 5: Seeds detected
    if seeds is not None and img_enh is not None:
        axes[0, 4].imshow(img_enh, cmap='gray')
        if len(seeds) > 0:
            axes[0, 4].scatter(seeds[:, 1], seeds[:, 0], c='red', s=20, marker='x')
        axes[0, 4].set_title(f'5. Seeds: {len(seeds) if seeds is not None else 0}')
    axes[0, 4].axis('off')
    
    # Panel 6: Initial segmentation (radial expansion)
    if labels_initial is not None:
        m = metrics.get('initial', {})
        axes[0, 5].imshow(label2rgb(labels_initial, bg_label=0))
        axes[0, 5].set_title(f'6. Initial: {labels_initial.max()} reg\nF1={m.get("F1", 0):.3f}')
    axes[0, 5].axis('off')
    
    # Panel 7: After merge
    if labels_merged is not None:
        m = metrics.get('merged', {})
        axes[0, 6].imshow(label2rgb(labels_merged, bg_label=0))
        axes[0, 6].set_title(f'7. Merged: {labels_merged.max()} reg\nF1={m.get("F1", 0):.3f}')
    axes[0, 6].axis('off')
    
    # Row 2: Later stages (smoothing, honeycomb, cleanup, split)
    # Panel 8: After filing
    if labels_filed is not None:
        m = metrics.get('filed', {})
        axes[1, 0].imshow(label2rgb(labels_filed, bg_label=0))
        axes[1, 0].set_title(f'8. Filed: {labels_filed.max()} reg\nF1={m.get("F1", 0):.3f}')
    axes[1, 0].axis('off')
    
    # Panel 9: After FFT smoothing
    if labels_smoothed is not None:
        m = metrics.get('smoothed', {})
        axes[1, 1].imshow(label2rgb(labels_smoothed, bg_label=0))
        axes[1, 1].set_title(f'9. Smoothed: {labels_smoothed.max()} reg\nF1={m.get("F1", 0):.3f}')
    axes[1, 1].axis('off')
    
    # Panel 10: After honeycomb
    if labels_honeycomb is not None:
        m = metrics.get('honeycomb', {})
        axes[1, 2].imshow(label2rgb(labels_honeycomb, bg_label=0))
        axes[1, 2].set_title(f'10. Honeycomb: {labels_honeycomb.max()} reg\nF1={m.get("F1", 0):.3f}')
    axes[1, 2].axis('off')
    
    # Panel 11: After cleanup
    if labels_cleaned is not None:
        m = metrics.get('cleaned', {})
        axes[1, 3].imshow(label2rgb(labels_cleaned, bg_label=0))
        axes[1, 3].set_title(f'11. Cleaned: {labels_cleaned.max()} reg\nF1={m.get("F1", 0):.3f}')
    axes[1, 3].axis('off')
    
    # Panel 12: After split (final)
    if labels_split is not None:
        m = metrics.get('split', {})
        axes[1, 4].imshow(label2rgb(labels_split, bg_label=0))
        axes[1, 4].set_title(f'12. Final: {labels_split.max()} reg\nF1={m.get("F1", 0):.3f}')
    axes[1, 4].axis('off')
    
    # Panel 13: Ground truth
    axes[1, 5].imshow(label2rgb(gt_labels, bg_label=0))
    axes[1, 5].set_title(f'Ground Truth: {gt_labels.max()} cells')
    axes[1, 5].axis('off')
    
    # Panel 14: Final vs GT overlay
    if labels_split is not None:
        # Create overlay: GT boundaries in green, pred boundaries in red
        from skimage.segmentation import find_boundaries
        gt_boundaries = find_boundaries(gt_labels, mode='outer')
        pred_boundaries = find_boundaries(labels_split, mode='outer')
        
        overlay = np.stack([image, image, image], axis=-1)
        overlay = (overlay - overlay.min()) / (overlay.max() - overlay.min() + 1e-8)
        overlay[gt_boundaries] = [0, 1, 0]  # Green for GT
        overlay[pred_boundaries] = [1, 0, 0]  # Red for prediction
        
        axes[1, 6].imshow(overlay)
        axes[1, 6].set_title('Final vs GT\n(Red=Pred, Green=GT)')
    axes[1, 6].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return fig




def plot_results(image, labels_before, labels_merged, labels_smoothed, labels_split, gt_labels,
                 metrics_before, metrics_merged, metrics_smoothed, metrics_split, 
                 split_info=None, iteration_snapshots=None):
    """Plot before/after comparison with region numbers and split iteration frames."""
    
    # Calculate number of iterations to show
    n_iterations = len(iteration_snapshots) if iteration_snapshots else 0
    
    # Row 0: Original, Initial, After Merge, After Smooth
    # Row 1: Ground Truth, Final, Boundary comparisons
    # Row 2+: Split iterations (full frame views)
    
    n_iter_rows = (n_iterations + 3) // 4 if n_iterations > 0 else 0
    n_rows = 2 + n_iter_rows
    
    fig, axes = plt.subplots(n_rows, 4, figsize=(20, 5 * n_rows))
    
    # Ensure axes is 2D
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    # ===== Row 0: Main pipeline stages =====
    axes[0, 0].imshow(image, cmap='gray')
    axes[0, 0].set_title('Original Image')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(label2rgb(labels_before, bg_label=0))
    props = regionprops(labels_before)
    for p in props:
        cy, cx = p.centroid
        axes[0, 1].text(cx, cy, str(p.label), color='white', fontsize=6, 
                       ha='center', va='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.1', facecolor='black', alpha=0.7))
    axes[0, 1].set_title(f'Initial: {labels_before.max()} regions\nF1={metrics_before["F1"]:.3f}')
    axes[0, 1].axis('off')
    
    axes[0, 2].imshow(label2rgb(labels_merged, bg_label=0))
    props = regionprops(labels_merged)
    for p in props:
        cy, cx = p.centroid
        axes[0, 2].text(cx, cy, str(p.label), color='white', fontsize=6, 
                       ha='center', va='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.1', facecolor='black', alpha=0.7))
    axes[0, 2].set_title(f'After Merge: {labels_merged.max()} regions\nF1={metrics_merged["F1"]:.3f}')
    axes[0, 2].axis('off')
    
    axes[0, 3].imshow(label2rgb(labels_smoothed, bg_label=0))
    props = regionprops(labels_smoothed)
    for p in props:
        cy, cx = p.centroid
        axes[0, 3].text(cx, cy, str(p.label), color='white', fontsize=6, 
                       ha='center', va='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.1', facecolor='black', alpha=0.7))
    axes[0, 3].set_title(f'After Smooth: {labels_smoothed.max()} regions\nF1={metrics_smoothed["F1"]:.3f}')
    axes[0, 3].axis('off')
    
    # ===== Row 1: Ground truth, Final result, Boundary comparisons =====
    axes[1, 0].imshow(label2rgb(gt_labels, bg_label=0))
    props = regionprops(gt_labels)
    for p in props:
        cy, cx = p.centroid
        axes[1, 0].text(cx, cy, str(p.label), color='white', fontsize=6, 
                       ha='center', va='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.1', facecolor='black', alpha=0.7))
    axes[1, 0].set_title(f'Ground Truth: {gt_labels.max()} cells')
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(label2rgb(labels_split, bg_label=0))
    props = regionprops(labels_split)
    for p in props:
        cy, cx = p.centroid
        axes[1, 1].text(cx, cy, str(p.label), color='white', fontsize=6, 
                       ha='center', va='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.1', facecolor='black', alpha=0.7))
    axes[1, 1].set_title(f'Final (After Split): {labels_split.max()} regions\nF1={metrics_split["F1"]:.3f}')
    axes[1, 1].axis('off')
    
    # Boundary comparisons: Smoothed vs GT, Final vs GT
    for ax_idx, (lbls, title) in enumerate([(labels_smoothed, 'Smoothed vs GT'), 
                                             (labels_split, 'Final vs GT')]):
        pred_fg = lbls > 0
        gt_fg = gt_labels > 0
        pred_bounds = pred_fg ^ binary_erosion(pred_fg)
        gt_bounds = gt_fg ^ binary_erosion(gt_fg)
        
        axes[1, ax_idx + 2].imshow(image, cmap='gray')
        axes[1, ax_idx + 2].imshow(gt_bounds, cmap='Greens', alpha=0.5)
        axes[1, ax_idx + 2].imshow(pred_bounds, cmap='Reds', alpha=0.5)
        axes[1, ax_idx + 2].set_title(f'{title}\nGreen=GT, Red=Pred')
        axes[1, ax_idx + 2].axis('off')
    
    # ===== Row 2+: Split iteration snapshots (full frame) =====
    if iteration_snapshots and n_iterations > 0:
        for idx, snapshot in enumerate(iteration_snapshots):
            row = 2 + idx // 4
            col = idx % 4
            
            if row >= n_rows:
                break
            
            ax = axes[row, col]
            iter_labels = snapshot['labels']
            n_regions = snapshot['n_regions']
            n_splits = snapshot['n_splits']
            description = snapshot['description']
            iteration = snapshot['iteration']
            
            ax.imshow(label2rgb(iter_labels, bg_label=0))
            
            # Add region labels
            props = regionprops(iter_labels)
            for p in props:
                cy, cx = p.centroid
                ax.text(cx, cy, str(p.label), color='white', fontsize=5, 
                       ha='center', va='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.1', facecolor='black', alpha=0.6))
            
            if iteration == 0:
                ax.set_title(f'Iter 0: Before Splits\n{n_regions} regions')
            else:
                ax.set_title(f'Iter {iteration}: {n_splits} splits\n{n_regions} regions')
            ax.axis('off')
        
        # Clear unused axes
        for idx in range(n_iterations, n_iter_rows * 4):
            row = 2 + idx // 4
            col = idx % 4
            if row < n_rows:
                axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.show()


