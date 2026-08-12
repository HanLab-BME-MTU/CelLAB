"""
CellADE splitting — neck detection, cluster analysis, cut lines, chunk tracking.
"""

import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion, label as ndlabel
from skimage.measure import label as relabel, regionprops
from skimage.draw import line
from skimage.morphology import disk

from .stress import solve_poisson, compute_stress, compute_z_scores, compute_neck_score, compute_neck_score_z

def find_neck_clusters(neck_score, mask, z_threshold_high, min_cluster_size=5, 
                       cluster_radius=3, max_aspect_ratio=4.0, 
                       z_threshold_low_ratio=0.5, sigma_scale=0.15, debug=False,
                       exclusion_mask=None):
    """
    Find clusters of high neck_score pixels using soft membership weighting.
    
    Algorithm:
    1. Find seed pixels using high threshold (z > z_threshold_high)
    2. Form initial clusters from seeds (using radius-based grouping)
    3. Check aspect ratio on seeds - reject linear clusters
    4. Compute soft membership weights based on distance and z-score
    5. Use effective_size (sum of weights) for size thresholds
    6. Use thresholded weights (w > 0.5) for aspect ratio check
    
    Parameters:
        neck_score: Neck score field
        mask: Binary region mask  
        z_threshold_high: High z-score threshold for seed pixels
        min_cluster_size: Minimum effective cluster size (sum of soft weights)
        cluster_radius: Radius for grouping nearby seed pixels
        max_aspect_ratio: Maximum aspect ratio for valid cluster
        z_threshold_low_ratio: DEPRECATED - kept for API compatibility, not used
        sigma_scale: Spatial decay scale as fraction of sqrt(area), default 0.15
        debug: Print debug information
        exclusion_mask: Optional mask of areas to ignore (e.g., previous cut locations)
    
    Returns:
        clusters: List of cluster info dicts, sorted by prominence
        labeled_clusters: Label array of clusters
        debug_info: Dictionary with intermediate results
    """
    from scipy.ndimage import label as ndlabel, binary_dilation
    
    z_threshold_low = z_threshold_high * z_threshold_low_ratio
    
    # Compute z-scores for neck_score
    z = np.zeros_like(neck_score)
    vals = neck_score[mask]
    
    if len(vals) == 0 or vals.max() < 1e-10:
        return [], np.zeros_like(mask, dtype=int), {'hot_mask': np.zeros_like(mask, dtype=bool)}
    
    vals_positive = vals[vals > 0]
    if len(vals_positive) == 0:
        return [], np.zeros_like(mask, dtype=int), {'hot_mask': np.zeros_like(mask, dtype=bool)}
    
    vals_log = np.log1p(vals_positive)
    mean_log = vals_log.mean()
    std_log = vals_log.std()
    
    if std_log > 1e-10:
        positive_mask = mask & (neck_score > 0)
        neck_score_log = np.log1p(neck_score)
        z[positive_mask] = (neck_score_log[positive_mask] - mean_log) / std_log
    
    # Step 1: Find seed pixels (high threshold)
    seed_mask = (z > z_threshold_high) & mask
    
    # Apply exclusion mask - remove seeds that are in exclusion zones (near previous cuts)
    if exclusion_mask is not None:
        n_seeds_before = seed_mask.sum()
        seed_mask = seed_mask & ~exclusion_mask
        n_excluded = n_seeds_before - seed_mask.sum()
        if debug and n_excluded > 0:
            print(f"    Excluded {n_excluded} seed pixels near previous cut lines")
    
    n_seeds = seed_mask.sum()
    
    # Note: low_mask kept for debug info but not used in soft membership approach
    low_mask = (z > z_threshold_high * z_threshold_low_ratio) & mask
    n_low = low_mask.sum()
    
    if debug:
        print(f"    Seed pixels (z > {z_threshold_high}): {n_seeds}")
        print(f"    Soft membership: sigma_scale={sigma_scale}")
    
    if n_seeds == 0:
        return [], np.zeros_like(mask, dtype=int), {
            'seed_mask': seed_mask, 
            'low_mask': low_mask,
            'z_scores': z
        }
    
    # Step 2: Form initial clusters from seeds using connected components
    # No dilation needed - soft membership expansion handles nearby pixels
    # Using 8-connectivity to group touching seed pixels
    labeled_seeds, n_clusters = ndlabel(seed_mask)
    
    if debug:
        print(f"    Raw seed clusters found: {n_clusters}")
    
    # Minimum seeds needed for reliable aspect ratio calculation
    min_seeds_for_aspect = 6
    
    # Step 3 & 4: Check compactness on seeds, then compute soft membership
    clusters = []
    all_raw_clusters = []  # Track ALL clusters including rejected ones for debugging
    final_labeled = np.zeros_like(mask, dtype=int)
    valid_cluster_id = 0
    
    for cluster_id in range(1, n_clusters + 1):
        # Get seed cluster (direct from labeling, no dilation)
        seed_cluster = (labeled_seeds == cluster_id)
        seed_size = seed_cluster.sum()
        
        if seed_size == 0:
            continue
        
        # Initialize raw cluster info for debugging
        seed_ys, seed_xs = np.where(seed_cluster)
        seed_centroid = (seed_ys.mean(), seed_xs.mean())
        
        raw_cluster_info = {
            'raw_id': cluster_id,
            'seed_size': seed_size,
            'seed_centroid': seed_centroid,
            'seed_mask': seed_cluster.copy(),
            'status': 'pending',
            'rejection_reason': None,
        }
        
        # Step 3: Check compactness on SEED pixels (before soft expansion)
        if seed_size >= min_seeds_for_aspect:
            # Compute aspect ratio on seeds
            ys_centered = seed_ys - seed_centroid[0]
            xs_centered = seed_xs - seed_centroid[1]
            
            cov_matrix = np.cov(ys_centered, xs_centered)
            eigenvalues = np.linalg.eigvalsh(cov_matrix)
            eigenvalues = np.sort(eigenvalues)[::-1]
            
            if eigenvalues[1] > 1e-6:
                seed_aspect_ratio = np.sqrt(eigenvalues[0] / eigenvalues[1])
            else:
                seed_aspect_ratio = float('inf')
            
            raw_cluster_info['seed_aspect_ratio'] = seed_aspect_ratio
            
            if seed_aspect_ratio > max_aspect_ratio:
                if debug:
                    print(f"      Cluster {cluster_id}: seed_size={seed_size}, seed_aspect={seed_aspect_ratio:.2f} - REJECTED (seeds too linear)")
                raw_cluster_info['status'] = 'rejected'
                raw_cluster_info['rejection_reason'] = f'seeds too linear (aspect={seed_aspect_ratio:.2f})'
                all_raw_clusters.append(raw_cluster_info)
                continue
        else:
            seed_aspect_ratio = 1.0
            raw_cluster_info['seed_aspect_ratio'] = seed_aspect_ratio
        
        # Step 4: Compute soft membership weights
        weights, effective_size, binary_mask = compute_soft_cluster_membership(
            seed_cluster, z, mask, 
            z_high=z_threshold_high, 
            z_min=0,
            sigma_scale=sigma_scale,
            debug=debug
        )
        
        raw_cluster_info['effective_size'] = effective_size
        raw_cluster_info['binary_mask'] = binary_mask.copy()
        raw_cluster_info['weights'] = weights.copy()
        
        # Check minimum effective size - as percentage of body area with cap
        # Use a lower threshold here to allow small clusters to reach the merging stage
        # The post-merge filter will apply a stricter threshold
        # Cap at 15 for initial filtering (will be merged if close to other clusters)
        body_area = mask.sum()
        adaptive_min_cluster_size = max(4, min(15, body_area * 0.008))  # 0.8% of area, floor=4, cap=15
        
        if effective_size < adaptive_min_cluster_size:
            if debug:
                print(f"      Cluster {cluster_id}: seed_size={seed_size}, effective_size={effective_size:.1f} - REJECTED (effective size too small, min={adaptive_min_cluster_size:.1f})")
            raw_cluster_info['status'] = 'rejected'
            raw_cluster_info['rejection_reason'] = f'effective size too small ({effective_size:.1f} < {adaptive_min_cluster_size:.1f})'
            all_raw_clusters.append(raw_cluster_info)
            continue
        
        # Step 5: Compute aspect ratio on binary mask (w > 0.5)
        aspect_ratio = get_expanded_aspect_ratio(binary_mask)
        raw_cluster_info['expanded_aspect_ratio'] = aspect_ratio
        
        # Check aspect ratio on expanded region
        # For small binary masks or small bodies, be more lenient:
        # - Very small binary (<8 pixels): skip check entirely (unreliable)
        # - Small body (<600 area): use relaxed threshold (6.0 instead of 4.0)
        # This is because small clusters near necks often expand linearly along the neck
        binary_size = binary_mask.sum()
        body_area = mask.sum()
        
        if body_area < 600:
            effective_max_aspect = max_aspect_ratio * 1.5  # 4.0 -> 6.0
        else:
            effective_max_aspect = max_aspect_ratio
        
        if binary_size >= 8 and aspect_ratio > effective_max_aspect:
            if debug:
                print(f"      Cluster {cluster_id}: seed_size={seed_size}, effective_size={effective_size:.1f}, "
                      f"expanded_aspect={aspect_ratio:.2f} - REJECTED (expanded too linear, max={effective_max_aspect:.1f})")
            raw_cluster_info['status'] = 'rejected'
            raw_cluster_info['rejection_reason'] = f'expanded too linear (aspect={aspect_ratio:.2f})'
            all_raw_clusters.append(raw_cluster_info)
            continue
        
        # Compute centroid from binary mask
        exp_ys, exp_xs = np.where(binary_mask)
        centroid = (exp_ys.mean(), exp_xs.mean()) if len(exp_ys) > 0 else seed_centroid
        
        # Step 6: Check if cluster is on image border (reject border clusters)
        # Clusters on borders often have artificially high neck scores due to boundary effects
        H, W = mask.shape
        border_margin = 3  # Pixels from edge to consider as border
        cy, cx = centroid
        
        on_border = (cy < border_margin or cy >= H - border_margin or 
                     cx < border_margin or cx >= W - border_margin)
        
        # Also check if any seed pixels touch the image border
        seed_ys, seed_xs = np.where(seed_cluster)
        seeds_touch_border = (seed_ys.min() < border_margin or seed_ys.max() >= H - border_margin or
                              seed_xs.min() < border_margin or seed_xs.max() >= W - border_margin)
        
        if on_border or seeds_touch_border:
            if debug:
                print(f"      Cluster {cluster_id}: seed_size={seed_size}, effective_size={effective_size:.1f} - "
                      f"REJECTED (on image border)")
            raw_cluster_info['status'] = 'rejected'
            raw_cluster_info['rejection_reason'] = 'on image border'
            raw_cluster_info['centroid'] = centroid
            all_raw_clusters.append(raw_cluster_info)
            continue
        
        if debug:
            print(f"      Cluster {cluster_id}: seed_size={seed_size}, effective_size={effective_size:.1f}, "
                  f"seed_aspect={seed_aspect_ratio:.2f}, expanded_aspect={aspect_ratio:.2f}")
        
        # Compute other properties using binary mask
        prominence = neck_score[binary_mask].sum() if binary_mask.any() else 0
        max_score = neck_score[binary_mask].max() if binary_mask.any() else 0
        mean_z = z[binary_mask].mean() if binary_mask.any() else 0
        
        valid_cluster_id += 1
        final_labeled[binary_mask] = valid_cluster_id
        
        cluster_info = {
            'id': valid_cluster_id,
            'size': effective_size,  # Now stores effective (soft) size
            'binary_size': binary_mask.sum(),  # Actual pixel count
            'seed_size': seed_size,
            'centroid': centroid,
            'prominence': prominence,
            'max_score': max_score,
            'mean_z': mean_z,
            'aspect_ratio': aspect_ratio,
            'seed_aspect_ratio': seed_aspect_ratio,
            'pixels': list(zip(exp_ys, exp_xs)),
            'mask': binary_mask,  # Binary mask (w > 0.5)
            'weights': weights,   # Soft weights for debugging
            'seed_mask': seed_cluster,
        }
        clusters.append(cluster_info)
        
        # Also add to raw clusters as valid
        raw_cluster_info['status'] = 'valid'
        raw_cluster_info['valid_id'] = valid_cluster_id
        raw_cluster_info['centroid'] = centroid
        all_raw_clusters.append(raw_cluster_info)
    
    # Merge clusters with very close centroids
    # This handles cases where the same neck region gets split into multiple seed clusters
    # Use smaller multiplier for large bodies to avoid merging clusters from different necks
    body_area = mask.sum()
    sigma = sigma_scale * np.sqrt(body_area)
    
    if body_area > 3000:
        # Large bodies: be conservative with merging (1.2 * sigma)
        merge_multiplier = 1.2
    elif body_area > 1500:
        # Medium bodies: moderate merging (1.5 * sigma)
        merge_multiplier = 1.5
    else:
        # Small bodies: more aggressive merging (2.0 * sigma)
        merge_multiplier = 2.0
    
    merge_distance = merge_multiplier * sigma
    
    if len(clusters) > 1:
        merged_clusters = []
        used = set()
        
        for i, cluster_i in enumerate(clusters):
            if i in used:
                continue
            
            # Start with cluster i
            merged = {
                'mask': cluster_i['mask'].copy(),
                'seed_mask': cluster_i['seed_mask'].copy(),
                'size': cluster_i['size'],
                'prominence': cluster_i['prominence'],
                'merged_from': [cluster_i['id']],
            }
            
            cy_i, cx_i = cluster_i['centroid']
            
            # Find all clusters close enough to merge
            for j, cluster_j in enumerate(clusters):
                if j <= i or j in used:
                    continue
                
                cy_j, cx_j = cluster_j['centroid']
                dist = np.sqrt((cy_i - cy_j)**2 + (cx_i - cx_j)**2)
                
                if dist < merge_distance:
                    # Merge cluster j into merged cluster
                    merged['mask'] = merged['mask'] | cluster_j['mask']
                    merged['seed_mask'] = merged['seed_mask'] | cluster_j['seed_mask']
                    merged['size'] += cluster_j['size']
                    merged['prominence'] += cluster_j['prominence']
                    merged['merged_from'].append(cluster_j['id'])
                    used.add(j)
            
            used.add(i)
            
            # Recompute centroid from combined binary mask
            merged_ys, merged_xs = np.where(merged['mask'])
            if len(merged_ys) > 0:
                merged_centroid = (merged_ys.mean(), merged_xs.mean())
            else:
                merged_centroid = cluster_i['centroid']
            
            # Recompute aspect ratio on merged mask
            merged_aspect = get_expanded_aspect_ratio(merged['mask'])
            
            # Create merged cluster info
            merged_cluster_info = {
                'id': len(merged_clusters) + 1,
                'size': merged['size'],
                'binary_size': merged['mask'].sum(),
                'seed_size': merged['seed_mask'].sum(),
                'centroid': merged_centroid,
                'prominence': merged['prominence'],
                'max_score': neck_score[merged['mask']].max() if merged['mask'].any() else 0,
                'mean_z': z[merged['mask']].mean() if merged['mask'].any() else 0,
                'aspect_ratio': merged_aspect,
                'seed_aspect_ratio': cluster_i['seed_aspect_ratio'],  # Keep from primary
                'pixels': list(zip(merged_ys, merged_xs)),
                'mask': merged['mask'],
                'weights': cluster_i['weights'],  # Keep from primary (approximate)
                'seed_mask': merged['seed_mask'],
                'merged_from': merged['merged_from'],
            }
            merged_clusters.append(merged_cluster_info)
        
        if debug and len(merged_clusters) < len(clusters):
            print(f"    Merged {len(clusters)} clusters → {len(merged_clusters)} (merge_distance={merge_distance:.1f})")
        
        clusters = merged_clusters
    
    # Post-merge filter: remove clusters that are still too small after merging
    # This catches isolated noise clusters that didn't get merged with anything
    # Use slightly stricter threshold than initial, but not too strict
    # Cap at 18 to allow reasonable clusters to pass through to two-cluster selection
    body_area = mask.sum()
    min_final_cluster_size = max(4, min(18, body_area * 0.008))  # 0.8% of area, floor=4, cap=18
    
    clusters_before_filter = len(clusters)
    clusters = [c for c in clusters if c['size'] >= min_final_cluster_size]
    
    if debug and len(clusters) < clusters_before_filter:
        print(f"    Post-merge filter: {clusters_before_filter} → {len(clusters)} clusters (min_size={min_final_cluster_size:.1f})")
    
    # Sort by prominence (most prominent first)
    clusters.sort(key=lambda c: c['prominence'], reverse=True)
    
    if debug:
        print(f"    Valid clusters: {len(clusters)}")
    
    debug_info = {
        'seed_mask': seed_mask,
        'low_mask': low_mask,
        'labeled_seeds': labeled_seeds,  # Direct labeling of seeds (no dilation)
        'z_scores': z,
        'n_raw_clusters': n_clusters,
        'all_raw_clusters': all_raw_clusters,  # All clusters for debugging
        'labeled_clusters': final_labeled,
        'z_threshold_high': z_threshold_high,
        'sigma_scale': sigma_scale,
    }
    
    return clusters, final_labeled, debug_info


