/**
 * Single source of truth for site-wide identity constants. Anything
 * that has to agree between pages (the project count used in
 * metadata, the year in the copyright line, the repo owner shown in
 * the footer) lives here so a single edit propagates everywhere
 * instead of relying on string duplication.
 *
 * Keep this file dependency-free. The rest of the codebase may
 * import from `@/lib/site`, but `site` itself imports nothing.
 */

import { getAllProjects, getTotalStars } from "./projects";

/** GitHub owner used everywhere we attribute the work / link the repo. */
export const SITE_OWNER = "badhope";

/** GitHub Pages base path (matches next.config.ts `basePath`).
 *  GitHub Pages serves a user/org site at `https://<owner>.github.io`
 *  and each *project* site at `https://<owner>.github.io/<repo>/`.
 *  The Next.js `basePath` setting (computed from the `GITHUB_REPOSITORY`
 *  env var) is just the repo name — the owner is already in the
 *  origin. Building the full base path as `/{owner}/{repo}` would
 *  double it (`/badhope/NetTools-Hub`), which is what the first cut
 *  of this file did and what the sitemap and JSON-LD payloads
 *  immediately picked up. The owner is therefore *not* part of
 *  `SITE_BASE_PATH` here. */
export const SITE_BASE_PATH = "/NetTools-Hub";

/** Canonical origin (no trailing slash). */
export const SITE_ORIGIN = "https://badhope.github.io";

/** Fully-qualified canonical URL of the landing page, *without* a
 *  trailing slash. Callers that want to point at a sub-path or at
 *  the root page itself are responsible for joining the slash:
 *
 *    SITE_CANONICAL                  → https://...Hub/NetTools-Hub
 *    `${SITE_CANONICAL}/`            → https://...Hub/NetTools-Hub/    (landing)
 *    `${SITE_CANONICAL}/explore`     → https://...Hub/NetTools-Hub/explore
 *
 *  Keeping the trailing slash *off* the constant means a careless
 *  caller can't produce `https://...Hub/NetTools-Hub//explore`
 *  (double slash) by writing `${SITE_CANONICAL}/${path}` — they
 *  always have to think about the separator, which makes the
 *  mistake obvious. */
export const SITE_CANONICAL = `${SITE_ORIGIN}${SITE_BASE_PATH}`;

/** Total number of curated projects — drives every "{n}" copy. */
export const PROJECT_COUNT: number = getAllProjects().length;

/** Sum of `stars` across all projects. */
export const TOTAL_STARS: number = getTotalStars();

/** Current year (build-time). Static export freezes this, but the
 *  value is recomputed on every `next build` so the year stays in
 *  sync with when the site was last deployed. */
export const COPYRIGHT_YEAR: number = new Date().getFullYear();
