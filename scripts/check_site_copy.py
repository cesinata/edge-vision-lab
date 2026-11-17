"""Check that every piece of wording in docs/site-copy.md is on the built website.

    python scripts/check_site_copy.py        (run `npm run build` in web/ first)

Splits the copy file into its sentences, headings, table cells and bullets, then looks for each one
in the generated web/src/content/copy.ts and in the built JavaScript. The one number the copy
quotes (drone recall) is checked against results/eval_torch.json instead. Exits 1 on any miss.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
md = (ROOT / "docs/site-copy.md").read_text()
copy_ts = (ROOT / "web/src/content/copy.ts").read_text()
copy = json.loads(copy_ts[copy_ts.index("{"):copy_ts.rindex("}") + 1])
flat = json.dumps(copy, ensure_ascii=False)
dist = sorted((ROOT / "web/dist/assets").glob("index-*.js"))
if not dist:
    sys.exit("web/dist is missing: run npm run build in web/ first")
bundle = "".join(p.read_text() for p in dist)
recall = f"{json.loads((ROOT / 'results/eval_torch.json').read_text())['per_class']['drone']['recall']:.3f}"

snips = []
SECTION_NAMES = {"Header", "Hero", "Footer"}  # structure of the copy file, not site text
for line in md.splitlines():
    line = line.rstrip()
    if not line.strip() or line.startswith(("# ", "---")) or (line.startswith("|") and set(line.replace("|", "").strip()) <= set("- ")):
        continue
    if line.startswith(("Public-safe", "Voice:")):  # notes to the editor, not site text
        continue
    if line.startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] in ("Step", "#"):  # table header row: column names, not site text
            continue
        snips += cells
        continue
    line = re.sub(r"^(- |\d\. |## )", "", line)
    if line in SECTION_NAMES:
        continue
    line = re.sub(r"^\*\*(Headline|Heading|Lead|Buttons|Next steps|Intro):?\*?\*?:? ?", "", line)
    line = re.sub(r"^(Caption under the drawing|Caption|Readouts|Site name|Nav): ?", "", line)
    m = re.match(r"\*\*(.*?)\*\*\s*(.*)$", line)  # a bold lead-in is stored apart from its sentence
    if m:
        snips += [m.group(1), m.group(2)]
    else:
        snips.append(line)

missing = []
n = 0
for sn in snips:
    sn = sn.strip()
    if not sn:
        continue
    # lists of items separated by the middle dot are stored as separate strings
    parts = [p.strip() for p in sn.split(" · ")] if re.fullmatch(r"[^.]*( · [^.]*)+", sn) and len(sn) < 90 else [sn]
    for p in parts:
        n += 1
        probe = p.replace(recall, "{{drone_recall}}")
        if probe not in flat and p not in flat:
            missing.append(("copy.ts", p[:90]))
        # the built JS holds the same strings (minified, so compare a distinctive stretch)
        key = probe[:40]
        if key not in bundle and key.encode("unicode_escape").decode() not in bundle:
            missing.append(("built JS", p[:90]))
print(f"checked {n} pieces of copy against copy.ts and the built JS; missing: {len(missing)}")
for where, s in missing[:20]:
    print("  MISSING in", where, ":", s)
sys.exit(1 if missing else 0)