def compute_soft_cluster_membership(seed_mask, z_scores, region_mask, z_high, z_min=0, 
                                     sigma_scale=0.15, debug=False):
    """
    Compute soft membership weights for pixels around a seed cluster.
    
    Each pixel gets a weight based on:
    - Spatial proximity to nearest seed pixel (Gaussian decay)
    - Z-score intensity (linear ramp from z_min to z_high)
    
    Weight = f(z) × g(distance)
    
    Parameters:
        seed_mask: Binary mask of seed pixels (high threshold)
        z_scores: Z-score field for the entire image
        region_mask: Binary mask of the region (boundary constraint)
        z_high: Z-score for full intensity weight (f(z) = 1)
        z_min: Z-score for zero intensity weight (f(z) = 0), default 0
        sigma_scale: Spatial decay scale as fraction of sqrt(area), default 0.15
        debug: Print debug information
    
    Returns:
        weights: Array of soft membership weights [0, 1]
        effective_size: Sum of weights (equivalent to soft cluster size)
        binary_mask: Thresholded mask (w > 0.5) for aspect ratio calculation
    """
    from scipy.ndimage import distance_transform_edt
    
    if not seed_mask.any():
        return np.zeros_like(region_mask, dtype=float), 0, np.zeros_like(region_mask, dtype=bool)
    
    # Compute sigma based on region size
    # For small bodies, use larger sigma_scale to allow more expansion
    # This helps when clusters are competing in hot regions
    area = region_mask.sum()
    if area < 400:
        # Very small bodies: much larger sigma to allow expansion
        effective_sigma_scale = sigma_scale * 2.5  # 0.15 -> 0.375
    elif area < 600:
        # Small bodies: increase sigma_scale
        effective_sigma_scale = sigma_scale * 2.0  # 0.15 -> 0.30
    elif area < 1000:
        effective_sigma_scale = sigma_scale * 1.5  # 0.15 -> 0.225
    else:
        effective_sigma_scale = sigma_scale
    
    sigma = effective_sigma_scale * np.sqrt(area)
    
    # Enforce minimum sigma to prevent too-tight clustering
    sigma = max(sigma, 4.0)  # Increased from 3.0
    
    if debug:
        print(f"      Soft membership: sigma={sigma:.2f} (area={area}, scale={effective_sigma_scale:.3f})")
    
    # Compute distance to nearest seed pixel
    # distance_transform_edt computes distance to nearest False pixel
    # So we invert seed_mask
    distance_to_seed = distance_transform_edt(~seed_mask)
    
    # Spatial decay: g(d) = exp(-d² / (2σ²))
    g_spatial = np.exp(-distance_to_seed**2 / (2 * sigma**2))
    
    # Intensity term: f(z) = clamp((z - z_min) / (z_high - z_min), 0, 1)
    z_range = z_high - z_min
    if z_range > 1e-10:
        f_intensity = np.clip((z_scores - z_min) / z_range, 0, 1)
    else:
        f_intensity = (z_scores > z_min).astype(float)
    
    # Combined weight (only within region)
    weights = f_intensity * g_spatial * region_mask
    
    # Effective cluster size = sum of weights
    effective_size = weights.sum()
    
    # Binary mask for aspect ratio (threshold at 0.5)
    binary_mask = (weights > 0.5) & region_mask
    
    # Also include all seed pixels in binary mask (they should always be "in")
    binary_mask = binary_mask | seed_mask
    
    if debug:
        n_binary = binary_mask.sum()
        print(f"      Effective size: {effective_size:.1f}, binary pixels (w>0.5): {n_binary}")
    
    return weights, effective_size, binary_mask


def get_expanded_aspect_ratio(binary_mask):
    """
    Compute aspect ratio from a binary mask using covariance eigenvalues.
    
    Returns:
        aspect_ratio: Ratio of major to minor axis (>= 1.0)
    """
    if binary_mask.sum() < 3:
        return 1.0
    
    ys, xs = np.where(binary_mask)
    centroid_y, centroid_x = ys.mean(), xs.mean()
    
    ys_centered = ys - centroid_y
    xs_centered = xs - centroid_x
    
    cov_matrix = np.cov(ys_centered, xs_centered)
    eigenvalues = np.linalg.eigvalsh(cov_matrix)
    eigenvalues = np.sort(eigenvalues)[::-1]
    
    if eigenvalues[1] > 1e-6:
        return np.sqrt(eigenvalues[0] / eigenvalues[1])
    else:
        return float('inf')


def expand_cluster_hysteresis(seed_mask, low_mask, region_mask):
    """
    DEPRECATED: Kept for backwards compatibility.
    Use compute_soft_cluster_membership instead.
    
    Expand a seed cluster by including connected low-threshold pixels.
    """
    from scipy.ndimage import binary_dilation
    
    current = seed_mask.copy()
    struct = np.ones((3, 3), dtype=bool)
    
    while True:
        dilated = binary_dilation(current, structure=struct, iterations=1)
        new_pixels = dilated & low_mask & region_mask & ~current
        
        if not new_pixels.any():
            break
        
        current = current | new_pixels
    
    return current


def find_neck_cut_line(clusters, mask, min_area_ratio=0.15, neck_score=None, 
                       concavity_factor=None, debug=False):
    """
    Given the two most prominent clusters, create a cutting line between them.
    
    Parameters:
        clusters: List of cluster info dicts (sorted by prominence)
        mask: Binary region mask
        min_area_ratio: Minimum area ratio for each part after split
        neck_score: Neck score field (optional, for concavity-based validation)
        concavity_factor: Concavity factor field (optional, for long cut validation)
        debug: Print debug information
    
    Returns:
        cut_line: Dictionary with cut line info, or None if no valid cut
        debug_info: Dictionary with debug information
    """
    from scipy.ndimage import label as ndlabel, binary_dilation
    from skimage.draw import line
    
    debug_info = {
        'n_clusters': len(clusters),
        'selected_clusters': None,
        'cut_endpoints': None,
        'creates_valid_split': False,
        'area_ratios': None,
        'rejection_reason': None,
    }
    
    if len(clusters) < 2:
        debug_info['rejection_reason'] = 'fewer_than_2_clusters'
        if debug:
            print(f"    Cannot create cut: only {len(clusters)} cluster(s)")
        return None, debug_info
    
    # Compute max diameter of shape using distance transform
    # This is the width of the shape at its widest point
    from scipy.ndimage import distance_transform_edt
    dist_transform = distance_transform_edt(mask)
    max_radius = dist_transform.max()
    max_diameter = 2 * max_radius
    
    # When there are 3+ clusters, try all pairs and select the one with shortest distance
    # This helps find the true neck cut rather than just using prominence
    if len(clusters) >= 3:
        # Compute min cluster size threshold
        body_area = mask.sum()
        min_cluster_size_two = max(4, min(30, body_area * 0.012))
        
        # Find all valid pairs (both clusters above min size)
        valid_pairs = []
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                c_i, c_j = clusters[i], clusters[j]
                if c_i['size'] >= min_cluster_size_two and c_j['size'] >= min_cluster_size_two:
                    cy_i, cx_i = c_i['centroid']
                    cy_j, cx_j = c_j['centroid']
                    dist = np.sqrt((cy_i - cy_j)**2 + (cx_i - cx_j)**2)
                    valid_pairs.append((dist, c_i, c_j))
        
        if valid_pairs:
            # Sort by distance (shortest first) and select the shortest
            valid_pairs.sort(key=lambda x: x[0])
            _, cluster_A, cluster_B = valid_pairs[0]
            
            if debug:
                print(f"    Multiple clusters ({len(clusters)}): trying {len(valid_pairs)} valid pairs")
                print(f"    Selected shortest-distance pair (dist={valid_pairs[0][0]:.1f})")
        else:
            # Fallback to top 2 by prominence
            cluster_A = clusters[0]
            cluster_B = clusters[1]
    else:
        # Only 2 clusters - use them directly
        cluster_A = clusters[0]
        cluster_B = clusters[1]
    
    debug_info['selected_clusters'] = (cluster_A, cluster_B)
    debug_info['max_diameter'] = max_diameter
    
    if debug:
        print(f"    Max diameter (from distance transform): {max_diameter:.1f} pixels")
        print(f"    Selected clusters:")
        # Show effective size (soft) and binary size (actual pixels)
        binary_A = cluster_A.get('binary_size', cluster_A['size'])
        binary_B = cluster_B.get('binary_size', cluster_B['size'])
        print(f"      Cluster A: effective_size={cluster_A['size']:.1f}, binary_size={binary_A}, centroid=({cluster_A['centroid'][0]:.1f}, {cluster_A['centroid'][1]:.1f})")
        print(f"      Cluster B: effective_size={cluster_B['size']:.1f}, binary_size={binary_B}, centroid=({cluster_B['centroid'][0]:.1f}, {cluster_B['centroid'][1]:.1f})")
    
    # === CHECK 1: Minimum cluster sizes ===
    # Adaptive: cluster should be at least ~0.8% of body area for two-cluster method
    # Cap at 18 to match post-merge filter threshold
    body_area = mask.sum()
    min_cluster_size_two = max(4, min(18, body_area * 0.008))  # 0.8% of area, floor=4, cap=18
    
    # Get effective sizes (soft membership sum) for comparison
    size_A = cluster_A['size']  # This is now effective_size (sum of soft weights)
    size_B = cluster_B['size']
    
    if debug:
        print(f"    Min effective size for body (area={body_area}): {min_cluster_size_two:.1f}")
    
    if size_A < min_cluster_size_two or size_B < min_cluster_size_two:
        debug_info['rejection_reason'] = 'clusters_too_small_for_two_cluster'
        if debug:
            print(f"    REJECTED: effective sizes ({size_A:.1f}, {size_B:.1f}) < {min_cluster_size_two:.1f} for two-cluster method")
        return None, debug_info
    
    # === CHECK 2: Distance between clusters ===
    # Get centroids
    cy_A, cx_A = cluster_A['centroid']
    cy_B, cx_B = cluster_B['centroid']
    
    # Check distance between clusters - should be less than max diameter
    # A valid neck cut crosses a constriction, not the whole cell diagonally
    cluster_distance = np.sqrt((cy_A - cy_B)**2 + (cx_A - cx_B)**2)
    distance_ratio = cluster_distance / max_diameter
    
    if debug:
        print(f"    Cluster distance: {cluster_distance:.1f} pixels (ratio={distance_ratio:.2f})")
    
    # DISTANCE CHECK with concavity override
    # If clusters are far apart (>75% of diameter), check if both have high concavity
    # High concavity at both ends = true neck spanning the cell
    # Low concavity = edge artifact
    max_distance_ratio = 0.75  # Soft limit - can be overridden with high concavity
    hard_max_distance_ratio = 1.0  # Hard limit - never allow cuts longer than diameter
    base_concavity_threshold = 0.25  # Base threshold at 75% distance (lowered from 0.3)
    
    # Hard rejection: cuts longer than the diameter are never valid
    if cluster_distance > max_diameter * hard_max_distance_ratio:
        debug_info['rejection_reason'] = 'clusters_exceed_hard_limit'
        debug_info['cluster_distance'] = cluster_distance
        if debug:
            print(f"    REJECTED: cluster distance ({cluster_distance:.1f}) > {hard_max_distance_ratio*100:.0f}% of max diameter ({max_diameter:.1f}) - hard limit")
        return None, debug_info
    
    if cluster_distance > max_diameter * max_distance_ratio:
        # Clusters are far apart - check concavity before rejecting
        allow_long_cut = False
        
        # Scale concavity threshold based on how far over 75% we are
        # At 75%: threshold = 0.25
        # At 100%: threshold = 0.45
        # Linear interpolation between them
        excess_ratio = (distance_ratio - max_distance_ratio) / (hard_max_distance_ratio - max_distance_ratio)
        scaled_concavity_threshold = base_concavity_threshold + excess_ratio * 0.2  # 0.25 to 0.45
        
        if concavity_factor is not None:
            # Compute mean concavity at each cluster location
            mask_A = cluster_A.get('mask')
            mask_B = cluster_B.get('mask')
            
            if mask_A is not None and mask_B is not None:
                concavity_A = concavity_factor[mask_A].mean() if mask_A.any() else 0
                concavity_B = concavity_factor[mask_B].mean() if mask_B.any() else 0
                
                if debug:
                    print(f"    Long cut check - concavity: A={concavity_A:.3f}, B={concavity_B:.3f} (scaled threshold={scaled_concavity_threshold:.3f})")
                
                # Allow long cut if:
                # 1. Both clusters have concavity above threshold, OR
                # 2. One cluster has very high concavity (>0.5) and average is above threshold
                avg_concavity = (concavity_A + concavity_B) / 2
                high_concavity_threshold = 0.5
                
                if concavity_A >= scaled_concavity_threshold and concavity_B >= scaled_concavity_threshold:
                    allow_long_cut = True
                    if debug:
                        print(f"    ALLOWED: Long cut accepted due to high concavity at both clusters")
                elif (concavity_A >= high_concavity_threshold or concavity_B >= high_concavity_threshold) and avg_concavity >= scaled_concavity_threshold * 0.8:
                    # One cluster has very high concavity and average is reasonable
                    allow_long_cut = True
                    if debug:
                        print(f"    ALLOWED: Long cut accepted - one cluster very high ({max(concavity_A, concavity_B):.3f}), avg={avg_concavity:.3f}")
        
        if not allow_long_cut:
            debug_info['rejection_reason'] = 'clusters_too_far_apart'
            debug_info['cluster_distance'] = cluster_distance
            if debug:
                print(f"    REJECTED: cluster distance ({cluster_distance:.1f}) > {max_distance_ratio*100:.0f}% of max diameter ({max_diameter:.1f})")
            return None, debug_info
    
    # Create cut line between centroids
    line_y, line_x = line(int(round(cy_A)), int(round(cx_A)), 
                          int(round(cy_B)), int(round(cx_B)))
    
    debug_info['cut_endpoints'] = ((cy_A, cx_A), (cy_B, cx_B))
    
    # Clip to image bounds
    H, W = mask.shape
    valid = (line_y >= 0) & (line_y < H) & (line_x >= 0) & (line_x < W)
    line_y = line_y[valid]
    line_x = line_x[valid]
    
    if len(line_y) == 0:
        debug_info['rejection_reason'] = 'cut_line_outside_bounds'
        if debug:
            print(f"    Cut line outside image bounds")
        return None, debug_info
    
    # Create cut mask and dilate slightly
    cut_mask = np.zeros_like(mask, dtype=bool)
    cut_mask[line_y, line_x] = True
    cut_dilated = binary_dilation(cut_mask, iterations=2)
    
    # Check if cutting creates valid split
    test_mask = mask & ~cut_dilated
    labeled, n_components = ndlabel(test_mask)
    
    if debug:
        print(f"    Cut line length: {len(line_y)} pixels")
        print(f"    Components after cut: {n_components}")
    
    if n_components < 2:
        debug_info['rejection_reason'] = 'no_split_created'
        if debug:
            print(f"    Cut does not create split")
        return None, debug_info
    
    # Check area ratios
    total_area = mask.sum()
    areas = []
    for i in range(1, n_components + 1):
        areas.append((labeled == i).sum())
    
    area_ratios = [a / total_area for a in areas]
    debug_info['area_ratios'] = area_ratios
    
    # Check if at least two parts are significant
    significant = [r for r in area_ratios if r >= min_area_ratio]
    
    if debug:
        print(f"    Area ratios: {[f'{r:.3f}' for r in area_ratios]}")
        print(f"    Significant parts (>= {min_area_ratio}): {len(significant)}")
    
    if len(significant) < 2:
        debug_info['rejection_reason'] = 'split_parts_too_small'
        if debug:
            print(f"    Split parts too small")
        return None, debug_info
    
    debug_info['creates_valid_split'] = True
    
    cut_line = {
        'cluster_A': cluster_A,
        'cluster_B': cluster_B,
        'line_y': line_y,
        'line_x': line_x,
        'cut_mask': cut_mask,
        'cut_dilated': cut_dilated,
        'n_components': n_components,
        'area_ratios': area_ratios,
    }
    
    if debug:
        print(f"    >>> VALID CUT LINE FOUND <<<")
    
    return cut_line, debug_info


