"""
CellADE evaluation — IoU-based F1 scoring (single version for CelLAB and the paper).

evaluate(pred, gt, iou_thresh=0.5) keeps all original keys:
    F1, Precision, Recall, TP, FP, FN, Pred, GT  (at iou_thresh)
    Empty image (no GT and no prediction): all F1/P/R = 1, meanIoU_matched = NaN.
    mAP       mean F1 over IoU 0.50:0.05:0.95 (kept for compatibility;
              in the paper call it "mean F1 over IoU 0.5-0.95", not mAP)
    Dice_FG   pixel-level foreground Dice
and adds:
    F1@0.50 ... F1@0.95   F1 at each IoU threshold (for F1-IoU curves)
    F1_mean_0.50-0.90     Caicedo et al. 2019 metric (BBBC039)
    F1_mean_0.50-0.95     same value as mAP
    meanIoU_matched       mean IoU of objects matched at iou_thresh

Matching: one-to-one, greedy by descending IoU, at IoU >= t
(identical to optimal matching for t >= 0.5).

Also: rgb_mask_to_labels (colour-coded GT masks), error_maps,
show_image_result, plot_f1_curve, summarize.
"""

import numpy as np
from skimage.measure import label as cc_label

THRESHOLDS = np.round(np.arange(0.50, 0.951, 0.05), 2)


# =================================================================
# IoU MATRIX AND MATCHING
# =================================================================

def iou_matrix(pred, gt):
    """IoU between every predicted and GT object (non-overlapping label maps).
    Vectorized via the pixel contingency table.
    Returns (iou [n_pred x n_gt], pred_ids, gt_ids)."""
    pred = np.asarray(pred)
    gt = np.asarray(gt)
    p_ids = np.unique(pred[pred > 0])
    g_ids = np.unique(gt[gt > 0])
    iou = np.zeros((len(p_ids), len(g_ids)))
    if len(p_ids) == 0 or len(g_ids) == 0:
        return iou, p_ids, g_ids
    p_idx = np.zeros(int(pred.max()) + 1, dtype=np.int64)
    p_idx[p_ids] = np.arange(len(p_ids))
    g_idx = np.zeros(int(gt.max()) + 1, dtype=np.int64)
    g_idx[g_ids] = np.arange(len(g_ids))
    p_area = np.bincount(p_idx[pred[pred > 0]], minlength=len(p_ids))
    g_area = np.bincount(g_idx[gt[gt > 0]], minlength=len(g_ids))
    both = (pred > 0) & (gt > 0)
    if both.any():
        code = p_idx[pred[both]] * len(g_ids) + g_idx[gt[both]]
        uniq, inter = np.unique(code, return_counts=True)
        i, j = uniq // len(g_ids), uniq % len(g_ids)
        iou[i, j] = inter / (p_area[i] + g_area[j] - inter)
    return iou, p_ids, g_ids


def match(iou, t):
    """One-to-one matching at IoU >= t, greedy by descending IoU.
    Returns list of (pred_index, gt_index, iou)."""
    ii, jj = np.nonzero(iou >= t)
    order = np.argsort(-iou[ii, jj], kind='stable')
    used_p, used_g, pairs = set(), set(), []
    for k in order:
        i, j = ii[k], jj[k]
        if i not in used_p and j not in used_g:
            used_p.add(i)
            used_g.add(j)
            pairs.append((i, j, iou[i, j]))
    return pairs


def _prf(tp, n_pred, n_gt):
    p = tp / n_pred if n_pred else 0.0
    r = tp / n_gt if n_gt else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return p, r, f1


# =================================================================
# MAIN METRIC
# =================================================================

