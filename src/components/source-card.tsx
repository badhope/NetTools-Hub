'use client';

import type { ProxySource } from '@/types/source';
import { useLang } from '@/components/lang-provider';
import { t } from '@/lib/i18n';
import { sourceTypeLabel, sourceFormatLabel, frequencyLabel } from '@/lib/sources';
import { formatStars } from '@/lib/utils';

/**
 * Card for a single free proxy source.
 *
 * Unlike a ProjectCard (which links to an internal detail page),
 * this card links directly to the external source URL — the user's
 * intent is to *get* nodes, not to read about the source. The card
 * shows enough metadata (type, format, update frequency, stars) to
 * help the user pick the right source before clicking through.
 */
export function SourceCard({ source: s }: { source: ProxySource }) {
  const { lang } = useLang();

  const isExternal = s.url.startsWith('http');
  const linkProps = isExternal
    ? { target: '_blank' as const, rel: 'noopener noreferrer' as const }
    : {};

  // Status badge colour — mirrors the project badge palette.
  const statusClass =
    s.status === 'active'
      ? 'badge--active'
      : s.status === 'stale'
        ? 'badge--stale'
        : 'badge--archived';

  return (
    <a
      href={s.url}
      {...linkProps}
      className="kind-card group block border border-line bg-bg-elev/40 p-4 transition-all hover:border-accent hover:bg-bg-sunk"
    >
      {/* Header: name + status badge */}
      <div className="mb-2 flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h2 className="truncate font-medium text-fg transition-colors group-hover:text-accent">
            {s.name}
          </h2>
          <p className="mt-0.5 font-mono text-[10.5px] text-muted">
            {sourceTypeLabel(s.type, lang)} · {sourceFormatLabel(s.format, lang)}
          </p>
        </div>
        <span className={`badge ${statusClass} shrink-0`}>{t(lang, `status.${s.status}`)}</span>
      </div>

      {/* Description */}
      <p className="mb-3 line-clamp-2 text-sm leading-relaxed text-fg-2">{s.description}</p>

      {/* Metadata grid */}
      <div className="mb-3 grid grid-cols-3 gap-2 text-xs">
        <MetaItem
          label={t(lang, 'sources.updated')}
          value={frequencyLabel(s.updateFrequency, lang)}
        />
        <MetaItem
          label={t(lang, 'sources.language')}
          value={s.language === 'zh' ? '中文' : s.language === 'en' ? 'English' : '中/英'}
        />
        <MetaItem label={t(lang, 'sources.stars')} value={s.stars ? formatStars(s.stars) : '—'} />
      </div>

      {/* Notes (if any) */}
      {s.notes && (
        <p className="mb-3 border-l-2 border-accent-3/40 pl-2 text-[12px] leading-relaxed text-muted">
          <span className="kicker mr-1">{t(lang, 'sources.notes')}</span>
          {s.notes}
        </p>
      )}

      {/* Footer: visit link */}
      <div className="flex items-center justify-between border-t border-line pt-2 text-[11px] text-muted">
        <span className="font-mono">
          {s.type === 'github' ? t(lang, 'sources.view_repo') : t(lang, 'sources.visit')}
        </span>
        <svg
          className="h-3.5 w-3.5 transition-transform duration-300 group-hover:translate-x-1"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
          aria-hidden
        >
          <path strokeLinecap="square" d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </div>
    </a>
  );
}

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-line px-2 py-1">
      <div className="text-[10px] leading-tight text-muted">{label}</div>
      <div className="mt-0.5 font-mono text-xs leading-tight text-fg">{value}</div>
    </div>
  );
}
