"""
CellADE plotter — single region deep debug analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage.color import label2rgb
from skimage.measure import regionprops

from ..operations.stress import solve_poisson, compute_stress, compute_z_scores, compute_neck_score, compute_neck_score_z
from ..operations.splitting import find_neck_clusters, split_region_cluster_based

def analyze_single_region(image, labels, region_id, params, debug=True):
    """Analyze and plot stress field for a single region with chunk tracking split."""
    mask = (labels == region_id)
    region_size = mask.sum()
    
    if region_size < 50:
        print(f"Region {region_id} too small ({region_size} pixels)")
        return None
    
    print(f"\n{'='*60}")
    print(f"Analyzing region {region_id} (size={region_size})...")
    print(f"{'='*60}")
    
    # Initial stress analysis
    w = solve_poisson(mask)
    stress = compute_stress(w, mask)
    stress_smooth = gaussian(stress, sigma=2)
    z, stats = compute_z_scores(stress_smooth, mask)
    
    print(f"  peak/mean = {stats['peak_to_mean']:.2f}")
    print(f"  max_z = {stats['max_z']:.2f}")
    
    # Try cluster-based split with debug
    use_cluster_method = params.get('use_cluster_detection', True)
    if use_cluster_method:
        print(f"\n  Starting cluster-based split...")
        split_labeled, n_parts, debug_info = split_region_cluster_based(
            mask, params, debug=debug, image=image
        )
    else:
        print(f"\n  Starting chunk tracking split...")
        split_labeled, n_parts, debug_info = split_region_chunk_tracking(
            mask, params, debug=debug, image=image
        )
    print(f"\n  Final result: {n_parts} parts")
    
    # ===== VISUALIZATION: Show stress fields at each iteration =====
    iterations = debug_info.get('iterations', [])
    n_iters = len(iterations)
    
    if n_iters > 0:
        # Get bounding box for the region
        ys, xs = np.where(mask)
        margin = 15
        y0, y1 = max(0, ys.min() - margin), min(mask.shape[0], ys.max() + margin)
        x0, x1 = max(0, xs.min() - margin), min(mask.shape[1], xs.max() + margin)
        
        # Create figure with rows for each iteration
        # Each row: [Working Mask, Stress Field, Neck Score, Hot Chunks]
        fig, axes = plt.subplots(n_iters, 4, figsize=(20, 5 * n_iters))
        if n_iters == 1:
            axes = axes.reshape(1, -1)
        
        for iter_idx, iter_info in enumerate(iterations):
            iter_num = iter_info.get('iteration', iter_idx + 1)
            working_mask = iter_info.get('working_mask')
            stress_field = iter_info.get('stress')
            neck_score = iter_info.get('neck_score')
            z_scores = iter_info.get('z_scores')
            hot_mask = iter_info.get('hot_mask')
            chunks = iter_info.get('chunks', [])
            iter_stats = iter_info.get('stats', {})
            edge_debug = iter_info.get('edge_debug')
            
            row = axes[iter_idx]
            
            # Panel 1: Working mask with image
            row[0].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.5)
            if working_mask is not None:
                mask_vis = np.zeros((y1-y0, x1-x0, 4))
                mask_vis[working_mask[y0:y1, x0:x1], :] = [0, 0.5, 1, 0.4]
                row[0].imshow(mask_vis)
                # Show boundary
                boundary = working_mask ^ binary_erosion(working_mask)
                bound_vis = np.zeros((y1-y0, x1-x0, 4))
                bound_vis[boundary[y0:y1, x0:x1], :] = [0, 0, 1, 0.8]
                row[0].imshow(bound_vis)
            row[0].set_title(f'Iter {iter_num}: Working Mask\n({working_mask.sum() if working_mask is not None else 0} px)')
            row[0].axis('off')
            
            # Panel 2: Stress field (log scale for better visualization)
            if stress_field is not None:
                stress_display = np.zeros_like(stress_field)
                if working_mask is not None:
                    stress_display[working_mask] = np.log1p(stress_field[working_mask])
                im = row[1].imshow(stress_display[y0:y1, x0:x1], cmap='hot')
                plt.colorbar(im, ax=row[1], fraction=0.046)
            row[1].set_title(f'Raw Stress (log)')
            row[1].axis('off')
            
            # Panel 3: Neck Score (or Z-scores if neck_score not available)
            if neck_score is not None:
                es_display = np.zeros_like(neck_score)
                if working_mask is not None:
                    es_display[working_mask] = np.log1p(neck_score[working_mask])
                im = row[2].imshow(es_display[y0:y1, x0:x1], cmap='hot')
                plt.colorbar(im, ax=row[2], fraction=0.046)
                pm = iter_stats.get('peak_to_mean', 0)
                mz = iter_stats.get('max_z', 0)
                row[2].set_title(f'Neck Score (log)\npm={pm:.2f}, mz={mz:.2f}')
            elif z_scores is not None:
                z_display = np.zeros_like(z_scores)
                if working_mask is not None:
                    z_display[working_mask] = z_scores[working_mask]
                im = row[2].imshow(z_display[y0:y1, x0:x1], cmap='hot', vmin=0, vmax=5)
                plt.colorbar(im, ax=row[2], fraction=0.046)
                pm = iter_stats.get('peak_to_mean', 0)
                mz = iter_stats.get('max_z', 0)
                row[2].set_title(f'Z-Scores\npm={pm:.2f}, mz={mz:.2f}')
            row[2].axis('off')
            
            # Panel 4: Hot chunks
            cut_max_z = params.get('cut_max_z', 2.5)
            row[3].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.5)
            if working_mask is not None:
                mask_vis = np.zeros((y1-y0, x1-x0, 4))
                mask_vis[working_mask[y0:y1, x0:x1], :] = [0.5, 0.5, 0.5, 0.3]
                row[3].imshow(mask_vis)
            
            if hot_mask is not None:
                hot_vis = np.zeros((y1-y0, x1-x0, 4))
                hot_vis[hot_mask[y0:y1, x0:x1], :] = [1, 0, 0, 0.6]
                row[3].imshow(hot_vis)
            
            # Mark chunk centroids
            for i, chunk in enumerate(chunks):
                cy, cx = chunk.get('centroid', (0, 0))
                row[3].plot(cx - x0, cy - y0, 'g*', markersize=12)
                row[3].annotate(f'{i+1}', (cx - x0 + 3, cy - y0), 
                               color='green', fontsize=10, fontweight='bold')
            
            row[3].set_title(f'Hot Chunks (z>{cut_max_z})\n{len(chunks)} chunks found')
            row[3].axis('off')
        
        plt.suptitle(f'Region {region_id}: Stress Analysis Iterations', fontsize=14, y=1.02)
        plt.tight_layout()
        plt.show()
        
        # ===== Additional plot: Cut lines and final result =====
        cut_lines = debug_info.get('cut_lines', [])
        
        fig2, axes2 = plt.subplots(1, 4, figsize=(20, 5))
        
        # Panel 1: Original mask
        axes2[0].imshow(image[y0:y1, x0:x1], cmap='gray')
        mask_vis = np.zeros((y1-y0, x1-x0, 4))
        mask_vis[mask[y0:y1, x0:x1], :] = [0, 0.5, 1, 0.4]
        axes2[0].imshow(mask_vis)
        axes2[0].set_title(f'Original Mask\n({mask.sum()} px)')
        axes2[0].axis('off')
        
        # Panel 2: All hot regions combined
        axes2[1].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.5)
        for iter_info in iterations:
            hot_mask = iter_info.get('hot_mask')
            if hot_mask is not None:
                iter_num = iter_info.get('iteration', 0)
                # Different colors for different iterations
                colors = [[1, 0, 0, 0.4], [0, 1, 0, 0.4], [0, 0, 1, 0.4]]
                color = colors[iter_num % len(colors)]
                hot_vis = np.zeros((y1-y0, x1-x0, 4))
                hot_vis[hot_mask[y0:y1, x0:x1], :] = color
                axes2[1].imshow(hot_vis)
        axes2[1].set_title(f'Hot Regions\n(Red=Iter1, Green=Iter2)')
        axes2[1].axis('off')
        
        # Panel 3: Cut lines
        axes2[2].imshow(image[y0:y1, x0:x1], cmap='gray')
        mask_vis = np.zeros((y1-y0, x1-x0, 4))
        mask_vis[mask[y0:y1, x0:x1], :] = [0, 0.5, 1, 0.3]
        axes2[2].imshow(mask_vis)
        
        for cut_info in cut_lines:
            cut_mask = cut_info.get('mask')
            if cut_mask is not None:
                cut_vis = np.zeros((y1-y0, x1-x0, 4))
                cut_vis[cut_mask[y0:y1, x0:x1], :] = [1, 1, 0, 0.9]
                axes2[2].imshow(cut_vis)
        axes2[2].set_title(f'Cut Lines\n({len(cut_lines)} cuts)')
        axes2[2].axis('off')
        
        # Panel 4: Final result
        axes2[3].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
        if n_parts > 1:
            axes2[3].imshow(split_labeled[y0:y1, x0:x1], cmap='nipy_spectral', alpha=0.7)
        else:
            mask_vis = np.zeros((y1-y0, x1-x0, 4))
            mask_vis[mask[y0:y1, x0:x1], :] = [0.5, 0.5, 0.5, 0.5]
            axes2[3].imshow(mask_vis)
        axes2[3].set_title(f'Final Result\n{n_parts} parts')
        axes2[3].axis('off')
        
        plt.suptitle(f'Region {region_id}: Split Result', fontsize=14)
        plt.tight_layout()
        plt.show()
    
    # ===== Cluster-Based Neck Detection =====
    use_cluster_detection = params.get('use_cluster_detection', True)
    if use_cluster_detection:
        print(f"\n  Running cluster-based neck detection...")
        
        # Compute neck score
        neck_score_field, z_neck, neck_stats, neck_debug = compute_neck_score_z(stress, mask, sigma_smooth=2)
        
        # Get concavity_factor for long cut validation
        concavity_factor = neck_debug.get('concavity_factor')
        
        # Detect clusters and find cut line
        cut_line, clusters, cluster_debug_info = detect_and_cut_necks(
            mask, neck_score_field, params, 
            concavity_factor=concavity_factor,
            debug=debug
        )
        
        print(f"\n  Cluster detection results:")
        print(f"    Clusters found: {len(clusters)}")
        print(f"    Valid cut line: {'YES' if cut_line is not None else 'NO'}")
        
        # Visualize cluster detection
        ys, xs = np.where(mask)
        margin = 15
        y0, y1 = max(0, ys.min() - margin), min(mask.shape[0], ys.max() + margin)
        x0, x1 = max(0, xs.min() - margin), min(mask.shape[1], xs.max() + margin)
        
        fig3, axes3 = plt.subplots(1, 5, figsize=(25, 5))
        
        # Panel 0: Neck score with hot pixels
        ax = axes3[0]
        ax.imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.5)
        ns_display = np.zeros_like(neck_score_field)
        ns_display[mask] = np.log1p(neck_score_field[mask])
        ax.imshow(ns_display[y0:y1, x0:x1], cmap='hot', alpha=0.6)
        
        # Show hot pixels
        hot_mask = cluster_debug_info['cluster_debug'].get('hot_mask')
        if hot_mask is not None and hot_mask.any():
            hot_vis = np.zeros((y1-y0, x1-x0, 4))
            hot_vis[hot_mask[y0:y1, x0:x1], :] = [0, 1, 0, 0.6]
            ax.imshow(hot_vis)
        ax.set_title(f'Neck Score + Hot Pixels\n(z > {params.get("cut_max_z", 2.5)})')
        ax.axis('off')
        
        # Panel 1: ALL RAW CLUSTERS (including rejected) - NEW
        ax = axes3[1]
        ax.imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.5)
        
        # Get all raw clusters from debug info
        all_raw_clusters = cluster_debug_info['cluster_debug'].get('all_raw_clusters', [])
        colors_valid = ['lime', 'cyan', 'yellow']
        colors_rejected = ['red', 'orange', 'magenta']
        
        n_valid = 0
        n_rejected = 0
        for raw_cluster in all_raw_clusters:
            seed_mask_c = raw_cluster.get('seed_mask')
            seed_centroid = raw_cluster.get('seed_centroid', (0, 0))
            status = raw_cluster.get('status', 'unknown')
            raw_id = raw_cluster.get('raw_id', 0)
            
            if status == 'valid':
                color = colors_valid[n_valid % len(colors_valid)]
                n_valid += 1
                marker = '*'
                label_prefix = 'V'
            else:
                color = colors_rejected[n_rejected % len(colors_rejected)]
                n_rejected += 1
                marker = 'x'
                label_prefix = 'R'
            
            # Show seed pixels
            if seed_mask_c is not None:
                seed_vis = np.zeros((y1-y0, x1-x0, 4))
                r, g, b = plt.cm.colors.to_rgb(color)
                seed_vis[seed_mask_c[y0:y1, x0:x1], :] = [r, g, b, 0.7]
                ax.imshow(seed_vis)
            
            # Show centroid with marker
            cy, cx = seed_centroid
            ax.plot(cx - x0, cy - y0, marker, color=color, markersize=12, markeredgecolor='white')
            
            # Build label with rejection reason if applicable
            seed_size = raw_cluster.get('seed_size', 0)
            rejection_reason = raw_cluster.get('rejection_reason', '')
            if status == 'valid':
                label = f'{label_prefix}{raw_id}\n({seed_size}px)'
            else:
                # Shorten rejection reason for display
                short_reason = rejection_reason.split('(')[0].strip() if rejection_reason else 'rejected'
                label = f'{label_prefix}{raw_id}\n{short_reason}'
            
            ax.text(cx - x0 + 3, cy - y0, label, color=color, fontsize=7, fontweight='bold')
        
        ax.set_title(f'All Raw Clusters\n({n_valid} valid, {n_rejected} rejected)')
        ax.axis('off')
        
        # Panel 2: Valid detected clusters (same as before, now shifted)
        ax = axes3[2]
        ax.imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.5)
        
        # Color each cluster differently
        colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta']
        for i, cluster in enumerate(clusters):
            color = colors[i % len(colors)]
            cy, cx = cluster['centroid']
            
            # Show cluster pixels
            cluster_vis = np.zeros((y1-y0, x1-x0, 4))
            cluster_mask = cluster['mask']
            r, g, b = plt.cm.colors.to_rgb(color)
            cluster_vis[cluster_mask[y0:y1, x0:x1], :] = [r, g, b, 0.6]
            ax.imshow(cluster_vis)
            
            # Show centroid
            ax.plot(cx - x0, cy - y0, '*', color=color, markersize=15, markeredgecolor='white')
            ax.text(cx - x0 + 3, cy - y0, f'C{i+1}\n({cluster["size"]:.1f})', 
                   color=color, fontsize=8, fontweight='bold')
        
        ax.set_title(f'Valid Clusters\n({len(clusters)} clusters)')
        ax.axis('off')
        
        # Panel 3: Cut line (or attempted cut line)
        ax = axes3[3]
        ax.imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.5)
        
        # Show mask
        mask_vis = np.zeros((y1-y0, x1-x0, 4))
        mask_vis[mask[y0:y1, x0:x1], :] = [0, 0.5, 1, 0.3]
        ax.imshow(mask_vis)
        
        # Get cut debug info (contains attempted cut even if rejected)
        cut_debug = cluster_debug_info.get('cut_debug', {})
        
        if cut_line is not None:
            # Valid cut line
            method = cut_line.get('method', 'two_cluster')
            
            if method == 'single_cluster_erosion':
                # Single cluster with erosion method
                cluster = cut_line['cluster']
                cy, cx = cluster['centroid']
                ax.plot(cx - x0, cy - y0, 'r*', markersize=15, label='Cluster centroid')
                
                # Show the cut region (eroded area)
                cut_mask = cut_line.get('cut_mask')
                if cut_mask is not None:
                    cut_vis = np.zeros((y1-y0, x1-x0, 4))
                    cut_vis[cut_mask[y0:y1, x0:x1], :] = [1, 1, 0, 0.7]  # Yellow
                    ax.imshow(cut_vis)
                
                erosion_level = cut_line.get('erosion_level', 0)
                title = f'Cut Region\n(cluster + {erosion_level} dilation)'
                
            elif method == 'single_cluster_regression':
                # Single cluster with regression (deprecated)
                cluster = cut_line['cluster']
                cy, cx = cluster['centroid']
                ax.plot(cx - x0, cy - y0, 'r*', markersize=15, label='Cluster centroid')
                
                # Show cut direction
                reg_info = cut_line.get('regression_info', {})
                cut_dir = reg_info.get('cut_direction', None)
                if cut_dir is not None:
                    # Draw cut direction arrow
                    arrow_len = 20
                    ax.arrow(cx - x0, cy - y0, 
                            cut_dir[1] * arrow_len, cut_dir[0] * arrow_len,
                            head_width=3, head_length=2, fc='cyan', ec='cyan', linewidth=2)
                
                title = f'Cut Line\n(single cluster regression)'
            else:
                # Two clusters
                cluster_A = cut_line.get('cluster_A')
                cluster_B = cut_line.get('cluster_B')
                
                if cluster_A is not None and cluster_B is not None:
                    cy_A, cx_A = cluster_A['centroid']
                    cy_B, cx_B = cluster_B['centroid']
                    
                    ax.plot(cx_A - x0, cy_A - y0, 'r*', markersize=15, label='Cluster A')
                    ax.plot(cx_B - x0, cy_B - y0, 'b*', markersize=15, label='Cluster B')
                
                # Show cut line
                line_y = cut_line['line_y']
                line_x = cut_line['line_x']
                ax.plot(line_x - x0, line_y - y0, 'y-', linewidth=3, label='Cut line')
                
                title = f'Cut Line\n(between top 2 clusters)'
            
            ax.set_title(title, color='green')
        else:
            # No valid cut - but show attempted cut if available
            reason = cut_debug.get('rejection_reason', 'unknown')
            
            # Try to show the attempted cut info
            if len(clusters) >= 1:
                # Show cluster centroids
                for i, cluster in enumerate(clusters[:2]):
                    cy, cx = cluster['centroid']
                    color = 'red' if i == 0 else 'blue'
                    ax.plot(cx - x0, cy - y0, '*', color=color, markersize=15)
                
                # For single cluster, show the cluster region
                if len(clusters) == 1:
                    cluster = clusters[0]
                    # Show cluster pixels that would be removed
                    cluster_vis = np.zeros((y1-y0, x1-x0, 4))
                    cluster_mask = cluster['mask']
                    cluster_vis[cluster_mask[y0:y1, x0:x1], :] = [1, 0.5, 0, 0.6]  # Orange
                    ax.imshow(cluster_vis)
                
                # For two clusters, draw line between them
                elif len(clusters) >= 2:
                    cy_A, cx_A = clusters[0]['centroid']
                    cy_B, cx_B = clusters[1]['centroid']
                    ax.plot([cx_A - x0, cx_B - x0], [cy_A - y0, cy_B - y0], 
                           'r--', linewidth=2, label='Attempted cut')
            
            ax.set_title(f'No Valid Cut\n({reason})', color='red')
        ax.axis('off')
        
        # Panel 4: Result after cut (from actual split_region_cluster_based result)
        ax = axes3[4]
        ax.imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.5)
        
        # Use split_labeled from actual split (includes pixel reassignment)
        if n_parts >= 2:
            ax.imshow(split_labeled[y0:y1, x0:x1], cmap='nipy_spectral', alpha=0.7)
            ax.set_title(f'Split Result\n({n_parts} parts, with reassignment)', color='green')
        else:
            mask_vis = np.zeros((y1-y0, x1-x0, 4))
            mask_vis[mask[y0:y1, x0:x1], :] = [0.5, 0.5, 0.5, 0.5]
            ax.imshow(mask_vis)
            ax.set_title('No Split' if cut_line is None else 'Split Failed', color='red')
        ax.axis('off')
        
        plt.suptitle(f'Region {region_id}: Cluster-Based Neck Detection', fontsize=14)
        plt.tight_layout()
        plt.show()
    
    return {
        'region_id': region_id,
        'mask': mask,
        'stats': stats,
        'n_parts': n_parts,
        'debug_info': debug_info,
    }


