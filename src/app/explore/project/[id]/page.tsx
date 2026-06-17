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
import { safeJsonLd } from '@/lib/utils';
import type { ProjectKind } from '@/types/project';

interface ProjectDetailPageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<{ title: string; description: string }> {
  const { id } = await params;
  const project = getProjectById(id);
  if (!project) return { title: 'Not found', description: 'Project not found.' };
  return {
    title: `${project.name} — ${project.kind}`,
    description: project.description,
  };
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
      titleData={{
        type: 'project',
        projectName: project.name,
        projectKind: project.kind,
      }}
      metaData={{
        variant: 'project',
        count: 1,
        projectName: project.name,
        projectStars: project.stars,
        projectLanguage: project.language,
      }}
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
