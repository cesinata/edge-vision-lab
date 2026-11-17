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

## D10. Dataset and split (Phase 2, owner decision 2026-11-06)
**Update 2026-11-06: the Mendeley "Drone vs Bird" dataset is rejected.** Its images are Pexels frames, and Pexels' help centre says its terms prohibit data mining and automated collection, explicitly including machine learning. Nothing was downloaded. A replacement is being researched (`docs/data.md`). The split method below stays, because it follows from the augmentation and clip structure of any video-derived dataset.
- (Original plan) Bird and drone: Mendeley "Drone vs Bird" (CC BY 4.0), see `docs/data.md`. "Neither": background crops from the same frames (train and main test), plus an Open Images subset with no Bird, Drone, Airplane, Helicopter or Kite labels, used only as an out-of-domain test set. Roboflow dropped.
- The provided `train`/`valid`/`test` folders are never reused. Augmentation is baked into the dataset and all images come from at most 42 source clips (`docs/data.md`), so near-identical frames would leak across a per-image split.
- Plan: (1) perceptual-hash duplicate check across the provided folders and report it; (2) cluster near-identical frames; (3) assign whole clusters to train, validation or test with a fixed seed; (4) save the assignment to disk. Cluster counts and the limits of this proxy for a split by clip go in the README.
- In-domain and out-of-domain metrics are reported separately.
- Class IDs and the label format are recorded only after inspecting the real download.
- Downloads: scripts only; no images are committed. Open Images attribution is generated as `attribution.csv`.

## D11. Public-safe CLAUDE.md
`CLAUDE.md` is now a public-safe version. The original is kept as an untracked private file excluded via `.git/info/exclude`.

## D12. Dataset: Svanstrom et al. visible-light videos (owner decision 2026-11-06)
Chosen after the Mendeley/Pexels rejection (D10). Licence confirmation from the authors is pending; nothing derived from the videos is published until then. Open Images is kept only as an out-of-domain test set. Details and verification are in `docs/data.md`.

