import { notFound } from 'next/navigation';
import { ExploreLayout } from '@/components/explore-layout';
import { ProjectCard } from '@/components/project-card';
import {
  getAllProjects,
  getKindCounts,
  getKindPlatformCounts,
  isValidKind,
  getProjectsByKind,
} from '@/lib/projects';
import { Breadcrumb } from '@/components/breadcrumb';
import { kindCrumb, rootCrumb } from '@/lib/breadcrumb';
import { kindLabel } from '@/lib/taxonomy';
import { SITE_CANONICAL } from '@/lib/site';
import { safeJsonLd } from '@/lib/utils';
import type { ProjectKind } from '@/types/project';

export function generateStaticParams() {
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
  const typedKind = kind as ProjectKind;
  const list = getProjectsByKind(typedKind);
  const sorted = [...list].sort((a, b) => b.stars - a.stars || a.name.localeCompare(b.name));
  const kindCounts = getKindCounts();
  const kpCounts = getKindPlatformCounts();
  const total = getAllProjects().length;
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: `NetTools Hub — ${kindLabel(typedKind)}`,
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
      current={{ kind: typedKind }}
      kindCounts={kindCounts}
      kindPlatformCounts={kpCounts}
      total={total}
      titleData={{ type: 'kind', kind: typedKind }}
      metaData={{ variant: 'kind', count: sorted.length, kind: typedKind }}
      breadcrumb={<Breadcrumb trail={[rootCrumb('en'), kindCrumb('en', typedKind)]} />}
    >
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: safeJsonLd(jsonLd) }} />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sorted.map((project) => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
    </ExploreLayout>
  );
}
