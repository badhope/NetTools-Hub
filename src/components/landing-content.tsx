"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  getAllProjects,
  getCategoryCounts,
  getCategories,
  getLastUpdated,
} from "@/lib/projects";
import { t, Lang, readLangFromUrl } from "@/lib/i18n";
import { TopNav } from "@/components/top-nav";
import { CATEGORY_GROUPS } from "@/lib/category-groups";
import { GroupMark, SiteMark } from "@/components/category-mark";
import { formatNumber } from "@/lib/utils";

// `lastUpdated` is read from data/projects.json at module load and
// shared across the whole landing render. The field is the source of
// truth for "last indexed" — hard-coding a date here would silently
// drift the moment the data file is updated.
const LAST_UPDATED = getLastUpdated();

// Total stars is derived from the same static dataset, so it can be
// hoisted alongside `LAST_UPDATED` and computed exactly once for the
// lifetime of the bundle.
const TOTAL_STARS = getAllProjects().reduce((sum, p) => sum + p.stars, 0);

const FEATURES = [
  {
    key: "features.curated",
    descKey: "features.curated_desc",
    fig: "06",
  },
  {
    key: "features.search",
    descKey: "features.search_desc",
    fig: "12",
  },
  {
    key: "features.sort",
    descKey: "features.sort_desc",
    fig: "21",
  },
  {
    key: "features.responsive",
    descKey: "features.responsive_desc",
    fig: "30",
  },
  {
    key: "features.maintained",
    descKey: "features.maintained_desc",
    fig: "48",
  },
  {
    key: "features.stars",
    descKey: "features.stars_desc",
    fig: "55",
  },
] as const;