def evaluate(pred, gt, iou_thresh=0.5):
    """Compute F1, Precision, Recall, mAP (mean F1), Dice_FG and the F1 curve."""
    pred = np.asarray(pred)
    gt = np.asarray(gt)

    pred_fg, gt_fg = pred > 0, gt > 0
    denom = pred_fg.sum() + gt_fg.sum()
    dice_fg = 2 * np.logical_and(pred_fg, gt_fg).sum() / denom if denom > 0 else 0

    iou, p_ids, g_ids = iou_matrix(pred, gt)
    n_p, n_g = len(p_ids), len(g_ids)

    out = {}
    if n_p == 0 and n_g == 0:
        # nothing annotated and nothing predicted: perfect agreement
        out.update({'F1': 1.0, 'Precision': 1.0, 'Recall': 1.0,
                    'TP': 0, 'FP': 0, 'FN': 0, 'Pred': 0, 'GT': 0,
                    'mAP': 1.0, 'Dice_FG': 1.0, 'meanIoU_matched': np.nan})
        for t in THRESHOLDS:
            out[f'F1@{t:.2f}'] = 1.0
        out['F1_mean_0.50-0.90'] = 1.0
        out['F1_mean_0.50-0.95'] = 1.0
        return out
    if n_p == 0 or n_g == 0:
        out.update({'F1': 0, 'Precision': 0, 'Recall': 0,
                    'TP': 0, 'FP': n_p, 'FN': n_g, 'Pred': n_p, 'GT': n_g,
                    'mAP': 0, 'Dice_FG': dice_fg, 'meanIoU_matched': 0.0})
        for t in THRESHOLDS:
            out[f'F1@{t:.2f}'] = 0.0
        out['F1_mean_0.50-0.90'] = 0.0
        out['F1_mean_0.50-0.95'] = 0.0
        return out

    # at the requested threshold
    pairs = match(iou, iou_thresh)
    tp = len(pairs)
    p, r, f1 = _prf(tp, n_p, n_g)
    out.update({'F1': f1, 'Precision': p, 'Recall': r,
                'TP': tp, 'FP': n_p - tp, 'FN': n_g - tp,
                'Pred': n_p, 'GT': n_g, 'Dice_FG': dice_fg,
                'meanIoU_matched': float(np.mean([x[2] for x in pairs])) if pairs else 0.0})

    # F1 curve over IoU thresholds
    f1s = np.array([_prf(len(match(iou, t)), n_p, n_g)[2] for t in THRESHOLDS])
    for t, v in zip(THRESHOLDS, f1s):
        out[f'F1@{t:.2f}'] = float(v)
    out['F1_mean_0.50-0.90'] = float(f1s[THRESHOLDS <= 0.90 + 1e-9].mean())
    out['F1_mean_0.50-0.95'] = float(f1s.mean())
    out['mAP'] = out['F1_mean_0.50-0.95']
    return out


# =================================================================
# GROUND-TRUTH LOADING
# =================================================================

def rgb_mask_to_labels(mask):
    """Instance labels from a colour-coded or label mask (e.g. BBBC039 PNGs).
    Each distinct value/colour is one class; connected components within it
    are split, so a colour reused for distant objects is handled."""
    m = np.asarray(mask)
    if m.ndim == 3:
        m = m[..., :3].astype(np.int64)
        code = (m[..., 0] << 16) | (m[..., 1] << 8) | m[..., 2]
    else:
        code = m.astype(np.int64)
    out = np.zeros(code.shape, dtype=np.int32)
    nxt = 1
    for c in np.unique(code):
        if c == 0:
            continue
        cc = cc_label(code == c, connectivity=1)
        out[cc > 0] = cc[cc > 0] + nxt - 1
        nxt += cc.max()
    return out


# =================================================================
# VISUALIZATION (matplotlib imported only when used)
# =================================================================

def error_maps(pred, gt, t=0.5):
    """Boolean maps: matched predictions, false positives, missed GT (IoU >= t)."""
    iou, p_ids, g_ids = iou_matrix(pred, gt)
    pairs = match(iou, t) if len(p_ids) and len(g_ids) else []
    tp_p = [p_ids[i] for i, _, _ in pairs]
    tp_g = {g_ids[j] for _, j, _ in pairs}
    tp = np.isin(pred, tp_p) & (pred > 0)
    fp = (pred > 0) & ~tp
    fn = np.isin(gt, list(set(g_ids) - tp_g)) & (gt > 0)
    return tp, fp, fn


