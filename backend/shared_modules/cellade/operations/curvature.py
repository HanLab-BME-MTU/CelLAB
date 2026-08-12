"""
CellADE curvature analysis — boundary curvature for merge decisions.
"""

import numpy as np
from skimage.measure import find_contours

def get_ordered_boundary(labels, region_id):
    """Get ordered boundary pixels for a region."""
    mask = (labels == region_id).astype(np.uint8)
    padded = np.pad(mask, 1, mode='constant', constant_values=0)
    contours = find_contours(padded, 0.5)
    
    if len(contours) == 0:
        return np.array([])
    
    main_contour = max(contours, key=len)
    main_contour = main_contour - 1
    return main_contour


def compute_curvature(contour, smooth_sigma=0, debug=False):
    """Compute curvature at each contour point."""
    if len(contour) < 5:
        return np.zeros(len(contour))
    
    if smooth_sigma > 0:
        contour_smooth = np.zeros_like(contour)
        contour_smooth[:, 0] = gaussian(contour[:, 0], sigma=smooth_sigma, mode='wrap')
        contour_smooth[:, 1] = gaussian(contour[:, 1], sigma=smooth_sigma, mode='wrap')
    else:
        contour_smooth = contour
    
    n = len(contour_smooth)
    dx = np.zeros(n)
    dy = np.zeros(n)
    for i in range(n):
        dx[i] = contour_smooth[(i + 1) % n, 1] - contour_smooth[(i - 1) % n, 1]
        dy[i] = contour_smooth[(i + 1) % n, 0] - contour_smooth[(i - 1) % n, 0]
    
    ddx = np.zeros(n)
    ddy = np.zeros(n)
    for i in range(n):
        ddx[i] = contour_smooth[(i + 1) % n, 1] - 2 * contour_smooth[i, 1] + contour_smooth[(i - 1) % n, 1]
        ddy[i] = contour_smooth[(i + 1) % n, 0] - 2 * contour_smooth[i, 0] + contour_smooth[(i - 1) % n, 0]
    
    numerator = dx * ddy - dy * ddx
    denominator = (dx**2 + dy**2)**1.5 + 1e-10
    
    curvature = numerator / denominator
    
    if debug:
        print(f"      DEBUG curvature: n={n}, dx_range=[{dx.min():.4f}, {dx.max():.4f}], "
              f"dy_range=[{dy.min():.4f}, {dy.max():.4f}], curv_range=[{curvature.min():.4f}, {curvature.max():.4f}]")
    
    return curvature


def analyze_region_boundary(labels, region_id, debug=False):
    """Analyze boundary curvature of a region."""
    contour = get_ordered_boundary(labels, region_id)
    
    if len(contour) < 5:
        return None
    
    curvature_raw = compute_curvature(contour, smooth_sigma=0, debug=debug)
    
    if debug:
        abs_curv = np.abs(curvature_raw)
        nonzero_count = np.sum(abs_curv > 1e-6)
        print(f"    Region {region_id}: contour length={len(contour)}, "
              f"curvature median_abs={np.median(abs_curv):.6f}, "
              f"mean_abs={np.mean(abs_curv):.6f}, "
              f"nonzero={nonzero_count}/{len(curvature_raw)}")
    
    return {
        'contour': contour,
        'curvature_raw': curvature_raw,
    }


