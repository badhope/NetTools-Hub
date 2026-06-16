'use client';

import Link from 'next/link';
import { t, langParam } from '@/lib/i18n';
import { LangProvider, useLang } from '@/components/lang-provider';

/**
 * The 404 page.
 *
 * `next/navigation` calls this with the active root layout, which
 * already wraps `children` in a `LangProvider`. The 404 page is
 * therefore a child of that provider and can call `useLang()`
 * directly. *But* Next.js also prerenders the `/_not-found` page
 * as a static fallback (used when the user types an arbitrary
 * URL that does not match any route), and the prerender path
 * does *not* go through the root layout — it renders the page
 * in isolation, with no provider above it. The defensive
 * `<LangProvider>` wrapper below covers that case: at runtime
 * the provider is a no-op (the page is already inside the
 * layout's provider, the contexts compose), and at prerender
 * time it is the only provider in scope and `useLang()` works.
 */
export default function NotFound() {
  return (
    <LangProvider>
      <NotFoundInner />
    </LangProvider>
  );
}

function NotFoundInner() {
  const { lang } = useLang();

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
