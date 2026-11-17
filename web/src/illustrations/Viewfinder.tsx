import { Svg, Tab } from './Svg';

/** Camera viewfinder shown until the camera starts: corner brackets, crosshair, a boxed bird. */
export function Viewfinder() {
  return (
    <Svg
      viewBox="0 0 560 300"
      td={14}
      tp={22}
      label="Camera viewfinder: corner brackets frame an empty sky with a line-drawn bird inside a detection box."
    >
      <path d="M24 54V24H54M506 24H536V54M536 246V276H506M54 276H24V246" />
      <path d="M270 150H290M280 140V160" strokeWidth="1" />
      <rect x="320" y="90" width="96" height="58" rx="2" />
      <path d="M338 128C348 112 358 112 366 124C374 112 384 112 394 128" />
      <Tab x={320} y={90} w={72} text="bird" />
      <path d="M90 230C120 220 150 224 170 234M400 236C440 222 480 224 510 236" strokeWidth="1" />
    </Svg>
  );
}
