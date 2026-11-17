"""Evaluate a crop classifier on the TEST split and write results.

    python train/evaluate.py [--model models/mobilenetv3s_best.pt] [--tag torch]
    python train/evaluate.py --onnx models/model_fp32.onnx --tag onnx_fp32

Reports (test split only, except the threshold which is chosen on validation):
  * per-class precision, recall, F1 with 95% bootstrap intervals resampled by video
  * confusion matrix over the 3 classes, and true subtype (bird, drone, background,
    airplane, helicopter) against the predicted class
  * per-video accuracy
  * bird-alert threshold: P(bird) cut-off chosen on the validation split, its cost
    on the test split, and the precision and recall at the firmware's default
  * average precision and PR curve points for P(bird)

Writes results/eval_<tag>.json (aggregates only) and, under results/local/
(gitignored), per-crop predictions and the misclassified list.
"""
import argparse
import collections
import json
import time
from pathlib import Path

import numpy as np
import torch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import data  # noqa: E402
import metrics  # noqa: E402

PRECISION_TARGET = 0.90  # illustrative alert requirement, not a measured need (docs/decisions.md D21)
FIRMWARE_DEFAULT_THRESHOLD = 0.85  # firmware/src/guardian.hpp Config::alert_threshold


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def torch_probs(model_path, rows):
    from train import build_model
    ck = torch.load(model_path, map_location="cpu")
    model = build_model(pretrained=False)
    model.load_state_dict(ck["state_dict"])
    model.eval()
    dl = torch.utils.data.DataLoader(data.CropDataset(rows, data.eval_transform()), batch_size=128, num_workers=0)
    out = []
    with torch.no_grad():
        for x, _ in dl:
            out.append(model(x).numpy())
    return softmax(np.concatenate(out))


def onnx_probs(onnx_path, rows):
    import onnxruntime as ort
    sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    name = sess.get_inputs()[0].name
    ds = data.CropDataset(rows, data.eval_transform())
    out = []
    for i in range(0, len(ds), 64):
        x = np.stack([ds[j][0].numpy() for j in range(i, min(i + 64, len(ds)))])
        out.append(sess.run(None, {name: x})[0])
    return softmax(np.concatenate(out))


def pr_curve(score, truth):
    """Precision and recall at every distinct score, plus average precision."""
    order = np.argsort(-score, kind="stable")
    s, t = score[order], truth[order]
    tp = np.cumsum(t)
    fp = np.cumsum(1 - t)
    last = np.r_[s[1:] != s[:-1], True]  # one point per distinct score
    prec = tp[last] / (tp[last] + fp[last])
    rec = tp[last] / max(t.sum(), 1)
    thr = s[last]
    ap = float(np.sum(np.diff(np.r_[0.0, rec]) * prec))
    return thr, prec, rec, ap


def choose_threshold(score_val, truth_val, target):
    """Lowest P(bird) threshold whose validation precision is at least `target`
    (that gives the highest recall under the constraint). None if unreachable."""
    thr, prec, rec, _ = pr_curve(score_val, truth_val)
    ok = np.where(prec >= target)[0]
    if len(ok) == 0:
        return None
    best = ok[np.argmax(rec[ok])]
    return float(thr[best])


def at_threshold(score, truth, groups, thr, n_boot=2000, seed=0):
    pred = (score >= thr).astype(int)
    summ = metrics.summarise(truth, pred, 2)
    ci = metrics.bootstrap_by_group(truth, pred, groups, 2, n_boot=n_boot, seed=seed)
    def f(a, i):
        return None if np.isnan(a[i]) else round(float(a[i]), 4)

    return {
        "threshold": round(float(thr), 4),
        "precision": f(summ["precision"], 1), "precision_ci95": ci["precision"][1][:2],
        "recall": f(summ["recall"], 1), "recall_ci95": ci["recall"][1][:2],
        "predicted_positive": int(pred.sum()), "true_positive": int(((pred == 1) & (truth == 1)).sum()),
    }


