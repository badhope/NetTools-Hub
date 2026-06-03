import type { MetadataRoute } from "next";
import { getAllProjects, getCategories, getLastUpdated } from "@/lib/projects";

// Required for `output: "export"`: the sitemap is generated at
// build time and never revalidated at runtime.
export const dynamic = "force-static";

// The sitemap is generated at build time from the same dataset the
// rest of the site reads, so it is impossible for a category to be
// referenced from the homepage and missing from the sitemap (or
// vice versa). Every entry includes its language alternates so
// Google can serve the right variant to the right user without
// having to guess from the `?lang=` query string.
const SITE = "https://badhope.github.io/NetTools-Hub";
const LANGS = ["en", "zh", "ja"] as const;
const LANGS_HTML: Record<typeof LANGS[number], string> = {
  en: "en",
  zh: "zh-Hans",
  ja: "ja",
};

function alternates(path: string) {
  // The path may already carry a query string (e.g.
  // `/explore?category=foo`); the language alternates must append
  // the `lang=` param with `&` in that case, not `?`.
  const sep = path.includes("?") ? "&" : "?";
  return LANGS.map((lang) => ({
    hreflang: LANGS_HTML[lang],
    href:
      lang === "en"
        ? `${SITE}${path}`
        : `${SITE}${path}${sep}lang=${lang}`,
  })).concat({
    hreflang: "x-default",
    href: `${SITE}${path}`,
  });
}

export default function sitemap(): MetadataRoute.Sitemap {
  const lastUpdated = getLastUpdated();
  const projects = getAllProjects();
  const categories = getCategories();

  // Per-category pages. The site uses `?category=slug` query params
  // rather than separate paths (the static export would otherwise
  // need a route segment per category), but we still want them in
  // the sitemap with their language alternates so they can rank.
  const categoryEntries: MetadataRoute.Sitemap = Object.keys(categories)
    .filter((slug) => projects.some((p) => p.category === slug))
    .flatMap((slug) =>
      LANGS.map((lang) => ({
        url: lang === "en" ? `${SITE}/explore?category=${slug}` : `${SITE}/explore?category=${slug}&lang=${lang}`,
        lastModified: lastUpdated,
        changeFrequency: "weekly" as const,
        priority: 0.6,
        alternates: {
          languages: Object.fromEntries(
            alternates(`/explore?category=${slug}`).map((a) => [a.hreflang, a.href]),
          ),
        },
      })),
    );

  return [
    {
      url: `${SITE}/`,
      lastModified: lastUpdated,
      changeFrequency: "weekly",
      priority: 1.0,
      alternates: {
        languages: Object.fromEntries(
          alternates("/").map((a) => [a.hreflang, a.href]),
        ),
      },
    },
    {
      url: `${SITE}/explore`,
      lastModified: lastUpdated,
      changeFrequency: "daily",
      priority: 0.9,
      alternates: {
        languages: Object.fromEntries(
          alternates("/explore").map((a) => [a.hreflang, a.href]),
        ),
      },
    },
    ...categoryEntries,
  ];
}
