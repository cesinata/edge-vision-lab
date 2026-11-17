"""Write results/split_summary.json: counts only, from the split file and the index.

    python train/summarise_split.py

Contains no video names, hashes or frames. The split file itself stays local until
the dataset licence is confirmed (see docs/todo.md).
"""
import collections
import json
from pathlib import Path

split = json.loads(Path("train/splits/split_seed0.json").read_text())
index = json.loads(Path("data/index/index.json").read_text())["videos"]
rep = split["report"]
by_cluster = collections.defaultdict(set)
for v, info in split["split"].items():
    by_cluster[info["class"]].add(info["cluster"])
sizes = collections.Counter(info["cluster"] for info in split["split"].values())
out = {
    "label": "measured (host CPU)",
    "command": "python train/make_split.py && python train/summarise_split.py",
    "seed": rep["seed"],
    "phash_threshold_bits": rep["phash_threshold_bits"],
    "n_videos": rep["n_videos"],
    "n_clusters": rep["n_clusters"],
    "largest_cluster_sizes": rep["largest_clusters"],
    "videos_per_class_per_split": rep["videos_per_class_per_split"],
    "clusters_per_class_per_split": rep["clusters_per_class_per_split"],
    "clusters_touched_per_class": {c: len(s) for c, s in sorted(by_cluster.items())},
    "videos_per_class": dict(collections.Counter(v["class"] for v in index.values())),
    "cross_split_video_pairs_within_threshold": rep["cross_split_video_pairs_within_threshold"],
    "excluded_count": len(rep["excluded"]),
    "excluded_reasons": dict(collections.Counter(e["reason"].split(":")[0].split(" (")[0] for e in rep["excluded"])),
}
Path("results").mkdir(exist_ok=True)
Path("results/split_summary.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
