import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import metrics  # noqa: E402


def test_confusion_matrix_and_prf():
    y_true = [0, 0, 1, 1, 2, 2]
    y_pred = [0, 1, 1, 1, 2, 0]
    cm = metrics.confusion_matrix(y_true, y_pred, 3)
    assert cm.tolist() == [[1, 1, 0], [0, 2, 0], [1, 0, 1]]
    p, r, f = metrics.precision_recall_f1(cm)
    assert math.isclose(p[0], 0.5) and math.isclose(r[0], 0.5)
    assert math.isclose(p[1], 2 / 3) and math.isclose(r[1], 1.0)
    assert math.isclose(p[2], 1.0) and math.isclose(r[2], 0.5)


def test_undefined_metric_is_nan_not_zero():
    cm = metrics.confusion_matrix([0, 0], [0, 0], 2)  # class 1 absent and never predicted
    p, r, f = metrics.precision_recall_f1(cm)
    assert np.isnan(p[1]) and np.isnan(r[1]) and np.isnan(f[1])


def test_bootstrap_resamples_videos_not_frames():
    # video A perfect, video B always wrong. Frame counts are very uneven.
    y_true = [0] * 100 + [1] * 2
    y_pred = [0] * 100 + [0] * 2
    groups = ["A"] * 100 + ["B"] * 2
    res = metrics.bootstrap_by_group(y_true, y_pred, groups, 2, n_boot=500, seed=1)
    lo, hi, n = res["recall"][1]
    # recall for class 1 is 0 whenever B is drawn, and undefined when only A is drawn
    assert hi == 0.0
    # with 2 videos, P(B never drawn) = 0.25, so about a quarter of replicates are undefined
    assert 300 < n < 450


def test_bootstrap_is_reproducible():
    rng = np.random.default_rng(0)
    y_true = rng.integers(0, 3, 300)
    y_pred = np.where(rng.random(300) < 0.8, y_true, rng.integers(0, 3, 300))
    groups = rng.integers(0, 10, 300)
    a = metrics.bootstrap_by_group(y_true, y_pred, groups, 3, n_boot=200, seed=7)
    b = metrics.bootstrap_by_group(y_true, y_pred, groups, 3, n_boot=200, seed=7)
    assert a == b


def test_json_safe_turns_nan_into_null_and_output_is_valid_json():
    import json

    out = metrics.dumps_strict({"a": float("nan"), "b": [1.0, float("inf")], "c": np.float64(0.5), "d": {"e": None}})
    back = json.loads(out, parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
    assert back == {"a": None, "b": [1.0, None], "c": 0.5, "d": {"e": None}}
