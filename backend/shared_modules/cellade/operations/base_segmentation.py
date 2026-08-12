"""
CellADE base segmentation (v2) — seed detection and radial expansion.

Pipeline: CLAHE → FCM clustering → H-maxima seeds → radial expansion.
"""

import numpy as np
from skimage import exposure
from skimage.measure import label as relabel, regionprops
from skimage.morphology import h_maxima, disk
from skimage.filters import gaussian
from scipy.ndimage import binary_dilation, binary_erosion, label as ndlabel

try:
    from skfuzzy import cmeans
    FCM_AVAILABLE = True
except ImportError:
    FCM_AVAILABLE = False

def run_cellade_v2(image, params, return_intermediates=False):
    """Run CellADE v2 and return labels.
    
    If return_intermediates=True, also returns a dict with:
        - img_enh: CLAHE enhanced image
        - fg_mask_raw: Raw foreground mask from FCM (before hole filling)
        - fg_mask: Foreground mask after hole filling
        - seeds: Detected seed points
        - labels: Final labels after radial expansion
    """
    verbose = params.get('verbose_cellade', False)
    
    image = image.astype(np.float32)
    image = (image - image.min()) / (image.max() - image.min() + 1e-8)
    
    img_enh = exposure.equalize_adapthist(image, clip_limit=params.get('clahe_clip', 0.01))
    fg_mask_raw, fg_stats = _global_fcm(img_enh, params.get('fcm_clusters', 3), params.get('fcm_min_sep', 0.1))
    
    # Fill internal holes in foreground mask (no external boundary changes)
    fg_mask = _fill_holes_in_mask(fg_mask_raw, verbose=verbose)
    
    seeds = _detect_seeds(img_enh, fg_mask, params.get('h_maxima_h', 0.05), params.get('seed_min_dist', 5))
    
    if len(seeds) == 0:
        labels = np.zeros(image.shape, dtype=np.int32)
    else:
        labels = _radial_expansion(img_enh, seeds, fg_stats, fg_mask, 
                                   params.get('max_radius', 100),
                                   params.get('local_fcm_sep', 0.08),
                                   params.get('z_threshold', 2.5),
                                   verbose=verbose)
    
    if return_intermediates:
        intermediates = {
            'img_enh': img_enh,
            'fg_mask_raw': fg_mask_raw,
            'fg_mask': fg_mask,
            'seeds': seeds,
        }
        return labels, img_enh, fg_mask, intermediates
    
    return labels, img_enh, fg_mask


def _global_fcm(image, n_clusters=3, min_separation=0.1):
    H, W = image.shape
    data = image.ravel().astype(np.float64).reshape(1, -1)
    
    if not FCM_AVAILABLE:
        from skimage.filters import threshold_otsu
        t = threshold_otsu(image)
        fg_mask = image > t
        fg_pixels = image[fg_mask]
        fg_stats = _compute_fg_stats(fg_pixels)
        return fg_mask, fg_stats
    
    cntr, u, *_ = cmeans(data, c=n_clusters, m=2.0, error=0.005, maxiter=200, init=None)
    centers = np.sort(cntr.flatten())
    
    if n_clusters == 3:
        sep1 = centers[1] - centers[0]
        sep2 = centers[2] - centers[1]
        if sep1 < min_separation or sep2 < min_separation:
            cntr, u, *_ = cmeans(data, c=2, m=2.0, error=0.005, maxiter=200, init=None)
            centers = np.sort(cntr.flatten())
            n_clusters = 2
    
    assignments = np.argmax(u, axis=0).reshape(H, W)
    center_order = np.argsort(cntr.flatten())
    reverse_map = {center_order[i]: i for i in range(n_clusters)}
    cluster_map = np.vectorize(lambda x: reverse_map[x])(assignments)
    
    fg_mask = cluster_map > 0
    fg_pixels = image[fg_mask]
    fg_stats = _compute_fg_stats(fg_pixels)
    
    return fg_mask, fg_stats


def _fill_holes_in_mask(fg_mask, verbose=False):
    """
    Fill internal holes in the foreground mask.
    
    This fills holes INSIDE foreground regions without changing external boundaries.
    Uses binary_fill_holes which fills regions of False surrounded by True.
    
    Parameters:
        fg_mask: Binary foreground mask
        verbose: Print detailed output
        
    Returns:
        filled_mask: Mask with internal holes filled
    """
    from scipy.ndimage import binary_fill_holes
    
    filled_mask = binary_fill_holes(fg_mask)
    
    n_filled = filled_mask.sum() - fg_mask.sum()
    if verbose and n_filled > 0:
        print(f"    Filled {n_filled} hole pixels in foreground mask")
    
    return filled_mask


def _compute_fg_stats(fg_pixels):
    if len(fg_pixels) == 0:
        return {'mean': 0.5, 'std': 0.1, 'p5': 0.3, 'p10': 0.35, 'p25': 0.4}
    return {
        'mean': np.mean(fg_pixels),
        'std': np.std(fg_pixels),
        'p5': np.percentile(fg_pixels, 5),
        'p10': np.percentile(fg_pixels, 10),
        'p25': np.percentile(fg_pixels, 25),
    }


def _detect_seeds(image, fg_mask, h=0.05, min_dist=5):
    img_smooth = gaussian(image, sigma=1.0)
    h_max = h_maxima(img_smooth, h=h)
    seeds = np.argwhere(h_max)
    
    if len(seeds) > 0:
        seeds = np.array([s for s in seeds if fg_mask[s[0], s[1]]])
    
    if len(seeds) > 1 and min_dist > 0:
        intensities = np.array([image[y, x] for y, x in seeds])
        order = np.argsort(intensities)[::-1]
        seeds = seeds[order]
        kept = [seeds[0]]
        for s in seeds[1:]:
            dists = np.sqrt(np.sum((np.array(kept) - s)**2, axis=1))
            if dists.min() >= min_dist:
                kept.append(s)
        seeds = np.array(kept)
    
    return seeds


