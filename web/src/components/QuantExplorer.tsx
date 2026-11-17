import { useState } from 'react';
import { benchMetric } from '../content/results';
import { Label } from './Label';

type Key = 'fp32_onnx' | 'int8_onnx';

/** Toggle between the float32 and the partly-int8 model, with this project's own measured numbers. */
export function QuantExplorer() {
  const [k, setK] = useState<Key>('int8_onnx');
  const m = (name: string) => benchMetric(k, name);
  const rows: [string, string, number | null | undefined, number][] = [
    ['Model size (KB)', 'size_kb', m('size_kb')?.value, 0],
    ['Test accuracy', 'test_accuracy', m('test_accuracy')?.value, 3],
    ['Test macro F1', 'test_macro_f1', m('test_macro_f1')?.value, 3],
    ['Bird recall', 'bird_recall', m('bird_recall')?.value, 3],
    ['Median latency on a laptop CPU (ms)', 'latency_ms_median', m('latency_ms_median')?.value, 2],
  ];
  if (!benchMetric('fp32_onnx', 'size_kb')) return <p className="sm">The export and bench have not been run yet.</p>;
  return (
    <div className="card pad">
      <div className="toggle" role="group" aria-label="Choose a model" style={{ maxWidth: 420 }}>
        <button aria-pressed={k === 'fp32_onnx'} onClick={() => setK('fp32_onnx')}>float32</button>
        <button aria-pressed={k === 'int8_onnx'} onClick={() => setK('int8_onnx')}>partly int8</button>
      </div>
      <div className="scroll">
        <table style={{ marginTop: 12 }}>
          <caption className="sr">Measured numbers for the selected model</caption>
          <thead><tr><th>Measure</th><th className="n">Value</th></tr></thead>
          <tbody>
            {rows.map(([name, , v, d]) => (
              <tr key={name}><td>{name}</td><td className="n">{v == null ? 'not run yet' : d === 0 ? Math.round(v).toLocaleString('en-AU') : v.toFixed(d)}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="cap"><Label kind="measured (host CPU)" /> One thread, batch 1, ONNX Runtime. KB = 1024 bytes. Nothing was measured on a board.</p>
    </div>
  );
}
