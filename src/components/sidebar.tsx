"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { ProjectCategory } from "@/types/project";
import { Lang } from "@/lib/i18n";
import { t } from "@/lib/i18n";
import { CATEGORY_GROUPS } from "@/lib/category-groups";

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

  const langParam = (path: string) => (lang !== "en" ? `${path}?lang=${lang}` : path);

  return (
    <aside
      className="hidden lg:flex w-[232px] shrink-0 flex-col border-r border-[#21262d] bg-[#0d1117]"
      aria-label={t(lang, "sidebar.nav_label")}
      role="navigation"
    >
      <div className="flex-1 overflow-y-auto px-3 py-5">
        <Link
          href={langParam("/explore")}
          className={`mb-5 flex items-center justify-between gap-2 rounded-xl px-3 py-2.5 text-sm transition-colors ${
            !activeCategory
              ? "bg-[#161b22] text-[#e6edf3] border border-[#30363d]"
              : "text-[#8b949e] hover:bg-[#161b22] hover:text-[#e6edf3]"
          }`}
        >
          <span className="flex items-center gap-2 truncate">
            <span>📦</span>
            <span className="truncate font-medium">{t(lang, "sidebar.all_projects")}</span>
          </span>
          <span className="shrink-0 rounded-md bg-[#21262d] px-1.5 py-0.5 text-[10px] text-[#6e7681]">
            {totalProjects}
          </span>
        </Link>

        <div className="space-y-4">
          {CATEGORY_GROUPS.map((group) => {
            const items = group.slugs
              .map((slug) => ({ slug, cat: categories[slug], count: counts[slug] || 0 }))
              .filter((item) => item.cat && item.count > 0);
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
                  className="mb-1.5 flex w-full items-center justify-between rounded-md px-1 py-1 text-left"
                >
                  <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[#6e7681]">
                    <span>{group.icon}</span>
                    <span>{t(lang, group.labelKey)}</span>
                  </span>
                  <svg
                    className={`h-3.5 w-3.5 text-[#6e7681] transition-transform duration-200 ${isCollapsed ? "-rotate-90" : ""}`}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {!isCollapsed && (
                  <ul className="space-y-0.5">
                    {items.map(({ slug, cat, count }) => {
                      const isActive = activeCategory === slug;
                      return (
                        <li key={slug}>
                          <Link
                            href={lang !== "en" ? `/explore?category=${slug}&lang=${lang}` : `/explore?category=${slug}`}
                            className={`flex items-center justify-between gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
                              isActive
                                ? "bg-[#161b22] text-[#58a6ff] border border-[#58a6ff]/30"
                                : "text-[#8b949e] hover:bg-[#161b22] hover:text-[#e6edf3]"
                            }`}
                          >
                            <span className="flex items-center gap-2 truncate">
                              <span>{cat.icon}</span>
                              <span className="truncate">{cat.name}</span>
                            </span>
                            <span className="shrink-0 rounded-md bg-[#21262d] px-1.5 py-0.5 text-[10px] text-[#6e7681]">
                              {count}
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
