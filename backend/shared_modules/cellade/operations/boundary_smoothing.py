"""
CellADE boundary smoothing — FFT and morphological smoothing.
"""

import numpy as np
from skimage.measure import regionprops, label as relabel, find_contours
from skimage.morphology import disk, opening, closing
from skimage.draw import polygon
from scipy.ndimage import binary_dilation, binary_erosion

from ..utils import get_mask_contour

def resample_contour(contour, n_points):
    """Resample contour to uniform spacing with n_points."""
    # Compute cumulative arc length
    diffs = np.diff(contour, axis=0)
    segment_lengths = np.sqrt((diffs**2).sum(axis=1))
    cumulative = np.concatenate([[0], np.cumsum(segment_lengths)])
    total_length = cumulative[-1]
    
    if total_length < 1e-10:
        return contour
    
    # Uniform samples along arc length
    uniform_positions = np.linspace(0, total_length, n_points, endpoint=False)
    
    # Interpolate
    resampled = np.zeros((n_points, 2))
    resampled[:, 0] = np.interp(uniform_positions, cumulative, contour[:, 0])
    resampled[:, 1] = np.interp(uniform_positions, cumulative, contour[:, 1])
    
    return resampled


def fft_smooth_contour(contour, keep_fraction=None, min_wavelength_pixels=6, amplitude_threshold=0.1):
    """
    Smooth contour using FFT filter based on wavelength and amplitude.
    
    Instead of keeping a fixed fraction of frequencies, we filter based on:
    1. Wavelength: Remove features smaller than min_wavelength_pixels
    2. Amplitude: Keep high-amplitude features even at higher frequencies
    
    Parameters:
        contour: Nx2 array of (y, x) coordinates
        keep_fraction: (deprecated) If provided, falls back to old behavior
        min_wavelength_pixels: Minimum feature size to keep (default 6 pixels)
                              Features smaller than this are considered noise
        amplitude_threshold: Relative amplitude threshold (0-1). 
                            Frequencies with amplitude < threshold * max_amplitude are removed.
    
    Returns:
        smoothed: Smoothed contour
    """
    n = len(contour)
    if n < 10:
        return contour
    
    # Convert to complex signal: z = x + i*y
    z = contour[:, 1] + 1j * contour[:, 0]
    
    # FFT
    Z = np.fft.fft(z)
    
    # Compute perimeter length for wavelength calculation
    diffs = np.diff(contour, axis=0, append=contour[:1])
    segment_lengths = np.sqrt(diffs[:, 0]**2 + diffs[:, 1]**2)
    perimeter = segment_lengths.sum()
    
    # For each frequency k, the wavelength is: perimeter / k
    # We want to remove frequencies where wavelength < min_wavelength_pixels
    # i.e., remove k where k > perimeter / min_wavelength_pixels
    
    # Frequency indices: 0, 1, 2, ..., n/2, ..., -2, -1
    # The actual frequency for index k is: k for k <= n/2, else n-k
    freq_indices = np.fft.fftfreq(n, d=1.0) * n  # Get actual frequency numbers
    freq_indices = np.abs(freq_indices)
    
    # Wavelength for each frequency component
    # wavelength[k] = perimeter / k (for k > 0)
    wavelengths = np.zeros(n)
    wavelengths[0] = np.inf  # DC component (mean position)
    wavelengths[1:] = perimeter / freq_indices[1:]
    
    # Compute amplitude spectrum
    amplitudes = np.abs(Z)
    max_amplitude = amplitudes[1:].max() if n > 1 else 1.0  # Exclude DC
    
    # Build filter based on wavelength AND amplitude
    # Keep if: wavelength >= min_wavelength OR amplitude >= threshold * max
    Z_filtered = np.zeros_like(Z)
    
    for k in range(n):
        if k == 0:
            # Always keep DC component (mean position)
            Z_filtered[k] = Z[k]
        elif wavelengths[k] >= min_wavelength_pixels:
            # Wavelength is large enough - keep it
            Z_filtered[k] = Z[k]
        elif amplitudes[k] >= amplitude_threshold * max_amplitude:
            # High amplitude - might be a real feature, keep it
            Z_filtered[k] = Z[k]
        # else: small wavelength AND low amplitude = noise, remove it
    
    # Inverse FFT
    z_filtered = np.fft.ifft(Z_filtered)
    
    # Convert back to contour
    smoothed = np.zeros_like(contour)
    smoothed[:, 0] = np.imag(z_filtered)  # y
    smoothed[:, 1] = np.real(z_filtered)  # x
    
    return smoothed


