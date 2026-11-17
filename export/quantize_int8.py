"""Static int8 quantisation of the ONNX model, calibrated on TRAIN crops only.

    python export/quantize_int8.py [--method minmax|entropy|percentile] [--ops all|conv_gemm]
                                   [--float-last-gemm] [--out models/model_int8.onnx]

Uses onnxruntime's quantize_static (QDQ format, per-channel weights, int8
activations and weights). The calibration subset is a seeded, class-balanced
sample of TRAIN crops; validation and test crops are never used here.

`export/select_quantisation.py` tries several settings and picks one by
validation score. Plain min-max over all operators was tried first and collapsed
the model (see docs/decisions.md D22).
"""
import argparse
import random
import sys
from pathlib import Path

import onnx
from onnxruntime.quantization import CalibrationDataReader, CalibrationMethod, QuantFormat, QuantType, quantize_static
from onnxruntime.quantization.shape_inference import quant_pre_process

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "train"))
import data  # noqa: E402

METHODS = {"minmax": CalibrationMethod.MinMax, "entropy": CalibrationMethod.Entropy,
           "percentile": CalibrationMethod.Percentile}
CONV_GEMM = ["Conv", "Gemm", "MatMul"]


class CropReader(CalibrationDataReader):
    def __init__(self, rows):
        ds = data.CropDataset(rows, data.eval_transform())
        self.it = iter([{"input": ds[i][0].numpy()[None]} for i in range(len(ds))])

    def get_next(self):
        return next(self.it, None)


def calibration_rows(n, seed):
    rows = data.read_manifest(split="train")
    rng = random.Random(seed)
    per = max(1, n // len(data.CLASSES))
    out = []
    for c in data.CLASSES:
        pool = [r for r in rows if r["class3"] == c]
        out += rng.sample(pool, min(per, len(pool)))
    assert all(r["split"] == "train" for r in out)
    return out


def last_gemm_name(path):
    names = [n.name for n in onnx.load(path).graph.node if n.op_type == "Gemm"]
    return names[-1] if names else None


def exclusion_names(path, exclude):
    """Names of Conv nodes to leave in float. 'se' = the squeeze-and-excite fc1/fc2 convolutions
    (named fc1/fc2 by torchvision); 'depthwise' = convolutions with group > 1."""
    names = []
    for n in onnx.load(path).graph.node:
        if n.op_type != "Conv":
            continue
        group = next((a.i for a in n.attribute if a.name == "group"), 1)
        if "se" in exclude.split("+") and ("/fc1/" in n.name or "/fc2/" in n.name):
            names.append(n.name)
        if "depthwise" in exclude.split("+") and group > 1:
            names.append(n.name)
    return names


def quantize(fp32, out, method="minmax", ops="all", float_last_gemm=False, n_calib=200, seed=0, exclude="none"):
    pre = str(Path(out).with_name("model_fp32_preproc.onnx"))
    quant_pre_process(fp32, pre)
    rows = calibration_rows(n_calib, seed)
    kwargs = {}
    if ops == "conv_gemm":
        kwargs["op_types_to_quantize"] = CONV_GEMM
    skip = exclusion_names(pre, exclude) if exclude != "none" else []
    if float_last_gemm and last_gemm_name(pre):
        skip.append(last_gemm_name(pre))
    if skip:
        kwargs["nodes_to_exclude"] = skip
    extra = {"CalibPercentile": 99.99} if method == "percentile" else {}
    quantize_static(pre, out, CropReader(rows), quant_format=QuantFormat.QDQ, activation_type=QuantType.QInt8,
                    weight_type=QuantType.QInt8, per_channel=True, calibrate_method=METHODS[method],
                    extra_options=extra, **kwargs)
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fp32", default="models/model_fp32.onnx")
    ap.add_argument("--out", default="models/model_int8.onnx")
    ap.add_argument("--method", default="minmax", choices=list(METHODS))
    ap.add_argument("--ops", default="all", choices=["all", "conv_gemm"])
    ap.add_argument("--float-last-gemm", action="store_true")
    ap.add_argument("--exclude", default="none", choices=["none", "se", "depthwise", "se+depthwise"])
    ap.add_argument("--n-calib", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    n = quantize(args.fp32, args.out, args.method, args.ops, args.float_last_gemm, args.n_calib, args.seed, args.exclude)
    print(f"calibration crops: {n} (train only); wrote {args.out}, {Path(args.out).stat().st_size} bytes")


if __name__ == "__main__":
    main()
