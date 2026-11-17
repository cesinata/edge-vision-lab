"""Make the fixed train/val/test split, by scene cluster, and save it to disk.

    python train/make_split.py [--index data/index/index.json] [--seed 0]
                               [--threshold 6] [--out train/splits/split_seed0.json]

Why clusters and not videos: many videos were filmed from the same spot, so
their backgrounds are near-identical (see docs/data.md). A split by video would
put the same scene in train and test. Videos whose whole-frame perceptual
hashes are within `threshold` bits (64-bit pHash, best match over three frames
per video) are joined into one cluster, and whole clusters are assigned to a
split. This is a proxy: pHash finds near-identical scenes, not every shared
location or session.

Assignment: a seeded random search (20000 trials) over cluster-to-split
assignments, keeping the one whose per-class video shares are closest to
train 0.6 / val 0.2 / test 0.2, with a penalty when a class has fewer than two
clusters in val or test. The output
holds video names and split labels only. No frames, hashes or images.
"""
import argparse
import collections
import json
import random
from pathlib import Path

import numpy as np

TARGET = {"train": 0.6, "val": 0.2, "test": 0.2}


def hamming(a, b):
    return bin(a ^ b).count("1")


def cluster_videos(videos, threshold):
    names = sorted(videos)
    n = len(names)
    hashes = [[int(h, 16) for h in videos[x]["phash"]] for x in names]
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    dist = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            d = min(hamming(a, b) for a in hashes[i] for b in hashes[j])
            dist[i, j] = dist[j, i] = d
            if d <= threshold:
                parent[find(i)] = find(j)
    groups = collections.defaultdict(list)
    for i in range(n):
        groups[find(i)].append(names[i])
    return list(groups.values()), names, dist


def score(assignment, clusters, videos, classes):
    """Lower is better: squared gap between each class's per-split video share
    and the target share, plus a penalty for any class with fewer than 2
    clusters in val or test (a split built from one scene says little)."""
    total = collections.Counter()
    got = {s: collections.Counter() for s in TARGET}
    nclust = {s: collections.defaultdict(int) for s in TARGET}
    for c, s in zip(clusters, assignment):
        seen = set()
        for v in c:
            cls = videos[v]["class"]
            total[cls] += 1
            got[s][cls] += 1
            seen.add(cls)
        for cls in seen:
            nclust[s][cls] += 1
    sc = 0.0
    for cls in classes:
        for s, t in TARGET.items():
            sc += (got[s][cls] / total[cls] - t) ** 2
    for s in ("val", "test"):
        for cls in classes:
            if nclust[s][cls] < 2:
                sc += 1.0
    return sc


def assign(clusters, videos, seed, n_trials=20000):
    """Seeded random search over cluster-to-split assignments. Deterministic for
    a given seed, clusters and videos."""
    rng = random.Random(seed)
    clusters = sorted(clusters, key=lambda c: sorted(c)[0])  # stable order
    classes = sorted({videos[v]["class"] for c in clusters for v in c})
    splits = list(TARGET)
    weights = [TARGET[s] for s in splits]
    best, best_score = None, float("inf")
    for _ in range(n_trials):
        cand = rng.choices(splits, weights=weights, k=len(clusters))
        sc = score(cand, clusters, videos, classes)
        if sc < best_score:
            best, best_score = cand, sc
    split_of = {v: s for c, s in zip(clusters, best) for v in c}
    return split_of, best_score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="data/index/index.json")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--threshold", type=int, default=6)
    ap.add_argument("--out", default="train/splits/split_seed0.json")
    args = ap.parse_args()

    index = json.loads(Path(args.index).read_text())
    videos = index["videos"]
    clusters, names, dist = cluster_videos(videos, args.threshold)
    split_of, final_score = assign(clusters, videos, args.seed)
    cluster_id = {v: k for k, c in enumerate(sorted(clusters, key=lambda c: sorted(c)[0])) for v in c}

    # cross-split near-duplicate check on the final assignment
    pos = {v: i for i, v in enumerate(names)}
    cross = collections.Counter()
    for a in names:
        for b in names:
            if a < b and split_of[a] != split_of[b]:
                d = dist[pos[a], pos[b]]
                for th in (6, 8, 10, 12):
                    if d <= th:
                        cross[th] += 1

    table = collections.defaultdict(lambda: collections.Counter())
    nclust = collections.defaultdict(lambda: collections.defaultdict(set))
    for v, s in split_of.items():
        cls = videos[v]["class"]
        table[cls][s] += 1
        nclust[cls][s].add(cluster_id[v])

    report = {
        "seed": args.seed,
        "phash_threshold_bits": args.threshold,
        "n_videos": len(split_of),
        "n_clusters": len(clusters),
        "assignment_score": round(final_score, 4),
        "largest_clusters": sorted((len(c) for c in clusters), reverse=True)[:8],
        "videos_per_class_per_split": {c: dict(t) for c, t in table.items()},
        "clusters_per_class_per_split": {c: {s: len(x) for s, x in d.items()} for c, d in nclust.items()},
        "cross_split_video_pairs_within_threshold": {str(k): cross[k] for k in (6, 8, 10, 12)},
        "excluded": index["excluded"],
    }
    out = {
        "report": report,
        "split": {v: {"split": s, "cluster": cluster_id[v], "class": videos[v]["class"]}
                  for v, s in sorted(split_of.items())},
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in report.items() if k != "excluded"}, indent=1))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
