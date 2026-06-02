"use client";

import { useState, useEffect, useCallback } from "react";
import { Sidebar } from "@/components/sidebar";
import { StatsBar } from "@/components/stats-bar";
import { SearchBar } from "@/components/search-bar";
import { SortSelect } from "@/components/sort-select";
import { ProjectList } from "@/components/project-list";
import { TopNav } from "@/components/top-nav";
import {
  getAllProjects,
  searchProjects,
  getCategoryCounts,
  getCategories,
} from "@/lib/projects";
import { t, Lang } from "@/lib/i18n";
import { SortOption } from "@/types/project";
import { getGroupOfSlug } from "@/lib/category-groups";

function isValidLang(value: string | null): value is Lang {
  return value === "en" || value === "zh" || value === "ja";
}

export function ExploreContent() {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortOption>("default");
  const [category, setCategory] = useState("");
  const [lang, setLang] = useState<Lang>("en");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const urlLang = params.get("lang");
    if (isValidLang(urlLang)) setLang(urlLang);
    const urlQuery = params.get("q") || "";
    if (urlQuery) setQuery(urlQuery);
    const urlSort = (params.get("sort") as SortOption) || "default";
    if (["default", "stars", "name", "updated"].includes(urlSort)) setSort(urlSort);
    const urlCat = params.get("category") || "";
    if (urlCat) setCategory(urlCat);
  }, []);

  const syncUrl = useCallback((updates: Record<string, string | null>) => {
    if (typeof window === "undefined") return;
    const url = new URL(window.location.href);
    for (const [k, v] of Object.entries(updates)) {
      if (v === null || v === "") url.searchParams.delete(k);
      else url.searchParams.set(k, v);
    }
    window.history.replaceState({}, "", url.toString());
  }, []);

  const handleLangChange = (newLang: Lang) => {
    setLang(newLang);
    syncUrl({ lang: newLang === "en" ? null : newLang });
    try {
      window.localStorage.setItem("nethub.lang", newLang);
    } catch {
      /* storage may be disabled */
    }
    window.dispatchEvent(new CustomEvent("nethub:langchange", { detail: { lang: newLang } }));
  };

  const handleQueryChange = (newQuery: string) => {
    setQuery(newQuery);
    syncUrl({ q: newQuery || null });
  };

  const handleSortChange = (newSort: SortOption) => {
    setSort(newSort);
    syncUrl({ sort: newSort === "default" ? null : newSort });
  };

  const allProjects = getAllProjects();
  const filtered = query
    ? searchProjects(query, category || undefined)
    : category
    ? allProjects.filter((p) => p.category === category)
    : allProjects;
  const stats = getCategoryCounts();
  const categories = getCategories();
  const totalStars = allProjects.reduce((sum, p) => sum + p.stars, 0);
  const categoryCount = Object.keys(stats).length;
  const activeGroup = category ? getGroupOfSlug(category) : undefined;

  return (
    <div className="flex min-h-screen flex-col bg-[#0d1117] text-[#e6edf3]">
      <TopNav
        lang={lang}
        onLangChange={handleLangChange}
        categories={categories}
        counts={stats}
        variant="explore"
      />

      <div className="flex flex-1">
        <Sidebar
          categories={categories}
          counts={stats}
          lang={lang}
          activeCategory={category}
        />

        <main className="min-w-0 flex-1">
          <div className="sticky top-16 z-30 border-b border-[#21262d] bg-[#0d1117]/85 backdrop-blur-md">
            <div className="flex flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
              <StatsBar
                projectCount={allProjects.length}
                categoryCount={categoryCount}
                totalStars={totalStars}
                lang={lang}
              />
              <div className="flex items-center gap-2.5">
                <SearchBar value={query} onChange={handleQueryChange} lang={lang} />
                <SortSelect value={sort} onChange={handleSortChange} lang={lang} />
              </div>
            </div>

            {category && (
              <div className="border-t border-[#21262d] px-4 py-4 sm:px-6">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{categories[category]?.icon || "📁"}</span>
                  <div className="min-w-0 flex-1">
                    <div className="text-[11px] font-medium uppercase tracking-wider text-[#6e7681]">
                      {activeGroup ? t(lang, activeGroup.labelKey) : ""}
                    </div>
                    <h1 className="truncate text-lg font-bold text-[#e6edf3]">
                      {t(lang, "category.header", { name: categories[category]?.name || category.replace(/_/g, " ") })}
                    </h1>
                  </div>
                  <span className="shrink-0 rounded-full border border-[#30363d] bg-[#21262d] px-2.5 py-1 text-xs text-[#8b949e]">
                    {t(lang, "category.count", { count: filtered.length })}
                  </span>
                  <button
                    onClick={() => {
                      setCategory("");
                      syncUrl({ category: null });
                    }}
                    className="shrink-0 rounded-md border border-[#30363d] bg-[#161b22] px-2.5 py-1 text-xs text-[#8b949e] transition-colors hover:border-[#58a6ff] hover:text-[#e6edf3]"
                    aria-label="Clear category"
                  >
                    ✕
                  </button>
                </div>
              </div>
            )}
          </div>

          {filtered.length === 0 ? (
            <div className="flex min-h-[50vh] flex-col items-center justify-center px-4 text-center">
              <span className="text-5xl">🔍</span>
              <h2 className="mt-6 text-lg font-semibold text-[#e6edf3]">
                {t(lang, "empty.title")}
              </h2>
              <p className="mt-3 max-w-md text-sm text-[#8b949e]">
                {t(lang, "empty.description")}
              </p>
              {(query || category) && (
                <button
                  onClick={() => {
                    setQuery("");
                    setCategory("");
                    syncUrl({ q: null, category: null });
                  }}
                  className="mt-8 inline-flex items-center gap-2 rounded-lg border border-[#30363d] bg-[#161b22] px-4 py-2 text-sm text-[#58a6ff] transition-colors hover:bg-[#21262d]"
                >
                  {t(lang, "empty.clear")}
                </button>
              )}
            </div>
          ) : (
            <ProjectList
              projects={filtered}
              sort={sort}
              stats={stats}
              categories={categories}
              lang={lang}
            />
          )}
        </main>
      </div>
    </div>
  );
}
