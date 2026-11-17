#!/usr/bin/env bash
# Fetch the third-party general detector for the website demo into
# web/public/models/ (gitignored). Run before `npm run dev` or `npm run build`.
#
# Model: YOLOX-Nano ONNX, COCO-trained, Megvii-BaseDetection/YOLOX release
# 0.1.1rc0. Repository licence: Apache-2.0. Third-party pre-trained model, not
# trained by this project. See docs/sources.md.
set -eu
cd "$(dirname "$0")/.."
url="https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.onnx"
size=3659407
sha256="c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d"
dst="web/public/models/yolox_nano.onnx"
mkdir -p web/public/models
if [ ! -f "$dst" ]; then curl -sS -L -o "$dst" "$url"; fi
[ "$(wc -c < "$dst")" -eq "$size" ] || { echo "size mismatch for $dst" >&2; rm -f "$dst"; exit 1; }
echo "$sha256  $dst" | shasum -a 256 -c - >/dev/null || { echo "sha256 mismatch for $dst" >&2; rm -f "$dst"; exit 1; }
echo "ok: $dst ($size bytes, sha256 verified)"