## D13. How the "neither" class is built (assumption, easy to change)
Target-absent frames are too rare (82 frames in all) to form a class. Default: "neither" = background crops from regions of frames that do not overlap any box (same videos, so they follow the video's split), with airplane and helicopter crops used as hard negatives and reported as a separate slice, never mixed into a single "neither" number without the split shown. Open Images images with none of the labels Bird, Drone, Airplane, Helicopter, Kite are out-of-domain test only. In-domain and out-of-domain results are reported separately. Whether airplane and helicopter crops go into training is a flag to be decided when training code is written; the split does not depend on it.

## D14. Split by scene cluster, not by video
Over half the videos have another video with an identical-looking frame, and 114 drone videos fall into 8 scene clusters. So the split assigns whole clusters (pHash within 6 bits). The threshold is a judgement call: 6 bits of 64 is tight enough to keep distinct scenes apart (largest cluster 47 of 235) while joining repeated shots of one scene. A looser threshold merges more and leaves 4 cross-split pairs at 10 bits and 46 at 12 bits as residual similarity. Reported in the README.

## D15. Label decoding is our own, strict
`mcos-decoder` 0.1.0 mis-decodes bird videos (a 2 x 4 box array is read as "target absent"). `train/mat_labels.py` reuses only its stream walker and raises an error on any file that does not match the expected structure instead of guessing. `V_AIRPLANE_002` is excluded for that reason. Third-party dependency `mcos-decoder` is pinned in `train/requirements-data.txt`.

## D16. Environment for data work
Python 3.13.5 in a local `.venv/` (gitignored); pinned in `train/requirements-data.txt` from the installed packages. TensorFlow and PyTorch are not installed yet; whether TensorFlow supports Python 3.13 on this machine is unchecked (D8 still applies).

## D17. Evaluation reporting (owner decision 2026-11-06)
Per-class counts, per-video results and bootstrap confidence intervals resampled by video (`train/metrics.py`, 2000 replicates, seed fixed). The README says plainly that the test set is small and noisy. A video-level bootstrap treats videos as independent, which they are not when they share a scene (D14), so the intervals are optimistic.

## D18. Crops (Phase A)
Every 15th frame is sampled. Each box in a sampled frame gives one crop: a square of 2.0 times the box's longer side (at least 48 px), centred on the box and kept inside the frame, resized to 112 x 112 (the model upsamples to 224). One background crop is taken from every second sampled frame, sized from the video's median box, from a random region that overlaps no box in that frame. The script asserts that no scene cluster appears in two splits. Crops stay in `data/crops/` (gitignored); only counts are in `results/crops_summary.json`.
Limits seen when checking a montage of test crops by eye: most background crops are plain sky, so the background subtype is likely easy, and bird and drone targets are often only a few dozen pixels across.

## D19. Site design brief
`MVP_PROMPT.md` was not in the repo, so its "Peach & Ink" design brief could not be read. The site uses the Pastel Paper Mono tokens in `docs/illustration-style.md` instead (the most conservative option that keeps site and figures consistent). Swap the tokens in `web/src/styles.css` if the brief turns up.

## D20. Python and requirements
Python 3.12.16 (Homebrew) in `.venv312/`. `requirements.txt` pins the PyTorch and ONNX stack actually installed. `export/baseline_quantize.py` needs TensorFlow, which is not pinned or installed; it is a legacy, untuned-baseline script outside the pipeline.

## D21. Bird alert threshold (Phase C)
The alert score is P(bird). The cut-off is chosen on the validation split as the lowest threshold whose validation precision is at least 0.90, which gives the highest recall under that constraint. The 0.90 target is an illustrative requirement I picked, not a measured need; change `PRECISION_TARGET` in `train/evaluate.py` to try another. The test split is then scored at that threshold, at 0.5, and at the firmware's default 0.85, so the cost of each choice is visible. The firmware default of 0.85 comes from the original simulation and had no measurement behind it.

## D23. Firmware (Phase E)
`firmware/firmware_sim.cpp` (random inputs, endless loop, a watchdog that did nothing, an unreachable recovery state) was deleted and replaced by a library (`firmware/src/guardian.*`), a CLI that replays a CSV trace, and assert-based tests registered with CTest. All time comes from the trace, so there is no `rand()` or `sleep`. The watchdog and recovery are implemented and tested. Every transition lives in one table that the tests, the Mermaid diagram and the website's diagram all read. Test coverage is measured with gcov (`results/firmware_coverage.json`). Not covered: real timing, interrupts, sensor noise, clock wrap-around at about 49.7 days, and any real board.

## D24. Website (Phase G)
- Hash routing, so a static host needs no rewrite rules. Relative asset base, so it works on a GitHub project page.
- ONNX Runtime Web is loaded only when a demo starts. Its wasm binary is about 14.8 MB (file size, `measured (host CPU)`); the first page load is about 330 kB (decimal: one 323.5 kB script, 5.2 kB of CSS and the HTML), well under the 2 MB limit.
- The general detector is YOLOX-Nano (Apache-2.0), fetched at build time with a size and SHA-256 check, never committed. It is labelled a third-party pre-trained model.
- This project's model is behind `MODEL_PUBLISHED = false` in `web/src/config.ts`. No placeholder model is shipped. The code path for it exists but has never been run against a real published model.
- The failure gallery uses no dataset frames: abstract original drawings, and numbers from the evaluation.
- `?selftest=1` on the site runs the real load-and-infer path on a synthetic image. It was used with headless Chrome to check the built site loads the runtime and the detector. Headless Chrome's virtual time makes `performance.now()` meaningless, so no timing came from that run.

## D25. Figures
Three hand-drawn figures and one chart in `docs/img/`, light and dark, generated by `scripts/make_figures.py` from the style tokens. A WCAG contrast check runs on every text and background pair (`results/contrast_check.json`). It caught light text on the bright split colours in dark mode (ratios of about 1.4 to 2); I added a dark `onsplit` text token for those dots. The firmware state diagram is Mermaid, generated by `guardian_cli --mermaid`.

## D26. CI
`ci.yml` (Python lint and tests, CMake build and ctest, web typecheck, tests and build) and `pages.yml` (official Pages actions, pinned to major versions). Neither has been run: both were only syntax-checked as YAML. CI installs CPU-only PyTorch wheels from the PyTorch index to avoid a multi-gigabyte CUDA download; that index and version pin were not tested.

## D27. Licence holder
`LICENSE` is MIT with "the edge-vision-lab authors" as the holder, because I did not want to choose a legal name for the owner. Replace it with your own name if you prefer.

## D22. Quantisation: what failed, what I changed
First attempt: static int8 over all operators, min-max calibration on 198 train crops. On the epoch-1 weights it collapsed (the model called nearly everything "neither"). On the final weights, all 12 settings that quantised every convolution (three calibration methods, with or without all operator types, with or without the last layer in float) scored at most 0.531 validation macro F1 against 0.7676 for float32. The second round, added after seeing that, kept the depthwise and/or squeeze-and-excite convolutions (found by their `fc1`/`fc2` names and by `group > 1`) in float32. `percentile/conv_gemm/float-se+depthwise` scored 0.7318 on validation and was chosen. Selection used the validation split only; the test split was not used to choose. All 18 settings tried, including the failures, are in `results/quantisation_search.json`. The chosen model is therefore partly int8, and the README and bench file say so. Its bird alert is worse than float32's (average precision 0.633 against 0.810 on test).
The int8 test accuracy being slightly above float32's (0.758 against 0.736) is within the noise of this test set and is not evidence that quantisation helps.

## D28. What the AI got wrong, and what changed (this build)
- A third-party label decoder was trusted at first; it read two-bird frames as "target absent". Caught by comparing decoded label counts with video frame counts; replaced by a strict extractor (D15).
- The first split search balanced total videos, not each class: bird had 15 training videos and 24 validation videos. Replaced by a seeded search scoring each class's share.
- Plain int8 quantisation was assumed good enough; it was not (D22).
- The `.gitignore` rule `data/` also matched `web/src/data/`, which would have left the site unbuildable from a clean clone. Found by running the CI steps on a clean copy of the non-ignored files; the folder was renamed to `web/src/content/`.
- Python wrote `NaN` into an evaluation JSON (precision undefined for a model that predicted no birds); the Vite build rejected it. All result writers now go through `metrics.dumps_strict`, which writes `null` instead.
- Dark-mode text on the bright split colours failed contrast (about 1.4 to 2:1); caught by the contrast script and fixed with a separate dark text token.
- A mistyped shell chain once ran `cmake` in the repository root instead of in the scratch copy; the stray `build/` folder was removed.
- Headless Chrome's virtual time made the self-test's inference timing read 0.0 ms; no timing from that run is reported.

## D29. Evaluation reporting choices
Bootstrap intervals use 2000 replicates, seed 0, resampling whole videos. They are labelled optimistic because videos from one scene are not independent. The out-of-domain test set was not built (HANDOFF did not include it); every result is in-domain.


## D30. Redesign: Option A, Datasheet (branch `redesign-a`)
Restyled the site and the README figures to a datasheet look (white page, navy ink, grid-paper panels, fine line drawings, one yellow highlight), replaced all home-page text with `docs/site-copy.md`, and added fine-line illustrations. The model, data, evaluation, firmware logic and every number are unchanged. The site is now one home page (hero, about, pipeline, split, board anatomy, live demo, lessons, results) plus six lesson pages and the glossary, with hash routes. Section links (`#/learn`, `#/demo`, `#/lessons`, `#/results`) scroll the home page; the old routes (`#/memory`, `#/states`, `#/failures`, `#/glossary`) still work. The earlier Board, Memory, State machine and Failure gallery pages became parts of lessons 4 to 6; the board explainer became the numbered anatomy figure from the copy. This replaces the Pastel Paper style (D19, `docs/illustration-style.md`).

## D31. Copy: generated, checked, one edit, one flag
`web/src/content/copy.ts` is generated from `docs/site-copy.md` by `scripts/make_site_copy.py`, so no wording is retyped. `scripts/check_site_copy.py` found all 111 pieces of copy in both `copy.ts` and the built JavaScript.
- **Edit made to the copy:** "a larger model made by someone else" became "a model made by someone else" in the General detector line. The file sizes do not support "larger": the detector is 3,659,407 bytes (3,573.6 KB), this project's model is 3,182.6 KB as int8 and 5,950.5 KB as float32.
- **Number check:** the copy's one number, drone recall 0.465, matches `results/eval_torch.json` (0.4646 rounds to 0.465). The site fills it from that file, and the generator fails if they ever differ.
- **Flag for the owner, left as written:** the About copy says the model "is sized for STM32-class chips". Nothing measured here supports or contradicts that (no run on a board; the int8 model is 3.2 MB and the activation lower bound is 441 KB, against many different STM32 parts). It is your wording, so I kept it, but `CLAUDE.md` says to make no claims about the board. See `docs/todo.md`.

## D32. Words that are not from the copy file
`docs/site-copy.md` covers the home page and the lesson titles and blurbs, not lesson bodies. Lesson page text, tool labels (sliders, tables, buttons), status messages and the glossary reuse the earlier site's text, restyled, plus a few plain sentences I wrote around the interactive tools. The UI strings "Start webcam", "Stop", "or upload an image:", "Theme: ...", "Home", "Previous", "Next" and "Glossary and sources" are carried over from the earlier site. The owner should read the lesson pages (`web/src/pages/Lesson.tsx` and the components it uses).

## D33. Illustrations
All drawings are React components in `web/src/illustrations/`, each under 6 KB, stroke `currentColor`, original, with a battery pack where the mock-up had a solar panel. Labels inside drawings use a per-drawing size (CSS variables) that is larger on phones so they stay readable when the drawing shrinks. Known limit: the split diagram's legend is about 12 px on a 375 px phone and other in-drawing labels are 12 to 14 px; all HTML text is at least 12 px (checked with a script on lesson 6 at 375 px).

## D34. Contrast and accessibility checks
- Site tokens: `scripts/check_contrast.py` checked 30 pairs across light, system dark and toggle dark: 0 failures, lowest ratio 7.14 (`results/site_contrast.json`).
- README figures: `scripts/make_figures.py` checked 44 text and background pairs: 0 failures, lowest ratio 7.14 (`results/contrast_check.json`).
- Playwright (system Chrome, `playwright-core` run from outside the repo): home and lesson 4 at 1280 and 375 px, light and dark: no horizontal scroll, no console errors. Keyboard focus on a board part highlights its table row. The in-browser self-test (`?selftest=1`) still loads the runtime and the detector. Screenshots were looked at and not committed.
- Yellow is only a fill; the only text on it is the dark ink.

## D35. Fonts, size and housekeeping
- IBM Plex Sans and Mono are self-hosted (`@fontsource`, latin subset, SIL OFL 1.1; licence texts in `web/public/licenses/`, listed in `NOTICE` and `docs/sources.md`). The font files total 139 kB (woff2, decimal); the first-load script is 354.7 kB and the CSS 13.3 kB.
- The reference mock-up `web/design/option-a-reference.html` stays local and is excluded from git (it contains a solar-panel drawing and a Google Fonts link). `scripts/preflight.sh` now also checks that no design-reference file or template marker is in `web/dist`, and that "solar" and "logo" appear nowhere in the README, site source, figures or build.
- The README's site screenshot showed the old design, so it was removed (and `docs/img/site-overview.png` deleted). A new one is not committed, per the rule not to commit screenshots; add one after you approve the look.
- The README figures were redrawn in this style (`pipeline`, `split-by-scene`, `board-data-path`, `results`); the firmware state diagram stays Mermaid.
