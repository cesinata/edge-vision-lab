"""Download the Svanstrom et al. drone detection dataset from Zenodo.

Local use only. Nothing downloaded here is committed (data/ is gitignored) and
nothing derived from it may be published until the data licence is confirmed
with the authors (see docs/data.md).

    python train/download_data.py [--data-dir data/raw]

Source: https://zenodo.org/records/5500576 (v1.0.0, DOI 10.5281/zenodo.5500576)
Zenodo licence field: "Other (Open)". The GitHub repository lists CC0-1.0.
The two disagree and the authors have not yet confirmed.
"""
import argparse
import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = ("https://zenodo.org/api/records/5500576/files/"
       "DroneDetectionThesis/Drone-detection-dataset-v1.0.0.zip/content")
FILENAME = "drone-detection-v1.0.0.zip"
SIZE = 311348350
MD5 = "5d9b891a87857b3d9ee8872e8a1f0f0f"  # as published by Zenodo


def md5sum(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/raw")
    args = ap.parse_args()

    out_dir = Path(args.data_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / FILENAME

    if not zip_path.exists():
        print(f"downloading {URL}")
        urllib.request.urlretrieve(URL, zip_path)

    if zip_path.stat().st_size != SIZE or md5sum(zip_path) != MD5:
        sys.exit(f"{zip_path}: size or md5 does not match Zenodo's published values")
    print("md5 ok")

    extract_dir = out_dir / "extracted"
    if not extract_dir.exists():
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(extract_dir)
    print(f"extracted to {extract_dir}")


if __name__ == "__main__":
    main()
