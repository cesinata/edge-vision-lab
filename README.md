# edge-vision-lab

Status: work in progress. Phase 1 of 8 (repo consolidation). There are no results yet, and this README says so rather than quoting numbers from earlier versions of the project.

## What this is

A small image classifier for three classes: **bird**, **drone**, and **neither** (background). The aim is to train it, quantise it to int8, measure it, test the state/power logic of a microcontroller camera node on a laptop, and explain the pipeline on an interactive website. It is written for people hiring in ML and edge AI, and for learners new to edge AI.

This is **image classification on crops**, not object detection. The model sees one cropped image and says which class it is. It does not find objects in a scene.

## Results

None yet. Every number that appears here later will be labelled `measured (host CPU)`, `measured (browser)`, `estimated (tool)`, `simulated`, `vendor-published` or `not measured on hardware`, with the command that reproduces it.

## What is in the repo now

| Path | State |
|---|---|
| `firmware/firmware_sim.cpp` | Legacy console simulation. Motion and model output are random numbers and the loop never exits. The watchdog does nothing and `STATE_RECOVERY` is never entered. Builds with CMake. To be rewritten in Phase 5 to run on scripted input traces, with unit tests. |
| `export/baseline_quantize.py` | Quantises a stock ImageNet MobileNetV3Small to int8. It is **not** a trained bird/drone model and has no fine-tuning. Needs your own calibration images. |
| `docs/decisions.md`, `docs/data.md`, `docs/todo.md` | Decisions, dataset candidates and licences, open items. |

Build the firmware simulation (it runs until you stop it):

```
cmake -S firmware -B build && cmake --build build && ./build/firmware_sim
```

## What it does not do

- It has not been run on any STM32 or ESP32 board. No board is available. Nothing here claims on-device latency, frame rate, power draw or NPU performance. Those are `not measured on hardware`.
- It does not detect objects in a scene.
- Earlier versions of this README quoted a model size reduction ("29.34 KB to 3.02 KB"). Those figures described files that are no longer in the repo and have been removed.

## Data and licences

No dataset has been chosen yet. Candidates and their licence status are in `docs/data.md`. No raw datasets are committed.

## AI disclosure

AI assistance (Claude) was used to draft and review code and text in this repo. I ran the experiments, and every reported number will come from a run in this repo.

## History

This repo started as `Solar-Guardian-Edge-AI`. The original commits are kept. Some earlier files, including two model files and two test images of unknown origin, were removed from the working tree in Phase 1 but remain in git history.
