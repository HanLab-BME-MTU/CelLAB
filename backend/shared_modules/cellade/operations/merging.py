"""
CellADE merging — curvature-based merge, honeycomb merge, fragment removal.
"""

import numpy as np
from skimage.measure import label as relabel, regionprops
from scipy.ndimage import binary_dilation
from scipy.spatial import ConvexHull

from ..utils import find_neighbors
from .curvature import get_ordered_boundary, compute_curvature, analyze_region_boundary

def find_merge_candidates(labels, region_analyses, neighbors, shared_boundaries,
                          ratio_threshold=0.8,
                          absolute_curv_threshold=0.015,
                          persistence_min_length=10,
                          persistence_curv_threshold=0.02,
                          max_ellipticity=2.5,
                          max_post_merge_aspect=3.0,
                          verbose=False):
    """
    Find pairs of regions that should be merged using RAW curvature.
    
    Added safeguards:
    - Don't merge if either body is already very elliptical
    - Don't merge if the result would create a neck/valley (high aspect ratio)
    """
    merge_pairs = []
    checked_pairs = set()
    
    for region_id, neighbor_set in neighbors.items():
        if region_analyses.get(region_id) is None:
            continue
            
        for neighbor_id in neighbor_set:
            pair = (min(region_id, neighbor_id), max(region_id, neighbor_id))
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)
            
            if region_analyses.get(neighbor_id) is None:
                continue
            
            shared_pixels = shared_boundaries.get(pair, [])
            if len(shared_pixels) < 3:
                continue
            
            analysis1 = region_analyses[region_id]
            analysis2 = region_analyses[neighbor_id]
            
            # === SAFEGUARD 1: Check pre-merge ellipticity ===
            # Don't merge if either body is already very elliptical
            mask1 = (labels == region_id)
            mask2 = (labels == neighbor_id)
            
            def compute_ellipticity(mask):
                """Compute aspect ratio (ellipticity) of a mask using PCA."""
                ys, xs = np.where(mask)
                if len(ys) < 3:
                    return 1.0
                coords = np.column_stack([ys - ys.mean(), xs - xs.mean()])
                cov = np.cov(coords.T)
                eigenvalues = np.linalg.eigvalsh(cov)
                eigenvalues = np.sort(eigenvalues)[::-1]
                if eigenvalues[1] > 1e-6:
                    return np.sqrt(eigenvalues[0] / eigenvalues[1])
                return float('inf')
            
            ellip1 = compute_ellipticity(mask1)
            ellip2 = compute_ellipticity(mask2)
            
            if ellip1 > max_ellipticity or ellip2 > max_ellipticity:
                # One of the bodies is already very elongated - don't merge
                if verbose:
                    print(f"    Merge BLOCKED {pair}: pre-merge ellipticity too high ({ellip1:.2f}, {ellip2:.2f}) > {max_ellipticity}")
                continue
            
            # === SAFEGUARD 2: Check post-merge aspect ratio ===
            # Predict if merged body would have a neck (high aspect ratio)
            combined_mask = mask1 | mask2
            post_merge_ellip = compute_ellipticity(combined_mask)
            
            if post_merge_ellip > max_post_merge_aspect:
                # Merged body would be too elongated (likely has a neck)
                if verbose:
                    print(f"    Merge BLOCKED {pair}: post-merge ellipticity too high ({post_merge_ellip:.2f}) > {max_post_merge_aspect}")
                continue
            
            contour1 = analysis1['contour']
            contour2 = analysis2['contour']
            curv1 = analysis1['curvature_raw']
            curv2 = analysis2['curvature_raw']
            
            near_shared_1 = []
            near_shared_2 = []
            
            for i, (y, x) in enumerate(contour1):
                for sy, sx in shared_pixels:
                    if abs(y - sy) <= 2 and abs(x - sx) <= 2:
                        near_shared_1.append(i)
                        break
            
            for i, (y, x) in enumerate(contour2):
                for sy, sx in shared_pixels:
                    if abs(y - sy) <= 2 and abs(x - sx) <= 2:
                        near_shared_2.append(i)
                        break
            
            if len(near_shared_1) < 2 or len(near_shared_2) < 2:
                continue
            
            curv_at_shared_1 = np.abs(curv1[near_shared_1])
            curv_at_shared_2 = np.abs(curv2[near_shared_2])
            
            # Use mean instead of median - median can be 0 for shapes with mostly straight edges
            # Also compute on non-zero values to avoid dilution by straight edges
            abs_curv1 = np.abs(curv1)
            abs_curv2 = np.abs(curv2)
            
            # For overall curvature, use mean of all values (captures corners)
            mean_curv_1 = np.mean(abs_curv1)
            mean_curv_2 = np.mean(abs_curv2)
            
            # For shared boundary curvature, use mean
            mean_at_shared_1 = np.mean(curv_at_shared_1)
            mean_at_shared_2 = np.mean(curv_at_shared_2)
            
            # Ratio: is the shared boundary flatter than average?
            ratio_1 = mean_at_shared_1 / (mean_curv_1 + 1e-10)
            ratio_2 = mean_at_shared_2 / (mean_curv_2 + 1e-10)
            ratio_pass = (ratio_1 < ratio_threshold) and (ratio_2 < ratio_threshold)
            
            # Absolute: is the shared boundary curvature below threshold?
            abs_curv_1 = mean_at_shared_1
            abs_curv_2 = mean_at_shared_2
            absolute_pass = (abs_curv_1 < absolute_curv_threshold) and (abs_curv_2 < absolute_curv_threshold)
            
            # For debug, also store the overall means
            median_curv_1 = mean_curv_1  # renamed for compatibility with debug output
            median_curv_2 = mean_curv_2
            
            def find_max_persistent_length(indices, curvatures, threshold):
                if len(indices) == 0:
                    return 0
                sorted_indices = sorted(indices)
                max_length = 0
                current_length = 0
                prev_idx = None
                for idx in sorted_indices:
                    if abs(curvatures[idx]) < threshold:
                        if prev_idx is None or idx == prev_idx + 1:
                            current_length += 1
                        else:
                            current_length = 1
                        max_length = max(max_length, current_length)
                        prev_idx = idx
                    else:
                        current_length = 0
                        prev_idx = None
                return max_length
            
            persist_len_1 = find_max_persistent_length(near_shared_1, curv1, persistence_curv_threshold)
            persist_len_2 = find_max_persistent_length(near_shared_2, curv2, persistence_curv_threshold)
            persistence_pass = (persist_len_1 >= persistence_min_length) and (persist_len_2 >= persistence_min_length)
            
            # Debug: print curvature stats
            if verbose:
                print(f"    Checking {pair}:")
                print(f"      Curvature stats region {region_id}: median_abs={median_curv_1:.4f}, at_shared={abs_curv_1:.4f}, ratio={ratio_1:.2f}")
                print(f"      Curvature stats region {neighbor_id}: median_abs={median_curv_2:.4f}, at_shared={abs_curv_2:.4f}, ratio={ratio_2:.2f}")
                print(f"      Thresholds: ratio<{ratio_threshold}, abs_curv<{absolute_curv_threshold}")
                print(f"      Pass: ratio={ratio_pass}, absolute={absolute_pass}, persistence={persistence_pass}")
            
            if ratio_pass or absolute_pass or persistence_pass:
                reasons = []
                if ratio_pass:
                    reasons.append(f"ratio({ratio_1:.2f},{ratio_2:.2f})")
                if absolute_pass:
                    reasons.append(f"abs_curv({abs_curv_1:.4f},{abs_curv_2:.4f})")
                if persistence_pass:
                    reasons.append(f"persist({persist_len_1},{persist_len_2})")
                
                # Debug: show ellipticity info
                if verbose:
                    print(f"    Merge candidate: {pair}, reasons: {', '.join(reasons)}")
                    print(f"      Pre-merge ellipticity: region {region_id}={ellip1:.2f}, region {neighbor_id}={ellip2:.2f}")
                    print(f"      Post-merge ellipticity: {post_merge_ellip:.2f}")
                    print(f"      Shared boundary: {len(shared_pixels)} pixels, near_shared: {len(near_shared_1)}, {len(near_shared_2)}")
                
                merge_pairs.append(pair)
    
    return merge_pairs


