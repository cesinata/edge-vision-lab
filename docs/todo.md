# To do

## Needs the owner (blocks publishing)
- [ ] Get the data licence confirmed in writing by the dataset authors (contact in the dataset README). The dataset repository's `LICENSE` is CC0 1.0 Universal and the Zenodo record says "Other (Open)". Until then nothing derived from the videos is published: no frames, crops, sample images, `train/splits/split_seed0.json`, weights, ONNX or TFLite files.
- [ ] After confirmation: run `bash scripts/publish_model.sh --i-have-confirmed-the-licence`, set `MODEL_PUBLISHED = true` in `web/src/config.ts`, rebuild, and decide whether to commit the split file.
- [ ] Approve any sample images for the website (none until approved).
- [ ] Decide whether to rewrite git history to remove an old name from early commits (not done; no force pushes without a decision).
- [ ] Optional: change `LICENSE` so it names you instead of "the edge-vision-lab authors" (decisions D27).
- [ ] Optional: stop using the university email for future commits (`git config user.email`); it is in existing history.
- [ ] Rename or archive the older `sentinel-vision` repository with a pointer README (owner does this).

## Check by eye after the redesign
- [ ] Decide on the About copy "is sized for STM32-class chips": nothing measured supports it (D31). Keep, soften or remove.
- [ ] Read the lesson pages: their body text is not from `docs/site-copy.md` (D32).
- [ ] Look at the live site on a real phone and in both colour themes; add a README screenshot if you like the look.
- [ ] The split diagram legend is about 12 px on a 375 px phone (D33).

## Not done in the unattended run
- [ ] Out-of-domain test set from Open Images (no download script, no attribution CSV, no out-of-domain numbers). All reported results are in-domain.
- [ ] Run the CI and Pages workflows. They were only parsed as YAML. The CPU-only PyTorch index and version pin used in `ci.yml` were not tested.
- [ ] Manual browser tests: webcam demo, image upload, and the project-model path. See the list in the final summary.
- [ ] A site screenshot or live link in the README (needs a Pages deploy).

## Unverified (do not state on the site or README until checked)
- [ ] Licence terms of the torchvision ImageNet weights for MobileNetV3-Small, used as the training start (downloaded at run time, never redistributed).
- [ ] The YOLOX release page states no licence for the weights separately from the repository's Apache-2.0 licence; confirm that it covers them.
- [ ] Pexels' terms (the wording came from search summaries; the pages returned 403). Only matters if the rejected Pexels-derived dataset is reconsidered.
- [ ] Vendor-published figures from `CLAUDE.md` (ST-YOLOX numbers): the original document was not read, so none are used.

## Ideas, only if wanted
- [ ] Try a larger scene-diverse training set so the model cannot lean on the place (the main limit found, see README).
- [ ] Quantisation-aware training, or leaving the squeeze-and-excite and hard-swish layers in float, if the int8 gap matters.
- [ ] A small object detector, and an energy-budget calculator for a duty-cycled camera (all assumptions labelled estimated).
