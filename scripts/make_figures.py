"""Generate the README figures in docs/img/ (light and dark variants).

    python scripts/make_figures.py

Style: docs/illustration-style.md (Pastel Paper Mono). Original drawings; no
dataset frames, no vendor artwork. Hand-made figures (pipeline, split-by-scene,
board-data-path) are written from the templates below with the light or dark
token set. The results figure is drawn from bench/results.json and shows
"not run yet" for anything that file does not contain.

Also runs a WCAG contrast check on every text/background pair used and writes
results/contrast_check.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img"

FONT = 'ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace'

TOKENS = {
    "light": dict(bg="#FBF8F3", surface="#FFFFFF", ink="#2E2A33", muted="#635C6B", line="#EDE6DA",
                  lilac="#E7DDF7", mint="#D5EEDF", butter="#FBEBB8", accent="#5B3FA8",
                  train="#A58BE0", val="#5DBB8A", test="#F2B84B", onsplit="#2E2A33"),
    "dark": dict(bg="#1F1B26", surface="#292433", ink="#F1EEF5", muted="#BDB5C9", line="#3A3348",
                 lilac="#3A3150", mint="#25423A", butter="#4A3F1E", accent="#CDBBFF",
                 train="#B7A0F0", val="#6FCFA0", test="#F5C766", onsplit="#1F1B26"),
}

# (foreground token, background token, size class) pairs actually used for text
TEXT_PAIRS = []


def luminance(hex_colour):
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class Svg:
    def __init__(self, w, h, title, desc, t):
        self.w, self.h, self.t, self.parts = w, h, t, []
        self.head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
                     f'role="img" aria-labelledby="t d" font-family=\'{FONT}\'>\n'
                     f'<title id="t">{title}</title>\n<desc id="d">{desc}</desc>\n')

    def rect(self, x, y, w, h, r, fill):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{self.t[fill]}"/>')

    def circle(self, cx, cy, r, fill):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{self.t[fill]}"/>')

    def line(self, x1, y1, x2, y2, colour="muted", width=3):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{self.t[colour]}" '
                          f'stroke-width="{width}" stroke-linecap="round"/>')

    def text(self, x, y, s, size=14, fill="ink", bg="bg", weight="normal", anchor="start"):
        TEXT_PAIRS.append((fill, bg, size, weight, s))
        s = s.replace("&", "&amp;").replace("<", "&lt;")
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
                          f'fill="{self.t[fill]}" text-anchor="{anchor}">{s}</text>')

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.head + "\n".join(self.parts) + "\n</svg>\n")


TILE_CYCLE = ["lilac", "mint", "butter"]


def pipeline(t):
    w, h = 868, 470
    s = Svg(w, h, "Pipeline from data to firmware",
            "Six steps in two rows: data, split, train, evaluate, quantise, firmware. Each tile has a number "
            "and a two-line caption.", t)
    s.rect(0, 0, w, h, 28, "bg")
    s.text(32, 46, "From video to firmware", 20, "ink", "bg", "bold")
    steps = [("Data", "Labelled video clips,", "boxes become crops"),
             ("Split", "Whole scenes go to", "train, val or test"),
             ("Train", "MobileNetV3-Small,", "fine-tuned on CPU"),
             ("Evaluate", "Test split only,", "intervals by video"),
             ("Quantise", "ONNX, then int8,", "size and accuracy"),
             ("Firmware", "C++ state logic,", "tested on a laptop")]
    for i, (title, l1, l2) in enumerate(steps):
        col, row = i % 3, i // 3
        x, y = 32 + col * (252 + 24), 72 + row * (150 + 24)
        tile = TILE_CYCLE[i % 3]
        s.rect(x, y, 252, 150, 22, tile)
        s.circle(x + 36, y + 40, 17, "ink")
        s.text(x + 36, y + 46, str(i + 1), 16, "bg", "ink", "bold", "middle")
        s.text(x + 66, y + 46, title, 18, "ink", tile, "bold")
        s.text(x + 24, y + 92, l1, 13, "ink", tile)
        s.text(x + 24, y + 116, l2, 13, "ink", tile)
        if col < 2:  # connector dots between tiles
            for k in range(3):
                s.circle(x + 252 + 6 + k * 6, y + 75, 2.5, "muted")
    s.text(32, 440, "Every step is a script in this repo. Numbers appear only where a run produced them.",
           13, "muted", "bg")
    return s


def split_by_scene(t):
    w, h = 868, 470
    s = Svg(w, h, "Why the split is by scene",
            "Left panel: a random frame split puts frames from one scene into train, validation and test, "
            "so the test set leaks. Right panel: whole scenes are assigned to one split each.", t)
    s.rect(0, 0, w, h, 28, "bg")
    s.text(32, 46, "Split by scene, not by frame", 20, "ink", "bg", "bold")
    # panels
    for px, label, tile in [(32, "Random frame split: leaks", "butter"), (452, "Split by scene: no leak", "mint")]:
        s.rect(px, 72, 384, 340, 22, tile)
        s.text(px + 24, 106, label, 15, "ink", tile, "bold")
    sp = [("train", "tr"), ("val", "va"), ("test", "te")]

    def dot(cx, cy, which):
        key, ab = sp[which]
        s.circle(cx, cy, 12, key)
        s.text(cx, cy + 4, ab, 12, "onsplit", key, "bold", "middle")

    # left: two scenes, every scene contains all three splits
    for sx, name in [(80, "scene A"), (270, "scene B")]:
        s.rect(sx - 30, 128, 150, 132, 22, "surface")
        s.text(sx - 14, 152, name, 13, "muted", "surface")
        for i in range(6):
            dot(sx + (i % 3) * 36 - 6, 184 + (i // 3) * 38, (i * 2 + i // 3) % 3)
    s.text(56, 292, "Near-identical frames sit", 13, "ink", "butter")
    s.text(56, 312, "in train and in test.", 13, "ink", "butter")
    s.text(56, 346, "The test score looks better", 13, "ink", "butter")
    s.text(56, 366, "than it should.", 13, "ink", "butter")
    # right: each scene one split
    for k, (sx, which, name) in enumerate([(500, 0, "scene A"), (690, 1, "scene B")]):
        s.rect(sx - 30, 128, 150, 132, 22, "surface")
        s.text(sx - 14, 152, name, 13, "muted", "surface")
        for i in range(6):
            dot(sx + (i % 3) * 36 - 6, 184 + (i // 3) * 38, which)
    s.text(476, 292, "Whole scenes go to one split.", 13, "ink", "mint")
    s.text(476, 312, "Scenes are grouped by", 13, "ink", "mint")
    s.text(476, 332, "perceptual hash.", 13, "ink", "mint")
    s.text(476, 366, "Limit: it finds near-identical", 13, "ink", "mint")
    s.text(476, 386, "scenes only.", 13, "ink", "mint")
    # legend
    lx = 32
    for i, (key, ab) in enumerate(sp):
        s.circle(lx + 12, 442, 10, key)
        s.text(lx + 30, 447, f"{ab} = {key}", 13, "ink", "bg")
        lx += 150
    return s


def board_data_path(t):
    w, h = 868, 440
    s = Svg(w, h, "Generic vision board data path",
            "A camera sends frames to a microcontroller in the middle. The microcontroller exchanges tensors with "
            "an optional accelerator, reads and writes memory, and sends results out over a host link. A strip "
            "says nothing here is measured on hardware.", t)
    s.rect(0, 0, w, h, 28, "bg")
    s.text(32, 46, "A generic vision board: where the data goes", 20, "ink", "bg", "bold")
    boxes = {  # name: (x, y, w, h, tile, title, subtitle)
        "camera": (32, 80, 190, 90, "lilac", "Camera", "sends frames"),
        "accel": (32, 220, 190, 90, "butter", "Accelerator", "optional, runs model"),
        "mcu": (339, 80, 190, 230, "mint", "Microcontroller", "runs the logic"),
        "host": (646, 80, 190, 90, "butter", "Host link", "results out"),
        "mem": (646, 220, 190, 90, "lilac", "Memory", "weights, buffers"),
    }
    # straight horizontal links at box mid-heights: (left box edge x, right box edge x, y, label)
    links = [(222, 339, 125, "frame"), (529, 646, 125, "results"),
             (222, 339, 265, "tensors"), (529, 646, 265, "read, write")]
    for x1, x2, y, label in links:
        s.line(x1, y, x2, y)
        s.circle(x1, y, 5, "ink")
        s.circle(x2, y, 5, "ink")
        s.text((x1 + x2) / 2, y - 10, label, 12, "muted", "bg", "normal", "middle")
    for k, (x, y, bw, bh, tile, a, b2) in boxes.items():
        s.rect(x, y, bw, bh, 22, tile)
        s.text(x + 20, y + 38, a, 15, "ink", tile, "bold")
        s.text(x + 20, y + 62, b2, 12, "ink", tile)
    s.rect(32, 340, 804, 52, 22, "surface")
    s.circle(62, 366, 8, "accent")
    s.text(82, 371, "not measured on hardware: no board was used,", 12, "ink", "surface")
    s.text(82, 389 - 2, "so this figure shows no speed, power or memory size", 12, "ink", "surface")
    return s


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for name, fn in [("pipeline", pipeline), ("split-by-scene", split_by_scene),
                     ("board-data-path", board_data_path)]:
        for variant, suffix in [("light", ""), ("dark", "-dark")]:
            TEXT_PAIRS.clear()
            svg = fn(TOKENS[variant])
            path = OUT / f"{name}{suffix}.svg"
            svg.save(path)
            made.append(path)
            check(name, variant, list(TEXT_PAIRS))
    sys.path.insert(0, str(Path(__file__).parent))
    import results_figure
    for variant, suffix in [("light", ""), ("dark", "-dark")]:
        TEXT_PAIRS.clear()
        svg = results_figure.build(Svg, TOKENS[variant], ROOT)
        path = OUT / f"results{suffix}.svg"
        svg.save(path)
        made.append(path)
        check("results", variant, list(TEXT_PAIRS))
    write_contrast()
    print("wrote", len(made), "figures to", OUT)


CHECKS = []


def check(figure, variant, pairs):
    t = TOKENS[variant]
    seen = {}
    for fg, bg, size, weight, s in pairs:
        ratio = contrast(t[fg], t[bg])
        large = size >= 24 or (size >= 18.66 and weight == "bold")
        need = 3.0 if large else 4.5
        key = (fg, bg, large)
        if key not in seen or ratio < seen[key][0]:
            seen[key] = (ratio, need)
    for (fg, bg, large), (ratio, need) in seen.items():
        CHECKS.append({"figure": figure, "variant": variant, "text": fg, "background": bg,
                       "ratio": round(ratio, 2), "required": need, "pass": ratio >= need})


def write_contrast():
    fails = [c for c in CHECKS if not c["pass"]]
    out = {"label": "measured (host CPU)", "command": "python scripts/make_figures.py",
           "method": "WCAG 2.x relative-luminance contrast ratio of each text colour on its background colour",
           "pairs_checked": len(CHECKS), "failures": len(fails), "lowest_ratio": min(c["ratio"] for c in CHECKS),
           "failing_pairs": fails, "pairs": CHECKS}
    p = ROOT / "results" / "contrast_check.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, indent=1))
    print(f"contrast: {len(CHECKS)} pairs, {len(fails)} failures, lowest {out['lowest_ratio']}")
    if fails:
        for c in fails:
            print("FAIL", c)
        sys.exit(1)


if __name__ == "__main__":
    main()
