"""Export the trained PyTorch classifier to ONNX and check it against PyTorch.

    python export/export_onnx.py [--ckpt models/mobilenetv3s_best.pt] [--out models/model_fp32.onnx]

Opset 17, dynamic batch axis, input 1x3x224x224. After export, runs the PyTorch
model and the ONNX model on the first N test crops and reports the largest
absolute difference between their logits. Models stay under models/ (gitignored).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "train"))
import data  # noqa: E402
from train import build_model  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="models/mobilenetv3s_best.pt")
    ap.add_argument("--out", default="models/model_fp32.onnx")
    ap.add_argument("--check", type=int, default=64)
    args = ap.parse_args()

    ck = torch.load(args.ckpt, map_location="cpu")
    model = build_model(pretrained=False)
    model.load_state_dict(ck["state_dict"])
    model.eval()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    dummy = torch.zeros(1, 3, data.INPUT, data.INPUT)
    torch.onnx.export(model, dummy, args.out, input_names=["input"], output_names=["logits"],
                      dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}}, opset_version=17,
                      dynamo=False)

    rows = data.read_manifest(split="test")[: args.check]
    ds = data.CropDataset(rows, data.eval_transform())
    x = torch.stack([ds[i][0] for i in range(len(ds))])
    with torch.no_grad():
        ref = model(x).numpy()
    sess = ort.InferenceSession(args.out, providers=["CPUExecutionProvider"])
    got = sess.run(None, {"input": x.numpy()})[0]
    diff = float(np.abs(ref - got).max())
    agree = float((ref.argmax(1) == got.argmax(1)).mean())
    print(json.dumps({"out": args.out, "bytes": Path(args.out).stat().st_size, "max_abs_logit_diff": diff,
                      "argmax_agreement": agree, "n_checked": len(rows)}))
    assert diff < 1e-3, "ONNX and PyTorch logits differ more than expected"


if __name__ == "__main__":
    main()
