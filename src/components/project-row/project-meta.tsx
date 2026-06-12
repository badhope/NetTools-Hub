import type { Project } from '@/types/project';
import { Lang, t } from '@/lib/i18n';
import { formatNumber } from '@/lib/utils';

export function ProjectMeta({ project, lang }: { project: Project; lang: Lang }) {
  return (
    <>
      <td className="num text-right" data-label={t(lang, 'table.col.stars')}>
        {formatNumber(project.stars, lang)}
        {project.forks > 0 && (
          <span className="ml-1 text-muted">/ {formatNumber(project.forks, lang)}</span>
        )}
      </td>
      <td className="hide-md num" data-label={t(lang, 'table.col.last_commit')}>
        {project.lastCommit}
      </td>
      <td className="hide-md num" data-label={t(lang, 'table.col.license')}>
        {project.license}
      </td>
    </>
  );
}
