"""Classification metrics with confidence intervals resampled by video.

Frames from one video are highly correlated, so the independent unit is the
video. The bootstrap therefore draws whole videos with replacement, not frames.
Pure numpy so it can be unit-tested without a model.
"""
import json
import math

import numpy as np


def confusion_matrix(y_true, y_pred, n_classes):
    """cm[i, j] = number of frames with true class i predicted as class j."""
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    cm = np.zeros((n_classes, n_classes), dtype=np.int64)
    np.add.at(cm, (y_true, y_pred), 1)
    return cm


def precision_recall_f1(cm):
    """Per-class precision, recall, F1 from a confusion matrix.

    A value is NaN when its denominator is zero (class never predicted, or
    class absent from the truth). NaN is kept, not replaced by 0, so an
    undefined metric is never reported as a measured one.
    """
    cm = np.asarray(cm, dtype=float)
    tp = np.diag(cm)
    with np.errstate(divide="ignore", invalid="ignore"):
        precision = np.where(cm.sum(axis=0) > 0, tp / cm.sum(axis=0), np.nan)
        recall = np.where(cm.sum(axis=1) > 0, tp / cm.sum(axis=1), np.nan)
        f1 = np.where(
            (precision + recall) > 0, 2 * precision * recall / (precision + recall), np.nan
        )
    return precision, recall, f1


def summarise(y_true, y_pred, n_classes):
    cm = confusion_matrix(y_true, y_pred, n_classes)
    p, r, f = precision_recall_f1(cm)
    return {
        "confusion_matrix": cm,
        "precision": p,
        "recall": r,
        "f1": f,
        "macro_f1": float(np.nanmean(f)) if not np.all(np.isnan(f)) else float("nan"),
        "accuracy": float(np.trace(cm) / cm.sum()) if cm.sum() else float("nan"),
        "support": cm.sum(axis=1),
    }


def per_group_results(y_true, y_pred, groups):
    """Per-video accuracy and frame counts. Returns {group: (n_frames, accuracy)}."""
    y_true, y_pred, groups = map(np.asarray, (y_true, y_pred, groups))
    out = {}
    for g in sorted(set(groups.tolist())):
        m = groups == g
        out[g] = (int(m.sum()), float((y_true[m] == y_pred[m]).mean()))
    return out


def bootstrap_by_group(y_true, y_pred, groups, n_classes, n_boot=2000, seed=0, alpha=0.05):
    """Percentile CIs for per-class recall, precision, F1 and macro-F1.

    Each replicate draws as many videos as the test set has, with replacement,
    and pools all their frames. A metric that is undefined in a replicate
    (NaN) is skipped for that replicate; the count of defined replicates is
    returned so a CI built from few replicates can be recognised.
    """
    y_true, y_pred, groups = map(np.asarray, (y_true, y_pred, groups))
    ids = np.array(sorted(set(groups.tolist())))
    # per-video confusion matrices: additive, so a replicate is a sum of them
    per_video = np.stack(
        [confusion_matrix(y_true[groups == g], y_pred[groups == g], n_classes) for g in ids]
    )
    rng = np.random.default_rng(seed)
    names = ["precision", "recall", "f1"]
    draws = {n: np.full((n_boot, n_classes), np.nan) for n in names}
    macro = np.full(n_boot, np.nan)
    for b in range(n_boot):
        pick = rng.integers(0, len(ids), size=len(ids))
        cm = per_video[pick].sum(axis=0)
        p, r, f = precision_recall_f1(cm)
        draws["precision"][b], draws["recall"][b], draws["f1"][b] = p, r, f
        if not np.all(np.isnan(f)):
            macro[b] = np.nanmean(f)
    lo, hi = 100 * alpha / 2, 100 * (1 - alpha / 2)

    def ci(a):
        a = a[~np.isnan(a)]
        if len(a) == 0:
            return (float("nan"), float("nan"), 0)
        return (float(np.percentile(a, lo)), float(np.percentile(a, hi)), int(len(a)))

    result = {n: [ci(draws[n][:, c]) for c in range(n_classes)] for n in names}
    result["macro_f1"] = ci(macro)
    result["n_videos"] = int(len(ids))
    result["n_boot"] = n_boot
    return result


def json_safe(obj):
    """Recursively turn NaN and infinity into None, and numpy scalars into Python numbers.

    An undefined metric (for example precision when nothing was predicted positive) must be
    written as null, never as the invalid JSON literal NaN and never as a made-up number.
    """
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, np.generic):
        obj = obj.item()
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    return obj


def dumps_strict(obj, **kw):
    """json.dumps after json_safe, refusing any NaN that slipped through."""
    return json.dumps(json_safe(obj), allow_nan=False, **kw)
