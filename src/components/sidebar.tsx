"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { ProjectCategory } from "@/types/project";
import { Lang, langParam, t, withLang } from "@/lib/i18n";
import { CATEGORY_GROUPS } from "@/lib/category-groups";
import { GroupMark, CategoryMark } from "@/components/category-mark";

interface SidebarProps {
  categories: Record<string, ProjectCategory>;
  counts: Record<string, number>;
  lang: Lang;
  activeCategory?: string;
}

export function Sidebar({ categories, counts, lang, activeCategory }: SidebarProps) {
  // User-controlled collapse state. The group containing the active
  // category is always shown expanded — this is derived at render time
  // (see activeGroupId below) instead of being patched in via useEffect.
  // The previous implementation ran a useEffect on every activeCategory
  // change to set `collapsed[group.id] = false`, which React 19's
  // `react-hooks/set-state-in-effect` rule correctly flags as the
  // cascading-render anti-pattern.
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const totalProjects = Object.values(counts).reduce((a, b) => a + b, 0);

  const activeGroupId = activeCategory
    ? CATEGORY_GROUPS.find((g) => g.slugs.includes(activeCategory))?.id
    : undefined;

  const toggle = useCallback((id: string) => {
    setCollapsed((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

  return (
    <aside
      // The sidebar is 252 px wide, so it only really fits on
      // desktop layouts (xl = 1280 px in Tailwind v4). On the
      // 1024-px `lg` band the sidebar would crowd the project
      // cards into a single, very narrow column — a worse
      // experience than just relying on the mobile drawer.
      className="hidden w-[252px] shrink-0 flex-col border-r border-line bg-bg xl:flex"
      aria-label={t(lang, "sidebar.nav_label")}
      role="navigation"
    >
      <div className="flex-1 overflow-y-auto px-5 py-7">
        <Link
          href={langParam(lang, "/explore")}
          className={`mb-6 flex items-center justify-between gap-2 border-l-2 py-2 pl-3 pr-1 text-sm transition-colors ${
            !activeCategory
              ? "border-accent text-fg"
              : "border-transparent text-fg-2 hover:border-dim hover:text-fg"
          }`}
        >
          <span className="flex items-center gap-2 truncate">
            <CategoryMark
              slug="collection"
              size={15}
              className="text-current"
            />
            <span className="truncate font-display">
              {t(lang, "sidebar.all_projects")}
            </span>
          </span>
          <span className="shrink-0 font-mono text-[10px] text-muted">
            {String(totalProjects).padStart(2, "0")}
          </span>
        </Link>

        <div className="space-y-7">
          {CATEGORY_GROUPS.map((group, idx) => {
            const items = group.slugs
              .map((slug) => ({ slug, cat: categories[slug], count: counts[slug] || 0 }))
              .filter(
                (item): item is { slug: string; cat: ProjectCategory; count: number } =>
                  item.cat !== undefined && item.count > 0,
              );
            if (items.length === 0) return null;
            // The active group is always shown expanded, regardless of the
            // user's stored `collapsed` preference. This makes the "auto-
            // expand on navigate" behaviour derive from props at render time
            // rather than being patched in via setState in a useEffect.
            const isCollapsed = group.id !== activeGroupId && Boolean(collapsed[group.id]);
            return (
              <div key={group.id}>
                <button
                  onClick={() => toggle(group.id)}
                  className="editorial-index mb-2 w-full text-left"
                  data-index={String(idx + 1).padStart(2, "0")}
                >
                  <span className="flex shrink-0 items-center gap-2">
                    <GroupMark
                      id={group.id}
                      size={13}
                      className="text-fg-2"
                    />
                    <span className="font-display text-sm text-fg">
                      {t(lang, group.labelKey)}
                    </span>
                  </span>
                </button>
                {!isCollapsed && (
                  <ul className="space-y-0.5">
                    {items.map(({ slug, cat, count }) => {
                      const isActive = activeCategory === slug;
                      return (
                        <li key={slug}>
                          <Link
                            href={withLang(lang, `/explore?category=${slug}`)}
                            className={`group flex items-center justify-between gap-2 border-l-2 px-3 py-1.5 text-[13px] transition-colors ${
                              isActive
                                ? "border-accent bg-bg-sunk text-fg"
                                : "border-transparent text-fg-2 hover:border-dim hover:text-fg"
                            }`}
                          >
                            <span className="truncate">{cat.name}</span>
                            <span
                              className={`shrink-0 font-mono text-[10px] ${
                                isActive ? "text-accent" : "text-muted"
                              }`}
                            >
                              {String(count).padStart(2, "0")}
                            </span>
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
