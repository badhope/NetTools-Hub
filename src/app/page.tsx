import { LandingContent } from "@/components/landing-content";
import { safeJsonLd } from "@/lib/utils";

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
  // The search box is purely client-side (state held in
  // `ExploreContent`); it does *not* rewrite the URL with
  // `?q=…`, so there is no `target` template to advertise. The
  // previous version listed a `SearchAction` template pointing
  // at `/explore?q={search_term_string}` that did not actually
  // resolve to anything — Google will silently demote or omit
  // the sitelinks search box if the template is a dead end, so
  // we just don't claim one exists.
  potentialAction: {
    "@type": "ReadAction",
    target: "https://badhope.github.io/NetTools-Hub/explore",
  },
};

export default function LandingPage() {
  return (
    <>
      <script
        type="application/ld+json"
        // `dangerouslySetInnerHTML` is the documented Next.js pattern
        // for an inline JSON-LD payload. The content goes through
        // `safeJsonLd` so any project `description` that happens to
        // contain `<`, `>`, or `&` (e.g. `<script>...` pasted by a
        // contributor) is escaped to its `\uXXXX` form before it
        // reaches the HTML — closing the `</script>`-injection
        // vector that raw `JSON.stringify` leaves open.
        dangerouslySetInnerHTML={{ __html: safeJsonLd(siteJsonLd) }}
      />
      <LandingContent />
    </>
  );
}
