"""
CellADE stress analysis — Poisson solver, Von Mises stress, neck score.
"""

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve
from scipy.ndimage import binary_erosion, binary_dilation
from skimage.filters import gaussian
from skimage.measure import find_contours

def solve_poisson(mask):
    """Solve nabla^2 w = -1 with w=0 at boundary (plate bending).
    
    Optimized version using vectorized operations.
    """
    H, W = mask.shape
    
    # Vectorized interior point detection
    interior = mask.copy()
    interior[0, :] = False
    interior[-1, :] = False
    interior[:, 0] = False
    interior[:, -1] = False
    interior[1:-1, 1:-1] &= (mask[:-2, 1:-1] & mask[2:, 1:-1] & 
                             mask[1:-1, :-2] & mask[1:-1, 2:])
    
    # Get interior point indices
    interior_coords = np.argwhere(interior)
    n = len(interior_coords)
    
    if n == 0:
        return np.zeros((H, W))
    
    # Create mapping from (i,j) to linear index
    point_idx = np.full((H, W), -1, dtype=np.int32)
    point_idx[interior] = np.arange(n)
    
    # Build sparse matrix using vectorized operations
    # Each interior point connects to itself (-4) and up to 4 neighbors (+1 each)
    rows = []
    cols = []
    vals = []
    
    # Diagonal entries
    rows.extend(range(n))
    cols.extend(range(n))
    vals.extend([-4.0] * n)
    
    # Neighbor connections (vectorized)
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni = interior_coords[:, 0] + di
        nj = interior_coords[:, 1] + dj
        neighbor_idx = point_idx[ni, nj]
        valid = neighbor_idx >= 0
        
        rows.extend(np.arange(n)[valid])
        cols.extend(neighbor_idx[valid])
        vals.extend([1.0] * valid.sum())
    
    A = csr_matrix((vals, (rows, cols)), shape=(n, n))
    b = -np.ones(n)
    w_int = spsolve(A, b)
    
    w = np.zeros((H, W))
    w[interior] = w_int
    
    return w


def compute_stress(w, mask):
    """Compute Von Mises bending stress.
    
    Optimized version using array slicing instead of loops.
    """
    H, W = w.shape
    
    # Compute curvatures using array slicing
    kxx = np.zeros_like(w)
    kyy = np.zeros_like(w)
    kxy = np.zeros_like(w)
    
    # Interior region
    kxx[1:-1, 1:-1] = w[1:-1, :-2] - 2*w[1:-1, 1:-1] + w[1:-1, 2:]
    kyy[1:-1, 1:-1] = w[:-2, 1:-1] - 2*w[1:-1, 1:-1] + w[2:, 1:-1]
    kxy[1:-1, 1:-1] = (w[2:, 2:] - w[2:, :-2] - w[:-2, 2:] + w[:-2, :-2]) / 4
    
    # Apply mask
    kxx[~mask] = 0
    kyy[~mask] = 0
    kxy[~mask] = 0
    
    stress = np.sqrt(kxx**2 + kyy**2 - kxx*kyy + 3*kxy**2)
    return stress


def compute_z_scores(stress, mask):
    """Compute z-scores on log-transformed stress."""
    z = np.zeros_like(stress)
    
    vals = stress[mask]
    if len(vals) == 0:
        return z, {}
    
    vals_log = np.log1p(vals)
    mean_log = vals_log.mean()
    std_log = vals_log.std()
    
    if std_log < 1e-10:
        return z, {'peak_to_mean': 1.0, 'max_z': 0.0}
    
    stress_log = np.log1p(stress)
    z[mask] = (stress_log[mask] - mean_log) / std_log
    
    max_stress = vals.max()
    mean_stress = vals.mean()
    peak_to_mean = max_stress / (mean_stress + 1e-10)
    max_z = z[mask].max()
    
    stats = {
        'peak_to_mean': peak_to_mean,
        'max_z': max_z,
    }
    
    return z, stats


