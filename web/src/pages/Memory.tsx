import { useMemo, useState } from 'react';
import { Label } from '../components/Label';
import { benchMetric } from '../content/results';

const RAM_OPTIONS_KB = [256, 512, 1024, 2048, 4096];
const FRAMES = [
  { name: '96 x 96, 1 byte per pixel (grey)', w: 96, h: 96, b: 1 },
  { name: '160 x 120, 2 bytes per pixel (RGB565)', w: 160, h: 120, b: 2 },
  { name: '224 x 224, 3 bytes per pixel (RGB888)', w: 224, h: 224, b: 3 },
  { name: '640 x 512, 3 bytes per pixel (RGB888)', w: 640, h: 512, b: 3 },
];

export function Memory() {
  const weightsBench = benchMetric('int8_onnx', 'size_kb');
  const arenaBench = benchMetric('memory_estimate', 'activation_lower_bound_kb');
  const [ram, setRam] = useState(1024);
  const [frameIdx, setFrameIdx] = useState(1);
  const [weightsInRam, setWeightsInRam] = useState(false);
  const [weights, setWeights] = useState(Math.round(weightsBench?.value ?? 1024));
  const [arena, setArena] = useState(Math.round(arenaBench?.value ?? 256));
  const [buffers, setBuffers] = useState(1);

  const f = FRAMES[frameIdx];
  const frameKb = useMemo(() => (f.w * f.h * f.b * buffers) / 1024, [f, buffers]);
  const segs = [
    { name: 'Model weights (in RAM)', kb: weightsInRam ? weights : 0, color: 'var(--train)' },
    { name: 'Tensor arena', kb: arena, color: 'var(--val)' },
    { name: `Frame buffer x${buffers}`, kb: frameKb, color: 'var(--test)' },
  ];
  const used = segs.reduce((a, s) => a + s.kb, 0);
  const over = used > ram;

  return (
    <>
      <h1>Memory budget</h1>
      <p>
        Drag the sliders to see how three things compete for working memory. The RAM sizes are illustrative, not a
        specific board. Everything here is <Label kind="estimated" detail="arithmetic from the assumptions below, calculated on this page" /> and{' '}
        <Label kind="not measured on hardware" />.
      </p>
      <div className="card">
        <div className="bar" role="img" aria-label={`Memory use ${used.toFixed(0)} KB of ${ram} KB. ${segs.map((s) => `${s.name} ${s.kb.toFixed(0)} KB`).join(', ')}.`}>
          {segs.map((s) => (
            <div key={s.name} className="seg" style={{ width: `${Math.min(100, (s.kb / Math.max(ram, used)) * 100)}%`, background: s.color }}>
              {s.kb / Math.max(ram, used) > 0.12 ? `${s.kb.toFixed(0)} KB` : ''}
            </div>
          ))}
        </div>
        <div className="legend">
          {segs.map((s) => <span key={s.name}><i style={{ background: s.color }} />{s.name}: {s.kb.toFixed(0)} KB</span>)}
        </div>
        <p aria-live="polite">
          <strong>{used.toFixed(0)} KB used of {ram} KB</strong> ({((used / ram) * 100).toFixed(0)}%).{' '}
          {over ? <strong style={{ color: 'var(--danger)' }}>Over budget by {(used - ram).toFixed(0)} KB: this combination does not fit.</strong> : `${(ram - used).toFixed(0)} KB left for everything else (program stack, drivers, your own code).`}
        </p>
      </div>
      <div className="card">
        <label htmlFor="ram">Illustrative RAM size</label>
        <select id="ram" value={ram} onChange={(e) => setRam(Number(e.target.value))}>
          {RAM_OPTIONS_KB.map((k) => <option key={k} value={k}>{k >= 1024 ? `${k / 1024} MB` : `${k} KB`}</option>)}
        </select>
        <label htmlFor="frame">Camera frame format</label>
        <select id="frame" value={frameIdx} onChange={(e) => setFrameIdx(Number(e.target.value))}>
          {FRAMES.map((x, k) => <option key={x.name} value={k}>{x.name}</option>)}
        </select>
        <label htmlFor="bufs">Frame buffers kept at once: {buffers}</label>
        <input id="bufs" type="range" min={1} max={3} value={buffers} onChange={(e) => setBuffers(Number(e.target.value))} />
        <label htmlFor="arena">Tensor arena: {arena} KB</label>
        <input id="arena" type="range" min={16} max={2048} step={16} value={arena} onChange={(e) => setArena(Number(e.target.value))} />
        <label htmlFor="weights">Model weights: {weights} KB</label>
        <input id="weights" type="range" min={16} max={4096} step={16} value={weights} onChange={(e) => setWeights(Number(e.target.value))} />
        <label className="row" style={{ marginTop: 12 }}>
          <input type="checkbox" checked={weightsInRam} onChange={(e) => setWeightsInRam(e.target.checked)} /> Count the weights as RAM
        </label>
      </div>
      <h2>Assumptions</h2>
      <ul>
        <li>Frame buffer = width x height x bytes per pixel x number of buffers. This is exact arithmetic for the format chosen.</li>
        <li>
          Weights default to this project's int8 model size{' '}
          {weightsBench ? <>({weightsBench.value?.toFixed(1)} KB <Label kind="measured (host CPU)" />)</> : '(not run yet, so a placeholder you can change)'}.
          Many microcontrollers keep weights in read-only storage, not RAM, so the box above is off by default. That is a general
          statement, not a fact about any one board.
        </li>
        <li>
          The tensor arena default is{' '}
          {arenaBench ? <>a lower bound of {arenaBench.value?.toFixed(0)} KB <Label kind="estimated" detail="ONNX shape inference, largest single-layer input plus output at int8" /></> : 'a placeholder you can change (no estimate has been run)'}.
          A real arena also holds values that must live across several layers, so the true need is higher than a single-layer bound. A runtime reports the exact figure; this project did not run one on a board.
        </li>
        <li>The RAM sizes are round numbers chosen for illustration.</li>
      </ul>
    </>
  );
}
