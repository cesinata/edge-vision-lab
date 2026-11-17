# Lessons learned

General lessons from building this repository, each tied to something that actually happened here. For the numbers behind them see `README.md`, `docs/error-analysis.md` and `docs/decisions.md`.

## Data
- **Split by scene, not by frame or by clip.** Neighbouring video frames are near-copies, and many clips were filmed from the same spot. A perceptual hash grouped the videos into scenes; whole scenes went to train, validation or test. Say what the grouping misses: it finds near-identical scenes, not every shared place or time of day.
- **Look at how the classes are distributed over scenes.** Drones came from a handful of places and birds from many. That makes "which place is this?" a shortcut the model can take, and it makes the drone test result depend on two scenes.
- **Check where data came from, not only its licence.** One candidate dataset carried a permissive licence but was built from a stock footage site whose terms prohibit machine-learning use, so it was dropped. Another is used with a licence question still open, so nothing derived from it is published.
- **Compare decoded labels with something independent.** A small third-party decoder for a proprietary label format misread frames with two objects as empty. Comparing the number of labels with the number of video frames exposed it. Make a parser fail loudly on input it does not recognise instead of guessing.

## Evaluation
- **A small test set needs honest intervals, and an honest caveat on the intervals.** Resampling by video is better than by frame, but videos from one scene are still not independent, so the intervals stay optimistic. Write that next to them.
- **Choose thresholds and settings on validation, then look at the test set once.** The int8 model's validation-chosen alert threshold did not deliver its validation precision on the test split. That is a result, not a bug to hide.
- **An easy class can flatter an average.** Background crops were almost all plain sky and nearly never wrong, which lifts the "neither" class without showing that anything was learned.
- **Associations are not causes.** Error rate rose with brightness and fell with texture, but both also track scene and distance. Report the association and name the confound.
- **Look at the failures by eye, locally, and write down what you saw.** Several missed drones were clearly visible on plain sky, which a size or distance table alone would not have shown.

## Quantisation
- **Do not assume int8 is free.** Quantising every convolution of a MobileNetV3-style network, with three calibration methods, lost most of the accuracy. Leaving the depthwise and squeeze-and-excite convolutions in float32 recovered most of it, at the cost of a smaller size reduction. Keep a record of every setting tried, including the failures.
- **Measure all three things.** Size, accuracy and speed moved differently: the model got smaller and a bit faster, and its bird alert got clearly worse.

## Device logic
- **Keep the hardware at the edge and test the middle.** The state machine takes timestamps, scores, battery levels, watchdog ticks and faults as input, with no clock or random numbers inside, so a laptop can replay a stall or a fault and check the result exactly.
- **Break the code on purpose to see whether the tests notice.** Changing one comparison, or disabling the watchdog, made tests fail; that is what makes passing meaningful. Then say what the tests do not cover (real timing, interrupts, sensor noise, clock wrap-around).
- **Do not let one table drift into three.** The transition table is the single source for the tests, the Mermaid diagram and the website's diagram.

## Process and tooling
- **Run the CI steps on a clean copy of the non-ignored files before pushing.** It found a `.gitignore` rule that silently excluded a source folder, and a `NaN` in a JSON file that only broke the build once real results existed.
- **Never write `NaN` into JSON.** An undefined metric is `null`, not an invalid literal and not a made-up zero.
- **Script the checks you would otherwise do by eye.** A contrast check on every text and background pair caught light text on bright pastel dots in dark mode.
- **Headless browsers can break timing.** Virtual time made a timing read 0.0 ms. Use headless runs to check that something works, and take timings from a real run.
- **Generate numbers into documents from the results files.** The README tables, findings and case study are written by scripts from the JSON, so a number in prose cannot drift from the run that produced it.
