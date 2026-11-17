// Preprocessing and output handling for this project's crop classifier. Matches
// train/data.py: 224x224 input, RGB, ImageNet mean and std, 3 outputs.
export const CLASSES = ['bird', 'drone', 'neither'] as const;
export const SIZE = 224;
const MEAN = [0.485, 0.456, 0.406];
const STD = [0.229, 0.224, 0.225];

/** RGBA pixels of a SIZE x SIZE canvas -> Float32 CHW, RGB, normalised. */
export function rgbaToNormalisedChw(rgba: Uint8ClampedArray): Float32Array {
  const plane = SIZE * SIZE;
  const out = new Float32Array(3 * plane);
  for (let i = 0; i < plane; i++) {
    for (let c = 0; c < 3; c++) out[c * plane + i] = (rgba[i * 4 + c] / 255 - MEAN[c]) / STD[c];
  }
  return out;
}

export function softmax(logits: ArrayLike<number>): number[] {
  const arr = Array.from(logits);
  const max = Math.max(...arr);
  const exps = arr.map((v) => Math.exp(v - max));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map((v) => v / sum);
}
