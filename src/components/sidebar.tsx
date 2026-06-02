"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { ProjectCategory, Lang } from "@/types/project";
import { t } from "@/lib/i18n";
import { CATEGORY_GROUPS } from "@/lib/category-groups";

interface SidebarProps {
  categories: Record<string, ProjectCategory>;
  counts: Record<string, number>;
  lang: Lang;
  activeCategory?: string;
}

export function Sidebar({ categories, counts, lang, activeCategory }: SidebarProps) {
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const totalProjects = Object.values(counts).reduce((a, b) => a + b, 0);

  useEffect(() => {
    if (activeCategory) {
      const group = CATEGORY_GROUPS.find((g) => g.slugs.includes(activeCategory));
      if (group) {
        setCollapsed((prev) => (prev[group.id] ? prev : { ...prev, [group.id]: false }));
      }
    }
  }, [activeCategory]);

  const toggle = useCallback((id: string) => {
    setCollapsed((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

  const langParam = (path: string) => (lang !== "en" ? `${path}?lang=${lang}` : path);

  return (
    <aside
      className="hidden lg:flex w-64 shrink-0 flex-col border-r border-[#21262d] bg-[#0d1117]"
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
            const isCollapsed = collapsed[group.id];
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

      <div className="border-t border-[#21262d] px-5 py-4 text-[11px] text-[#6e7681]">
        <div className="flex items-center justify-between">
          <span>{t(lang, "footer.text")}</span>
        </div>
      </div>
    </aside>
  );
}
