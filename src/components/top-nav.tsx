"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { Lang, t } from "@/lib/i18n";
import { LanguageSwitcher } from "@/components/language-switcher";
import { CATEGORY_GROUPS } from "@/lib/category-groups";
import { ProjectCategory } from "@/types/project";

interface TopNavProps {
  lang: Lang;
  onLangChange?: (lang: Lang) => void;
  categories: Record<string, ProjectCategory>;
  counts: Record<string, number>;
  variant: "landing" | "explore";
}

export function TopNav({ lang, onLangChange, categories, counts, variant }: TopNavProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(CATEGORY_GROUPS.map((g) => [g.id, true])),
  );
  const [activeGroup, setActiveGroup] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!menuOpen) return;
    const onClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
        setActiveGroup(null);
      }
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [menuOpen]);

  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  const openMenu = useCallback(() => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    setMenuOpen(true);
  }, []);

  const scheduleClose = useCallback(() => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    closeTimer.current = setTimeout(() => {
      setMenuOpen(false);
      setActiveGroup(null);
    }, 150);
  }, []);

  const langParam = (path: string) => (lang !== "en" ? `${path}?lang=${lang}` : path);
  const homeHref = langParam("/");
  const exploreHref = langParam("/explore");
  const primaryCta = variant === "landing" ? t(lang, "nav.explore") : t(lang, "nav.home");
  const primaryHref = variant === "landing" ? exploreHref : homeHref;

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-[#21262d] bg-[#0d1117]/85 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6">
          <Link href={homeHref} className="flex shrink-0 items-center gap-2">
            <span className="text-xl">🛠️</span>
            <span className="hidden bg-gradient-to-r from-[#58a6ff] to-[#3fb950] bg-clip-text text-base font-bold text-transparent sm:inline">
              {t(lang, "site.title")}
            </span>
          </Link>

          <div
            ref={dropdownRef}
            className="relative"
            onMouseLeave={scheduleClose}
          >
            <button
              onClick={() => setMenuOpen((v) => !v)}
              onMouseEnter={openMenu}
              className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[#8b949e] transition-colors hover:bg-[#161b22] hover:text-[#e6edf3]"
              aria-label={t(lang, "nav.categories")}
            >
              <span className="hidden sm:inline">{t(lang, "nav.categories")}</span>
              <span className="sm:hidden">📂</span>
              <svg
                className={`h-3.5 w-3.5 transition-transform duration-200 ${menuOpen ? "rotate-180" : ""}`}
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {menuOpen && (
              <div
                onMouseEnter={openMenu}
                className="absolute left-0 top-full mt-2 w-[min(92vw,680px)] rounded-2xl border border-[#30363d] bg-[#0d1117] p-3 shadow-2xl shadow-black/40"
              >
                <div className="grid grid-cols-1 gap-1 sm:grid-cols-2 lg:grid-cols-3">
                  {CATEGORY_GROUPS.map((group) => (
                    <div
                      key={group.id}
                      className="rounded-xl p-2 transition-colors hover:bg-[#161b22]"
                      onMouseEnter={() => setActiveGroup(group.id)}
                    >
                      <div className="mb-1.5 flex items-center gap-2 px-1">
                        <span>{group.icon}</span>
                        <span className="text-sm font-semibold text-[#e6edf3]">
                          {t(lang, group.labelKey)}
                        </span>
                      </div>
                      <ul className="space-y-0.5">
                        {group.slugs.map((slug) => {
                          const cat = categories[slug];
                          if (!cat || (counts[slug] || 0) === 0) return null;
                          return (
                            <li key={slug}>
                              <Link
                                href={lang !== "en" ? `/explore?category=${slug}&lang=${lang}` : `/explore?category=${slug}`}
                                onClick={() => {
                                  setMenuOpen(false);
                                  setActiveGroup(null);
                                }}
                                className="flex items-center justify-between gap-2 rounded-md px-2 py-1.5 text-sm text-[#8b949e] transition-colors hover:bg-[#21262d] hover:text-[#e6edf3]"
                              >
                                <span className="flex items-center gap-1.5 truncate">
                                  <span>{cat.icon}</span>
                                  <span className="truncate">{cat.name}</span>
                                </span>
                                <span className="shrink-0 rounded bg-[#21262d] px-1.5 py-0.5 text-[10px] text-[#6e7681]">
                                  {counts[slug] || 0}
                                </span>
                              </Link>
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex-1" />

          <LanguageSwitcher lang={lang} onChange={onLangChange} />

          {variant === "explore" ? (
            <Link
              href={homeHref}
              className="hidden items-center gap-1.5 rounded-lg border border-[#30363d] bg-[#161b22] px-3.5 py-2 text-sm text-[#8b949e] transition-colors hover:border-[#58a6ff] hover:text-[#e6edf3] sm:inline-flex"
            >
              ← {t(lang, "nav.home")}
            </Link>
          ) : null}

          <Link
            href={primaryHref}
            className="inline-flex items-center gap-1.5 rounded-lg bg-[#238636] px-3.5 py-2 text-sm font-medium text-white transition-colors hover:bg-[#2ea043]"
          >
            {primaryCta}
            {variant === "landing" && (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            )}
          </Link>

          <button
            onClick={() => setMobileOpen(true)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-[#30363d] bg-[#161b22] text-[#8b949e] transition-colors hover:text-[#e6edf3] lg:hidden"
            aria-label={t(lang, "nav.menu")}
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </header>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/70" onClick={() => setMobileOpen(false)} />
          <div className="absolute inset-y-0 right-0 flex w-[min(88vw,360px)] flex-col border-l border-[#30363d] bg-[#0d1117]">
            <div className="flex h-16 shrink-0 items-center justify-between border-b border-[#21262d] px-5">
              <span className="bg-gradient-to-r from-[#58a6ff] to-[#3fb950] bg-clip-text text-base font-bold text-transparent">
                {t(lang, "nav.categories")}
              </span>
              <button
                onClick={() => setMobileOpen(false)}
                className="rounded-md p-1.5 text-[#8b949e] hover:bg-[#161b22] hover:text-[#e6edf3]"
                aria-label={t(lang, "nav.close")}
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <nav className="flex-1 overflow-y-auto p-4 space-y-5">
              {CATEGORY_GROUPS.map((group) => {
                const isOpen = expandedGroups[group.id];
                return (
                  <div key={group.id}>
                    <button
                      onClick={() =>
                        setExpandedGroups((prev) => ({ ...prev, [group.id]: !prev[group.id] }))
                      }
                      className="mb-2 flex w-full items-center justify-between rounded-lg px-1 py-1 text-sm font-semibold text-[#e6edf3]"
                    >
                      <span className="flex items-center gap-2">
                        <span>{group.icon}</span>
                        <span>{t(lang, group.labelKey)}</span>
                      </span>
                      <svg
                        className={`h-4 w-4 text-[#6e7681] transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
                        fill="none" viewBox="0 0 24 24" stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {isOpen && (
                      <ul className="space-y-0.5">
                        {group.slugs.map((slug) => {
                          const cat = categories[slug];
                          if (!cat || (counts[slug] || 0) === 0) return null;
                          return (
                            <li key={slug}>
                              <Link
                                href={lang !== "en" ? `/explore?category=${slug}&lang=${lang}` : `/explore?category=${slug}`}
                                onClick={() => setMobileOpen(false)}
                                className="flex items-center justify-between gap-2 rounded-lg px-3 py-2 text-sm text-[#8b949e] transition-colors hover:bg-[#161b22] hover:text-[#e6edf3]"
                              >
                                <span className="flex items-center gap-2 truncate">
                                  <span>{cat.icon}</span>
                                  <span className="truncate">{cat.name}</span>
                                </span>
                                <span className="shrink-0 rounded bg-[#21262d] px-1.5 py-0.5 text-[10px] text-[#6e7681]">
                                  {counts[slug] || 0}
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
            </nav>
          </div>
        </div>
      )}
    </>
  );
}