def find_cut_line_single_cluster(cluster, mask, extend_ratio=0.3, min_area_ratio=0.15, debug=False):
    """
    Create a cut line from a single cluster using linear regression.
    
    When the neck is very narrow, both sides merge into one cluster.
    We use the cluster's shape (via regression) to find the cutting direction.
    
    Algorithm:
    1. Fit a line through all cluster pixels using linear regression
    2. Extend the line by extend_ratio from both ends
    3. Check if the cut creates a valid split
    
    Parameters:
        cluster: Cluster info dict with 'pixels', 'centroid', etc.
        mask: Binary region mask
        extend_ratio: How much to extend the line (0.3 = 30% from each end)
        min_area_ratio: Minimum area ratio for valid split
        debug: Print debug information
    
    Returns:
        cut_line: Cut line info dict, or None if no valid cut
        debug_info: Dictionary with debug information
    """
    from scipy.ndimage import label as ndlabel, binary_dilation, binary_erosion, distance_transform_edt
    
    debug_info = {
        'cluster': cluster,
        'method': 'erosion',
        'creates_valid_split': False,
        'area_ratios': None,
        'rejection_reason': None,
        'erosion_iterations': 0,
    }
    
    if debug:
        print(f"    Using erosion-based method for single cluster...")
    
    # Get the cluster region
    cluster_mask = cluster['mask']
    cluster_centroid = cluster['centroid']
    
    # FIRST ATTEMPT: Remove cluster pixels directly and dilate
    # The cluster is at the neck, so removing it might split the shape
    for dilation_iter in range(0, 4):  # Try 0, 1, 2, 3 dilations of cluster
        if dilation_iter == 0:
            cut_region = cluster_mask.copy()
        else:
            cut_region = binary_dilation(cluster_mask, iterations=dilation_iter)
        
        # Remove cut region from mask
        test_mask = mask & ~cut_region
        
        # Check if split
        labeled, n_components = ndlabel(test_mask)
        
        if n_components >= 2:
            # Check if we have at least 2 significant parts
            total_area = mask.sum()
            areas = []
            for i in range(1, n_components + 1):
                areas.append((labeled == i).sum())
            
            area_ratios = [a / total_area for a in areas]
            significant = [r for r in area_ratios if r >= min_area_ratio]
            
            if len(significant) >= 2:
                if debug:
                    print(f"    Split achieved by removing cluster + {dilation_iter} dilation")
                    print(f"    Components: {n_components}, Area ratios: {[f'{r:.3f}' for r in area_ratios]}")
                
                debug_info['erosion_iterations'] = dilation_iter
                debug_info['area_ratios'] = area_ratios
                debug_info['creates_valid_split'] = True
                debug_info['method'] = 'cluster_removal'
                
                cut_ys, cut_xs = np.where(cut_region & mask)
                
                cut_line = {
                    'cluster': cluster,
                    'method': 'single_cluster_erosion',
                    'line_y': cut_ys,
                    'line_x': cut_xs,
                    'cut_mask': cut_region & mask,
                    'cut_dilated': cut_region & mask,
                    'eroded_mask': test_mask,
                    'erosion_level': dilation_iter,
                    'n_components': n_components,
                    'area_ratios': area_ratios,
                }
                
                if debug:
                    print(f"    >>> VALID SPLIT FOUND (cluster removal) <<<")
                
                return cut_line, debug_info
    
    if debug:
        print(f"    Cluster removal did not split, trying distance-based erosion...")
    
    # SECOND ATTEMPT: Global erosion based on distance transform
    # Compute distance transform - gives distance to nearest edge
    dist_transform = distance_transform_edt(mask)
    max_radius = dist_transform.max()
    
    if debug:
        print(f"    Max distance (radius): {max_radius:.1f} pixels")
    
    # Iteratively erode by thresholding distance transform
    # Start from distance=1 and increase until split
    max_iterations = int(max_radius)
    
    for erosion_level in range(1, max_iterations + 1):
        # Keep only pixels with distance > erosion_level
        eroded_mask = dist_transform > erosion_level
        eroded_mask = eroded_mask & mask  # Stay within original mask
        
        # Check if split
        labeled, n_components = ndlabel(eroded_mask)
        
        if n_components >= 2:
            # Check if we have at least 2 significant parts
            total_area = mask.sum()
            areas = []
            for i in range(1, n_components + 1):
                areas.append((labeled == i).sum())
            
            area_ratios = [a / total_area for a in areas]
            significant = [r for r in area_ratios if r >= min_area_ratio]
            
            if len(significant) >= 2:
                if debug:
                    print(f"    Split achieved at erosion level {erosion_level}")
                    print(f"    Components: {n_components}, Area ratios: {[f'{r:.3f}' for r in area_ratios]}")
                
                debug_info['erosion_iterations'] = erosion_level
                debug_info['area_ratios'] = area_ratios
                debug_info['creates_valid_split'] = True
                
                # Create cut mask - the eroded pixels
                cut_mask = mask & ~eroded_mask
                
                # For visualization, get the boundary between eroded parts
                # The "cut line" is effectively the eroded region
                cut_ys, cut_xs = np.where(cut_mask)
                
                cut_line = {
                    'cluster': cluster,
                    'method': 'single_cluster_erosion',
                    'line_y': cut_ys,
                    'line_x': cut_xs,
                    'cut_mask': cut_mask,
                    'cut_dilated': cut_mask,  # Already dilated by erosion
                    'eroded_mask': eroded_mask,
                    'erosion_level': erosion_level,
                    'n_components': n_components,
                    'area_ratios': area_ratios,
                }
                
                if debug:
                    print(f"    >>> VALID SPLIT FOUND (erosion method) <<<")
                
                return cut_line, debug_info
        
        # If erosion removed everything, stop
        # Use adaptive threshold based on region size
        min_remaining = max(20, int(mask.sum() * 0.1))  # At least 10% or 20px
        if eroded_mask.sum() < min_remaining:
            if debug:
                print(f"    Erosion removed too much at level {erosion_level} (remaining: {eroded_mask.sum()} < {min_remaining})")
            break
    
    debug_info['rejection_reason'] = 'erosion_did_not_split'
    if debug:
        print(f"    Erosion did not create valid split after {max_iterations} iterations")
    
    return None, debug_info


