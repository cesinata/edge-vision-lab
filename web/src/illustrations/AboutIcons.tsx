import { Svg } from './Svg';

const VB = '0 0 96 56';

/** What's the example? A bird and a drone side by side. */
export function BirdDroneIcon() {
  return (
    <Svg viewBox={VB} className="ill ico">
      <path d="M8 34C14 22 22 22 26 32C30 22 38 22 44 34" />
      <circle cx="26" cy="32" r="2.5" fill="var(--mark)" />
      <rect x="62" y="30" width="20" height="9" rx="3" />
      <path d="M62 33L52 27M82 33L92 27M62 37L52 43M82 37L92 43" />
      <ellipse cx="50" cy="26" rx="7" ry="1.8" />
      <ellipse cx="94" cy="26" rx="7" ry="1.8" />
      <path d="M68 39V45M76 39V45" />
    </Svg>
  );
}

/** Why is it hard? A small chip next to a much larger laptop outline. */
export function ChipLaptopIcon() {
  return (
    <Svg viewBox={VB} className="ill ico">
      <rect x="6" y="28" width="16" height="16" rx="2" />
      <rect x="11" y="33" width="6" height="6" fill="var(--mark)" />
      <path d="M10 28V24M14 28V24M18 28V24M10 44V48M14 44V48M18 44V48M6 32H2M6 36H2M6 40H2M22 32H26M22 36H26M22 40H26" />
      <rect x="40" y="8" width="52" height="34" rx="3" />
      <path d="M34 48H98M40 42L34 48M92 42L98 48" />
    </Svg>
  );
}

/** What will I find here? Six boxes in a row, the first one marked. */
export function SixBoxesIcon() {
  return (
    <Svg viewBox={VB} className="ill ico">
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <g key={i}>
          <rect x={4 + i * 15} y="22" width="11" height="14" rx="1.5" fill={i === 0 ? 'var(--mark)' : 'none'} />
          <path d={`M${7 + i * 15} 42H${12 + i * 15}`} strokeWidth="1.25" />
          {i < 5 ? <path d={`M${15 + i * 15} 29H${19 + i * 15}`} strokeWidth="1.25" /> : null}
        </g>
      ))}
    </Svg>
  );
}

/** What's real? A ruler and a check mark. */
export function RulerCheckIcon() {
  return (
    <Svg viewBox={VB} className="ill ico">
      <rect x="6" y="18" width="52" height="14" rx="2" />
      <path d="M14 18V25M22 18V23M30 18V25M38 18V23M46 18V25M54 18V23" />
      <path d="M66 30L74 38L90 16" />
      <circle cx="74" cy="38" r="2.5" fill="var(--mark)" />
      <path d="M6 44H58" strokeDasharray="3 4" />
    </Svg>
  );
}
