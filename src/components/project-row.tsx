'use client';

import { useEffect, useRef, useState } from 'react';
import type { Project } from '@/types/project';
import { Lang, t } from '@/lib/i18n';
import { useLinkPreflight } from './project-row/use-link-preflight';
import { PlatformBadges, StatusBadge, VerdictBadge } from './project-row/project-badges';
import { ProjectMeta } from './project-row/project-meta';

interface ProjectRowProps {
  project: Project;
  lang: Lang;
}

/**
 * Single project row in the /explore table.
 *
 * The whole row is clickable: clicking anywhere — the name, the
 * description, the platform badges, even the stars cell — opens
 * the upstream repository in a new tab. A short (~280 ms)
 * transition animation plays first, so the click is *seen* and
 * not silently lost: the row gets a brief `data-pressing` state
 * (left-rail pulse, accent background, slide-out `↗` icon)
 * before the new tab is opened. The delay is also useful on
 * touch devices, where the system would otherwise interpret a
 * long-press as a text-selection.
 *
 * Pre-flight check: delegated to the `useLinkPreflight` hook,
 * which issues a HEAD request and caches the result per-session.
 * Rows that fail get a "link broken" badge so the user is never
 * sent to a 404.
 *
 * The name <a> is preserved with `target="_blank"` so that
 * right-click "Open in new tab", middle-click, and keyboard
 * navigation keep working.
 */
export function ProjectRow({ project: p, lang }: ProjectRowProps) {
  const [pressing, setPressing] = useState(false);
  const timerRef = useRef<number | null>(null);
  const { linkState, preflight } = useLinkPreflight(p.url);

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, []);

  const open = async () => {
    const ok = await preflight();
    if (!ok) return; // broken: stay on page, badge already shown
    window.open(p.url, '_blank', 'noopener,noreferrer');
  };

  const navigate = () => {
    if (timerRef.current !== null) {
      window.clearTimeout(timerRef.current);
    }
    timerRef.current = window.setTimeout(() => {
      void open();
      timerRef.current = null;
    }, 280);
  };

  return (
    <tr
      className="proj-row"
      data-pressing={pressing ? 'true' : undefined}
      data-link={linkState}
      onPointerDown={(e) => {
        // Don't hijack middle / right clicks; those are the
        // browser's "open in new tab" gestures.
        if (e.button !== 0) return;
        setPressing(true);
        navigate();
      }}
      onPointerUp={() => setPressing(false)}
      onPointerCancel={() => setPressing(false)}
      onPointerLeave={() => setPressing(false)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          setPressing(true);
          navigate();
        }
      }}
      tabIndex={0}
      role="link"
      aria-label={`${p.name} — open repository in a new tab`}
    >
      <td data-label={t(lang, 'table.col.name')}>
        <div className="name">
          <a
            href={p.url}
            target="_blank"
            rel="noopener noreferrer"
            title={`${p.name} — ${p.description}`}
            onClick={(e) => e.stopPropagation()}
          >
            {p.name}
          </a>
          <span className="ml-1 text-[10.5px] text-muted">@{p.author}</span>
          <span className="ext-icon" aria-hidden="true">
            ↗
          </span>
          {linkState === 'broken' && (
            <span
              className="ml-2 text-[10px] text-accent-4"
              title="This link failed the pre-flight check"
            >
              link broken
            </span>
          )}
        </div>
        <p className="desc mt-0.5">{p.description}</p>
        <p className="tag mt-0.5 truncate">
          {p.tags
            .slice(0, 6)
            .map((tag) => `#${tag}`)
            .join('  ')}
        </p>
      </td>
      <td className="hide-md" data-label={t(lang, 'table.col.platforms')}>
        <PlatformBadges project={p} lang={lang} />
      </td>
      <ProjectMeta project={p} lang={lang} />
      <td className="hide-md" data-label={t(lang, 'table.col.status')}>
        <StatusBadge status={p.status} lang={lang} />
      </td>
      <td className="hide-md" data-label={t(lang, 'table.col.verdict')}>
        <VerdictBadge verdict={p.verdict ?? ''} lang={lang} />
      </td>
    </tr>
  );
}