def find_cut_line_single_cluster_regression(cluster, mask, extend_ratio=0.3, min_area_ratio=0.15, debug=False):
    """
    [DEPRECATED - kept for reference]
    Create a cut line from a single cluster using linear regression.
    
    When the neck is very narrow, both sides merge into one cluster.
    We use the cluster's shape (via regression) to find the cutting direction.
    
    Algorithm:
    1. Fit a line through all cluster pixels using linear regression
    2. Extend the line to cross the mask
    3. Check if the cut creates a valid split
    
    Parameters:
        cluster: Cluster info dict with 'pixels', 'centroid', etc.
        mask: Binary region mask
        extend_ratio: How much to extend the line (0.3 = 30% from each end)
        min_area_ratio: Minimum area ratio for valid split
        debug: Print debug information
    
    Returns:
        cut_line: Cut line info dict, or None if no valid cut
        debug_info: Dictionary with debug information
    """
    from scipy.ndimage import label as ndlabel, binary_dilation
    from skimage.draw import line
    
    debug_info = {
        'cluster': cluster,
        'regression_info': None,
        'cut_endpoints': None,
        'creates_valid_split': False,
        'area_ratios': None,
        'rejection_reason': None,
    }
    
    # Get cluster pixels
    pixels = cluster['pixels']  # List of (y, x) tuples
    if len(pixels) < 3:
        debug_info['rejection_reason'] = 'cluster_too_small_for_regression'
        if debug:
            print(f"    Cluster too small for regression ({len(pixels)} pixels)")
        return None, debug_info
    
    # Convert to arrays
    ys = np.array([p[0] for p in pixels])
    xs = np.array([p[1] for p in pixels])
    
    # Fit line using linear regression
    # We fit both y = ax + b and x = cy + d, then use the one with better fit
    # This handles vertical and horizontal lines properly
    
    # Try y = ax + b (x as independent variable)
    if xs.std() > 1e-6:
        coeffs_yx = np.polyfit(xs, ys, 1)
        y_pred_yx = np.polyval(coeffs_yx, xs)
        residuals_yx = np.sum((ys - y_pred_yx)**2)
    else:
        residuals_yx = float('inf')
    
    # Try x = cy + d (y as independent variable)
    if ys.std() > 1e-6:
        coeffs_xy = np.polyfit(ys, xs, 1)
        x_pred_xy = np.polyval(coeffs_xy, ys)
        residuals_xy = np.sum((xs - x_pred_xy)**2)
    else:
        residuals_xy = float('inf')
    
    # Choose better fit
    if residuals_yx <= residuals_xy:
        # Use y = ax + b
        use_yx = True
        slope = coeffs_yx[0]
        intercept = coeffs_yx[1]
        # Tangent direction vector: (slope, 1) in (y, x) space, normalized
        tangent = np.array([slope, 1.0])
        tangent = tangent / np.linalg.norm(tangent)
    else:
        # Use x = cy + d
        use_yx = False
        slope = coeffs_xy[0]
        intercept = coeffs_xy[1]
        # Tangent direction vector: (1, slope) in (y, x) space
        tangent = np.array([1.0, slope])
        tangent = tangent / np.linalg.norm(tangent)
    
    # CRITICAL: The single cluster at a neck spans ACROSS the neck
    # (from one edge to the other). So:
    # - Tangent = direction the cluster is elongated = ACROSS the neck
    # - We should cut ALONG the tangent (along the cluster), not perpendicular!
    # 
    # This is OPPOSITE to what we might initially think. The regression
    # line through the cluster pixels gives us the direction ACROSS the neck,
    # which is exactly where we want to cut.
    cut_direction = tangent  # Cut along the cluster (across the neck)
    
    debug_info['regression_info'] = {
        'use_yx': use_yx,
        'slope': slope,
        'intercept': intercept,
        'tangent': tangent,
        'cut_direction': cut_direction,
        'residuals_yx': residuals_yx,
        'residuals_xy': residuals_xy,
    }
    
    if debug:
        print(f"    Regression: {'y=ax+b' if use_yx else 'x=cy+d'}, slope={slope:.3f}")
        print(f"    Cluster direction (across neck): ({tangent[0]:.3f}, {tangent[1]:.3f})")
        print(f"    Cut direction: ({cut_direction[0]:.3f}, {cut_direction[1]:.3f})")
    
    # Find extent of cluster along the TANGENT (to know cluster width)
    centroid = np.array(cluster['centroid'])  # (y, x)
    
    # Project all pixels onto the tangent direction
    pixel_coords = np.column_stack([ys, xs])
    centered = pixel_coords - centroid
    projections_tangent = np.dot(centered, tangent)
    
    cluster_width = projections_tangent.max() - projections_tangent.min()
    
    if debug:
        print(f"    Cluster width (along tangent): {cluster_width:.1f} pixels")
    
    # For single cluster cut, we extend from centroid in both directions
    # along the CUT direction (perpendicular to cluster/edge)
    # We need to extend far enough to EXIT the mask on both sides
    
    # Compute max diameter
    from scipy.ndimage import distance_transform_edt
    dist_transform = distance_transform_edt(mask)
    max_radius = dist_transform.max()
    max_diameter = 2 * max_radius
    
    # Extend generously to ensure we exit the mask
    # Use max_diameter to guarantee we reach both edges
    extension = max_diameter
    
    # Calculate endpoints along cut_direction
    start_point = centroid - cut_direction * extension
    end_point = centroid + cut_direction * extension
    
    if debug:
        print(f"    Max diameter: {max_diameter:.1f} pixels")
    
    # Create the cut line
    H, W = mask.shape
    line_y, line_x = line(int(round(start_point[0])), int(round(start_point[1])),
                          int(round(end_point[0])), int(round(end_point[1])))
    
    # Clip to image bounds
    valid = (line_y >= 0) & (line_y < H) & (line_x >= 0) & (line_x < W)
    line_y = line_y[valid]
    line_x = line_x[valid]
    
    if len(line_y) == 0:
        debug_info['rejection_reason'] = 'cut_line_outside_bounds'
        if debug:
            print(f"    Cut line outside image bounds")
        return None, debug_info
    
    # IMPORTANT: Trim cut line to only the portion INSIDE the mask
    # This gives us the actual neck width
    inside_mask = mask[line_y, line_x]
    
    if not inside_mask.any():
        debug_info['rejection_reason'] = 'cut_line_outside_mask'
        if debug:
            print(f"    Cut line does not intersect mask")
        return None, debug_info
    
    # Find continuous segment containing the centroid
    # (in case line enters/exits mask multiple times)
    distances_to_centroid = np.sqrt((line_y - centroid[0])**2 + (line_x - centroid[1])**2)
    closest_idx = np.argmin(distances_to_centroid)
    
    # Expand outward from closest point while inside mask
    start_idx = closest_idx
    end_idx = closest_idx
    
    while start_idx > 0 and inside_mask[start_idx - 1]:
        start_idx -= 1
    while end_idx < len(inside_mask) - 1 and inside_mask[end_idx + 1]:
        end_idx += 1
    
    # Trim to this segment
    line_y = line_y[start_idx:end_idx+1]
    line_x = line_x[start_idx:end_idx+1]
    
    cut_length = len(line_y)
    
    if cut_length < 3:
        debug_info['rejection_reason'] = 'cut_line_too_short'
        if debug:
            print(f"    Cut line too short after trimming ({cut_length} pixels)")
        return None, debug_info
    
    # Check if cut line is longer than max diameter (would indicate diagonal cut)
    if cut_length > max_diameter:
        debug_info['rejection_reason'] = 'cut_line_too_long'
        if debug:
            print(f"    REJECTED: trimmed cut length ({cut_length}) > max diameter ({max_diameter:.1f})")
        return None, debug_info
    
    debug_info['cut_endpoints'] = ((line_y[0], line_x[0]), (line_y[-1], line_x[-1]))
    debug_info['max_diameter'] = max_diameter
    debug_info['cut_length'] = cut_length
    
    if debug:
        print(f"    Cut line (trimmed to mask): {cut_length} pixels")
        print(f"    Cut line: ({line_y[0]}, {line_x[0]}) -> ({line_y[-1]}, {line_x[-1]})")
        print(f"    Cluster centroid: ({centroid[0]:.1f}, {centroid[1]:.1f})")
    
    # Create cut mask and dilate
    cut_mask = np.zeros_like(mask, dtype=bool)
    cut_mask[line_y, line_x] = True
    cut_dilated = binary_dilation(cut_mask, iterations=2)
    
    # Check if cutting creates valid split
    test_mask = mask & ~cut_dilated
    labeled, n_components = ndlabel(test_mask)
    
    if debug:
        print(f"    Components after cut: {n_components}")
        if n_components < 2:
            # Show more info about why split failed
            print(f"    Mask area: {mask.sum()} pixels")
            print(f"    Cut dilated area: {cut_dilated.sum()} pixels")
            print(f"    Remaining mask area: {test_mask.sum()} pixels")
    
    if n_components < 2:
        debug_info['rejection_reason'] = 'no_split_created'
        if debug:
            print(f"    Cut does not create split")
        return None, debug_info
    
    # Check area ratios
    total_area = mask.sum()
    areas = []
    for i in range(1, n_components + 1):
        areas.append((labeled == i).sum())
    
    area_ratios = [a / total_area for a in areas]
    debug_info['area_ratios'] = area_ratios
    
    # Check if at least two parts are significant
    significant = [r for r in area_ratios if r >= min_area_ratio]
    
    if debug:
        print(f"    Area ratios: {[f'{r:.3f}' for r in area_ratios]}")
        print(f"    Significant parts (>= {min_area_ratio}): {len(significant)}")
    
    if len(significant) < 2:
        debug_info['rejection_reason'] = 'split_parts_too_small'
        if debug:
            print(f"    Split parts too small")
        return None, debug_info
    
    debug_info['creates_valid_split'] = True
    
    cut_line = {
        'cluster': cluster,
        'method': 'single_cluster_regression',
        'line_y': line_y,
        'line_x': line_x,
        'cut_mask': cut_mask,
        'cut_dilated': cut_dilated,
        'n_components': n_components,
        'area_ratios': area_ratios,
        'regression_info': debug_info['regression_info'],
    }
    
    if debug:
        print(f"    >>> VALID CUT LINE FOUND (single cluster regression) <<<")
    
    return cut_line, debug_info


def detect_and_cut_necks(mask, neck_score, params, concavity_factor=None, debug=False, exclusion_mask=None):
    """
    Main function: detect neck clusters and create cutting line.
    
    Algorithm:
    1. Find clusters of high neck_score using soft membership weighting
    2. If 2+ clusters: Draw line between top 2 cluster centroids
    3. If 1 cluster: Use linear regression on cluster pixels to find cut direction
    4. Verify the cut creates a valid split
    
    Parameters:
        mask: Binary region mask
        neck_score: Neck score field
        params: Parameters dictionary
        concavity_factor: Concavity factor field (for validating long cuts)
        debug: Print debug information
        exclusion_mask: Optional mask of areas to ignore (e.g., previous cut locations)
    
    Returns:
        cut_line: Cut line info dict, or None if no valid cut
        clusters: List of detected clusters
        debug_info: Dictionary with all debug information
    """
    z_threshold_high = params.get('cut_max_z', 2.5)
    z_threshold_low_ratio = params.get('z_threshold_low_ratio', 0.5)  # Kept for compatibility
    min_cluster_size = params.get('min_cluster_size', 5)
    cluster_radius = params.get('cluster_radius', 3)
    max_aspect_ratio = params.get('cluster_max_aspect_ratio', 4.0)
    min_area_ratio = params.get('poly_min_area_ratio', 0.15)
    single_cluster_extend = params.get('single_cluster_extend', 0.3)
    sigma_scale = params.get('sigma_scale', 0.15)  # Soft membership spatial decay
    
    if debug:
        print(f"\n  === Cluster-Based Neck Detection (Soft Membership) ===")
        print(f"    Parameters: z_high={z_threshold_high}, sigma_scale={sigma_scale}, "
              f"min_cluster={min_cluster_size}, radius={cluster_radius}, max_aspect={max_aspect_ratio}")
    
    # Step 1: Find clusters using soft membership weighting
    clusters, labeled_clusters, cluster_debug = find_neck_clusters(
        neck_score, mask, z_threshold_high, min_cluster_size, cluster_radius, 
        max_aspect_ratio, z_threshold_low_ratio, sigma_scale, debug,
        exclusion_mask=exclusion_mask
    )
    
    cut_line = None
    cut_debug = {'n_clusters': len(clusters)}
    
    # Step 2: Create cut line based on number of clusters
    if len(clusters) >= 2:
        # Two or more clusters: connect top 2 centroids
        if debug:
            print(f"\n  Using two-cluster method (connecting centroids)...")
        cut_line, cut_debug = find_neck_cut_line(
            clusters, mask, min_area_ratio, 
            neck_score=neck_score,
            concavity_factor=concavity_factor,
            debug=debug
        )
        cut_debug['method'] = 'two_cluster'
        
    elif len(clusters) == 1:
        # Single cluster: use erosion-based method
        if debug:
            print(f"\n  Using single-cluster method (erosion-based)...")
        cut_line, cut_debug = find_cut_line_single_cluster(
            clusters[0], mask, 
            min_area_ratio=min_area_ratio, 
            debug=debug
        )
        cut_debug['method'] = 'single_cluster_erosion'
    else:
        if debug:
            print(f"\n  No valid clusters found")
        cut_debug['rejection_reason'] = 'no_clusters'
        cut_debug['method'] = None
    
    debug_info = {
        'cluster_debug': cluster_debug,
        'cut_debug': cut_debug,
        'clusters': clusters,
        'labeled_clusters': labeled_clusters,
    }
    
    return cut_line, clusters, debug_info


def split_region_cluster_based(mask, params, debug=False, image=None, exclusion_mask=None):
    """
    Split a region using cluster-based neck detection.
    
    Algorithm:
    1. Compute stress field and neck_score
    2. Find clusters of high neck_score (true necks are dense clusters)
    3. Take the two most prominent clusters
    4. Draw cut line between their centroids
    5. Apply cut and return split parts
    
    Parameters:
        mask: Binary mask of the region (should already be smoothed)
        params: Parameters dictionary
        debug: Print debug information
        image: Optional image for debug plotting
        exclusion_mask: Optional mask of areas to ignore (e.g., previous cut locations)
    
    Returns:
        labeled: Label array with split bodies (0=background, 1,2,...=parts)
        n_parts: Number of parts after split
        debug_info: Dictionary with debug information
    """
    from scipy.ndimage import label as ndlabel, binary_dilation
    
    H, W = mask.shape
    original_mask = mask.copy()
    
    debug_info = {
        'original_mask': original_mask.copy(),
        'stress': None,
        'neck_score': None,
        'clusters': [],
        'cut_line': None,
        'iterations': [],
        'exclusion_mask': exclusion_mask,
    }
    
    # Step 1: Compute stress and neck_score
    w = solve_poisson(mask)
    stress = compute_stress(w, mask)
    
    debug_info['stress'] = stress.copy()
    
    # Compute neck_score
    neck_score, z_scores, stats, neck_debug = compute_neck_score_z(stress, mask, sigma_smooth=2)
    
    debug_info['neck_score'] = neck_score.copy()
    debug_info['z_scores'] = z_scores.copy()
    debug_info['stats'] = stats
    
    if debug:
        print(f"  Neck score stats: peak/mean={stats['peak_to_mean']:.2f}, max_z={stats['max_z']:.2f}")
    
    # Store iteration info for compatibility with existing visualization
    debug_info['iterations'].append({
        'iteration': 1,
        'working_mask': mask.copy(),
        'stress': stress.copy(),
        'neck_score': neck_score.copy(),
        'z_scores': z_scores.copy(),
        'stats': stats,
    })
    
    # Get concavity_factor from neck_debug for long cut validation
    concavity_factor = neck_debug.get('concavity_factor')
    
    # Step 2: Detect clusters and find cut line
    cut_line, clusters, cluster_debug = detect_and_cut_necks(
        mask, neck_score, params, 
        concavity_factor=concavity_factor,
        debug=debug,
        exclusion_mask=exclusion_mask
    )
    
    debug_info['clusters'] = clusters
    debug_info['cluster_debug'] = cluster_debug
    debug_info['cut_line'] = cut_line
    
    # Step 3: Apply cut if valid
    if cut_line is None:
        if debug:
            print(f"  No valid cut line found")
        # Return original mask as single part
        labeled = np.zeros_like(mask, dtype=int)
        labeled[mask] = 1
        return labeled, 1, debug_info
    
    # Apply the cut
    cut_dilated = cut_line['cut_dilated']
    cut_mask_region = mask & ~cut_dilated  # Pixels NOT on the cut line
    
    # Label the resulting parts (without cut pixels)
    labeled, n_parts = ndlabel(cut_mask_region)
    
    # Filter out tiny fragments
    # Use smaller threshold for small regions
    total_area = mask.sum()
    min_part_size = min(50, int(total_area * 0.1))  # At least 10% of region or 50px, whichever is smaller
    min_part_size = max(min_part_size, 20)  # But at least 20 pixels
    
    valid_labels = []
    for i in range(1, n_parts + 1):
        part_size = (labeled == i).sum()
        if part_size >= min_part_size:
            valid_labels.append(i)
    
    if debug:
        print(f"  After cutting: {n_parts} components, {len(valid_labels)} valid (>={min_part_size} pixels)")
    
    if len(valid_labels) < 2:
        if debug:
            print(f"  Cut did not create valid split")
        # Return original mask as single part
        labeled = np.zeros_like(mask, dtype=int)
        labeled[mask] = 1
        return labeled, 1, debug_info
    
    # Relabel to consecutive integers
    new_labeled = np.zeros_like(labeled)
    for new_id, old_id in enumerate(valid_labels, start=1):
        new_labeled[labeled == old_id] = new_id
    
    # Assign cut pixels to nearest body using distance transform
    # This ensures no pixels are lost - each cut pixel goes to nearest body
    cut_pixels = mask & cut_dilated  # Pixels ON the cut line
    n_cut_pixels = cut_pixels.sum()
    
    if n_cut_pixels > 0:
        from scipy.ndimage import distance_transform_edt
        
        # For each label, compute distance transform from that label's boundary
        # Then assign each cut pixel to the label with minimum distance
        n_labels = len(valid_labels)
        
        # Create distance maps for each label
        distance_maps = []
        for label_id in range(1, n_labels + 1):
            label_mask = (new_labeled == label_id)
            # Distance transform gives distance to nearest True pixel
            # We want distance FROM the label, so use the label mask
            dist = distance_transform_edt(~label_mask)
            distance_maps.append(dist)
        
        # Stack into array for easy comparison
        distance_stack = np.stack(distance_maps, axis=0)  # Shape: (n_labels, H, W)
        
        # For each cut pixel, find which label has minimum distance
        cut_ys, cut_xs = np.where(cut_pixels)
        
        for cy, cx in zip(cut_ys, cut_xs):
            # Get distances to each label at this pixel
            distances_at_pixel = distance_stack[:, cy, cx]
            # Find label with minimum distance (add 1 because labels are 1-indexed)
            nearest_label = np.argmin(distances_at_pixel) + 1
            new_labeled[cy, cx] = nearest_label
        
        if debug:
            # Count how many went to each label
            for label_id in range(1, n_labels + 1):
                count = ((new_labeled == label_id) & cut_pixels).sum()
                print(f"  Assigned to body {label_id}: {count} cut pixels")
            print(f"  Total assigned: {n_cut_pixels} cut pixels")
    
    # Store cut line info (handle both single and two-cluster methods)
    cut_line_info = {
        'line_y': cut_line['line_y'],
        'line_x': cut_line['line_x'],
        'mask': cut_line['cut_mask'],
        'method': cut_line.get('method', 'two_cluster'),
    }
    
    # Add cluster info based on method
    if 'cluster_A' in cut_line:
        cut_line_info['cluster_A'] = cut_line['cluster_A']
        cut_line_info['cluster_B'] = cut_line['cluster_B']
    elif 'cluster' in cut_line:
        cut_line_info['cluster'] = cut_line['cluster']
        cut_line_info['regression_info'] = cut_line.get('regression_info')
    
    debug_info['cut_lines'] = [cut_line_info]
    
    if debug:
        print(f"  → SUCCESS! Split into {len(valid_labels)} parts")
    
    return new_labeled, len(valid_labels), debug_info