def subtype_accuracy_ci(correct, subtype, groups, which, n_boot=2000, seed=0):
    """Share of crops of one subtype predicted into their class, resampled by video."""
    m = subtype == which
    vids = sorted(set(groups[m].tolist()))
    c = np.array([correct[m & (groups == v)].sum() for v in vids], dtype=float)
    n = np.array([(m & (groups == v)).sum() for v in vids], dtype=float)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(vids), len(vids))
        vals.append(c[pick].sum() / n[pick].sum())
    return {"accuracy": round(float(c.sum() / n.sum()), 4), "n_crops": int(n.sum()), "n_videos": len(vids),
            "ci95": [round(float(np.percentile(vals, 2.5)), 4), round(float(np.percentile(vals, 97.5)), 4)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="models/mobilenetv3s_best.pt")
    ap.add_argument("--onnx", default=None)
    ap.add_argument("--tag", default="torch")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()

    test = data.read_manifest(split="test")
    val = data.read_manifest(split="val")
    index = json.loads(Path("data/index/index.json").read_text())["videos"]
    t0 = time.time()
    def probs_fn(rows):
        return onnx_probs(args.onnx, rows) if args.onnx else torch_probs(args.model, rows)

    p_test, p_val = probs_fn(test), probs_fn(val)
    wall = time.time() - t0

    def arrays(rows, p):
        y = np.array([data.CLASSES.index(r["class3"]) for r in rows])
        sub = np.array([r["subtype"] for r in rows])
        vid = np.array([r["video"] for r in rows])
        return y, p.argmax(1), sub, vid

    y, pred, sub, vid = arrays(test, p_test)
    nc = len(data.CLASSES)
    summ = metrics.summarise(y, pred, nc)
    ci = metrics.bootstrap_by_group(y, pred, vid, nc, n_boot=args.n_boot, seed=0)
    def rnd(x):
        return None if x is None or np.isnan(x) else round(float(x), 4)


    per_class = {}
    for i, c in enumerate(data.CLASSES):
        per_class[c] = {
            "support": int(summ["support"][i]),
            "precision": rnd(summ["precision"][i]), "precision_ci95": [rnd(ci["precision"][i][0]), rnd(ci["precision"][i][1])],
            "recall": rnd(summ["recall"][i]), "recall_ci95": [rnd(ci["recall"][i][0]), rnd(ci["recall"][i][1])],
            "f1": rnd(summ["f1"][i]), "f1_ci95": [rnd(ci["f1"][i][0]), rnd(ci["f1"][i][1])],
        }

    # true subtype (rows) against predicted class (columns)
    sub_conf = {s: [int(((sub == s) & (pred == j)).sum()) for j in range(nc)] for s in data.SUBTYPES}
    correct = (y == pred)
    sub_acc = {s: subtype_accuracy_ci(correct, sub, vid, s, args.n_boot) for s in data.SUBTYPES if (sub == s).any()}

    # per-video accuracy (crops of any subtype that came from that video)
    per_video = []
    for v in sorted(set(vid.tolist())):
        m = vid == v
        per_video.append({"video": v, "class": index[v]["class"], "distance_bin": index[v]["distance_bin"],
                          "n_crops": int(m.sum()), "accuracy": round(float(correct[m].mean()), 4)})

    # bird alert threshold: chosen on validation, applied to test
    yv = np.array([data.CLASSES.index(r["class3"]) for r in val])
    tv = (yv == 0).astype(int)
    tt = (y == 0).astype(int)
    sv, st = p_val[:, 0], p_test[:, 0]
    thr_val = choose_threshold(sv, tv, PRECISION_TARGET)
    _, _, _, ap_val = pr_curve(sv, tv)
    pt, pp, pr, ap_test = pr_curve(st, tt)
    keep = np.unique(np.linspace(0, len(pt) - 1, min(60, len(pt))).astype(int))
    threshold = {
        "score": "P(bird)", "validation_precision_target": PRECISION_TARGET,
        "chosen_on": "validation split", "average_precision_test": round(ap_test, 4),
        "average_precision_val": round(ap_val, 4),
        "pr_curve_test": [{"threshold": round(float(pt[i]), 4), "precision": round(float(pp[i]), 4),
                           "recall": round(float(pr[i]), 4)} for i in keep],
        "argmax_rule": at_threshold(st, tt, vid, 0.5, args.n_boot) | {"note": "P(bird) >= 0.5 (not the same as argmax over 3 classes)"},
        "firmware_default": at_threshold(st, tt, vid, FIRMWARE_DEFAULT_THRESHOLD, args.n_boot),
    }
    if thr_val is None:
        threshold["chosen"] = None
        threshold["note"] = "no validation threshold reaches the precision target"
    else:
        threshold["chosen"] = at_threshold(st, tt, vid, thr_val, args.n_boot)
        a, b = threshold["chosen"], threshold["argmax_rule"]
        threshold["cost_vs_0.5"] = {
            "recall_change": None if a["recall"] is None or b["recall"] is None else round(a["recall"] - b["recall"], 4),
            "precision_change": None if a["precision"] is None or b["precision"] is None else round(a["precision"] - b["precision"], 4)}

    videos_test = sorted(set(vid.tolist()))
    result = {
        "label": "measured (host CPU)",
        "command": f"python train/evaluate.py{' --onnx ' + args.onnx if args.onnx else ''} --tag {args.tag}",
        "split": "test", "n_crops": len(test), "n_videos": len(videos_test),
        "videos_per_class": dict(collections.Counter(index[v]["class"] for v in videos_test)),
        "crops_per_subtype": dict(collections.Counter(sub.tolist())),
        "bootstrap": {"method": "resample whole videos with replacement", "replicates": args.n_boot, "seed": 0,
                      "note": "treats videos as independent; videos from one scene are not, so intervals are optimistic"},
        "accuracy": rnd(summ["accuracy"]), "macro_f1": rnd(summ["macro_f1"]),
        "macro_f1_ci95": [rnd(ci["macro_f1"][0]), rnd(ci["macro_f1"][1])],
        "per_class": per_class,
        "confusion_matrix": {"rows_true": data.CLASSES, "cols_pred": data.CLASSES, "values": summ["confusion_matrix"].tolist()},
        "subtype_vs_predicted": {"cols_pred": data.CLASSES, "rows": sub_conf},
        "subtype_accuracy": sub_acc,
        "threshold": threshold,
        "per_video": per_video,
        "eval_wall_seconds_test_and_val": round(wall, 1),
    }
    Path("results").mkdir(exist_ok=True)
    Path(f"results/eval_{args.tag}.json").write_text(metrics.dumps_strict(result, indent=1))

    # local-only detail (gitignored): per-crop predictions and misclassified list
    loc = Path("results/local")
    loc.mkdir(parents=True, exist_ok=True)
    with open(loc / f"test_predictions_{args.tag}.csv", "w") as f:
        f.write("video,frame,subtype,true,pred,p_bird,p_drone,p_neither\n")
        for r, pr_, row in zip(test, pred, p_test):
            f.write(f'{r["video"]},{r["frame"]},{r["subtype"]},{r["class3"]},{data.CLASSES[pr_]},'
                    f'{row[0]:.4f},{row[1]:.4f},{row[2]:.4f}\n')
    print(json.dumps({k: result[k] for k in ("n_crops", "n_videos", "accuracy", "macro_f1", "macro_f1_ci95", "per_class")}, indent=1))
    print("subtype accuracy:", json.dumps(sub_acc))
    print("threshold chosen:", json.dumps(threshold.get("chosen")), "AP test", threshold["average_precision_test"])


if __name__ == "__main__":
    main()
