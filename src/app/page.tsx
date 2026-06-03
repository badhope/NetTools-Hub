import { LandingContent } from "@/components/landing-content";

// JSON-LD WebSite + Organization schema for the landing page.
// Search engines use this to build rich results (sitelinks
// searchbox, knowledge-panel data). The `SearchAction` lets a
// future `/search?q={search_term_string}` route appear directly
// in the Google search box; the `target` is a placeholder that
// will need to point at the real search URL when one is added.
const siteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "NetTools Hub",
  alternateName: "Network Tools Atlas",
  url: "https://badhope.github.io/NetTools-Hub",
  description:
    "A curated atlas of 120+ open-source network tools, organised by purpose, with multilingual annotations and editorial notes.",
  inLanguage: ["en", "zh-Hans", "ja"],
  publisher: {
    "@type": "Person",
    name: "badhope",
    url: "https://github.com/badhope",
  },
  potentialAction: {
    "@type": "SearchAction",
    target: {
      "@type": "EntryPoint",
      urlTemplate:
        "https://badhope.github.io/NetTools-Hub/explore?q={search_term_string}",
    },
    "query-input": "required name=search_term_string",
  },
};

export default function LandingPage() {
  return (
    <>
      <script
        type="application/ld+json"
        // `dangerouslySetInnerHTML` is safe here: the payload is
        // 100% static, authored at build time, and never touches
        // user input. The Next.js CSP already restricts
        // `script-src` to `'self' 'unsafe-inline'` for the
        // Next-injected hydration scripts; this is the same
        // exception class.
        dangerouslySetInnerHTML={{ __html: JSON.stringify(siteJsonLd) }}
      />
      <LandingContent />
    </>
  );
}
