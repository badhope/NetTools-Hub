// ============================================================================
// NetTools Hub — Free proxy source type definitions
// ============================================================================
//
// A "free proxy source" is NOT a software project — it is a resource
// that publishes free proxy nodes, subscription links, or node lists.
// Examples: GitHub repos that auto-crawl nodes daily, websites that
// list free servers, Telegram channels, subscription converters.
//
// This is a separate data model from `Project` because the fields,
// display needs, and user intent are fundamentally different:
//
//   - A Project is a tool you *install* (has stars, license, platforms).
//   - A Source is a resource you *visit* (has update frequency, format,
//     and a "what it provides" descriptor).
//
// The two share the /free-sources route but never mix in the same grid.
// ============================================================================

/** Where the source lives. */
export type SourceType =
  | 'github' // GitHub repository
  | 'website' // standalone website
  | 'telegram' // Telegram channel
  | 'tool'; // self-hostable tool (converter, tester, aggregator)

/** What format the source delivers. */
export type SourceFormat =
  | 'subscription' // a subscription URL (clash yaml, v2ray base64, etc.)
  | 'nodes' // raw node list (ss://, vmess://, trojan:// links)
  | 'converter' // converts between subscription formats
  | 'tester' // tests/validates node liveness and speed
  | 'aggregator' // crawls + aggregates from multiple upstreams
  | 'tutorial'; // guide / tutorial (not nodes itself)

/** How often the source publishes new content. */
export type UpdateFrequency = 'daily' | 'hourly' | 'weekly' | 'irregular' | 'stale';

/** Activity status — mirrors the Project status semantics. */
export type SourceStatus = 'active' | 'stale' | 'archived';

/**
 * A single free proxy source entry.
 *
 * The `id` is a kebab-case slug used in URLs and React keys. The
 * `url` is the canonical link the user follows to get the resource.
 */
export interface ProxySource {
  // -- Identity --------------------------------------------------------------
  id: string;
  name: string;
  description: string;
  url: string;

  // -- Classification --------------------------------------------------------
  type: SourceType;
  /** What the source provides (subscription, nodes, converter, ...). */
  format: SourceFormat;
  /**
   * Editorial sub-bucket for grouping within the page. Flat string,
   * e.g. "node-repos", "websites", "telegram", "converters", "testers".
   */
  category: string;

  // -- Metadata --------------------------------------------------------------
  /** Primary language of the source's content. */
  language: 'zh' | 'en' | 'zh-en';
  /** How often new content is published. */
  updateFrequency: UpdateFrequency;
  /** Activity status. */
  status: SourceStatus;

  // -- Editorial -------------------------------------------------------------
  /** Optional one-line caveat or usage note. */
  notes?: string;
  /**
   * Optional star count (for GitHub repos only). Rounded to nearest
   * integer; 0 for non-GitHub sources. Used for sorting and display.
   */
  stars?: number;

  // -- Lifecycle -------------------------------------------------------------
  /** Date the entry was first added (ISO 8601, UTC). */
  addedAt: string;
}

/** Top-level container for the free-sources data file. */
export interface ProxySourcesData {
  /** Date the index was last touched (ISO 8601, UTC). */
  lastUpdated: string;
  /** Schema version. */
  schemaVersion: number;
  sources: ProxySource[];
}
