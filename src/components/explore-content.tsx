"use client";

import { useState, useEffect, useCallback, useDeferredValue, useMemo, useRef } from "react";
import { Sidebar } from "@/components/sidebar";
import { StatsBar } from "@/components/stats-bar";
import { SearchBar, SearchBarHandle } from "@/components/search-bar";
import { SortSelect } from "@/components/sort-select";
import { ProjectList } from "@/components/project-list";
import { TopNav } from "@/components/top-nav";
import {
  getAllProjects,
  searchProjects,
  getCategoryCounts,
  getCategories,
  getTotalStars,
  getCategoryCount,
} from "@/lib/projects";
import { t, Lang, readLangFromUrl } from "@/lib/i18n";
import { SortOption } from "@/types/project";
import { getGroupOfSlug } from "@/lib/category-groups";
import { CategoryMark } from "@/components/category-mark";

function isValidSort(value: string | null): value is SortOption {
  return value === "default" || value === "stars" || value === "name" || value === "updated";
}

// The dataset is static and immutable for the lifetime of the bundle.
// Hoist these lookups to the module scope so the component body does
// not rebuild the counts map and the categories map on every render.
const ALL_PROJECTS = getAllProjects();
const STATS = getCategoryCounts();
const CATEGORIES = getCategories();
const TOTAL_STARS = getTotalStars();
const CATEGORY_COUNT = getCategoryCount();

// The four URL-driven pieces of state — `lang`, `query`, `sort`,
// `category` — must be initialised with the *server* value during
// `useState`'s lazy initializer. If the client-side `readUrlState`
// returned `?category=foo` while the SSR HTML was rendered without
// the filter, React 19 would throw hydration error #418 ("text
// content did not match") on the first paint.
//
// The URL values are then re-read inside the mount effect (below)
// and applied as a controlled state update. This is the documented
// escape hatch for the `react-hooks/set-state-in-effect` rule:
// `window.location` is only available on the client, so we *must*
// do this inside an effect to avoid a window-touching render on
// the server.
function readUrlState() {
  if (typeof window === "undefined") {
    return { lang: "en" as Lang, query: "", sort: "default" as SortOption, category: "" };
  }
  const sp = new URLSearchParams(window.location.search);
  const sortV = sp.get("sort");
  return {
    lang: readLangFromUrl(),
    query: sp.get("q") ?? "",
    sort: isValidSort(sortV) ? sortV : "default",
    category: sp.get("category") ?? "",
  };
}

