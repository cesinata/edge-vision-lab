import { Svg } from './Svg';

const VB = '0 0 300 90';
const cls = 'ill sk';

/** Small bar sketch: three bars, one short and marked. A sketch, not a chart: no numbers. */
export function SketchRecall() {
  return (
    <Svg viewBox={VB} className={cls}>
      <path d="M10 80H290" />
      <rect x="40" y="20" width="56" height="60" />
      <rect x="122" y="52" width="56" height="28" fill="var(--mark)" />
      <rect x="204" y="28" width="56" height="52" />
    </Svg>
  );
}

/** A grid shrinks to a smaller square, part of it kept as dashed. */
export function SketchShrink() {
  return (
    <Svg viewBox={VB} className={cls}>
      <rect x="30" y="14" width="70" height="66" rx="2" />
      <path d="M30 36H100M30 58H100M53 14V80M76 14V80" />
      <path d="M118 47H160M150 39L160 47L150 55" />
      <rect x="180" y="34" width="40" height="40" rx="2" fill="var(--mark)" />
      <rect x="226" y="34" width="40" height="40" rx="2" strokeDasharray="4 4" />
    </Svg>
  );
}

/** A row of scene boxes, two of them marked: few places. */
export function SketchScenes() {
  return (
    <Svg viewBox={VB} className={cls}>
      {[20, 74, 128].map((x) => <rect key={x} x={x} y="20" width="44" height="44" rx="4" />)}
      {[182, 236].map((x) => <rect key={x} x={x} y="20" width="44" height="44" rx="4" fill="var(--mark)" />)}
      <path d="M182 76H280" />
    </Svg>
  );
}
