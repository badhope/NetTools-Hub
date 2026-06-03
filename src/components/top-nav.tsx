"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { Lang, t } from "@/lib/i18n";
import { LanguageSwitcher } from "@/components/language-switcher";
import { CATEGORY_GROUPS } from "@/lib/category-groups";
import { ProjectCategory } from "@/types/project";
import { SiteMark, GroupMark } from "@/components/category-mark";

interface TopNavProps {
  lang: Lang;
  onLangChange?: (lang: Lang) => void;
  categories: Record<string, ProjectCategory>;
  counts: Record<string, number>;
  variant: "landing" | "explore";
}

export function TopNav({ lang, onLangChange, categories, counts, variant }: TopNavProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(CATEGORY_GROUPS.map((g) => [g.id, true])),
  );
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const panelRef = useRef<HTMLDivElement | null>(null);

  // Scroll-lock the page when the mobile drawer is open. We remember
  // the previous overflow value so that whatever rule the page already
  // had in place (e.g. `auto`) is restored when the drawer closes —
  // blindly setting `body.style.overflow = ""` would clobber it.
  useEffect(() => {
    if (!mobileOpen) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previous;
    };
  }, [mobileOpen]);

  // Close the drawer on Escape, and trap focus inside it while it is
  // open. The trap is a minimal but correct two-step: when Tab would
  // move past the last focusable element, wrap back to the close
  // button; when Shift+Tab would move past the close button, wrap to
  // the last focusable element. The close button receives focus on
  // open and the trigger receives focus back on close so the user's
  // keyboard position is preserved.
  useEffect(() => {
    if (!mobileOpen) return;
    const panel = panelRef.current;
    // Snapshot the trigger ref now (not in the cleanup) — by the time
    // cleanup runs the component may have re-rendered with a fresh
    // ref value, and focusing the wrong button is a small but real
    // a11y bug.
    const trigger = triggerRef.current;
    const focusables = () =>
      panel
        ? Array.from(
            panel.querySelectorAll<HTMLElement>(
              'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
            ),
          )
        : [];
    const closeBtn = panel?.querySelector<HTMLElement>("[data-drawer-close]");
    closeBtn?.focus();

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        setMobileOpen(false);
        return;
      }
      if (e.key !== "Tab") return;
      const items = focusables();
      if (items.length === 0) return;
      const first = items[0]!;
      const last = items[items.length - 1]!;
      const active = document.activeElement as HTMLElement | null;
      if (e.shiftKey && active === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && active === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      trigger?.focus();
    };
  }, [mobileOpen]);

  // Closing the drawer on language change is part of the spec: the
  // language switcher in the mobile drawer (`onChange`) and the one in
  // the top bar both call this, and leaving the drawer up after the
  // copy under it has re-rendered would be visually confusing.
  const handleLangChange = useCallback(
    (next: Lang) => {
      onLangChange?.(next);
      setMobileOpen(false);
    },
    [onLangChange],
  );

  const langParam = (path: string) => (lang !== "en" ? `${path}?lang=${lang}` : path);
  const homeHref = langParam("/");
  const exploreHref = langParam("/explore");
  const primaryCta = variant === "landing" ? t(lang, "editorial.open_atlas") : t(lang, "nav.home");
  const primaryHref = variant === "landing" ? exploreHref : homeHref;

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-line bg-bg/85 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6">
          <Link
            href={homeHref}
            className="group flex shrink-0 items-center gap-2.5 text-fg"
          >
            <SiteMark
              size={22}
              className="text-accent transition-transform duration-500 group-hover:rotate-45"
            />
            <span className="hidden font-display text-[1.05rem] font-medium leading-none tracking-tight sm:inline">
              {t(lang, "site.title")}
            </span>
          </Link>

          <span
            aria-hidden
            className="hidden h-5 w-px shrink-0 bg-dim md:inline-block"
          />

          <span className="kicker hidden md:inline-block">
            {t(lang, "editorial.edition", { date: "2026" })}
          </span>

          <div className="flex-1" />

          <LanguageSwitcher lang={lang} onChange={onLangChange} />

          <Link
            href={primaryHref}
            className="link-editorial inline-flex h-9 items-center gap-2 px-1 text-sm"
          >
            <span className="hidden sm:inline">{primaryCta}</span>
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="square"
                strokeLinejoin="miter"
                d="M5 12h14M13 6l6 6-6 6"
              />
            </svg>
          </Link>

          <button
            ref={triggerRef}
            onClick={() => setMobileOpen(true)}
            className="inline-flex h-9 w-9 items-center justify-center border border-dim text-fg-2 transition-colors hover:border-accent hover:text-accent lg:hidden"
            aria-label={t(lang, "nav.menu")}
            aria-expanded={mobileOpen}
            aria-controls="mobile-drawer"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path strokeLinecap="square" d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
        </div>
      </header>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-bg/80"
            onClick={() => setMobileOpen(false)}
          />
          <div
            id="mobile-drawer"
            ref={panelRef}
            role="dialog"
            aria-modal="true"
            aria-label={t(lang, "nav.categories")}
            className="absolute inset-y-0 right-0 flex w-[min(88vw,360px)] flex-col border-l border-line bg-bg-elev"
          >
            <div className="flex h-16 shrink-0 items-center justify-between border-b border-line px-5">
              <span className="kicker">{t(lang, "nav.categories")}</span>
              <button
                data-drawer-close
                onClick={() => setMobileOpen(false)}
                className="text-fg-2 hover:text-accent"
                aria-label={t(lang, "nav.close")}
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path strokeLinecap="square" d="M6 6l12 12M18 6L6 18" />
                </svg>
              </button>
            </div>
            <nav className="flex-1 overflow-y-auto px-4 py-5">
              {CATEGORY_GROUPS.map((group, idx) => {
                const isOpen = expandedGroups[group.id];
                return (
                  <div key={group.id} className="mb-5 last:mb-0">
                    <button
                      onClick={() =>
                        setExpandedGroups((prev) => ({
                          ...prev,
                          [group.id]: !prev[group.id],
                        }))
                      }
                      className="editorial-index mb-2 w-full text-left"
                      data-index={String(idx + 1).padStart(2, "0")}
                      aria-expanded={isOpen}
                    >
                      <span className="flex shrink-0 items-center gap-2 text-fg-2">
                        <GroupMark id={group.id} size={14} />
                        <span className="font-display text-sm text-fg">
                          {t(lang, group.labelKey)}
                        </span>
                      </span>
                    </button>
                    {isOpen && (
                      <ul className="space-y-0.5">
                        {group.slugs.map((slug) => {
                          const cat = categories[slug];
                          if (!cat || (counts[slug] || 0) === 0) return null;
                          return (
                            <li key={slug}>
                              <Link
                                href={
                                  lang !== "en"
                                    ? `/explore?category=${slug}&lang=${lang}`
                                    : `/explore?category=${slug}`
                                }
                                onClick={() => setMobileOpen(false)}
                                className="flex items-center justify-between gap-2 px-3 py-2 text-sm text-fg-2 transition-colors hover:bg-bg-sunk hover:text-fg"
                              >
                                <span className="truncate">{cat.name}</span>
                                <span className="font-mono text-[10px] text-muted">
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
            <div className="shrink-0 border-t border-line p-4">
              <LanguageSwitcher lang={lang} onChange={handleLangChange} />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
