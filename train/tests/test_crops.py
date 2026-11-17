import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import make_crops as mc  # noqa: E402


def test_crop_square_is_inside_frame_and_contains_box():
    for box in [(5, 5, 10, 10), (630, 500, 8, 8), (300, 250, 30, 20), (0, 0, 3, 3)]:
        x0, y0, side = mc.crop_square(box, 640, 512)
        assert side >= mc.MIN_SIDE or side == 512
        assert 0 <= x0 and x0 + side <= 640 and 0 <= y0 and y0 + side <= 512
        x, y, w, h = box
        assert x0 <= x and x + w <= x0 + side and y0 <= y and y + h <= y0 + side


def test_background_never_overlaps_a_box():
    boxes = [(100, 100, 40, 40), (300, 200, 60, 30)]
    rng = random.Random(0)
    for _ in range(200):
        sq = mc.background_square(boxes, 64, 640, 512, rng)
        assert sq is not None
        assert not mc.overlaps(*sq, boxes)


def test_background_returns_none_when_frame_is_covered():
    assert mc.background_square([(0, 0, 640, 512)], 64, 640, 512, random.Random(0)) is None
