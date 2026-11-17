# Data

Status: **dataset chosen, pending written confirmation of the data licence from the authors** (owner decision 2026-11-06). The Mendeley / Pexels dataset was rejected (see below). The Zenodo file was downloaded for local inspection into `data/` (gitignored). No raw data is committed, and **nothing derived from the videos (frames, crops, sample images, weights, plots showing frames) is to be published until the licence is confirmed.** Facts below were read on 2026-11-05 and 2026-11-06 from the pages named. Anything marked "not verified" has not been read at the source.

## Rejected (2026-11-06): Drone vs Bird (Mendeley Data)

**Reason:** the images are frames from Pexels footage, and Pexels' help centre states that its terms prohibit data mining and automated collection, explicitly including machine learning. The owner does not want a public model resting on that. The dataset's own CC BY 4.0 licence does not change Pexels' terms. Nothing from this dataset was downloaded (only the 10 KB spreadsheet of source links was read, to see provenance). The facts below are kept as a record of what was checked.

- Page: https://data.mendeley.com/datasets/6ghdz52pd7/5 . DOI 10.17632/6ghdz52pd7.5, version 5, published 13 April 2023.
- Title on version 5: "Segmented Dataset Based on YOLOv7 for Drone vs. Bird Identification for Deep and Machine Learning Algorithms".
- Authors: Aditya Srivastav, Shishir Kumar Shandilya, Agni Datta, Kyrylo Yemets, Atulya Nagar (VIT Bhopal University).
- **Licence, from the dataset's own page: "CC BY 4.0".** The page does not reproduce the licence text. Attribution is required.
- Related article: Shandilya, Srivastav, Yemets, Datta, Nagar, "YOLO-based Segmented Dataset for Drone vs. Bird Detection for Deep and Machine Learning Algorithms", Data in Brief, 2023 (ScienceDirect PII S2352340923004742; the page I read gives no DOI, volume or article number, so none is recorded here). Accepted version is listed as CC BY 4.0.
- Suggested citation: the dataset page does not give one. Until the download is inspected, cite as: Srivastav, A., Shandilya, S.K., Datta, A., Yemets, K., Nagar, A. (2023). Segmented Dataset Based on YOLOv7 for Drone vs. Bird Identification for Deep and Machine Learning Algorithms, v5. Mendeley Data. doi:10.17632/6ghdz52pd7.5 . (Assembled from the page's metadata, not copied from a citation line.)
- Files (from Mendeley's public file listing for version 5):
  - `Dataset.zip`, 1,128,956,760 bytes, SHA-256 `5bf5b257071176713664659db6e7e31ebc4c331d94e0c3f369461c1e7ecac51c` (as published by Mendeley; to be checked after download).
  - `Raw DataSet links .xlsx`, 10,550 bytes, SHA-256 `5bdbf3f7f16bd6268a61c031feef70d094ef9e1070fa8753fa6ffb23b1e37c62`. Downloaded and read; it lists the source clips, see below.
- Described as: 20,925 JPEG images at 640 x 640, folders `train`, `valid`, `test`, each with `images` and `labels`, "YOLOv7 PyTorch specification". Images are "segmented and augmented with a range of circumstances", so **augmentation is baked in** (types and counts not stated).
- **Class IDs and label line format: not stated on the page. To be recorded from the real download only.** Likewise per-split counts and filename scheme.

### Source clips (from the dataset's own "Raw DataSet links" spreadsheet)
The spreadsheet has 44 text cells: the headings BIRD and DRONE, then 23 bird entries and 19 drone entries (counted by me from the sheet's text; each is a pexels.com clip link or page title, and I did not match entries to images). So the 20,925 images come from **at most 42 source clips** (fewer if an entry repeats a clip), and many images from one clip will look nearly the same. There is no mapping from image file to clip on the page. Consequences:
- A random split by image would leak badly. The provided `train`/`valid`/`test` folders must not be reused as the evaluation split.
- Splitting by cluster of near-identical frames (see `docs/decisions.md`) is the only available proxy for splitting by clip, and with 19 to 23 clips per class the test set will be small in clips and its metrics noisy. The README reports cluster counts and this limit.

### Pexels terms (third-party source material)
The images are frames from Pexels footage. Pexels terms are separate from the dataset's CC BY 4.0 licence.
**Status: I could not read the Pexels pages (they returned HTTP 403 to my tool). The points below come from search-result summaries of pexels.com and help.pexels.com pages, not from reading them, and are not verified.** The owner should read them:
- https://www.pexels.com/license/
- https://www.pexels.com/terms-of-service/
- https://help.pexels.com/hc/en-us/articles/360042332714-What-are-the-rules-for-using-Pexels-photos-or-videos

What the summaries said:
- Photos and videos are free to use, attribution not required, and may be edited.
- Selling unmodified copies, and re-uploading to other stock or wallpaper sites, is not allowed.
- Bulk, large-scale or systematic copying of content is prohibited without permission.
- The Terms prohibit scraping and automated data collection for unauthorised purposes, explicitly including machine learning. Help text says the API may not be used to collect content at scale to train, fine-tune or evaluate models without permission.
- It was not clear whether a third party redistributing frames as a dataset is covered.

What this means for the repo (a risk, not a legal conclusion):
- Nothing from Pexels or this dataset is committed. The download script fetches from Mendeley.
- No sample images on the website, and no failure-gallery images, until the owner approves. The "licensed sample" idea in the project rules is not available from this dataset unless Pexels terms are confirmed to allow it.
- Decision: rejected, see the top of this section.

## "Neither" class (plan from the rejected design; to be revisited with the new dataset)
- **In-domain:** background crops taken from the same frames as the bird and drone images (train and main test). How background crops are cut depends on the label format and is decided after inspecting the download.
- **Out-of-domain test only:** an Open Images V7 subset of images with none of the labels Bird, Drone, Airplane, Helicopter, Kite. Open Images is never used for training.
  - Page: https://storage.googleapis.com/openimages/web/factsfigures_v7.html
  - Licence stated there: annotations CC BY 4.0 (Google LLC); **images listed as CC BY 2.0**, with per-image authors.
  - A download script will fetch the chosen images and write `attribution.csv` (image id, author, licence, source URL) from the Open Images metadata. The script and CSV are committed; images are not.
  - Whether "Drone" exists as a label in Open Images was not verified. The exclusion list will use the class names actually present in the downloaded class-descriptions file.
  - The exact Open Images file names and fields are not verified yet.

## Reporting
In-domain and out-of-domain metrics are reported separately, never pooled.

## Chosen: Svanstrom et al. drone detection dataset, visible-light videos (verified from the real files, 2026-11-06)

Reproduce: `python train/download_data.py`, then `python train/build_index.py`, then `python train/make_split.py`. Counts below are from those scripts.

### What was downloaded
- Zenodo record 5500576, file `DroneDetectionThesis/Drone-detection-dataset-v1.0.0.zip`, 311,348,350 bytes. MD5 `5d9b891a87857b3d9ee8872e8a1f0f0f` matches Zenodo's published value (checked by the download script).
- Contents (counted): 652 `.mp4` (650 dataset videos plus 2 demo clips), 650 `.mat` label files, 90 `.wav`, `README.md`, `LICENSE`, `Data/Video_dataset_description.xlsx`, `Data/Create_a_dataset_from_videos_and_labels.m`. 357 MB extracted. The zip is a GitHub snapshot (directory `DroneDetectionThesis-Drone-detection-dataset-e7a6eaf`), which explains why it is small: the videos are short and compressed. The earlier "311 MB looks small for 650 videos" doubt is resolved.
- Folders: `Data/Video_V` (visible, 285 videos), `Data/Video_IR` (infrared, 365), `Data/Audio`.

### Licence, now partly resolved
- The `LICENSE` file in the snapshot is the CC0 1.0 Universal legal code (I read its header; I did not diff it against the official text). The README says "Free to download, use and edit."
- The Zenodo record still says "Other (Open)". The paper gives no data licence.
- **Still pending: written confirmation from the authors** (contact in the README). Until then, nothing derived is published.

### Classes, counts and names (visible videos)
- Names: `V_<CLASS>_<NNN>.mp4` and `V_<CLASS>_<NNN>_LABELS.mat`, `<CLASS>` one of AIRPLANE, BIRD, DRONE, HELICOPTER, `<NNN>` a 3-digit number. The video number is the video ID. Distance bin and drone type are not in the file name; they are in the spreadsheet (sheet `Blad1`, columns SENSOR, CLASS, NUMBER, DISTANCE BIN, INTER BIN NUMBER, DRONE TYPE / INTERNET SOURCE). Every spreadsheet row for a visible video matched a file.
- Counts per class match the paper: airplane 59, bird 51, drone 114, helicopter 61 (285).
- Every visible video is 640 x 512 at 30.0 fps (read with OpenCV). The paper's other figure, 1280 x 720, does not apply to these files.

### The 49 YouTube clips
- The spreadsheet's source column holds `https://www.youtube.com/user/SK678387` for exactly 49 visible videos: **11 airplane (038-048) and 38 helicopter (019-056)**. No bird, drone or infrared video carries that mark. These 49 are excluded.
- Remaining airplane videos: 59 minus 11 YouTube = 48 (001-037, 049-059). `V_AIRPLANE_002` is also excluded because its label file does not decode (below), leaving **47**: 001, 003-037, 049-059.
- Remaining helicopter videos: **23**: 001-018, 057-061.

### Labels: what works and what does not
- `scipy.io.loadmat` opens the `.mat` files but returns the groundTruth object as an opaque blob (`MatlabOpaque`); the boxes are not accessible. The paper's statement that scipy can load them does not hold for the boxes (measured on `V_BIRD_001_LABELS.mat`).
- The third-party `mcos-decoder` 0.1.0 (MIT, 265 lines, pure Python; I read its source) decodes by byte size and is wrong for these files. On the 285 visible videos its label count differed from the video's frame count by more than 5 in 11 videos (10 bird, 1 helicopter). Cause, found by inspecting the file structure: it treats a 112-byte cell as "target absent", but that size is a 2 x 4 box array (two birds in the frame), and a 1 x 4 box array has the same size as a 1 x 30 character array. `V_BIRD_005` decodes to one label instead of 302.
- `train/mat_labels.py` uses only the decoder's stream walker and reads each array's class and dimensions. Each frame is a group of five arrays: a timestamp and four label slots, one per class in alphabetical order. The video's class slot holds an N x 4 array of (x, y, w, h) (column-major) or an empty array.
- Result on all 285 visible videos: 284 decode; in all 284 the number of label groups equals the number of decodable frames exactly; 0 boxes lie outside the frame. `V_AIRPLANE_002` has one frame with an unexpected element in its label slot, so the extractor refuses it (excluded, not guessed).
- Frame alignment (label group k = video frame k) was checked by drawing the boxes on 10 frames from 5 videos (bird single, bird flock, drone) and viewing them locally; all boxes sat on the object. That is a small visual check, not a proof for every video. The overlay images were not saved to the repo.
- Boxes: one per object. Birds appear in flocks (`V_BIRD_005` has 4 to 7 boxes in every frame). Totals for the 235 kept videos: bird 21,775 boxes in 16,118 frames; drone 36,316 in 35,496; airplane 14,809 in 14,808; helicopter 7,095 in 7,096.
- Per-video median box size (pixels): bird width 27 (range 22 to 37), height 26 (21 to 37); drone width 33 (17 to 75), height 26 (16 to 49). Objects are small in a 640 x 512 frame.

### Target-absent frames: not enough for a "neither" class
Frames with no target, among the 235 kept videos: bird 81 frames (of 16,118; in `V_BIRD_003`, `V_BIRD_004`, `V_BIRD_006`), helicopter 1, airplane 0, drone 0. That is far too few to form a class. So **"neither" cannot come from target-absent frames.** Default chosen (see `docs/decisions.md` D13): background crops cut from regions of the frames that do not overlap any box, plus airplane and helicopter crops as a separate hard-negative slice, plus Open Images as out-of-domain test only.

### Scene duplicates: the main limit of this dataset
- Whole-frame perceptual hashes (64-bit pHash of three frames per video; distance = best match over the 3 x 3 pairs). For **more than half of the 235 videos there is another video whose frame hashes are identical** (median nearest-other-video distance 0 bits): many videos were filmed from the same spot.
- Clustering videos within 6 bits gives **99 scene clusters**. The largest have 47, 28, 13 and 11 videos. Drone: **114 videos in only 8 clusters** (103 in clusters of 5 or more, none single). Bird: 51 videos in 38 clusters (30 are alone). Airplane: 47 videos in 42 clusters. Helicopter: 23 videos in 13 clusters.
- Consequences, to be stated in the README: (1) a split by video would leak backgrounds, so the split is by cluster; (2) drones were filmed in few places and birds in many, so a classifier can partly learn the place instead of the object, and results may not carry to other scenes; (3) the drone test set covers few scenes (below), so its metrics are noisy.
- pHash finds near-identical scenes, not every shared location, time or camera setting. It is a proxy.

### Split (fixed, by scene cluster, seed 0)
`train/splits/split_seed0.json` (video IDs, class, cluster id, split; no frames or hashes). Seeded random search over cluster assignments (20,000 trials), closest to 60/20/20 per class, with at least 2 clusters per class in val and test. Rerunning gives a byte-identical file (checked). Videos per split (clusters in brackets):

| Class | train | val | test |
|---|---|---|---|
| bird | 29 (19) | 10 (9) | 12 (10) |
| drone | 66 (4) | 16 (2) | 32 (2) |
| airplane | 30 (26) | 7 (7) | 10 (9) |
| helicopter | 14 (8) | 5 (2) | 4 (3) |

Cross-split check on the final assignment: video pairs in different splits with hash distance at most 6 bits: 0; at most 8: 1; at most 10: 4; at most 12: 46.

**Limits of this split:** the drone test set is **2 scene clusters** (32 videos), and the helicopter test set is 4 videos. Bootstrap intervals resampled by video understate the uncertainty when videos from one scene are not independent; the true uncertainty for drones is closer to a 2-scene sample than to 32 videos.

## Replacement candidates (researched 2026-11-06, nothing downloaded)

Screening rules from the owner: reject anything built from stock-photo sites or with unclear provenance. For each: who captured it, the dataset licence, the terms of any site the images came from, whether ML use is allowed, size, label format, sequence IDs. "Not stated" means I read the page and it was not there.

### Rank 1: Multi-sensor drone detection dataset (Svanström, Alonso-Fernandez, Englund), visible-light videos only
- Sources read: GitHub README https://github.com/DroneDetectionThesis/Drone-detection-dataset ; Zenodo record https://zenodo.org/records/5500576 ; paper (open access, CC BY) https://pmc.ncbi.nlm.nih.gov/articles/PMC8573135 , Data in Brief 39 (2021) 107521, DOI 10.1016/j.dib.2021.107521 .
- **Captured by:** the authors (Swedish Armed Forces; Halmstad University), in and around Halmstad and Falkenberg, and at Halmstad, Gothenburg City and Malmo airports. Exception: 49 clips (11 airplane, 38 helicopter) come from a YouTube channel described in the paper as non-copyrighted, added because of COVID-19 restrictions. Those are airplane/helicopter only and would be excluded here. No bird or drone clip is listed as external.
- **Classes (video):** Airplane, Bird, Drone, Helicopter. Visible-light videos per class, from the paper's tables: Airplane 59, Bird 51, Drone 114, Helicopter 61 (total 285). Infrared: 365 videos (thermal, 320x256; not useful for a visible-light camera model, so not planned).
- **Licence:** **conflicting, unresolved.** GitHub shows CC0-1.0 and the README says "Free to download, use and edit" (I did not read the LICENSE file itself). The Zenodo record says "Other (Open)" with "No further description". The paper states a CC BY licence for the article only and gives no licence for the data. Before use: read the repo LICENSE file and ask the authors (contact in the README) to confirm the data licence in writing.
- **Site terms:** none apply to author-recorded clips. Zenodo and GitHub terms not read.
- **ML use allowed:** the paper says it is meant for training and evaluating drone detection and that the data "can be used as-is". No licence text restricting ML was found. Not a legal conclusion.
- **Size:** paper: 650 videos (365 IR, 285 visible), 203,328 annotated frames if every frame is extracted (the per-class frame counts are not stated). The Zenodo record's single file is 311.3 MB (`Drone-detection-dataset-v1.0.0.zip`, md5 5d9b891a87857b3d9ee8872e8a1f0f0f), which looks small for 650 videos; what it contains is not stated. Needs checking before download.
- **Labels:** one bounding box per frame in MATLAB Video Labeler `groundTruth` `.mat` files. The README says standard Python loaders cannot read them and points to a third-party package (`mcos-decoder`); the paper says `scipy.io.loadmat` works. These conflict. A frame without the target returns no box, which may give target-absent frames for the "neither" class (not verified).
- **Sequence IDs:** yes, one per video, in the file name (for example `IR_DRONE_001.mp4`; visible files presumably `V_...`, not verified). Distance bin, drone type and an "is from the Internet" flag are in a separate spreadsheet (`Video_dataset_description.xlsx`). A split by video is therefore possible directly, and no clustering is needed for the split (the pHash check still runs).
- **Limits (from the paper):** daylight only, maximum distance 200 m, Swedish conditions, three drone types, bird species not stated. Video resolution is given as 640x512 in one place and as a 1280x720 capture in another; not resolved. Frames in a video are highly correlated, so the number of independent samples is the number of videos (51 bird, 114 drone), which makes test metrics noisy.
- **Fit:** closest match to "bird vs drone vs neither" with clean provenance. Classification on crops cut from the boxes.

### Rank 2 (conditional): "Visual drone detection dataset, not augmented" (Zenodo) for drones, plus Open Images for birds and "neither"
- Record read: https://zenodo.org/records/15632958 . University of Zagreb, Faculty of Transport and Traffic Sciences. CC BY 4.0 (on the page). 141.4 MB. YOLOv11 format.
- **Fails the provenance test as it stands:** the page does not say where the images came from, who captured them, the classes, or how frames were chosen. Not usable until the authors say so. Listed only because it is the one drone-only RGB set found with a clean licence label.
- Birds and "neither" would come from Open Images (see the fallback), which is a different domain from the drone images. Bird and drone would then differ in photographer, camera and background, and a classifier could learn the source instead of the object. This option is weaker than rank 1 even if provenance is confirmed.

### Rank 3 / fallback task: bird vs not-bird, Open Images V7 images with a CC BY licence only
- Pages read: https://storage.googleapis.com/openimages/web/factsfigures_v7.html (licences) and https://storage.googleapis.com/openimages/web/download_v7.html (download and metadata).
- **Captured by:** many Flickr users. Google compiled the set. Licences: annotations CC BY 4.0; images "listed as having a CC BY 2.0 license". The download page does not state a dataset licence, and says "The data is as it appears on the destination websites."
- **Site terms:** Flickr terms **not read**. ML use under CC BY is not restricted by the licence itself, but I have not confirmed that Flickr's terms or Google's terms add nothing. Not verified.
- **Labels:** image-level labels with human-verified and machine-generated sources (human-verified have confidence 1 or 0); boxes for 600 boxable classes. An image-information file with `License`, `Author`, `OriginalURL` columns is described, which allows filtering to CC BY and generating an attribution CSV. I did not confirm that "Bird" is a class name (expected, not verified); a download script would read the class-descriptions file.
- **Size:** 1,743,042 training images and 14.6M boxes across 600 boxable classes (dataset-wide; per-class counts not read). A subset of a few thousand images is enough.
- **Sequence IDs:** none; images are independent photos, so a per-image split is appropriate, with the pHash check still run and a split by author as a cheap guard against one photographer's near-identical shots.
- **Fit:** a different task (no drone class). Strongest on licence clarity, weakest on matching the project story. If used, the README and website say "bird vs not-bird" and the drone story is dropped, with the firmware text adjusted to match.

### Rejected in this round
- **Drone-vs-Bird Challenge videos (Coluccia et al.):** published description says the data is open to the research community "for non-commercial purposes" (from a paper abstract, via search; no formal licence text found). Non-commercial terms and an unclear licence document: rejected.
- **AOD-4 (airborne object detection):** a search summary said it was assembled from diverse sources; the article page would not load for me (browser check), so I could not confirm. Rejected as unclear provenance.
- **Anti-UAV, DUT Anti-UAV, Det-Fly, MAV-VID, NPS-Drones:** drone-only, and I found no licence for any of them. Not assessed further; MAV-VID is described as a Kaggle collection (provenance unclear).
- **Roboflow Universe projects:** unverified upstream rights.
- **Kaggle "StealthKnight Bird vs Drone":** licence unverified; likely the same Pexels-derived material as the rejected set (unverified).
- **CUB-200-2011:** birds only; a mirror states non-commercial research and education use only.
- **iNaturalist Open Data (as a bird source):** photo licences vary (CC0, CC-BY, CC-BY-NC), so it needs per-photo filtering; the page I read does not say anything about ML use. Possible bird supplement later, not a primary choice.

### Outcome
Rank 1 chosen by the owner on 2026-11-06 and inspected above. Rank 2 (Zagreb) dropped for now. Open Images is kept only as an out-of-domain test set.

## Crops (Phase A, `train/make_crops.py`)

Every 15th frame of each of the 235 kept videos is sampled. Each labelled box in a sampled frame becomes one crop: a square of twice the box's longer side (at least 48 px), centred on the box, kept inside the frame, resized to 112 x 112 and stored as JPEG in `data/crops/` (gitignored, never published). One background crop is taken from every second sampled frame, from a random region that overlaps no box, sized like the video's median box. Total 8012 crops (`measured (host CPU)`, counts in `results/crops_summary.json`). The script asserts that no scene cluster appears in two splits.

| Split | bird | drone | background | airplane | helicopter | all |
| --- | --- | --- | --- | --- | --- | --- |
| train | 873 | 1404 | 1522 | 643 | 294 | 4736 |
| val | 340 | 396 | 413 | 152 | 105 | 1406 |
| test | 267 | 678 | 629 | 213 | 83 | 1870 |

Airplane, helicopter and background crops all carry the class "neither"; the subtype is kept so they can be reported separately.

Limits seen when checking a montage of test crops by eye (local only, not saved): most background crops are plain sky, so that subtype is easy and a model can get it right without learning much; and bird and drone targets are often only a few dozen pixels across, so after enlarging to the model input they are blurs.

## Out-of-domain test set

Planned (Open Images images with none of the labels Bird, Drone, Airplane, Helicopter, Kite) but **not built**: no Open Images download script or attribution file exists yet. All reported results are in-domain.