def stretch(img, lo=1, hi=99.5):
    a = np.asarray(img, dtype=float)
    if a.ndim == 3:
        a = a.mean(axis=2)
    p0, p1 = np.percentile(a, [lo, hi])
    return np.clip((a - p0) / (p1 - p0 + 1e-12), 0, 1)


def show_image_result(img, gt, pred, metrics, title='', save=None):
    """Image | GT | prediction | errors at IoU 0.5 (green matched, red FP, blue missed)."""
    import matplotlib.pyplot as plt
    from skimage.segmentation import find_boundaries
    base = stretch(img)
    rgb = lambda: np.stack([base] * 3, -1)
    fig, ax = plt.subplots(1, 4, figsize=(16, 4.4))
    ax[0].imshow(base, cmap='gray')
    ax[0].set_title('Image')
    g = rgb()
    g[find_boundaries(gt, mode='inner')] = [0, 1, 1]
    ax[1].imshow(g)
    ax[1].set_title(f'GT ({metrics["GT"]})')
    p = rgb()
    p[find_boundaries(pred, mode='inner')] = [1, 1, 0]
    ax[2].imshow(p)
    ax[2].set_title(f'Prediction ({metrics["Pred"]})')
    tp, fp, fn = error_maps(pred, gt)
    e = rgb() * 0.6
    e[find_boundaries(np.where(tp, pred, 0), mode='inner')] = [0.1, 0.9, 0.1]
    e[find_boundaries(np.where(fp, pred, 0), mode='inner')] = [1.0, 0.2, 0.2]
    e[find_boundaries(np.where(fn, gt, 0), mode='inner')] = [0.2, 0.5, 1.0]
    ax[3].imshow(e)
    ax[3].set_title(f'F1@0.5={metrics["F1@0.50"]:.2f}  '
                    f'meanF1[.5:.9]={metrics["F1_mean_0.50-0.90"]:.2f}')
    for a in ax:
        a.axis('off')
    fig.suptitle(f'{title}   green: matched | red: false positive | blue: missed', fontsize=10)
    plt.tight_layout()
    if save:
        plt.savefig(save, dpi=150, facecolor='white')
    plt.show()


def plot_f1_curve(df, label='CellADE', ax=None, color='#388E3C', save=None):
    """Mean F1 vs IoU threshold with 95% bootstrap CI over images (df rows = images)."""
    import matplotlib.pyplot as plt
    F = df[[f'F1@{t:.2f}' for t in THRESHOLDS]].to_numpy()
    mean = F.mean(axis=0)
    rng = np.random.default_rng(0)
    boots = np.array([F[rng.integers(0, len(F), len(F))].mean(axis=0) for _ in range(1000)])
    lo, hi = np.percentile(boots, [2.5, 97.5], axis=0)
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(4.5, 3.5))
    ax.plot(THRESHOLDS, mean, '-o', color=color, ms=3, label=label)
    ax.fill_between(THRESHOLDS, lo, hi, color=color, alpha=0.2)
    ax.set_xlabel('IoU threshold')
    ax.set_ylabel('F1')
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    if own:
        plt.tight_layout()
        if save:
            plt.savefig(save, dpi=150, facecolor='white')
        plt.show()
    return ax


def summarize(df):
    """Mean and std over images of the main metrics."""
    cols = ['GT', 'Pred', 'F1', 'Precision', 'Recall', 'F1@0.75',
            'F1_mean_0.50-0.90', 'F1_mean_0.50-0.95', 'meanIoU_matched', 'Dice_FG', 'time_s']
    cols = [c for c in cols if c in df.columns]
    s = df[cols].agg(['mean', 'std']).T
    s.columns = ['mean', 'std']
    return s.round(3)