def get_chunk_info(labeled_chunks, chunk_id):
    """Get centroid and pixels of a chunk."""
    ys, xs = np.where(labeled_chunks == chunk_id)
    if len(ys) == 0:
        return None
    return {
        'id': chunk_id,
        'centroid': (ys.mean(), xs.mean()),
        'pixels': list(zip(ys, xs)),
        'size': len(ys),
    }


def merge_nearby_chunks(chunks, mask, distance_threshold_ratio=0.10):
    """
    Merge chunks that are too close to each other, preserving at least 2 chunks.
    
    Algorithm:
    1. Compute all pairwise distances
    2. Sort by distance (closest first)
    3. Merge closest pair if result still has >= 2 chunks
    4. Repeat until no more merges possible or only 2 chunks remain
    
    Returns merged list of chunks and the normalized distance of last merge.
    """
    if len(chunks) <= 2:
        return chunks  # Already 2 or fewer, no merging needed
    
    # Compute bounding box diagonal for normalization
    ys, xs = np.where(mask)
    bbox_height = ys.max() - ys.min()
    bbox_width = xs.max() - xs.min()
    diagonal = np.sqrt(bbox_height**2 + bbox_width**2)
    
    # Work with a copy
    current_chunks = list(chunks)
    
    while len(current_chunks) > 2:
        # Find closest pair
        min_dist = float('inf')
        min_norm_dist = float('inf')
        merge_pair = None
        
        for i in range(len(current_chunks)):
            for j in range(i + 1, len(current_chunks)):
                c1 = current_chunks[i]['centroid']
                c2 = current_chunks[j]['centroid']
                dist = np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
                norm_dist = dist / diagonal
                
                if norm_dist < min_norm_dist:
                    min_norm_dist = norm_dist
                    min_dist = dist
                    merge_pair = (i, j)
        
        # Check if closest pair is within threshold
        if min_norm_dist > distance_threshold_ratio:
            break  # No more pairs close enough to merge
        
        # Merge the closest pair
        i, j = merge_pair
        chunk_i = current_chunks[i]
        chunk_j = current_chunks[j]
        
        # Combine pixels
        all_pixels = list(chunk_i['pixels']) + list(chunk_j['pixels'])
        all_pixels_arr = np.array(all_pixels)
        
        # Track merged IDs
        merged_from_i = chunk_i.get('merged_from', [chunk_i['id']])
        merged_from_j = chunk_j.get('merged_from', [chunk_j['id']])
        
        merged_chunk = {
            'id': chunk_i['id'],  # Keep first ID
            'centroid': (all_pixels_arr[:, 0].mean(), all_pixels_arr[:, 1].mean()),
            'pixels': [tuple(p) for p in all_pixels],
            'size': len(all_pixels),
            'merged_from': merged_from_i + merged_from_j,
            'last_merge_dist': min_norm_dist,
        }
        
        # Remove old chunks and add merged one
        # Remove j first (higher index) to avoid index shift issues
        current_chunks.pop(j)
        current_chunks.pop(i)
        current_chunks.append(merged_chunk)
    
    # Re-number the chunks
    for idx, chunk in enumerate(current_chunks, 1):
        chunk['id'] = idx
    
    return current_chunks


def find_chunk_lineage(chunks_A, chunks_B, max_distance=15):
    """
    Find which B chunks follow which A chunks.
    
    Returns list of (A_id, B_id, direction_vector) tuples.
    """
    lineages = []
    
    for chunk_A in chunks_A:
        if chunk_A is None:
            continue
        cy_a, cx_a = chunk_A['centroid']
        
        # Find nearest B chunk
        best_dist = float('inf')
        best_B = None
        
        for chunk_B in chunks_B:
            if chunk_B is None:
                continue
            cy_b, cx_b = chunk_B['centroid']
            
            dist = np.sqrt((cy_b - cy_a)**2 + (cx_b - cx_a)**2)
            if dist < best_dist and dist < max_distance:
                best_dist = dist
                best_B = chunk_B
        
        if best_B is not None:
            # Direction vector from A to B
            cy_b, cx_b = best_B['centroid']
            dy = cy_b - cy_a
            dx = cx_b - cx_a
            length = np.sqrt(dy**2 + dx**2)
            if length > 0:
                direction = (dy / length, dx / length)
            else:
                direction = (0, 0)
            
            lineages.append({
                'A': chunk_A,
                'B': best_B,
                'direction': direction,
                'angle': np.arctan2(dy, dx),  # Angle in radians
                'midpoint': ((cy_a + cy_b) / 2, (cx_a + cx_b) / 2),
            })
    
    return lineages


def find_opposing_pairs(lineages, angle_threshold=np.pi/3, max_perpendicular_dist=20):
    """
    Find pairs of lineages that are face-to-face (coincident, not just parallel).
    
    Two lineages are opposing if:
    1. Their angles differ by ~180° (pointing toward each other)
    2. They are roughly collinear (not parallel but offset)
    
    To check collinearity: 
    - Project the midpoint of lineage2 onto the line defined by lineage1
    - The perpendicular distance should be small
    """
    pairs = []
    used = set()
    
    for i, lin1 in enumerate(lineages):
        if i in used:
            continue
        
        # Get line1 properties
        tip1 = np.array(lin1['B']['centroid'])  # End point of lineage 1
        dir1 = np.array(lin1['direction'])       # Direction vector
        angle1 = lin1['angle']
        
        best_match = None
        best_score = float('inf')
        
        for j, lin2 in enumerate(lineages):
            if j <= i or j in used:
                continue
            
            tip2 = np.array(lin2['B']['centroid'])
            dir2 = np.array(lin2['direction'])
            angle2 = lin2['angle']
            
            # Check 1: Angles should be approximately opposite (differ by π)
            angle_diff = abs(angle1 - angle2)
            angle_diff = min(angle_diff, 2*np.pi - angle_diff)
            opposite_diff = abs(angle_diff - np.pi)
            
            if opposite_diff > angle_threshold:
                continue
            
            # Check 2: They should point TOWARD each other
            # Vector from tip1 to tip2
            tip1_to_tip2 = tip2 - tip1
            dist_between = np.linalg.norm(tip1_to_tip2)
            
            if dist_between < 1:
                continue
            
            tip1_to_tip2_normalized = tip1_to_tip2 / dist_between
            
            # dir1 should point toward tip2 (positive dot product)
            dot1 = np.dot(dir1, tip1_to_tip2_normalized)
            # dir2 should point toward tip1 (negative dot product with tip1_to_tip2)
            dot2 = np.dot(dir2, tip1_to_tip2_normalized)
            
            # Both should be pointing toward each other
            if dot1 < 0.3 or dot2 > -0.3:
                continue  # Not pointing toward each other
            
            # Check 3: Perpendicular distance (collinearity check)
            # Project tip2 onto the line defined by tip1 + t*dir1
            # Perpendicular distance = |tip1_to_tip2 - (tip1_to_tip2 · dir1) * dir1|
            projection_length = np.dot(tip1_to_tip2, dir1)
            projection = projection_length * dir1
            perpendicular = tip1_to_tip2 - projection
            perp_dist = np.linalg.norm(perpendicular)
            
            if perp_dist > max_perpendicular_dist:
                continue  # Lines are parallel but offset too much
            
            # Score: combination of angle difference, perpendicular distance, and alignment
            score = opposite_diff + perp_dist / 50 + (1 - dot1) + (1 + dot2)
            
            if score < best_score:
                best_score = score
                best_match = j
        
        if best_match is not None:
            pairs.append((i, best_match))
            used.add(i)
            used.add(best_match)
    
    return pairs


def extend_line_to_boundary(start_point, direction, mask, max_length=200):
    """
    Extend a line from start_point in the given direction until it leaves the mask.
    
    Returns the endpoint.
    """
    H, W = mask.shape
    y, x = start_point
    dy, dx = direction
    
    # Extend in the given direction
    for t in range(1, max_length):
        ny = int(y + t * dy)
        nx = int(x + t * dx)
        
        if ny < 0 or ny >= H or nx < 0 or nx >= W:
            return (int(y + (t-1) * dy), int(x + (t-1) * dx))
        
        if not mask[ny, nx]:
            return (ny, nx)
    
    return (int(y + max_length * dy), int(x + max_length * dx))


def create_cut_line_from_pair(lin1, lin2, mask):
    """
    Create a cut line connecting two opposing lineages.
    
    The cut line goes from the extended end of lin1 through both midpoints
    to the extended end of lin2.
    """
    H, W = mask.shape
    
    # Get the B chunk centroids (the "tips" of the erosion paths)
    tip1 = lin1['B']['centroid']
    tip2 = lin2['B']['centroid']
    
    # Direction from tip1 toward tip2
    dy = tip2[0] - tip1[0]
    dx = tip2[1] - tip1[1]
    length = np.sqrt(dy**2 + dx**2)
    
    if length < 5:
        return None, None
    
    # Extend beyond both tips to reach the boundary
    direction = (dy / length, dx / length)
    
    # Extend from tip1 backward (opposite direction)
    end1 = extend_line_to_boundary(tip1, (-direction[0], -direction[1]), mask)
    
    # Extend from tip2 forward
    end2 = extend_line_to_boundary(tip2, direction, mask)
    
    # Draw line from end1 to end2
    rr, cc = line(int(end1[0]), int(end1[1]), int(end2[0]), int(end2[1]))
    
    cut_mask = np.zeros((H, W), dtype=bool)
    valid = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < W)
    cut_mask[rr[valid], cc[valid]] = True
    cut_mask = cut_mask & mask
    
    return cut_mask, (end1, end2)


