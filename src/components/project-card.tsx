'use client';

import Link from 'next/link';
import type { Project } from '@/types/project';
import { formatStars, formatNumber } from '@/lib/utils';
import { PlatformBadges, StatusBadge, VerdictBadge } from './project-row/project-badges';
import { useLang } from '@/components/lang-provider';
import { t } from '@/lib/i18n';

interface ProjectCardProps {
  project: Project;
}

/**
 * Project card for grid display.
 *
 * Rich information in a compact card layout:
 * - Header: name, author, status/verdict badges
 * - Description (2 lines max)
 * - Key metrics: stars, forks, language, license
 * - Platform badges
 * - Tags (first 3)
 * - Link to detail page
 *
 * The card is a client component to read the active language
 * from LangProvider for i18n labels.
 */
export function ProjectCard({ project: p }: ProjectCardProps) {
  const { lang } = useLang();

  const lastCommitDate = new Date(p.lastCommit).toLocaleDateString(
    lang === 'zh' ? 'zh-CN' : lang === 'ja' ? 'ja-JP' : 'en-US',
    { year: 'numeric', month: 'short', day: 'numeric' },
  );

  return (
    <Link
      href={`/explore/project/${p.id}?lang=${lang}`}
      className="group block border border-line bg-bg-elev/40 p-4 transition-all hover:border-accent hover:bg-bg-sunk"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-fg group-hover:text-accent transition-colors truncate">
            {p.name}
          </h3>
          <p className="text-xs text-muted mt-0.5">{p.author}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <StatusBadge status={p.status} />
          {p.verdict && <VerdictBadge verdict={p.verdict} />}
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-fg-2 leading-relaxed line-clamp-2 mb-3">
        {p.description}
      </p>

      {/* Key metrics */}
      <div className="grid grid-cols-4 gap-2 mb-3 text-xs">
        <MetricItem label={t(lang, 'table.col.stars')} value={formatStars(p.stars)} />
        <MetricItem label="Forks" value={formatNumber(p.forks)} />
        <MetricItem label={t(lang, 'table.col.language')} value={p.language} />
        <MetricItem label={t(lang, 'table.col.license')} value={p.license} />
      </div>

      {/* Platform badges */}
      <div className="mb-3">
        <PlatformBadges project={p} />
      </div>

      {/* Tags (first 3) */}
      {p.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {p.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="font-mono text-[10px] text-muted border border-line px-1.5 py-0.5"
            >
              #{tag}
            </span>
          ))}
          {p.tags.length > 3 && (
            <span className="font-mono text-[10px] text-muted">
              +{p.tags.length - 3}
            </span>
          )}
        </div>
      )}

      {/* Footer: last commit */}
      <div className="flex items-center justify-between text-[11px] text-muted pt-2 border-t border-line">
        <span>{t(lang, 'table.col.last_commit')}</span>
        <span className="font-mono">{lastCommitDate}</span>
      </div>
    </Link>
  );
}

function MetricItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-line px-2 py-1">
      <div className="text-[10px] text-muted leading-tight">{label}</div>
      <div className="font-mono text-fg text-xs leading-tight mt-0.5">{value}</div>
    </div>
  );
}
