import { useEffect, useState } from 'react';
import { COPY } from './content/copy';
import { Glossary } from './pages/Glossary';
import { Home } from './pages/Home';
import { LessonPage } from './pages/Lesson';

const REPO = 'https://github.com/cesinata/edge-vision-lab';

type Route = { page: 'home'; scroll: string | null } | { page: 'lesson'; n: number } | { page: 'glossary' };

// Hash routes. Section links keep the home page and scroll to the section. Old route names still work.
const SECTIONS: Record<string, string> = { '/learn': 'learn', '/demo': 'demo', '/lessons': 'lessons', '/results': 'results', '/board': 'learn', '/lessons-old': 'lessons' };
const LEGACY: Record<string, Route> = {
  '/memory': { page: 'lesson', n: 6 }, '/states': { page: 'lesson', n: 6 }, '/failures': { page: 'lesson', n: 4 }, '/glossary': { page: 'glossary' },
};

function parse(): Route {
  const h = window.location.hash.replace(/^#/, '') || '/';
  const m = h.match(/^\/lesson\/([1-6])$/);
  if (m) return { page: 'lesson', n: Number(m[1]) };
  if (LEGACY[h]) return LEGACY[h];
  if (SECTIONS[h]) return { page: 'home', scroll: SECTIONS[h] };
  return { page: 'home', scroll: null };
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
  const [route, setRoute] = useState<Route>(parse());
  const [theme, setTheme] = useState<Theme>(readTheme());

  useEffect(() => {
    const onHash = () => setRoute(parse());
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

  useEffect(() => {
    if (route.page === 'home' && route.scroll) {
      document.getElementById(route.scroll)?.scrollIntoView();
    } else {
      window.scrollTo(0, 0);
      document.getElementById('main')?.focus({ preventScroll: true });
    }
    document.title = route.page === 'lesson' ? `${COPY.lessons.items[route.n - 1].title} | ${COPY.siteName}` : route.page === 'glossary' ? `Glossary and sources | ${COPY.siteName}` : COPY.siteName;
  }, [route]);

  const next: Record<Theme, Theme> = { system: 'light', light: 'dark', dark: 'system' };
  const links = [
    { label: COPY.nav[0], href: '#/learn', key: 'learn' },
    { label: COPY.nav[1], href: '#/demo', key: 'demo' },
    { label: COPY.nav[2], href: '#/results', key: 'results' },
  ];

  return (
    <>
      <a className="skip" href="#main" onClick={(e) => { e.preventDefault(); document.getElementById('main')?.focus(); }}>Skip to content</a>
      <header className="site">
        <div className="wrap bar-top">
          <a className="brand" href="#/" aria-label={`${COPY.siteName}, home`}>
            <svg width="34" height="34" viewBox="0 0 34 34" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="2" y="2" width="30" height="30" rx="4" /><circle cx="17" cy="17" r="7" /><circle cx="17" cy="17" r="2.5" fill="var(--mark)" /><path d="M2 10H6M2 24H6M28 10H32M28 24H32" />
            </svg>
            <span>{COPY.siteName}</span>
          </a>
          <nav aria-label="Main">
            <ul>
              {links.map((l) => <li key={l.key}><a href={l.href} aria-current={route.page === 'home' && route.scroll === l.key ? 'location' : undefined}>{l.label}</a></li>)}
              <li><a className="ext" href={REPO}>{COPY.nav[3]}</a></li>
              <li><button className="theme" onClick={() => setTheme(next[theme])} aria-label={`Colour theme: ${theme}. Activate to change.`}>Theme: {theme}</button></li>
            </ul>
          </nav>
        </div>
      </header>
      <main id="main" tabIndex={-1} style={{ outline: 'none' }}>
        {route.page === 'home' ? <Home /> : route.page === 'lesson' ? <LessonPage n={route.n} /> : <Glossary />}
      </main>
      <footer className="site">
        <div className="wrap">
          <p>{COPY.footer}</p>
          <p><a href="#/glossary">Glossary and sources</a></p>
        </div>
      </footer>
    </>
  );
}