def fft_smooth_contour_legacy(contour, keep_fraction):
    """
    Legacy FFT smoothing using simple fraction-based cutoff.
    Kept for backwards compatibility.
    """
    n = len(contour)
    if n < 10:
        return contour
    
    z = contour[:, 1] + 1j * contour[:, 0]
    Z = np.fft.fft(z)
    
    n_keep = max(1, int(n * keep_fraction / 2))
    
    Z_filtered = np.zeros_like(Z)
    Z_filtered[:n_keep] = Z[:n_keep]
    if n_keep > 1:
        Z_filtered[-n_keep+1:] = Z[-n_keep+1:]
    
    z_filtered = np.fft.ifft(Z_filtered)
    
    smoothed = np.zeros_like(contour)
    smoothed[:, 0] = np.imag(z_filtered)
    smoothed[:, 1] = np.real(z_filtered)
    
    return smoothed


def contour_to_mask(contour, shape):
    """Convert contour back to binary mask."""
    from skimage.draw import polygon
    
    # Clip contour to valid range
    contour_clipped = contour.copy()
    contour_clipped[:, 0] = np.clip(contour_clipped[:, 0], 0, shape[0] - 1)
    contour_clipped[:, 1] = np.clip(contour_clipped[:, 1], 0, shape[1] - 1)
    
    rr, cc = polygon(contour_clipped[:, 0], contour_clipped[:, 1], shape)
    mask = np.zeros(shape, dtype=bool)
    if len(rr) > 0:
        mask[rr, cc] = True
    return mask


def morphological_smooth_mask(mask, radius=2):
    """
    Smooth a binary mask using morphological opening (erosion then dilation).
    
    This acts like physical filing - removes small protrusions while
    preserving the overall shape and concave features.
    
    Parameters:
        mask: Binary mask to smooth
        radius: Radius of the disk structuring element (default 2)
    
    Returns:
        smoothed_mask: Smoothed binary mask
    """
    from skimage.morphology import binary_opening, disk
    
    radius_int = max(1, int(round(radius)))
    
    if radius_int <= 0:
        return mask.copy()
    
    selem = disk(radius_int)
    
    # Opening: erosion followed by dilation
    # Removes small protrusions (like filing)
    smoothed = binary_opening(mask, selem)
    
    # Ensure we don't lose the region entirely
    if smoothed.sum() < 0.5 * mask.sum():
        # Opening removed too much, return original
        return mask.copy()
    
    return smoothed


