import { Svg } from './Svg';

type Kind = 'train' | 'validation' | 'test';
const SCENES: Kind[] = ['train', 'train', 'validation', 'train', 'test', 'test'];
// frames of the random-split box: T = train, X = test. Both kinds sit in the same scene.
const RANDOM = 'TXTTXTTXTTXTXTTT';

function Frame({ x, y, kind, id }: { x: number; y: number; kind: Kind; id: string }) {
  const fill = kind === 'train' ? 'var(--ink)' : kind === 'test' ? 'var(--mark)' : `url(#${id})`;
  return <rect x={x} y={y} width="22" height="22" rx="2" fill={fill} />;
}

/** Six scenes of four frames each, coloured by split, beside a random split that mixes train and test. */
export function SplitDiagram({ id = 'sd' }: { id?: string }) {
  const hatch = `${id}-hatch`;
  return (
    <Svg
      viewBox="0 0 640 232"
      td={14}
      tp={24}
      label="Drawing of six scenes, each a box of four frames, marked train, validation or test, so each scene sits entirely in one group. Beside them, a box labelled random split mixes train and test frames from the same scenes."
    >
      <defs>
        <pattern id={hatch} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <path d="M0 0V6" stroke="currentColor" strokeWidth="2" />
        </pattern>
      </defs>
      {SCENES.map((k, i) => {
        const bx = 8 + (i % 3) * 132;
        const by = 8 + Math.floor(i / 3) * 78;
        return (
          <g key={i}>
            <rect x={bx} y={by} width="122" height="62" rx="4" fill="var(--bg)" />
            {[0, 1, 2, 3].map((f) => (
              <Frame key={f} x={bx + 8 + f * 27} y={by + 14} kind={k} id={hatch} />
            ))}
          </g>
        );
      })}
      <rect x="418" y="8" width="214" height="208" rx="4" fill="var(--bg)" strokeDasharray="5 4" />
      <text x="430" y="32" className="t" fill="var(--ink)" stroke="none">random split</text>
      {RANDOM.split('').map((c, i) => (
        <Frame key={i} x={434 + (i % 4) * 46} y={48 + Math.floor(i / 4) * 40} kind={c === 'T' ? 'train' : 'test'} id={hatch} />
      ))}
      {[0, 1, 2].map((k) => (
        <g key={k}>
          <Frame x={[8, 140, 316][k]} y={190} kind={(['train', 'validation', 'test'] as Kind[])[k]} id={hatch} />
          <text x={[36, 168, 344][k]} y={207} className="t" fill="var(--ink)" stroke="none">{(['train', 'validation', 'test'] as Kind[])[k]}</text>
        </g>
      ))}
    </Svg>
  );
}
