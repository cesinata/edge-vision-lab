"""Untuned baseline: stock ImageNet MobileNetV3Small quantised to int8.

This is NOT a trained bird/drone model. It has 1000 ImageNet classes and no
fine-tuning. It exists only to exercise the TFLite int8 conversion path until
the real model from train/ is available (Phase 4).

Usage (from the repo root):
    python export/baseline_quantize.py --calib-dir path/to/some/images

Calibration images are not bundled (provenance of the old test images was
unknown). Use any images you have the right to use.
"""
import argparse
import os

import cv2
import numpy as np
import tensorflow as tf

IMG_SIZE = 224
EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def load_images(calib_dir):
    images = []
    for name in sorted(os.listdir(calib_dir)):
        if not name.lower().endswith(EXTENSIONS):
            continue
        img = cv2.imread(os.path.join(calib_dir, name))
        if img is None:
            print(f"skipping unreadable file: {name}")
            continue
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE)).astype(np.float32) / 255.0
        images.append(np.expand_dims(img, axis=0))
    return images


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calib-dir", required=True)
    parser.add_argument("--out", default="export/baseline_int8.tflite")
    args = parser.parse_args()

    images = load_images(args.calib_dir)
    if not images:
        raise SystemExit("No readable images found in --calib-dir.")

    model = tf.keras.applications.MobileNetV3Small(
        input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=True, weights="imagenet"
    )

    def representative_data_gen():
        for img in images:
            yield [img]

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_data_gen
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    tflite_model = converter.convert()
    with open(args.out, "wb") as f:
        f.write(tflite_model)
    # Size is a plain file size of the output on this machine.
    print(f"wrote {args.out}: {len(tflite_model)} bytes")


if __name__ == "__main__":
    main()
