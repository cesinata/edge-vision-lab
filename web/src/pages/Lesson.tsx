import type { ReactNode } from 'react';
import { FailureGallery } from '../components/FailureGallery';
import { Label, fmt } from '../components/Label';
import { MemoryBudget } from '../components/MemoryBudget';
import { QuantExplorer } from '../components/QuantExplorer';
import { StateViewer } from '../components/StateViewer';
import { ThresholdSlider } from '../components/ThresholdSlider';
import { COPY } from '../content/copy';
import { TERMS } from '../content/glossary';
import { evalTorch, splitSummary } from '../content/results';
import {
  BudgetBlocks, ConfusionGrid, CropDrawing, EdgeVsCloud, LeakDrawing, PipelineStrip, PrecisionRecallSketch, QuantSteps, SleepTimeline,
} from '../illustrations/LessonDrawings';
import { LessonIcon } from '../illustrations/LessonIcons';
import { SplitDiagram } from '../illustrations/SplitDiagram';

const term = (name: string) => TERMS.find(([t]) => t === name)?.[1] ?? '';

function Fig({ children, narrow }: { children: ReactNode; narrow?: boolean }) {
  return <div className={`card gridbg pad fig${narrow ? ' narrow' : ''}`}>{children}</div>;
}

function L1() {
  return (
    <>
      <p>{COPY.about.items[1].a}</p>
      <Fig><EdgeVsCloud /></Fig>
      <p className="cap">Left: the answer travels to the cloud and back. Right: it stays on the chip.</p>
    </>
  );
}

function L2() {
  return (
    <>
      <p>{COPY.pipeline.lead}</p>
      <PipelineStrip titles={COPY.pipeline.steps.map((s) => s.title)} />
      <div className="scroll card pad">
        <table>
          <caption className="sr">The six steps</caption>
          <thead><tr><th>Step</th><th>Title</th><th>One line</th></tr></thead>
          <tbody>{COPY.pipeline.steps.map((s) => <tr key={s.n}><td className="mono">{s.n}</td><td>{s.title}</td><td>{s.line}</td></tr>)}</tbody>
        </table>
      </div>
      <h2>The model sees crops</h2>
      <p>
        The task is image classification on crops with three classes: bird, drone and neither. It is not object detection: the model
        sees one cropped image and names its class.
      </p>
      <Fig><CropDrawing /></Fig>
    </>
  );
}

