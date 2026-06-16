import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { ExploreLayout } from '@/components/explore-layout';
import { ProjectDetail } from '@/components/project-detail';
import {
  getAllProjects,
  getKindCounts,
  getKindPlatformCounts,
  getProjectById,
  getRelatedProjects,
} from '@/lib/projects';
import { Breadcrumb } from '@/components/breadcrumb';
import { rootCrumb } from '@/lib/breadcrumb';
import { safeJsonLd, formatStars } from '@/lib/utils';
import type { ProjectKind } from '@/types/project';

export const metadata: Metadata = {
  title: 'Project Detail',
  description: `Detailed view of a network tool project from the NetTools Hub index.`,
};

interface ProjectDetailPageProps {
  // Next.js 15+: `params` is a Promise<> that has to be awaited.
  // We intentionally do NOT also accept `searchParams` here —
  // `output: "export"` cannot statically pre-render a route that
  // reads query parameters, and the language the user picks via
  // `?lang=` is already picked up on the client by `LangProvider`
  // (see `src/components/lang-provider.tsx`). The breadcrumb's
  // hrefs are re-built with the right lang on every render from
  // the client-side context.
  params: Promise<{ id: string }>;
}

export default async function ProjectDetailPage({ params }: ProjectDetailPageProps) {
  const { id } = await params;
  const project = getProjectById(id);

  if (!project) {
    notFound();
  }

  const projects = getAllProjects();
  const kindCounts = getKindCounts();
  const kpCounts = getKindPlatformCounts();
  const relatedProjects = getRelatedProjects(project.id, 4);

  // JSON-LD for the project
  const projectJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: project.name,
    description: project.description,
    url: project.url,
    applicationCategory: 'NetworkApplication',
    operatingSystem: project.platform.join(', '),
    author: {
      '@type': 'Person',
      name: project.author,
    },
    dateModified: project.lastCommit,
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: Math.min(5, Math.max(1, project.stars / 1000)).toFixed(1),
      ratingCount: project.stars,
    },
  };

  const title = `${project.name} — ${project.kind}`;
  // The breadcrumb label for "explore" is the same string in all
  // three languages, so we can pick 'en' for the server render
  // without losing information; the client component picks the
  // active language from `useLang()` and re-writes the hrefs.
  const breadcrumbTrail = [
    rootCrumb('en'),
    { label: project.kind, href: `/explore/k/${project.kind}` },
    { label: project.name },
  ];

  return (
    <ExploreLayout
      current={{ kind: project.kind as ProjectKind }}
      kindCounts={kindCounts}
      kindPlatformCounts={kpCounts}
      total={projects.length}
      title={title}
      meta={
        <p className="text-[12.5px] text-fg-2">
          <span className="font-mono text-muted">[ detail ]</span> {project.name} ·{' '}
          {formatStars(project.stars)} stars ·{' '}
          <span className="font-mono text-muted">{project.language}</span>
        </p>
      }
      breadcrumb={<Breadcrumb trail={breadcrumbTrail} />}
    >
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: safeJsonLd(projectJsonLd) }}
      />
      <ProjectDetail project={project} relatedProjects={relatedProjects} />
    </ExploreLayout>
  );
}

export function generateStaticParams() {
  const projects = getAllProjects();
  return projects.map((p) => ({ id: p.id }));
}
