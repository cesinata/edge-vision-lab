"""Fill the generated tables in README.md from the JSON files, so no number is typed by hand.

    python scripts/make_readme_results.py

Replaces the text between <!-- results:start --> and <!-- results:end --> in README.md.
Every value comes from results/*.json or bench/results.json; a missing file gives "not run yet".
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START, END = "<!-- results:start -->", "<!-- results:end -->"
FSTART, FEND = "<!-- findings:start -->", "<!-- findings:end -->"
HOST = "measured (host CPU)"


def load(rel):
    p = ROOT / rel
    return json.loads(p.read_text()) if p.exists() else None


def f(v, d=3):
    return "n/a" if v is None else f"{v:.{d}f}"


def ci(pair, d=2):
    return "n/a" if not pair or pair[0] is None else f"{pair[0]:.{d}f} to {pair[1]:.{d}f}"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def build():
    ev, bench = load("results/eval_torch.json"), load("bench/results.json")
    split, cov, tlog = load("results/split_summary.json"), load("results/firmware_coverage.json"), load("results/train_log.json")
    q = load("results/quantisation_search.json")
    parts = []

    if ev:
        rows = [(c, m["support"], f(m["precision"]), ci(m["precision_ci95"]), f(m["recall"]), ci(m["recall_ci95"]), f(m["f1"]))
                for c, m in ev["per_class"].items()]
        rows.append(("macro F1", "", "", "", "", "", f"{f(ev['macro_f1'])} ({ci(ev['macro_f1_ci95'])})"))
        parts.append(f"**Test split, {ev['n_crops']} crops from {ev['n_videos']} videos, {ev['label']}.** "
                     f"Crop-level accuracy {f(ev['accuracy'])}. Intervals are 95%, resampled by video "
                     f"({ev['bootstrap']['replicates']} replicates). They treat videos as independent, which videos from one scene are not, "
                     f"so they are optimistic.\n\n" + table(["Class", "Crops", "Precision", "95% interval", "Recall", "95% interval", "F1"], rows))
        sub = [(k, m["n_videos"], m["n_crops"], f(m["accuracy"]), ci(m["ci95"])) for k, m in ev["subtype_accuracy"].items()]
        parts.append("**Share of test crops classified into their own class, by subtype** (airplane, helicopter and background all count as \"neither\"; "
                     f"{ev['label']}).\n\n" + table(["Subtype", "Videos", "Crops", "Correct", "95% interval"], sub))
        th = ev["threshold"]
        tr = []
        for name, key in (("P(bird) >= 0.5", "argmax_rule"), ("P(bird) >= 0.85 (firmware default)", "firmware_default"),
                          ("chosen on validation for precision >= 0.90", "chosen")):
            t = th.get(key)
            if t:
                tr.append((name, f(t["threshold"]), f(t["precision"]), ci(t["precision_ci95"]), f(t["recall"]), ci(t["recall_ci95"])))
        parts.append(f"**Bird alert threshold** on the test split ({ev['label']}). Average precision for P(bird): {f(th['average_precision_test'])} on test, "
                     f"{f(th['average_precision_val'])} on validation.\n\n" + table(["Rule", "Threshold", "Precision", "95% interval", "Recall", "95% interval"], tr))
    else:
        parts.append("Evaluation: not run yet.")

    if bench:
        h = bench["host"]
        r = []
        for k, name in (("fp32_onnx", "float32 ONNX"), ("int8_onnx", "int8 ONNX")):
            m = bench[k]
            r.append((name, f"{m['size_kb']['value']:.0f}", f(m["test_accuracy"]["value"]), f(m["test_macro_f1"]["value"]),
                      f(m["bird_recall"]["value"]), f(m["latency_ms_median"]["value"], 2), f(m["latency_ms_p95"]["value"], 2)))
        parts.append(f"**Size, accuracy and host-CPU latency** ({HOST}; CPU: {h['cpu']}; ONNX Runtime {h['onnxruntime']}, {h['latency_threads']} thread, "
                     f"batch 1, median of {h['timed_runs']} runs after {h['warmup_runs']} warm-up runs; KB = 1024 bytes). Reproduce with `python bench/run_bench.py`.\n\n"
                     + table(["Model", "Size (KB)", "Test accuracy", "Test macro F1", "Bird recall", "Median latency (ms)", "p95 latency (ms)"], r)
                     + f"\n\nSize ratio float32 / int8: {bench['size_ratio_fp32_over_int8']['value']} ({HOST}). "
                     f"Activation memory lower bound from ONNX shape inference: {bench['memory_estimate']['activation_lower_bound_kb']['value']} KB "
                     f"(estimated, onnx {h['onnx']}; a lower bound, not a tensor arena size). "
                     "On a microcontroller: latency, frame rate, power and runtime arena size are **not measured on hardware**.")
    else:
        parts.append("Export and bench: not run yet.")
    if q:
        parts.append(f"**Quantisation search** ({HOST}): {len(q['variants']) - 1} int8 settings were tried and scored on the validation split only; "
                     f"chosen: `{q['chosen']}`. Full table in `results/quantisation_search.json`.")
    if tlog:
        parts.append(f"**Training** ({HOST}): {tlog['epochs']} epochs, seed {tlog['seed']}, {tlog['n_train']} train crops, {tlog['wall_seconds']:.0f} s wall time "
                     f"on a laptop CPU (the machine named in the bench table), best epoch {tlog['best_epoch']} by validation macro F1 {tlog['best_val_macro_f1']}.")
    if cov:
        parts.append(f"**Firmware logic** (host build): {cov['checks']} checks, {cov['check_failures']} failures; line coverage of `guardian.cpp` {cov['lines_executed_percent']}% "
                     f"of {cov['lines_total']} lines ({HOST}, {cov['tool']}).")
    if split:
        rows = []
        for c in ("BIRD", "DRONE", "AIRPLANE", "HELICOPTER"):
            v, cl = split["videos_per_class_per_split"][c], split["clusters_per_class_per_split"][c]
            rows.append((c.lower(), f"{v['train']} ({cl['train']})", f"{v['val']} ({cl['val']})", f"{v['test']} ({cl['test']})"))
        parts.append(f"**Split** ({HOST}, `train/make_split.py`): {split['n_videos']} videos in {split['n_clusters']} scene clusters. Videos per split (clusters in brackets).\n\n"
                     + table(["Class", "Train", "Val", "Test"], rows))
    return "\n\n".join(parts)


def pct(x):
    return f"{100 * x:.1f}%"


def findings():
    ev, bench = load("results/eval_torch.json"), load("bench/results.json")
    ea, sp = load("results/error_analysis.json"), load("results/split_summary.json")
    q, tl = load("results/quantisation_search.json"), load("results/train_log.json")
    cov = load("results/firmware_coverage.json")
    e8 = load("results/eval_onnx_int8.json")
    if not (ev and bench and ea and sp and q and tl and cov and e8):
        return "Findings: not generated (some results files are missing)."
    pcs, cm = ev["per_class"], ev["confusion_matrix"]["values"]
    d, th = ea["error_rate_by_subtype_and_distance"], ev["threshold"]
    w = ea["wrong_by_subtype_to_predicted"]
    sc = ea["drone_crops_by_scene"]
    el = tl["epochs_log"]
    first, second = q["variants"][1:13], q["variants"][13:]
    f32, i8 = bench["fp32_onnx"], bench["int8_onnx"]
    out = [
        f"1. **The model is good at calling background \"neither\" and weak at drones.** Test recall is {f(pcs['neither']['recall'])} for neither, "
        f"{f(pcs['bird']['recall'])} for bird and {f(pcs['drone']['recall'])} for drone. {w['drone -> neither']} of {ev['subtype_accuracy']['drone']['n_crops']} drone crops were called neither "
        f"and {cm[1][0]} were called bird, so bird precision is only {f(pcs['bird']['precision'])}. Almost all background crops are plain sky, which is easy ({ea['background_crops']['errors']} of {ea['background_crops']['n']} wrong).",
        f"2. **Distance matters.** Share of drone crops wrong: {pct(d['drone/CLOSE']['error_rate'])} close, {pct(d['drone/MEDIUM']['error_rate'])} medium, {pct(d['drone/DISTANT']['error_rate'])} distant. "
        "Details and ten observations are in [docs/error-analysis.md](docs/error-analysis.md).",
        f"3. **High-precision bird alerts cost most of the recall.** At P(bird) >= 0.5: precision {f(th['argmax_rule']['precision'])}, recall {f(th['argmax_rule']['recall'])}. "
        f"At the threshold {f(th['chosen']['threshold'], 4)} chosen on validation for precision >= 0.90: precision {f(th['chosen']['precision'])}, recall {f(th['chosen']['recall'])}. "
        f"The firmware's original default of 0.85 gives precision {f(th['firmware_default']['precision'])} and recall {f(th['firmware_default']['recall'])}.",
        f"4. **The data limits what these numbers mean.** The {sp['videos_per_class']['DRONE']} drone videos fall into only {sp['clusters_touched_per_class']['DRONE']} scene clusters, the {sp['videos_per_class']['BIRD']} bird videos into {sp['clusters_touched_per_class']['BIRD']}. "
        f"The {sum(x['n_videos'] for x in sc)} drone test videos come from {len(sc)} scenes, with drone crops wrong {pct(sc[0]['error_rate'])} in one and {pct(sc[1]['error_rate'])} in the other (the second is mostly distant clips, so scene and distance are tangled). "
        f"Training loss fell from {el[0]['train_loss']} to {el[-1]['train_loss']} over {len(el)} epochs while validation macro F1 stayed between {min(e['val_macro_f1'] for e in el):.3f} and {max(e['val_macro_f1'] for e in el):.3f}, "
        "which fits a model that partly learns the place. I cannot show that it does, and this test set cannot rule it out.",
        f"5. **Plain int8 quantisation broke the model; a partial int8 model recovers most of it.** All {len(first)} settings that quantised the convolutions together scored at most {max(v['val_macro_f1'] for v in first):.3f} validation macro F1 "
        f"(float32: {q['variants'][0]['val_macro_f1']}). Leaving the depthwise and squeeze-and-excite convolutions in float32 recovered it to {max(v['val_macro_f1'] for v in second):.3f}. "
        f"On the test split that model has accuracy {f(i8['test_accuracy']['value'])} against {f(f32['test_accuracy']['value'])} for float32 (a difference within the noise of this test set), "
        f"is {bench['size_ratio_fp32_over_int8']['value']} times smaller ({i8['size_kb']['value']:.0f} against {f32['size_kb']['value']:.0f} KB) and runs {f(f32['latency_ms_median']['value'], 2)} to {f(i8['latency_ms_median']['value'], 2)} ms on this laptop CPU. "
        f"Its bird alert is clearly worse: average precision {f(e8['threshold']['average_precision_test'])} against {f(ev['threshold']['average_precision_test'])}, and at the threshold {f(e8['threshold']['chosen']['threshold'], 4)} "
        f"that it picked on validation for precision >= 0.90 it reached only precision {f(e8['threshold']['chosen']['precision'])} and recall {f(e8['threshold']['chosen']['recall'])} on test (`results/eval_onnx_int8.json`).",
        f"6. **The device logic is tested without a board.** {cov['checks']} checks pass, including a watchdog stall, a fault in every state and battery hysteresis, "
        f"and line coverage is {cov['lines_executed_percent']}%. Two deliberate breakages of the code were caught by the tests. This says nothing about real timing, interrupts or hardware.",
    ]
    return "\n\n".join(out)


def main():
    p = ROOT / "README.md"
    text = p.read_text()
    for a_, b_ in ((START, END), (FSTART, FEND)):
        assert a_ in text and b_ in text, "README.md needs the generated-block markers"
    a, b = text.index(START) + len(START), text.index(END)
    text = text[:a] + "\n\n" + build() + "\n\n" + text[b:]
    a, b = text.index(FSTART) + len(FSTART), text.index(FEND)
    text = text[:a] + "\n\n" + findings() + "\n\n" + text[b:]
    p.write_text(text)
    print("README.md generated blocks updated")


if __name__ == "__main__":
    main()
