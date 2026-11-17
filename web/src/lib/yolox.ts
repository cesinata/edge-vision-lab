import { COCO_CLASSES } from './cocoClasses';

// YOLOX-Nano ONNX from the Megvii release: input [1,3,416,416] float, BGR, values
// 0..255 (no normalisation), letterboxed with grey 114 at the top left. Output
// [1,3549,85]: per anchor (x, y, w, h, objectness, 80 class scores), raw, not
// decoded. Decoding adds the grid offset and multiplies by the stride.
export const INPUT = 416;
export const STRIDES = [8, 16, 32];
export const N_CLASSES = 80;
export const N_ANCHORS = STRIDES.reduce((n, s) => n + (INPUT / s) ** 2, 0); // 3549

export interface Detection {
  x: number; // top-left, in source image pixels
  y: number;
  w: number;
  h: number;
  score: number;
  classId: number;
  label: string;
}

export function letterboxScale(srcW: number, srcH: number): number {
  return Math.min(INPUT / srcH, INPUT / srcW);
}

/** RGBA pixels of the 416x416 letterboxed canvas -> Float32 CHW in BGR order. */
export function rgbaToBgrChw(rgba: Uint8ClampedArray): Float32Array {
  const plane = INPUT * INPUT;
  const out = new Float32Array(3 * plane);
  for (let i = 0; i < plane; i++) {
    out[i] = rgba[i * 4 + 2]; // B
    out[plane + i] = rgba[i * 4 + 1]; // G
    out[2 * plane + i] = rgba[i * 4]; // R
  }
  return out;
}

export function iou(a: Detection, b: Detection): number {
  const iw = Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x));
  const ih = Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
  const inter = iw * ih;
  const union = a.w * a.h + b.w * b.h - inter;
  return union > 0 ? inter / union : 0;
}

/** Greedy non-maximum suppression, per class. */
export function nms(dets: Detection[], iouThreshold: number): Detection[] {
  const sorted = [...dets].sort((p, q) => q.score - p.score);
  const kept: Detection[] = [];
  for (const d of sorted) {
    if (kept.every((k) => k.classId !== d.classId || iou(k, d) <= iouThreshold)) kept.push(d);
  }
  return kept;
}

/**
 * Decode the raw output into detections in source-image pixels.
 * scale is the letterbox scale (resized = source * scale).
 */
export function decode(
  output: Float32Array,
  scale: number,
  scoreThreshold = 0.3,
  iouThreshold = 0.45,
  maxDetections = 20,
): Detection[] {
  const dets: Detection[] = [];
  let a = 0;
  for (const stride of STRIDES) {
    const n = INPUT / stride;
    for (let gy = 0; gy < n; gy++) {
      for (let gx = 0; gx < n; gx++, a++) {
        const o = a * (5 + N_CLASSES);
        const obj = output[o + 4];
        if (obj < scoreThreshold * 0.5) continue; // cheap early skip, cannot reach the threshold
        let best = 0;
        let bestScore = 0;
        for (let c = 0; c < N_CLASSES; c++) {
          const s = obj * output[o + 5 + c];
          if (s > bestScore) {
            bestScore = s;
            best = c;
          }
        }
        if (bestScore < scoreThreshold) continue;
        const cx = (output[o] + gx) * stride;
        const cy = (output[o + 1] + gy) * stride;
        const w = Math.exp(output[o + 2]) * stride;
        const h = Math.exp(output[o + 3]) * stride;
        dets.push({
          x: (cx - w / 2) / scale,
          y: (cy - h / 2) / scale,
          w: w / scale,
          h: h / scale,
          score: bestScore,
          classId: best,
          label: COCO_CLASSES[best],
        });
      }
    }
  }
  return nms(dets, iouThreshold).slice(0, maxDetections);
}
