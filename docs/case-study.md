# Case study: a small classifier, measured honestly

For readers who want the story in one page. Every number is `measured (host CPU)` unless it says otherwise, comes from a file in `results/` or `bench/`, and is reproduced by the commands in the README.

## The problem
A camera node on a solar-powered device should react to birds but not to drones or airplanes, using a tiny model that could one day run on a microcontroller. I had no board, so the goal was to do everything that can be done honestly on a laptop and to say clearly what cannot: train a classifier, quantise it, measure it, test the node's power logic, and explain the pipeline on a website.

## What I built
- A three-class classifier (bird, drone, neither) on small crops cut from labelled video frames of a public dataset (visible-light videos only; 235 videos after exclusions). MobileNetV3-Small, fine-tuned from ImageNet weights on a laptop CPU in 4492 s.
- A split by scene, not by frame or clip, because 114 drone clips turned out to come from only 8 places.
- An evaluation on the test split with intervals resampled by video, a per-subtype breakdown (background, airplane, helicopter), a threshold for bird alerts, and an error analysis.
- ONNX export and static int8 quantisation, with size, accuracy and host-CPU latency measured before and after.
- C++ state and power logic (idle, capture, infer, alert, low-power, recovery) with a working watchdog, replayed from scripted traces and unit-tested: 348 checks, 96.43% line coverage.
- A website with a webcam demo of a third-party detector, a board explainer, a memory-budget calculator and a state-machine viewer.

## What the numbers say
- Test macro F1 0.700 (95% interval 0.62 to 0.77). Recall is 0.92 for neither, 0.77 for bird and only 0.46 for drone; drones that are far away are mostly missed.
- A bird alert tuned for high precision (0.98) keeps only 0.35 of the birds.
- Quantising every convolution to int8 destroyed the model (best of 12 settings: validation macro F1 0.53 against 0.77). Keeping the depthwise and squeeze-and-excite layers in float32 recovered it. That partial int8 model is 1.87 times smaller (3183 against 5951 KB), about 9% faster on this CPU, and has a worse bird alert (average precision 0.63 against 0.81).

## What I would not claim
Nothing was run on a board, so there is no on-device speed, power or memory result (`not measured on hardware`). The test set is small and the drone test clips come from two scenes, so these results do not show how the model behaves in a new place. The training curve fits a model that partly learns the scene; I could not rule that out. The project's model and all frames are unpublished until the dataset authors confirm the data licence.

## What I would do next
Train on footage from many more scenes, add the planned out-of-domain test set, try quantisation-aware training, and, with a board, measure the real arena size and latency.