def apply_merges(labels, merge_pairs):
    """Apply merge operations using union-find."""
    if not merge_pairs:
        return labels.copy()
    
    parent = {}
    
    def find(x):
        if x not in parent:
            parent[x] = x
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
    
    for id1, id2 in merge_pairs:
        union(id1, id2)
    
    new_labels = labels.copy()
    region_ids = set(np.unique(labels)) - {0}
    id_map = {}
    
    for rid in region_ids:
        root = find(rid)
        if root not in id_map:
            id_map[root] = len(id_map) + 1
    
    for rid in region_ids:
        root = find(rid)
        new_id = id_map[root]
        new_labels[labels == rid] = new_id
    
    new_labels, _ = relabel(new_labels, return_num=True)
    return new_labels


def honeycomb_merge(labels, params, debug_plot=False):
    """
    Merge clusters of fragmented regions (honeycomb pattern).
    
    Algorithm:
    1. Build adjacency graph of ALL regions
    2. Find connected components (clusters)
    3. For each cluster with 2+ regions:
       - If total area is within reasonable cell size → MERGE (union of all region pixels)
    
    Parameters:
        labels: Label array
        params: Dictionary containing:
            - use_honeycomb_merging: Enable/disable (default True)
            - honeycomb_small_threshold: Fraction of median area to be "small" (default 0.5)
            - honeycomb_min_merged_size: Min merged size as fraction of median (default 0.3)
            - honeycomb_max_merged_size: Max merged size as fraction of median (default 3.0)
            - honeycomb_adjacency_radius: Dilation radius for adjacency (default 5)
            - verbose_honeycomb: Verbose output (default False)
        debug_plot: Whether to show debug visualization
    
    Returns:
        merged_labels: Label array with honeycomb clusters merged
    """
    from skimage.morphology import disk, binary_dilation
    import matplotlib.pyplot as plt
    
    use_honeycomb = params.get('use_honeycomb_merging', True)
    small_threshold_frac = params.get('honeycomb_small_threshold', 0.5)
    min_merged_frac = params.get('honeycomb_min_merged_size', 0.3)
    max_merged_frac = params.get('honeycomb_max_merged_size', 3.0)
    adjacency_radius = params.get('honeycomb_adjacency_radius', 5)
    verbose = params.get('verbose_honeycomb', False)
    
    if not use_honeycomb:
        return labels.copy()
    
    region_ids = [rid for rid in np.unique(labels) if rid > 0]
    
    if len(region_ids) < 2:
        return labels.copy()
    
    # Compute areas and centroids for all regions
    areas = {}
    centroids = {}
    for rid in region_ids:
        mask = (labels == rid)
        areas[rid] = mask.sum()
        ys, xs = np.where(mask)
        centroids[rid] = (ys.mean(), xs.mean())
    
    median_area = np.median(list(areas.values()))
    
    # Define thresholds
    small_threshold = small_threshold_frac * median_area
    min_merged_size = min_merged_frac * median_area
    max_merged_size = max_merged_frac * median_area
    
    # Identify small vs large regions (for visualization)
    small_regions = set(rid for rid, area in areas.items() if area < small_threshold)
    large_regions = set(region_ids) - small_regions
    
    if verbose:
        print(f"    Honeycomb merging (adj_radius={adjacency_radius}, merge size: {min_merged_size:.0f}-{max_merged_size:.0f}px)...")
        print(f"      Median area: {median_area:.0f}, Small: {len(small_regions)}, Large: {len(large_regions)}")
    
    # Step 1: Build adjacency graph of ALL regions
    selem = disk(adjacency_radius)
    adjacency = {rid: set() for rid in region_ids}
    
    for rid in region_ids:
        mask = (labels == rid)
        dilated = binary_dilation(mask, selem)
        neighbor_labels = set(np.unique(labels[dilated & ~mask])) - {0, rid}
        adjacency[rid] = neighbor_labels
        # Make symmetric
        for neighbor in neighbor_labels:
            if neighbor in adjacency:
                adjacency[neighbor].add(rid)
    
    # Step 2: Find connected components (clusters) using BFS
    visited = set()
    all_clusters = []
    
    for start_rid in region_ids:
        if start_rid in visited:
            continue
        
        # BFS to find all connected regions
        cluster = []
        queue = [start_rid]
        
        while queue:
            rid = queue.pop(0)
            if rid in visited:
                continue
            visited.add(rid)
            cluster.append(rid)
            
            for neighbor in adjacency[rid]:
                if neighbor not in visited:
                    queue.append(neighbor)
        
        all_clusters.append(cluster)
    
    if verbose:
        print(f"      Found {len(all_clusters)} connected components")
    
    # Step 3: Analyze each cluster - merge if 2+ regions and reasonable size
    merge_operations = []
    cluster_info = []  # For visualization
    
    for cluster in all_clusters:
        n_regions = len(cluster)
        
        # Skip single-region clusters (nothing to merge)
        if n_regions < 2:
            continue
        
        # Compute total area (sum of all region pixels, no hull filling)
        cluster_areas = [areas[rid] for rid in cluster]
        sum_areas = sum(cluster_areas)
        
        # Count small/large for info
        small_in_cluster = set(cluster) & small_regions
        large_in_cluster = set(cluster) & large_regions
        
        info = {
            'cluster': cluster,
            'n_small': len(small_in_cluster),
            'n_large': len(large_in_cluster),
            'sum_areas': sum_areas,
        }
        cluster_info.append(info)
        
        # Check size constraints (use sum of areas, not hull)
        if min_merged_size <= sum_areas <= max_merged_size:
            merge_operations.append(cluster)
            info['merge'] = True
            if verbose:
                print(f"      Cluster: {n_regions} regions ({len(small_in_cluster)} small, {len(large_in_cluster)} large)")
                print(f"        Areas: {sorted(cluster_areas)}, sum={sum_areas} → MERGE")
        else:
            reason = "too small" if sum_areas < min_merged_size else "too large"
            info['merge'] = False
            if verbose:
                print(f"      Cluster: {n_regions} regions ({len(small_in_cluster)} small, {len(large_in_cluster)} large)")
                print(f"        Areas: {sorted(cluster_areas)}, sum={sum_areas} → SKIP ({reason})")
    
    # Debug visualization
    if debug_plot:
        n_panels = 3
        fig, axes = plt.subplots(1, n_panels, figsize=(5 * n_panels, 5))
        
        # Panel 1: All regions colored by small/large
        ax = axes[0]
        display = np.zeros((*labels.shape, 3))
        for rid in region_ids:
            mask = labels == rid
            if rid in small_regions:
                display[mask] = [1, 0.3, 0.3]  # Red for small
            else:
                display[mask] = [0.3, 0.3, 1]  # Blue for large
        ax.imshow(display)
        ax.set_title(f'Small (red): {len(small_regions)}, Large (blue): {len(large_regions)}')
        for rid in region_ids:
            cy, cx = centroids[rid]
            ax.text(cx, cy, str(rid), fontsize=5, color='yellow', ha='center', va='center')
        ax.axis('off')
        
        # Panel 2: Connected components (each cluster different color)
        ax = axes[1]
        display2 = np.zeros((*labels.shape, 3))
        colors = plt.cm.tab20(np.linspace(0, 1, max(20, len(all_clusters))))
        for i, cluster in enumerate(all_clusters):
            color = colors[i % len(colors)][:3]
            for rid in cluster:
                mask = labels == rid
                display2[mask] = color
        ax.imshow(display2)
        ax.set_title(f'Connected components: {len(all_clusters)}')
        ax.axis('off')
        
        # Panel 3: Clusters to merge (valid ones highlighted)
        ax = axes[2]
        display3 = np.zeros((*labels.shape, 3))
        # Show all regions faintly
        for rid in region_ids:
            mask = labels == rid
            display3[mask] = [0.2, 0.2, 0.2]
        # Highlight clusters to merge
        colors = plt.cm.Set1(np.linspace(0, 1, max(9, len(cluster_info))))
        valid_count = 0
        for i, info in enumerate(cluster_info):
            if info.get('merge', False):
                color = colors[i % len(colors)][:3]
                for rid in info['cluster']:
                    mask = labels == rid
                    display3[mask] = color
                valid_count += 1
        ax.imshow(display3)
        ax.set_title(f'Clusters to merge: {valid_count}')
        ax.axis('off')
        
        plt.tight_layout()
        plt.show()
    
    if not merge_operations:
        if verbose:
            print(f"      No clusters to merge")
        return labels.copy()
    
    # Apply merges - just assign all regions in cluster to same label (no filling)
    new_labels = labels.copy()
    next_label = labels.max() + 1
    
    for cluster in merge_operations:
        # Assign all regions in cluster to the same new label
        for rid in cluster:
            new_labels[labels == rid] = next_label
        next_label += 1
    
    # Relabel to have consecutive IDs
    new_labels, _ = relabel(new_labels, return_num=True)
    
    n_merged = sum(len(c) for c in merge_operations)
    n_new = len(merge_operations)
    if verbose:
        print(f"      Merged {n_merged} regions into {n_new} new cells")
    
    return new_labels


