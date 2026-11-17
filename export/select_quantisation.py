"""Try several int8 settings and pick one by VALIDATION macro F1. The test split is not used.

    python export/select_quantisation.py [--fp32 models/model_fp32.onnx]

Writes models/model_int8.onnx (the chosen variant) and results/quantisation_search.json
(validation numbers for every variant tried, including the ones that failed).
"""
import argparse
import itertools
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "train"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import data  # noqa: E402
import evaluate as ev  # noqa: E402
import metrics  # noqa: E402
import quantize_int8 as q  # noqa: E402


def val_scores(onnx_path, rows, y):
    p = ev.onnx_probs(onnx_path, rows)
    s = metrics.summarise(y, p.argmax(1), len(data.CLASSES))
    return s["macro_f1"], s["accuracy"], [float(r) for r in s["recall"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fp32", default="models/model_fp32.onnx")
    ap.add_argument("--out", default="models/model_int8.onnx")
    args = ap.parse_args()

    val = data.read_manifest(split="val")
    y = np.array([data.CLASSES.index(r["class3"]) for r in val])
    base_f1, base_acc, base_rec = val_scores(args.fp32, val, y)
    tried = [{"variant": "float32 reference", "val_macro_f1": round(base_f1, 4), "val_accuracy": round(base_acc, 4),
              "val_recall": dict(zip(data.CLASSES, [round(r, 4) for r in base_rec]))}]
    best = None
    grid = [(m, o, last, "none") for m, o, last in itertools.product(["minmax", "entropy", "percentile"], ["all", "conv_gemm"], [False, True])]
    # second round, added after the first 12 settings all lost most of the accuracy: keep the
    # squeeze-and-excite and/or depthwise convolutions in float
    grid += [(m, "conv_gemm", False, ex) for m, ex in itertools.product(["percentile", "minmax"], ["se", "depthwise", "se+depthwise"])]
    for k, (method, ops, last, excl) in enumerate(grid):
        name = f"{method}/{ops}{'/float-last-gemm' if last else ''}{'' if excl == 'none' else '/float-' + excl}"
        tmp = f"models/_q_{k}.onnx"
        try:
            q.quantize(args.fp32, tmp, method, ops, last, exclude=excl)
            f1, acc, rec = val_scores(tmp, val, y)
            rec_ = {"variant": name, "val_macro_f1": round(f1, 4), "val_accuracy": round(acc, 4),
                    "val_recall": dict(zip(data.CLASSES, [round(r, 4) for r in rec])),
                    "size_bytes": Path(tmp).stat().st_size}
            if best is None or f1 > best[0]:
                best = (f1, tmp, name)
        except Exception as e:  # keep failures in the record
            rec_ = {"variant": name, "error": f"{type(e).__name__}: {str(e)[:200]}"}
        tried.append(rec_)
        print(rec_, flush=True)
    assert best is not None, "no variant could be built"
    shutil.copy(best[1], args.out)
    for p in Path("models").glob("_q_*.onnx"):
        p.unlink()
    out = {"label": "measured (host CPU)", "command": "python export/select_quantisation.py",
           "selection_rule": "highest macro F1 on the validation split; the test split is not used",
           "calibration": "198 train crops, class-balanced, seed 0", "chosen": best[2], "variants": tried}
    Path("results/quantisation_search.json").write_text(metrics.dumps_strict(out, indent=1))
    print("chosen:", best[2], "val macro F1", round(best[0], 4), "vs float32", round(base_f1, 4))


if __name__ == "__main__":
    main()
