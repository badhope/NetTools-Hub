import { TreeSidebar } from "@/components/tree-sidebar";
import { TopNav } from "@/components/top-nav";
import { ReactNode } from "react";
import type { ProjectKind, ProjectPlatform } from "@/types/project";

interface ExploreLayoutProps {
  current: { kind?: ProjectKind; platform?: ProjectPlatform };
  kindCounts: Record<string, number>;
  kindPlatformCounts: Record<string, number>;
  total: number;
  lang: "en" | "zh" | "ja";
  title: string;
  meta?: ReactNode;
  breadcrumb?: ReactNode;
  children: ReactNode;
}

/**
 * Shared layout for the /explore/* URL tree.
 *
 *   ┌──────────────────────────────────────────────────────────┐
 *   │  TopNav (site chrome, language switcher)                 │
 *   ├──────────────────────────────────────────────────────────┤
 *   │  breadcrumb   /  kind  /  platform                       │
 *   │  title         "Proxy cores — desktop"                    │
 *   │  meta line     12 entries · 5.4k stars · sorted by ...   │
 *   ├──────────────────────────────────────────────────────────┤
 *   │ ┌──────────┐  ┌──────────────────────────────────────┐  │
 *   │ │ tree     │  │  table                               │  │
 *   │ │ sidebar  │  │                                      │  │
 *   │ └──────────┘  └──────────────────────────────────────┘  │
 *   └──────────────────────────────────────────────────────────┘
 *
 * The tree sidebar is a server component, so no client JS is
 * needed for navigation beyond Next's prefetch (which runs on
 * hover/intersection, not on click — and a click in Next's app
 * router is already a `pushState` round-trip).
 */
export function ExploreLayout({
  current,
  kindCounts,
  kindPlatformCounts,
  total,
  lang,
  title,
  meta,
  breadcrumb,
  children,
}: ExploreLayoutProps) {
  return (
    <div className="min-h-screen bg-bg text-fg">
      <TopNav
        lang={lang}
        kindCounts={kindCounts}
        total={total}
        variant="explore"
        sticky
      />
      <main id="main" className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
        <header className="mb-5 border-b border-line pb-4">
          {breadcrumb}
          <h1 className="mt-2 text-[1.5rem] font-semibold leading-tight text-fg">
            {title}
          </h1>
          {meta && <div className="mt-1">{meta}</div>}
        </header>
        <div className="flex flex-col gap-6 lg:flex-row">
          <TreeSidebar
            current={current}
            kindCounts={kindCounts}
            kindPlatformCounts={kindPlatformCounts}
            total={total}
            lang={lang}
          />
          <div className="min-w-0 flex-1 overflow-x-auto">{children}</div>
        </div>
      </main>
    </div>
  );
}
