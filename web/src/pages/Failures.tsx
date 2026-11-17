import { Label, fmt } from '../components/Label';
import { evalTorch } from '../content/results';
import { OBSERVATIONS } from '../content/observations';

const FAILURE_KINDS = [
  { t: 'Tiny target', c: 'lilac', d: 'The object fills only a few dozen pixels. After the crop is enlarged to the model size it is a blur, and a blur could be a bird or a drone.', w: 'small' },
  { t: 'Busy background', c: 'mint', d: 'Trees, buildings or cloud edges in the crop look more like an object than the sky does.', w: 'bg' },
  { t: 'Look-alikes', c: 'butter', d: 'Airplanes and helicopters share a dark shape on sky with birds and drones. They are the hard negatives.', w: 'look' },
] as const;

function Glyph({ kind }: { kind: string }) {
  // Original abstract drawings. These are not dataset frames.
  return (
    <svg viewBox="0 0 120 80" width="120" height="80" role="img" aria-label={`Abstract drawing for ${kind}`}>
      <rect width="120" height="80" rx="16" fill="var(--bg)" />
      {kind === 'small' ? <circle cx="60" cy="40" r="3" fill="var(--ink)" /> : null}
      {kind === 'bg' ? (<><path d="M0 70 L20 45 L35 62 L55 38 L80 66 L100 50 L120 68 V80 H0Z" fill="var(--muted)" /><circle cx="64" cy="30" r="4" fill="var(--ink)" /></>) : null}
      {kind === 'look' ? (<><ellipse cx="38" cy="40" rx="20" ry="6" fill="var(--ink)" /><ellipse cx="86" cy="40" rx="12" ry="9" fill="var(--ink)" /><line x1="70" y1="30" x2="102" y2="30" stroke="var(--ink)" strokeWidth="3" /></>) : null}
    </svg>
  );
}

export function Failures() {
  const e = evalTorch;
  return (
    <>
      <h1>Failure gallery</h1>
      <p>
        This page deliberately shows <strong>no frames or crops</strong> from the dataset. The licence has not been
        confirmed, so it uses original drawings and numbers instead. The drawings are abstract and are not real examples.
      </p>
      <div className="tiles">
        {FAILURE_KINDS.map((f) => (
          <div key={f.t} className={`tile ${f.c}`}>
            <Glyph kind={f.w} />
            <h3>{f.t}</h3>
            <p>{f.d}</p>
          </div>
        ))}
      </div>

      <h2>How often each kind of crop is classified into its own class</h2>
      {e ? (
        <div className="card scroll">
          <table>
            <caption className="sr">Share of test crops of each subtype that were predicted as their own class</caption>
            <thead><tr><th>Crop subtype</th><th className="num">Crops</th><th className="num">Videos</th><th className="num">Correct</th><th className="num">95% interval (by video)</th></tr></thead>
            <tbody>
              {Object.entries(e.subtype_accuracy).map(([k, m]) => (
                <tr key={k}>
                  <td>{k === 'airplane' || k === 'helicopter' ? `${k} (counts as "neither")` : k === 'background' ? 'background (counts as "neither")' : k}</td>
                  <td className="num">{m.n_crops}</td><td className="num">{m.n_videos}</td><td className="num">{fmt(m.accuracy)}</td>
                  <td className="num">{fmt(m.ci95[0])} to {fmt(m.ci95[1])}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p><Label kind="measured (host CPU)" /> Test split only. Small sample, noisy.</p>
        </div>
      ) : <p>The evaluation has not been run yet.</p>}

      <h2>What the error analysis found</h2>
      {OBSERVATIONS.length === 0 ? (
        <p>The error analysis has not been written up yet.</p>
      ) : (
        <ol>
          {OBSERVATIONS.map((o) => (
            <li key={o.title}><strong>{o.title}.</strong> {o.what} <span className="muted">{o.why}</span></li>
          ))}
        </ol>
      )}
    </>
  );
}
