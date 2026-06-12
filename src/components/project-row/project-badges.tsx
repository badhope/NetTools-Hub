import type { Project } from "@/types/project";
import { platformLabel } from "@/lib/taxonomy";
import { Lang, t } from "@/lib/i18n";

export function PlatformBadges({ project, lang }: { project: Project; lang: Lang }) {
  return (
    <div className="flex flex-wrap gap-1">
      {project.platform.map((plat) => (
        <span key={plat} className="badge" title={platformLabel(plat, lang)}>
          {plat}
        </span>
      ))}
    </div>
  );
}

export function StatusBadge({ status, lang }: { status: string; lang: Lang }) {
  return (
    <span className={`badge badge--${status}`}>
      {t(lang, `status.${status}`)}
    </span>
  );
}

export function VerdictBadge({ verdict, lang }: { verdict: string; lang: Lang }) {
  if (!verdict) return null;
  return (
    <span className={`badge badge--${verdict}`}>
      {t(lang, `verdict.${verdict}`)}
    </span>
  );
}
