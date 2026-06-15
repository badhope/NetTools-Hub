'use client';

import type { Project } from '@/types/project';
import { t } from '@/lib/i18n';
import { formatStars, formatNumber } from '@/lib/utils';
import { PlatformBadges, StatusBadge, VerdictBadge } from './project-badges';
import Link from 'next/link';
import { useLang } from '@/components/lang-provider';

interface ProjectDetailProps {
  project: Project;
  relatedProjects?: readonly Project[];
}

/**
 * Project detail view.
 *
 * Displays comprehensive information about a single project:
 * - Header with name, author, description
 * - Key metrics (stars, forks, language, license)
 * - Platform support
 * - Status and verdict
 * - Tags
 * - Highlights
 * - Notes (if any)
 * - Links to repository and homepage
 *
 * The layout is optimized for scanning: the most important information
 * (name, description, stars) is at the top, followed by structured
 * metadata in a two-column grid on desktop, stacking on mobile.
 *
 * Reads the active language from the `LangProvider` context so a
 * language switch in the top nav re-renders the labels, date
 * formats, and badges without a full page reload.
 */
export function ProjectDetail({ project: p, relatedProjects }: ProjectDetailProps) {
  const { lang } = useLang();
  const addedDate = new Date(p.addedAt).toLocaleDateString(
    lang === 'zh' ? 'zh-CN' : lang === 'ja' ? 'ja-JP' : 'en-US',
    { year: 'numeric', month: 'short', day: 'numeric' },
  );
  const lastCommitDate = new Date(p.lastCommit).toLocaleDateString(
    lang === 'zh' ? 'zh-CN' : lang === 'ja' ? 'ja-JP' : 'en-US',
    { year: 'numeric', month: 'short', day: 'numeric' },
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-line pb-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <h2 className="text-[1.75rem] font-semibold text-fg">{p.name}</h2>
            <p className="mt-1 text-sm text-muted">
              by <span className="text-fg-2">{p.author}</span>
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <StatusBadge status={p.status} />
            {p.verdict && <VerdictBadge verdict={p.verdict} />}
          </div>
        </div>
        <p className="mt-3 text-[0.9375rem] text-fg-2 leading-relaxed">{p.description}</p>
      </div>

      {/* Key metrics grid */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <MetricCard label={t(lang, 'metric.stars')} value={formatStars(p.stars)} />
        <MetricCard label={t(lang, 'metric.forks')} value={formatNumber(p.forks)} />
        <MetricCard label={t(lang, 'metric.license')} value={p.license} />
        <MetricCard label={t(lang, 'metric.language')} value={p.language} />
      </div>

      {/* Platform support */}
      <div className="border border-line p-4">
        <h3 className="kicker mb-3">{t(lang, 'taxonomy.platform')}</h3>
        <div className="flex flex-wrap gap-2">
          <PlatformBadges project={p} />
        </div>
      </div>

      {/* Metadata grid */}
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="border border-line p-4">
          <h3 className="kicker mb-3">Timeline</h3>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-muted">Added</dt>
              <dd className="font-mono text-fg-2">{addedDate}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted">{t(lang, 'metric.last_commit')}</dt>
              <dd className="font-mono text-fg-2">{lastCommitDate}</dd>
            </div>
          </dl>
        </div>

        <div className="border border-line p-4">
          <h3 className="kicker mb-3">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {p.tags.map((tag) => (
              <span
                key={tag}
                className="font-mono text-xs text-muted border border-line px-2 py-0.5"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Highlights */}
      {p.highlights.length > 0 && (
        <div className="border border-line p-4">
          <h3 className="kicker mb-3">Highlights</h3>
          <ul className="space-y-2 text-sm text-fg-2">
            {p.highlights.map((highlight, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-accent mt-0.5">•</span>
                <span>{highlight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Notes */}
      {p.notes && (
        <div className="border border-line p-4 bg-bg-elev">
          <h3 className="kicker mb-3">Notes</h3>
          <p className="text-sm text-fg-2 leading-relaxed">{p.notes}</p>
        </div>
      )}

      {/* Links */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <a
          href={p.url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`${p.name} repository (opens in new tab)`}
          className="link-editorial inline-flex items-center gap-2 px-4 py-2 border border-accent text-accent hover:bg-accent hover:text-bg transition-colors"
        >
          <span>View Repository</span>
          <span aria-hidden="true">↗</span>
        </a>
        {p.homepage && (
          <a
            href={p.homepage}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`${p.name} homepage (opens in new tab)`}
            className="link-editorial inline-flex items-center gap-2 px-4 py-2 border border-line text-fg-2 hover:border-fg-2 hover:text-fg transition-colors"
          >
            <span>Homepage</span>
            <span aria-hidden="true">↗</span>
          </a>
        )}
        <Link
          href={`/explore/k/${p.kind}?lang=${lang}`}
          aria-label={`Back to ${p.kind} category`}
          className="inline-flex items-center gap-2 px-4 py-2 border border-line text-fg-2 hover:border-fg-2 hover:text-fg transition-colors"
        >
          <span aria-hidden="true">←</span>
          <span>Back to {p.kind}</span>
        </Link>
      </div>

      {/* Related projects */}
      {relatedProjects && relatedProjects.length > 0 && (
        <div className="border-t border-line pt-6">
          <h3 className="kicker mb-4">{t(lang, 'related.title')}</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            {relatedProjects.map((related) => (
              <Link
                key={related.id}
                href={`/explore/project/${related.id}?lang=${lang}`}
                className="group border border-line p-4 hover:border-accent transition-colors"
                aria-label={`View ${related.name}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-fg group-hover:text-accent transition-colors truncate">
                      {related.name}
                    </h4>
                    <p className="text-xs text-muted mt-0.5">{related.author}</p>
                  </div>
                  <StatusBadge status={related.status} />
                </div>
                <p className="text-sm text-fg-2 mt-2 line-clamp-2">{related.description}</p>
                <div className="flex items-center gap-3 mt-3 text-xs text-muted">
                  <span className="font-mono">{formatStars(related.stars)}</span>
                  <span>·</span>
                  <span className="font-mono">{related.language}</span>
                  <span>·</span>
                  <span className="capitalize">{related.kind}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-line p-3" role="group" aria-label={label}>
      <dt className="kicker mb-1">{label}</dt>
      <dd className="font-mono text-lg text-fg" aria-label={`${label}: ${value}`}>
        {value}
      </dd>
    </div>
  );
}
