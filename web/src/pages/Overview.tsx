import { Label, fmt } from '../components/Label';
import { benchMetric, evalTorch } from '../content/results';

const STEPS = [
  { t: 'Data', c: 'lilac', d: 'Labelled video clips from a public drone-detection dataset. Boxes become small square crops.' },
  { t: 'Split', c: 'mint', d: 'Whole scenes go to train, validation or test, because many clips share a background.' },
  { t: 'Train', c: 'butter', d: 'MobileNetV3-Small, fine-tuned on a laptop CPU from ImageNet starting weights.' },
  { t: 'Evaluate', c: 'lilac', d: 'Test split only. Intervals are resampled by video, and the test set is small.' },
  { t: 'Quantise', c: 'mint', d: 'Export to ONNX, then int8. Compare size and accuracy before and after.' },
  { t: 'Firmware', c: 'butter', d: 'C++ state and power logic, run on scripted traces and unit-tested on a laptop.' },
];

export function Overview() {
  const e = evalTorch;
  const size32 = benchMetric('fp32_onnx', 'size_kb');
  const size8 = benchMetric('int8_onnx', 'size_kb');
  return (
    <>
      <h1>Train a small classifier, quantise it, measure it, and test the logic on a laptop</h1>
      <p>
        The task is image classification on crops with three classes: <strong>bird</strong>, <strong>drone</strong>{' '}
        and <strong>neither</strong>. It is not object detection: the model sees one cropped image and names its class.
        No microcontroller board was used. Everything about a board on this site is a generic explanation, and any
        number about one is labelled <Label kind="not measured on hardware" />.
      </p>
      <div className="notice warn" role="note">
        <strong>Model not published yet.</strong> The classifier was trained on a dataset whose licence has not been
        confirmed in writing by its authors, so no weights, frames or crops appear on this site. The demo page uses a
        different, general-purpose detector from another project, and says so.
      </div>

      <h2>The pipeline</h2>
      <div className="tiles">
        {STEPS.map((s, i) => (
          <div key={s.t} className={`tile ${s.c}`}>
            <h3>{i + 1}. {s.t}</h3>
            <p>{s.d}</p>
          </div>
        ))}
      </div>

      <h2>Results so far</h2>
      {e ? (
        <div className="card">
          <p>
            Test split: {e.n_crops} crops from {e.n_videos} videos. Macro F1 {fmt(e.macro_f1)} (95% interval{' '}
            {fmt(e.macro_f1_ci95[0])} to {fmt(e.macro_f1_ci95[1])}, resampled by video) <Label kind="measured (host CPU)" />
          </p>
          <div className="scroll">
            <table>
              <caption className="sr">Per-class results on the test split</caption>
              <thead><tr><th>Class</th><th className="num">Crops</th><th className="num">Precision</th><th className="num">Recall</th><th className="num">F1</th></tr></thead>
              <tbody>
                {Object.entries(e.per_class).map(([c, m]) => (
                  <tr key={c}>
                    <td>{c}</td><td className="num">{m.support}</td>
                    <td className="num">{fmt(m.precision)}</td><td className="num">{fmt(m.recall)}</td><td className="num">{fmt(m.f1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="muted">The test set is small and noisy, and the drone test videos come from very few scenes. Treat these as a rough guide, not a benchmark. See the Failure gallery for what goes wrong.</p>
        </div>
      ) : (
        <p>The evaluation has not been run yet.</p>
      )}

      <h2>Model size</h2>
      <div className="card">
        <table>
          <caption className="sr">Model size before and after int8 quantisation</caption>
          <thead><tr><th>Model</th><th className="num">Size</th><th>Label</th></tr></thead>
          <tbody>
            <tr><td>float32 ONNX</td><td className="num">{size32 ? `${fmt(size32.value, 1)} KB` : 'not run yet'}</td><td>{size32 ? <Label kind="measured (host CPU)" /> : null}</td></tr>
            <tr><td>int8 ONNX</td><td className="num">{size8 ? `${fmt(size8.value, 1)} KB` : 'not run yet'}</td><td>{size8 ? <Label kind="measured (host CPU)" /> : null}</td></tr>
          </tbody>
        </table>
      </div>

      <h2>What this does not do</h2>
      <ul>
        <li>It was never run on a microcontroller. There is no on-device latency, frame rate, power or accelerator figure here.</li>
        <li>It does not find objects in a scene. It classifies a crop.</li>
        <li>It has not been tested on scenes unlike the training footage. The footage is daylight only, within about 200 m, from one region.</li>
      </ul>
    </>
  );
}
