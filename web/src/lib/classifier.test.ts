import { describe, expect, it } from 'vitest';
import { SIZE, rgbaToNormalisedChw, softmax } from './classifier';

describe('classifier helpers', () => {
  it('normalises with ImageNet mean and std in RGB order', () => {
    const rgba = new Uint8ClampedArray(SIZE * SIZE * 4);
    rgba[0] = 255; rgba[1] = 0; rgba[2] = 0; rgba[3] = 255;
    const chw = rgbaToNormalisedChw(rgba);
    const plane = SIZE * SIZE;
    expect(chw[0]).toBeCloseTo((1 - 0.485) / 0.229, 5);
    expect(chw[plane]).toBeCloseTo((0 - 0.456) / 0.224, 5);
    expect(chw[2 * plane]).toBeCloseTo((0 - 0.406) / 0.225, 5);
  });

  it('softmax sums to one and is stable for large logits', () => {
    const p = softmax([1000, 0, -1000]);
    expect(p.reduce((a, b) => a + b, 0)).toBeCloseTo(1, 9);
    expect(p[0]).toBeCloseTo(1, 9);
    expect(Number.isNaN(p[1])).toBe(false);
  });
});