export function ExploreContent() {
  // Lazy initializers use the SSR value (always empty / "en" / default).
  // The mount effect below applies the real URL state on the client.
  const [query, setQuery] = useState<string>("");
  const [sort, setSort] = useState<SortOption>("default");
  const [category, setCategory] = useState<string>("");
  const [lang, setLang] = useState<Lang>("en");
  const searchRef = useRef<SearchBarHandle | null>(null);

  // Defer the heavy work of filtering + rendering the (potentially
  // large) result list behind React's scheduler. Typing into the
  // search box updates `query` immediately (so the input stays
  // responsive), but the actual filter+render of the project grid
  // happens on `deferredQuery`, which is allowed to lag a frame or
  // two under load. This is the documented pattern for keeping a
  // controlled input snappy against an expensive render.
  const deferredQuery = useDeferredValue(query);

  // Global `/` keyboard shortcut to focus the search box. The
  // `keydown` listener is attached to the document and the
  // handler ignores the event when the user is already typing in
  // any other input/textarea/contenteditable element, so the `/`
  // key stays usable in the search box itself and in the sort
  // dropdown. This is the de-facto search-shortcut convention
  // (GitHub, Algolia docs, Linear all do the same).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "/") return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const target = e.target as HTMLElement | null;
      if (target) {
        const tag = target.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA" || target.isContentEditable) return;
      }
      e.preventDefault();
      searchRef.current?.focus();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  // Sync the four URL-driven pieces of state on mount and on every
  // popstate (browser back/forward). This is the documented escape
  // hatch for the `react-hooks/set-state-in-effect` rule:
  // `readUrlState()` reads `window.location`, which is only available
  // on the client, so we *must* do this inside an effect to avoid
  // a window-touching render on the server. The four setState calls
  // fire on the same event tick so React batches them into a single
  // re-render.
  useEffect(() => {
    const onPop = () => {
      const next = readUrlState();
      setLang(next.lang);
      setQuery(next.query);
      setSort(next.sort);
      setCategory(next.category);
    };
    onPop();
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
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

  // `deferredQuery` is what drives the actual filter+render, so the
  // filter is recomputed against the deferred value (and so does
  // not block the input). The result is memoised by the same
  // (deferredQuery, category) key, so a re-render that re-uses the
  // same values returns the same array reference and skips the
  // ProjectList work entirely.
  const filtered = useMemo(() => {
    if (deferredQuery) return searchProjects(deferredQuery, category || undefined);
    if (category) return ALL_PROJECTS.filter((p) => p.category === category);
    return ALL_PROJECTS;
  }, [deferredQuery, category]);

  const activeGroup = category ? getGroupOfSlug(category) : undefined;

  return (
    <div className="flex min-h-screen flex-col bg-bg text-fg">
      <TopNav
        lang={lang}
        onLangChange={handleLangChange}
        categories={CATEGORIES}
        counts={STATS}
        variant="explore"
      />

      <div className="flex flex-1">
        <Sidebar
          categories={CATEGORIES}
          counts={STATS}
          lang={lang}
          activeCategory={category}
        />

        <main
          id="main"
          aria-label={t(lang, "a11y.main")}
          className="min-w-0 flex-1"
        >
          <div className="sticky top-16 z-30 border-b border-line bg-bg/85 backdrop-blur-md">
            <div className="flex flex-col gap-5 px-5 py-5 sm:flex-row sm:items-end sm:justify-between sm:px-8">
              <StatsBar
                projectCount={ALL_PROJECTS.length}
                categoryCount={CATEGORY_COUNT}
                totalStars={TOTAL_STARS}
                lang={lang}
              />
              <div className="flex items-center gap-3">
                <SearchBar
                  ref={searchRef}
                  value={query}
                  onChange={handleQueryChange}
                  lang={lang}
                  shortcutHint={t(lang, "search.shortcut_hint")}
                />
                <SortSelect value={sort} onChange={handleSortChange} lang={lang} />
              </div>
            </div>

            {category && (
              <div className="border-t border-line px-5 py-5 sm:px-8">
                <div className="flex flex-wrap items-end justify-between gap-4">
                  <div className="flex min-w-0 items-end gap-4">
                    <CategoryMark
                      slug={category}
                      size={32}
                      className="shrink-0 text-fg-2"
                    />
                    <div className="min-w-0">
                      <div className="kicker">
                        {activeGroup
                          ? `${t(lang, "editorial.plate", { n: activeGroup.id.toUpperCase() })} — ${t(lang, activeGroup.labelKey)}`
                          : t(lang, "editorial.section.curated")}
                      </div>
                      <h1 className="mt-1 truncate font-display text-2xl leading-tight text-fg sm:text-3xl">
                        {t(lang, "category.header", {
                          name: CATEGORIES[category]?.name || category.replace(/_/g, " "),
                        })}
                      </h1>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 font-mono text-[11px] text-muted">
                    {/* `aria-live="polite"` lets screen-reader users hear
                     *  the new result count without it interrupting the
                     *  user mid-typing. */}
                    <span aria-live="polite">
                      {t(lang, "list.results_count", { count: filtered.length })}
                    </span>
                    <button
                      onClick={() => {
                        setCategory("");
                        syncUrl({ category: null });
                      }}
                      className="link-editorial inline-flex items-center gap-1.5"
                      aria-label={t(lang, "empty.clear")}
                    >
                      <svg
                        className="h-3 w-3"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth={1.5}
                      >
                        <path
                          strokeLinecap="square"
                          d="M6 6l12 12M18 6L6 18"
                        />
                      </svg>
                      <span>{t(lang, "empty.clear")}</span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {filtered.length === 0 ? (
            <div className="flex min-h-[50vh] flex-col items-center justify-center px-4 text-center">
              <span className="font-display text-4xl text-fg-2">
                {t(lang, "empty.title")}
              </span>
              <p className="mt-3 max-w-md text-sm text-fg-2">
                {t(lang, "empty.description")}
              </p>
              {(query || category) && (
                <button
                  onClick={() => {
                    setQuery("");
                    setCategory("");
                    syncUrl({ q: null, category: null });
                  }}
                  className="mt-8 link-editorial inline-flex items-center gap-1.5"
                >
                  <span>{t(lang, "empty.clear")}</span>
                </button>
              )}
            </div>
          ) : (
            <ProjectList
              projects={filtered}
              sort={sort}
              stats={STATS}
              categories={CATEGORIES}
              lang={lang}
            />
          )}
        </main>
      </div>
    </div>
  );
}
