import type { KeyboardEvent, ReactElement } from 'react';
import { Svg } from './Svg';

interface Part {
  n: number;
  name: string;
  hit: [number, number, number, number];
  badge: [number, number];
  body: ReactElement;
}

const PARTS: Part[] = [
  { n: 1, name: 'Camera connector', hit: [184, 228, 152, 64], badge: [260, 318],
    body: <><rect x="190" y="262" width="140" height="24" rx="3" /><path d="M200 274H320M260 232V262" strokeDasharray="2 4" /></> },
  { n: 2, name: 'Microcontroller', hit: [196, 104, 132, 130], badge: [338, 100],
    body: <><rect x="210" y="118" width="104" height="104" rx="6" fill="var(--bg)" /><rect x="232" y="140" width="60" height="60" rx="3" fill="var(--mark)" />
      <path d="M224 118V108M240 118V108M256 118V108M272 118V108M288 118V108M300 118V108M224 222V232M240 222V232M256 222V232M272 222V232M288 222V232M300 222V232M210 134H200M210 150H200M210 166H200M210 182H200M210 198H200M314 134H324M314 150H324M314 166H324M314 182H324M314 198H324" /></> },
  { n: 3, name: 'Neural accelerator', hit: [320, 138, 112, 64], badge: [446, 130],
    body: <><rect x="350" y="146" width="70" height="48" rx="5" /><path d="M362 170H408M385 158V182M324 166H350" /></> },
  { n: 4, name: 'RAM', hit: [86, 112, 124, 70], badge: [84, 104],
    body: <><rect x="96" y="132" width="70" height="40" rx="4" /><path d="M108 132V124M120 132V124M132 132V124M144 132V124M156 132V124M166 152H200" /></> },
  { n: 5, name: 'Flash', hit: [86, 186, 124, 50], badge: [84, 250],
    body: <><rect x="96" y="192" width="70" height="34" rx="4" /><path d="M166 209H200" /></> },
  { n: 6, name: 'USB debug port', hit: [214, 4, 78, 50], badge: [306, 22],
    body: <><rect x="225" y="14" width="56" height="26" rx="5" fill="var(--bg)" /><path d="M237 27H269" /></> },
  { n: 7, name: 'Pin headers', hit: [44, 72, 36, 196], badge: [488, 170],
    body: <path d="M58 80V260M70 80V260M450 80V260M462 80V260" strokeDasharray="1 7" strokeWidth="3" /> },
];

export const BOARD_PARTS = PARTS.map(({ n, name }) => ({ n, name }));

/** Simplified original board drawing. Parts are numbered; hovering, focusing or tapping a number highlights it. */
export function BoardAnatomy({ active, onHover, onSelect }: { active: number | null; onHover: (n: number | null) => void; onSelect: (n: number) => void }) {
  const key = (n: number) => (e: KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect(n);
    }
  };
  return (
    <Svg
      viewBox="0 0 520 340"
      td={15}
      tp={24}
      label="Simplified line drawing of a generic microcontroller vision board with numbered parts: 1 camera connector, 2 microcontroller, 3 neural accelerator, 4 RAM, 5 flash, 6 USB debug port, 7 pin headers."
    >
      <rect x="40" y="30" width="440" height="280" rx="16" fill="var(--bg)" />
      <circle cx="62" cy="52" r="6" /><circle cx="458" cy="52" r="6" /><circle cx="62" cy="288" r="6" /><circle cx="458" cy="288" r="6" />
      {PARTS.map((p) => {
        const on = active === p.n;
        return (
          <g key={p.n} strokeWidth={on ? 3 : 1.5}>
            <rect x={p.hit[0]} y={p.hit[1]} width={p.hit[2]} height={p.hit[3]} rx="6" fill="var(--mark)" fillOpacity={on ? 0.55 : 0} stroke="none" />
            {p.body}
          </g>
        );
      })}
      {PARTS.map((p) => (
        <g
          key={`b${p.n}`}
          className="board-hit"
          role="button"
          tabIndex={0}
          aria-pressed={active === p.n}
          aria-label={`${p.n}, ${p.name}`}
          onMouseEnter={() => onHover(p.n)}
          onMouseLeave={() => onHover(null)}
          onFocus={() => onHover(p.n)}
          onBlur={() => onHover(null)}
          onClick={() => onSelect(p.n)}
          onKeyDown={key(p.n)}
        >
          <circle cx={p.badge[0]} cy={p.badge[1]} r="15" fill="var(--ink)" stroke="none" />
          <text x={p.badge[0]} y={p.badge[1] + 5} textAnchor="middle" className="t" fill="var(--on-ink)" stroke="none">{p.n}</text>
        </g>
      ))}
    </Svg>
  );
}
