import type { MetadataRoute } from "next";
import { SITE_CANONICAL } from "@/lib/site";

export const dynamic = "force-static";

export default function robots(): MetadataRoute.Robots {
  return {
    // `Host` is technically only respected by Yandex and a handful
    // of minor crawlers, but adding it is cheap and signals the
    // canonical host to anything that does read it. `Sitemap` is
    // what Google and Bing actually consume to discover URLs.
    rules: [
      {
        userAgent: "*",
        allow: "/",
      },
    ],
    sitemap: `${SITE_CANONICAL}/sitemap.xml`,
    host: SITE_CANONICAL,
  };
}
