'use client';

import { TreeSidebar } from '@/components/tree-sidebar';
import { TopNav } from '@/components/top-nav';
import { ReactNode } from 'react';
import type { ProjectKind, ProjectPlatform } from '@/types/project';

interface ExploreLayoutProps {
  current: { kind?: ProjectKind; platform?: ProjectPlatform };
  kindCounts: Record<string, number>;
  kindPlatformCounts: Record<string, number>;
  total: number;
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
 * The language is read from the `LangProvider` context by the
 * children (TopNav, TreeSidebar, Breadcrumb) so a switch in the
 * top nav re-renders the labels, tree titles, and breadcrumbs
 * without a full page reload. The `title` and `meta` props are
 * still passed in from the page because they are page-specific
 * and not in the i18n key space.
 */
export function ExploreLayout({
  current,
  kindCounts,
  kindPlatformCounts,
  total,
  title,
  meta,
  breadcrumb,
  children,
}: ExploreLayoutProps) {
  return (
    <div className="min-h-screen bg-bg text-fg">
      <TopNav kindCounts={kindCounts} total={total} variant="explore" sticky />
      <main id="main" className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
        <header className="mb-5 border-b border-line pb-4">
          {breadcrumb}
          <h1 className="mt-2 text-[1.5rem] font-semibold leading-tight text-fg">{title}</h1>
          {meta && <div className="mt-1">{meta}</div>}
        </header>
        <div className="flex flex-col gap-6 lg:flex-row">
          <TreeSidebar
            current={current}
            kindCounts={kindCounts}
            kindPlatformCounts={kindPlatformCounts}
            total={total}
          />
          <div className="min-w-0 flex-1 overflow-x-auto">{children}</div>
        </div>
      </main>
    </div>
  );
}
