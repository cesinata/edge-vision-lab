// Results written by the Python scripts (results/*.json and bench/results.json).
// Missing files are fine: the pages then say "not run yet" instead of showing a number.
type Json = Record<string, unknown>;

const found = import.meta.glob<Json>(['../../../results/*.json', '../../../bench/results.json'], {
  eager: true,
  import: 'default',
});

function pick(suffix: string): Json | null {
  const key = Object.keys(found).find((k) => k.endsWith(suffix));
  return key ? found[key] : null;
}

export const evalTorch = pick('results/eval_torch.json') as EvalResult | null;
export const bench = pick('bench/results.json') as BenchResult | null;
export const trainLog = pick('results/train_log.json');
export const cropsSummary = pick('results/crops_summary.json');
export const firmwareCoverage = pick('results/firmware_coverage.json');
export const splitSummary = pick('results/split_summary.json') as SplitSummary | null;

export interface Metric {
  value: number | null;
  label: string;
  ci95?: [number, number];
}

export interface EvalResult {
  label: string;
  n_crops: number;
  n_videos: number;
  accuracy: number;
  macro_f1: number;
  macro_f1_ci95: [number, number];
  per_class: Record<
    string,
    { support: number; precision: number; recall: number; f1: number; precision_ci95: [number, number]; recall_ci95: [number, number] }
  >;
  confusion_matrix: { rows_true: string[]; cols_pred: string[]; values: number[][] };
  subtype_vs_predicted: { cols_pred: string[]; rows: Record<string, number[]> };
  subtype_accuracy: Record<string, { accuracy: number; n_crops: number; n_videos: number; ci95: [number, number] }>;
  videos_per_class: Record<string, number>;
}

export interface BenchResult {
  [key: string]: unknown;
}

export interface BenchMetric {
  value: number | null;
  label: string;
  unit?: string;
  detail?: string;
}

/** Read a labelled metric from bench/results.json, or null if it is not there. */
export function benchMetric(...path: string[]): BenchMetric | null {
  let node: unknown = bench;
  for (const key of path) {
    if (node === null || typeof node !== 'object') return null;
    node = (node as Record<string, unknown>)[key];
  }
  if (node && typeof node === 'object' && 'label' in (node as object)) return node as BenchMetric;
  return null;
}

export interface SplitSummary {
  n_videos: number;
  n_clusters: number;
  largest_cluster_sizes: number[];
  videos_per_class: Record<string, number>;
  videos_per_class_per_split: Record<string, Record<string, number>>;
  clusters_touched_per_class: Record<string, number>;
  cross_split_video_pairs_within_threshold: Record<string, number>;
  phash_threshold_bits: number;
}
