'use client';

import { TreeSidebar } from '@/components/tree-sidebar';
import { TopNav } from '@/components/top-nav';
import { ExploreMeta } from '@/components/explore-meta';
import { useLang } from '@/components/lang-provider';
import { t } from '@/lib/i18n';
import { kindLabel, platformLabel } from '@/lib/taxonomy';
import { ReactNode } from 'react';
import type { ProjectKind, ProjectPlatform } from '@/types/project';

interface ExploreLayoutProps {
  current: { kind?: ProjectKind; platform?: ProjectPlatform };
  kindCounts: Record<string, number>;
  kindPlatformCounts: Record<string, number>;
  total: number;
  /** Structured title data; the layout renders it with i18n. */
  titleData: {
    type: 'all' | 'kind' | 'platform' | 'project';
    kind?: ProjectKind;
    platform?: ProjectPlatform;
    projectName?: string;
    projectKind?: ProjectKind;
  };
  /** Structured meta data; the layout renders it with i18n. */
  metaData: {
    variant: 'all' | 'kind' | 'platform' | 'project';
    count: number;
    totalStars?: number;
    kind?: ProjectKind;
    projectName?: string;
    projectStars?: number;
    projectLanguage?: string;
  };
  breadcrumb?: ReactNode;
  children: ReactNode;
}

/**
 * Shared layout for the /explore/* URL tree.
 *
 * Reads the active language from LangProvider so the title, meta
 * line, tree sidebar, and breadcrumbs all re-render on language
 * switch without a full page reload.
 */
export function ExploreLayout({
  current,
  kindCounts,
  kindPlatformCounts,
  total,
  titleData,
  metaData,
  breadcrumb,
  children,
}: ExploreLayoutProps) {
  const { lang } = useLang();

  // Compute the page title from structured data + i18n.
  let title: string;
  switch (titleData.type) {
    case 'all':
      title = t(lang, 'explore.all_projects');
      break;
    case 'kind':
      title = `${kindLabel(titleData.kind!, lang)} (${titleData.kind})`;
      break;
    case 'platform':
      title = `${platformLabel(titleData.platform!, lang)} · ${kindLabel(titleData.kind!, lang)}`;
      break;
    case 'project':
      title = `${titleData.projectName} — ${titleData.projectKind}`;
      break;
  }

  return (
    <div className="min-h-screen bg-bg text-fg">
      <TopNav kindCounts={kindCounts} total={total} variant="explore" sticky />
      <main id="main" className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
        <header className="mb-5 border-b border-line pb-4">
          {breadcrumb}
          <h1 className="mt-2 text-[1.5rem] font-semibold leading-tight text-fg">{title}</h1>
          <div className="mt-1">
            <ExploreMeta {...metaData} />
          </div>
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