export function LandingContent() {
  const [lang, setLang] = useState<Lang>(readLangFromUrl);

  // Sync the language with the URL on mount and on every popstate
  // (browser back/forward). React 19's `output: "export"` static HTML
  // bakes the page in English regardless of the URL, and the useState
  // lazy initializer is not re-applied during hydration — so this
  // effect is what actually wires ?lang= into the rendered output.
  // The first call (outside the event handler) is a legitimate
  // mount-time cascade; the popstate handler keeps the state aligned
  // with subsequent navigation.
  useEffect(() => {
    const onPop = () => setLang(readLangFromUrl());
    onPop();
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const handleLangChange = (newLang: Lang) => {
    setLang(newLang);
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      if (newLang === "en") url.searchParams.delete("lang");
      else url.searchParams.set("lang", newLang);
      window.history.replaceState({}, "", url.toString());
      try {
        window.localStorage.setItem("nethub.lang", newLang);
      } catch {
        /* storage may be disabled */
      }
      window.dispatchEvent(
        new CustomEvent("nethub:langchange", { detail: { lang: newLang } }),
      );
    }
  };

  // Static, immutable for the lifetime of the bundle — see the
  // module-scope definitions of `LAST_UPDATED` and `TOTAL_STARS`.
  const projects = getAllProjects();
  const counts = getCategoryCounts();
  const categories = getCategories();
  const totalProjects = projects.length;
  const langParam = (path: string) => (lang !== "en" ? `${path}?lang=${lang}` : path);

  return (
    <div className="min-h-screen bg-bg text-fg">
      <TopNav
        lang={lang}
        onLangChange={handleLangChange}
        categories={categories}
        counts={counts}
        variant="landing"
      />

      {/* =========================================================
       *  Plate 0 — Cover / hero
       * ========================================================= */}
      <section className="relative overflow-hidden">
        <div className="mx-auto grid max-w-6xl gap-12 px-5 pb-24 pt-20 sm:px-8 sm:pt-28 lg:grid-cols-[1.2fr_1fr] lg:gap-16 lg:pb-32 lg:pt-32">
          <div className="reveal reveal-1 flex flex-col">
            <div className="mb-8 flex items-center gap-3">
              <span className="kicker">
                {t(lang, "editorial.eyebrow")}
              </span>
              <span className="h-px flex-1 bg-dim" />
              <span className="font-mono text-[10px] text-muted">
                {t(lang, "editorial.plate", { n: "00" })}
              </span>
            </div>

            <h1 className="font-display text-[clamp(2.75rem,7vw,5.5rem)] font-normal leading-[0.96] tracking-[-0.02em] text-fg">
              {lang === "zh" ? "网络工具" : lang === "ja" ? "ネットワークツール" : "Network Tools"}
              <span
                aria-hidden
                className="ml-3 inline-block translate-y-[-0.08em] font-display text-[0.45em] italic text-accent"
                style={{ fontVariationSettings: "'opsz' 144, 'SOFT' 50, 'WONK' 1" }}
              >
                —
              </span>
              <br />
              <span
                className="text-accent"
                style={{ fontVariationSettings: "'opsz' 144" }}
              >
                {lang === "zh"
                  ? "图鉴"
                  : lang === "ja"
                  ? "図鑑"
                  : "An Atlas"}
              </span>
            </h1>

            <p className="mt-8 max-w-xl text-balance text-[15px] leading-[1.7] text-fg-2 sm:text-base">
              {t(lang, "editorial.subtitle", { total: totalProjects })}
            </p>

            <div className="mt-10 flex flex-wrap items-center gap-x-8 gap-y-4">
              <Link
                href={langParam("/explore")}
                className="group inline-flex items-center gap-3 border-b border-accent pb-1.5 font-display text-lg text-accent transition-colors hover:text-accent-hover"
              >
                <span>{t(lang, "editorial.open_atlas")}</span>
                <svg
                  className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="square"
                    d="M5 12h14M13 6l6 6-6 6"
                  />
                </svg>
              </Link>

              <span className="flex items-baseline gap-2 font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-accent" />
                {t(lang, "editorial.last_indexed")} · {LAST_UPDATED}
              </span>
            </div>
          </div>

          {/* Right rail: stats column framed by hairlines */}
          <aside className="reveal reveal-3 flex flex-col gap-6 self-stretch border-l border-dim pl-8 sm:pl-10">
            <span className="kicker">— Compendium</span>
            <dl className="grid grid-cols-1 gap-y-5">
              <div className="flex items-baseline justify-between gap-4 border-b border-line pb-4">
                <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
                  {t(lang, "stats.projects")}
                </dt>
                <dd className="font-display text-3xl leading-none text-fg">
                  {String(totalProjects).padStart(3, "0")}
                </dd>
              </div>
              <div className="flex items-baseline justify-between gap-4 border-b border-line pb-4">
                <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
                  {t(lang, "stats.categories")}
                </dt>
                <dd className="font-display text-3xl leading-none text-fg">
                  {String(CATEGORY_GROUPS.length).padStart(2, "0")}
                </dd>
              </div>
              <div className="flex items-baseline justify-between gap-4 border-b border-line pb-4">
                <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
                  {t(lang, "stats.total_stars")}
                </dt>
                <dd className="font-display text-3xl leading-none text-fg">
                  {(TOTAL_STARS / 1000000).toFixed(1)}
                  <span className="ml-1 text-base text-fg-2">M</span>
                </dd>
              </div>
              <div className="flex items-baseline justify-between gap-4">
                <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
                  {t(lang, "editorial.compiled_by")}
                </dt>
                <dd className="font-mono text-sm text-fg-2">badhope</dd>
              </div>
            </dl>
          </aside>
        </div>

        {/* Editorial divider: a row of typography marks */}
        <div className="mx-auto flex max-w-6xl items-center gap-4 border-t border-line px-5 py-5 sm:px-8">
          <SiteMark size={14} className="shrink-0 text-fg-2" />
          <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
            Folio 01 · Six groups · 21 categories · {formatNumber(TOTAL_STARS, lang)} cumulative stars
          </span>
          <span className="ml-auto font-mono text-[10px] text-muted">
            {t(lang, "editorial.edition", { date: "2026" })}
          </span>
        </div>
      </section>

      {/* =========================================================
       *  Plate I — Why this atlas
       * ========================================================= */}
      <section className="border-t border-line">
        <div className="mx-auto max-w-6xl px-5 py-20 sm:px-8 sm:py-24">
          <header className="mb-12 flex flex-col gap-3 sm:flex-row sm:items-baseline sm:justify-between">
            <div>
              <span className="kicker">
                {t(lang, "editorial.plate", { n: "I" })} —{" "}
                {t(lang, "editorial.section.why")}
              </span>
              <h2 className="mt-3 font-display text-3xl leading-tight text-fg sm:text-4xl">
                {t(lang, "features.title")}
              </h2>
            </div>
            <p className="max-w-sm text-sm leading-relaxed text-fg-2">
              {t(lang, "features.subtitle")}
            </p>
          </header>

          <ul className="grid grid-cols-1 gap-x-10 gap-y-10 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f, i) => (
              <li
                key={f.key}
                className={`reveal reveal-${Math.min(i + 1, 8)} flex flex-col gap-3`}
              >
                <span className="editorial-index" data-index={f.fig}>
                  <span className="font-mono text-[11px] text-muted">
                    {t(lang, f.key, { total: totalProjects, stars: (TOTAL_STARS / 1000000).toFixed(1) })}
                  </span>
                </span>
                <p className="text-[13.5px] leading-[1.7] text-fg-2">
                  {t(lang, f.descKey)}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* =========================================================
       *  Plate II — The six groups (asymmetric atlas grid)
       * ========================================================= */}
      <section className="border-t border-line bg-bg-sunk/40">
        <div className="mx-auto max-w-6xl px-5 py-20 sm:px-8 sm:py-24">
          <header className="mb-12 flex flex-col gap-3 sm:flex-row sm:items-baseline sm:justify-between">
            <div>
              <span className="kicker">
                {t(lang, "editorial.plate", { n: "II" })} —{" "}
                {t(lang, "editorial.section.groups")}
              </span>
              <h2 className="mt-3 font-display text-3xl leading-tight text-fg sm:text-4xl">
                {t(lang, "categories.title")}
              </h2>
            </div>
            <p className="max-w-sm text-sm leading-relaxed text-fg-2">
              {t(lang, "categories.subtitle")}
            </p>
          </header>

          <div className="grid grid-cols-1 gap-px bg-line sm:grid-cols-2 lg:grid-cols-3">
            {CATEGORY_GROUPS.map((group, gIdx) => {
              const items = group.slugs
                .map((slug) => ({ slug, cat: categories[slug], count: counts[slug] || 0 }))
                .filter(
                  (item): item is { slug: string; cat: { name: string; icon: string; description: string; color: string[] }; count: number } =>
                    item.cat !== undefined && item.count > 0,
                );
              if (items.length === 0) return null;
              const total = items.reduce((a, b) => a + b.count, 0);
              return (
                <article
                  key={group.id}
                  className="reveal group relative flex flex-col gap-5 bg-bg p-6 transition-colors duration-300 hover:bg-bg-elev sm:p-7"
                >
                  <header className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-[10px] text-muted">
                        {String(gIdx + 1).padStart(2, "0")}
                      </span>
                      <GroupMark
                        id={group.id}
                        size={26}
                        className="text-fg-2 transition-colors group-hover:text-accent"
                      />
                    </div>
                    <span className="font-mono text-[11px] text-muted">
                      {String(total).padStart(2, "0")}
                    </span>
                  </header>
                  <h3 className="font-display text-xl text-fg transition-colors group-hover:text-accent">
                    {t(lang, group.labelKey)}
                  </h3>
                  <ul className="space-y-1.5">
                    {items.map(({ slug, cat, count }) => (
                      <li key={slug}>
                        <Link
                          href={
                            lang !== "en"
                              ? `/explore?category=${slug}&lang=${lang}`
                              : `/explore?category=${slug}`
                          }
                          className="group/link flex items-center justify-between gap-2 py-1 text-[13px] text-fg-2 transition-colors hover:text-fg"
                        >
                          <span className="flex items-center gap-2 truncate">
                            <span
                              aria-hidden
                              className="inline-block h-px w-2 bg-dim transition-colors group-hover/link:bg-accent"
                            />
                            <span className="truncate">{cat.name}</span>
                          </span>
                          <span className="shrink-0 font-mono text-[10px] text-muted">
                            {String(count).padStart(2, "0")}
                          </span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      {/* =========================================================
       *  Plate III — Begin reading
       * ========================================================= */}
      <section className="border-t border-line">
        <div className="mx-auto max-w-4xl px-5 py-24 text-center sm:py-32">
          <span className="kicker">
            {t(lang, "editorial.plate", { n: "III" })} —{" "}
            {t(lang, "editorial.section.begin")}
          </span>
          <h2 className="mx-auto mt-5 max-w-2xl font-display text-4xl leading-[1.05] text-fg sm:text-5xl">
            {t(lang, "cta.title")}
          </h2>
          <p className="mx-auto mt-6 max-w-md text-sm leading-relaxed text-fg-2">
            {t(lang, "cta.description")}
          </p>
          <div className="mt-10 flex items-center justify-center gap-6">
            <Link
              href={langParam("/explore")}
              className="group inline-flex items-center gap-3 border-b border-accent pb-1.5 font-display text-lg text-accent transition-colors hover:text-accent-hover"
            >
              <span>{t(lang, "editorial.continue_reading")}</span>
              <svg
                className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="square"
                  d="M5 12h14M13 6l6 6-6 6"
                />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* =========================================================
       *  Colophon
       * ========================================================= */}
      <footer className="border-t border-line bg-bg-sunk/50">
        <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8">
          <div className="grid grid-cols-1 gap-10 sm:grid-cols-3">
            <div>
              <span className="kicker">{t(lang, "editorial.colophon")}</span>
              <div className="mt-3 flex items-center gap-2.5 text-fg">
                <SiteMark size={20} className="text-accent" />
                <span className="font-display text-lg">{t(lang, "site.title")}</span>
              </div>
              <p className="mt-3 max-w-xs text-sm leading-relaxed text-fg-2">
                {t(lang, "footer.text")}
              </p>
            </div>
            <div>
              <span className="kicker">— {t(lang, "editorial.compiled_by")}</span>
              <p className="mt-3 font-display text-lg text-fg">badhope</p>
              <p className="mt-1 text-[13px] text-fg-2">
                <a
                  href="https://github.com/badhope/NetTools-Hub"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="link-editorial"
                >
                  github.com/badhope/NetTools-Hub
                </a>
              </p>
            </div>
            <div>
              <span className="kicker">— {t(lang, "editorial.last_indexed")}</span>
              <p className="mt-3 font-display text-lg text-fg">{LAST_UPDATED}</p>
              <p className="mt-3 max-w-xs text-[11px] leading-relaxed text-muted">
                {t(lang, "footer.disclaimer")}
              </p>
            </div>
          </div>
          <div className="mt-10 flex flex-col items-start justify-between gap-2 border-t border-line pt-5 font-mono text-[10px] uppercase tracking-[0.2em] text-muted sm:flex-row sm:items-center">
            <span>
              {t(lang, "editorial.edition", { date: "2026" })}
            </span>
            <span>© badhope · Set in Fraunces, Instrument Sans, JetBrains Mono</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
