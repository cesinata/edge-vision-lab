"""Cut classification crops from the labelled frames, at a fixed frame stride.

    python train/make_crops.py [--stride 15] [--seed 0]
        [--split train/splits/split_seed0.json] [--index data/index/index.json]
        [--out data/crops]

Classes and subtypes:
  bird                  crops around bird boxes
  drone                 crops around drone boxes
  neither / background  crops from a region of a sampled frame that overlaps no
                        box, sized like a box from the same video
  neither / airplane    crops around airplane boxes (hard negatives)
  neither / helicopter  crops around helicopter boxes (hard negatives)

Every `stride`-th frame is sampled so adjacent frames do not dominate. Boxes in
a sampled frame each give one crop. One background crop is taken from every
second sampled frame. A crop is a square of side `CONTEXT * max(box w, h)`
(at least MIN_SIDE pixels), centred on the box and shifted to stay inside the
frame, resized to OUT x OUT.

A video belongs to one scene cluster and one split (train/make_split.py), so
every crop inherits its video's split; this script asserts that no cluster ends
up in two splits.

Outputs, all under data/ (gitignored, never published):
  data/crops/<split>/<class>/<name>.jpg   crops
  data/crops/manifest.csv                  one row per crop
and a counts-only summary at results/crops_summary.json.
"""
import argparse
import collections
import csv
import json
import random
from pathlib import Path

import cv2

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mat_labels import load_frame_boxes  # noqa: E402

CONTEXT = 2.0
MIN_SIDE = 48
OUT = 112
CLASS3 = {"BIRD": "bird", "DRONE": "drone", "AIRPLANE": "neither", "HELICOPTER": "neither"}
SUBTYPE = {"BIRD": "bird", "DRONE": "drone", "AIRPLANE": "airplane", "HELICOPTER": "helicopter"}


def crop_square(box, frame_w, frame_h):
    """Square crop (x0, y0, side) around a box (x, y, w, h), inside the frame."""
    x, y, w, h = box
    side = int(round(max(CONTEXT * max(w, h), MIN_SIDE)))
    side = min(side, frame_w, frame_h)
    cx, cy = x + w / 2.0, y + h / 2.0
    x0 = int(round(min(max(cx - side / 2.0, 0), frame_w - side)))
    y0 = int(round(min(max(cy - side / 2.0, 0), frame_h - side)))
    return x0, y0, side


def overlaps(x0, y0, side, boxes):
    """True if the square (x0, y0, side) intersects any box (x, y, w, h)."""
    for x, y, w, h in boxes:
        if x < x0 + side and x + w > x0 and y < y0 + side and y + h > y0:
            return True
    return False


def background_square(boxes, side, frame_w, frame_h, rng, tries=50):
    """A random square of the given side that overlaps no box, or None."""
    side = min(side, frame_w, frame_h)
    for _ in range(tries):
        x0 = rng.randint(0, frame_w - side)
        y0 = rng.randint(0, frame_h - side)
        if not overlaps(x0, y0, side, boxes):
            return x0, y0, side
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stride", type=int, default=15)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--split", default="train/splits/split_seed0.json")
    ap.add_argument("--index", default="data/index/index.json")
    ap.add_argument("--raw", default="data/raw/extracted")
    ap.add_argument("--out", default="data/crops")
    ap.add_argument("--summary", default="results/crops_summary.json")
    args = ap.parse_args()

    split = json.loads(Path(args.split).read_text())["split"]
    videos = json.loads(Path(args.index).read_text())["videos"]
    root = next(Path(args.raw).glob("*/Data/Video_V"))
    out = Path(args.out)
    rows = []

    for name in sorted(split):
        info, v = split[name], videos[name]
        cls = v["class"]
        boxes = load_frame_boxes(root / f"{name}_LABELS.mat", cls)
        rng = random.Random(f"{args.seed}-{name}")
        cap = cv2.VideoCapture(str(root / f"{name}.mp4"))
        k = 0
        sampled = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if k % args.stride == 0:
                h, w = frame.shape[:2]
                fb = [tuple(b) for b in boxes[k]]
                items = []
                for j, b in enumerate(fb):
                    items.append((SUBTYPE[cls], CLASS3[cls], crop_square(b, w, h), b, j))
                if sampled % 2 == 0:  # background: every second sampled frame
                    side = int(round(max(CONTEXT * max(v['box_w_median'], v['box_h_median']), MIN_SIDE)))
                    sq = background_square(fb, side, w, h, rng)
                    if sq is not None:
                        items.append(("background", "neither", sq, None, -1))
                for subtype, c3, (x0, y0, side), b, j in items:
                    patch = frame[y0:y0 + side, x0:x0 + side]
                    patch = cv2.resize(patch, (OUT, OUT), interpolation=cv2.INTER_AREA)
                    d = out / info["split"] / subtype
                    d.mkdir(parents=True, exist_ok=True)
                    path = d / f"{name}_f{k:04d}_{j}.jpg"
                    cv2.imwrite(str(path), patch, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    rows.append({
                        "path": str(path), "split": info["split"], "class3": c3, "subtype": subtype,
                        "video": name, "frame": k, "cluster": info["cluster"],
                        "box": "" if b is None else ";".join(f"{x:.1f}" for x in b),
                        "crop": f"{x0};{y0};{side}",
                    })
                sampled += 1
            k += 1
        cap.release()

    # a scene cluster must live in exactly one split
    by_cluster = collections.defaultdict(set)
    for r in rows:
        by_cluster[r["cluster"]].add(r["split"])
    leaks = {c: s for c, s in by_cluster.items() if len(s) > 1}
    assert not leaks, f"scene clusters in more than one split: {leaks}"

    out.mkdir(parents=True, exist_ok=True)
    with open(out / "manifest.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)

    counts = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        counts[r["split"]][f'{r["class3"]}/{r["subtype"]}'] += 1
    summary = {
        "label": "measured (host CPU)",
        "command": "python train/make_crops.py",
        "stride": args.stride, "seed": args.seed, "context": CONTEXT,
        "min_side": MIN_SIDE, "out_size": OUT,
        "n_crops": len(rows),
        "clusters_in_more_than_one_split": 0,
        "per_split_per_subtype": {s: dict(c) for s, c in sorted(counts.items())},
    }
    Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary).write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
