"use client";

import { useState, useEffect, useDeferredValue, useMemo, useRef, useCallback } from "react";
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
import { useClientLang } from "@/lib/use-client-lang";
import { t } from "@/lib/i18n";
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

// Read the three URL-driven filter values (`q`, `sort`, `category`).
//
// This is intentionally client-only: it touches `window.location`.
// The component's `useState` initializers must NOT call it directly
// — the static prerender runs them on the server, where `window` is
// undefined, and the call would also mismatch the prerender's empty
// state. The first read happens in the mount effect, which is fine
// because effects only run on the client after hydration.
//
// Kept as a module-scope helper (not a hook) because it has no React
// dependencies — it just parses the current URL.
function readUrlFilters(): {
  query: string;
  sort: SortOption;
  category: string;
} {
  const sp = new URLSearchParams(window.location.search);
  const sortV = sp.get("sort");
  return {
    query: sp.get("q") ?? "",
    sort: isValidSort(sortV) ? sortV : "default",
    category: sp.get("category") ?? "",
  };
}

export function ExploreContent() {
  // SSR-safe initial values: always the empty / default state. This
  // matches the prerendered HTML and is the only way to keep React
  // 19 happy during hydration (text content must agree between
  // server render and the *first* client render). The mount effect
  // below swaps in the real URL values once hydration is done.
  const [query, setQuery] = useState<string>("");
  const [sort, setSort] = useState<SortOption>("default");
  const [category, setCategory] = useState<string>("");
  // `lang` and the language setter come from the shared
  // `useClientLang` hook, which now centralises the popstate +
  // `nethub:langchange` coordination for every page that renders
  // localised text (see `lib/use-client-lang.ts`).
  const [lang, handleLangChange] = useClientLang();
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

  // ----------------------------------------------------------------
  // Auto-hide header on scroll-down / show on scroll-up.
  //
  // "上栏可以折叠" — the spec is that swiping *up* (which is what
  // reading a long project list looks like in a touch device) hides
  // the top bar so the project cards get the full viewport height,
  // and swiping *down* (back towards the page top) brings it back.
  // We do this at the `window` scroll level rather than via the
  // pointer events directly: scroll position captures both touch
  // *and* mouse-wheel / track-pad gestures, and a single listener
  // drives both. The "swipe up" gesture *is* "scroll down" on a
  // page that has more content below the fold.
  //
  // The hide / show threshold is 8 px of cumulative delta, not a
  // single event, so jitter around the threshold does not
  // cause the header to flicker. The hide is also suppressed
  // while `scrollY < 120` so the user is always one short swipe
  // away from seeing the navigation again.
  //
  // Desktop users with a fine pointer get the same behaviour,
  // because the header getting out of the way when you scroll
  // through a long list is a universally useful affordance, not
  // a touch-only one.
  // ----------------------------------------------------------------
  const [headerCollapsed, setHeaderCollapsed] = useState(false);
  // `useRef` so the scroll handler always reads the *latest*
  // `headerCollapsed` value without needing to be re-attached on
  // every state flip (which would also drop any in-flight
  // momentum scrolls).
  const headerCollapsedRef = useRef(headerCollapsed);
  useEffect(() => {
    headerCollapsedRef.current = headerCollapsed;
  }, [headerCollapsed]);

  useEffect(() => {
    let lastY = window.scrollY;
    let pendingDelta = 0;
    let rafId: number | null = null;

    // Returns true when keyboard focus is currently inside the
    // sticky header (the tab that the user just used to *expand*
    // it, the search box, the sort dropdown, the language switcher,
    // etc). When that is the case we suppress the auto-collapse so
    // a Tab/Space press does not get "interrupted" by the very
    // element it just revealed disappearing again — which is
    // exactly the kind of jitter that made the previous design
    // confusing to keyboard users.
    const isFocusInsideHeader = () => {
      const active = document.activeElement;
      if (!active || active === document.body) return false;
      // The header is the first <header> ancestor of the focused
      // element. Using `.closest("header")` is robust to the exact
      // wrapping structure (the search bar lives in a sibling
      // section, not inside <header>, so we widen the predicate
      // to "any ancestor within the sticky wrapper", which is
      // identified here by walking up to the wrapper that carries
      // the .sticky top-0 z-40 class set in the JSX below).
      const wrapper = (active as HTMLElement).closest?.(
        ".sticky.top-0",
      );
      return wrapper !== null && wrapper !== undefined;
    };

    const flush = () => {
      rafId = null;
      const y = window.scrollY;
      const netDelta = pendingDelta;
      pendingDelta = 0;
      // Always show the header near the top of the page; the
      // user is one short swipe away from needing it back.
      if (y < 120) {
        if (headerCollapsedRef.current) setHeaderCollapsed(false);
        lastY = y;
        return;
      }
      // Don't yank the chrome away from a keyboard user who
      // just focused something inside it.
      if (isFocusInsideHeader()) {
        lastY = y;
        return;
      }
      if (netDelta > 8 && !headerCollapsedRef.current) {
        // Scrolling down (or finger moving up) past the threshold
        // — hide the header.
        setHeaderCollapsed(true);
      } else if (netDelta < -8 && headerCollapsedRef.current) {
        // Scrolling up (or finger moving down) past the threshold
        // — bring the header back.
        setHeaderCollapsed(false);
      }
      lastY = y;
    };

    const onScroll = () => {
      const y = window.scrollY;
      const delta = y - lastY;
      lastY = y;
      pendingDelta += delta;
      if (rafId !== null) return;
      rafId = window.requestAnimationFrame(flush);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      if (rafId !== null) window.cancelAnimationFrame(rafId);
    };
  }, []);

  // Hydration bridge for the three URL-driven filters.
  //
  //   - On mount, read the real values from the URL and apply them
  //     as controlled state updates. This is the *only* place these
  //     three `useState`s are populated client-side after the empty
  //     SSR render, and the `react-hooks/set-state-in-effect` rule
  //     is satisfied because the `setState` is in the effect body —
  //     i.e. it is exactly the pattern the rule describes as the
  //     legitimate escape hatch (cannot read `window.location`
  //     during render, so the read must happen post-mount).
  //   - On `popstate`, re-apply the URL values so browser
  //     back/forward keeps the filter in sync. The `lang` change
  //     that can ride along on `popstate` is handled by
  //     `useClientLang`, so this listener only touches the three
  //     filter pieces.
  //
  // We do NOT call `onPop()` synchronously inside this effect the
  // way the previous version did — that would set the filter
  // state during the same tick as hydration, and React 19 considers
  // *any* synchronous setState in an effect body a violation of
  // the rule. The mount effect runs after hydration, so a single
  // `setQuery/setSort/setCategory` round trip is all that is
  // needed to apply the URL.
  useEffect(() => {
    const applyFromUrl = () => {
      const next = readUrlFilters();
      setQuery(next.query);
      setSort(next.sort);
      setCategory(next.category);
    };
    applyFromUrl();
    window.addEventListener("popstate", applyFromUrl);
    return () => window.removeEventListener("popstate", applyFromUrl);
  }, []);

  const syncUrl = useCallback((updates: Record<string, string | null>) => {
    if (typeof window === "undefined") return;
    const url = new URL(window.location.href);
    for (const k in updates) {
      const v = updates[k];
      // `updates[k]` is `string | null | undefined` under
      // `noUncheckedIndexedAccess`. `null` and `""` are
      // semantically "remove this key"; `undefined` is the
      // impossible-via-the-public-type path that the `for…in`
      // surfaces — guard it explicitly so the `set()` call sees
      // only `string`.
      if (v === undefined || v === null || v === "") {
        url.searchParams.delete(k);
      } else {
        url.searchParams.set(k, v);
      }
    }
    window.history.replaceState({}, "", url.toString());
  }, []);

  const handleQueryChange = useCallback(
    (newQuery: string) => {
      setQuery(newQuery);
      syncUrl({ q: newQuery || null });
    },
    [syncUrl],
  );

  const handleSortChange = useCallback(
    (newSort: SortOption) => {
      setSort(newSort);
      syncUrl({ sort: newSort === "default" ? null : newSort });
    },
    [syncUrl],
  );

  // Wrap the inline clear-category / clear-all buttons so the
  // `<button onClick={…}>` props stay referentially stable
  // across renders. Without `useCallback` the inline lambdas
  // would re-allocate on every keystroke during search, which
  // forces the `<button>` to re-render (and any React DevTools
  // signal in the profile) even when the rest of the tree
  // hasn't changed.
  const clearCategory = useCallback(() => {
    setCategory("");
    syncUrl({ category: null });
  }, [syncUrl]);

  const clearAll = useCallback(() => {
    setQuery("");
    setCategory("");
    syncUrl({ q: null, category: null });
  }, [syncUrl]);

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

  const clearHeader = useCallback(() => {
    setHeaderCollapsed(false);
    // Tapping the peek tab is also a one-tap "back to top" — that
    // is the natural expectation on a long list (most other
    // apps collapse the header *and* jump you back to the
    // anchor of the page you came from). `behavior: "smooth"`
    // is fine here because we are *not* in a passive scroll
    // listener, so the user gesture is unambiguously a click.
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-bg text-fg">
      {/* The entire top bar — site nav + stats + search + active
       *  category title — is hoisted into a single sticky
       *  wrapper. The inner `<div>` carries the `transform:
       *  translateY(...)` animation, so a `headerCollapsed` flip
       *  smoothly slides the whole 200-ish-pixel chrome out of
       *  the way without leaving a hole. The 32-px `top-0` peek
       *  stays reachable at every scroll position — large enough
       *  to be a comfortable touch target (WCAG 2.2 SC 2.5.8
       *  wants ≥24×24) and big enough to also fit a small text
       *  label + chevron. `will-change-transform` is set on the
       *  inner div so the browser can promote the layer once
       *  and reuse it across the many tiny scroll deltas the
       *  rAF flush coalesces. The wrapper itself is sticky so
       *  the visible tab stays reachable at all scroll positions. */}
      <div className="sticky top-0 z-40">
        <div
          className={`will-change-transform transition-transform duration-300 ease-out motion-reduce:transition-none ${
            headerCollapsed ? "-translate-y-[calc(100%-32px)]" : "translate-y-0"
          }`}
        >
          <TopNav
            lang={lang}
            onLangChange={handleLangChange}
            categories={CATEGORIES}
            counts={STATS}
            variant="explore"
            sticky={false}
          />
          <div className="border-b border-line bg-bg/85 backdrop-blur-md">
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

            <div className="border-t border-line px-5 py-5 sm:px-8">
              <div className="flex flex-wrap items-end justify-between gap-4">
                <div className="flex min-w-0 items-end gap-4">
                  {category ? (
                    <CategoryMark
                      slug={category}
                      size={32}
                      className="shrink-0 text-fg-2"
                    />
                  ) : (
                    <span
                      aria-hidden
                      className="grid h-8 w-8 shrink-0 place-items-center text-fg-3"
                    >
                      {/* Compass mark in lieu of a per-category glyph
                       *  for the un-filtered "all" view. */}
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={1.2}
                      >
                        <circle cx="12" cy="12" r="9" />
                        <path d="M15.5 8.5l-2 5-5 2 2-5z" />
                      </svg>
                    </span>
                  )}
                  <div className="min-w-0">
                    <div className="kicker">
                      {category
                        ? `${t(lang, "editorial.plate", {
                            n: activeGroup
                              ? activeGroup.id.toUpperCase()
                              : "—",
                          })} — ${
                            activeGroup
                              ? t(lang, activeGroup.labelKey)
                              : t(lang, "editorial.section.curated")
                          }`
                        : t(lang, "editorial.section.curated")}
                    </div>
                    <h1 className="mt-1 truncate font-display text-2xl leading-tight text-fg sm:text-3xl">
                      {category
                        ? t(lang, "category.header", {
                            name:
                              CATEGORIES[category]?.name ||
                              category.replace(/_/g, " "),
                          })
                        : t(lang, "explore.title")}
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
                  {category && (
                    <button
                      onClick={clearCategory}
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
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* The "expand" handle: the only piece of the header
         *  that remains visible while `headerCollapsed` is true.
         *  Tapping it (or any downward swipe) brings the rest
         *  back AND smooth-scrolls the page to the top — see
         *  the `clearHeader` callback above.
         *
         *  The button is 32px tall (h-8) so it stays a comfortable
         *  touch target under WCAG 2.2 SC 2.5.8 (≥24×24px) and the
         *  `active:scale-95` gives an immediate press feedback on
         *  touch devices. `aria-label` describes the *action* —
         *  "Show header" — not the visual state, because that is
         *  what the screen reader user is about to invoke. */}
        {headerCollapsed && (
          <button
            type="button"
            onClick={clearHeader}
            aria-label={t(lang, "nav.show_header")}
            className="absolute inset-x-0 top-0 z-10 mx-auto flex h-8 w-28 items-center justify-center gap-1.5 rounded-b-full border border-t-0 border-line bg-bg-elev/90 text-fg-3 backdrop-blur transition-all duration-150 hover:text-accent focus-visible:border-accent focus-visible:text-accent active:scale-95 motion-reduce:transition-none"
          >
            <svg
              aria-hidden
              className="h-3 w-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="square" d="M6 9l6 6 6-6" />
            </svg>
            <span className="font-mono text-[10px] uppercase tracking-[0.18em]">
              {t(lang, "nav.show_header")}
            </span>
          </button>
        )}
      </div>

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
                  onClick={clearAll}
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
