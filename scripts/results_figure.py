"""Figure 5 (results): confusion matrix and float32 vs int8, drawn from the JSON files in Option A style.

Called by scripts/make_figures.py. Reads results/eval_torch.json and bench/results.json. Anything
missing is drawn as "not run yet"; no placeholder numbers.
"""
import json


def _load(root, rel):
    p = root / rel
    return json.loads(p.read_text()) if p.exists() else None


def build(Svg, t, root):
    ev, bench = _load(root, "results/eval_torch.json"), _load(root, "bench/results.json")
    w, h = 880, 492
    s = Svg(w, h, "Results: confusion matrix and float32 versus int8",
            "Left: a three by three confusion matrix of real class against predicted class on the test split, with counts and the diagonal marked. "
            "Right: model size and test accuracy for the float32 and partly int8 ONNX models. Every number is measured on the host CPU.", t)
    s.raw(f'<defs><pattern id="hatch2" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0V6" stroke="{t["line"]}" stroke-width="2"/></pattern></defs>')
    s.label(28, 34, "Fig. 5 · Results on the test split")
    s.text(28, 64, "What the test showed", 20, "ink", "bg", 600)

    s.rect(28, 88, 400, 308, "panel", rx=6, extra=f'stroke="{t["ink"]}"')
    s.text(44, 114, "Confusion matrix (crops)", 14, "ink", "panel", 600)
    if ev is None:
        s.text(44, 150, "not run yet", 14, "ink", "panel")
    else:
        cls = ev["confusion_matrix"]["rows_true"]
        vals = ev["confusion_matrix"]["values"]
        x0, y0, cw, ch = 152, 168, 84, 58
        s.text(x0 + 1.5 * cw, 138, "model said", 12, "muted", "panel", 500, "middle")
        s.text(44, y0 + 1.5 * ch + 4, "real", 12, "muted", "panel", 500)
        for j, c in enumerate(cls):
            s.text(x0 + j * cw + cw / 2, 158, c, 12, "ink", "panel", 600, "middle")
            s.text(x0 - 10, y0 + j * ch + ch / 2 + 4, c, 12, "ink", "panel", 600, "end")
        for i in range(3):
            for j in range(3):
                on = i == j
                s.rect(x0 + j * cw, y0 + i * ch, cw, ch, "mark" if on else "bg", extra=f'stroke="{t["ink"]}"' + (' stroke-width="2.5"' if on else ""))
                s.text(x0 + j * cw + cw / 2, y0 + i * ch + ch / 2 + 6, str(vals[i][j]), 16, "onmark" if on else "ink", "mark" if on else "bg", 600, "middle")
        s.text(44, 372, f"{ev['n_crops']} crops, {ev['n_videos']} videos. measured (host CPU)", 12, "ink2", "panel", 500)

    s.rect(452, 88, 400, 308, "panel", rx=6, extra=f'stroke="{t["ink"]}"')
    s.text(468, 114, "float32 vs partly int8 (ONNX)", 14, "ink", "panel", 600)
    if bench is None:
        s.text(468, 150, "not run yet", 14, "ink", "panel")
    else:
        f, i8 = bench["fp32_onnx"], bench["int8_onnx"]

        def bar(y, name, v, vmax, text, hatched):
            s.text(468, y, name, 12, "ink", "panel", 500)
            bw = 230 * v / vmax
            s.raw(f'<rect x="468" y="{y + 8}" width="{bw:.1f}" height="22" fill="{"url(#hatch2)" if hatched else t["ink"]}"/>')
            s.text(468 + bw + 8, y + 25, text, 12, "ink", "panel", 500)

        smax = max(f["size_kb"]["value"], i8["size_kb"]["value"])
        s.text(468, 144, "Model size (KB)", 12, "muted", "panel", 600)
        bar(164, "float32", f["size_kb"]["value"], smax, f"{f['size_kb']['value']:,.0f}", False)
        bar(212, "partly int8", i8["size_kb"]["value"], smax, f"{i8['size_kb']['value']:,.0f}", True)
        s.text(468, 268, "Test accuracy (crop level, bars start at 0)", 12, "muted", "panel", 600)
        bar(288, "float32", f["test_accuracy"]["value"], 1.0, f"{f['test_accuracy']['value']:.3f}", False)
        bar(336, "partly int8", i8["test_accuracy"]["value"], 1.0, f"{i8['test_accuracy']['value']:.3f}", True)
        s.text(468, 384, "measured (host CPU)", 12, "ink2", "panel", 500)

    s.rect(28, 412, 824, 62, "bg", rx=6, extra=f'stroke="{t["ink"]}"')
    s.raw(f'<circle cx="50" cy="434" r="6" fill="{t["mark"]}"/>')
    s.text(66, 438, "Small, noisy test set from few scenes.", 12, "ink", "bg", 500)
    s.text(66, 456, "Nothing was run on a board: latency, power and arena size are not measured on hardware.", 12, "ink", "bg", 500)
    return s
