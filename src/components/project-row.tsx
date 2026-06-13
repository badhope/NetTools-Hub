import type { Project } from '@/types/project';
import { Lang, t } from '@/lib/i18n';
import { PlatformBadges, StatusBadge, VerdictBadge } from './project-row/project-badges';
import { ProjectMeta } from './project-row/project-meta';

interface ProjectRowProps {
  project: Project;
  lang: Lang;
}

/**
 * Single project row in the /explore table.
 *
 * Server-rendered: the whole row is a real `<a>` element that
 * opens the upstream repository in a new tab. No client JS, no
 * preflight HEAD check, no useState. The full HTML is delivered
 * with the page, so the user can see and click rows before any
 * JS has even loaded.
 *
 * The CSS in globals.css handles the hover/press affordances
 * (left-rail pulse, accent background tint, ↗ icon slide) so
 * the visual feedback is preserved without any client logic.
 */
export function ProjectRow({ project: p, lang }: ProjectRowProps) {
  return (
    <tr className="proj-row">
      <td data-label={t(lang, 'table.col.name')}>
        <div className="name">
          <a
            href={p.url}
            target="_blank"
            rel="noopener noreferrer"
            title={`${p.name} — ${p.description}`}
            aria-label={`${p.name} — open repository in a new tab`}
            className="block"
          >
            <span>{p.name}</span>
            <span className="ml-1 text-[10.5px] text-muted">@{p.author}</span>
            <span className="ext-icon" aria-hidden="true">
              ↗
            </span>
          </a>
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
