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

import { getAllProjects, getCategoryCount, getTotalForks, getTotalStars } from "./projects";

/** GitHub owner used everywhere we attribute the work / link the repo. */
export const SITE_OWNER = "badhope";

/** GitHub Pages base path (matches next.config.ts `basePath`). */
export const SITE_BASE_PATH = `/${SITE_OWNER}/NetTools-Hub`;

/** Canonical origin (no trailing slash). */
export const SITE_ORIGIN = "https://badhope.github.io";

/** Fully-qualified canonical URL of the landing page. */
export const SITE_CANONICAL = `${SITE_ORIGIN}${SITE_BASE_PATH}/`;

/** Total number of curated projects — drives every "{n}+" copy. */
export const PROJECT_COUNT: number = getAllProjects().length;

/** Total number of distinct categories. */
export const CATEGORY_COUNT: number = getCategoryCount();

/** Sum of `stars` across all projects. */
export const TOTAL_STARS: number = getTotalStars();

/** Sum of `forks` across all projects. */
export const TOTAL_FORKS: number = getTotalForks();

/** Current year (build-time). Static export freezes this, but the
 *  value is recomputed on every `next build` so the year stays in
 *  sync with when the site was last deployed. */
export const COPYRIGHT_YEAR: number = new Date().getFullYear();
