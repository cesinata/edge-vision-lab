import { Svg } from './Svg';

const VB = '0 0 48 48';

export function IconData() {
  return (
    <Svg viewBox={VB} className="ill ico">
      <rect x="6" y="12" width="36" height="24" rx="3" />
      <path d="M6 18H42M6 30H42M12 12V18M18 12V18M24 12V18M30 12V18M36 12V18M12 30V36M18 30V36M24 30V36M30 30V36M36 30V36" />
      <rect x="19" y="20" width="10" height="8" fill="var(--mark)" stroke="none" />
    </Svg>
  );
}
export function IconSplit() {
  return (
    <Svg viewBox={VB} className="ill ico">
      <circle cx="24" cy="8" r="4" />
      <path d="M24 12V20M24 20L10 32M24 20V32M24 20L38 32" />
      <rect x="5" y="32" width="10" height="10" rx="2" />
      <rect x="19" y="32" width="10" height="10" rx="2" />
      <rect x="33" y="32" width="10" height="10" rx="2" fill="var(--mark)" />
    </Svg>
  );
}
export function IconTrain() {
  return (
    <Svg viewBox={VB} className="ill ico">
      <path d="M10 14L24 10M10 14L24 24M10 14L24 38M10 34L24 10M10 34L24 24M10 34L24 38M24 10L38 24M24 24L38 24M24 38L38 24" />
      {[[10, 14], [10, 34], [24, 10], [24, 24], [24, 38]].map(([x, y]) => (
        <circle key={`${x}${y}`} cx={x} cy={y} r="3.5" fill="var(--bg)" />
      ))}
      <circle cx="38" cy="24" r="3.5" fill="var(--mark)" />
    </Svg>
  );
}
export function IconEval() {
  return (
    <Svg viewBox={VB} className="ill ico">
      <rect x="8" y="8" width="32" height="32" rx="2" />
      <path d="M8 18.7H40M8 29.3H40M18.7 8V40M29.3 8V40" />
      <rect x="10" y="10" width="7" height="7" fill="var(--mark)" stroke="none" />
      <rect x="20.7" y="20.7" width="7" height="7" fill="var(--mark)" stroke="none" />
      <rect x="31.3" y="31.3" width="7" height="7" fill="var(--mark)" stroke="none" />
    </Svg>
  );
}
export function IconQuant() {
  return (
    <Svg viewBox={VB} className="ill ico">
      <rect x="5" y="7" width="22" height="22" rx="2" />
      <path d="M5 14H27M5 21H27M12 7V29M19 7V29" />
      <path d="M28 30L34 34M34 34V29M34 34H29" />
      <rect x="34" y="34" width="10" height="10" rx="1.5" fill="var(--mark)" />
    </Svg>
  );
}
export function IconFirmware() {
  return (
    <Svg viewBox={VB} className="ill ico">
      <rect x="13" y="13" width="22" height="22" rx="3" />
      <rect x="19" y="19" width="10" height="10" rx="1" fill="var(--mark)" />
      <path d="M18 13V7M24 13V7M30 13V7M18 35V41M24 35V41M30 35V41M13 18H7M13 24H7M13 30H7M35 18H41M35 24H41M35 30H41" />
    </Svg>
  );
}

export const PIPELINE_ICONS = [IconData, IconSplit, IconTrain, IconEval, IconQuant, IconFirmware];
