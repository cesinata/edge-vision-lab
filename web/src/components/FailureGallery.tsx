import { Label, fmt } from './Label';
import { OBSERVATIONS } from '../content/observations';
import { evalTorch } from '../content/results';
import { Svg } from '../illustrations/Svg';

const KINDS = [
  { t: 'Tiny target', d: 'The object fills only a few dozen pixels. Enlarged to the model size it is a blur, and a blur could be a bird or a drone.' },
  { t: 'Busy background', d: 'Trees, buildings or cloud edges in the crop look more like an object than the sky does.' },
  { t: 'Look-alikes', d: 'Airplanes and helicopters share a dark shape on sky with birds and drones. They are the hard negatives.' },
];

function Glyph({ i }: { i: number }) {
  return (
    <Svg viewBox="0 0 120 80" width={120} height={80} label={`Abstract drawing: ${KINDS[i].t.toLowerCase()}`}>
      <rect x="1" y="1" width="118" height="78" rx="4" stroke="var(--rule)" />
      {i === 0 ? <circle cx="60" cy="40" r="3" fill="var(--mark)" /> : null}
      {i === 1 ? (<><path d="M2 70L24 46L40 62L60 36L86 66L104 50L118 66V78H2Z" /><circle cx="66" cy="26" r="4" fill="var(--mark)" /></>) : null}
      {i === 2 ? (<><ellipse cx="38" cy="40" rx="20" ry="6" /><ellipse cx="86" cy="40" rx="12" ry="9" /><path d="M70 30H102" /><circle cx="86" cy="40" r="2.5" fill="var(--mark)" /></>) : null}
    </Svg>
  );
}

/** What goes wrong, with no dataset frames: abstract drawings, the subtype table and the written observations. */
export function FailureGallery() {
  const e = evalTorch;
  return (
    <div className="stack">
      <p className="sm">This section shows <strong>no frames or crops</strong> from the dataset. The licence has not been confirmed, so it uses original drawings and numbers. The drawings are abstract, not real examples.</p>
      <div className="cols c3">
        {KINDS.map((k, i) => (
          <div key={k.t} className="card pad"><Glyph i={i} /><h3 style={{ marginTop: 8 }}>{k.t}</h3><p className="sm" style={{ margin: 0 }}>{k.d}</p></div>
        ))}
      </div>
      {e ? (
        <div className="card pad scroll">
          <table>
            <caption className="sr">Share of test crops of each subtype classified into their own class</caption>
            <thead><tr><th>Crop subtype</th><th className="n">Crops</th><th className="n">Videos</th><th className="n">Correct</th><th className="n">95% interval (by video)</th></tr></thead>
            <tbody>
              {Object.entries(e.subtype_accuracy).map(([k, m]) => (
                <tr key={k}>
                  <td>{k === 'airplane' || k === 'helicopter' || k === 'background' ? `${k} (counts as "neither")` : k}</td>
                  <td className="n">{m.n_crops}</td><td className="n">{m.n_videos}</td><td className="n">{fmt(m.accuracy)}</td>
                  <td className="n">{fmt(m.ci95[0])} to {fmt(m.ci95[1])}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="cap"><Label kind="measured (host CPU)" /> Test split only. Small sample, noisy.</p>
        </div>
      ) : <p className="sm">The evaluation has not been run yet.</p>}
      {OBSERVATIONS.length === 0 ? <p className="sm">The error analysis has not been written up yet.</p> : (
        <>
          <ol className="sm">
            {OBSERVATIONS.map((o) => <li key={o.title}><strong>{o.title}.</strong> {o.what} <span className="muted">{o.why}</span></li>)}
          </ol>
          <p className="cap">Every figure in this list comes from the test split. <Label kind="measured (host CPU)" /></p>
        </>
      )}
    </div>
  );
}
