import { useEffect, useState, type ReactElement } from 'react';
import { Board } from './pages/Board';
import { Demo } from './pages/Demo';
import { Failures } from './pages/Failures';
import { Glossary } from './pages/Glossary';
import { Lessons } from './pages/Lessons';
import { Memory } from './pages/Memory';
import { Overview } from './pages/Overview';
import { States } from './pages/States';

const ROUTES: { path: string; label: string; page: () => ReactElement }[] = [
  { path: '/', label: 'Overview', page: Overview },
  { path: '/demo', label: 'Try it', page: Demo },
  { path: '/lessons', label: 'Lessons', page: Lessons },
  { path: '/board', label: 'Board', page: Board },
  { path: '/memory', label: 'Memory budget', page: Memory },
  { path: '/states', label: 'State machine', page: States },
  { path: '/failures', label: 'Failure gallery', page: Failures },
  { path: '/glossary', label: 'Glossary and sources', page: Glossary },
];

function currentPath(): string {
  const h = window.location.hash.replace(/^#/, '');
  return ROUTES.some((r) => r.path === h) ? h : '/';
}

type Theme = 'system' | 'light' | 'dark';

function readTheme(): Theme {
  const q = new URLSearchParams(window.location.search).get('theme');
  if (q === 'light' || q === 'dark') return q; // ?theme=light|dark, for screenshots
  try {
    const t = localStorage.getItem('theme');
    return t === 'light' || t === 'dark' ? t : 'system';
  } catch {
    return 'system';
  }
}

export function App() {
  const [path, setPath] = useState(currentPath());
  const [theme, setTheme] = useState<Theme>(readTheme());

  useEffect(() => {
    const onHash = () => {
      setPath(currentPath());
      window.scrollTo(0, 0);
      document.getElementById('main')?.focus();
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'system') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('theme', theme);
    } catch {
      /* storage can be blocked; the page still works */
    }
  }, [theme]);

  const route = ROUTES.find((r) => r.path === path) ?? ROUTES[0];
  const Page = route.page;
  const next: Record<Theme, Theme> = { system: 'light', light: 'dark', dark: 'system' };

  useEffect(() => {
    document.title = route.path === '/' ? 'edge-vision-lab' : `${route.label} | edge-vision-lab`;
  }, [route]);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="site">
        <button className="theme" onClick={() => setTheme(next[theme])} aria-label={`Colour theme: ${theme}. Activate to change.`}>
          Theme: {theme}
        </button>
        <div className="brand"><span className="dot" aria-hidden="true" /> edge-vision-lab</div>
        <nav aria-label="Main">
          <ul>
            {ROUTES.map((r) => (
              <li key={r.path}>
                <a href={`#${r.path}`} aria-current={r.path === path ? 'page' : undefined}>{r.label}</a>
              </li>
            ))}
          </ul>
        </nav>
      </header>
      <main id="main" tabIndex={-1}>
        <Page />
      </main>
      <footer>
        <p>
          AI assistance (Claude) was used to draft and review code and text. The repository owner ran the
          experiments; every number on this site comes from a run in the repository and carries a label saying
          how it was produced. Nothing here was measured on a microcontroller board.
        </p>
      </footer>
    </>
  );
}
