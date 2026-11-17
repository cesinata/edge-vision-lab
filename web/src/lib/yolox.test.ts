import { describe, expect, it } from 'vitest';
import { COCO_CLASSES } from './cocoClasses';
import { INPUT, N_ANCHORS, N_CLASSES, decode, iou, letterboxScale, nms, rgbaToBgrChw } from './yolox';

function blank(): Float32Array {
  return new Float32Array(N_ANCHORS * (5 + N_CLASSES)); // all zeros: objectness 0
}

describe('yolox decoding', () => {
  it('has 80 class names and 3549 anchors', () => {
    expect(COCO_CLASSES.length).toBe(80);
    expect(COCO_CLASSES[4]).toBe('airplane');
    expect(COCO_CLASSES[14]).toBe('bird');
    expect(N_ANCHORS).toBe(3549);
  });

  it('decodes one stride-8 anchor by hand-computed values', () => {
    // grid 52x52 at stride 8; anchor at gx=10, gy=5 -> index 5*52+10
    const a = 5 * 52 + 10;
    const out = blank();
    const o = a * 85;
    out[o] = 0.5; // tx
    out[o + 1] = 0.25; // ty
    out[o + 2] = Math.log(2); // tw -> w = 2*8 = 16
    out[o + 3] = Math.log(3); // th -> h = 3*8 = 24
    out[o + 4] = 0.9; // objectness
    out[o + 5 + 14] = 0.8; // class 14 = bird, score 0.9*0.8 = 0.72
    const scale = 0.5; // source was twice as large as the letterboxed image
    const d = decode(out, scale);
    expect(d.length).toBe(1);
    const cx = (10 + 0.5) * 8; // 84
    const cy = (5 + 0.25) * 8; // 42
    expect(d[0].label).toBe('bird');
    expect(d[0].score).toBeCloseTo(0.72, 5);
    expect(d[0].w).toBeCloseTo(16 / scale, 4);
    expect(d[0].h).toBeCloseTo(24 / scale, 4);
    expect(d[0].x).toBeCloseTo((cx - 8) / scale, 4);
    expect(d[0].y).toBeCloseTo((cy - 12) / scale, 4);
  });

  it('indexes stride-16 and stride-32 anchors after the stride-8 block', () => {
    const out = blank();
    const base16 = 52 * 52; // first stride-16 anchor
    const o16 = (base16 + 3 * 26 + 4) * 85; // gx=4, gy=3 at stride 16
    out[o16] = 0; out[o16 + 1] = 0; out[o16 + 2] = 0; out[o16 + 3] = 0; out[o16 + 4] = 1; out[o16 + 5 + 4] = 0.7;
    const base32 = 52 * 52 + 26 * 26;
    const o32 = (base32 + 2 * 13 + 1) * 85; // gx=1, gy=2 at stride 32
    out[o32] = 0; out[o32 + 1] = 0; out[o32 + 2] = 0; out[o32 + 3] = 0; out[o32 + 4] = 1; out[o32 + 5 + 0] = 0.6;
    const d = decode(out, 1).sort((p, q) => q.score - p.score);
    expect(d.map((x) => x.label)).toEqual(['airplane', 'person']);
    expect(d[0].x).toBeCloseTo(4 * 16 - 8, 4); // centre 4*16, width 1*16
    expect(d[1].y).toBeCloseTo(2 * 32 - 16, 4);
  });

  it('drops detections below the score threshold', () => {
    const out = blank();
    const o = 0;
    out[o + 4] = 0.5;
    out[o + 5] = 0.5; // 0.25 < 0.3
    expect(decode(out, 1).length).toBe(0);
  });

  it('non-maximum suppression keeps the higher score of overlapping same-class boxes', () => {
    const mk = (x: number, score: number, classId = 0) => ({ x, y: 0, w: 10, h: 10, score, classId, label: 'person' });
    const kept = nms([mk(0, 0.9), mk(1, 0.8), mk(100, 0.7), mk(1, 0.95, 1)], 0.45);
    expect(kept.map((k) => k.score).sort()).toEqual([0.7, 0.9, 0.95].sort());
  });

  it('computes iou and letterbox scale', () => {
    const a = { x: 0, y: 0, w: 10, h: 10, score: 1, classId: 0, label: 'x' };
    const b = { x: 5, y: 0, w: 10, h: 10, score: 1, classId: 0, label: 'x' };
    expect(iou(a, b)).toBeCloseTo(50 / 150, 6);
    expect(letterboxScale(640, 512)).toBeCloseTo(416 / 640, 6);
  });

  it('converts RGBA to BGR CHW without normalising', () => {
    const rgba = new Uint8ClampedArray(INPUT * INPUT * 4);
    rgba[0] = 10; rgba[1] = 20; rgba[2] = 30; rgba[3] = 255; // first pixel R=10 G=20 B=30
    const chw = rgbaToBgrChw(rgba);
    const plane = INPUT * INPUT;
    expect([chw[0], chw[plane], chw[2 * plane]]).toEqual([30, 20, 10]);
  });
});
