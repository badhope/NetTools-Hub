import { ExploreLayout } from '@/components/explore-layout';
import { ProjectCard } from '@/components/project-card';
import {
  getAllProjects,
  getKindCounts,
  getKindPlatformCounts,
  getTotalStars,
} from '@/lib/projects';
import { Breadcrumb } from '@/components/breadcrumb';
import { rootCrumb } from '@/lib/breadcrumb';
import { PROJECT_COUNT, SITE_CANONICAL } from '@/lib/site';
import { safeJsonLd, formatStars } from '@/lib/utils';

export const metadata = {
  title: 'Explore',
  description: `Browse ${PROJECT_COUNT}+ open-source network tools. Drill down by kind (proxy, VPN, DNS, ...) and platform (desktop, mobile, CLI, server, browser, router).`,
};

// JSON-LD `ItemList` for the explore root. Capped at 100 items
// (Google only renders ~10 in rich results; the rest still help
// with entity indexing but the payload is the cost).
const itemListJsonLd = {
  '@context': 'https://schema.org',
  '@type': 'ItemList',
  name: 'NetTools Hub — Open-source Network Tools',
  description: 'A curated link index of open-source network tools, organised by kind and platform.',
  url: `${SITE_CANONICAL}/explore`,
  numberOfItems: getAllProjects().length,
  itemListElement: getAllProjects()
    .slice(0, 100)
    .map((p, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: p.name,
      url: p.url,
      description: p.description,
    })),
};

export default function ExploreRootPage() {
  const projects = getAllProjects();
  const totalStars = getTotalStars();
  const kindCounts = getKindCounts();
  const kpCounts = getKindPlatformCounts();
  // Deterministic order: stars desc, then name asc.
  const sorted = [...projects].sort((a, b) => b.stars - a.stars || a.name.localeCompare(b.name));
  return (
    <ExploreLayout
      current={{}}
      kindCounts={kindCounts}
      kindPlatformCounts={kpCounts}
      total={projects.length}
      title="All projects"
      meta={
        <p className="text-[12.5px] text-fg-2">
          <span className="font-mono text-muted">[ index ]</span> {projects.length} entries ·{' '}
          {formatStars(totalStars)} total stars ·{' '}
          <span className="font-mono text-muted">sorted by stars</span>
        </p>
      }
      breadcrumb={<Breadcrumb trail={[rootCrumb('en')]} />}
    >
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: safeJsonLd(itemListJsonLd) }}
      />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sorted.map((project) => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
    </ExploreLayout>
  );
}
