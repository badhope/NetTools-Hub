import { notFound } from 'next/navigation';
import { ExploreLayout } from '@/components/explore-layout';
import { ProjectTable } from '@/components/project-table';
import {
  getAllProjects,
  getKindCounts,
  getKindPlatformCounts,
  isValidKind,
  getProjectsByKind,
} from '@/lib/projects';
import { Breadcrumb, kindCrumb, rootCrumb } from '@/components/breadcrumb';
import { kindLabel } from '@/lib/taxonomy';
import { SITE_CANONICAL } from '@/lib/site';
import { safeJsonLd } from '@/lib/utils';
import type { ProjectKind } from '@/types/project';

export function generateStaticParams() {
  // Pre-render one page per known kind. Static export requires the
  // exhaustive list of valid paths at build time; the array below
  // is the same one the validator accepts as `kind` values.
  return (
    ['proxy', 'vpn', 'dns', 'acceleration', 'security', 'monitoring', 'ops', 'tools'] as const
  ).map((kind) => ({ kind }));
}

export async function generateMetadata({ params }: { params: Promise<{ kind: string }> }) {
  const { kind } = await params;
  if (!isValidKind(kind)) return { title: 'Not found' };
  const list = getProjectsByKind(kind);
  return {
    title: `${kindLabel(kind)} — Explore`,
    description: `${list.length} open-source ${kindLabel(kind).toLowerCase()} tools. Drill down by platform (desktop, mobile, CLI, server, browser, router).`,
  };
}

export default async function KindPage({ params }: { params: Promise<{ kind: string }> }) {
  const { kind } = await params;
  if (!isValidKind(kind)) notFound();
  const list = getProjectsByKind(kind);
  // Deterministic order: stars desc, then name asc.
  const sorted = [...list].sort((a, b) => b.stars - a.stars || a.name.localeCompare(b.name));
  const kindCounts = getKindCounts();
  const kpCounts = getKindPlatformCounts();
  const total = getAllProjects().length;
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: `NetTools Hub — ${kindLabel(kind)}`,
    url: `${SITE_CANONICAL}/explore/k/${kind}`,
    numberOfItems: sorted.length,
    itemListElement: sorted.slice(0, 100).map((p, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: p.name,
      url: p.url,
      description: p.description,
    })),
  };
  return (
    <ExploreLayout
      current={{ kind: kind as ProjectKind }}
      kindCounts={kindCounts}
      kindPlatformCounts={kpCounts}
      total={total}
      lang="en"
      title={`${kindLabel(kind)} (${kind})`}
      meta={
        <p className="text-[12.5px] text-fg-2">
          <span className="font-mono text-muted">[ {kind} ]</span> {sorted.length} entries ·{' '}
          <span className="font-mono text-muted">sorted by stars</span> ·{' '}
          <a href={`${SITE_CANONICAL}/explore`} className="link-editorial">
            ← back to index
          </a>
        </p>
      }
      breadcrumb={<Breadcrumb trail={[rootCrumb('en'), kindCrumb('en', kind)]} lang="en" />}
    >
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: safeJsonLd(jsonLd) }} />
      <ProjectTable projects={sorted} lang="en" />
    </ExploreLayout>
  );
}
