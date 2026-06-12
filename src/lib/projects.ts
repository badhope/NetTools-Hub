import { ProjectsData, Project, ProjectKind, ProjectPlatform } from '@/types/project';
// data/projects.json lives at the repository root (kept outside src/ so
// that future tooling — e.g. a separate data-validation script — can
// read it without going through the Next.js import graph). Resolve
// with a relative path; the @/ alias only covers src/.
import rawData from '../../data/projects.json';
import { formatNumber, formatTotalStars } from '@/lib/utils';

export { formatNumber, formatTotalStars };

const data = rawData as ProjectsData;

// ============================================================================
// Schema version check
// ============================================================================
//
// Warn if the data schema version doesn't match what the code expects.
// This helps catch mismatches when the data refresh script updates the
// schema but the frontend hasn't been updated yet.

const CURRENT_SCHEMA_VERSION = 2;

if (data.schemaVersion !== CURRENT_SCHEMA_VERSION) {
  console.warn(
    `[projects] Schema version mismatch: expected ${CURRENT_SCHEMA_VERSION}, got ${data.schemaVersion}. Some features may not work correctly.`
  );
}

// ============================================================================
// Pre-computed indexes
// ============================================================================
//
// The dataset is static and immutable for the lifetime of the bundle.
// Every lookup the UI does on render — by-id, by-kind, by-kind-and-platform,
// totals, last-updated — is therefore computed exactly once at module load
// and reused for the lifetime of the page. Hoisting these out of the
// component body drops per-render allocation and replaces O(n) scans with
// O(1) Map lookups.
//
// All returned collections are frozen so accidental mutation by a
// downstream component would throw loudly during development.

const PROJECTS: readonly Project[] = Object.freeze(data.projects.slice());
const LAST_UPDATED: string = data.lastUpdated;

const TOTAL_STARS: number = PROJECTS.reduce((sum, p) => sum + p.stars, 0);

// ---------------------------------------------------------------------------
// By-kind index. /explore/k/[kind] is the primary axis of the new
// navigation tree; this map makes the page render an O(1) lookup.
// ---------------------------------------------------------------------------
const BY_KIND: ReadonlyMap<ProjectKind, readonly Project[]> = (() => {
  const m = new Map<ProjectKind, Project[]>();
  for (const p of PROJECTS) {
    const list = m.get(p.kind);
    if (list) list.push(p);
    else m.set(p.kind, [p]);
  }
  const frozen = new Map<ProjectKind, readonly Project[]>();
  for (const [k, v] of m) frozen.set(k, Object.freeze(v));
  return frozen;
})();

// ---------------------------------------------------------------------------
// By-kind-and-platform index. /explore/k/[kind]/p/[platform] is the
// second axis; key is `${kind}|${platform}`. Multi-platform projects
// (e.g. sing-box is server+mobile+desktop) appear under every bucket
// their `platform[]` array contains.
// ---------------------------------------------------------------------------
const BY_KIND_PLATFORM: ReadonlyMap<string, readonly Project[]> = (() => {
  const m = new Map<string, Project[]>();
  for (const p of PROJECTS) {
    for (const plat of p.platform) {
      const key = `${p.kind}|${plat}`;
      const list = m.get(key);
      if (list) list.push(p);
      else m.set(key, [p]);
    }
  }
  const frozen = new Map<string, readonly Project[]>();
  for (const [k, v] of m) frozen.set(k, Object.freeze(v));
  return frozen;
})();

// ---------------------------------------------------------------------------
// By-id index. Used for deep links of the form `/explore/project/[id]`
// and by the future "this project is also in: ..." component.
// ---------------------------------------------------------------------------
const BY_ID: ReadonlyMap<string, Project> = (() => {
  const m = new Map<string, Project>();
  for (const p of PROJECTS) m.set(p.id, p);
  return m;
})();

// ---------------------------------------------------------------------------
// Counts derived from the same indexes. Frozen so callers cannot
// accidentally mutate the cached values.
// ---------------------------------------------------------------------------
const KIND_COUNTS: Readonly<Record<string, number>> = Object.freeze(
  Object.fromEntries(Array.from(BY_KIND.entries()).map(([k, v]) => [k, v.length])),
);
const KIND_PLATFORM_COUNTS: Readonly<Record<string, number>> = Object.freeze(
  Object.fromEntries(Array.from(BY_KIND_PLATFORM.entries()).map(([k, v]) => [k, v.length])),
);

