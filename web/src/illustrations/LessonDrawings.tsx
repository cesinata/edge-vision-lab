import { Svg, Tab } from './Svg';
import { PIPELINE_ICONS } from './PipelineIcons';

/** Lesson 1: the answer travels to the cloud and back, or stays on the chip. */
export function EdgeVsCloud() {
  return (
    <Svg viewBox="0 0 560 200" td={15} tp={24} label="Two small diagrams. Left: a camera sends data up to a cloud and waits for the answer to come back. Right: a camera passes data to a chip beside it and the answer stays on the device.">
      <rect x="20" y="130" width="46" height="32" rx="5" /><circle cx="76" cy="146" r="8" /><circle cx="76" cy="146" r="3" fill="var(--mark)" />
      <path d="M120 60C120 46 142 42 150 54C156 40 184 40 186 58C198 56 206 72 192 78H124C112 78 110 62 120 60Z" />
      <text x="124" y="30" className="t" fill="var(--ink)" stroke="none">cloud</text>
      <path d="M60 126C70 100 100 86 130 82M170 82C200 90 220 110 224 136" strokeDasharray="4 5" />
      <path d="M130 82L122 80M130 82L124 90M224 136L218 128M224 136L230 128" />
      <rect x="320" y="130" width="46" height="32" rx="5" /><circle cx="376" cy="146" r="8" /><circle cx="376" cy="146" r="3" fill="var(--mark)" />
      <rect x="430" y="122" width="48" height="48" rx="5" /><rect x="442" y="134" width="24" height="24" fill="var(--mark)" />
      <path d="M440 122V114M454 122V114M468 122V114M440 170V178M454 170V178M468 170V178" />
      <path d="M394 146H426M420 140L426 146L420 152" />
      <text x="428" y="104" className="t" fill="var(--ink)" stroke="none">chip</text>
      <path d="M20 190H540" strokeWidth="1" strokeDasharray="2 5" />
    </Svg>
  );
}

/** Lesson 2: the whole pipeline as a row of its six icons. */
export function PipelineStrip({ titles }: { titles: string[] }) {
  return (
    <div className="strip" role="img" aria-label={`The six steps in a row: ${titles.join(', ')}.`}>
      {PIPELINE_ICONS.map((Icon, i) => (
        <div key={i} className="strip-step" aria-hidden="true">
          <Icon />
          <span className="lbl">{titles[i]}</span>
        </div>
      ))}
    </div>
  );
}

/** Lesson 2: a boxed bird in a frame is cut out as a small square crop. */
export function CropDrawing() {
  return (
    <Svg viewBox="0 0 560 210" td={15} tp={24} label="A video frame with a bird inside a box, an arrow, and the small square crop cut out around it.">
      <rect x="20" y="20" width="260" height="170" rx="4" />
      <path d="M32 170C60 160 100 162 130 172M200 176C230 166 262 168 270 176" strokeWidth="1" />
      <rect x="150" y="60" width="84" height="52" rx="2" strokeWidth="1.25" />
      <path d="M164 98C172 84 180 84 186 94C192 84 200 84 208 98" />
      <Tab x={150} y={60} w={78} text="bird" />
      <path d="M300 105H372M362 97L372 105L362 113" />
      <rect x="400" y="48" width="120" height="120" rx="4" fill="var(--mark)" fillOpacity="0.25" />
      <path d="M420 128C434 106 448 106 458 122C468 106 482 106 496 128" />
      <text x="400" y="196" className="t" fill="var(--ink)" stroke="none">crop</text>
    </Svg>
  );
}

/** Lesson 3: two nearly identical frames from one scene, one used to train and one to test. */
export function LeakDrawing() {
  return (
    <Svg viewBox="0 0 560 190" td={15} tp={24} label="Two nearly identical frames from the same scene. One is used for training and one for testing, joined by an equals sign, so the test frame is not new to the model.">
      <rect x="30" y="20" width="200" height="120" rx="4" />
      <path d="M44 120C80 108 120 112 160 124M170 126C196 116 216 118 224 124" strokeWidth="1" />
      <path d="M100 66C108 54 116 54 122 62C128 54 136 54 144 66" />
      <rect x="330" y="20" width="200" height="120" rx="4" />
      <path d="M344 120C380 108 420 112 460 124M470 126C496 116 516 118 524 124" strokeWidth="1" />
      <path d="M404 70C412 58 420 58 426 66C432 58 440 58 448 70" />
      <path d="M252 72H308M252 88H308" />
      <rect x="30" y="150" width="70" height="22" fill="var(--ink)" stroke="none" /><text x="38" y="166" className="t" fill="var(--on-ink)" stroke="none">train</text>
      <rect x="330" y="150" width="70" height="22" fill="var(--mark)" /><text x="338" y="166" className="t" fill="var(--ink)" stroke="none">test</text>
    </Svg>
  );
}

