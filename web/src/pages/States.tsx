import { useEffect, useState } from 'react';
import { Label } from '../components/Label';
import { modelUrl } from '../lib/ort';

interface Row { t_ms: number; state: string; event: string; score: number; battery_pct: number; tick: number; fault: number }
interface Trace {
  label: string;
  note: string;
  trace: string;
  config: Record<string, number>;
  transitions: { from: string; to: string; label: string }[];
  timeline: Row[];
}

const NODES: Record<string, [number, number]> = {
  idle: [110, 110], capture: [330, 50], infer: [550, 110], alert: [550, 250], 'low-power': [110, 250], recovery: [330, 330],
};

export function States() {
  const [trace, setTrace] = useState<Trace | null>(null);
  const [err, setErr] = useState('');
  const [i, setI] = useState(0);

  useEffect(() => {
    fetch(modelUrl('trace.json'))
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setTrace)
      .catch((e) => setErr(String(e)));
  }, []);

  if (err) return <><h1>State machine</h1><p role="alert">Could not load the trace: {err}</p></>;
  if (!trace) return <><h1>State machine</h1><p>Loading the trace...</p></>;

  const row = trace.timeline[i];
  const prev = i > 0 ? trace.timeline[i - 1].state : row.state;
  const lastEdge = prev !== row.state ? `${prev} to ${row.state}` : null;

  return (
    <>
      <h1>State machine</h1>
      <p>
        This is the C++ power and state logic in <code>firmware/</code>, replayed from a scripted trace
        (<code>{trace.trace}</code>) <Label kind="simulated" />. There is no clock, no random number and no hardware in
        it: every transition comes from the timestamps, scores, battery levels, watchdog ticks and faults in the trace.
        The durations are configuration values of the logic, not measurements of any device (
        <Label kind="not measured on hardware" />).
      </p>
      <div className="card">
        <svg viewBox="0 0 660 380" width="100%" role="img" aria-labelledby="sm-t sm-d">
          <title id="sm-t">State diagram</title>
          <desc id="sm-d">Six states: idle, capture, infer, alert, low-power and recovery, with the allowed transitions between them. The current state in the replay is highlighted.</desc>
          <defs>
            <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">
              <path d="M0 1 L10 5 L0 9 Z" fill="var(--muted)" />
            </marker>
            <marker id="arr-hot" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">
              <path d="M0 1 L10 5 L0 9 Z" fill="var(--accent)" />
            </marker>
          </defs>
          {trace.transitions.map((t, k) => {
            const [x1, y1] = NODES[t.from];
            const [x2, y2] = NODES[t.to];
            const dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy);
            const ox = (dx / len) * 52, oy = (dy / len) * 30;
            const reverse = trace.transitions.some((u) => u.from === t.to && u.to === t.from);
            const off = reverse ? 8 : 0;
            const nx = (-dy / len) * off, ny = (dx / len) * off;
            const hot = lastEdge === `${t.from} to ${t.to}`;
            return (
              <line key={k} x1={x1 + ox * 0.9 + nx} y1={y1 + oy * 0.9 + ny} x2={x2 - ox * 0.9 + nx} y2={y2 - oy * 0.9 + ny}
                stroke={hot ? 'var(--accent)' : 'var(--muted)'} strokeWidth={hot ? 4 : 1.5} markerEnd={hot ? 'url(#arr-hot)' : 'url(#arr)'} opacity={hot ? 1 : 0.7}>
                <title>{`${t.from} to ${t.to}: ${t.label}`}</title>
              </line>
            );
          })}
          {Object.entries(NODES).map(([name, [x, y]]) => {
            const on = row.state === name;
            return (
              <g key={name}>
                <rect x={x - 52} y={y - 24} width={104} height={48} rx={22} fill={on ? 'var(--train)' : 'var(--lilac)'} stroke={on ? 'var(--accent)' : 'none'} strokeWidth={3} />
                <text x={x} y={y + 5} textAnchor="middle" fontSize="14" fontWeight={on ? 700 : 400} fill={on ? 'var(--onsplit)' : 'var(--ink)'}>{name}</text>
              </g>
            );
          })}
        </svg>
        <label htmlFor="step">Row {i + 1} of {trace.timeline.length}</label>
        <input id="step" type="range" min={0} max={trace.timeline.length - 1} value={i} onChange={(e) => setI(Number(e.target.value))} />
        <div className="row">
          <button onClick={() => setI(Math.max(0, i - 1))} disabled={i === 0}>Previous</button>
          <button onClick={() => setI(Math.min(trace.timeline.length - 1, i + 1))} disabled={i === trace.timeline.length - 1}>Next</button>
        </div>
        <p aria-live="polite">
          At <strong>{row.t_ms} ms</strong> the state is <strong>{row.state}</strong>
          {lastEdge ? ` (changed: ${lastEdge})` : ''}. Event: {row.event}. Input: score {row.score < 0 ? 'none' : row.score}, battery {row.battery_pct}%, watchdog tick {row.tick ? 'yes' : 'no'}, fault {row.fault ? 'yes' : 'no'}.
        </p>
      </div>
      <details className="card">
        <summary>All {trace.transitions.length} allowed transitions, as a table</summary>
        <div className="scroll">
          <table>
            <caption className="sr">Allowed state transitions</caption>
            <thead><tr><th>From</th><th>To</th><th>When</th></tr></thead>
            <tbody>
              {trace.transitions.map((t, k) => (<tr key={k}><td>{t.from}</td><td>{t.to}</td><td>{t.label}</td></tr>))}
            </tbody>
          </table>
        </div>
      </details>
      <h2>Rules, in plain words</h2>
      <ul>
        <li>A score of at least {trace.config.alert_threshold} after inference raises an alert. The threshold is a setting; this page does not claim it is the right one for any real device.</li>
        <li>A fault, or no watchdog tick for longer than {trace.config.watchdog_timeout_ms} ms, sends any state to recovery. Recovery holds for {trace.config.recovery_ms} ms, then restarts.</li>
        <li>At {trace.config.low_battery_pct}% battery or below, idle goes to low-power. It stays there until {trace.config.resume_battery_pct}% (a gap, so it does not flicker).</li>
        <li>A score that arrives while the node is busy or in low-power is ignored.</li>
      </ul>
      <p className="muted">The unit tests cover every transition in this diagram and the boundaries of each rule. They do not cover real timing, interrupts, sensor noise, or a clock that wraps around.</p>
    </>
  );
}