def remove_small_fragments(labels, params):
    """
    Remove extremely small regions using 4-sigma rule.
    
    These are likely noise/artifacts - scattered fragments that didn't get
    merged in honeycomb merging.
    
    Parameters:
        labels: Label array
        params: Dictionary containing:
            - use_fragment_removal: Enable/disable (default True)
            - fragment_min_size: Absolute minimum size in pixels (default 50)
            - verbose_cleanup: Verbose output (default False)
    
    Returns:
        cleaned_labels: Label array with small fragments removed
    """
    use_removal = params.get('use_fragment_removal', True)
    min_size_floor = params.get('fragment_min_size', 50)
    verbose = params.get('verbose_cleanup', False)
    
    if not use_removal:
        return labels.copy()
    
    region_ids = [rid for rid in np.unique(labels) if rid > 0]
    
    if len(region_ids) <= 1:
        return labels.copy()
    
    # Compute sizes
    sizes = np.array([np.sum(labels == rid) for rid in region_ids])
    mean_size = sizes.mean()
    std_size = sizes.std()
    
    # Threshold: mean - 4*std, with floor
    min_size_4sigma = max(min_size_floor, mean_size - 4 * std_size)
    
    if verbose:
        print(f"    Fragment removal (4σ rule: mean={mean_size:.0f}, std={std_size:.0f}, threshold={min_size_4sigma:.0f}px)...")
    
    # Find and remove tiny regions
    new_labels = labels.copy()
    removed_info = []
    
    for rid, size in zip(region_ids, sizes):
        if size < min_size_4sigma:
            new_labels[labels == rid] = 0
            removed_info.append((rid, size))
    
    if verbose:
        if removed_info:
            print(f"      Removed {len(removed_info)} tiny fragments: {[(rid, sz) for rid, sz in removed_info]}")
        else:
            print(f"      No fragments removed (all regions >= {min_size_4sigma:.0f}px)")
    
    # Relabel
    new_labels, _ = relabel(new_labels, return_num=True)
    
    return new_labels


