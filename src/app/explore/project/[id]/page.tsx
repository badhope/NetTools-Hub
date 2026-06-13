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
  getTotalStars,
} from '@/lib/projects';
import { Breadcrumb, rootCrumb } from '@/components/breadcrumb';
import { safeJsonLd, formatStars } from '@/lib/utils';
import { Lang } from '@/lib/i18n';
import type { ProjectKind } from '@/types/project';

export const metadata: Metadata = {
  title: 'Project Detail',
  description: `Detailed view of a network tool project from the NetTools Hub index.`,
};

interface ProjectDetailPageProps {
  // Next.js 15+: params and searchParams are now async (Promise<>).
  params: Promise<{ id: string }>;
  searchParams: Promise<{ lang?: string }>;
}

export default async function ProjectDetailPage({ params }: ProjectDetailPageProps) {
  const { id } = await params;
  const project = getProjectById(id);

  if (!project) {
    notFound();
  }

  // The page is statically generated, so we hard-code the
  // default language. The LanguageSwitcher on the client can
  // still re-render with a chosen language via its own
  // localStorage state.
  const lang: Lang = 'en';

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
  const breadcrumbTrail = [
    rootCrumb(lang),
    { label: project.kind, href: `/explore/k/${project.kind}` },
    { label: project.name },
  ];

  return (
    <ExploreLayout
      current={{ kind: project.kind as ProjectKind }}
      kindCounts={kindCounts}
      kindPlatformCounts={kpCounts}
      total={projects.length}
      lang={lang}
      title={title}
      meta={
        <p className="text-[12.5px] text-fg-2">
          <span className="font-mono text-muted">[ detail ]</span> {project.name} ·{' '}
          {formatStars(project.stars)} stars ·{' '}
          <span className="font-mono text-muted">{project.language}</span>
        </p>
      }
      breadcrumb={<Breadcrumb trail={breadcrumbTrail} lang={lang} />}
    >
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: safeJsonLd(projectJsonLd) }}
      />
      <ProjectDetail project={project} lang={lang} relatedProjects={relatedProjects} />
    </ExploreLayout>
  );
}

export function generateStaticParams() {
  const projects = getAllProjects();
  return projects.map((p) => ({ id: p.id }));
}
