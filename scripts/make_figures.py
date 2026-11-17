"""Generate the README figures in docs/img/ in the Option A (Datasheet) style, light and dark.

    python scripts/make_figures.py

Style: docs/illustration-style.md. Original fine-line drawings: 1.5 px strokes, round caps, no fills
except the yellow highlight and background masks. Text uses a system monospace stack because README
SVGs cannot load web fonts. The results figure is drawn from results/eval_torch.json and
bench/results.json and says "not run yet" for anything missing. Also runs a WCAG contrast check on
every text and background pair used and writes results/contrast_check.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img"
FONT = 'ui-monospace, "SF Mono", Menlo, Consolas, monospace'

TOKENS = {
    "light": dict(bg="#FFFFFF", panel="#F7F9FC", grid="#E3E9F2", ink="#03234B", ink2="#2A4365", muted="#3C5677",
                  rule="#C6D2E1", line="#03234B", mark="#FFD200", onink="#FFFFFF", onmark="#03234B"),
    "dark": dict(bg="#0B1A2E", panel="#10243F", grid="#1A3354", ink="#EAF2FB", ink2="#C9D8EA", muted="#A8BCD6",
                 rule="#2B4A70", line="#8FD3F4", mark="#FFD200", onink="#0B1A2E", onmark="#03234B"),
}
TEXT_PAIRS = []


def luminance(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class Svg:
    def __init__(self, w, h, title, desc, t):
        self.w, self.h, self.t, self.p = w, h, t, []
        self.head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
                     f'aria-labelledby="t d" font-family=\'{FONT}\' fill="none" stroke="{t["line"]}" stroke-width="1.5" '
                     f'stroke-linecap="round" stroke-linejoin="round">\n<title id="t">{title}</title>\n<desc id="d">{desc}</desc>\n')
        self.p.append(f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="6" fill="{t["bg"]}"/>')

    def raw(self, s):
        self.p.append(s)

    def rect(self, x, y, w, h, fill=None, rx=0, stroke=True, sw=None, extra=""):
        f = self.t[fill] if fill else "none"
        st = "" if stroke else ' stroke="none"'
        sws = f' stroke-width="{sw}"' if sw else ""
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}"{st}{sws} {extra}/>')

    def text(self, x, y, s, size=13, fill="ink", bg="bg", weight=400, anchor="start", spacing=None):
        TEXT_PAIRS.append((fill, bg, size, weight))
        sp = f' letter-spacing="{spacing}"' if spacing else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;")
        self.p.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{self.t[fill]}" stroke="none" '
                      f'text-anchor="{anchor}"{sp}>{s}</text>')

    def label(self, x, y, s, bg="bg"):
        self.text(x, y, s.upper(), 12, "muted", bg, 500, spacing="0.72")

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.head + "\n".join(self.p) + "\n</svg>\n")


# fine-line icons for the pipeline, 48 x 48 (same drawings as the website)
ICONS = [
    ('<rect x="6" y="12" width="36" height="24" rx="3"/><path d="M6 18H42M6 30H42M12 12V18M18 12V18M24 12V18M30 12V18M36 12V18M12 30V36M18 30V36M24 30V36M30 30V36M36 30V36"/><rect x="19" y="20" width="10" height="8" fill="{mark}" stroke="none"/>'),
    ('<circle cx="24" cy="8" r="4"/><path d="M24 12V20M24 20L10 32M24 20V32M24 20L38 32"/><rect x="5" y="32" width="10" height="10" rx="2"/><rect x="19" y="32" width="10" height="10" rx="2"/><rect x="33" y="32" width="10" height="10" rx="2" fill="{mark}"/>'),
    ('<path d="M10 14L24 10M10 14L24 24M10 14L24 38M10 34L24 10M10 34L24 24M10 34L24 38M24 10L38 24M24 24L38 24M24 38L38 24"/><circle cx="10" cy="14" r="3.5" fill="{bg}"/><circle cx="10" cy="34" r="3.5" fill="{bg}"/><circle cx="24" cy="10" r="3.5" fill="{bg}"/><circle cx="24" cy="24" r="3.5" fill="{bg}"/><circle cx="24" cy="38" r="3.5" fill="{bg}"/><circle cx="38" cy="24" r="3.5" fill="{mark}"/>'),
    ('<rect x="8" y="8" width="32" height="32" rx="2"/><path d="M8 18.7H40M8 29.3H40M18.7 8V40M29.3 8V40"/><rect x="10" y="10" width="7" height="7" fill="{mark}" stroke="none"/><rect x="20.7" y="20.7" width="7" height="7" fill="{mark}" stroke="none"/><rect x="31.3" y="31.3" width="7" height="7" fill="{mark}" stroke="none"/>'),
    ('<rect x="5" y="7" width="22" height="22" rx="2"/><path d="M5 14H27M5 21H27M12 7V29M19 7V29M28 30L34 34M34 34V29M34 34H29"/><rect x="34" y="34" width="10" height="10" rx="1.5" fill="{mark}"/>'),
    ('<rect x="13" y="13" width="22" height="22" rx="3"/><rect x="19" y="19" width="10" height="10" rx="1" fill="{mark}"/><path d="M18 13V7M24 13V7M30 13V7M18 35V41M24 35V41M30 35V41M13 18H7M13 24H7M13 30H7M35 18H41M35 24H41M35 30H41"/>'),
]


def pipeline(t):
    w, h = 880, 330
    s = Svg(w, h, "Pipeline from data to firmware",
            "Six numbered cells in a row: data, split, train, evaluate, quantise and firmware, each with a small line icon and a short caption.", t)
    s.label(28, 34, "Fig. 1 · The pipeline")
    s.text(28, 64, "From video to firmware", 20, "ink", "bg", 600)
    steps = [("01", "Data", ["Labelled video", "clips; boxes", "become crops"]),
             ("02", "Split", ["Whole scenes go", "to train, val,", "or test"]),
             ("03", "Train", ["Small network,", "fine-tuned on", "a laptop CPU"]),
             ("04", "Evaluate", ["Test split only", "intervals by", "video"]),
             ("05", "Quantise", ["ONNX, then int8", "size and", "accuracy"]),
             ("06", "Firmware", ["C++ state logic", "tested on a", "laptop"])]
    x0, y0, cw = 28, 92, 824 / 6
    s.rect(x0, y0, 824, 210, "bg", rx=6, extra=f'stroke="{t["ink"]}"')
    for i, (n, title, lines) in enumerate(steps):
        cx = x0 + i * cw
        if i:
            s.raw(f'<path d="M{cx:.1f} {y0}V{y0 + 210}" stroke="{t["rule"]}" stroke-width="1"/>')
        s.text(cx + 14, y0 + 28, n, 12, "muted", "bg", 500)
        s.raw(f'<g transform="translate({cx + 14:.1f} {y0 + 40})" stroke="{t["line"]}">' + ICONS[i].format(mark=t["mark"], bg=t["bg"]) + "</g>")
        s.text(cx + 14, y0 + 118, title, 14, "ink", "bg", 600)
        for k, ln in enumerate(lines):
            s.text(cx + 14, y0 + 142 + k * 17, ln, 12, "ink2", "bg")
    return s


def split_by_scene(t):
    w, h = 880, 360
    s = Svg(w, h, "Why the split is by scene",
            "Left: six scenes of four frames each, every scene entirely train, validation or test. Right: a random frame split mixes train and test frames from the same scenes. A legend explains the fills.", t)
    s.raw('<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          f'<path d="M0 0V6" stroke="{t["line"]}" stroke-width="2"/></pattern></defs>')
    s.label(28, 34, "Fig. 3 · Why the split is by scene")
    s.text(28, 64, "Split by scene, not by frame", 20, "ink", "bg", 600)

    def frame(x, y, kind):
        fill = {"train": t["ink"], "test": t["mark"], "validation": "url(#hatch)"}[kind]
        s.raw(f'<rect x="{x}" y="{y}" width="30" height="30" rx="2" fill="{fill}"/>')

    s.rect(28, 88, 520, 196, "panel", rx=6, extra=f'stroke="{t["ink"]}"')
    s.text(44, 112, "scenes: each box stays on one side", 12, "ink2", "panel", 500)
    kinds = ["train", "train", "validation", "train", "test", "test"]
    for i, k in enumerate(kinds):
        bx, by = 44 + (i % 3) * 165, 126 + (i // 3) * 78
        s.rect(bx, by, 154, 66, "bg", rx=4)
        for f in range(4):
            frame(bx + 10 + f * 35, by + 18, k)
    s.rect(572, 88, 280, 196, "bg", rx=6, extra=f'stroke="{t["ink"]}" stroke-dasharray="6 4"')
    s.text(588, 112, "random split: the same scene", 12, "ink2", "bg", 500)
    s.text(588, 128, "lands on both sides", 12, "ink2", "bg", 500)
    mix = "TXTTXTTXTTXTXTTT"
    for i, c in enumerate(mix):
        frame(592 + (i % 4) * 62, 144 + (i // 4) * 34, "train" if c == "T" else "test")
    for j, (k, x) in enumerate([("train", 28), ("validation", 150), ("test", 330)]):
        frame(x, 300, k)
        s.text(x + 42, 321, k, 13, "ink", "bg", 500)
    s.text(28, 348, "Each box is one scene. A random frame split (right) leaks the same scene into both sides.", 12, "muted", "bg", 500)
    return s


def board_data_path(t):
    w, h = 880, 400
    s = Svg(w, h, "Generic vision board data path",
            "A camera feeds a microcontroller in the middle, which exchanges tensors with an optional accelerator, reads and writes memory, and sends results out over a host link. A strip says nothing here is measured on hardware.", t)
    s.label(28, 34, "Fig. 4 · A generic vision board")
    s.text(28, 64, "Where the data goes", 20, "ink", "bg", 600)

    def box(x, y, bw, bh, title, sub, fill="bg"):
        s.rect(x, y, bw, bh, fill, rx=6, extra=f'stroke="{t["ink"]}"')
        bgk = "mark" if fill == "mark" else "bg"
        s.text(x + 14, y + 30, title, 14, "onmark" if fill == "mark" else "ink", bgk, 600)
        s.text(x + 14, y + 50, sub, 12, "onmark" if fill == "mark" else "ink2", bgk)

    box(28, 92, 210, 80, "Camera", "sends frames")
    box(28, 224, 210, 80, "Accelerator", "optional, runs the model", "mark")
    box(335, 92, 210, 212, "Microcontroller", "runs the logic")
    s.raw(f'<rect x="395" y="168" width="90" height="90" rx="4" fill="{t["bg"]}"/><rect x="415" y="188" width="50" height="50" rx="3" fill="{t["mark"]}"/>'
          '<path d="M410 168V158M430 168V158M450 168V158M470 168V158M410 258V268M430 258V268M450 258V268M470 258V268M395 190H385M395 210H385M395 230H385M485 190H495M485 210H495M485 230H495"/>')
    box(642, 92, 210, 80, "Host link", "results out")
    box(642, 224, 210, 80, "Memory", "weights, buffers")
    for (x1, x2, y, lab) in [(238, 335, 132, "frame"), (545, 642, 132, "results"), (238, 335, 264, "tensors"), (545, 642, 264, "read, write")]:
        s.raw(f'<path d="M{x1} {y}H{x2}"/><circle cx="{x1}" cy="{y}" r="3.5" fill="{t["line"]}"/><circle cx="{x2}" cy="{y}" r="3.5" fill="{t["line"]}"/>')
        s.text((x1 + x2) / 2, y - 10, lab, 12, "muted", "bg", 500, "middle")
    s.rect(28, 330, 824, 50, "panel", rx=6, extra=f'stroke="{t["ink"]}"')
    s.raw(f'<circle cx="52" cy="355" r="6" fill="{t["mark"]}"/>')
    s.text(70, 360, "not measured on hardware: no board was used, so this shows no speed, power or memory size", 12, "ink", "panel", 500)
    return s


CHECKS = []


def check(figure, variant, pairs):
    t = TOKENS[variant]
    seen = {}
    for fg, bg, size, weight in pairs:
        ratio = contrast(t[fg], t[bg])
        large = size >= 24 or (size >= 18.66 and weight >= 600)
        need = 3.0 if large else 4.5
        key = (fg, bg, large)
        if key not in seen or ratio < seen[key][0]:
            seen[key] = (ratio, need)
    for (fg, bg, large), (ratio, need) in seen.items():
        CHECKS.append({"figure": figure, "variant": variant, "text": fg, "background": bg, "ratio": round(ratio, 2),
                       "required": need, "pass": ratio >= need})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(Path(__file__).parent))
    import results_figure
    made = []
    for name, fn in [("pipeline", pipeline), ("split-by-scene", split_by_scene), ("board-data-path", board_data_path),
                     ("results", lambda t: results_figure.build(Svg, t, ROOT))]:
        for variant, suffix in [("light", ""), ("dark", "-dark")]:
            TEXT_PAIRS.clear()
            svg = fn(TOKENS[variant])
            path = OUT / f"{name}{suffix}.svg"
            svg.save(path)
            made.append(path)
            check(name, variant, list(TEXT_PAIRS))
    fails = [c for c in CHECKS if not c["pass"]]
    rep = {"label": "measured (host CPU)", "command": "python scripts/make_figures.py",
           "method": "WCAG 2.x contrast ratio of each text colour on its background colour, per figure and variant",
           "pairs_checked": len(CHECKS), "failures": len(fails), "lowest_ratio": min(c["ratio"] for c in CHECKS),
           "failing_pairs": fails, "pairs": CHECKS}
    (ROOT / "results" / "contrast_check.json").write_text(json.dumps(rep, indent=1))
    print(f"wrote {len(made)} figures; contrast: {len(CHECKS)} pairs, {len(fails)} failures, lowest {rep['lowest_ratio']}")
    if fails:
        for c in fails:
            print("FAIL", c)
        sys.exit(1)


if __name__ == "__main__":
    main()
