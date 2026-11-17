import { useState } from 'react';
import { evalTorch } from '../content/results';
import { Label } from './Label';

/** Move the bird-alert threshold along the real precision-recall points of the test split. */
export function ThresholdSlider() {
  const curve = evalTorch?.threshold.pr_curve_test;
  const [i, setI] = useState(0);
  if (!curve || curve.length === 0) return <p className="sm">The evaluation has not been run yet.</p>;
  const pts = [...curve].sort((a, b) => b.threshold - a.threshold);
  const p = pts[Math.min(i, pts.length - 1)];
  return (
    <div className="card pad">
      <label htmlFor="thr" style={{ marginTop: 0 }}>Bird alert threshold: <span className="mono">{p.threshold.toFixed(4)}</span></label>
      <input id="thr" type="range" min={0} max={pts.length - 1} value={i} onChange={(e) => setI(Number(e.target.value))} />
      <div className="readouts" style={{ maxWidth: 420, marginTop: 12 }}>
        <div><span className="k">precision</span>{p.precision.toFixed(3)}</div>
        <div><span className="k">recall</span>{p.recall.toFixed(3)}</div>
      </div>
      <p className="cap" aria-live="polite">
        Test split, P(bird) at or above the threshold raises an alert. A stricter threshold gives fewer false alarms and misses more birds.{' '}
        <Label kind="measured (host CPU)" />
      </p>
    </div>
  );
}