def split_region_chunk_tracking(mask, params, debug=False, image=None):
    """
    Split a region using chunk tracking with line extension.
    
    NOTE: FFT smoothing is now done globally before this function is called.
    The input mask should already be smoothed.
    
    Algorithm:
    1. Iteration 1: Find hot chunks (A1, A2, ...)
    2. Erode hot chunks, bend again
    3. Iteration 2: Find new hot chunks (B1, B2, ...)
    4. Track lineage: which B follows which A
    5. Find opposing pairs of lineages
    6. Extend lines to connect opposing pairs → cut lines
    7. Apply all cut lines
    
    Returns:
        labeled: Label array with split bodies
        n_parts: Number of parts after split
        debug_info: Dictionary with debug information
    """
    cut_max_z = params.get('cut_max_z', 2.5)
    cut_peak_to_mean = params.get('cut_peak_to_mean', 2.0)
    chunk_merge_threshold = params.get('chunk_merge_threshold', 0.10)
    use_neck_score = params.get('use_neck_score', True)  # Use neck_score to suppress edge artifacts
    
    H, W = mask.shape
    original_mask = mask.copy()
    working_mask = mask.copy()  # Already smoothed globally
    
    debug_info = {
        'original_mask': original_mask.copy(),
        'chunks_A': [],
        'chunks_B': [],
        'lineages': [],
        'pairs': [],
        'cut_lines': [],
        'iterations': [],  # Store stress field info for each iteration
    }
    
    # For debug plotting
    if debug:
        ys, xs = np.where(original_mask)
        margin = 10
        y0, y1 = max(0, ys.min() - margin), min(H, ys.max() + margin)
        x0, x1 = max(0, xs.min() - margin), min(W, xs.max() + margin)
    
    # ========== ITERATION 1: Find first set of chunks ==========
    w = solve_poisson(working_mask)
    stress = compute_stress(w, working_mask)
    stress_smooth = gaussian(stress, sigma=1)
    
    # Use neck_score to suppress edge artifacts
    if use_neck_score:
        neck_score, z, stats, edge_debug = compute_neck_score_z(stress, working_mask, sigma_smooth=1)
        detection_field = neck_score  # Use neck_score for hot pixel detection
        if debug:
            print(f"  Iteration 1 (neck_score): pm={stats['peak_to_mean']:.2f}, mz={stats['max_z']:.2f}")
    else:
        z, stats = compute_z_scores(stress_smooth, working_mask)
        detection_field = stress_smooth  # Use raw stress
        edge_debug = None
        if debug:
            print(f"  Iteration 1 (raw stress): pm={stats['peak_to_mean']:.2f}, mz={stats['max_z']:.2f}")
    
    # Store iteration 1 info
    debug_info['iterations'].append({
        'iteration': 1,
        'working_mask': working_mask.copy(),
        'stress': stress_smooth.copy(),
        'neck_score': neck_score.copy() if use_neck_score else None,
        'z_scores': z.copy(),
        'stats': stats.copy(),
        'hot_mask': None,  # Will be set below
        'chunks': [],
        'edge_debug': edge_debug,
    })
    
    if stats.get('max_z', 0) < cut_max_z or stats.get('peak_to_mean', 0) < cut_peak_to_mean:
        if debug:
            print(f"  → No significant stress concentration")
        result = np.zeros_like(mask, dtype=int)
        result[original_mask] = 1
        return result, 1, debug_info
    
    # Find hot chunks A (raw, before merging)
    hot_mask_A = (z > cut_max_z) & working_mask
    labeled_A, n_chunks_A = ndlabel(hot_mask_A)
    
    chunks_A_raw = []
    for i in range(1, n_chunks_A + 1):
        chunk = get_chunk_info(labeled_A, i)
        if chunk is not None and chunk['size'] >= 3:  # Min chunk size
            chunks_A_raw.append(chunk)
    
    # Update iteration 1 with hot mask and chunks
    debug_info['iterations'][0]['hot_mask'] = hot_mask_A.copy()
    debug_info['iterations'][0]['chunks'] = chunks_A_raw.copy()
    
    # ========== EARLY SPLIT CHECK ==========
    # For cells with small shared boundary: eroding the hot area might already split them
    # Check if removing hot pixels creates 2+ components
    eroded_mask = original_mask & ~hot_mask_A
    labeled_eroded, n_components = ndlabel(eroded_mask)
    
    # Count valid components (>50 pixels)
    valid_components = []
    for i in range(1, n_components + 1):
        comp_size = (labeled_eroded == i).sum()
        if comp_size > 50:
            valid_components.append(i)
    
    if len(valid_components) >= 2:
        if debug:
            print(f"  → EARLY SPLIT! Eroding hot area created {len(valid_components)} components")
        
        # Build result by assigning eroded pixels + restoring hot pixels to nearest component
        final_result = np.zeros_like(mask, dtype=int)
        for new_id, old_id in enumerate(valid_components, 1):
            final_result[labeled_eroded == old_id] = new_id
        
        # Assign hot pixels to nearest component
        hot_pixels = list(zip(*np.where(hot_mask_A)))
        for (y, x) in hot_pixels:
            min_dist = float('inf')
            nearest_label = 1
            for new_id, old_id in enumerate(valid_components, 1):
                body_ys, body_xs = np.where(labeled_eroded == old_id)
                if len(body_ys) == 0:
                    continue
                dists = np.sqrt((body_ys - y)**2 + (body_xs - x)**2)
                min_body_dist = dists.min()
                if min_body_dist < min_dist:
                    min_dist = min_body_dist
                    nearest_label = new_id
            final_result[y, x] = nearest_label
        
        debug_info['early_split'] = True
        debug_info['hot_mask'] = hot_mask_A
        
        if debug:
            # Debug plot for early split
            ys, xs = np.where(original_mask)
            margin = 10
            y0, y1 = max(0, ys.min() - margin), min(H, ys.max() + margin)
            x0, x1 = max(0, xs.min() - margin), min(W, xs.max() + margin)
            
            fig, axes = plt.subplots(1, 4, figsize=(20, 5))
            
            # Panel 1: Original with hot area
            axes[0].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
            if image is not None:
                axes[0].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
            hot_vis = np.zeros((y1-y0, x1-x0, 4))
            hot_vis[hot_mask_A[y0:y1, x0:x1], :] = [1, 0, 0, 0.7]
            axes[0].imshow(hot_vis)
            axes[0].set_title(f'Hot Area (stress > {cut_max_z})\n{hot_mask_A.sum()} pixels')
            axes[0].axis('off')
            
            # Panel 2: After erosion
            axes[1].imshow(eroded_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.7)
            if image is not None:
                axes[1].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
            axes[1].set_title(f'After Erosion\n{len(valid_components)} components')
            axes[1].axis('off')
            
            # Panel 3: Final result
            axes[2].imshow(final_result[y0:y1, x0:x1], cmap='nipy_spectral')
            part_sizes = [(final_result == i).sum() for i in range(1, len(valid_components) + 1)]
            axes[2].set_title(f'Final: {len(valid_components)} parts\nSizes: {part_sizes}')
            axes[2].axis('off')
            
            # Panel 4: Overlay
            if image is not None:
                axes[3].imshow(image[y0:y1, x0:x1], cmap='gray')
                for i in range(1, len(valid_components) + 1):
                    part_mask = (final_result == i)
                    if part_mask.sum() > 0:
                        part_boundary = part_mask ^ binary_erosion(part_mask)
                        color_overlay = np.zeros((y1-y0, x1-x0, 4))
                        color = plt.cm.tab10(i / 10)
                        color_overlay[part_boundary[y0:y1, x0:x1], :] = [color[0], color[1], color[2], 0.8]
                        axes[3].imshow(color_overlay)
            axes[3].set_title('Result overlay')
            axes[3].axis('off')
            
            plt.suptitle('EARLY SPLIT: Small shared boundary detected')
            plt.tight_layout()
            plt.show()
        
        return final_result, len(valid_components), debug_info
    
    if debug:
        print(f"  No early split (eroding gave {len(valid_components)} valid components)")
    
    # ========== Continue with normal chunk tracking ==========
    # Merge nearby chunks (normalized by bounding box)
    chunks_A = merge_nearby_chunks(chunks_A_raw, original_mask, distance_threshold_ratio=chunk_merge_threshold)
    
    if debug:
        if len(chunks_A_raw) != len(chunks_A):
            print(f"  Found {len(chunks_A_raw)} raw chunks → merged to {len(chunks_A)} chunks")
            for chunk in chunks_A:
                if 'merged_from' in chunk and len(chunk['merged_from']) > 1:
                    print(f"    Chunk {chunk['id']}: merged from {chunk['merged_from']}")
        else:
            print(f"  Found {len(chunks_A)} chunks in iteration 1")
    
    if len(chunks_A) < 2:
        if debug:
            print(f"  → Not enough chunks for cutting")
            
            # Plot debug info
            ys, xs = np.where(original_mask)
            margin = 10
            y0, y1 = max(0, ys.min() - margin), min(H, ys.max() + margin)
            x0, x1 = max(0, xs.min() - margin), min(W, xs.max() + margin)
            
            fig, axes = plt.subplots(1, 4, figsize=(20, 5))
            
            # Panel 1: Original mask
            axes[0].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
            if image is not None:
                axes[0].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
            axes[0].set_title(f'Original Region\n({original_mask.sum()} pixels)')
            axes[0].axis('off')
            
            # Panel 2: Stress field
            stress_display = np.zeros_like(stress_smooth)
            stress_display[working_mask] = stress_smooth[working_mask]
            axes[1].imshow(stress_display[y0:y1, x0:x1], cmap='hot')
            axes[1].set_title(f'Stress Field\npm={stats["peak_to_mean"]:.2f}, mz={stats["max_z"]:.2f}')
            axes[1].axis('off')
            
            # Panel 3: Raw chunks (before merging)
            axes[2].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.3)
            if image is not None:
                axes[2].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
            # Show hot mask
            hot_vis = np.zeros((y1-y0, x1-x0, 4))
            hot_vis[hot_mask_A[y0:y1, x0:x1], :] = [1, 0, 0, 0.6]
            axes[2].imshow(hot_vis)
            # Show raw chunk centroids
            for chunk in chunks_A_raw:
                cy, cx = chunk['centroid']
                axes[2].plot(cx - x0, cy - y0, 'yo', markersize=10)
                axes[2].annotate(f"A{chunk['id']}", (cx - x0, cy - y0), color='yellow', fontsize=10)
            axes[2].set_title(f'Raw Chunks: {len(chunks_A_raw)}\n(before merging)')
            axes[2].axis('off')
            
            # Panel 4: After merging
            axes[3].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.3)
            if image is not None:
                axes[3].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
            for chunk in chunks_A:
                cy, cx = chunk['centroid']
                axes[3].plot(cx - x0, cy - y0, 'ro', markersize=12)
                label = f"M{chunk['id']}"
                if 'merged_from' in chunk:
                    label += f"\n({chunk['merged_from']})"
                axes[3].annotate(label, (cx - x0 + 3, cy - y0), color='red', fontsize=9)
            axes[3].set_title(f'After Merging: {len(chunks_A)}\n(threshold={params.get("chunk_merge_threshold", 0.15):.2f})')
            axes[3].axis('off')
            
            plt.tight_layout()
            plt.show()
        
        result = np.zeros_like(mask, dtype=int)
        result[original_mask] = 1
        return result, 1, debug_info
    
    debug_info['chunks_A'] = chunks_A
    
    # ========== SPECIAL CASE: Exactly 2 chunks in iteration 1 ==========
    # Connect them directly - no need for iteration 2
    if len(chunks_A) == 2:
        if debug:
            print(f"  → Exactly 2 chunks found! Direct connection (no iteration 2 needed)")
        
        c1 = chunks_A[0]['centroid']  # (y, x)
        c2 = chunks_A[1]['centroid']  # (y, x)
        
        # Simple line between the two centroids (no extension)
        rr, cc = line(int(c1[0]), int(c1[1]), int(c2[0]), int(c2[1]))
        
        cut_mask = np.zeros((H, W), dtype=bool)
        valid = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < W)
        cut_mask[rr[valid], cc[valid]] = True
        cut_mask = cut_mask & original_mask  # Only within mask
        
        debug_info['cut_lines'] = [{'mask': cut_mask, 'centroids': (c1, c2)}]
        
        if debug:
            print(f"  Centroids: ({c1[0]:.0f},{c1[1]:.0f}) and ({c2[0]:.0f},{c2[1]:.0f})")
            print(f"  Cut pixels: {cut_mask.sum()}")
        
        # Apply cut
        cut_dilated = binary_dilation(cut_mask, iterations=1)
        result_mask = original_mask & ~cut_dilated
        
        labeled_result, n_parts = ndlabel(result_mask)
        
        # Filter tiny fragments
        valid_parts = []
        for i in range(1, n_parts + 1):
            if (labeled_result == i).sum() > 50:
                valid_parts.append(i)
        
        if debug:
            print(f"  After cutting: {n_parts} components, {len(valid_parts)} valid (>50 pixels)")
        
        if len(valid_parts) >= 2:
            # Build final result
            final_result = np.zeros_like(mask, dtype=int)
            for new_id, old_id in enumerate(valid_parts, 1):
                final_result[labeled_result == old_id] = new_id
            
            # Assign cut line pixels to nearest body
            cut_pixels = list(zip(*np.where(cut_dilated & original_mask)))
            for (y, x) in cut_pixels:
                min_dist = float('inf')
                nearest_label = 1
                for new_id, old_id in enumerate(valid_parts, 1):
                    body_ys, body_xs = np.where(labeled_result == old_id)
                    if len(body_ys) == 0:
                        continue
                    dists = np.sqrt((body_ys - y)**2 + (body_xs - x)**2)
                    min_body_dist = dists.min()
                    if min_body_dist < min_dist:
                        min_dist = min_body_dist
                        nearest_label = new_id
                final_result[y, x] = nearest_label
            
            if debug:
                print(f"  → SUCCESS! Split into {len(valid_parts)} parts (direct connection)")
                
                # Debug plot for 2-chunk case
                ys, xs = np.where(original_mask)
                margin = 10
                y0, y1 = max(0, ys.min() - margin), min(H, ys.max() + margin)
                x0, x1 = max(0, xs.min() - margin), min(W, xs.max() + margin)
                
                fig, axes = plt.subplots(1, 4, figsize=(20, 5))
                
                # Panel 1: Original with 2 chunks
                axes[0].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
                if image is not None:
                    axes[0].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
                for chunk in chunks_A:
                    cy, cx = chunk['centroid']
                    axes[0].plot(cx - x0, cy - y0, 'ro', markersize=12)
                    axes[0].annotate(f"C{chunk['id']}", (cx - x0 + 3, cy - y0), color='red', fontsize=12)
                axes[0].set_title(f'2 Chunks Found\n(Direct connection)')
                axes[0].axis('off')
                
                # Panel 2: Cut line (extended)
                axes[1].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.3)
                if image is not None:
                    axes[1].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
                cut_vis = np.zeros((y1-y0, x1-x0, 4))
                cut_vis[cut_mask[y0:y1, x0:x1], :] = [1, 0, 0, 0.8]
                axes[1].imshow(cut_vis)
                # Show centroids only (not extended line endpoints)
                axes[1].plot(c1[1] - x0, c1[0] - y0, 'yo', markersize=8)
                axes[1].plot(c2[1] - x0, c2[0] - y0, 'yo', markersize=8)
                axes[1].set_title(f'Extended Cut Line\n({cut_mask.sum()} pixels)')
                axes[1].axis('off')
                
                # Panel 3: Final result
                axes[2].imshow(final_result[y0:y1, x0:x1], cmap='nipy_spectral')
                part_sizes = [(final_result == i).sum() for i in range(1, len(valid_parts) + 1)]
                axes[2].set_title(f'Final: {len(valid_parts)} parts\nSizes: {part_sizes}')
                axes[2].axis('off')
                
                # Panel 4: Overlay
                if image is not None:
                    axes[3].imshow(image[y0:y1, x0:x1], cmap='gray')
                    for i in range(1, len(valid_parts) + 1):
                        part_mask = (final_result == i)
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
            
            return final_result, len(valid_parts), debug_info
        else:
            if debug:
                print(f"  → Cut didn't create valid split, continuing to iteration 2...")
                
                # Debug plot to see why cut failed
                ys, xs = np.where(original_mask)
                margin = 10
                y0, y1 = max(0, ys.min() - margin), min(H, ys.max() + margin)
                x0, x1 = max(0, xs.min() - margin), min(W, xs.max() + margin)
                
                fig, axes = plt.subplots(1, 4, figsize=(20, 5))
                
                # Panel 1: Original with 2 chunks and their pixels
                axes[0].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
                if image is not None:
                    axes[0].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
                # Show chunk pixels
                for i, chunk in enumerate(chunks_A):
                    chunk_mask = np.zeros_like(original_mask, dtype=bool)
                    for (py, px) in chunk['pixels']:
                        chunk_mask[py, px] = True
                    color = [[1, 0, 0, 0.5], [0, 1, 0, 0.5]][i % 2]
                    chunk_vis = np.zeros((y1-y0, x1-x0, 4))
                    chunk_vis[chunk_mask[y0:y1, x0:x1], :] = color
                    axes[0].imshow(chunk_vis)
                    cy, cx = chunk['centroid']
                    axes[0].plot(cx - x0, cy - y0, 'ko', markersize=12)
                    axes[0].annotate(f"C{chunk['id']}", (cx - x0 + 3, cy - y0), color='black', fontsize=12, fontweight='bold')
                axes[0].set_title(f'2 Chunks\nRed & Green = chunk pixels')
                axes[0].axis('off')
                
                # Panel 2: Cut line on mask
                axes[1].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
                if image is not None:
                    axes[1].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
                # Show cut line
                cut_vis = np.zeros((y1-y0, x1-x0, 4))
                cut_vis[cut_mask[y0:y1, x0:x1], :] = [1, 0, 0, 0.8]
                axes[1].imshow(cut_vis)
                # Show dilated cut
                cut_dilated_vis = np.zeros((y1-y0, x1-x0, 4))
                cut_dilated_vis[cut_dilated[y0:y1, x0:x1], :] = [1, 1, 0, 0.4]
                axes[1].imshow(cut_dilated_vis)
                axes[1].plot([c1[1] - x0, c2[1] - x0], [c1[0] - y0, c2[0] - y0], 'r-', linewidth=2)
                axes[1].plot(c1[1] - x0, c1[0] - y0, 'ro', markersize=10)
                axes[1].plot(c2[1] - x0, c2[0] - y0, 'ro', markersize=10)
                axes[1].set_title(f'Cut Line (red) + Dilated (yellow)\nLine pixels: {cut_mask.sum()}')
                axes[1].axis('off')
                
                # Panel 3: After removing cut line
                axes[2].imshow(result_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.7)
                if image is not None:
                    axes[2].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
                axes[2].set_title(f'After Cut Removal\nRemaining: {result_mask.sum()} pixels')
                axes[2].axis('off')
                
                # Panel 4: Connected components
                axes[3].imshow(labeled_result[y0:y1, x0:x1], cmap='nipy_spectral')
                comp_sizes = [(labeled_result == i).sum() for i in range(1, n_parts + 1)]
                axes[3].set_title(f'Components: {n_parts}\nSizes: {comp_sizes}\nValid (>50): {len(valid_parts)}')
                axes[3].axis('off')
                
                plt.tight_layout()
                plt.show()
    
    # ========== Continue with iteration 2 for 3+ chunks ==========
    # Erode chunks A
    for chunk in chunks_A:
        for (y, x) in chunk['pixels']:
            working_mask[y, x] = False
    
    # ========== ITERATION 2: Find second set of chunks ==========
    w = solve_poisson(working_mask)
    stress = compute_stress(w, working_mask)
    stress_smooth = gaussian(stress, sigma=1)
    
    # Use neck_score to suppress edge artifacts
    if use_neck_score:
        neck_score, z, stats, edge_debug = compute_neck_score_z(stress, working_mask, sigma_smooth=1)
        if debug:
            print(f"  Iteration 2 (neck_score): pm={stats['peak_to_mean']:.2f}, mz={stats['max_z']:.2f}")
    else:
        z, stats = compute_z_scores(stress_smooth, working_mask)
        edge_debug = None
        if debug:
            print(f"  Iteration 2 (raw stress): pm={stats['peak_to_mean']:.2f}, mz={stats['max_z']:.2f}")
    
    # Find hot chunks B
    hot_mask_B = (z > cut_max_z) & working_mask
    labeled_B, n_chunks_B = ndlabel(hot_mask_B)
    
    chunks_B_raw = []
    for i in range(1, n_chunks_B + 1):
        chunk = get_chunk_info(labeled_B, i)
        if chunk is not None and chunk['size'] >= 3:
            chunks_B_raw.append(chunk)
    
    # Merge nearby chunks
    chunks_B = merge_nearby_chunks(chunks_B_raw, original_mask, distance_threshold_ratio=chunk_merge_threshold)
    
    if debug:
        if len(chunks_B_raw) != len(chunks_B):
            print(f"  Found {len(chunks_B_raw)} raw chunks → merged to {len(chunks_B)} chunks")
        else:
            print(f"  Found {len(chunks_B)} chunks in iteration 2")
    
    # Store iteration 2 info
    debug_info['iterations'].append({
        'iteration': 2,
        'working_mask': working_mask.copy(),
        'stress': stress_smooth.copy(),
        'neck_score': neck_score.copy() if use_neck_score else None,
        'z_scores': z.copy(),
        'stats': stats.copy(),
        'hot_mask': hot_mask_B.copy(),
        'chunks': chunks_B.copy(),
        'edge_debug': edge_debug,
    })
    
    debug_info['chunks_B'] = chunks_B
    
    # ========== TRACK LINEAGE ==========
    lineages = find_chunk_lineage(chunks_A, chunks_B, max_distance=20)
    debug_info['lineages'] = lineages
    
    if debug:
        print(f"  Found {len(lineages)} lineages (A→B connections)")
        for i, lin in enumerate(lineages):
            angle_deg = np.degrees(lin['angle'])
            print(f"    Lineage {i}: A{lin['A']['id']}→B{lin['B']['id']}, angle={angle_deg:.1f}°")
    
    if len(lineages) < 2:
        if debug:
            print(f"  → Not enough lineages to find pairs")
        result = np.zeros_like(mask, dtype=int)
        result[original_mask] = 1
        return result, 1, debug_info
    
    # ========== FIND OPPOSING PAIRS ==========
    pairs = find_opposing_pairs(lineages, angle_threshold=np.pi/3, max_perpendicular_dist=25)
    debug_info['pairs'] = pairs
    
    if debug:
        print(f"  Found {len(pairs)} opposing pairs (face-to-face)")
        for p1, p2 in pairs:
            lin1, lin2 = lineages[p1], lineages[p2]
            angle1 = np.degrees(lin1['angle'])
            angle2 = np.degrees(lin2['angle'])
            tip1 = lin1['B']['centroid']
            tip2 = lin2['B']['centroid']
            dist = np.sqrt((tip1[0]-tip2[0])**2 + (tip1[1]-tip2[1])**2)
            print(f"    Pair: Lineage {p1} ({angle1:.1f}°) ↔ Lineage {p2} ({angle2:.1f}°), tip_dist={dist:.1f}")
    
    if len(pairs) == 0:
        if debug:
            print(f"  → No opposing pairs found")
            
            # Still plot debug info to understand why
            ys, xs = np.where(original_mask)
            margin = 10
            y0, y1 = max(0, ys.min() - margin), min(H, ys.max() + margin)
            x0, x1 = max(0, xs.min() - margin), min(W, xs.max() + margin)
            
            fig, axes = plt.subplots(1, 4, figsize=(20, 5))
            
            # Panel 1: Original with chunks A
            axes[0].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
            if image is not None:
                axes[0].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
            for chunk in chunks_A:
                cy, cx = chunk['centroid']
                axes[0].plot(cx - x0, cy - y0, 'ro', markersize=10)
                axes[0].annotate(f"A{chunk['id']}", (cx - x0, cy - y0), color='red', fontsize=10)
            axes[0].set_title(f'Iteration 1: {len(chunks_A)} chunks')
            axes[0].axis('off')
            
            # Panel 2: After erosion with chunks B
            axes[1].imshow(working_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
            if image is not None:
                axes[1].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
            for chunk in chunks_B:
                cy, cx = chunk['centroid']
                axes[1].plot(cx - x0, cy - y0, 'go', markersize=10)
                axes[1].annotate(f"B{chunk['id']}", (cx - x0, cy - y0), color='green', fontsize=10)
            axes[1].set_title(f'Iteration 2: {len(chunks_B)} chunks')
            axes[1].axis('off')
            
            # Panel 3: Lineages with direction info
            axes[2].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.3)
            if image is not None:
                axes[2].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
            colors = plt.cm.tab10(np.linspace(0, 1, max(len(lineages), 1)))
            for i, lin in enumerate(lineages):
                cy_a, cx_a = lin['A']['centroid']
                cy_b, cx_b = lin['B']['centroid']
                # Draw arrow
                axes[2].arrow(cx_a - x0, cy_a - y0, 
                             (cx_b - cx_a) * 0.8, (cy_b - cy_a) * 0.8,
                             head_width=3, head_length=2, fc=colors[i], ec=colors[i], linewidth=2)
                # Extend the arrow to show direction
                dy, dx = lin['direction']
                axes[2].arrow(cx_b - x0, cy_b - y0, 
                             dx * 15, dy * 15,
                             head_width=2, head_length=1, fc=colors[i], ec=colors[i], 
                             linewidth=1, linestyle='--', alpha=0.5)
                angle_deg = np.degrees(lin['angle'])
                axes[2].annotate(f"{i}:{angle_deg:.0f}°", 
                               ((cx_a + cx_b)/2 - x0, (cy_a + cy_b)/2 - y0), 
                               color='white', fontsize=10, fontweight='bold',
                               bbox=dict(boxstyle='round', facecolor=colors[i], alpha=0.8))
            axes[2].set_title(f'Lineages: {len(lineages)}\n(dashed = direction)')
            axes[2].axis('off')
            
            # Panel 4: Why no pairs? Show all pairwise checks
            axes[3].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.3)
            if image is not None:
                axes[3].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
            # Draw all lineage tips and check why they don't pair
            info_text = "Pairing analysis:\n"
            for i, lin1 in enumerate(lineages):
                for j, lin2 in enumerate(lineages):
                    if j <= i:
                        continue
                    tip1 = np.array(lin1['B']['centroid'])
                    tip2 = np.array(lin2['B']['centroid'])
                    dir1 = np.array(lin1['direction'])
                    dir2 = np.array(lin2['direction'])
                    
                    # Compute checks
                    angle_diff = abs(lin1['angle'] - lin2['angle'])
                    angle_diff = min(angle_diff, 2*np.pi - angle_diff)
                    opposite_diff = abs(angle_diff - np.pi)
                    
                    tip1_to_tip2 = tip2 - tip1
                    dist = np.linalg.norm(tip1_to_tip2)
                    if dist > 0:
                        tip1_to_tip2_norm = tip1_to_tip2 / dist
                        dot1 = np.dot(dir1, tip1_to_tip2_norm)
                        dot2 = np.dot(dir2, tip1_to_tip2_norm)
                    else:
                        dot1, dot2 = 0, 0
                    
                    # Draw line between tips
                    axes[3].plot([tip1[1] - x0, tip2[1] - x0], 
                                [tip1[0] - y0, tip2[0] - y0], 
                                'r--', alpha=0.3, linewidth=1)
                    
                    info_text += f"{i}↔{j}: ang={np.degrees(opposite_diff):.0f}°, d1={dot1:.2f}, d2={dot2:.2f}\n"
            
            axes[3].set_title(f'No pairs found\n{info_text[:100]}...')
            axes[3].axis('off')
            
            plt.tight_layout()
            plt.show()
        
        result = np.zeros_like(mask, dtype=int)
        result[original_mask] = 1
        return result, 1, debug_info
    
    # ========== CREATE CUT LINES ==========
    all_cut_masks = []
    for p1, p2 in pairs:
        cut_mask, endpoints = create_cut_line_from_pair(lineages[p1], lineages[p2], original_mask)
        if cut_mask is not None and cut_mask.sum() > 0:
            all_cut_masks.append(cut_mask)
            debug_info['cut_lines'].append({'mask': cut_mask, 'endpoints': endpoints})
            if debug:
                print(f"    Created cut line with {cut_mask.sum()} pixels")
    
    if len(all_cut_masks) == 0:
        if debug:
            print(f"  → No valid cut lines created")
        result = np.zeros_like(mask, dtype=int)
        result[original_mask] = 1
        return result, 1, debug_info
    
    # ========== APPLY CUT LINES ==========
    combined_cut = np.zeros_like(mask, dtype=bool)
    for cut_mask in all_cut_masks:
        combined_cut |= cut_mask
    
    # Dilate cut line slightly
    combined_cut_dilated = binary_dilation(combined_cut, iterations=1)
    
    # Remove cut line from mask
    result_mask = original_mask & ~combined_cut_dilated
    
    # Label connected components
    labeled_result, n_parts = ndlabel(result_mask)
    
    # Filter tiny fragments
    valid_parts = []
    for i in range(1, n_parts + 1):
        if (labeled_result == i).sum() > 50:
            valid_parts.append(i)
    
    if debug:
        print(f"  After cutting: {n_parts} components, {len(valid_parts)} valid (>50 pixels)")
    
    if len(valid_parts) < 2:
        if debug:
            print(f"  → Cut didn't create valid split")
        result = np.zeros_like(mask, dtype=int)
        result[original_mask] = 1
        return result, 1, debug_info
    
    # Build final result with valid parts only
    final_result = np.zeros_like(mask, dtype=int)
    for new_id, old_id in enumerate(valid_parts, 1):
        final_result[labeled_result == old_id] = new_id
    
    # Assign cut line pixels to nearest body
    cut_pixels = list(zip(*np.where(combined_cut_dilated & original_mask)))
    for (y, x) in cut_pixels:
        min_dist = float('inf')
        nearest_label = 1
        
        for new_id, old_id in enumerate(valid_parts, 1):
            body_ys, body_xs = np.where(labeled_result == old_id)
            if len(body_ys) == 0:
                continue
            dists = np.sqrt((body_ys - y)**2 + (body_xs - x)**2)
            min_body_dist = dists.min()
            if min_body_dist < min_dist:
                min_dist = min_body_dist
                nearest_label = new_id
        
        final_result[y, x] = nearest_label
    
    if debug:
        print(f"  → SUCCESS! Split into {len(valid_parts)} parts")
    
    # ========== DEBUG VISUALIZATION ==========
    if debug:
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        
        # Row 1: Process visualization
        # Panel 1: Original with chunks A
        axes[0, 0].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
        if image is not None:
            axes[0, 0].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
        for chunk in chunks_A:
            cy, cx = chunk['centroid']
            axes[0, 0].plot(cx - x0, cy - y0, 'ro', markersize=10)
            axes[0, 0].annotate(f"A{chunk['id']}", (cx - x0, cy - y0), color='red', fontsize=10)
        axes[0, 0].set_title(f'Iteration 1: {len(chunks_A)} chunks')
        axes[0, 0].axis('off')
        
        # Panel 2: After erosion with chunks B
        axes[0, 1].imshow(working_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
        if image is not None:
            axes[0, 1].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
        for chunk in chunks_B:
            cy, cx = chunk['centroid']
            axes[0, 1].plot(cx - x0, cy - y0, 'go', markersize=10)
            axes[0, 1].annotate(f"B{chunk['id']}", (cx - x0, cy - y0), color='green', fontsize=10)
        axes[0, 1].set_title(f'Iteration 2: {len(chunks_B)} chunks')
        axes[0, 1].axis('off')
        
        # Panel 3: Lineages (A→B connections)
        axes[0, 2].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.3)
        if image is not None:
            axes[0, 2].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
        colors = plt.cm.tab10(np.linspace(0, 1, len(lineages)))
        for i, lin in enumerate(lineages):
            cy_a, cx_a = lin['A']['centroid']
            cy_b, cx_b = lin['B']['centroid']
            axes[0, 2].arrow(cx_a - x0, cy_a - y0, 
                            (cx_b - cx_a) * 0.8, (cy_b - cy_a) * 0.8,
                            head_width=3, head_length=2, fc=colors[i], ec=colors[i], linewidth=2)
            axes[0, 2].annotate(f"{i}", ((cx_a + cx_b)/2 - x0, (cy_a + cy_b)/2 - y0), 
                               color='white', fontsize=12, fontweight='bold',
                               bbox=dict(boxstyle='round', facecolor=colors[i], alpha=0.8))
        axes[0, 2].set_title(f'Lineages: {len(lineages)}')
        axes[0, 2].axis('off')
        
        # Panel 4: Opposing pairs
        axes[0, 3].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.3)
        if image is not None:
            axes[0, 3].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
        pair_colors = plt.cm.Set1(np.linspace(0, 1, max(len(pairs), 1)))
        for pi, (p1, p2) in enumerate(pairs):
            lin1, lin2 = lineages[p1], lineages[p2]
            # Draw both lineages in same color
            for lin in [lin1, lin2]:
                cy_a, cx_a = lin['A']['centroid']
                cy_b, cx_b = lin['B']['centroid']
                axes[0, 3].arrow(cx_a - x0, cy_a - y0, 
                                (cx_b - cx_a) * 0.8, (cy_b - cy_a) * 0.8,
                                head_width=3, head_length=2, fc=pair_colors[pi], ec=pair_colors[pi], linewidth=3)
        axes[0, 3].set_title(f'Opposing pairs: {len(pairs)}')
        axes[0, 3].axis('off')
        
        # Row 2: Cut lines and result
        # Panel 5: Cut lines
        axes[1, 0].imshow(original_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
        if image is not None:
            axes[1, 0].imshow(image[y0:y1, x0:x1], cmap='gray', alpha=0.3)
        for cut_info in debug_info['cut_lines']:
            cut_vis = np.zeros((y1-y0, x1-x0, 4))
            cut_vis[cut_info['mask'][y0:y1, x0:x1], :] = [1, 0, 0, 0.8]
            axes[1, 0].imshow(cut_vis)
            if cut_info['endpoints'] is not None:
                e1, e2 = cut_info['endpoints']
                axes[1, 0].plot([e1[1] - x0, e2[1] - x0], [e1[0] - y0, e2[0] - y0], 'r-', linewidth=2)
        axes[1, 0].set_title(f'Cut lines: {len(debug_info["cut_lines"])}')
        axes[1, 0].axis('off')
        
        # Panel 6: After cutting (before restoration)
        axes[1, 1].imshow(result_mask[y0:y1, x0:x1], cmap='Blues', alpha=0.5)
        axes[1, 1].set_title(f'After cut\n{result_mask.sum()} pixels')
        axes[1, 1].axis('off')
        
        # Panel 7: Final labeled result
        axes[1, 2].imshow(final_result[y0:y1, x0:x1], cmap='nipy_spectral')
        part_sizes = [(final_result == i).sum() for i in range(1, len(valid_parts) + 1)]
        axes[1, 2].set_title(f'Final: {len(valid_parts)} parts\nSizes: {part_sizes}')
        axes[1, 2].axis('off')
        
        # Panel 8: Overlay on original image
        if image is not None:
            axes[1, 3].imshow(image[y0:y1, x0:x1], cmap='gray')
            for i in range(1, len(valid_parts) + 1):
                part_mask = (final_result == i)
                part_boundary = part_mask ^ binary_erosion(part_mask)
                color_overlay = np.zeros((y1-y0, x1-x0, 4))
                color = plt.cm.tab10(i / 10)
                color_overlay[part_boundary[y0:y1, x0:x1], :] = [color[0], color[1], color[2], 0.8]
                axes[1, 3].imshow(color_overlay)
        axes[1, 3].set_title('Result overlay')
        axes[1, 3].axis('off')
        
        plt.tight_layout()
        plt.show()
    
    return final_result, len(valid_parts), debug_info


def find_split_candidates(labels, params, min_region_size=None):
    """Find regions that need splitting based on stress concentration.
    
    Optimized for large numbers of regions using regionprops for size filtering.
    """
    from skimage.measure import regionprops
    
    cut_peak_to_mean = params.get('cut_peak_to_mean', 2.0)
    cut_max_z = params.get('cut_max_z', 2.5)
    verbose = params.get('verbose_split', False)
    if min_region_size is None:
        min_region_size = params.get('cut_min_region_size', 100)  # Lowered from 200 to 100
    
    n_regions = labels.max()
    
    if verbose:
        print(f"    Scanning {n_regions} regions (min_size={min_region_size})...")
    
    # First pass: quick size filter using regionprops (much faster than looping)
    props = regionprops(labels)
    
    # Filter by size first
    size_candidates = []
    for prop in props:
        if prop.area >= min_region_size:
            size_candidates.append(prop.label)
    
    if verbose:
        print(f"    {len(size_candidates)} regions pass size filter")
    
    # Second pass: stress check only on size-filtered regions
    candidates = []
    for region_id in size_candidates:
        mask = (labels == region_id)
        
        # Compute stress and neck_score (same as actual splitting)
        w = solve_poisson(mask)
        stress = compute_stress(w, mask)
        
        # Use neck_score for candidate selection - same as actual split detection
        neck_score, z_scores, stats, _ = compute_neck_score_z(stress, mask, sigma_smooth=2)
        
        pm = stats.get('peak_to_mean', 0)
        mz = stats.get('max_z', 0)
        
        # More lenient: try if EITHER threshold is exceeded
        # (the actual split will still require clusters to be found)
        should_try = (pm > cut_peak_to_mean * 0.75) or (mz > cut_max_z)
        
        if verbose:
            print(f"      Region {region_id}: size={mask.sum()}, "
                  f"peak/mean={pm:.2f}, max_z={mz:.2f}, "
                  f"should_try={should_try}")
        
        if should_try:
            candidates.append(region_id)
    
    if verbose:
        print(f"    {len(candidates)} candidates have stress concentration")
    
    return candidates


def apply_splits_chunk_tracking(labels, params):
    """
    Apply splitting to all candidate regions using cluster-based neck detection.
    Iterates until no more splits are possible or max iterations reached.
    
    Optimization: After first iteration, only check newly created bodies.
    
    Safeguard: Clusters near previous cut lines are ignored to prevent
    false positives from cut artifacts.
    
    Returns:
        final_labels: Final label array after all splits
        all_split_info: List of individual split details
        iteration_snapshots: List of (iteration_num, labels_copy, n_regions, n_splits) for each iteration
    """
    cut_peak_to_mean = params.get('cut_peak_to_mean', 2.0)
    cut_max_z = params.get('cut_max_z', 2.5)
    min_region_size = params.get('cut_min_region_size', 100)
    max_iterations = params.get('max_split_iterations', 5)
    use_cluster_method = params.get('use_cluster_detection', True)
    verbose = params.get('verbose_split', False)
    cut_exclusion_radius = params.get('cut_exclusion_radius', 10)  # Pixels to exclude near previous cuts
    
    current_labels = labels.copy()
    all_split_info = []
    iteration_snapshots = []
    next_label = current_labels.max() + 1
    
    # Track previous cut lines as a mask of exclusion zones
    H, W = labels.shape
    cut_exclusion_mask = np.zeros((H, W), dtype=bool)
    
    # Save initial state (iteration 0 = after merge, before any splits)
    initial_relabeled, _ = relabel(current_labels.copy(), return_num=True)
    iteration_snapshots.append({
        'iteration': 0,
        'labels': initial_relabeled,
        'n_regions': initial_relabeled.max(),
        'n_splits': 0,
        'description': 'After Merge (before splits)'
    })
    
    # First iteration: check all regions
    bodies_to_check = None  # None means check all
    
    for iteration in range(max_iterations):
        if verbose:
            print(f"\n    === Split Iteration {iteration + 1}/{max_iterations} ===")
        
        # Find candidates
        if bodies_to_check is None:
            # First iteration: find all candidates
            candidates = find_split_candidates(current_labels, params)
        else:
            # Subsequent iterations: only check specified bodies
            if len(bodies_to_check) == 0:
                if verbose:
                    print(f"    No new bodies to check. Stopping.")
                break
                
            if verbose:
                print(f"    Checking {len(bodies_to_check)} new bodies from previous splits...")
            candidates = []
            for region_id in bodies_to_check:
                mask = (current_labels == region_id)
                region_size = mask.sum()
                
                if region_size < min_region_size:
                    if verbose:
                        print(f"      Region {region_id}: size={region_size} (too small)")
                    continue
                
                # Use neck_score for candidate selection - same as actual split detection
                w = solve_poisson(mask)
                stress = compute_stress(w, mask)
                neck_score, z_scores, stats, _ = compute_neck_score_z(stress, mask, sigma_smooth=2)
                
                pm = stats.get('peak_to_mean', 0)
                mz = stats.get('max_z', 0)
                should_try = (pm > cut_peak_to_mean * 0.75) or (mz > cut_max_z)
                
                if verbose:
                    print(f"      Region {region_id}: size={region_size}, "
                          f"pm={pm:.2f}, mz={mz:.2f}, try={should_try}")
                
                if should_try:
                    candidates.append(region_id)
        
        if not candidates:
            if verbose:
                print(f"    No split candidates. Stopping.")
            break
        
        if verbose:
            print(f"    Candidates: {candidates}")
        
        splits_this_iteration = 0
        new_bodies = []  # Track new bodies for next iteration
        
        for region_id in candidates:
            mask = (current_labels == region_id)
            
            if verbose:
                print(f"\n    Processing region {region_id} (size={mask.sum()})...")
            
            # For new child regions (from previous iteration's splits), don't apply exclusion
            # The exclusion is meant to prevent re-cutting the SAME region, not its children
            # Check if this region was created in a previous iteration (is in bodies_to_check)
            apply_exclusion = bodies_to_check is None or region_id not in bodies_to_check
            region_exclusion_mask = cut_exclusion_mask if apply_exclusion else None
            
            # Try to split using cluster-based method or old chunk tracking
            if use_cluster_method:
                split_labeled, n_parts, debug_info = split_region_cluster_based(
                    mask, params, debug=False, exclusion_mask=region_exclusion_mask)
                
                # Show cluster info for debugging
                if verbose:
                    clusters = debug_info.get('clusters', [])
                    cut_line = debug_info.get('cut_line')
                    print(f"      Clusters found: {len(clusters)}")
                    if cut_line:
                        print(f"      Cut method: {cut_line.get('method', 'unknown')}")
                    else:
                        cut_debug = debug_info.get('cluster_debug', {}).get('cut_debug', {})
                        print(f"      No cut - reason: {cut_debug.get('rejection_reason', 'unknown')}")
            else:
                split_labeled, n_parts, debug_info = split_region_chunk_tracking(mask, params, debug=False)
            
            if n_parts >= 2:
                # Get split method info
                cut_line = debug_info.get('cut_line')
                method = cut_line.get('method', 'unknown') if cut_line else 'unknown'
                
                # Update exclusion mask with CLUSTER locations (not cut line)
                # Clusters are broader and better represent the artifact zone
                # This prevents future iterations from detecting false necks near previous split locations
                clusters = debug_info.get('clusters', [])
                if clusters:
                    from skimage.morphology import binary_dilation, disk
                    
                    for cluster in clusters:
                        cluster_mask = cluster.get('mask')
                        if cluster_mask is not None and cluster_mask.any():
                            # cluster_mask is already in global coordinates (same shape as full image)
                            # Dilate the cluster zone to create exclusion buffer
                            if cut_exclusion_radius > 0:
                                dilated_zone = binary_dilation(cluster_mask, disk(cut_exclusion_radius))
                                cut_exclusion_mask |= dilated_zone
                            else:
                                cut_exclusion_mask |= cluster_mask
                            
                            if verbose:
                                cy, cx = cluster['centroid']
                                print(f"        Added exclusion zone around cluster at ({cy:.1f}, {cx:.1f})")
                
                # Clear original region
                current_labels[mask] = 0
                
                # Add new parts - use adaptive min size
                total_area = mask.sum()
                min_part_size = max(20, int(total_area * 0.1))  # At least 10% or 20px
                
                new_part_ids = []
                valid_parts = []
                for part_id in range(1, n_parts + 1):
                    part_mask = (split_labeled == part_id)
                    part_size = part_mask.sum()
                    
                    if part_size >= min_part_size:
                        valid_parts.append((part_id, part_mask, part_size))
                
                # Only accept split if we have at least 2 valid parts
                if len(valid_parts) >= 2:
                    if verbose:
                        print(f"      → Split into {len(valid_parts)} parts! (method: {method})")
                    splits_this_iteration += 1
                    
                    for part_id, part_mask, part_size in valid_parts:
                        current_labels[part_mask] = next_label
                        new_part_ids.append(next_label)
                        new_bodies.append(next_label)
                        if verbose:
                            print(f"        Part {part_id}: {part_size} px → label {next_label}")
                        next_label += 1
                    
                    all_split_info.append({
                        'iteration': iteration + 1,
                        'original_id': region_id,
                        'new_ids': new_part_ids,
                        'n_parts': len(valid_parts),
                        'debug_info': debug_info,
                    })
                else:
                    # Not enough valid parts - restore original region
                    current_labels[mask] = region_id
                    if verbose:
                        print(f"      → Split rejected: only {len(valid_parts)} valid part(s) >= {min_part_size}px")
            else:
                if verbose:
                    print(f"      → No split")
        
        if verbose:
            print(f"\n    Iteration {iteration + 1}: {splits_this_iteration} splits, {len(new_bodies)} new bodies")
        
        # Save snapshot after this iteration
        iter_relabeled, _ = relabel(current_labels.copy(), return_num=True)
        iteration_snapshots.append({
            'iteration': iteration + 1,
            'labels': iter_relabeled,
            'n_regions': iter_relabeled.max(),
            'n_splits': splits_this_iteration,
            'description': f'After Iteration {iteration + 1} ({splits_this_iteration} splits)'
        })
        
        if splits_this_iteration == 0:
            if verbose:
                print(f"    No splits. Stopping.")
            break
        
        # Next iteration: only check the new bodies
        bodies_to_check = new_bodies
    
    # Final relabel
    current_labels, _ = relabel(current_labels, return_num=True)
    
    return current_labels, all_split_info, iteration_snapshots


