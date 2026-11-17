"""WCAG contrast check of the website's colour tokens, read from web/src/styles.css.

    python scripts/check_contrast.py

Checks every text pair the site uses, in light and in both dark blocks (the media query and the
manual toggle), plus the illustration stroke colour against the page (3:1, non-text). Writes
results/site_contrast.json and exits 1 on any failure. Yellow (--mark) is only ever a fill, and the
only text on it is --ink-on-yellow (the light-theme ink), so that pair is checked too.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
css = (ROOT / "web/src/styles.css").read_text()


def block(start_pat):
    m = re.search(start_pat + r"\s*\{([^}]*)\}", css, re.S | re.M)
    assert m, start_pat
    return dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", m.group(1)))


light = block(r"^:root")
dark_media = block(r'@media \(prefers-color-scheme: dark\) \{\s*:root:not\(\[data-theme="light"\]\)')
dark_manual = block(r':root\[data-theme="dark"\]')
THEMES = {"light": light, "dark (system)": {**light, **dark_media}, "dark (toggle)": {**light, **dark_manual}}


def lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(a, b):
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# (foreground token, background token, what it is, minimum ratio)
PAIRS = [
    ("ink", "bg", "body and heading text", 4.5), ("ink-2", "bg", "secondary text", 4.5), ("muted", "bg", "labels and captions", 4.5),
    ("ink", "panel", "text on grid-paper panels", 4.5), ("ink-2", "panel", "secondary text on panels", 4.5),
    ("muted", "panel", "captions on panels", 4.5), ("on-ink", "ink", "primary button and number badges", 4.5),
    ("line", "bg", "illustration strokes (non-text)", 3.0), ("line", "panel", "illustration strokes on panels (non-text)", 3.0),
    ("ink", "mark", "text on a yellow highlight (light-theme ink)", 4.5),
]
rows, fails = [], []
for theme, t in THEMES.items():
    for fg, bg, what, need in PAIRS:
        fgc = "#03234b" if (fg, bg) == ("ink", "mark") else t[fg]  # on yellow the text is always the dark ink
        r = ratio(fgc, t[bg])
        row = {"theme": theme, "text": fg, "background": bg, "use": what, "ratio": round(r, 2), "required": need, "pass": r >= need}
        rows.append(row)
        if not row["pass"]:
            fails.append(row)
out = {"label": "measured (host CPU)", "command": "python scripts/check_contrast.py", "source": "web/src/styles.css",
       "pairs_checked": len(rows), "failures": len(fails), "lowest_ratio": min(r["ratio"] for r in rows), "failing_pairs": fails, "pairs": rows}
(ROOT / "results/site_contrast.json").write_text(json.dumps(out, indent=1))
print(f"site contrast: {len(rows)} pairs across {len(THEMES)} themes, {len(fails)} failures, lowest {out['lowest_ratio']}")
for f in fails:
    print("FAIL", f)
sys.exit(1 if fails else 0)