def morphological_smooth_all_regions(labels, params):
    """
    Apply morphological opening to all regions for edge filing.
    
    Parameters:
        labels: Label array where each unique value > 0 is a region
        params: Dictionary containing:
            - use_morphological_smoothing: Whether to apply smoothing (default False)
            - morphological_base_radius: Base radius for opening (default 2)
            - morphological_aggressiveness: Multiplier for radius (default 1.0, try 1.5-2.0 for more aggressive)
              Actual radius = base_radius * aggressiveness * sqrt(area) / sqrt(median_area)
              So median-sized cell gets base_radius * aggressiveness
            - verbose_filing: Verbose output (default False)
    
    Returns:
        smoothed_labels: Label array with filed/smoothed boundaries
    """
    use_morph_smoothing = params.get('use_morphological_smoothing', False)
    base_radius = params.get('morphological_base_radius', 2)
    aggressiveness = params.get('morphological_aggressiveness', 1.0)
    verbose = params.get('verbose_filing', False)
    
    if not use_morph_smoothing or base_radius <= 0:
        return labels.copy()
    
    H, W = labels.shape
    smoothed_labels = np.zeros_like(labels)
    
    region_ids = [rid for rid in np.unique(labels) if rid > 0]
    
    # Compute areas for all regions (excluding very small ones)
    areas = []
    for region_id in region_ids:
        area = (labels == region_id).sum()
        if area >= 50:
            areas.append(area)
    
    if not areas:
        return labels.copy()
    
    # Adaptive reference_size: sqrt of median area
    # This means median-sized cell gets exactly base_radius * aggressiveness
    median_area = np.median(areas)
    reference_size = np.sqrt(median_area)
    
    effective_base = base_radius * aggressiveness
    if verbose:
        print(f"    Morphological smoothing (base={base_radius}, aggr={aggressiveness}, effective={effective_base:.1f}, ref_size={reference_size:.1f})...")
    
    # Track radii used for debugging
    radii_used = []
    
    for region_id in region_ids:
        mask = (labels == region_id)
        original_area = mask.sum()
        
        # Skip very small regions
        if original_area < 50:
            smoothed_labels[mask] = region_id
            continue
        
        # Adaptive radius: radius = base_radius * aggressiveness * sqrt(area) / reference_size
        adaptive_radius = effective_base * np.sqrt(original_area) / reference_size
        radius_int = max(1, int(round(adaptive_radius)))
        radii_used.append((original_area, adaptive_radius, radius_int))
        
        # Apply morphological opening with adaptive radius
        smoothed_mask = morphological_smooth_mask(mask, radius=adaptive_radius)
        
        # Store in output (handle potential overlaps)
        new_pixels = smoothed_mask & (smoothed_labels == 0)
        smoothed_labels[new_pixels] = region_id
    
    # Print radius statistics
    if verbose and radii_used:
        areas_used = [r[0] for r in radii_used]
        radii_float = [r[1] for r in radii_used]
        radii_int = [r[2] for r in radii_used]
        print(f"      Areas: min={min(areas_used)}, max={max(areas_used)}, median={np.median(areas_used):.0f}")
        print(f"      Radii (float): min={min(radii_float):.2f}, max={max(radii_float):.2f}, median={np.median(radii_float):.2f}")
        print(f"      Radii (int): {dict(zip(*np.unique(radii_int, return_counts=True)))}")
    
    # Handle any pixels that were in original but not in smoothed
    # Use fast nearest-neighbor assignment via distance transform
    missing_pixels = (labels > 0) & (smoothed_labels == 0)
    n_missing = missing_pixels.sum()
    
    if n_missing > 0:
        from scipy.ndimage import distance_transform_edt
        
        # Create distance transform from all smoothed regions combined
        # Then assign each missing pixel to its nearest region
        smoothed_fg = smoothed_labels > 0
        
        if smoothed_fg.any():
            # For each missing pixel, find which region is closest
            # We do this by computing distance to background for each region
            # and picking the region with minimum distance
            
            # Get missing pixel coordinates
            missing_ys, missing_xs = np.where(missing_pixels)
            
            # For each region, compute distance from every pixel to that region
            min_distances = np.full((H, W), np.inf)
            nearest_region = np.zeros((H, W), dtype=labels.dtype)
            
            for region_id in region_ids:
                region_mask = (smoothed_labels == region_id)
                if not region_mask.any():
                    # Region was completely removed by opening, use original
                    region_mask = (labels == region_id)
                if not region_mask.any():
                    continue
                
                # Distance from each pixel to this region
                dist = distance_transform_edt(~region_mask)
                
                # Update nearest region where this is closer
                closer = dist < min_distances
                min_distances[closer] = dist[closer]
                nearest_region[closer] = region_id
            
            # Assign missing pixels to nearest region
            smoothed_labels[missing_pixels] = nearest_region[missing_pixels]
        
        if verbose:
            print(f"      Reassigned {n_missing} pixels from filing")
    
    return smoothed_labels


def smooth_mask_fft(mask, keep_fraction=None, n_resample_points=256, 
                    min_wavelength_pixels=6, amplitude_threshold=0.1):
    """
    Smooth a binary mask by FFT filtering its boundary.
    
    Parameters:
        mask: Binary mask to smooth
        keep_fraction: (deprecated) If provided, uses legacy fraction-based filter
        n_resample_points: Number of points to resample contour to (higher = more detail)
        min_wavelength_pixels: Minimum feature size to keep in pixels (default 6)
                              Features smaller than this are removed as noise
        amplitude_threshold: Relative amplitude threshold (0-1).
                            High-amplitude features are kept even if small.
    
    Returns:
        smoothed_mask: Smoothed binary mask
        contour_original: Original contour (for debugging)
        contour_smoothed: Smoothed contour (for debugging)
    """
    # Extract contour
    contour = get_mask_contour(mask)
    if contour is None or len(contour) < 10:
        return mask, None, None
    
    # Resample to uniform spacing
    contour_resampled = resample_contour(contour, n_resample_points)
    
    # FFT smooth - use new wavelength-based or legacy method
    if keep_fraction is not None:
        # Legacy mode for backwards compatibility
        contour_smoothed = fft_smooth_contour_legacy(contour_resampled, keep_fraction)
    else:
        # New wavelength-based smoothing
        contour_smoothed = fft_smooth_contour(
            contour_resampled, 
            min_wavelength_pixels=min_wavelength_pixels,
            amplitude_threshold=amplitude_threshold
        )
    
    # Convert back to mask
    smoothed_mask = contour_to_mask(contour_smoothed, mask.shape)
    
    # Ensure we don't lose too much area (sanity check)
    original_area = mask.sum()
    smoothed_area = smoothed_mask.sum()
    
    if smoothed_area < 0.5 * original_area:
        # Smoothing removed too much, return original
        return mask, contour_resampled, contour_smoothed
    
    return smoothed_mask, contour_resampled, contour_smoothed


