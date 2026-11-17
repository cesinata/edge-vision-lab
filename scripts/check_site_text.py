"""Scan the built site, the site source and the README for terms that must not appear.

    python scripts/check_site_text.py        (run `npm run build` in web/ first)

Looks for: solar, logo, the banned employer/course terms, and "object detection" (printed for a
human to read: it is fine when it says this project does NOT do detection, and wrong when it is
used about this project's model). web/design/ is excluded: it holds the reference mock-up, which is
never shipped. Exits 1 on any hard hit.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = [ROOT / "README.md"] + sorted((ROOT / "web/src").rglob("*.ts*")) + sorted((ROOT / "web/src").rglob("*.css"))
files += sorted((ROOT / "docs/img").glob("*.svg")) + sorted((ROOT / "web/dist").rglob("*.html"))
files += sorted((ROOT / "web/dist/assets").glob("index-*.*"))
HARD = re.compile(r"solar|logo|proa|metcube|internship|imx519|unimelb|student|employer", re.I)
hard, soft = [], []
for f in files:
    if "design" in f.parts and "web" in f.parts and f.parent.name == "design":
        continue
    text = f.read_text(errors="ignore")
    for m in HARD.finditer(text):
        ctx = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
        # "catalog", "logos" etc. are not the word: ignore substrings inside longer words for 'logo'
        if m.group(0).lower() == "logo" and re.search(r"[A-Za-z]logo|logo[a-z]", text[max(0, m.start() - 1):m.end() + 1]):
            continue
        hard.append((f.relative_to(ROOT), ctx))
    for m in re.finditer(r"object detection", text, re.I):
        soft.append((f.relative_to(ROOT), text[max(0, m.start() - 70):m.end() + 50].replace("\n", " ")))
print(f"scanned {len(files)} files")
print(f"hard hits: {len(hard)}")
for f, c in hard[:15]:
    print("  HIT", f, "...", c)
print(f"'object detection' mentions to read: {len(soft)}")
for f, c in soft[:12]:
    print("  READ", f, "...", c)
sys.exit(1 if hard else 0)
