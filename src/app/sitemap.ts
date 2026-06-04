import type { MetadataRoute } from "next";
import {
  getAllProjects,
  getCategories,
  getLastUpdated,
} from "@/lib/projects";
import { LANG_HTML_LANG, Lang } from "@/lib/i18n";
import { SITE_CANONICAL } from "@/lib/site";

// Required for `output: "export"`: the sitemap is generated at
// build time and never revalidated at runtime.
export const dynamic = "force-static";

// The sitemap is generated at build time from the same dataset the
// rest of the site reads, so it is impossible for a category to be
// referenced from the homepage and missing from the sitemap (or
// vice versa). Every entry includes its language alternates so
// Google can serve the right variant to the right user without
// having to guess from the `?lang=` query string.
//
// `LANGS_HTML` used to be a local lookup table; the previous
// version had drifted out of sync with the canonical tags in
// `LANG_HTML_LANG` (one was `zh-Hans`, the other was `zh-CN`), so
// we now read directly from the i18n module's record.
const LANGS: readonly Lang[] = ["en", "zh", "ja"];

function alternates(path: string) {
  // The path may already carry a query string (e.g.
  // `/explore?category=foo`); the language alternates must append
  // the `lang=` param with `&` in that case, not `?`.
  const sep = path.includes("?") ? "&" : "?";
  return LANGS.map((lang) => ({
    hreflang: LANG_HTML_LANG[lang],
    href:
      lang === "en"
        ? `${SITE_CANONICAL}${path}`
        : `${SITE_CANONICAL}${path}${sep}lang=${lang}`,
  })).concat({
    hreflang: "x-default",
    href: `${SITE_CANONICAL}${path}`,
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
        url:
          lang === "en"
            ? `${SITE_CANONICAL}/explore?category=${slug}`
            : `${SITE_CANONICAL}/explore?category=${slug}&lang=${lang}`,
        lastModified: lastUpdated,
        changeFrequency: "weekly" as const,
        priority: 0.6,
        alternates: {
          languages: Object.fromEntries(
            alternates(`/explore?category=${slug}`).map((a) => [
              a.hreflang,
              a.href,
            ]),
          ),
        },
      })),
    );

  return [
    {
      url: `${SITE_CANONICAL}/`,
      lastModified: lastUpdated,
      changeFrequency: "weekly",
      priority: 1.0,
      alternates: {
        languages: Object.fromEntries(
          alternates("/").map((a) => [a.hreflang, a.href]),
        ),
      },
    },
    // Explicit `/?lang=` alternates for the landing page so Google
    // can index the Chinese/Japanese variants directly from the
    // sitemap (rather than having to discover them via the hreflang
    // cluster from the canonical English URL). The per-language
    // URLs themselves are still served from the same single static
    // `out/index.html` after `useClientLang` rehydrates.
    ...LANGS.filter((l) => l !== "en").map((lang) => ({
      url: `${SITE_CANONICAL}/?lang=${lang}`,
      lastModified: lastUpdated,
      changeFrequency: "weekly" as const,
      priority: 0.8,
      alternates: {
        languages: Object.fromEntries(
          alternates("/").map((a) => [a.hreflang, a.href]),
        ),
      },
    })),
    {
      url: `${SITE_CANONICAL}/explore`,
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
