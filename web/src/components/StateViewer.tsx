import { useEffect, useState } from 'react';
import { modelUrl } from '../lib/ort';
import { Label } from './Label';
import { Svg } from '../illustrations/Svg';

interface Row { t_ms: number; state: string; event: string; score: number; battery_pct: number; tick: number; fault: number }
interface Trace {
  trace: string;
  config: Record<string, number>;
  transitions: { from: string; to: string; label: string }[];
  timeline: Row[];
}

const NODES: Record<string, [number, number]> = {
  idle: [110, 110], capture: [330, 50], infer: [550, 110], alert: [550, 250], 'low-power': [110, 250], recovery: [330, 330],
};

/** The C++ state logic replayed from a scripted trace, drawn from the same transition table the tests use. */
export function StateViewer() {
  const [trace, setTrace] = useState<Trace | null>(null);
  const [err, setErr] = useState('');
  const [i, setI] = useState(0);

  useEffect(() => {
    fetch(modelUrl('trace.json'))
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setTrace)
      .catch((e) => setErr(String(e)));
  }, []);

  if (err) return <p role="alert">Could not load the trace: {err}</p>;
  if (!trace) return <p>Loading the trace...</p>;
  const row = trace.timeline[i];
  const prev = i > 0 ? trace.timeline[i - 1].state : row.state;
  const lastEdge = prev !== row.state ? `${prev} to ${row.state}` : null;

  return (
    <div className="stack">
      <p className="sm">
        This is the C++ power and state logic in <code>firmware/</code>, replayed from a scripted trace (<code>{trace.trace}</code>) <Label kind="simulated" />.
        There is no clock, no random number and no hardware in it: every move comes from the timestamps, scores, battery levels, watchdog ticks and faults in the trace.
        The durations are settings of the logic, not measurements of any device <Label kind="not measured on hardware" />.
      </p>
      <div className="card gridbg pad">
        <Svg viewBox="0 0 660 380" td={15} tp={24} label="State diagram: idle, capture, infer, alert, low-power and recovery, with the allowed moves between them. The current state in the replay is highlighted.">
          <defs>
            <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 1L10 5L0 9Z" fill="currentColor" stroke="none" /></marker>
          </defs>
          {trace.transitions.map((t, k) => {
            const [x1, y1] = NODES[t.from];
            const [x2, y2] = NODES[t.to];
            const dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy);
            const ox = (dx / len) * 52, oy = (dy / len) * 30;
            const both = trace.transitions.some((u) => u.from === t.to && u.to === t.from);
            const nx = both ? (-dy / len) * 8 : 0, ny = both ? (dx / len) * 8 : 0;
            const hot = lastEdge === `${t.from} to ${t.to}`;
            return (
              <line key={k} x1={x1 + ox * 0.9 + nx} y1={y1 + oy * 0.9 + ny} x2={x2 - ox * 0.9 + nx} y2={y2 - oy * 0.9 + ny}
                strokeWidth={hot ? 3.5 : 1.25} strokeDasharray={hot ? undefined : '1 0'} markerEnd="url(#arr)" opacity={hot ? 1 : 0.55}>
                <title>{`${t.from} to ${t.to}: ${t.label}`}</title>
              </line>
            );
          })}
          {Object.entries(NODES).map(([name, [x, y]]) => {
            const on = row.state === name;
            return (
              <g key={name}>
                <rect x={x - 54} y={y - 24} width={108} height={48} rx={5} fill={on ? 'var(--mark)' : 'var(--bg)'} strokeWidth={on ? 3 : 1.5} />
                <text x={x} y={y + 5} textAnchor="middle" className="t" fill={on ? '#03234b' : 'var(--ink)'} stroke="none">{name}</text>
              </g>
            );
          })}
        </Svg>
      </div>
      <label htmlFor="step">Row {i + 1} of {trace.timeline.length}</label>
      <input id="step" type="range" min={0} max={trace.timeline.length - 1} value={i} onChange={(e) => setI(Number(e.target.value))} />
      <div className="row">
        <button className="btn secondary" onClick={() => setI(Math.max(0, i - 1))} disabled={i === 0}>Previous</button>
        <button className="btn secondary" onClick={() => setI(Math.min(trace.timeline.length - 1, i + 1))} disabled={i === trace.timeline.length - 1}>Next</button>
      </div>
      <p className="sm" aria-live="polite">
        At <strong>{row.t_ms} ms</strong> the state is <strong>{row.state}</strong>{lastEdge ? ` (changed: ${lastEdge})` : ''}. Event: {row.event}. Input: score {row.score < 0 ? 'none' : row.score}, battery {row.battery_pct}%, watchdog tick {row.tick ? 'yes' : 'no'}, fault {row.fault ? 'yes' : 'no'}.
      </p>
      <details className="card pad">
        <summary>All {trace.transitions.length} allowed moves, as a table</summary>
        <div className="scroll">
          <table>
            <caption className="sr">Allowed state transitions</caption>
            <thead><tr><th>From</th><th>To</th><th>When</th></tr></thead>
            <tbody>{trace.transitions.map((t, k) => (<tr key={k}><td>{t.from}</td><td>{t.to}</td><td>{t.label}</td></tr>))}</tbody>
          </table>
        </div>
      </details>
      <ul className="sm">
        <li>A score of at least {trace.config.alert_threshold} after inference raises an alert. That threshold is a setting, not a claim about any real device.</li>
        <li>A fault, or no watchdog tick for longer than {trace.config.watchdog_timeout_ms} ms, sends any state to recovery. Recovery holds for {trace.config.recovery_ms} ms, then restarts.</li>
        <li>At {trace.config.low_battery_pct}% battery or below, idle goes to low-power. It stays there until {trace.config.resume_battery_pct}% so it does not flicker.</li>
        <li>A score that arrives while the node is busy or in low-power is ignored.</li>
      </ul>
      <p className="cap">The unit tests cover every move in this diagram and the edges of each rule. They do not cover real timing, interrupts, sensor noise or a clock that wraps around.</p>
    </div>
  );
}