// ---------------------------------------------------------------------------
// Enumerations. Frozen tuples; a code reviewer looking for "is `proxy` a
// valid kind" will get a TypeScript error on a typo, and the runtime list
// here is what the validator and sitemap agree on.
// ---------------------------------------------------------------------------
const ALL_KINDS: readonly ProjectKind[] = Object.freeze([
  'proxy',
  'vpn',
  'dns',
  'acceleration',
  'security',
  'monitoring',
  'ops',
  'tools',
]);
const ALL_PLATFORMS: readonly ProjectPlatform[] = Object.freeze([
  'desktop',
  'mobile',
  'cli',
  'server',
  'browser',
  'router',
]);

// ============================================================================
// Public API
// ============================================================================

export function getAllProjects(): readonly Project[] {
  return PROJECTS;
}

export function getLastUpdated(): string {
  return LAST_UPDATED;
}

export function getTotalStars(): number {
  return TOTAL_STARS;
}

export function getProjectById(id: string): Project | undefined {
  return BY_ID.get(id);
}

const EMPTY_BUCKET: readonly Project[] = Object.freeze([]);

export function getProjectsByKind(kind: ProjectKind): readonly Project[] {
  return BY_KIND.get(kind) ?? EMPTY_BUCKET;
}

export function getProjectsByKindPlatform(
  kind: ProjectKind,
  platform: ProjectPlatform,
): readonly Project[] {
  return BY_KIND_PLATFORM.get(`${kind}|${platform}`) ?? EMPTY_BUCKET;
}

export function getKindCounts(): Readonly<Record<string, number>> {
  return KIND_COUNTS;
}

export function getKindPlatformCounts(): Readonly<Record<string, number>> {
  return KIND_PLATFORM_COUNTS;
}

export function getAllKinds(): readonly ProjectKind[] {
  return ALL_KINDS;
}

export function getAllPlatforms(): readonly ProjectPlatform[] {
  return ALL_PLATFORMS;
}

export function isValidKind(s: string): s is ProjectKind {
  return (ALL_KINDS as readonly string[]).includes(s);
}

export function isValidPlatform(s: string): s is ProjectPlatform {
  return (ALL_PLATFORMS as readonly string[]).includes(s);
}

// ---------------------------------------------------------------------------
// Related projects. Score every other project against the given one using
// weighted overlap on kind, platform, tags and category. Returns the top N
// sorted by descending score. The weights are tuned so that same-kind is
// the strongest signal, shared platforms are secondary, and tag overlap
// provides fine-grained ranking within the same kind.
// ---------------------------------------------------------------------------

const WEIGHT_KIND = 10;
const WEIGHT_PLATFORM = 3;
const WEIGHT_TAG = 2;
const WEIGHT_CATEGORY = 1;

export function getRelatedProjects(id: string, limit = 4): readonly Project[] {
  const target = BY_ID.get(id);
  if (!target) return EMPTY_BUCKET;

  const targetPlatforms = new Set(target.platform);
  const targetTags = new Set(target.tags);

  const scored: { project: Project; score: number }[] = [];

  for (const p of PROJECTS) {
    if (p.id === id) continue;

    let score = 0;

    // Kind match — strongest signal
    if (p.kind === target.kind) score += WEIGHT_KIND;

    // Platform overlap
    for (const plat of p.platform) {
      if (targetPlatforms.has(plat)) score += WEIGHT_PLATFORM;
    }

    // Tag overlap
    for (const tag of p.tags) {
      if (targetTags.has(tag)) score += WEIGHT_TAG;
    }

    // Category match
    if (p.category === target.category) score += WEIGHT_CATEGORY;

    if (score > 0) scored.push({ project: p, score });
  }

  scored.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    // Tiebreak by stars descending
    return b.project.stars - a.project.stars;
  });

  return Object.freeze(scored.slice(0, limit).map((s) => s.project));
}
