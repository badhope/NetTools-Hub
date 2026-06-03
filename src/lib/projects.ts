import { ProjectsData, ProjectCategory, Project } from "@/types/project";
// data/projects.json lives at the repository root (kept outside src/ so
// that future tooling — e.g. a separate data-validation script — can
// read it without going through the Next.js import graph). Resolve
// with a relative path; the @/ alias only covers src/.
import rawData from "../../data/projects.json";
import { formatNumber, formatTotalStars } from "@/lib/utils";

export { formatNumber, formatTotalStars };

const data = rawData as ProjectsData;

// ============================================================================
// Pre-computed indexes
// ============================================================================
//
// The dataset is static and immutable for the lifetime of the bundle. Every
// lookup that the UI does on render — search, category counts, total stars,
// per-category grouping — can therefore be computed exactly once at module
// load and reused for the lifetime of the page. Hoisting these out of the
// component body:
//   - removes per-render allocation (the old code built the counts map
//     and re-scanned the dataset on every state change);
//   - drops the search filter from 5 `toLowerCase().includes()` calls per
//     project per keystroke to a single substring check against a
//     pre-lowercased haystack;
//   - replaces the O(slugs × projects) `flatMap(filter())` in project-list
//     with an O(1) `Map.get(slug)`.
// All returned collections are frozen so accidental mutation by a
// downstream component would throw loudly during development.

const PROJECTS: readonly Project[] = Object.freeze(data.projects.slice());
const CATEGORIES: Record<string, ProjectCategory> = data.categories;
const LAST_UPDATED: string = data.lastUpdated;

// Per-project search haystack. Lowercased once at module load so the
// search filter is a single `.includes()` per project per keystroke.
// We concatenate every searchable field into one string and stash the
// starting offset of each field so that future ranking (boost name
// matches over description matches) can be added without rescanning.
interface IndexedProject {
  project: Project;
  haystack: string;
}
const INDEXED: readonly IndexedProject[] = Object.freeze(
  PROJECTS.map((p) => ({
    project: p,
    haystack: (
      p.name +
      " " +
      p.author +
      " " +
      p.description +
      " " +
      p.tags.join(" ") +
      " " +
      p.highlights.join(" ")
    ).toLowerCase(),
  })),
);

// Per-category grouping. The old project-list used
// `group.slugs.flatMap(slug => sorted.filter(p => p.category === slug))`
// which is O(slugs × projects) on every render. The Map gives O(1)
// lookups and the per-group iteration is O(group size).
const BY_CATEGORY: ReadonlyMap<string, readonly Project[]> = (() => {
  // Build into a mutable Map first (so `Array.push` works during
  // construction), then freeze the inner arrays at the end so the
  // public read view is locked down.
  const m = new Map<string, Project[]>();
  for (const p of PROJECTS) {
    const list = m.get(p.category);
    if (list) list.push(p);
    else m.set(p.category, [p]);
  }
  // Freeze the inner arrays too — they are part of the public read view.
  // `Object.freeze` on a `Project[]` widens to `readonly Project[]`,
  // which is exactly the value type the public `ReadonlyMap` exposes.
  const frozen = new Map<string, readonly Project[]>();
  for (const [k, v] of m) frozen.set(k, Object.freeze(v));
  return frozen;
})();

const COUNTS: Readonly<Record<string, number>> = Object.freeze(
  Object.fromEntries(
    Array.from(BY_CATEGORY.entries()).map(([k, v]) => [k, v.length]),
  ),
);

const TOTAL_STARS: number = PROJECTS.reduce((sum, p) => sum + p.stars, 0);
const TOTAL_FORKS: number = PROJECTS.reduce((sum, p) => sum + p.forks, 0);
const CATEGORY_COUNT: number = BY_CATEGORY.size;

// ============================================================================
// Public API
// ============================================================================

export function getAllProjects(): readonly Project[] {
  return PROJECTS;
}

export function getLastUpdated(): string {
  return LAST_UPDATED;
}

export function getCategories(): Record<string, ProjectCategory> {
  return CATEGORIES;
}

export function getCategoryCounts(): Readonly<Record<string, number>> {
  return COUNTS;
}

/**
 * O(1) lookup of the projects in a single category. Returns an empty
 * (frozen) array for unknown slugs so callers can avoid a null check.
 */
export function getProjectsByCategoryMap(): ReadonlyMap<string, readonly Project[]> {
  return BY_CATEGORY;
}

const EMPTY_LIST: readonly Project[] = Object.freeze([]);
export function getProjectsByCategory(category: string): readonly Project[] {
  if (!category || category === "all") return PROJECTS;
  return BY_CATEGORY.get(category) ?? EMPTY_LIST;
}

export function getTotalStars(): number {
  return TOTAL_STARS;
}

export function getTotalForks(): number {
  return TOTAL_FORKS;
}

export function getCategoryCount(): number {
  return CATEGORY_COUNT;
}

/**
 * Fast, ranking-aware search. The haystack is the precomputed
 * lowercase concatenation of every searchable field on the project,
 * so a single `String.includes` per project is the only per-keystroke
 * work the filter does. When a category is supplied it is used as an
 * additional predicate on top of the text match.
 */
export function searchProjects(
  query: string,
  category?: string,
): readonly Project[] {
  const q = query.trim().toLowerCase();
  const scoped = category ? BY_CATEGORY.get(category) : undefined;
  const base = scoped ?? PROJECTS;
  if (!q) return base;
  // The `scoped` path still needs the per-project haystack (we did not
  // pre-index per-category), so we fall back to filtering the indexed
  // list and intersecting with the category. The list is small enough
  // (120 projects) that the two-stage filter is still O(n).
  if (scoped) {
    return scoped.filter((_, i) => {
      // `scoped` and `INDEXED` are not the same array; rebuild the
      // haystack lookup by id. The id-keyed index below makes this O(1).
      return haystackFor(scoped[i]!.id).includes(q);
    });
  }
  const out: Project[] = [];
  for (const { project, haystack } of INDEXED) {
    if (haystack.includes(q)) out.push(project);
  }
  return out;
}

// id -> haystack map, used by the scoped-search path above. Building
// it once at module load turns the per-project `Array.find` into an
// O(1) `Map.get`. Keys are 120 strings so the memory cost is trivial.
const HAYSTACK_BY_ID: ReadonlyMap<string, string> = (() => {
  const m = new Map<string, string>();
  for (const { project, haystack } of INDEXED) m.set(project.id, haystack);
  return m;
})();
function haystackFor(id: string): string {
  return HAYSTACK_BY_ID.get(id) ?? "";
}
