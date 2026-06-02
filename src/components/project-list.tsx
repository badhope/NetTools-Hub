"use client";

import { useMemo } from "react";
import Link from "next/link";
import { Project, SortOption, ProjectCategory, Lang } from "@/types/project";
import { t } from "@/lib/i18n";
import { ProjectCard } from "@/components/project-card";
import { CATEGORY_GROUPS } from "@/lib/category-groups";

interface ProjectListProps {
  projects: Project[];
  sort: SortOption;
  stats: Record<string, number>;
  categories: Record<string, ProjectCategory>;
  lang: Lang;
}

export function ProjectList({ projects, sort, stats, categories, lang }: ProjectListProps) {
  const sorted = useMemo(() => {
    const copy = [...projects];
    switch (sort) {
      case "stars":
        return copy.sort((a, b) => b.stars - a.stars);
      case "name":
        return copy.sort((a, b) => a.name.localeCompare(b.name, "en"));
      case "updated":
        return copy.sort(
          (a, b) =>
            new Date(b.lastCommit).getTime() - new Date(a.lastCommit).getTime(),
        );
      default:
        return copy;
    }
  }, [projects, sort]);

  if (projects.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-[#6e7681]">
        <span className="text-5xl">🔍</span>
        <p className="mt-5 text-lg">{t(lang, "list.not_found")}</p>
        <p className="mt-2 text-sm">{t(lang, "list.try_again")}</p>
      </div>
    );
  }

  if (sort !== "default") {
    return (
      <div className="px-4 py-6 sm:px-6 sm:py-8">
        <div className="mb-6 text-sm text-[#8b949e]">
          {t(lang, "list.found", { count: projects.length })}
        </div>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {sorted.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      </div>
    );
  }

  const groupedByGroup = CATEGORY_GROUPS.map((group) => {
    const slugs = group.slugs.filter((s) => stats[s] > 0);
    const groupProjects = slugs.flatMap((slug) => sorted.filter((p) => p.category === slug));
    if (groupProjects.length === 0) return null;
    return { group, groupProjects };
  }).filter((g): g is { group: typeof CATEGORY_GROUPS[number]; groupProjects: Project[] } => g !== null);

  return (
    <div className="space-y-12 px-4 py-6 sm:space-y-16 sm:px-6 sm:py-8">
      {groupedByGroup.map(({ group, groupProjects }) => (
        <section key={group.id}>
          <div className="mb-6 flex items-center gap-3">
            <span
              className="inline-block h-2.5 w-2.5 shrink-0 rounded-full"
              style={{ background: `linear-gradient(135deg, ${groupProjects[0]?.gradient[0] || "#58a6ff"}, ${groupProjects[0]?.gradient[1] || "#3fb950"})` }}
            />
            <span className="text-base font-semibold text-[#e6edf3]">
              {group.icon} {t(lang, group.labelKey)}
            </span>
            <span className="rounded-full border border-[#30363d] bg-[#21262d] px-2 py-0.5 text-xs text-[#6e7681]">
              {groupProjects.length}
            </span>
          </div>

          <div className="space-y-10">
            {group.slugs.filter((s) => stats[s] > 0).map((slug) => {
              const catInfo = categories[slug];
              const catProjects = groupProjects.filter((p) => p.category === slug);
              if (catProjects.length === 0) return null;
              return (
                <div key={slug} id={`cat-${slug}`}>
                  <div className="mb-4 flex items-center justify-between gap-2">
                    <Link
                      href={lang !== "en" ? `/explore?category=${slug}&lang=${lang}` : `/explore?category=${slug}`}
                      className="group flex min-w-0 items-center gap-2 text-sm font-medium text-[#8b949e] transition-colors hover:text-[#58a6ff]"
                    >
                      <span className="truncate">{catInfo?.icon} {catInfo?.name || slug}</span>
                      <span className="text-[#6e7681] opacity-0 transition-opacity group-hover:opacity-100">→</span>
                    </Link>
                    <span className="shrink-0 text-xs text-[#6e7681]">
                      {catProjects.length}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                    {catProjects.map((project) => (
                      <ProjectCard key={project.id} project={project} />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
