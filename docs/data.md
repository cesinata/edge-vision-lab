# Data

Status: **no dataset chosen yet.** Nothing has been downloaded. No raw data is committed. Licences below were read from the pages named, on 2026-11-05, and must be re-read before use.

The task needs three classes: bird, drone, neither (background). None of the candidates below supplies a ready-made "neither" class, so that needs a separate decision.

## Candidate 1: Drone vs Bird, YOLO-format segmented dataset (Mendeley Data)
- Page: https://data.mendeley.com/datasets/6ghdz52pd7/5 (DOI 10.17632/6ghdz52pd7)
- Licence stated on the page: **CC BY 4.0** (attribution required).
- 20,925 images, 640x640 JPEG, taken from video frames then segmented and augmented. Authors: Aditya Srivastav, Shishir Kumar Shandilya, Agni Datta, Kyrylo Yemets, Atulya Nagar (VIT Bhopal University).
- Format follows the YOLOv7 PyTorch specification, so labels are probably bounding boxes. Crops would have to be cut from them. The page does not say this outright. Not verified.
- No background class. Augmentation means near-duplicate images may land in different splits unless split by source video, which the page does not expose. This is a leakage risk to check.
- Probably the same underlying material as the Kaggle "StealthKnight" set named in the old README (unverified).

## Candidate 2: Open Images V7 (bird images; background from other classes)
- Page: https://storage.googleapis.com/openimages/web/factsfigures_v7.html
- Licence stated: annotations CC BY 4.0 (Google LLC); **images listed as CC BY 2.0**. Each image has its own author, so attribution is per image.
- Large and well-documented. Gives birds and plenty of sky/cloud/aircraft/background images for "neither". The page I read did not list per-class counts, and I did not confirm a drone-like class exists. Not verified. Drones would need another source, so this does not solve the task alone.
- Needs a download script that fetches only chosen classes, with a per-image attribution file.

## Candidate 3: Roboflow Universe "Drones-Vs-Birds-Classification"
- Page: https://universe.roboflow.com/drones-hsv8d/drones-vs-birds-classification
- Search listing showed CC BY 4.0 for several Roboflow drone/bird projects; this page returned 403 to me, so **the licence and contents of this specific project are unverified**. Roboflow projects often reuse images from other sources, so upstream rights also need checking.
- Closest to a classification-shaped dataset, but the least documented.

## Not recommended without more checking
- Kaggle "StealthKnight Bird vs Drone" (named in the old README): licence not verified.
- CUB-200-2011: birds only, and a Caltech-hosted mirror states non-commercial research and education use only. Wrong shape and likely incompatible with a public portfolio.

## What I suggest
Candidate 1 for birds and drones (clear CC BY 4.0), plus Open Images (Candidate 2) for the "neither" class, with a download script and an attribution file. Check first that Candidate 1's labels allow clean crops and that a split by source avoids leakage. This is a suggestion; the choice is the owner's.

## Chosen dataset and exact licence text
To be filled in after the owner chooses.
