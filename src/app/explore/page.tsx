import { ExploreContent } from "@/components/explore-content";
import { getAllProjects } from "@/lib/projects";
import { PROJECT_COUNT, SITE_CANONICAL } from "@/lib/site";
import { safeJsonLd } from "@/lib/utils";

// JSON-LD `ItemList` for the explore page. The list is the same
// PROJECT_COUNT projects that the page renders, in the same default
// order (which is the order they appear in `data/projects.json`).
// Google uses this to build "list" rich results, where each entry
// shows the project name, URL, and a short description.
//
// We deliberately cap at 100 items. Google's documentation says
// more than 100 is allowed but the visible rich result only shows
// the first ~10 anyway; the rest still help with entity indexing
// but inflate the HTML payload for the static export. 100 keeps
// the trade-off honest.
const itemListJsonLd = {
  "@context": "https://schema.org",
  "@type": "ItemList",
  name: "NetTools Hub — Curated Network Tools",
  description:
    "A curated atlas of open-source network tools, organised by purpose, with multilingual annotations.",
  url: `${SITE_CANONICAL}/explore`,
  numberOfItems: getAllProjects().length,
  itemListElement: getAllProjects()
    .slice(0, 100)
    .map((p, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: p.name,
      url: p.url,
      description: p.description,
    })),
};

export const metadata = {
  title: "Explore",
  description: `Browse and search ${PROJECT_COUNT}+ curated network tools across 6 themed groups. Filter by proxy, VPN, Clash, DNS, security tools and more.`,
};

export default function ExplorePage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: safeJsonLd(itemListJsonLd) }}
      />
      <ExploreContent />
    </>
  );
}
