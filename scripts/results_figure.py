"""Figure 5: confusion matrix and float vs int8 comparison, drawn from the JSON files.

Called by scripts/make_figures.py. Reads results/eval_torch.json and bench/results.json.
Anything missing is drawn as "not run yet"; no placeholder numbers.
"""
import json


def _load(root, rel):
    p = root / rel
    return json.loads(p.read_text()) if p.exists() else None


def build(Svg, t, root):
    ev = _load(root, "results/eval_torch.json")
    bench = _load(root, "bench/results.json")
    w, h = 868, 560
    s = Svg(w, h, "Results: confusion matrix and float versus int8",
            "Left: a three by three confusion matrix of true class against predicted class on the test split, with counts. "
            "Right: model size and test accuracy for the float32 and int8 ONNX models. Every number is labelled "
            "measured on the host CPU.", t)
    s.rect(0, 0, w, h, 28, "bg")
    s.text(32, 46, "Results on the test split", 20, "ink", "bg", "bold")

    # ---- left: confusion matrix
    s.rect(32, 72, 400, 400, 22, "lilac")
    s.text(52, 104, "Confusion matrix (crops)", 15, "ink", "lilac", "bold")
    if ev is None:
        s.text(52, 150, "not run yet", 14, "ink", "lilac")
    else:
        cls = ev["confusion_matrix"]["rows_true"]
        vals = ev["confusion_matrix"]["values"]
        x0, y0, cell = 150, 170, 80
        s.text(x0 + 1.5 * cell, 140, "predicted", 12, "muted", "lilac", "normal", "middle")
        s.text(52, y0 + 1.5 * cell + 4, "true", 12, "muted", "lilac")
        for j, c in enumerate(cls):
            s.text(x0 + j * cell + cell / 2, 160, c, 12, "ink", "lilac", "bold", "middle")
            s.text(x0 - 12, y0 + j * cell + cell / 2 + 4, c, 12, "ink", "lilac", "bold", "end")
        for i in range(3):
            for j in range(3):
                v = vals[i][j]
                share = v / max(sum(vals[i]), 1)
                x, y = x0 + j * cell + 4, y0 + i * cell + 4
                s.parts.append(f'<rect x="{x}" y="{y}" width="{cell - 8}" height="{cell - 8}" rx="16" '
                               f'fill="{t["accent"]}" fill-opacity="{0.10 + 0.55 * share:.2f}"/>')
                # text sits on a surface chip so contrast does not depend on the fill
                s.rect(x + 12, y + 20, cell - 32, 28, 14, "surface")
                s.text(x + (cell - 8) / 2, y + 40, str(v), 14, "ink", "surface", "bold", "middle")
        s.text(52, 450, f"{ev['n_crops']} crops, {ev['n_videos']} videos. measured (host CPU)", 12, "ink", "lilac")

    # ---- right: float vs int8
    s.rect(452, 72, 384, 400, 22, "mint")
    s.text(472, 104, "float32 vs int8 (ONNX)", 15, "ink", "mint", "bold")
    if bench is None:
        s.text(472, 150, "not run yet", 14, "ink", "mint")
    else:
        def bar(y, label, v, vmax, text, tile="mint"):
            s.text(472, y, label, 12, "ink", tile)
            width = 240 * (v / vmax) if vmax else 0
            s.rect(472, y + 8, max(width, 4), 22, 11, "train")
            s.text(472 + max(width, 4) + 8, y + 25, text, 12, "ink", tile)

        f, i = bench["fp32_onnx"], bench["int8_onnx"]
        smax = max(f["size_kb"]["value"], i["size_kb"]["value"])
        s.text(472, 140, "Size", 13, "muted", "mint", "bold")
        bar(160, "float32", f["size_kb"]["value"], smax, f"{f['size_kb']['value']:.0f} KB")
        bar(214, "int8", i["size_kb"]["value"], smax, f"{i['size_kb']['value']:.0f} KB")
        s.text(472, 290, "Test accuracy (crop level)", 13, "muted", "mint", "bold")
        bar(310, "float32", f["test_accuracy"]["value"], 1.0, f"{f['test_accuracy']['value']:.3f}")
        bar(364, "int8", i["test_accuracy"]["value"], 1.0, f"{i['test_accuracy']['value']:.3f}")
        s.text(472, 440, "measured (host CPU). Accuracy bars start at 0.", 12, "ink", "mint")
    # ---- bottom strip
    s.rect(32, 488, 804, 52, 22, "surface")
    s.circle(62, 514, 8, "accent")
    s.text(82, 512, "Small, noisy test set from few scenes. Nothing here was run on a board:", 12, "ink", "surface")
    s.text(82, 530, "device latency, power and arena size are not measured on hardware.", 12, "ink", "surface")
    return s
