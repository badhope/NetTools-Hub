"use client";

import { useMemo } from "react";
import Link from "next/link";
import { Project, SortOption, ProjectCategory } from "@/types/project";
import { Lang, t, langParam } from "@/lib/i18n";
import { ProjectCard } from "@/components/project-card";
import { CATEGORY_GROUPS } from "@/lib/category-groups";
import { GroupMark, CategoryMark } from "@/components/category-mark";

interface ProjectListProps {
  projects: readonly Project[];
  sort: SortOption;
  stats: Readonly<Record<string, number>>;
  categories: Record<string, ProjectCategory>;
  lang: Lang;
}

export function ProjectList({ projects, sort, stats, categories, lang }: ProjectListProps) {
  const sorted = useMemo(() => {
    // `toSorted` is the ES2023 immutable cousin of `sort`; it returns
    // a new array and leaves the input untouched, which means a
    // stable reference survives across renders when the input
    // reference itself is stable (which it is — the parent passes
    // the same `filtered` array reference until the query changes).
    const copy = projects.slice();
    switch (sort) {
      case "stars":
        return copy.sort((a, b) => b.stars - a.stars);
      case "name":
        return copy.sort((a, b) => a.name.localeCompare(b.name, lang));
      case "updated":
        return copy.sort(
          (a, b) =>
            new Date(b.lastCommit).getTime() - new Date(a.lastCommit).getTime(),
        );
      default:
        return copy;
    }
  }, [projects, sort, lang]);

  // Pre-group the (already-sorted) projects by slug exactly once, then
  // every group in the render below does an O(1) `byCategory.get(slug)`
  // lookup. The old code did
  //   group.slugs.flatMap(slug => sorted.filter(p => p.category === slug))
  // which is O(slugs × projects) per render. With ~120 projects and
  // six groups this is fast, but on the "no filter, default sort"
  // hot path it ran on every keystroke of the search box, so moving
  // to O(n) up front was a free win.
  //
  // This hook must run on every render regardless of `sort`; the
  // early-return branch below (the "non-default sort" grid view)
  // does not use `byCategory`, but it is cheaper to compute the
  // memoised map and ignore it than to add a second conditional
  // hook call (which would violate `react-hooks/rules-of-hooks`).
  const byCategory = useMemo(() => {
    const m = new Map<string, Project[]>();
    for (const p of sorted) {
      const list = m.get(p.category);
      if (list) list.push(p);
      else m.set(p.category, [p]);
    }
    return m;
  }, [sorted]);

  // The parent (`explore-content`) renders a "no projects" empty
  // state when `projects.length === 0`, so this branch is unreachable
  // in practice. Defending against it here would only mask a parent
  // bug, so it is intentionally omitted.
  if (sort !== "default") {
    return (
      <div className="px-5 py-8 sm:px-8 sm:py-10">
        <div className="mb-6 flex items-center justify-between border-b border-line pb-3">
          <span className="kicker">
            {t(lang, "list.found", { count: projects.length })}
          </span>
          <span className="font-mono text-[10px] text-muted">
            {String(projects.length).padStart(3, "0")}
          </span>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {sorted.map((project) => (
            <ProjectCard key={project.id} project={project} lang={lang} />
          ))}
        </div>
      </div>
    );
  }

  const groupedByGroup = CATEGORY_GROUPS.map((group) => {
    // Under noUncheckedIndexedAccess, `stats[s]` is `number | undefined`.
    // `?? 0` is the safe coercion; an absent stat means "0 projects".
    // Filter once per group; both the `slugs` list and the per-category
    // sub-section below re-use it, so memoising it as `activeSlugs`
    // avoids a second O(slugs) scan per group on every render.
    const activeSlugs = group.slugs.filter((s) => (stats[s] ?? 0) > 0);
    const groupProjects: Project[] = [];
    for (const slug of activeSlugs) {
      const list = byCategory.get(slug);
      if (list && list.length > 0) groupProjects.push(...list);
    }
    if (groupProjects.length === 0) return null;
    return { group, activeSlugs, groupProjects };
  })
    .filter(
      (g): g is {
        group: typeof CATEGORY_GROUPS[number];
        activeSlugs: string[];
        groupProjects: Project[];
      } => g !== null,
    );

  return (
    <div className="space-y-16 px-5 py-8 sm:space-y-20 sm:px-8 sm:py-10">
      {groupedByGroup.map(({ group, activeSlugs, groupProjects }, gIdx) => (
        // `content-visibility: auto` + an explicit `contain-intrinsic-size`
        // tells the browser to defer rendering of off-screen groups
        // until the user scrolls near them. With 120+ cards on the
        // page, this turns a long-scroll jankfest into a 60fps
        // experience, especially on mobile.
        <section
          key={group.id}
          id={`group-${group.id}`}
          className="cv-auto"
        >
          <header className="mb-7 flex items-baseline justify-between gap-4 border-b border-line pb-3">
            <h2 className="flex items-baseline gap-3 font-display text-2xl text-fg">
              <span className="font-mono text-[11px] text-muted">
                {String(gIdx + 1).padStart(2, "0")}
              </span>
              <GroupMark
                id={group.id}
                size={20}
                className="self-center text-fg-2"
              />
              <span>{t(lang, group.labelKey)}</span>
            </h2>
            <span className="font-mono text-[11px] text-muted">
              {t(lang, "editorial.summary", { n: groupProjects.length, m: activeSlugs.length })}
            </span>
          </header>

          <div className="space-y-12">
            {activeSlugs.map((slug, idx) => {
              const catInfo = categories[slug];
              const catProjects = byCategory.get(slug) ?? [];
              if (catProjects.length === 0) return null;
              return (
                <div key={slug} id={`cat-${slug}`} className="cv-auto">
                  <div className="editorial-index mb-4" data-index={String(idx + 1).padStart(2, "0")}>
                    <Link
                      href={langParam(lang, `/explore?category=${slug}`)}
                      className="flex items-center gap-2 text-fg-2 transition-colors hover:text-accent"
                    >
                      <CategoryMark
                        slug={slug}
                        size={14}
                        className="text-fg-2"
                      />
                      <span className="font-display text-base text-fg">
                        {catInfo?.name || slug}
                      </span>
                      <span className="font-mono text-[10px] text-muted">
                        {String(catProjects.length).padStart(2, "0")}
                      </span>
                    </Link>
                  </div>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {catProjects.map((project) => (
                      <ProjectCard key={project.id} project={project} lang={lang} />
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
