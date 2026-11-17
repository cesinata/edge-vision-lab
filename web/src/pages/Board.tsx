import { useState } from 'react';
import { Label } from '../components/Label';

interface Part { id: string; name: string; x: number; y: number; w: number; h: number; tile: string; short: string; body: string }

const PARTS: Part[] = [
  { id: 'camera', name: 'Camera', x: 20, y: 30, w: 160, h: 80, tile: 'var(--lilac)', short: 'sends frames',
    body: 'The image sensor and its lens. It produces a stream of frames. Resolution and frame rate decide how much data arrives and how much memory a single frame needs.' },
  { id: 'accel', name: 'Accelerator', x: 20, y: 170, w: 160, h: 80, tile: 'var(--butter)', short: 'optional',
    body: 'Some boards have a block built to run neural-network layers faster than the main core. It is optional. A model must be converted so the accelerator can run it, and this project never did that.' },
  { id: 'mcu', name: 'Microcontroller', x: 260, y: 30, w: 160, h: 220, tile: 'var(--mint)', short: 'runs the logic',
    body: 'The main core. It sets up the camera, prepares the image, runs the model if there is no accelerator, applies the decision rules (the state machine on the previous page) and talks to the outside.' },
  { id: 'host', name: 'Host link', x: 500, y: 30, w: 160, h: 80, tile: 'var(--butter)', short: 'results out',
    body: 'A serial, USB or radio link that sends results or alerts to another device. Sending data costs energy and time too, so many designs send a small result instead of the image.' },
  { id: 'mem', name: 'Memory', x: 500, y: 170, w: 160, h: 80, tile: 'var(--lilac)', short: 'weights, buffers',
    body: 'Two kinds matter here. Storage that keeps the program and the model weights. Working memory for the camera frame, the intermediate values of the model (often called the tensor arena) and the program stack. Working memory is usually the tighter limit. See the Memory budget page.' },
];

const STEPS: { parts: string[]; text: string }[] = [
  { parts: ['camera'], text: 'The camera captures a frame.' },
  { parts: ['camera', 'mem'], text: 'The frame is written into a buffer in memory.' },
  { parts: ['mcu', 'mem'], text: 'The microcontroller crops and resizes it to the model input size.' },
  { parts: ['mcu', 'accel', 'mem'], text: 'The model runs, on the main core or on an accelerator if there is one. Intermediate values live in the tensor arena.' },
  { parts: ['mcu'], text: 'The decision rules turn the scores into an action.' },
  { parts: ['mcu', 'host'], text: 'A short result goes out over the host link.' },
];

export function Board() {
  const [sel, setSel] = useState<string>('mcu');
  const [view, setView] = useState<'blocks' | 'path'>('blocks');
  const [step, setStep] = useState(0);
  const part = PARTS.find((p) => p.id === sel)!;
  const lit = view === 'path' ? STEPS[step].parts : [sel];

  return (
    <>
      <h1>Board explainer</h1>
      <p>
        A generic microcontroller vision board, drawn from scratch for this site. It is not any specific product, and
        nothing on this page was measured on one <Label kind="not measured on hardware" />. Select a block (mouse, touch
        or keyboard) to read what it does.
      </p>
      <div className="row" role="group" aria-label="View">
        <button className={view === 'blocks' ? 'primary' : ''} aria-pressed={view === 'blocks'} onClick={() => setView('blocks')}>Blocks</button>
        <button className={view === 'path' ? 'primary' : ''} aria-pressed={view === 'path'} onClick={() => setView('path')}>Anatomy: follow one frame</button>
      </div>
      <div className="card board">
        <svg viewBox="0 0 680 280" width="100%" role="group" aria-labelledby="bd-t bd-d">
          <title id="bd-t">Generic vision board</title>
          <desc id="bd-d">Five blocks: camera, accelerator, microcontroller, host link and memory. The camera, the accelerator, the host link and memory each connect to the microcontroller.</desc>
          {[[180, 70, 260, 70], [180, 210, 260, 210], [420, 70, 500, 70], [420, 210, 500, 210]].map(([x1, y1, x2, y2], k) => (
            <g key={k}>
              <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--muted)" strokeWidth={3} strokeLinecap="round" />
              <circle cx={x1} cy={y1} r={5} fill="var(--ink)" /><circle cx={x2} cy={y2} r={5} fill="var(--ink)" />
            </g>
          ))}
          {PARTS.map((p) => {
            const on = lit.includes(p.id);
            return (
              <g key={p.id} className="part" role="button" tabIndex={0} aria-pressed={sel === p.id} aria-label={`${p.name}: ${p.short}`}
                onClick={() => setSel(p.id)} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setSel(p.id); } }} style={{ cursor: 'pointer' }}>
                <rect x={p.x} y={p.y} width={p.w} height={p.h} rx={22} fill={p.tile} stroke={on ? 'var(--accent)' : 'none'} strokeWidth={4} />
                <text x={p.x + 16} y={p.y + 34} fontSize="15" fontWeight="700" fill="var(--ink)">{p.name}</text>
                <text x={p.x + 16} y={p.y + 56} fontSize="12" fill="var(--ink)">{p.short}</text>
              </g>
            );
          })}
        </svg>
        {view === 'blocks' ? (
          <div aria-live="polite">
            <h2 style={{ marginTop: 8 }}>{part.name}</h2>
            <p>{part.body}</p>
          </div>
        ) : (
          <div aria-live="polite">
            <h2 style={{ marginTop: 8 }}>Step {step + 1} of {STEPS.length}</h2>
            <p>{STEPS[step].text}</p>
            <div className="row">
              <button onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}>Previous</button>
              <button onClick={() => setStep(Math.min(STEPS.length - 1, step + 1))} disabled={step === STEPS.length - 1}>Next</button>
            </div>
          </div>
        )}
      </div>
      <p className="muted">General description only. Details such as where weights are stored, whether an accelerator exists, and how much memory there is differ between boards and are not specified here.</p>
    </>
  );
}
