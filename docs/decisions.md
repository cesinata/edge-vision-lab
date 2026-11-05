# Decisions

Format: what was decided, why, and what it replaced. Dates are 2026-11-05 unless stated.

## D1. Task: bird vs drone vs neither, as classification on crops
Chosen by the owner after the Phase 0 audit (option A). The model classifies a cropped image. It does not detect objects. The README says so.

## D2. sentinel-vision is not imported
It solves a different task (clean vs dusty solar panels), and its 9.4 MB `sentinel_model.h5` would enter this repo's history permanently, against the no-model-files rule. New training code will be written in `train/`. Only its ideas are reused: a fixed split and a recall/precision evaluation. The deviation from the original Phase 1 plan (a `git subtree` import) is deliberate.

## D3. Stale README numbers and committed models removed
"29.34 KB to 3.02 KB, 89.72%" described files from the first commit and cannot be reproduced. Removed from the README.
Removed from the working tree (still in history, not rewritten):
- `deployment/solar_guardian_quantized.tflite` (2,880,680 bytes). Per its script it is a stock ImageNet MobileNetV3Small quantised to int8, with no bird/drone training. The licence of the Keras ImageNet weights could not be verified (see `docs/todo.md`), so I chose removal over labelling it "untuned baseline" and keeping it.
- `solar_guardian_model.h5` (30,048 bytes). A one-convolution toy network; unknown whether it was ever trained; nothing loaded it.
`.gitignore` now blocks `*.h5`, `*.tflite`, `*.onnx`. Models will be published as GitHub Releases or via a download script.

## D4. Test images removed
`deployment/bird_test.jpg` and `deployment/drone_test.jpg` have unknown provenance and licence. Removed from the working tree. (`drone_test.jpg` was a WebP file with a `.jpg` extension.) `export/baseline_quantize.py` now takes `--calib-dir`.

## D5. Firmware
Phase 1 only moves the file to `firmware/`, renames its class, adds the missing `<cstdlib>` include and a `CMakeLists.txt`. The behaviour is unchanged, including the unhandled `STATE_RECOVERY` (one `-Wswitch` warning). The rewrite onto scripted input traces, a real watchdog or removal of recovery, and unit tests happen in Phase 5, as the phase plan has it. Decision from the owner: no `rand()` or `sleep` in the final version.

## D6. Old project name removed from new and edited files
An earlier project name that appeared in the original README and firmware has been removed from every new and edited file. Git history is not rewritten.

## D7. Layout
`deployment/` is replaced by `firmware/` and `export/`. `train/`, `bench/` and `web/` are created in the phases that fill them, not as empty folders.

## D8. Environment (assumption)
TensorFlow needs Python 3.11 or 3.12. This machine has 3.13 and 3.14 (Homebrew). I will use a pinned virtual environment in Phase 2 and record the exact versions then. `requirements.txt` is unpinned until it can be generated from a working environment.

## D9. Licence for this repo's code (assumption)
MIT, unless the owner prefers another. No `LICENSE` file has been added yet.