/** Lesson 4: a 3 x 3 grid of true class against predicted class, the diagonal marked. No numbers. */
export function ConfusionGrid() {
  const names = ['bird', 'drone', 'neither'];
  return (
    <Svg viewBox="0 0 300 230" td={15} tp={22} label="A three by three grid. Rows are the real class, columns are what the model said, each one bird, drone or neither. The diagonal, where the two agree, is marked.">
      {names.map((n, i) => (
        <g key={n}>
          <text x={86 + i * 66 + 33} y="22" textAnchor="middle" className="t" fill="var(--ink)" stroke="none">{n}</text>
          <text x="78" y={34 + i * 54 + 32} textAnchor="end" className="t" fill="var(--ink)" stroke="none">{n}</text>
        </g>
      ))}
      {[0, 1, 2].map((r) => [0, 1, 2].map((c) => (
        <rect key={`${r}${c}`} x={86 + c * 66} y={34 + r * 54} width="66" height="54" fill={r === c ? 'var(--mark)' : 'none'} />
      )))}
      <text x="86" y="214" className="t" fill="var(--muted)" stroke="none">said →   real ↓</text>
    </Svg>
  );
}

/** Lesson 4: overlapping circles for what is real and what the model picked. */
export function PrecisionRecallSketch() {
  return (
    <Svg viewBox="0 0 300 200" td={15} tp={22} label="Two overlapping circles. One holds the real drones and one holds what the model called a drone. The overlap is the ones it got right.">
      <circle cx="115" cy="100" r="68" />
      <circle cx="190" cy="100" r="68" />
      <path d="M152 44C176 62 176 138 152 156C128 138 128 62 152 44Z" fill="var(--mark)" fillOpacity="0.6" />
      <text x="40" y="190" className="t" fill="var(--ink)" stroke="none">real</text>
      <text x="206" y="190" className="t" fill="var(--ink)" stroke="none">picked</text>
    </Svg>
  );
}

/** Lesson 5: a smooth curve against the same curve in a few steps. */
export function QuantSteps() {
  return (
    <Svg viewBox="0 0 560 210" td={15} tp={24} label="A smooth rising curve on the left stands for full-size numbers. On the right the same curve is drawn as a staircase of a few steps, which stands for 8-bit integers.">
      <path d="M30 170H250M30 170V30M310 170H530M310 170V30" strokeWidth="1" />
      <path d="M30 160C90 150 130 90 160 70C190 52 230 40 250 38" />
      <path d="M310 160H350V132H390V100H430V70H470V52H510V40" />
      <circle cx="510" cy="40" r="4" fill="var(--mark)" />
      <text x="30" y="198" className="t" fill="var(--ink)" stroke="none">full-size numbers</text>
      <text x="310" y="198" className="t" fill="var(--ink)" stroke="none">8-bit integers</text>
    </Svg>
  );
}

/** Lesson 6: three kinds of data stacked inside one block of working memory. */
export function BudgetBlocks() {
  return (
    <Svg viewBox="0 0 300 220" td={15} tp={22} label="A tall outline stands for the chip's memory. Three blocks sit inside it: the model's weights, its working space and the camera frame. Some memory is left over at the top.">
      <rect x="70" y="14" width="160" height="190" rx="4" />
      <rect x="70" y="150" width="160" height="54" fill="var(--ink)" />
      <path d="M70 100H230" />
      <path d="M78 108L120 142M110 108L152 142M142 108L184 142M174 108L216 142" />
      <rect x="70" y="72" width="160" height="28" fill="var(--mark)" />
      <path d="M250 14V72M244 14H256M244 72H256" strokeWidth="1" />
      <text x="258" y="48" className="t" fill="var(--muted)" stroke="none">left</text>
    </Svg>
  );
}

/** Lesson 6: a timeline that is asleep most of the time with short awake pulses. */
export function SleepTimeline() {
  return (
    <Svg viewBox="0 0 560 150" td={15} tp={24} label="A timeline. A long low line stands for the camera asleep. Three short tall pulses stand for it waking, looking and going back to sleep.">
      <path d="M20 110H80V50H96V110H210V50H226V110H340V50H356V110H540" />
      <rect x="80" y="50" width="16" height="60" fill="var(--mark)" stroke="none" />
      <rect x="210" y="50" width="16" height="60" fill="var(--mark)" stroke="none" />
      <rect x="340" y="50" width="16" height="60" fill="var(--mark)" stroke="none" />
      <text x="20" y="138" className="t" fill="var(--ink)" stroke="none">asleep</text>
      <text x="76" y="36" className="t" fill="var(--ink)" stroke="none">awake</text>
    </Svg>
  );
}