def compute_edge_tangents(mask):
    """
    Compute edge tangent directions at each pixel using distance transform gradient.
    
    The tangent is perpendicular to the inward normal (rotated 90°).
    
    Returns:
        tangent_y, tangent_x: Arrays of tangent vector components (along edge)
        normal_y, normal_x: Arrays of normal vector components (perpendicular to edge, inward)
    """
    from scipy.ndimage import distance_transform_edt
    
    # Compute distance transform of the mask interior
    # Gradient of distance transform points toward the center (inward normal)
    dist = distance_transform_edt(mask)
    
    # Compute gradient of distance field (points inward, toward medial axis)
    grad_y = np.zeros_like(dist)
    grad_x = np.zeros_like(dist)
    
    # Central differences
    grad_y[1:-1, :] = (dist[2:, :] - dist[:-2, :]) / 2
    grad_x[:, 1:-1] = (dist[:, 2:] - dist[:, :-2]) / 2
    
    # Normalize to unit vectors (these are inward normals)
    magnitude = np.sqrt(grad_y**2 + grad_x**2) + 1e-10
    normal_y = grad_y / magnitude
    normal_x = grad_x / magnitude
    
    # Tangent is perpendicular to normal: rotate 90° counterclockwise
    # If normal = (ny, nx), tangent = (-nx, ny)
    tangent_y = -normal_x
    tangent_x = normal_y
    
    return tangent_y, tangent_x, normal_y, normal_x


def compute_neck_score(stress, mask, sigma_smooth=2):
    """
    Compute neck_score that distinguishes true neck stress from edge artifacts.
    
    Two key factors:
    
    1. First derivative (tangential gradient):
       - True necks: Stress peaks at neck, drops off → HIGH gradient along edge
       - Edge artifacts: Stress constantly high → LOW gradient along edge
    
    2. Second derivative (curvature along edge):
       - True necks: Local maximum → NEGATIVE second derivative (concave down)
       - Edge artifacts: Constant or increasing → ~zero or positive second derivative
    
    neck_score = stress × |∂stress/∂tangent| × max(0, -∂²stress/∂tangent²)
    
    Parameters:
        stress: Stress field array
        mask: Binary mask of the region
        sigma_smooth: Smoothing sigma for gradient computation
    
    Returns:
        neck_score: Modified stress field that amplifies necks, suppresses edges
        debug_info: Dictionary with intermediate fields for visualization
    """
    H, W = stress.shape
    
    # Smooth stress for stable gradient computation
    stress_smooth = gaussian(stress, sigma=sigma_smooth)
    
    # ===== First derivatives =====
    # Compute stress gradient (standard spatial derivatives)
    stress_grad_y = np.zeros_like(stress)
    stress_grad_x = np.zeros_like(stress)
    
    # Central differences for first derivative
    stress_grad_y[1:-1, :] = (stress_smooth[2:, :] - stress_smooth[:-2, :]) / 2
    stress_grad_x[:, 1:-1] = (stress_smooth[:, 2:] - stress_smooth[:, :-2]) / 2
    
    # ===== Second derivatives =====
    # Compute second derivatives (Hessian components)
    stress_grad_yy = np.zeros_like(stress)  # ∂²stress/∂y²
    stress_grad_xx = np.zeros_like(stress)  # ∂²stress/∂x²
    stress_grad_xy = np.zeros_like(stress)  # ∂²stress/∂x∂y
    
    # Second derivative using central differences
    stress_grad_yy[1:-1, :] = stress_smooth[2:, :] - 2*stress_smooth[1:-1, :] + stress_smooth[:-2, :]
    stress_grad_xx[:, 1:-1] = stress_smooth[:, 2:] - 2*stress_smooth[:, 1:-1] + stress_smooth[:, :-2]
    
    # Mixed partial (cross derivative)
    stress_grad_xy[1:-1, 1:-1] = (stress_smooth[2:, 2:] - stress_smooth[2:, :-2] 
                                  - stress_smooth[:-2, 2:] + stress_smooth[:-2, :-2]) / 4
    
    # Get edge tangent and normal directions
    tangent_y, tangent_x, normal_y, normal_x = compute_edge_tangents(mask)
    
    # ===== First derivative along tangent =====
    # ∂stress/∂tangent = ∇stress · tangent
    tangential_gradient = stress_grad_y * tangent_y + stress_grad_x * tangent_x
    
    # Also compute normal gradient for debugging
    normal_gradient = stress_grad_y * normal_y + stress_grad_x * normal_x
    
    # ===== Second derivative along tangent =====
    # ∂²stress/∂tangent² = tangent^T · H · tangent
    # where H is the Hessian matrix [[∂²/∂y², ∂²/∂y∂x], [∂²/∂x∂y, ∂²/∂x²]]
    # = ty² * Hyy + 2*ty*tx * Hxy + tx² * Hxx
    tangential_second_deriv = (tangent_y**2 * stress_grad_yy + 
                               2 * tangent_y * tangent_x * stress_grad_xy + 
                               tangent_x**2 * stress_grad_xx)
    
    # ===== Compute gradient magnitude for normalization =====
    grad_magnitude = np.sqrt(stress_grad_y**2 + stress_grad_x**2) + 1e-10
    
    # ===== Factor 1: Tangential gradient magnitude =====
    # High |tangential_gradient| = stress varies along edge = TRUE NECK
    abs_tangent_grad = np.abs(tangential_gradient)
    tangent_fraction = abs_tangent_grad / grad_magnitude
    
    # ===== Factor 2: Negative second derivative (local maximum) =====
    # At a true neck (local max), second derivative is NEGATIVE
    # We want to amplify negative values, suppress positive/zero
    # Use: max(0, -second_deriv) to keep only local maxima
    
    # Normalize second derivative for scale invariance
    max_second = np.abs(tangential_second_deriv[mask]).max() if mask.any() else 1.0
    normalized_second_deriv = tangential_second_deriv / (max_second + 1e-10)
    
    # Concavity factor: 1 at strong local max, 0 at inflection/local min
    # -normalized_second_deriv is positive at local max, negative at local min
    concavity_factor = np.clip(-normalized_second_deriv, 0, 1)
    
    # Alternative: softer transition using sigmoid-like function
    # concavity_factor = 1 / (1 + np.exp(normalized_second_deriv * 5))
    
    # ===== Combine factors =====
    # neck_score = stress × tangent_fraction × concavity_factor
    # 
    # True neck: high stress + high tangent_fraction + high concavity → HIGH score
    # Edge artifact: high stress + low tangent_fraction + low concavity → LOW score
    
    neck_score = stress_smooth * tangent_fraction * concavity_factor
    
    # Zero out outside mask
    neck_score[~mask] = 0
    
    debug_info = {
        'stress_smooth': stress_smooth,
        'stress_grad_y': stress_grad_y,
        'stress_grad_x': stress_grad_x,
        'stress_grad_yy': stress_grad_yy,
        'stress_grad_xx': stress_grad_xx,
        'stress_grad_xy': stress_grad_xy,
        'grad_magnitude': grad_magnitude,
        'tangent_y': tangent_y,
        'tangent_x': tangent_x,
        'normal_y': normal_y,
        'normal_x': normal_x,
        'tangential_gradient': tangential_gradient,
        'abs_tangent_grad': abs_tangent_grad,
        'normal_gradient': normal_gradient,
        'tangent_fraction': tangent_fraction,
        'tangential_second_deriv': tangential_second_deriv,
        'normalized_second_deriv': normalized_second_deriv,
        'concavity_factor': concavity_factor,
    }
    
    return neck_score, debug_info


