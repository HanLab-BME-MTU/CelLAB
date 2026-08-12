"""
CellADE utilities — contour extraction and neighbor finding.
"""

import numpy as np
from skimage.measure import find_contours, regionprops
from scipy.ndimage import binary_dilation


def get_mask_contour(mask):
    """Extract ordered boundary points from a binary mask."""
    padded = np.pad(mask.astype(float), 1, mode='constant', constant_values=0)
    contours = find_contours(padded, 0.5)
    if len(contours) == 0:
        return None
    contour = max(contours, key=len) - 1
    return contour

def find_neighbors(labels):
    """Find neighboring regions efficiently using vectorized operations."""
    H, W = labels.shape
    neighbors = {}
    shared_boundary_pixels = {}
    
    # Initialize neighbor sets
    max_label = labels.max()
    for region_id in range(1, max_label + 1):
        neighbors[region_id] = set()
    
    # Vectorized horizontal neighbor detection
    h_diff = labels[:, :-1] != labels[:, 1:]
    h_pairs_y, h_pairs_x = np.where(h_diff)
    
    for y, x in zip(h_pairs_y, h_pairs_x):
        left = labels[y, x]
        right = labels[y, x + 1]
        if left != 0 and right != 0:
            neighbors[left].add(right)
            neighbors[right].add(left)
            pair = (min(left, right), max(left, right))
            if pair not in shared_boundary_pixels:
                shared_boundary_pixels[pair] = []
            shared_boundary_pixels[pair].extend([(y, x), (y, x + 1)])
    
    # Vectorized vertical neighbor detection
    v_diff = labels[:-1, :] != labels[1:, :]
    v_pairs_y, v_pairs_x = np.where(v_diff)
    
    for y, x in zip(v_pairs_y, v_pairs_x):
        top = labels[y, x]
        bottom = labels[y + 1, x]
        if top != 0 and bottom != 0:
            neighbors[top].add(bottom)
            neighbors[bottom].add(top)
            pair = (min(top, bottom), max(top, bottom))
            if pair not in shared_boundary_pixels:
                shared_boundary_pixels[pair] = []
            shared_boundary_pixels[pair].extend([(y, x), (y + 1, x)])
    
    # Remove duplicates
    for pair in shared_boundary_pixels:
        shared_boundary_pixels[pair] = list(set(shared_boundary_pixels[pair]))
    
    return neighbors, shared_boundary_pixels


