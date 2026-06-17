'use client';

import Link from 'next/link';
import { TopNav } from '@/components/top-nav';
import { SourceCard } from '@/components/source-card';
import { useLang } from '@/components/lang-provider';
import { t, withLang } from '@/lib/i18n';
import {
  getAllSources,
  getSourcesLastUpdated,
  SOURCE_CATEGORY_ORDER,
  sourceCategoryLabel,
} from '@/lib/sources';
import { getKindCounts } from '@/lib/projects';
import { formatStars } from '@/lib/utils';

/**
 * Free proxy sources page.
 *
 * This is a *separate* section from /explore — it lists resources
 * that publish free proxy nodes/subscriptions, not software projects.
 * The page groups sources by category (node repos, websites, Telegram
 * channels, converters, testers) and renders a SourceCard grid per
 * group.
 *
 * The page is a client component so the title, subtitle, and
 * category headers re-render on language switch without a full
 * page reload.
 */
export default function FreeSourcesPage() {
  const { lang } = useLang();
  const sources = getAllSources();
  const lastUpdated = getSourcesLastUpdated();
  const kindCounts = getKindCounts();

  // Total stars across GitHub sources (for the stat bar).
  const totalStars = sources.reduce((sum, s) => sum + (s.stars ?? 0), 0);

  // TopNav draws the mobile drawer "All projects" link with this total;
  // it must be the project count, not the source count.
  const totalProjects = Object.values(kindCounts).reduce((sum, n) => sum + n, 0);

  return (
    <div className="min-h-screen bg-bg text-fg">
      <TopNav kindCounts={kindCounts} total={totalProjects} variant="explore" sticky />
      <main
        id="main"
        aria-label={t(lang, 'sources.aria_sources')}
        className="mx-auto max-w-7xl px-4 py-6 sm:px-6"
      >
        {/* Header */}
        <header className="mb-6 border-b border-line pb-4">
          <div className="manual-index mb-3" data-index="★">
            <span>{t(lang, 'sources.folio')}</span>
          </div>
          <h1 className="text-[1.5rem] font-semibold leading-tight text-fg sm:text-[1.75rem]">
            {t(lang, 'sources.title')}
          </h1>
          <p className="mt-2 max-w-3xl text-sm leading-relaxed text-fg-2">
            {t(lang, 'sources.subtitle')}
          </p>

          {/* Stat bar */}
          <div className="mt-4 grid grid-cols-3 gap-3 border-y border-line py-3">
            <Stat label={t(lang, 'sources.count', { count: sources.length })} />
            <Stat label={`${formatStars(totalStars)} ${t(lang, 'sources.stars')}`} />
            <Stat label={`${t(lang, 'sources.last_updated')}: ${lastUpdated.split('T')[0]}`} />
          </div>

          {/* Disclaimer */}
          <div
            role="note"
            aria-label={t(lang, 'sources.aria_disclaimer')}
            className="mt-4 border-l-2 border-accent-3/60 bg-bg-sunk/40 p-3 text-[13px] leading-relaxed text-fg-2"
          >
            <span className="kicker mr-2 text-accent-3">!</span>
            {t(lang, 'sources.disclaimer')}
          </div>
        </header>

        {/* Source groups by category */}
        <div className="space-y-10">
          {SOURCE_CATEGORY_ORDER.map((category) => {
            const groupSources = sources.filter((s) => s.category === category);
            if (groupSources.length === 0) return null;
            return (
              <section key={category} aria-label={sourceCategoryLabel(category, lang)}>
                <div
                  className="manual-index mb-4"
                  data-index={String(SOURCE_CATEGORY_ORDER.indexOf(category) + 1).padStart(2, '0')}
                >
                  <span>
                    {sourceCategoryLabel(category, lang)}{' '}
                    <span className="text-muted">({groupSources.length})</span>
                  </span>
                </div>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {groupSources.map((source) => (
                    <SourceCard key={source.id} source={source} />
                  ))}
                </div>
              </section>
            );
          })}
        </div>

        {/* Back to index */}
        <div className="mt-12 border-t border-line pt-6">
          <Link href={withLang(lang, '/explore')} className="link-editorial font-mono text-sm">
            {t(lang, 'sources.back_to_index')}
          </Link>
        </div>
      </main>
    </div>
  );
}

function Stat({ label }: { label: string }) {
  return (
    <div className="text-center">
      <span className="font-mono text-sm text-fg">{label}</span>
    </div>
  );
}
