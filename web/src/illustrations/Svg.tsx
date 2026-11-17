import type { CSSProperties, ReactNode } from 'react';

interface Props {
  viewBox: string;
  /** Accessible name. Leave out for a purely decorative drawing (it is then aria-hidden). */
  label?: string;
  className?: string;
  width?: number | string;
  height?: number | string;
  strokeWidth?: number;
  /** Label size in drawing units on desktop and on phones, so labels stay readable when the drawing shrinks. */
  td?: number;
  tp?: number;
  children: ReactNode;
}

/** Fine-line drawing wrapper: stroke follows the theme (currentColor), round caps and joins, no fill. */
export function Svg({ viewBox, label, className = 'ill', width, height, strokeWidth = 1.5, td = 14, tp = 20, children }: Props) {
  const style = { '--td': `${td}px`, '--tp': `${tp}px` } as CSSProperties;
  const a11y = label ? { role: 'img' as const, 'aria-label': label } : { 'aria-hidden': true as const };
  return (
    <svg
      viewBox={viewBox}
      className={className}
      width={width}
      height={height}
      style={style}
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      {...a11y}
    >
      {children}
    </svg>
  );
}

/** Label with a filled ink tab behind it, as used for detection boxes. y is the bottom edge of the tab. */
export function Tab({ x, y, w, text }: { x: number; y: number; w: number; text: string }) {
  return (
    <>
      <rect x={x} y={y - 26} width={w} height={26} fill="var(--ink)" stroke="none" />
      <text x={x + 6} y={y - 8} fill="var(--on-ink)" stroke="none" className="t">{text}</text>
    </>
  );
}
