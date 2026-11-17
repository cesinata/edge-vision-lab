"""Train a MobileNetV3-Small crop classifier (bird / drone / neither) on CPU.

    python train/train.py [--epochs 8] [--seed 0]

Starts from torchvision's ImageNet weights (downloaded at run time, never
committed), replaces the last layer with 3 outputs and fine-tunes everything.
Uses the train split; the validation split picks the best epoch (macro F1). The
test split is not touched here (see train/evaluate.py).

Writes models/mobilenetv3s_best.pt (gitignored) and results/train_log.json
(metrics and timings only).
"""
import argparse
import json
import platform
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import data  # noqa: E402
import metrics  # noqa: E402


def build_model(pretrained=True):
    w = MobileNet_V3_Small_Weights.IMAGENET1K_V1 if pretrained else None
    m = mobilenet_v3_small(weights=w)
    m.classifier[3] = nn.Linear(m.classifier[3].in_features, len(data.CLASSES))
    return m


def run_eval(model, loader):
    model.eval()
    ys, ps = [], []
    with torch.no_grad():
        for x, y in loader:
            ps.append(model(x).argmax(1).numpy())
            ys.append(y.numpy())
    y, p = np.concatenate(ys), np.concatenate(ps)
    return metrics.summarise(y, p, len(data.CLASSES))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--lr", type=float, default=5e-4)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="models/mobilenetv3s_best.pt")
    ap.add_argument("--log", default="results/train_log.json")
    args = ap.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(args.threads)

    train_rows = data.read_manifest(split="train")
    val_rows = data.read_manifest(split="val")
    g = torch.Generator().manual_seed(args.seed)
    train_dl = DataLoader(data.CropDataset(train_rows, data.train_transform()), batch_size=args.batch,
                          shuffle=True, num_workers=args.workers, generator=g, persistent_workers=True)
    val_dl = DataLoader(data.CropDataset(val_rows, data.eval_transform()), batch_size=128,
                        num_workers=args.workers, persistent_workers=True)

    model = build_model()
    weights = data.class_weights(train_rows)
    loss_fn = nn.CrossEntropyLoss(weight=weights)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs * len(train_dl))

    log = {
        "label": "measured (host CPU)", "command": "python train/train.py",
        "seed": args.seed, "epochs": args.epochs, "batch": args.batch, "lr": args.lr,
        "model": "torchvision mobilenet_v3_small, ImageNet-pretrained start, 3-way head",
        "input": data.INPUT, "torch": torch.__version__, "python": platform.python_version(),
        "cpu_threads": args.threads, "machine": platform.platform(),
        "n_train": len(train_rows), "n_val": len(val_rows),
        "class_weights": dict(zip(data.CLASSES, [round(float(w), 4) for w in weights])),
        "epochs_log": [],
    }
    best, t_start = -1.0, time.time()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    for epoch in range(1, args.epochs + 1):
        model.train()
        t0, running, n = time.time(), 0.0, 0
        for x, y in train_dl:
            opt.zero_grad()
            loss = loss_fn(model(x), y)
            loss.backward()
            opt.step()
            sched.step()
            running += loss.item() * len(y)
            n += len(y)
        v = run_eval(model, val_dl)
        rec = {"epoch": epoch, "train_loss": round(running / n, 4), "val_macro_f1": round(v["macro_f1"], 4),
               "val_accuracy": round(v["accuracy"], 4), "epoch_seconds": round(time.time() - t0, 1)}
        log["epochs_log"].append(rec)
        print(rec, flush=True)
        if v["macro_f1"] > best:
            best = v["macro_f1"]
            torch.save({"state_dict": model.state_dict(), "classes": data.CLASSES, "epoch": epoch}, args.out)
            log["best_epoch"] = epoch
    log["best_val_macro_f1"] = round(best, 4)
    log["wall_seconds"] = round(time.time() - t_start, 1)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).write_text(json.dumps(log, indent=1))
    print("done", log["wall_seconds"], "s; best epoch", log["best_epoch"])


if __name__ == "__main__":
    main()
