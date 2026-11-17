#!/usr/bin/env bash
# Copy the trained ONNX model into the website's public folder.
#
# WARNING: run this ONLY after the dataset authors have confirmed the data
# licence in writing and the repository owner has said so. The model was trained
# on the Svanstrom et al. dataset; publishing it before that is not allowed
# (see NOTICE and docs/todo.md). The model files are gitignored by default; this
# script copies into web/public/models/, which is tracked, so add them to git
# only after confirmation.
set -eu
cd "$(dirname "$0")/.."
if [ "${1:-}" != "--i-have-confirmed-the-licence" ]; then
  echo "Refusing to run. Read the warning in this script, then run:" >&2
  echo "  bash scripts/publish_model.sh --i-have-confirmed-the-licence" >&2
  exit 1
fi
src="models/model_int8.onnx"
[ -f "$src" ] || { echo "missing $src (run python export/export_onnx.py first)" >&2; exit 1; }
mkdir -p web/public/models
cp "$src" web/public/models/guardian_int8.onnx
echo "copied to web/public/models/guardian_int8.onnx"
echo "Now set MODEL_PUBLISHED=true in web/src/config.ts and rebuild."
