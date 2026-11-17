// A small tag saying how a number was produced. Labels are the fixed set from CLAUDE.md.
export type LabelKind =
  | 'measured (host CPU)'
  | 'measured (browser)'
  | 'estimated'
  | 'simulated'
  | 'vendor-published'
  | 'not measured on hardware';

export function Label({ kind, detail }: { kind: LabelKind; detail?: string }) {
  return <span className="tag">{detail ? `${kind}: ${detail}` : kind}</span>;
}

export function fmt(v: number | null | undefined, digits = 3): string {
  return v === null || v === undefined || Number.isNaN(v) ? 'not run yet' : v.toFixed(digits);
}