def _radial_expansion(image, seeds, fg_stats, global_fg_mask, max_radius=100, 
                      fcm_separation=0.08, z_threshold=2.5, verbose=False):
    H, W = image.shape
    labels = np.zeros((H, W), dtype=np.int32)
    regions = {}
    boundaries = {}
    active = set()
    
    for i, (y, x) in enumerate(seeds):
        seed_id = i + 1
        y, x = int(y), int(x)
        labels[y, x] = seed_id
        regions[seed_id] = {(y, x)}
        boundaries[seed_id] = {(y, x)}
        active.add(seed_id)
    
    for iteration in range(max_radius * 4):
        if not active:
            break
        
        still_active = set()
        for seed_id in list(active):
            grew, has_expandable = _expand_step(
                image, labels, regions[seed_id], boundaries[seed_id], seed_id,
                fg_stats, global_fg_mask, fcm_separation, z_threshold
            )
            if has_expandable:
                still_active.add(seed_id)
        active = still_active
    
    # Enforce fg_mask coverage: assign unassigned fg pixels to nearest body
    labels = _enforce_fg_coverage(labels, global_fg_mask, verbose=verbose)
    
    labels, _ = relabel(labels, return_num=True)
    return labels


def _enforce_fg_coverage(labels, fg_mask, verbose=False):
    """
    Assign any unassigned foreground pixels to the nearest labeled body.
    
    This ensures all fg_mask pixels are part of some region after expansion.
    Uses distance transform to find the nearest labeled pixel.
    
    Parameters:
        labels: Current label array (some fg pixels may be 0)
        fg_mask: Foreground mask (all True pixels should be assigned)
        verbose: Print detailed output
        
    Returns:
        labels: Updated labels with all fg pixels assigned
    """
    from scipy.ndimage import distance_transform_edt
    
    # Find unassigned foreground pixels
    unassigned = fg_mask & (labels == 0)
    n_unassigned = unassigned.sum()
    
    if n_unassigned == 0:
        return labels
    
    # Create a mask of assigned pixels
    assigned_mask = labels > 0
    
    if not assigned_mask.any():
        # No labels at all - nothing to assign to
        return labels
    
    # Compute distance transform from assigned pixels
    # This gives distance to nearest assigned pixel for each unassigned pixel
    distances, indices = distance_transform_edt(~assigned_mask, return_indices=True)
    
    # For each unassigned fg pixel, copy the label from nearest assigned pixel
    new_labels = labels.copy()
    unassigned_coords = np.where(unassigned)
    
    for y, x in zip(unassigned_coords[0], unassigned_coords[1]):
        nearest_y, nearest_x = indices[0, y, x], indices[1, y, x]
        new_labels[y, x] = labels[nearest_y, nearest_x]
    
    if verbose:
        print(f"    Enforced fg coverage: assigned {n_unassigned} unassigned pixels to nearest bodies")
    
    return new_labels


def _expand_step(image, labels, region, boundary, seed_id, fg_stats, global_fg_mask, 
                 fcm_separation, z_threshold):
    H, W = image.shape
    
    candidates = set()
    for (y, x) in boundary:
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy == 0 and dx == 0:
                    continue
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and labels[ny, nx] == 0:
                    candidates.add((ny, nx))
    
    if not candidates:
        boundary.clear()
        return False, False
    
    all_coords = list(region) + list(candidates)
    pixel_values = np.array([image[y, x] for y, x in all_coords])
    n_region = len(region)
    
    if len(pixel_values) < 20:
        local_fg_mask = pixel_values >= fg_stats['p5']
    else:
        local_fg_mask = _local_fcm(pixel_values, fcm_separation, fg_stats)
    
    new_pixels = []
    for i, (y, x) in enumerate(all_coords):
        if i < n_region:
            continue
        if labels[y, x] != 0:
            continue
        if not global_fg_mask[y, x]:
            continue
        if not local_fg_mask[i]:
            continue
        intensity = image[y, x]
        z_score = (fg_stats['mean'] - intensity) / (fg_stats['std'] + 1e-8)
        if z_score > z_threshold:
            continue
        labels[y, x] = seed_id
        region.add((y, x))
        new_pixels.append((y, x))
    
    boundary.clear()
    boundary.update(new_pixels)
    
    has_expandable = False
    for (y, x) in boundary:
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and labels[ny, nx] == 0:
                    has_expandable = True
                    break
            if has_expandable:
                break
    
    return len(new_pixels) > 0, has_expandable


def _local_fcm(pixel_values, min_separation, fg_stats):
    if not FCM_AVAILABLE:
        return pixel_values >= fg_stats['p5']
    
    data = pixel_values.reshape(1, -1).astype(np.float64)
    try:
        cntr, u, *_ = cmeans(data, c=2, m=2.0, error=0.01, maxiter=50, init=None)
        centers = cntr.flatten()
        separation = abs(centers[1] - centers[0])
        if separation < min_separation:
            return np.ones(len(pixel_values), dtype=bool)
        bg_idx = np.argmin(centers)
        fg_idx = np.argmax(centers)
        if centers[bg_idx] >= fg_stats['p10']:
            return np.ones(len(pixel_values), dtype=bool)
        return u[fg_idx] >= 0.4
    except:
        return pixel_values >= fg_stats['p5']


