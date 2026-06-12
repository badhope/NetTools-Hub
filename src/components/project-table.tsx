import { Project } from "@/types/project";
import { Lang, t } from "@/lib/i18n";
import { ProjectRow } from "@/components/project-row";

interface ProjectTableProps {
  projects: readonly Project[];
  lang: Lang;
}

/**
 * Project table.
 *
 * Renders the canonical view of a filtered set of projects. Every
 * column is right-aligned or monospace where appropriate; rows are
 * dense (single line of description) so the table is scannable
 * top-to-bottom and a single screen holds 30+ rows on desktop.
 *
 * The "Name" column is the only "wide" one — it shows the project
 * name, a one-line description, and a tag row. The "Stars" /
 * "Last commit" / "License" / "Status" / "Verdict" columns are
 * 3-9 character mono fields that all read from the same line of
 * the table.
 */
export function ProjectTable({ projects, lang }: ProjectTableProps) {
  if (projects.length === 0) {
    return (
      <p className="border border-dashed border-dim p-6 text-center text-[13px] text-muted">
        {t(lang, "table.empty")}
      </p>
    );
  }
  return (
    <table className="proj-table">
      <thead>
        <tr>
          <th>{t(lang, "table.col.name")}</th>
          <th className="hide-md">{t(lang, "table.col.platforms")}</th>
          <th className="num text-right">{t(lang, "table.col.stars")}</th>
          <th className="hide-md">{t(lang, "table.col.last_commit")}</th>
          <th className="hide-md">{t(lang, "table.col.license")}</th>
          <th className="hide-md">{t(lang, "table.col.status")}</th>
          <th className="hide-md">{t(lang, "table.col.verdict")}</th>
        </tr>
      </thead>
      <tbody>
        {projects.map((p) => (
          <ProjectRow key={p.id} project={p} lang={lang} />
        ))}
      </tbody>
    </table>
  );
}
