#!/usr/bin/env bash
# Preflight before publishing. Read-only: uses only read-only git commands.
# Run from the repo root: bash scripts/preflight.sh
# Exit code 1 if any check fails.
set -u
fail=0
cd "$(git rev-parse --show-toplevel)" || exit 2

echo "== (a) banned terms in non-ignored files (CLAUDE.md and this script excluded)"
# The pattern list lives in this script, so the script itself is excluded.
files=$(git ls-files -co --exclude-standard | grep -v -E '^(CLAUDE\.md|scripts/preflight\.sh)$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)
hits=$(printf '%s\n' "$files" | xargs grep -n -i -I -E 'proa|metcube|internship|imx519|unimelb|student' 2>/dev/null)
if [ -n "$hits" ]; then echo "$hits"; echo "FAIL: banned terms found"; fail=1; else echo "ok: none found"; fi

echo "== (b) files over 5 MB (non-ignored)"
big=$(printf '%s\n' "$files" | while read -r f; do [ -f "$f" ] && [ "$(wc -c < "$f")" -gt 5242880 ] && echo "$f"; done)
if [ -n "$big" ]; then echo "$big"; echo "FAIL: large files"; fail=1; else echo "ok: none"; fi

echo "== (c) ignore rules"
mkdir -p .preflight-probe
for p in data/probe models/probe probe/a.onnx probe/a.tflite probe/a.h5 probe/a.mp4 probe/a.jpg probe/a.png; do
  if git check-ignore -q "$p"; then :; else echo "FAIL: not gitignored: $p"; fail=1; fi
done
rmdir .preflight-probe 2>/dev/null
tracked_private=$( { git ls-files web/design/reference-private; git diff --cached --name-only -- web/design/reference-private; } 2>/dev/null )
if [ -n "$tracked_private" ]; then echo "FAIL: reference-private is tracked or staged:"; echo "$tracked_private"; fail=1; else echo "ok: nothing under web/design/reference-private is tracked or staged"; fi
bad_tracked=$(git ls-files | grep -E '\.(onnx|tflite|h5|mp4|jpg|jpeg|png|webp)$' | grep -v -E '^(docs/img/|web/public/)')
if [ -n "$bad_tracked" ]; then echo "FAIL: media or model files tracked outside docs/img and web/public:"; echo "$bad_tracked"; fail=1; else echo "ok: no tracked media or model files outside docs/img and web/public"; fi
for q in data/ models/; do git check-ignore -q "$q" || { echo "FAIL: $q not ignored"; fail=1; }; done

echo "== (d) git status"
git status --short

if [ "$fail" -ne 0 ]; then echo "PREFLIGHT FAILED"; exit 1; fi
echo "PREFLIGHT OK"
