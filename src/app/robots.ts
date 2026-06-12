import type { MetadataRoute } from 'next';
import { SITE_CANONICAL, SITE_ORIGIN } from '@/lib/site';

export const dynamic = 'force-static';

export default function robots(): MetadataRoute.Robots {
  return {
    // `Host` is technically only respected by Yandex and a handful
    // of minor crawlers, but adding it is cheap and signals the
    // canonical host to anything that does read it. `Sitemap` is
    // what Google and Bing actually consume to discover URLs.
    rules: [
      {
        userAgent: '*',
        allow: '/',
      },
    ],
    // `SITE_CANONICAL` has no trailing slash (see `lib/site.ts`
    // for the rationale) so the sitemap URL is built by joining
    // the path with a literal `/` — using template-literal
    // concatenation without a separator would have produced
    // `https://...Hubsitemap.xml`.
    sitemap: `${SITE_CANONICAL}/sitemap.xml`,
    // The `Host` directive is a Yandex convention; the value
    // should be the *origin* of the canonical host, not a
    // specific page URL, so we strip the `/NetTools-Hub` suffix
    // back to the bare origin.
    host: SITE_ORIGIN,
  };
}