def smooth_all_regions(labels, params):
    """
    Apply FFT smoothing to all regions in a label map.
    
    Parameters:
        labels: Label array where each unique value > 0 is a region
        params: Dictionary containing:
            - use_fft_smoothing: Whether to apply smoothing
            - fft_n_points: Number of contour points for resampling
            - fft_min_wavelength: Minimum feature size in pixels (default 6)
            - fft_amplitude_threshold: Relative amplitude threshold (default 0.1)
            - fft_keep_fraction: (deprecated) If set, uses legacy mode
            - verbose_smooth: Verbose output (default False)
    
    Returns:
        smoothed_labels: Label array with smoothed boundaries
        smoothing_info: Dictionary with debug info for each region
    """
    use_fft_smoothing = params.get('use_fft_smoothing', True)
    n_points = params.get('fft_n_points', 256)
    min_wavelength = params.get('fft_min_wavelength', 6)  # pixels
    amplitude_threshold = params.get('fft_amplitude_threshold', 0.1)
    keep_fraction = params.get('fft_keep_fraction', None)  # Legacy, None = use new method
    verbose = params.get('verbose_smooth', False)
    
    if not use_fft_smoothing:
        return labels.copy(), {}
    
    H, W = labels.shape
    smoothed_labels = np.zeros_like(labels)
    smoothing_info = {}
    
    region_ids = [rid for rid in np.unique(labels) if rid > 0]
    
    if verbose:
        if keep_fraction is not None:
            print(f"    Smoothing {len(region_ids)} regions (legacy mode: keep_fraction={keep_fraction})...")
        else:
            print(f"    Smoothing {len(region_ids)} regions (min_wavelength={min_wavelength}px, amp_thresh={amplitude_threshold})...")
    
    for region_id in region_ids:
        mask = (labels == region_id)
        original_area = mask.sum()
        
        # Skip very small regions
        if original_area < 50:
            smoothed_labels[mask] = region_id
            continue
        
        # Smooth this region
        smoothed_mask, contour_orig, contour_smooth = smooth_mask_fft(
            mask, 
            keep_fraction=keep_fraction,  # None = use new method
            n_resample_points=n_points,
            min_wavelength_pixels=min_wavelength,
            amplitude_threshold=amplitude_threshold
        )
        
        smoothed_area = smoothed_mask.sum()
        
        # Store in output (handle potential overlaps by giving priority to existing labels)
        # First pass: only fill where smoothed_labels is still 0
        new_pixels = smoothed_mask & (smoothed_labels == 0)
        smoothed_labels[new_pixels] = region_id
        
        smoothing_info[region_id] = {
            'original_area': original_area,
            'smoothed_area': smoothed_area,
            'area_change': smoothed_area - original_area,
            'contour_original': contour_orig,
            'contour_smoothed': contour_smooth,
            'original_mask': mask.copy(),
            'smoothed_mask': smoothed_mask.copy(),
        }
    
    # Handle any pixels that were in original but not in smoothed (due to smoothing shrinkage)
    # Assign them to nearest region
    missing_pixels = (labels > 0) & (smoothed_labels == 0)
    n_missing = missing_pixels.sum()
    
    if n_missing > 0:
        if verbose:
            print(f"    Reassigning {n_missing} pixels lost during smoothing...")
        from scipy.ndimage import distance_transform_edt
        
        # For each region, compute distance transform
        for region_id in region_ids:
            region_mask = (smoothed_labels == region_id)
            if region_mask.sum() == 0:
                continue
            
            # Find missing pixels that were originally this region
            orig_region = (labels == region_id)
            missing_from_this = missing_pixels & orig_region
            
            if missing_from_this.sum() > 0:
                # Just assign back to original region
                smoothed_labels[missing_from_this] = region_id
    
    # Relabel to ensure consecutive IDs
    smoothed_labels, _ = relabel(smoothed_labels, return_num=True)
    
    total_orig = (labels > 0).sum()
    total_smooth = (smoothed_labels > 0).sum()
    if verbose:
        print(f"    Smoothing complete: {total_orig} → {total_smooth} pixels "
              f"({total_smooth - total_orig:+d})")
    
    return smoothed_labels, smoothing_info

