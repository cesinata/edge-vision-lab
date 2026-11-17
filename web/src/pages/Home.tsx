import { useState } from 'react';
import { DemoPanel } from '../components/DemoPanel';
import { Label, fmt } from '../components/Label';
import { COPY } from '../content/copy';
import { benchMetric, evalTorch } from '../content/results';
import { BirdDroneIcon, ChipLaptopIcon, RulerCheckIcon, SixBoxesIcon } from '../illustrations/AboutIcons';
import { BoardAnatomy } from '../illustrations/BoardAnatomy';
import { HeroScene } from '../illustrations/HeroScene';
import { LessonIcon } from '../illustrations/LessonIcons';
import { PIPELINE_ICONS } from '../illustrations/PipelineIcons';
import { SketchRecall, SketchScenes, SketchShrink } from '../illustrations/ResultSketches';
import { SplitDiagram } from '../illustrations/SplitDiagram';

const ABOUT_ICONS = [BirdDroneIcon, ChipLaptopIcon, SixBoxesIcon, RulerCheckIcon];
const SKETCHES = [SketchRecall, SketchShrink, SketchScenes];

function Hero() {
  const [pre, post] = COPY.hero.headline.split('bird');
  return (
    <div className="hero gridbg">
      <div className="wrap">
        <div className="copy">
          <div className="lbl">Fig. 0 · {COPY.siteName}</div>
          <h1>{pre}<span className="hl">bird</span>{post}</h1>
          <p>{COPY.hero.intro}</p>
          <div className="row">
            <a className="btn primary" href="#/demo">{COPY.hero.buttons[0]}</a>
            <a className="btn secondary" href="#/lessons">{COPY.hero.buttons[1]}</a>
          </div>
        </div>
        <div className="art"><HeroScene /></div>
      </div>
    </div>
  );
}

