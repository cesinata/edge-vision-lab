import { Svg, Tab } from './Svg';

/** Hero: a camera on a pole with a battery pack watches the sky. Original drawing. */
export function HeroScene() {
  return (
    <Svg
      viewBox="0 0 560 420"
      td={15}
      tp={20}
      label="Line drawing: a camera on a pole, with a battery pack beside it, watches the sky. A bird and a small drone fly in its field of view, each marked with a labelled box."
    >
      <circle cx="470" cy="70" r="26" />
      <path d="M470 30V36M470 104V110M430 70H436M504 70H510M442 42L446 46M494 94L498 98M498 42L494 46M446 94L442 98" />
      <path d="M300 92C300 80 318 76 324 86C328 74 350 74 352 88C362 86 368 98 358 102H302C294 102 294 92 300 92Z" />
      <path d="M20 380H540" />
      <path d="M40 380C60 360 90 356 120 368M380 380C410 352 470 350 520 372" />
      <path d="M70 380V370M78 380V366M86 380V372M480 380V368M488 380V364M496 380V370" />
      {/* pole and mounts */}
      <path d="M150 380V196" />
      <path d="M132 380L150 350L168 380" />
      {/* battery pack on the pole: body, terminal, level bars, mounts */}
      <rect x="92" y="296" width="46" height="62" rx="4" fill="var(--panel)" />
      <rect x="107" y="289" width="16" height="7" rx="1.5" />
      <path d="M100 312H130M100 324H130" />
      <rect x="100" y="334" width="30" height="10" rx="1.5" fill="var(--mark)" />
      <path d="M138 308H150M138 346H150" />
      {/* camera */}
      <rect x="126" y="206" width="56" height="38" rx="6" fill="var(--bg)" />
      <circle cx="192" cy="225" r="11" fill="var(--bg)" />
      <circle cx="192" cy="225" r="4" fill="var(--mark)" />
      <path d="M140 244V256H168V244" />
      <path d="M204 219L540 118" strokeDasharray="4 6" />
      <path d="M204 231L540 336" strokeDasharray="4 6" />
      {/* bird in a box */}
      <rect x="316" y="138" width="80" height="44" rx="2" strokeWidth="1.25" />
      <path d="M330 166C338 154 346 154 352 164C358 154 366 154 374 166M352 164L352 168" />
      <Tab x={316} y={138} w={68} text="bird" />
      {/* drone in a box */}
      <rect x="402" y="236" width="110" height="50" rx="2" strokeWidth="1.25" />
      <Tab x={402} y={236} w={82} text="drone" />
      <rect x="441" y="258" width="32" height="12" rx="3" />
      <path d="M441 262L424 254M473 262L490 254M441 266L424 274M473 266L490 274" />
      <ellipse cx="420" cy="252" rx="12" ry="2.5" />
      <ellipse cx="494" cy="252" rx="12" ry="2.5" />
      <path d="M448 270V278M466 270V278" />
      {/* callouts */}
      <path d="M232 300H300M232 300V286" strokeWidth="1" />
      <text x="236" y="322" className="t" fill="var(--muted)" stroke="none">field of view</text>
      <path d="M60 230H112" strokeWidth="1" />
      <circle cx="112" cy="230" r="2" fill="currentColor" />
      <text x="20" y="220" className="t" fill="var(--muted)" stroke="none">camera</text>
      <path d="M44 292L90 326" strokeWidth="1" />
      <circle cx="90" cy="326" r="2" fill="currentColor" />
      <text x="8" y="284" className="t" fill="var(--muted)" stroke="none">battery</text>
    </Svg>
  );
}
