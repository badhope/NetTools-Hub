'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { Lang, langParam, t, withLang } from '@/lib/i18n';
import { LanguageSwitcher } from '@/components/language-switcher';
import { SiteMark } from '@/components/site-mark';
import { ThemeToggle } from '@/components/theme-toggle';
import { COPYRIGHT_YEAR } from '@/lib/site';
import { kindLabel } from '@/lib/taxonomy';
import { KIND_ORDER } from '@/lib/constants';
import { useLang } from '@/components/lang-provider';

interface TopNavProps {
  /**
   * Per-kind counts, used by the mobile drawer to render a kind
   * list with project totals. Optional — when absent (e.g. on a
   * page that doesn't have them in scope), the drawer still
   * renders but the counts are omitted.
   */
  kindCounts?: Readonly<Record<string, number>>;
  total?: number;
  variant: 'landing' | 'explore';
  /**
   * Whether the `<header>` should attach itself to the viewport
   * edge via `position: sticky`. The new explore layout never
   * wraps the top nav in its own sticky element, so this defaults
   * to true and the explore page sets it explicitly to keep that
   * behaviour.
   */
  sticky?: boolean;
}

export function TopNav({ kindCounts, total, variant, sticky = true }: TopNavProps) {
  const { lang, setLang } = useLang();
  const [mobileOpen, setMobileOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const panelRef = useRef<HTMLDivElement | null>(null);

  // Focus trap + Esc-to-close for the mobile drawer. Same shape as
  // before; the only thing that changed is the inner content.
  useEffect(() => {
    if (!mobileOpen) return;
    const panel = panelRef.current;
    const trigger = triggerRef.current;
    const focusables = () =>
      panel
        ? Array.from(
            panel.querySelectorAll<HTMLElement>(
              'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
            ),
          )
        : [];
    const closeBtn = panel?.querySelector<HTMLElement>('[data-drawer-close]');
    closeBtn?.focus();

    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        setMobileOpen(false);
        return;
      }
      if (e.key !== 'Tab') return;
      const items = focusables();
      if (items.length === 0) return;
      const first = items[0]!;
      const last = items[items.length - 1]!;
      const active = document.activeElement as HTMLElement | null;
      if (e.shiftKey && active === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && active === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('keydown', onKey);
      trigger?.focus();
    };
  }, [mobileOpen]);

  const handleLangChange = useCallback(
    (next: Lang) => {
      setLang(next);
      setMobileOpen(false);
    },
    [setLang],
  );

  const homeHref = langParam(lang, '/');
  const exploreHref = langParam(lang, '/explore');
  const primaryCta = variant === 'landing' ? t(lang, 'editorial.open_atlas') : t(lang, 'nav.home');
  const primaryHref = variant === 'landing' ? exploreHref : homeHref;

  return (
    <>
      <header
        className={`z-40 border-b border-line bg-bg/85 backdrop-blur-md ${
          sticky ? 'sticky top-0' : 'relative'
        }`}
      >
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6">
          <Link href={homeHref} className="group flex shrink-0 items-center gap-2.5 text-fg">
            <SiteMark
              size={22}
              className="text-accent transition-transform duration-500 group-hover:rotate-45"
            />
            <span className="hidden font-display text-[1.05rem] font-medium leading-none tracking-tight sm:inline">
              {t(lang, 'site.title')}
            </span>
          </Link>

          <span aria-hidden className="hidden h-5 w-px shrink-0 bg-dim md:inline-block" />

          <span className="kicker hidden md:inline-block">
            {t(lang, 'editorial.edition', { date: String(COPYRIGHT_YEAR) })}
          </span>

          <div className="flex-1" />

          <ThemeToggle />
          <LanguageSwitcher lang={lang} onChange={setLang} />

          <Link
            href={primaryHref}
            className="link-editorial inline-flex h-9 items-center gap-2 px-1 text-sm"
          >
            <span className="hidden sm:inline">{primaryCta}</span>
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path strokeLinecap="square" d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </Link>

          <button
            ref={triggerRef}
            onClick={() => setMobileOpen(true)}
            className="inline-flex h-9 w-9 items-center justify-center border border-dim text-fg-2 transition-colors hover:border-accent hover:text-accent lg:hidden"
            aria-label={t(lang, 'nav.menu')}
            aria-expanded={mobileOpen}
            aria-controls="mobile-drawer"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path strokeLinecap="square" d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
        </div>
      </header>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-bg/80" onClick={() => setMobileOpen(false)} />
          <div
            id="mobile-drawer"
            ref={panelRef}
            role="dialog"
            aria-modal="true"
            aria-label={t(lang, 'nav.index')}
            className="absolute inset-y-0 right-0 flex w-[min(88vw,360px)] flex-col border-l border-line bg-bg-elev"
          >
            <div className="flex h-16 shrink-0 items-center justify-between border-b border-line px-5">
              <span className="kicker">{t(lang, 'taxonomy.index')}</span>
              <button
                data-drawer-close
                onClick={() => setMobileOpen(false)}
                className="text-fg-2 hover:text-accent"
                aria-label={t(lang, 'nav.close')}
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path strokeLinecap="square" d="M6 6l12 12M18 6L6 18" />
                </svg>
              </button>
            </div>
            <nav className="flex-1 overflow-y-auto px-4 py-5 font-mono text-[12.5px]">
              {/* All projects — root */}
              <Link
                href={withLang(lang, '/explore')}
                onClick={() => setMobileOpen(false)}
                className="flex items-center justify-between border-b border-line py-2 text-fg-2 hover:text-accent"
              >
                <span>
                  <span className="text-muted">/</span> {t(lang, 'taxonomy.all')}
                </span>
                {total !== undefined && (
                  <span className="text-[10px] text-muted">{String(total).padStart(3, '0')}</span>
                )}
              </Link>
              {/* Kinds */}
              {KIND_ORDER.map((k) => {
                const count = kindCounts?.[k] ?? 0;
                if (count === 0) return null;
                return (
                  <Link
                    key={k}
                    href={withLang(lang, `/explore/k/${k}`)}
                    onClick={() => setMobileOpen(false)}
                    className="flex items-center justify-between border-b border-line py-2 text-fg-2 hover:text-accent"
                  >
                    <span>
                      <span className="text-muted">/</span> {kindLabel(k, lang)}{' '}
                      <span className="text-[10px] text-muted">/{k}</span>
                    </span>
                    <span className="text-[10px] text-muted">{String(count).padStart(3, '0')}</span>
                  </Link>
                );
              })}
            </nav>
            <div className="shrink-0 border-t border-line p-4">
              <LanguageSwitcher lang={lang} onChange={handleLangChange} />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
