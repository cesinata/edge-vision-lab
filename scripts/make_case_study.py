"""Write docs/case-study.md (one page) with numbers read from the JSON results.

    python scripts/make_case_study.py
"""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
ev = json.loads((R / "results/eval_torch.json").read_text())
e8 = json.loads((R / "results/eval_onnx_int8.json").read_text())
b = json.loads((R / "bench/results.json").read_text())
sp = json.loads((R / "results/split_summary.json").read_text())
q = json.loads((R / "results/quantisation_search.json").read_text())
cov = json.loads((R / "results/firmware_coverage.json").read_text())
tl = json.loads((R / "results/train_log.json").read_text())
pc, th = ev["per_class"], ev["threshold"]
f32, i8 = b["fp32_onnx"], b["int8_onnx"]
first = q["variants"][1:13]

text = f"""# Case study: a small classifier, measured honestly

For readers who want the story in one page. Every number is `measured (host CPU)` unless it says otherwise, comes from a file in `results/` or `bench/`, and is reproduced by the commands in the README.

## The problem
A camera node on a solar-powered device should react to birds but not to drones or airplanes, using a tiny model that could one day run on a microcontroller. I had no board, so the goal was to do everything that can be done honestly on a laptop and to say clearly what cannot: train a classifier, quantise it, measure it, test the node's power logic, and explain the pipeline on a website.

## What I built
- A three-class classifier (bird, drone, neither) on small crops cut from labelled video frames of a public dataset (visible-light videos only; {sp['n_videos']} videos after exclusions). MobileNetV3-Small, fine-tuned from ImageNet weights on a laptop CPU in {tl['wall_seconds']:.0f} s.
- A split by scene, not by frame or clip, because {sp['videos_per_class']['DRONE']} drone clips turned out to come from only {sp['clusters_touched_per_class']['DRONE']} places.
- An evaluation on the test split with intervals resampled by video, a per-subtype breakdown (background, airplane, helicopter), a threshold for bird alerts, and an error analysis.
- ONNX export and static int8 quantisation, with size, accuracy and host-CPU latency measured before and after.
- C++ state and power logic (idle, capture, infer, alert, low-power, recovery) with a working watchdog, replayed from scripted traces and unit-tested: {cov['checks']} checks, {cov['lines_executed_percent']}% line coverage.
- A website with a webcam demo of a third-party detector, a board explainer, a memory-budget calculator and a state-machine viewer.

## What the numbers say
- Test macro F1 {ev['macro_f1']:.3f} (95% interval {ev['macro_f1_ci95'][0]:.2f} to {ev['macro_f1_ci95'][1]:.2f}). Recall is {pc['neither']['recall']:.2f} for neither, {pc['bird']['recall']:.2f} for bird and only {pc['drone']['recall']:.2f} for drone; drones that are far away are mostly missed.
- A bird alert tuned for high precision ({th['chosen']['precision']:.2f}) keeps only {th['chosen']['recall']:.2f} of the birds.
- Quantising every convolution to int8 destroyed the model (best of {len(first)} settings: validation macro F1 {max(v['val_macro_f1'] for v in first):.2f} against {q['variants'][0]['val_macro_f1']:.2f}). Keeping the depthwise and squeeze-and-excite layers in float32 recovered it. That partial int8 model is {b['size_ratio_fp32_over_int8']['value']} times smaller ({i8['size_kb']['value']:.0f} against {f32['size_kb']['value']:.0f} KB), about {100 * (1 - i8['latency_ms_median']['value'] / f32['latency_ms_median']['value']):.0f}% faster on this CPU, and has a worse bird alert (average precision {e8['threshold']['average_precision_test']:.2f} against {ev['threshold']['average_precision_test']:.2f}).

## What I would not claim
Nothing was run on a board, so there is no on-device speed, power or memory result (`not measured on hardware`). The test set is small and the drone test clips come from two scenes, so these results do not show how the model behaves in a new place. The training curve fits a model that partly learns the scene; I could not rule that out. The project's model and all frames are unpublished until the dataset authors confirm the data licence.

## What I would do next
Train on footage from many more scenes, add the planned out-of-domain test set, try quantisation-aware training, and, with a board, measure the real arena size and latency.
"""
(R / "docs/case-study.md").write_text(text)
print("wrote docs/case-study.md,", len(text.split()), "words")