function About() {
  return (
    <section className="block wrap" aria-labelledby="about-h">
      <div className="lbl">Fig. 1 · {COPY.about.title}</div>
      <h2 id="about-h">{COPY.about.title}</h2>
      <div className="cols c2">
        {COPY.about.items.map((it, i) => {
          const Icon = ABOUT_ICONS[i];
          return (
            <div key={it.q} className="card about-item">
              <Icon />
              <h3>{it.q}</h3>
              <p className="sm ink2" style={{ margin: 0 }}>{it.a}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function Pipeline() {
  return (
    <section className="block wrap" id="learn" aria-labelledby="pipe-h">
      <div className="lbl">Fig. 2 · {COPY.pipeline.title}</div>
      <h2 id="pipe-h">{COPY.pipeline.heading}</h2>
      <p>{COPY.pipeline.lead}</p>
      <div className="pipeline">
        {COPY.pipeline.steps.map((s, i) => {
          const Icon = PIPELINE_ICONS[i];
          return (
            <div key={s.n}>
              <span className="lbl">{s.n}</span>
              <Icon />
              <h3>{s.title}</h3>
              <span className="sm ink2">{s.line}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function Split() {
  return (
    <section className="block wrap" aria-labelledby="split-h">
      <div className="split">
        <div>
          <div className="lbl">Fig. 3 · {COPY.split.title}</div>
          <h2 id="split-h">{COPY.split.title}</h2>
          {COPY.split.paragraphs.map((p) => <p key={p}>{p}</p>)}
        </div>
        <figure style={{ margin: 0 }}>
          <div className="card gridbg pad"><SplitDiagram id="home-split" /></div>
          <figcaption className="cap">{COPY.split.caption}</figcaption>
        </figure>
      </div>
    </section>
  );
}

function Anatomy() {
  const [hover, setHover] = useState<number | null>(null);
  const [sel, setSel] = useState<number | null>(null);
  const active = hover ?? sel;
  const toggle = (n: number) => setSel((s) => (s === n ? null : n));
  return (
    <section className="block wrap" aria-labelledby="anat-h">
      <div className="lbl">Fig. 4 · {COPY.anatomy.title}</div>
      <h2 id="anat-h">{COPY.anatomy.heading}</h2>
      <p>{COPY.anatomy.lead}</p>
      <div className="anatomy">
        <figure className="fig" style={{ margin: 0 }}>
          <div className="card gridbg pad">
            <BoardAnatomy active={active} onHover={setHover} onSelect={toggle} />
          </div>
          <figcaption className="cap">{COPY.anatomy.caption}</figcaption>
        </figure>
        <div className="parts">
          <ol>
            {COPY.anatomy.parts.map((p) => {
              const n = Number(p.n);
              return (
                <li key={p.n} className={active === n ? 'on' : ''} onMouseEnter={() => setHover(n)} onMouseLeave={() => setHover(null)}>
                  <button className="badge" aria-pressed={sel === n} aria-label={`${p.n}, ${p.part}`} onClick={() => toggle(n)} onFocus={() => setHover(n)} onBlur={() => setHover(null)}>{p.n}</button>
                  <span><b style={{ display: 'block', fontSize: '1rem' }}>{p.part}</b><span className="sm ink2">{p.does}</span></span>
                </li>
              );
            })}
          </ol>
        </div>
      </div>
    </section>
  );
}

function Demo() {
  return (
    <section className="block wrap" id="demo" aria-labelledby="demo-h">
      <div className="lbl">Fig. 5 · {COPY.demo.title}</div>
      <h2 id="demo-h">{COPY.demo.heading}</h2>
      <p>{COPY.demo.intro}</p>
      <p>{COPY.demo.modelsIntro}</p>
      <ul className="sm">
        {COPY.demo.models.map((m) => <li key={m.name}><strong>{m.name}</strong> {m.text}</li>)}
      </ul>
      <p className="sm ink2">{COPY.demo.warning}</p>
      <DemoPanel />
    </section>
  );
}

function Lessons() {
  return (
    <section className="block wrap" id="lessons" aria-labelledby="les-h">
      <div className="lbl">Fig. 6 · {COPY.lessons.title}</div>
      <h2 id="les-h">{COPY.lessons.heading}</h2>
      <div className="lessons">
        {COPY.lessons.items.map((l, i) => (
          <a key={l.n} className="card lesson-card" href={`#/lesson/${i + 1}`}>
            <LessonIcon index={i} />
            <span>
              <span className="lbl" style={{ display: 'block' }}>{l.n}</span>
              <b style={{ display: 'block', margin: '2px 0 4px' }}>{l.title}</b>
              <span className="sm ink2">{l.blurb}</span>
            </span>
          </a>
        ))}
      </div>
    </section>
  );
}

function Results() {
  const recall = evalTorch?.per_class.drone.recall ?? null;
  const f32 = benchMetric('fp32_onnx', 'size_kb')?.value;
  const i8 = benchMetric('int8_onnx', 'size_kb')?.value;
  const kb = (v: number | null | undefined) => (v == null ? 'not run yet' : `${Math.round(v).toLocaleString('en-AU')} KB`);
  return (
    <section className="block wrap" id="results" aria-labelledby="res-h">
      <div className="lbl">Fig. 7 · {COPY.results.title}</div>
      <h2 id="res-h">{COPY.results.heading}</h2>
      <p>{COPY.results.lead}</p>
      <div className="cols c3">
        {COPY.results.items.map((it, i) => {
          const Sketch = SKETCHES[i];
          return (
            <div key={it.title} className="card result-card">
              <Sketch />
              {i === 0 ? <div className="num">{fmt(recall)} <Label kind="measured (host CPU)" /></div> : null}
              {i === 1 ? (
                <div className="mono sm" style={{ marginBottom: 4 }}>
                  float32 {kb(f32)} · int8 {kb(i8)} <Label kind="measured (host CPU)" />
                </div>
              ) : null}
              <h3>{it.title}</h3>
              <p className="sm ink2" style={{ margin: 0 }}>{it.text.replace('{{drone_recall}}', fmt(recall))}</p>
            </div>
          );
        })}
      </div>
      <p style={{ marginTop: 16 }}><strong>Next steps:</strong> {COPY.results.next}</p>
    </section>
  );
}

export function Home() {
  return (
    <>
      <Hero />
      <About />
      <Pipeline />
      <Split />
      <Anatomy />
      <Demo />
      <Lessons />
      <Results />
    </>
  );
}
