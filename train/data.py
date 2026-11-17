"""Crop dataset and preprocessing shared by training, evaluation and export.

The manifest (data/crops/manifest.csv) is written by train/make_crops.py. Crops
are 112 x 112 JPEGs; the model input is 224 x 224, ImageNet-normalised.
"""
import csv

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms as T

CLASSES = ["bird", "drone", "neither"]
SUBTYPES = ["bird", "drone", "background", "airplane", "helicopter"]
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)
INPUT = 224


def read_manifest(path="data/crops/manifest.csv", split=None):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if split is None or r["split"] == split]


def eval_transform():
    return T.Compose([T.Resize((INPUT, INPUT), interpolation=T.InterpolationMode.BILINEAR),
                      T.ToTensor(), T.Normalize(MEAN, STD)])


def train_transform():
    return T.Compose([
        T.RandomResizedCrop(INPUT, scale=(0.7, 1.0), ratio=(0.9, 1.1),
                            interpolation=T.InterpolationMode.BILINEAR),
        T.RandomHorizontalFlip(),
        T.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.15),
        T.ToTensor(), T.Normalize(MEAN, STD)])


class CropDataset(Dataset):
    def __init__(self, rows, transform):
        self.rows, self.transform = rows, transform

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        r = self.rows[i]
        img = Image.open(r["path"]).convert("RGB")
        return self.transform(img), CLASSES.index(r["class3"])


def class_weights(rows):
    """Inverse-frequency weights over the three classes, from these rows only."""
    counts = np.array([sum(r["class3"] == c for r in rows) for c in CLASSES], dtype=float)
    w = counts.sum() / (len(CLASSES) * counts)
    return torch.tensor(w, dtype=torch.float32)