def compute_neck_score_z(stress, mask, sigma_smooth=2):
    """
    Compute neck_score and return z-scores for thresholding.
    
    Returns:
        neck_score: Raw neck score field
        z: Z-scores of neck_score
        stats: Statistics dict with peak_to_mean and max_z
        debug_info: Intermediate fields for visualization
    """
    neck_score, debug_info = compute_neck_score(stress, mask, sigma_smooth)
    
    # Compute z-scores on neck_score
    z = np.zeros_like(neck_score)
    
    vals = neck_score[mask]
    if len(vals) == 0 or vals.max() < 1e-10:
        return neck_score, z, {'peak_to_mean': 1.0, 'max_z': 0.0}, debug_info
    
    # Use log transform for z-score (same as regular stress)
    vals_positive = vals[vals > 0]
    if len(vals_positive) == 0:
        return neck_score, z, {'peak_to_mean': 1.0, 'max_z': 0.0}, debug_info
    
    vals_log = np.log1p(vals_positive)
    mean_log = vals_log.mean()
    std_log = vals_log.std()
    
    if std_log < 1e-10:
        return neck_score, z, {'peak_to_mean': 1.0, 'max_z': 0.0}, debug_info
    
    # Only compute z-scores for positive neck_score values
    positive_mask = mask & (neck_score > 0)
    neck_score_log = np.log1p(neck_score)
    z[positive_mask] = (neck_score_log[positive_mask] - mean_log) / std_log
    
    max_score = vals.max()
    mean_score = vals[vals > 0].mean() if (vals > 0).any() else 1e-10
    peak_to_mean = max_score / (mean_score + 1e-10)
    max_z = z[mask].max() if mask.any() else 0
    
    stats = {
        'peak_to_mean': peak_to_mean,
        'max_z': max_z,
    }
    
    return neck_score, z, stats, debug_info


