import { notFound } from 'next/navigation';
import { ExploreLayout } from '@/components/explore-layout';
import { ProjectTable } from '@/components/project-table';
import {
  getAllProjects,
  getKindCounts,
  getKindPlatformCounts,
  isValidKind,
  isValidPlatform,
  getProjectsByKindPlatform,
} from '@/lib/projects';
import { Breadcrumb, kindCrumb, platformCrumb, rootCrumb } from '@/components/breadcrumb';
import { kindLabel, platformLabel } from '@/lib/taxonomy';
import { SITE_CANONICAL } from '@/lib/site';
import { safeJsonLd } from '@/lib/utils';
import type { ProjectKind, ProjectPlatform } from '@/types/project';

export function generateStaticParams() {
  // Only generate combinations that actually have projects.
  // This avoids creating empty pages that just show "no entries".
  const projects = getAllProjects();
  const combinations = new Set<string>();

  for (const project of projects) {
    for (const platform of project.platform) {
      combinations.add(`${project.kind}/${platform}`);
    }
  }

  return Array.from(combinations).map((combo) => {
    const [kind, platform] = combo.split('/');
    return { kind, platform };
  });
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ kind: string; platform: string }>;
}) {
  const { kind, platform } = await params;
  if (!isValidKind(kind) || !isValidPlatform(platform)) return { title: 'Not found' };
  return {
    title: `${platformLabel(platform)} · ${kindLabel(kind)} — Explore`,
    description: `${kindLabel(kind)} tools that run on ${platformLabel(platform).toLowerCase()}.`,
  };
}

export default async function KindPlatformPage({
  params,
}: {
  params: Promise<{ kind: string; platform: string }>;
}) {
  const { kind, platform } = await params;
  if (!isValidKind(kind) || !isValidPlatform(platform)) notFound();
  const list = getProjectsByKindPlatform(kind as ProjectKind, platform as ProjectPlatform);
  const sorted = [...list].sort((a, b) => b.stars - a.stars || a.name.localeCompare(b.name));
  const total = getAllProjects().length;
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: `NetTools Hub — ${kindLabel(kind)} on ${platformLabel(platform)}`,
    url: `${SITE_CANONICAL}/explore/k/${kind}/p/${platform}`,
    numberOfItems: sorted.length,
    itemListElement: sorted.slice(0, 100).map((p, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: p.name,
      url: p.url,
    })),
  };
  return (
    <ExploreLayout
      current={{ kind: kind as ProjectKind, platform: platform as ProjectPlatform }}
      kindCounts={getKindCounts()}
      kindPlatformCounts={getKindPlatformCounts()}
      total={total}
      lang="en"
      title={`${platformLabel(platform)} · ${kindLabel(kind)}`}
      meta={
        <p className="text-[12.5px] text-fg-2">
          <span className="font-mono text-muted">
            [ {kind} / {platform} ]
          </span>{' '}
          {sorted.length} entries · <span className="font-mono text-muted">sorted by stars</span> ·{' '}
          <a href={`${SITE_CANONICAL}/explore/k/${kind}`} className="link-editorial">
            ← back to {kindLabel(kind)}
          </a>
        </p>
      }
      breadcrumb={
        <Breadcrumb
          trail={[rootCrumb('en'), kindCrumb('en', kind), platformCrumb('en', kind, platform)]}
          lang="en"
        />
      }
    >
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: safeJsonLd(jsonLd) }} />
      <ProjectTable projects={sorted} lang="en" />
    </ExploreLayout>
  );
}
