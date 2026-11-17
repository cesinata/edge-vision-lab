import { SOURCES, TERMS } from '../content/glossary';

export function Glossary() {
  return (
    <div className="wrap">
      <div className="crumbs"><a href="#/">Home</a></div>
      <h1>Glossary and sources</h1>
      <h2>Terms</h2>
      <dl>{TERMS.map(([t, d]) => (<div key={t}><dt>{t}</dt><dd className="sm">{d}</dd></div>))}</dl>
      <h2>Sources</h2>
      <dl>{SOURCES.map(([t, d]) => (<div key={t}><dt>{t}</dt><dd className="sm">{d}</dd></div>))}</dl>
    </div>
  );
}
