import type { MetadataRoute } from "next";
import {
  getAllKinds,
  getAllPlatforms,
  getKindPlatformCounts,
  getLastUpdated,
  isValidKind,
  isValidPlatform,
} from "@/lib/projects";
import { LANG_HTML_LANG, Lang } from "@/lib/i18n";
import { SITE_CANONICAL } from "@/lib/site";

// Required for `output: "export"`: the sitemap is generated at
// build time and never revalidated at runtime.
export const dynamic = "force-static";

const LANGS: readonly Lang[] = ["en", "zh", "ja"];

/** Build hreflang alternates for a given path. */
function alternates(path: string) {
  return LANGS.map((lang) => ({
    hreflang: LANG_HTML_LANG[lang],
    href:
      lang === "en"
        ? `${SITE_CANONICAL}${path}`
        : `${SITE_CANONICAL}${path}?lang=${lang}`,
  })).concat({
    hreflang: "x-default",
    href: `${SITE_CANONICAL}${path}`,
  });
}

export default function sitemap(): MetadataRoute.Sitemap {
  const lastUpdated = getLastUpdated();
  const kinds = getAllKinds();
  const platforms = getAllPlatforms();
  const kpCounts = getKindPlatformCounts();

  // /explore/k/<kind> entries. The kind list is the canonical axis
  // of the navigation tree; the sitemap mirrors it 1:1.
  const kindEntries: MetadataRoute.Sitemap = kinds.flatMap((k) =>
    LANGS.map((lang) => ({
      url:
        lang === "en"
          ? `${SITE_CANONICAL}/explore/k/${k}`
          : `${SITE_CANONICAL}/explore/k/${k}?lang=${lang}`,
      lastModified: lastUpdated,
      changeFrequency: "weekly" as const,
      priority: 0.7,
      alternates: {
        languages: Object.fromEntries(
          alternates(`/explore/k/${k}`).map((a) => [a.hreflang, a.href]),
        ),
      },
    })),
  );

  // /explore/k/<kind>/p/<platform> entries. Only combinations that
  // have at least one matching project are emitted, to keep the
  // sitemap free of zero-row pages that would otherwise waste
  // crawl budget.
  const kpEntries: MetadataRoute.Sitemap = kinds.flatMap((k) =>
    platforms.flatMap((p) => {
      if ((kpCounts[`${k}|${p}`] || 0) === 0) return [];
      if (!isValidKind(k) || !isValidPlatform(p)) return [];
      return LANGS.map((lang) => ({
        url:
          lang === "en"
            ? `${SITE_CANONICAL}/explore/k/${k}/p/${p}`
            : `${SITE_CANONICAL}/explore/k/${k}/p/${p}?lang=${lang}`,
        lastModified: lastUpdated,
        changeFrequency: "weekly" as const,
        priority: 0.5,
        alternates: {
          languages: Object.fromEntries(
            alternates(`/explore/k/${k}/p/${p}`).map((a) => [a.hreflang, a.href]),
          ),
        },
      }));
    }),
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
    ...kindEntries,
    ...kpEntries,
  ];
}
