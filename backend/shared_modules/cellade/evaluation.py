"""
CellADE evaluation — IoU-based F1 scoring.
"""

import numpy as np
from skimage.measure import regionprops

def evaluate(pred, gt, iou_thresh=0.5):
    """Compute F1, Precision, Recall, mAP, and Dice (foreground).
    
    Optimized version using bounding boxes to skip non-overlapping regions.
    """
    from skimage.measure import regionprops
    
    pred_ids = set(np.unique(pred)) - {0}
    gt_ids = set(np.unique(gt)) - {0}
    
    if len(pred_ids) == 0 or len(gt_ids) == 0:
        return {'F1': 0, 'Precision': 0, 'Recall': 0, 
                'TP': 0, 'FP': len(pred_ids), 'FN': len(gt_ids),
                'Pred': len(pred_ids), 'GT': len(gt_ids),
                'mAP': 0, 'Dice_FG': 0}
    
    # Precompute bounding boxes and coords for all regions
    pred_props = {p.label: p for p in regionprops(pred)}
    gt_props = {p.label: p for p in regionprops(gt)}
    
    def bbox_overlap(bb1, bb2):
        """Check if two bounding boxes overlap."""
        # bb format: (min_row, min_col, max_row, max_col)
        return not (bb1[2] <= bb2[0] or bb2[2] <= bb1[0] or 
                   bb1[3] <= bb2[1] or bb2[3] <= bb1[1])
    
    # Precompute IoU matrix using bounding box optimization
    iou_matrix = {}  # (pid, gid) -> iou
    for pid in pred_ids:
        if pid not in pred_props:
            continue
        pred_prop = pred_props[pid]
        pred_bbox = pred_prop.bbox
        pred_coords = set(map(tuple, pred_prop.coords))
        pred_area = len(pred_coords)
        
        for gid in gt_ids:
            if gid not in gt_props:
                continue
            gt_prop = gt_props[gid]
            
            # Quick bounding box check - skip if no overlap
            if not bbox_overlap(pred_bbox, gt_prop.bbox):
                continue
            
            gt_coords = set(map(tuple, gt_prop.coords))
            gt_area = len(gt_coords)
            
            # Compute IoU using coordinate sets
            intersection = len(pred_coords & gt_coords)
            if intersection == 0:
                continue
            
            union = pred_area + gt_area - intersection
            iou = intersection / union if union > 0 else 0
            if iou > 0:
                iou_matrix[(pid, gid)] = iou
    
    # Match at the specified threshold (for F1)
    matched = set()
    for pid in pred_ids:
        best_iou, best_gt = 0, None
        for gid in gt_ids - matched:
            iou = iou_matrix.get((pid, gid), 0)
            if iou > best_iou:
                best_iou = iou
                best_gt = gid
        if best_iou >= iou_thresh and best_gt is not None:
            matched.add(best_gt)
    
    tp = len(matched)
    fp = len(pred_ids) - tp
    fn = len(gt_ids) - tp
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    # Compute mAP across IoU thresholds [0.5, 0.55, ..., 0.95]
    ap_list = []
    for thresh in np.arange(0.5, 1.0, 0.05):
        matched_t = set()
        for pid in pred_ids:
            best_iou, best_gt = 0, None
            for gid in gt_ids - matched_t:
                iou = iou_matrix.get((pid, gid), 0)
                if iou > best_iou:
                    best_iou = iou
                    best_gt = gid
            if best_iou >= thresh and best_gt is not None:
                matched_t.add(best_gt)
        tp_t = len(matched_t)
        fp_t = len(pred_ids) - tp_t
        fn_t = len(gt_ids) - tp_t
        prec_t = tp_t / (tp_t + fp_t) if (tp_t + fp_t) > 0 else 0
        rec_t = tp_t / (tp_t + fn_t) if (tp_t + fn_t) > 0 else 0
        f1_t = 2 * prec_t * rec_t / (prec_t + rec_t) if (prec_t + rec_t) > 0 else 0
        ap_list.append(f1_t)
    mAP = np.mean(ap_list)
    
    # Compute Dice for foreground (pixel-level, ignoring instance boundaries)
    pred_fg = (pred > 0)
    gt_fg = (gt > 0)
    intersection_fg = np.logical_and(pred_fg, gt_fg).sum()
    dice_fg = (2 * intersection_fg) / (pred_fg.sum() + gt_fg.sum()) if (pred_fg.sum() + gt_fg.sum()) > 0 else 0
    
    return {'F1': f1, 'Precision': precision, 'Recall': recall, 
            'TP': tp, 'FP': fp, 'FN': fn,
            'Pred': len(pred_ids), 'GT': len(gt_ids),
            'mAP': mAP, 'Dice_FG': dice_fg}


