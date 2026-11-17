import { Svg } from './Svg';

export const LESSON_PATHS = [
  { path: 'M14 40L26 28L34 36L50 20M50 20H42M50 20V28', dx: 14, dy: 40 },
  { path: 'M12 32H24M40 32H52M24 24H40V40H24Z', dx: 52, dy: 32 },
  { path: 'M32 14V26M32 26L18 40M32 26V40M32 26L46 40', dx: 46, dy: 44 },
  { path: 'M14 14H50V50H14ZM14 26H50M14 38H50M26 14V50M38 14V50', dx: 20, dy: 20 },
  { path: 'M12 12H36V36H12ZM40 40L46 46', dx: 48, dy: 48 },
  { path: 'M22 22H42V42H22ZM28 22V14M36 22V14M28 42V50M36 42V50M22 28H14M22 36H14M42 28H50M42 36H50', dx: 32, dy: 32 },
];

/** One drawing per lesson, 64 x 64 in a light outlined frame. size scales the same drawing up for the lesson page. */
export function LessonIcon({ index, size = 64 }: { index: number; size?: number }) {
  const l = LESSON_PATHS[index];
  return (
    <Svg viewBox="0 0 64 64" width={size} height={size} className="ill ico">
      <rect x="1" y="1" width="62" height="62" rx="4" stroke="var(--rule)" />
      <path d={l.path} />
      <circle cx={l.dx} cy={l.dy} r="4" fill="var(--mark)" />
    </Svg>
  );
}
