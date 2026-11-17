"""Error analysis on the test split, from per-crop predictions.

    python train/error_analysis.py [--tag torch]

Reads results/local/test_predictions_<tag>.csv (written by train/evaluate.py), the crop
manifest and the video index. Writes results/error_analysis.json (aggregates, and the
video names and frame indices of misclassified crops; no images) and
results/local/misclassified_<tag>.csv.

What it checks, so every observation in docs/error-analysis.md has a number behind it:
error rate by distance bin, by object size (box area), by crop brightness and by crop
texture (pixel standard deviation), and per video.
"""
import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402


def tercile_rates(values, wrong, names=("low", "mid", "high")):
    values, wrong = np.asarray(values, float), np.asarray(wrong, bool)
    cuts = np.percentile(values, [100 / 3, 200 / 3])
    bins = np.digitize(values, cuts)
    out = {}
    for b, name in enumerate(names):
        m = bins == b
        out[name] = {"range": [round(float(values[m].min()), 2), round(float(values[m].max()), 2)],
                     "n": int(m.sum()), "error_rate": round(float(wrong[m].mean()), 4)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="torch")
    args = ap.parse_args()

    index = json.loads(Path("data/index/index.json").read_text())["videos"]
    rows = list(csv.DictReader(open(f"results/local/test_predictions_{args.tag}.csv")))
    test_manifest = [r for r in csv.DictReader(open("data/crops/manifest.csv")) if r["split"] == "test"]
    assert len(rows) == len(test_manifest)

    recs = []
    for p, m in zip(rows, test_manifest):  # same order as evaluate.py read them
        assert p["video"] == m["video"] and int(p["frame"]) == int(m["frame"])
        img = cv2.imread(m["path"], cv2.IMREAD_GRAYSCALE).astype(np.float32)
        box = [float(x) for x in m["box"].split(";")] if m["box"] else None
        recs.append({
            "video": p["video"], "frame": int(p["frame"]), "subtype": p["subtype"], "true": p["true"], "pred": p["pred"],
            "wrong": p["true"] != p["pred"], "distance": index[p["video"]]["distance_bin"],
            "box_area": None if box is None else box[2] * box[3],
            "brightness": float(img.mean()), "texture": float(img.std()),
            "p_bird": float(p["p_bird"]),
        })

    out = {"label": "measured (host CPU)", "command": f"python train/error_analysis.py --tag {args.tag}",
           "n_crops": len(recs), "n_wrong": sum(r["wrong"] for r in recs)}

    # by subtype and distance bin
    by = {}
    for sub in ("bird", "drone", "airplane", "helicopter", "background"):
        for dist in ("CLOSE", "MEDIUM", "DISTANT"):
            sel = [r for r in recs if r["subtype"] == sub and r["distance"] == dist]
            if sel:
                by[f"{sub}/{dist}"] = {"n": len(sel), "n_videos": len({r["video"] for r in sel}),
                                       "error_rate": round(sum(r["wrong"] for r in sel) / len(sel), 4)}
    out["error_rate_by_subtype_and_distance"] = by

    # by object size / brightness / texture, for crops that have a box (object crops)
    obj = [r for r in recs if r["box_area"] is not None]
    for key, label in (("box_area", "by_object_size_px2"), ("brightness", "by_crop_brightness_0_255"), ("texture", "by_crop_texture_std")):
        for group, sel in (("bird_and_drone", [r for r in obj if r["subtype"] in ("bird", "drone")]),
                           ("all_object_crops", obj)):
            if sel:
                out.setdefault(label, {})[group] = tercile_rates([r[key] for r in sel], [r["wrong"] for r in sel])
    bg = [r for r in recs if r["subtype"] == "background"]
    out["background_crops"] = {"n": len(bg), "errors": sum(r["wrong"] for r in bg)}
    out["background_errors_texture"] = [round(r["texture"], 2) for r in bg if r["wrong"]]

    # where do wrong predictions go
    conf = {}
    for r in recs:
        if r["wrong"]:
            conf[f'{r["subtype"]} -> {r["pred"]}'] = conf.get(f'{r["subtype"]} -> {r["pred"]}', 0) + 1
    out["wrong_by_subtype_to_predicted"] = dict(sorted(conf.items(), key=lambda kv: -kv[1]))

    # drone crops by scene cluster (split file is local-only; cluster ids are just labels)
    split_path = Path("train/splits/split_seed0.json")
    if split_path.exists():
        split = json.loads(split_path.read_text())["split"]
        sc = {}
        for r in recs:
            if r["subtype"] == "drone":
                d = sc.setdefault(split[r["video"]]["cluster"], {"videos": set(), "n": 0, "wrong": 0})
                d["videos"].add(r["video"])
                d["n"] += 1
                d["wrong"] += r["wrong"]
        out["drone_crops_by_scene"] = [
            {"scene_cluster": k, "n_videos": len(d["videos"]), "n_crops": d["n"], "error_rate": round(d["wrong"] / d["n"], 4),
             "distance_mix": {b: sum(1 for v in d["videos"] if index[v]["distance_bin"] == b) for b in ("CLOSE", "MEDIUM", "DISTANT")}}
            for k, d in sorted(sc.items())]

    # per video
    pv = {}
    for r in recs:
        v = pv.setdefault(r["video"], {"video": r["video"], "class": index[r["video"]]["class"], "distance": r["distance"], "n": 0, "wrong": 0, "wrong_frames": []})
        v["n"] += 1
        if r["wrong"]:
            v["wrong"] += 1
            v["wrong_frames"].append(r["frame"])
    per_video = sorted(pv.values(), key=lambda v: (-v["wrong"] / v["n"], -v["n"]))
    for v in per_video:
        v["accuracy"] = round(1 - v["wrong"] / v["n"], 4)
        v["wrong_frames"] = sorted(set(v["wrong_frames"]))
    out["videos_by_error_rate"] = per_video
    out["videos_all_correct"] = sum(1 for v in per_video if v["wrong"] == 0)
    out["videos_total"] = len(per_video)

    Path("results").mkdir(exist_ok=True)
    Path("results/error_analysis.json").write_text(metrics.dumps_strict(out, indent=1))
    with open(f"results/local/misclassified_{args.tag}.csv", "w") as f:
        f.write("video,frame,subtype,true,pred,p_bird,distance,box_area\n")
        for r in recs:
            if r["wrong"]:
                f.write(f'{r["video"]},{r["frame"]},{r["subtype"]},{r["true"]},{r["pred"]},{r["p_bird"]:.3f},{r["distance"]},{r["box_area"]}\n')
    print(json.dumps({k: out[k] for k in ("n_crops", "n_wrong", "error_rate_by_subtype_and_distance", "wrong_by_subtype_to_predicted", "videos_all_correct", "videos_total")}, indent=1))
    print(json.dumps({k: out.get(k) for k in ("by_object_size_px2", "by_crop_brightness_0_255", "by_crop_texture_std")}, indent=1)[:1800])


if __name__ == "__main__":
    main()
