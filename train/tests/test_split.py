import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import make_split  # noqa: E402


def fake_videos():
    # two scenes per class; hashes within a scene differ by 1 bit, across scenes by many
    vids = {}
    k = 0
    for cls in ("BIRD", "DRONE"):
        for scene in range(8):
            base = (scene * 0x0F0F0F0F0F0F0F0F + (0x1111 if cls == "DRONE" else 0)) & (2**64 - 1)
            for i in range(3):
                h = format(base ^ (1 << i), "016x")
                vids[f"V_{cls}_{k:03d}"] = {"class": cls, "phash": [h, h, h]}
                k += 1
    return vids


def test_clusters_group_near_identical_scenes():
    vids = fake_videos()
    clusters, _, _ = make_split.cluster_videos(vids, threshold=6)
    assert all(len(c) % 3 == 0 for c in clusters)  # videos of a scene stay together
    assert sum(len(c) for c in clusters) == len(vids)


def test_split_is_deterministic_and_never_splits_a_cluster():
    vids = fake_videos()
    clusters, _, _ = make_split.cluster_videos(vids, threshold=6)
    a, _ = make_split.assign(clusters, vids, seed=3, n_trials=500)
    b, _ = make_split.assign(clusters, vids, seed=3, n_trials=500)
    assert a == b
    for c in clusters:
        assert len({a[v] for v in c}) == 1
    c2, _ = make_split.assign(clusters, vids, seed=4, n_trials=500)
    assert c2 != a  # the seed matters
