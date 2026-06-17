import { notFound } from 'next/navigation';
import { ExploreLayout } from '@/components/explore-layout';
import { ProjectCard } from '@/components/project-card';
import {
  getAllProjects,
  getKindCounts,
  getKindPlatformCounts,
  isValidKind,
  isValidPlatform,
  getProjectsByKindPlatform,
} from '@/lib/projects';
import { Breadcrumb } from '@/components/breadcrumb';
import { kindCrumb, platformCrumb, rootCrumb } from '@/lib/breadcrumb';
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
  const typedKind = kind as ProjectKind;
  const typedPlatform = platform as ProjectPlatform;
  const list = getProjectsByKindPlatform(typedKind, typedPlatform);
  const sorted = [...list].sort((a, b) => b.stars - a.stars || a.name.localeCompare(b.name));
  const total = getAllProjects().length;
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: `NetTools Hub — ${kindLabel(typedKind)} on ${platformLabel(typedPlatform)}`,
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
      current={{ kind: typedKind, platform: typedPlatform }}
      kindCounts={getKindCounts()}
      kindPlatformCounts={getKindPlatformCounts()}
      total={total}
      titleData={{ type: 'platform', kind: typedKind, platform: typedPlatform }}
      metaData={{ variant: 'platform', count: sorted.length, kind: typedKind }}
      breadcrumb={
        <Breadcrumb
          trail={[
            rootCrumb('en'),
            kindCrumb('en', typedKind),
            platformCrumb('en', typedKind, typedPlatform),
          ]}
        />
      }
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
