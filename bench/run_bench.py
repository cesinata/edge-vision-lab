"""Size, host-CPU latency and an activation-memory estimate; writes bench/results.json.

    python bench/run_bench.py

Needs models/model_fp32.onnx and models/model_int8.onnx, and the evaluation
results results/eval_onnx_fp32.json and results/eval_onnx_int8.json (run
train/evaluate.py --onnx ... --tag onnx_fp32 / onnx_int8 first).

Every metric has a label. Nothing here is measured on a microcontroller; those
fields are present with value null and the label "not measured on hardware".
"""
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
from onnx import shape_inference

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "train"))
import data  # noqa: E402
import metrics  # noqa: E402

WARMUP, RUNS, THREADS = 20, 200, 1
HOST = "measured (host CPU)"


def metric(value, label, unit=None, detail=None):
    m = {"value": value, "label": label}
    if unit:
        m["unit"] = unit
    if detail:
        m["detail"] = detail
    return m


def cpu_model():
    try:
        return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
    except Exception:
        return platform.processor() or "unknown"


def latency(path, x):
    so = ort.SessionOptions()
    so.intra_op_num_threads = THREADS
    so.inter_op_num_threads = 1
    sess = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
    for _ in range(WARMUP):
        sess.run(None, {"input": x})
    ts = []
    for _ in range(RUNS):
        t = time.perf_counter()
        sess.run(None, {"input": x})
        ts.append((time.perf_counter() - t) * 1000)
    ts.sort()
    return {"median": statistics.median(ts), "p95": ts[int(0.95 * len(ts)) - 1], "min": ts[0]}


def activation_lower_bound_kb(path):
    """Largest, over all nodes, of (input + output activation elements) at 1 byte each.
    Ignores weights and values that must stay alive across several layers, so it is a
    lower bound on a real tensor arena, not an estimate of it."""
    m = shape_inference.infer_shapes(onnx.load(path))
    init = {i.name for i in m.graph.initializer}
    shapes = {}
    for vi in list(m.graph.value_info) + list(m.graph.input) + list(m.graph.output):
        dims = []
        for d in vi.type.tensor_type.shape.dim:
            dims.append(d.dim_value if d.dim_value > 0 else 1)  # dynamic batch -> 1
        shapes[vi.name] = int(np.prod(dims)) if dims else 1
    best, where = 0, ""
    for n in m.graph.node:
        elems = sum(shapes.get(t, 0) for t in list(n.input) + list(n.output) if t not in init)
        if elems > best:
            best, where = elems, f"{n.op_type} {n.name}"
    return best / 1024.0, where


def main():
    fp32, int8 = "models/model_fp32.onnx", "models/model_int8.onnx"
    ev = {k: json.loads(Path(f"results/eval_onnx_{k}.json").read_text()) for k in ("fp32", "int8")}
    ds = data.CropDataset(data.read_manifest(split="test")[:1], data.eval_transform())
    x = ds[0][0].numpy()[None]  # one real preprocessed crop; latency does not depend on its values

    out = {
        "note": "Every metric carries a label. Microcontroller fields are null: nothing was run on a board.",
        "host": {
            "cpu": cpu_model(), "os": platform.platform(), "python": platform.python_version(),
            "onnxruntime": ort.__version__, "onnx": onnx.__version__,
            "latency_threads": THREADS, "warmup_runs": WARMUP, "timed_runs": RUNS,
            "label": HOST, "command": "python bench/run_bench.py",
        },
        "units": "KB = 1024 bytes",
    }
    for key, path in (("fp32_onnx", fp32), ("int8_onnx", int8)):
        e = ev[key.split("_")[0]]
        lat = latency(path, x)
        out[key] = {
            "size_kb": metric(round(Path(path).stat().st_size / 1024, 2), HOST, "KB"),
            "test_accuracy": metric(e["accuracy"], HOST, "fraction of test crops", f"crop level, {e['n_crops']} crops, {e['n_videos']} videos"),
            "test_macro_f1": metric(e["macro_f1"], HOST, None, f"95% interval by video {e['macro_f1_ci95']}"),
            "bird_recall": metric(e["per_class"]["bird"]["recall"], HOST),
            "latency_ms_median": metric(round(lat["median"], 3), HOST, "ms", f"median of {RUNS} runs after {WARMUP} warm-up runs, {THREADS} thread, batch 1, ONNX Runtime CPU provider"),
            "latency_ms_p95": metric(round(lat["p95"], 3), HOST, "ms"),
        }
    qs = json.loads(Path("results/quantisation_search.json").read_text())
    out["int8_onnx"]["variant"] = {
        "chosen": qs["chosen"], "label": HOST,
        "note": "partial int8: the depthwise and squeeze-and-excite convolutions stay in float32; the other convolutions and the "
                "classifier layer are int8 (QDQ, per-channel weights). Chosen on the validation split among "
                f"{len(qs['variants']) - 1} settings (results/quantisation_search.json); plain settings that quantised everything lost most of the accuracy.",
    }
    kb, where = activation_lower_bound_kb(fp32)
    out["memory_estimate"] = {
        "activation_lower_bound_kb": metric(round(kb, 1), f"estimated (onnx {onnx.__version__} shape inference)", "KB",
                                            f"largest single-node input+output activation footprint at 1 byte per element; node: {where}; a lower bound, not a tensor arena size"),
    }
    out["microcontroller"] = {
        "latency_ms": metric(None, "not measured on hardware"),
        "frames_per_second": metric(None, "not measured on hardware"),
        "power_mw": metric(None, "not measured on hardware"),
        "tensor_arena_kb_from_runtime": metric(None, "not measured on hardware"),
        "accelerator_offload": metric(None, "not measured on hardware", None, "never attempted"),
    }
    ratio = out["fp32_onnx"]["size_kb"]["value"] / out["int8_onnx"]["size_kb"]["value"]
    out["size_ratio_fp32_over_int8"] = metric(round(ratio, 2), HOST)
    Path("bench").mkdir(exist_ok=True)
    Path("bench/results.json").write_text(metrics.dumps_strict(out, indent=1))
    print(json.dumps({k: out[k] for k in ("fp32_onnx", "int8_onnx", "memory_estimate", "size_ratio_fp32_over_int8")}, indent=1))


if __name__ == "__main__":
    main()
