"""Decode per-frame bounding boxes from the dataset's MATLAB groundTruth files.

Why this exists: scipy.io.loadmat returns the groundTruth object as an opaque
blob. The third-party `mcos-decoder` 0.1.0 package can walk the blob, but its
`load_groundtruth` guesses by byte size and gets bird videos wrong: it treats a
112-byte cell as "target absent" when that size is a 2x4 box array (two birds),
and it can confuse a 1x4 box with a 1x30 character array of the same size.
Checked on the real files; see docs/data.md.

What is used here: only mcos-decoder's stream walker (MatStream). Each frame is
stored as a group of five arrays at nesting depth 5: a timestamp (class 13)
followed by four label slots, one per class in alphabetical order (airplane,
bird, drone, helicopter). Each slot is an N x 4 double array (N boxes,
column-major x, y, w, h) or an empty 0 x 0 double array. Only the slot of the
video's own class may hold boxes; the file name gives the class. Any file that
does not follow this pattern raises ValueError instead of being guessed.

Frame alignment (label group k <-> video frame k) is an assumption that is
checked separately by overlaying boxes on frames (train/check_labels.py).
"""

import numpy as np
import scipy.io
from mcos_decoder import MatStream

CLASS_DOUBLE = 6
CLASS_INT32 = 13  # per-frame timestamp arrays
CLASS_SLOTS = {"AIRPLANE": 0, "BIRD": 1, "DRONE": 2, "HELICOPTER": 3}
FRAME_DEPTH = 5


def _array_info(elem):
    """(matlab class, dims) of an miMATRIX element, or None."""
    if elem.type_id == 14 and len(elem.children) >= 2:
        flags, dims = elem.children[0], elem.children[1]
        if flags.type_id == 6 and dims.type_id == 5:
            return int(flags.as_array()[0]) & 0xFF, tuple(int(x) for x in dims.as_array())
    return None


def _depth5_arrays(elem, depth, out):
    info = _array_info(elem)
    if info is not None and depth == FRAME_DEPTH:
        out.append((info, elem))
    for child in elem.children:
        _depth5_arrays(child, depth + 1, out)


def _boxes(elem, n):
    data = next(c for c in elem.children if c.type_id == 9)
    arr = np.frombuffer(data.payload, dtype="<f8")
    if arr.size != n * 4:
        raise ValueError("box array size does not match its dimensions")
    return arr.reshape(n, 4, order="F")  # MATLAB is column-major


def load_frame_boxes(mat_path, class_name):
    """Return a list with one entry per frame: an (N, 4) float array of
    (x, y, w, h) boxes in pixels (top-left origin), or an empty (0, 4) array
    when the target is absent in that frame. `class_name` is the video's class
    as in the file name (AIRPLANE, BIRD, DRONE, HELICOPTER)."""
    slot = CLASS_SLOTS[class_name]
    raw = scipy.io.loadmat(str(mat_path))
    fw = raw["__function_workspace__"].tobytes()
    items = []
    for top in MatStream(fw, skip_header=8).walk():
        _depth5_arrays(top, 0, items)

    def token(item):
        (cls, dims), elem = item
        if cls == CLASS_INT32:
            return "T", None
        if cls == CLASS_DOUBLE and dims == (0, 0):
            return "E", None
        if cls == CLASS_DOUBLE and len(dims) == 2 and dims[1] == 4 and dims[0] >= 1:
            return "B", _boxes(elem, dims[0])
        return "?", None

    toks = [token(i) for i in items]

    def group_at(k):
        """The four label slots of a frame group starting at k, or None."""
        g = toks[k : k + 5]
        if len(g) == 5 and g[0][0] == "T" and all(t[0] in "BE" for t in g[1:]):
            return g[1:]
        return None

    starts = [k for k in range(len(toks)) if group_at(k) is not None]
    if not starts:
        raise ValueError(f"{mat_path}: no frame groups found")
    # groups must form one contiguous run with a fixed stride of 5 elements
    if starts != list(range(starts[0], starts[-1] + 1, 5)):
        raise ValueError(f"{mat_path}: frame groups are not one contiguous run")
    frames = []
    for k in starts:
        slots = group_at(k)
        for i, (kind, _) in enumerate(slots):
            if kind == "B" and i != slot:
                raise ValueError(f"{mat_path}: box in slot {i}, expected slot {slot}")
        kind, boxes = slots[slot]
        frames.append(boxes if kind == "B" else np.zeros((0, 4)))
    return frames
