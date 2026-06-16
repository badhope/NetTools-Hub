'use client';

import type { Project } from '@/types/project';
import { platformLabel } from '@/lib/taxonomy';
import { t } from '@/lib/i18n';
import { useLang } from '@/components/lang-provider';

/**
 * Platform / status / verdict badges.
 *
 * Three small chip components, all client-side so they re-render
 * when the language changes. The shared `badge` / `badge--<key>`
 * class names live in `globals.css` (the editorial-muted palette:
 * recommended = green, caution = amber, avoid = red, archived =
 * red, stale = amber).
 */

export function PlatformBadges({ project }: { project: Project }) {
  const { lang } = useLang();
  return (
    <div className="flex flex-wrap gap-1.5">
      {project.platform.map((plat) => (
        <span key={plat} className="badge" title={platformLabel(plat, lang)}>
          {plat}
        </span>
      ))}
    </div>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const { lang } = useLang();
  return <span className={`badge badge--${status}`}>{t(lang, `status.${status}`)}</span>;
}

export function VerdictBadge({ verdict }: { verdict: string }) {
  const { lang } = useLang();
  if (!verdict) return null;
  return <span className={`badge badge--${verdict}`}>{t(lang, `verdict.${verdict}`)}</span>;
}
