'use client';

import Link from 'next/link';
import { t, langParam } from '@/lib/i18n';
import { useClientLang } from '@/lib/use-client-lang';

export default function NotFound() {
  // `output: "export"` pre-renders this page in English regardless of
  // the URL, so the shared `useClientLang` hook picks up `?lang=`
  // (and the storage / navigator fallback chain) on mount. The
  // skip-link target `id="main"` here makes the global
  // `<a href="#main" class="skip-link">` in the layout actually
  // usable from this error page, which is a common a11y miss.
  const [lang] = useClientLang();

  return (
    <main
      id="main"
      aria-label={t(lang, 'a11y.main')}
      tabIndex={-1}
      className="flex min-h-screen flex-col items-center justify-center bg-bg px-6 text-center outline-none"
    >
      <div className="mb-6 flex items-center gap-3">
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
          {t(lang, '404.folio')}
        </span>
        <span className="h-px w-12 bg-dim" />
      </div>
      <h1 className="font-display text-7xl leading-none text-fg sm:text-8xl">
        4<span className="italic text-accent">0</span>4
      </h1>
      <p className="mt-6 max-w-sm text-sm leading-relaxed text-fg-2">
        {t(lang, '404.description')}
      </p>
      <Link
        href={langParam(lang, '/')}
        className="group mt-10 inline-flex items-center gap-3 border-b border-accent pb-1 font-display text-lg text-accent transition-colors hover:text-accent-hover"
      >
        <span>{t(lang, '404.back')}</span>
        <svg
          className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path strokeLinecap="square" d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </Link>
    </main>
  );
}
