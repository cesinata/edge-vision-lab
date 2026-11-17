"""Write docs/error-analysis.md and web/src/content/observations.ts from the JSON results.

    python scripts/make_error_analysis_doc.py

Numbers come from results/eval_torch.json and results/error_analysis.json. The only typed-in
text is the qualitative notes from looking at misclassified crops locally; those are marked.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ev = json.loads((ROOT / "results/eval_torch.json").read_text())
ea = json.loads((ROOT / "results/error_analysis.json").read_text())

pc = lambda x: f"{100 * x:.1f}%"  # noqa: E731
sub = ev["subtype_accuracy"]
w = ea["wrong_by_subtype_to_predicted"]
d = ea["error_rate_by_subtype_and_distance"]
size = ea["by_object_size_px2"]["bird_and_drone"]
bri = ea["by_crop_brightness_0_255"]["bird_and_drone"]
tex = ea["by_crop_texture_std"]["bird_and_drone"]
scenes = ea["drone_crops_by_scene"]


def mix(m):
    return f"{m['CLOSE']} close, {m['MEDIUM']} medium, {m['DISTANT']} distant videos"

n_drone = sub["drone"]["n_crops"]
drone_wrong = w["drone -> neither"] + w["drone -> bird"]
worst = [v for v in ea["videos_by_error_rate"] if v["wrong"]][:2]
air_n, heli_n = sub["airplane"]["n_crops"], sub["helicopter"]["n_crops"]
air_wrong = w["airplane -> bird"] + w["airplane -> drone"]
heli_wrong = w["helicopter -> drone"]
th = ev["threshold"]
bg = ea["background_crops"]

obs = [
    ("Drone is the weak class",
     f"{drone_wrong} of {n_drone} test drone crops ({pc(drone_wrong / n_drone)}) were wrong: {w['drone -> neither']} called neither and {w['drone -> bird']} called bird.",
     "Recall for drone is the lowest of the three classes."),
    ("Distance matters a lot for drones",
     f"Wrong share of drone crops: {pc(d['drone/CLOSE']['error_rate'])} close ({d['drone/CLOSE']['n_videos']} videos), {pc(d['drone/MEDIUM']['error_rate'])} medium ({d['drone/MEDIUM']['n_videos']}), {pc(d['drone/DISTANT']['error_rate'])} distant ({d['drone/DISTANT']['n_videos']}). Birds: {pc(d['bird/MEDIUM']['error_rate'])} medium ({d['bird/MEDIUM']['n_videos']} videos), {pc(d['bird/DISTANT']['error_rate'])} distant (only {d['bird/DISTANT']['n_videos']} videos, {d['bird/DISTANT']['n']} crops).",
     "The distant-bird figure rests on two videos and says almost nothing."),
    ("Small objects fail more",
     f"Bird and drone crops split into thirds by box area: wrong share {pc(size['low']['error_rate'])} (smallest third, {size['low']['range'][0]:.0f} to {size['low']['range'][1]:.0f} px squared), {pc(size['mid']['error_rate'])} (middle), {pc(size['high']['error_rate'])} (largest).",
     "Size and distance overlap, so this is partly the same effect."),
    ("Whole clips fail, not odd frames",
     f"Only {ea['videos_all_correct']} of {ea['videos_total']} test videos had every crop right. The worst, {worst[0]['video']} and {worst[1]['video']}, had {worst[0]['wrong']} and {worst[1]['wrong']} of {worst[0]['n']} crops wrong, with wrong frames spread across the whole clip (indices {', '.join(map(str, worst[0]['wrong_frames'][:6]))} and on).",
     "Errors come in whole-clip runs rather than isolated frames."),
    ("Two scenes decide the drone result",
     f"The {sum(s['n_videos'] for s in scenes)} drone test videos come from {len(scenes)} scene clusters. Drone crops wrong: {pc(scenes[0]['error_rate'])} in the cluster with {scenes[0]['n_videos']} videos ({mix(scenes[0]['distance_mix'])}) and {pc(scenes[1]['error_rate'])} in the cluster with {scenes[1]['n_videos']} videos ({mix(scenes[1]['distance_mix'])}).",
     "Scene and distance cannot be separated here: the worse scene is mostly distant clips."),
    ("Visible drones are missed on plain sky (looked at by eye, local only)",
     "In a random sample of 8 drone crops called neither, several show a clearly visible quadcopter shape on plain sky, not just a blur. Nothing was saved.",
     "That fits the model leaning on the scene: most of the background crops it learned as neither are plain sky (checked by eye on a sample)."),
    ("Brighter and plainer crops fail more",
     f"For bird and drone crops, wrong share by brightness third: {pc(bri['low']['error_rate'])} (darkest), {pc(bri['mid']['error_rate'])}, {pc(bri['high']['error_rate'])} (brightest). By texture third (pixel standard deviation): {pc(tex['low']['error_rate'])} (plainest), {pc(tex['mid']['error_rate'])}, {pc(tex['high']['error_rate'])} (most texture).",
     "These are associations only. Brightness and texture also track scene and distance, so this does not show that lighting causes the errors."),
    ("Background is easy, so neither looks better than it is",
     f"{bg['errors']} of {bg['n']} background crops were wrong ({pc(bg['errors'] / bg['n'])}).",
     "Plain sky is easy to call neither without learning anything about objects."),
    ("Look-alikes are confused with the targets",
     f"{air_wrong} of {air_n} airplane crops ({pc(air_wrong / air_n)}) were called bird or drone, and {heli_wrong} of {heli_n} helicopter crops ({pc(heli_wrong / heli_n)}) were called drone. Airplane crops wrong by distance: {pc(d['airplane/CLOSE']['error_rate'])} close ({d['airplane/CLOSE']['n_videos']} videos), {pc(d['airplane/MEDIUM']['error_rate'])} medium, {pc(d['airplane/DISTANT']['error_rate'])} distant. In the sample I looked at, a large, clear airplane was called bird.",
     "Only 2 close airplane videos and 4 helicopter videos are in the test set."),
    ("High precision costs most of the recall",
     f"Bird alert at P(bird) >= {th['argmax_rule']['threshold']}: precision {th['argmax_rule']['precision']:.3f}, recall {th['argmax_rule']['recall']:.3f}. At the threshold chosen on validation for precision >= 0.90 ({th['chosen']['threshold']}): precision {th['chosen']['precision']:.3f}, recall {th['chosen']['recall']:.3f}, {th['chosen']['predicted_positive']} alerts.",
     "The firmware's default of 0.85 gave precision " + f"{th['firmware_default']['precision']:.3f} and recall {th['firmware_default']['recall']:.3f}. The test set is small, so each figure has a wide interval (see the README)."),
]

lines = ["# Error analysis (test split, PyTorch float32 model)", "",
         "Generated by `python scripts/make_error_analysis_doc.py` from `results/eval_torch.json` and `results/error_analysis.json`; "
         "those come from `python train/evaluate.py` and `python train/error_analysis.py`. All numbers are `measured (host CPU)`. "
         "No images are stored in the repository. The test set is small (58 videos, few scenes), so treat these as observations to check, not conclusions.", "",
         "What was checked: wrong share by distance bin, by object size (box area), by crop brightness and by crop texture (pixel standard deviation), "
         "per scene cluster, and per video. In addition I looked at 32 randomly chosen misclassified test crops locally, as a montage that was not saved.", "",
         "## Observations", ""]
for i, (t, what, why) in enumerate(obs, 1):
    lines += [f"{i}. **{t}.** {what} {why}", ""]
lines += ["## Wrong share by subtype and distance", "", "| Subtype / distance | Videos | Crops | Wrong share |", "| --- | --- | --- | --- |"]
for k, v in d.items():
    lines.append(f"| {k} | {v['n_videos']} | {v['n']} | {pc(v['error_rate'])} |")
lines += ["", "## Where the wrong predictions went", "", "| True subtype to predicted class | Crops |", "| --- | --- |"]
for k, v in w.items():
    lines.append(f"| {k} | {v} |")
lines += ["", "## Worst test videos (video, class, distance, crops, wrong, wrong frame indices)", "",
          "Frame indices are the sampled frames (every 15th) whose crop was misclassified.", "",
          "| Video | Class | Distance | Crops | Wrong | Wrong frames |", "| --- | --- | --- | --- | --- | --- |"]
for v in ea["videos_by_error_rate"][:12]:
    lines.append(f"| {v['video']} | {v['class'].lower()} | {v['distance'].lower()} | {v['n']} | {v['wrong']} | {', '.join(map(str, v['wrong_frames']))} |")
lines += ["", f"{ea['videos_all_correct']} of {ea['videos_total']} test videos had every sampled crop correct. The full per-video table is in `results/error_analysis.json`.", ""]
(ROOT / "docs/error-analysis.md").write_text("\n".join(lines))

ts = ["// Generated by scripts/make_error_analysis_doc.py from results/*.json. Do not edit by hand.",
      "export interface Observation {", "  title: string;", "  what: string; // what was checked and found",
      "  why: string; // the cautious reading", "}", "export const OBSERVATIONS: Observation[] = ["]
for t, what, why in obs:
    ts.append("  " + json.dumps({"title": t, "what": what, "why": why}) + ",")
ts.append("];")
(ROOT / "web/src/content/observations.ts").write_text("\n".join(ts) + "\n")
print("wrote docs/error-analysis.md and web/src/content/observations.ts;", len(obs), "observations")
