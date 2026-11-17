import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evaluate as ev  # noqa: E402


def test_pr_curve_perfect_ranking_has_ap_one():
    score = np.array([0.9, 0.8, 0.3, 0.2])
    truth = np.array([1, 1, 0, 0])
    thr, prec, rec, ap = ev.pr_curve(score, truth)
    assert ap == 1.0
    assert prec[1] == 1.0 and rec[1] == 1.0


def test_pr_curve_known_values():
    # ranked: pos, neg, pos -> precision 1.0, 0.5, 0.667 ; recall 0.5, 0.5, 1.0
    score = np.array([0.9, 0.8, 0.7])
    truth = np.array([1, 0, 1])
    thr, prec, rec, ap = ev.pr_curve(score, truth)
    assert np.allclose(prec, [1.0, 0.5, 2 / 3])
    assert np.allclose(rec, [0.5, 0.5, 1.0])
    assert np.isclose(ap, 0.5 * 1.0 + 0.0 + 0.5 * (2 / 3))


def test_ties_make_one_point():
    score = np.array([0.5, 0.5, 0.5, 0.1])
    truth = np.array([1, 0, 1, 0])
    thr, prec, rec, _ = ev.pr_curve(score, truth)
    assert len(thr) == 2 and np.isclose(prec[0], 2 / 3)


def test_choose_threshold_takes_highest_recall_meeting_target():
    score = np.array([0.95, 0.9, 0.8, 0.7, 0.6, 0.5])
    truth = np.array([1, 1, 0, 1, 1, 0])
    # at 0.9: precision 1.0, recall 0.5 ; at 0.7: precision 0.75 ; at 0.6: 0.8
    assert ev.choose_threshold(score, truth, 0.99) == 0.9
    assert ev.choose_threshold(score, truth, 0.79) == 0.6
    assert ev.choose_threshold(score, truth, 1.01) is None


def test_softmax_rows_sum_to_one():
    p = ev.softmax(np.array([[1.0, 2.0, 3.0], [1000.0, 0.0, -1000.0]]))
    assert np.allclose(p.sum(axis=1), 1.0) and not np.isnan(p).any()
