import { safeJsonLd } from "@/lib/utils";
import { LandingContent } from "@/components/landing-content";
import { PROJECT_COUNT, SITE_CANONICAL, SITE_OWNER } from "@/lib/site";

// JSON-LD WebSite + Organization schema for the landing page.
// Search engines use this to build rich results (sitelinks
// searchbox, knowledge-panel data). The previous version had a
// `potentialAction: SearchAction` that pointed at a template
// that did not exist; Google silently demotes sites that lie
// about search endpoints, so the field is gone.
const siteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "NetTools Hub",
  url: `${SITE_CANONICAL}/`,
  description: `A field manual of ${PROJECT_COUNT} open-source network tools, organised by kind (proxy, VPN, DNS, acceleration, security, monitoring, ops, tools) and by platform (desktop, mobile, CLI, server, browser, router).`,
  inLanguage: ["en", "zh-Hans", "ja"],
  publisher: {
    "@type": "Person",
    name: SITE_OWNER,
    url: `https://github.com/${SITE_OWNER}`,
  },
  potentialAction: {
    "@type": "ReadAction",
    target: `${SITE_CANONICAL}/explore`,
  },
};

export default function LandingPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: safeJsonLd(siteJsonLd) }}
      />
      <LandingContent />
    </>
  );
}
