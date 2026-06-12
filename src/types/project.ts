// ============================================================================
// NetTools Hub — Project type definitions
// ============================================================================
//
// The data model supports two orthogonal taxonomies:
//
//   - `kind`     = the *what* (proxy / VPN / DNS / acceleration / ...)
//   - `platform` = the *where* (desktop / mobile / CLI / server / router / ...)
//
// The site's URL hierarchy is derived from these two fields, e.g.
//
//   /explore/proxy/desktop   -> all proxy projects that run on desktop
//   /explore/dns/server      -> DNS tools that run on a server
//
// `category` is kept as a flat third axis (the *which*) for the
// editorial grouping the user has come to expect (GUI clients,
// subscription managers, etc.). The combination of the three is the
// unique address of a project; the schema validator in
// `scripts/validate-projects.mjs` enforces uniqueness on
// `(kind, platform[], category, id)`.

/** The "what" — the primary kind of network tool. */
export type ProjectKind =
  | "proxy"        // proxy cores (clash, v2ray, sing-box, ...)
  | "vpn"          // VPN wire protocols (wireguard, openvpn, ...)
  | "dns"          // DNS resolvers / filters / smartdns
  | "acceleration" // GitHub acceleration / mirror / CDN
  | "security"     // WAF / IDS / honeypot / firewall
  | "monitoring"   // smokeping / prometheus exporters / uptime
  | "ops"          // docker / orchestration / server mgmt
  | "tools";       // utilities / network test / data transfer

/** The "where" — runtime platform(s) a project supports. */
export type ProjectPlatform =
  | "desktop"   // Windows / macOS / Linux native GUI or service
  | "mobile"    // iOS / Android app
  | "cli"       // command-line / TUI tool
  | "server"    // server / daemon
  | "browser"   // browser extension
  | "router";   // OpenWrt / router firmware

/**
 * Editorial verdict — the maintainer's personal take. Calibrated
 * against the disclaimer in DISCLAIMER.md: this is a *navigational*
 * signal, not a guarantee, and the project page makes that clear.
 */
export type ProjectVerdict =
  | "recommended" // actively used and worth picking up
  | "neutral"     // known to work, no strong opinion
  | "caution"     // works but has caveats; see `notes`
  | "avoid";      // known unmaintained, broken, or harmful

/**
 * Activity status — derived from `lastCommit` by the validator
 * (see `scripts/validate-projects.mjs`). Stored in the data so
 * the build does not have to repeat the comparison on every
 * render, and so a manual override (e.g. "the repo is stale but
 * the project is still the standard") is possible.
 */
export type ProjectStatus = "active" | "stale" | "archived";

export interface ProjectCategory {
  name: string;
  description: string;
  color: string[];
}

export interface Project {
  // -- Identity --------------------------------------------------------------
  id: string;
  name: string;
  author: string;
  description: string;
  url: string;
  homepage?: string;

  // -- Metrics (refreshed by scripts/refresh-projects.mjs) -------------------
  stars: number;
  forks: number;
  language: string;
  license: string;

  // -- Taxonomies ------------------------------------------------------------
  /**
   * The "what". Each project has exactly one kind — a sing-box is
   * a proxy core, a smartdns is a dns tool, a wireguard is a vpn.
   * Drives the top-level `/explore/<kind>/...` path segment.
   */
  kind: ProjectKind;
  /**
   * The "where". Multi-valued because some projects ship for
   * multiple runtimes (e.g. sing-box runs on server *and* mobile).
   * Drives the second-level path segment.
   */
  platform: ProjectPlatform[];
  /**
   * Editorial sub-bucket (GUI client, subscription manager, rule
   * collection, etc.). Flat enumeration, derived from the existing
   * `categories` table; the third-level path segment.
   */
  category: string;
  /** Free-form tags for search and the per-project "Tags" row. */
  tags: string[];

  // -- Editorial -------------------------------------------------------------
  /** Optional one-or-two-line personal take on the project. */
  notes?: string;
  /** Maintainer verdict (see ProjectVerdict). */
  verdict?: ProjectVerdict;

  // -- Lifecycle -------------------------------------------------------------
  /** Date of the last observed commit (ISO 8601, UTC). */
  lastCommit: string;
  /** Date the entry was first added to the index (ISO 8601, UTC). */
  addedAt: string;
  /** Activity status. Derived by the validator, overridable manually. */
  status: ProjectStatus;

  // -- Visual (kept for back-compat with the existing card) ------------------
  highlights: string[];
  /** First colour is the project card's left rail; rest are unused. */
  gradient: string[];
}

export interface ProjectsData {
  /** Date the index was last touched (ISO 8601, UTC). */
  lastUpdated: string;
  /** Schema version, bumped on breaking changes. */
  schemaVersion: number;
  categories: Record<string, ProjectCategory>;
  projects: Project[];
}

export type SortOption = "default" | "stars" | "name" | "updated" | "kind";
