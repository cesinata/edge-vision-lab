# Sources

Each entry says what was checked and what was not. "Verified" means I read the named page or file on the date given. Nothing here is a legal opinion.

## Dataset
- Svanstrom F., Alonso-Fernandez F., Englund C. "A dataset for multi-sensor drone detection". Data in Brief 39 (2021) 107521. DOI 10.1016/j.dib.2021.107521. Open access (CC BY for the article). Read 2026-11-06 via PubMed Central.
- Data: Zenodo record 5500576, v1.0.0, file `Drone-detection-dataset-v1.0.0.zip`, 311,348,350 bytes, MD5 `5d9b891a87857b3d9ee8872e8a1f0f0f` (matches the download script's check). Zenodo licence field: "Other (Open)".
- Repository: github.com/DroneDetectionThesis/Drone-detection-dataset. Its `LICENSE` file (read in the downloaded snapshot) is CC0 1.0 Universal; the README says "Free to download, use and edit."
- **Open:** written confirmation from the authors of the data licence has been requested and not received. See `NOTICE` and `docs/todo.md`.
- Details of what the files contain and how they were checked: `docs/data.md`.

## Model and training
- Howard A. et al. "Searching for MobileNetV3". ICCV 2019. Cited as the architecture. Not re-read for this repo.
- torchvision (code): BSD 3-Clause, "Copyright (c) Soumith Chintala 2016". Verified 2026-11-17 from the repository `LICENSE` file.
- torchvision ImageNet weights for MobileNetV3-Small (`MobileNet_V3_Small_Weights.IMAGENET1K_V1`, 2,542,856 parameters including the 1000-class head): downloaded at training time from download.pytorch.org, never stored in this repository. **Licence terms for these weights not verified.** The repository `LICENSE` file says nothing about weights.

## Website demo (third-party model, not trained by this project)
- YOLOX-Nano, ONNX file from Megvii-BaseDetection/YOLOX release 0.1.1rc0 (published 2021-08-18), 3,659,407 bytes, SHA-256 `c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d`. Repository licence: Apache License 2.0, "Copyright (c) 2021-2022 Megvii Inc." Verified 2026-11-17 from the repository `LICENSE` file and the release asset list (GitHub API). The release page states no separate licence for the weights; I treat the repository licence as applying and have not confirmed that.
- Ge Z. et al. "YOLOX: Exceeding YOLO Series in 2021" (2021). Cited, not re-read.
- COCO class names (80): from `yolox/data/datasets/coco_classes.py` in the same repository. COCO has "bird" and "airplane" classes and no "drone" class.
- Input and output format (416 x 416, BGR, 0..255, letterbox pad 114, raw output 1 x 3549 x 85 needing grid decode) were checked by running the model with ONNX Runtime and comparing decoded boxes with labelled boxes on local frames; see `web/src/lib/yolox.test.ts` for the decode test.
- It is fetched at build time by `scripts/fetch_web_assets.sh` with a size and SHA-256 check. It is not committed.
- Why not Ultralytics YOLO: excluded by the project's licence requirement (Apache-2.0 or MIT only).

## Runtime and tooling
- ONNX Runtime and ONNX Runtime Web: MIT, "Copyright (c) Microsoft Corporation". Verified 2026-11-17 from the repository `LICENSE`; package `license` fields also read as MIT for `onnxruntime-web`, `react`, `vite` and `vitest`; `typescript` reads Apache-2.0.
- PyTorch, torchvision, onnx, onnxruntime, numpy, scipy, OpenCV, Pillow, ImageHash: installed from PyPI at the versions in `requirements.txt`. Licences not individually re-verified.
- `mcos-decoder` 0.1.0 (MIT per its package metadata; 265 lines of pure Python, read in full). Only its stream walker is used, see `train/mat_labels.py`.

## Fonts (website)
- IBM Plex Sans and IBM Plex Mono, version 5.3.0 of the `@fontsource/ibm-plex-sans` and `@fontsource/ibm-plex-mono` packages, self-hosted (latin subset, weights 400 to 700 and 400 to 600). Licence: SIL Open Font Licence 1.1, "Copyright 2019 IBM Corp." Verified 2026-11-18 from the `LICENSE` file and `license` field in each package. The licence texts are shipped with the site under `licenses/` (copied from the packages into `web/public/licenses/`). No font service is contacted at run time.

## Planned, not used yet
- Open Images V7 as an out-of-domain test set: annotations CC BY 4.0 (Google LLC); images "listed as having a CC BY 2.0 license" with per-image authors (https://storage.googleapis.com/openimages/web/factsfigures_v7.html, read 2026-11-06). Flickr's own terms were not read. Not downloaded.

## Rejected
- "Segmented Dataset Based on YOLOv7 for Drone vs. Bird Identification" (Mendeley Data, DOI 10.17632/6ghdz52pd7.5, CC BY 4.0): built from Pexels footage. Pexels' help centre says its terms prohibit data mining and automated collection, explicitly including machine learning. Pexels pages returned HTTP 403 to my tools, so the wording comes from search summaries and is unverified; the owner decided not to rest a public model on it.
- Drone-vs-Bird Challenge videos: described as available for non-commercial purposes (from a paper abstract); no formal licence found.
- A Zagreb "Visual drone detection dataset" (Zenodo 15632958, CC BY 4.0): the page does not say where the images came from.

## Vendor-published figures
None are used. `CLAUDE.md` lists one set of vendor figures that may be used after re-verification against the original document; that document was not read, so none appear in this repository.