function L3() {
  const s = splitSummary;
  return (
    <>
      {COPY.split.paragraphs.map((p) => <p key={p}>{p}</p>)}
      <Fig><SplitDiagram id="lesson-split" /></Fig>
      <p className="cap">{COPY.split.caption}</p>
      <Fig><LeakDrawing /></Fig>
      {s ? (
        <>
          <h2>What the scenes looked like here</h2>
          <p>
            Grouping the clips by how similar their frames look gave {s.n_clusters} scene clusters from {s.n_videos} videos <Label kind="measured (host CPU)" />.
            The {s.videos_per_class.DRONE} drone videos fall into only {s.clusters_touched_per_class.DRONE} clusters, while the {s.videos_per_class.BIRD} bird videos fall into {s.clusters_touched_per_class.BIRD}.
            So drones were filmed in a few places and birds in many, and a model can pick up the place instead of the object.
          </p>
          <div className="card pad scroll">
            <table>
              <caption className="sr">Videos per split, with scene clusters in brackets</caption>
              <thead><tr><th>Class</th><th className="n">Train</th><th className="n">Validation</th><th className="n">Test</th></tr></thead>
              <tbody>
                {['BIRD', 'DRONE', 'AIRPLANE', 'HELICOPTER'].map((c) => (
                  <tr key={c}>
                    <td>{c.toLowerCase()}</td>
                    {['train', 'val', 'test'].map((k) => <td key={k} className="n">{s.videos_per_class_per_split[c][k]} ({s.clusters_per_class_per_split[c][k]})</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="cap">Videos per split, scene clusters in brackets. <Label kind="measured (host CPU)" /></p>
          </div>
        </>
      ) : null}
    </>
  );
}

function L4() {
  const e = evalTorch;
  return (
    <>
      <dl>
        {['Precision', 'Recall', 'F1', 'Confusion matrix', 'Bootstrap interval'].map((t) => <div key={t}><dt>{t}</dt><dd className="sm">{term(t)}</dd></div>)}
      </dl>
      <div className="cols c2">
        <Fig narrow><ConfusionGrid /></Fig>
        <Fig narrow><PrecisionRecallSketch /></Fig>
      </div>
      {e ? (
        <>
          <h2>This project's results</h2>
          <div className="card pad scroll">
            <table>
              <caption className="sr">Per-class results on the test split</caption>
              <thead><tr><th>Class</th><th className="n">Crops</th><th className="n">Precision</th><th className="n">Recall</th><th className="n">F1</th></tr></thead>
              <tbody>{Object.entries(e.per_class).map(([c, m]) => <tr key={c}><td>{c}</td><td className="n">{m.support}</td><td className="n">{fmt(m.precision)}</td><td className="n">{fmt(m.recall)}</td><td className="n">{fmt(m.f1)}</td></tr>)}</tbody>
            </table>
            <p className="cap">{e.n_crops} crops from {e.n_videos} test videos. Macro F1 {fmt(e.macro_f1)} (95% interval {fmt(e.macro_f1_ci95[0])} to {fmt(e.macro_f1_ci95[1])}, resampled by video). <Label kind="measured (host CPU)" /> The test set is small and noisy.</p>
          </div>
          <div className="card pad scroll" style={{ marginTop: 16 }}>
            <table>
              <caption className="sr">Confusion matrix on the test split</caption>
              <thead><tr><th>Real class</th>{e.confusion_matrix.cols_pred.map((c) => <th key={c} className="n">said {c}</th>)}</tr></thead>
              <tbody>{e.confusion_matrix.values.map((row, i) => <tr key={i}><td>{e.confusion_matrix.rows_true[i]}</td>{row.map((v, j) => <td key={j} className="n" style={i === j ? { background: 'var(--panel)', fontWeight: 600 } : undefined}>{v}</td>)}</tr>)}</tbody>
            </table>
            <p className="cap">Counts of test crops. The diagonal, in bold, is where the model agreed with the real class. <Label kind="measured (host CPU)" /></p>
          </div>
        </>
      ) : null}
      <h2>Move the threshold</h2>
      <ThresholdSlider />
      <h2>What goes wrong</h2>
      <FailureGallery />
    </>
  );
}

function L5() {
  return (
    <>
      <p>{term('Quantisation')}</p>
      <Fig><QuantSteps /></Fig>
      <h2>{COPY.results.items[1].title}</h2>
      <p>{COPY.results.items[1].text}</p>
      <QuantExplorer />
      <p className="sm" style={{ marginTop: 16 }}>
        Every plain setting that quantised all the convolutions lost most of the accuracy. Leaving the depthwise and squeeze-and-excite
        convolutions in full-size numbers recovered most of it. The bird alert of the shrunk model is still clearly worse, so the saving has a cost.
        All the settings tried are listed in <code>results/quantisation_search.json</code>.
      </p>
    </>
  );
}

function L6() {
  return (
    <>
      <dl>
        {['Tensor arena', 'Watchdog', 'State machine'].map((t) => <div key={t}><dt>{t}</dt><dd className="sm">{term(t)}</dd></div>)}
      </dl>
      <Fig narrow><BudgetBlocks /></Fig>
      <h2>Memory budget</h2>
      <MemoryBudget />
      <h2>Staying asleep</h2>
      <Fig><SleepTimeline /></Fig>
      <h2>The states</h2>
      <StateViewer />
    </>
  );
}

const BODIES = [L1, L2, L3, L4, L5, L6];

export function LessonPage({ n }: { n: number }) {
  const l = COPY.lessons.items[n - 1];
  const Body = BODIES[n - 1];
  return (
    <div className="wrap">
      <div className="crumbs"><a href="#/">Home</a> / <a href="#/lessons">{COPY.lessons.title}</a></div>
      <div className="lesson-head">
        <div className="big"><LessonIcon index={n - 1} size={128} /></div>
        <div>
          <div className="lbl">Lesson {l.n}</div>
          <h1>{l.title}</h1>
          <p className="ink2">{l.blurb}</p>
        </div>
      </div>
      <div className="stack"><Body /></div>
      <nav className="pager" aria-label="Lessons">
        {n > 1 ? <a className="btn secondary" href={`#/lesson/${n - 1}`}>← {COPY.lessons.items[n - 2].title}</a> : <span />}
        {n < 6 ? <a className="btn secondary" href={`#/lesson/${n + 1}`}>{COPY.lessons.items[n].title} →</a> : <a className="btn secondary" href="#/results">{COPY.results.title}</a>}
      </nav>
    </div>
  );
}
