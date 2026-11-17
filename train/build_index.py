"""Build a per-video index of the visible-light videos from the real files.

    python train/build_index.py [--raw data/raw/extracted] [--out data/index/index.json]

For each visible-light video: class, number, distance bin and drone type from the
dataset's description spreadsheet, frame count and size from the video file,
label statistics decoded from the .mat file (train/mat_labels.py), and a
perceptual hash of three whole frames (for the scene-duplicate check).

Excluded, with the reason recorded in the output:
  * the 49 clips the spreadsheet marks as coming from a YouTube channel
    (all airplane or helicopter);
  * any video whose label file does not match the expected structure.

Output goes under data/ which is gitignored. Nothing derived from the videos is
published.
"""
import argparse
import glob
import json
import os
import sys
from pathlib import Path

import cv2
import imagehash
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mat_labels import load_frame_boxes  # noqa: E402
from xlsx_reader import read_xlsx  # noqa: E402

HASH_POSITIONS = (0.2, 0.5, 0.8)  # fractions of the video length


def read_frames(path):
    cap = cv2.VideoCapture(str(path))
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    cap.release()
    return frames


def phash_hex(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return str(imagehash.phash(Image.fromarray(rgb)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw/extracted")
    ap.add_argument("--out", default="data/index/index.json")
    args = ap.parse_args()

    root = glob.glob(os.path.join(args.raw, "*", "Data"))[0]
    sheet = read_xlsx(os.path.join(root, "Video_dataset_description.xlsx"))["Blad1"]
    rows = sheet[1:]  # sheet[0] is the header row
    meta = {}
    for sensor, cls, num, dist, _, extra in (r + [""] * (6 - len(r)) for r in rows):
        if sensor == "V":
            meta[f"V_{cls}_{int(num):03d}"] = {
                "class": cls,
                "distance_bin": dist,
                "source": extra,
                "from_youtube": extra.startswith("https://www.youtube.com/"),
            }

    videos, excluded = {}, []
    for name in sorted(meta):
        m = meta[name]
        if m["from_youtube"]:
            excluded.append({"video": name, "reason": "youtube clip (per spreadsheet)"})
            continue
        mp4 = os.path.join(root, "Video_V", f"{name}.mp4")
        try:
            boxes = load_frame_boxes(os.path.join(root, "Video_V", f"{name}_LABELS.mat"), m["class"])
        except ValueError as e:
            excluded.append({"video": name, "reason": f"label file not decoded: {e}"})
            continue
        frames = read_frames(mp4)
        if len(frames) != len(boxes):
            excluded.append({"video": name, "reason": f"{len(boxes)} label groups vs {len(frames)} frames"})
            continue
        h, w = frames[0].shape[:2]
        present = [b for b in boxes if len(b)]
        all_boxes = np.concatenate(present) if present else np.zeros((0, 4))
        videos[name] = {
            **m,
            "n_frames": len(frames),
            "width": w,
            "height": h,
            "frames_with_target": len(present),
            "frames_target_absent": len(boxes) - len(present),
            "n_boxes": int(len(all_boxes)),
            "box_w_median": float(np.median(all_boxes[:, 2])) if len(all_boxes) else None,
            "box_h_median": float(np.median(all_boxes[:, 3])) if len(all_boxes) else None,
            "phash": [phash_hex(frames[int(p * (len(frames) - 1))]) for p in HASH_POSITIONS],
        }
        print(name, videos[name]["n_frames"], videos[name]["n_boxes"], flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"videos": videos, "excluded": excluded}, indent=1))
    print(f"indexed {len(videos)} videos, excluded {len(excluded)} -> {out}")


if __name__ == "__main__":
    main()
