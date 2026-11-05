# CLAUDE.md: edge-vision-lab

Instructions for AI assistants working in this repo. Read this file fully before doing anything.

## What this project is

A public portfolio repo: **train a small bird / drone / neither image classifier, quantise it, measure it, test microcontroller state and power logic on a laptop, and teach the whole pipeline on an interactive website.**

- It is image classification on crops, not object detection. Say so wherever results are described.
- No microcontroller board is available. Everything must work without one.
- Audience: people hiring for ML engineer, edge AI and junior software roles, and learners new to edge AI.

## Voice

Direct, concrete, no buzzwords, no emojis, no hype. Text reads like a careful engineer explaining what was done and what was not. First person is fine in decisions sections.

## Rules that override everything

1. **Never invent a number, result, tool or claim.** If a value is not in the repo's own output, do not write it. Ask.
2. **Label every number** in code, README, docs and the website as one of:
   - `measured (host CPU)` or `measured (browser)`: produced by code in this repo, with the command that reproduces it
   - `estimated (tool name)`: a tool report, naming the tool and version
   - `simulated`: from an emulator or model, naming it
   - `vendor-published`: from a third party's document, with the source
   - `not measured on hardware`: the default for anything about the microcontroller itself
3. **Public material only.** No employer, client or university-assessment material may appear in this repo: no code, file names, architecture, driver or register tables, datasets, images, diagrams or screenshots. Do not ask for such material. Do not name employers, client projects or course units in any file.
4. **No claims about a board.** Do not claim NPU performance, real-time FPS, power draw or on-device latency. Never present third-party figures as this project's results.
5. **Data.** Public datasets only, with the exact licence recorded in `docs/data.md`. Never commit raw datasets or images whose redistribution rights are not clear. Provide a download script and a small licensed sample instead. No sample images on the website until the owner approves them.
6. **Third-party material.** Do not copy vendor figures, PDFs, photos, datasheet text or pretrained weights into the repo. Draw illustrations as original SVG. Cite documents by title and number in `docs/sources.md`. Check a model's licence before committing any weights; prefer releases or download scripts.
7. **Learning content.** Draft notes may include analogies marked as unverified. Rewrite them in the owner's words and verify every technical claim against the official vendor or Arm document before it goes on the site. If it cannot be verified, leave it out or flag it as "unverified" in `docs/todo.md`.
8. **AI disclosure.** The README states that AI assistance (Claude) was used to draft and review code and text, that the owner ran the experiments, and that every number comes from a run. Keep that section.
9. **Git hygiene.** Keep existing history. No force pushes. One branch per phase, small commits, clear messages. No secrets, tokens, large binaries or model files in git history (use GitHub Releases or a download script). Assistants do not run `git commit`, `git push`, `git config`, `git reset --hard`, `git rebase` or `git tag`: at the end of a unit of work they give the owner the paths to add, a commit message (imperative, under 72 characters) and the branch name.
10. **When blocked, ask exactly one question** and wait. Otherwise proceed with a sensible default and record the assumption in `docs/decisions.md`.
11. **Local-only files.** Files excluded through `.git/info/exclude` are never linked from or quoted in tracked files.

## Target structure

```
edge-vision-lab/
  README.md                 problem, live link, results table, how to run, limits
  CLAUDE.md
  train/                    PyTorch and TensorFlow/Keras MobileNetV2, fixed split, metrics
  export/                   ONNX and int8 TFLite export, before/after accuracy
  bench/                    size, host-CPU latency, tensor arena report, results.json
  firmware/                 C++ state/power logic, CMake, unit tests (host build)
  web/                      interactive learning site (Vite, TypeScript, React)
  docs/                     case-study, decisions, lessons-learned, data, sources, todo
  .github/workflows/        CI: lint, tests, build, deploy site to GitHub Pages
```

## Default tech choices (change only with a note in `docs/decisions.md`)

- Python 3.11 or 3.12, `requirements.txt` with pinned versions, fixed seeds, one command to train and one to evaluate.
- PyTorch (torchvision MobileNetV2) and TensorFlow/Keras, same split and metrics, compared in one table.
- C++17 with CMake and Catch2 or GoogleTest. Firmware logic must build and test on the host with no board SDK, driven by scripted input traces (no `rand`, no `sleep`).
- Website: Vite, TypeScript, React, static site on GitHub Pages (set the Vite `base` path). In-browser demo uses ONNX Runtime Web. Browser timings are labelled `measured (browser)`.
- npm with a lockfile. No tracking, no external fonts or scripts that break offline use.

## Phases: do in order, stop at each Definition of Done, and report

0. **Audit** (done).
1. **Consolidate** (done). sentinel-vision was not imported.
2. **Honest evaluation.** Fixed split by cluster of near-identical frames, saved with seed. Recall, precision, F1, confusion matrix and PR curve on the test set only. In-domain and out-of-domain results reported separately. Error analysis of 20 to 30 misclassified images. Chosen threshold and its precision cost.
3. **PyTorch comparison.** Same split, same metrics, same table.
4. **Export and bench.** int8 export, accuracy before and after, size in KB, host-CPU latency, tensor arena size from the runtime, `bench/results.json` with a label on every field.
5. **Firmware host tests.** Unit tests, Mermaid state diagram, honest coverage.
6. **Learning site.** Pipeline, quantisation explorer, in-browser try-it, original SVG board explainer, memory budget, failure gallery, glossary and sources. Responsive, keyboard accessible, light and dark mode, alt text on every illustration, no page over 2 MB excluding the model.
7. **CI and deploy.** Lint, Python tests, C++ tests, web build, Pages deploy, badge and live link in the README.
8. **Docs.** case-study, decisions, lessons-learned, data, sources.

## Facts that may be used

- Vendor-published (label as such, and re-verify against the original document before publishing): ST-YOLOX COCO-Person on STM32N6570-DK, STEdgeAI Core v3.0.0: 192x192 input, 6.63 ms, 150.74 FPS, AP50 38.16%; 416x416 input, 21.3 ms, 46.95 FPS, AP50 54.8%. These are ST's numbers, not this project's.
- Everything else comes from this repo's own runs.

## Definition of done for the whole repo

- Clean clone runs with the README commands
- Every number is labelled and reproducible
- No secrets, private data, third-party figures or restricted material in history
- Live site deployed and linked, CI green
- README states what it does not do, the data licences and the AI disclosure
