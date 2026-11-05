# To do

## Needs the owner
- [ ] Choose the dataset (`docs/data.md`).
- [ ] Decide whether a public-safe `CLAUDE.md` is committed.
- [ ] Decide whether to rewrite git history to remove an old name from early commits (not done; no force pushes without a decision).
- [ ] Confirm the code licence (MIT proposed).
- [ ] Rename or archive `sentinel-vision` with a pointer README (owner does this).
- [ ] Optional: remove the university email from future commits (`git config user.email`); it is in existing history.

## Unverified (do not state on the site or README until checked)
- [ ] Licence of the Keras MobileNetV3 ImageNet weights. Weights are fetched from `https://storage.googleapis.com/tensorflow/keras-applications/mobilenet_v3/`; no licence statement found in the Keras source file or by search. Check the TensorFlow/Keras documentation and the original model release.
- [ ] Whether Keras MobileNetV3 expects 0-255 input (it rescales internally) rather than 0-1. `export/baseline_quantize.py` feeds 0-1. Check the Keras docs.
- [ ] Contents of the removed baseline `.tflite` (input shape, classes). Not needed unless it is rebuilt.
- [ ] sentinel-vision README figures ("0.5% per day", "up to 57%", "143M parameters"): not used here; do not copy.

## Later phases
- [ ] Pin `requirements.txt` from a working Python 3.11/3.12 environment (Phase 2).
- [ ] Rewrite firmware onto scripted traces, add Catch2 or GoogleTest tests (Phase 5).
