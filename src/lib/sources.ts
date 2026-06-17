// ============================================================================
// NetTools Hub — Free proxy sources data access + taxonomy
// ============================================================================
//
// Mirrors the shape of `lib/projects.ts` but for the `ProxySource`
// data model. The data file lives at `data/free-sources.json` and is
// imported at build time; all functions are synchronous and cache
// their results in module-level variables.
// ============================================================================

import type {
  ProxySource,
  ProxySourcesData,
  SourceType,
  SourceFormat,
  UpdateFrequency,
} from '@/types/source';
import type { Lang } from '@/lib/i18n';
import rawData from '../../data/free-sources.json';

const data = rawData as ProxySourcesData;

// ============================================================================
// Schema version check
// ============================================================================

const CURRENT_SCHEMA_VERSION = 1;

if (data.schemaVersion !== CURRENT_SCHEMA_VERSION) {
  console.warn(
    `[sources] Schema version mismatch: expected ${CURRENT_SCHEMA_VERSION}, got ${data.schemaVersion}. Some features may not work correctly.`,
  );
}

// ============================================================================
// Taxonomy labels
// ============================================================================

type Label = { en: string; zh: string; ja: string };

/** Source type labels (github / website / telegram / tool). */
const SOURCE_TYPE_LABELS: Record<SourceType, Label> = {
  github: { en: 'GitHub repo', zh: 'GitHub 仓库', ja: 'GitHub リポジトリ' },
  website: { en: 'Website', zh: '网站', ja: 'ウェブサイト' },
  telegram: { en: 'Telegram', zh: 'Telegram 频道', ja: 'Telegram' },
  tool: { en: 'Tool', zh: '工具', ja: 'ツール' },
};

/** Source format labels (what the source provides). */
const SOURCE_FORMAT_LABELS: Record<SourceFormat, Label> = {
  subscription: { en: 'Subscription', zh: '订阅链接', ja: 'サブスクリプション' },
  nodes: { en: 'Node list', zh: '节点列表', ja: 'ノードリスト' },
  converter: { en: 'Converter', zh: '格式转换', ja: 'コンバーター' },
  tester: { en: 'Tester', zh: '测速验证', ja: 'テスター' },
  aggregator: { en: 'Aggregator', zh: '聚合抓取', ja: 'アグリゲーター' },
  tutorial: { en: 'Tutorial', zh: '教程合集', ja: 'チュートリアル' },
};

/** Update frequency labels. */
const FREQUENCY_LABELS: Record<UpdateFrequency, Label> = {
  daily: { en: 'Daily', zh: '每日', ja: '毎日' },
  hourly: { en: 'Every few hours', zh: '数小时', ja: '数時間' },
  weekly: { en: 'Weekly', zh: '每周', ja: '毎週' },
  irregular: { en: 'Irregular', zh: '不定期', ja: '不定期' },
  stale: { en: 'Stale', zh: '已停更', ja: '更新停止' },
};

/** Category labels for the page section grouping. */
const CATEGORY_LABELS: Record<string, Label> = {
  'node-repos': { en: 'Node repositories', zh: '节点仓库', ja: 'ノードリポジトリ' },
  websites: { en: 'Websites', zh: '网站', ja: 'ウェブサイト' },
  telegram: { en: 'Telegram channels', zh: 'Telegram 频道', ja: 'Telegram チャンネル' },
  converters: { en: 'Subscription converters', zh: '订阅转换工具', ja: 'サブスクリプション変換' },
  testers: { en: 'Node testers', zh: '节点测速工具', ja: 'ノードテスター' },
};

/** Canonical ordering of categories for display. */
export const SOURCE_CATEGORY_ORDER = [
  'node-repos',
  'websites',
  'telegram',
  'converters',
  'testers',
] as const;

export function sourceTypeLabel(type: SourceType, lang: Lang = 'en'): string {
  return SOURCE_TYPE_LABELS[type]?.[lang] ?? SOURCE_TYPE_LABELS[type]?.en ?? type;
}

export function sourceFormatLabel(format: SourceFormat, lang: Lang = 'en'): string {
  return SOURCE_FORMAT_LABELS[format]?.[lang] ?? SOURCE_FORMAT_LABELS[format]?.en ?? format;
}

export function frequencyLabel(freq: UpdateFrequency, lang: Lang = 'en'): string {
  return FREQUENCY_LABELS[freq]?.[lang] ?? FREQUENCY_LABELS[freq]?.en ?? freq;
}

export function sourceCategoryLabel(category: string, lang: Lang = 'en'): string {
  return CATEGORY_LABELS[category]?.[lang] ?? CATEGORY_LABELS[category]?.en ?? category;
}

// ============================================================================
// Data access
// ============================================================================

let cachedSources: readonly ProxySource[] | null = null;

/** All sources, sorted by status (active first), then stars (desc), then name. */
export function getAllSources(): readonly ProxySource[] {
  if (cachedSources) return cachedSources;
  cachedSources = Object.freeze(
    [...data.sources].sort((a, b) => {
      // Active first, then by stars desc, then by name.
      if (a.status !== b.status) {
        if (a.status === 'active') return -1;
        if (b.status === 'active') return 1;
      }
      const sa = a.stars ?? 0;
      const sb = b.stars ?? 0;
      if (sb !== sa) return sb - sa;
      return a.name.localeCompare(b.name);
    }),
  );
  return cachedSources;
}

/** Sources filtered by category, preserving sort order. */
export function getSourcesByCategory(category: string): ProxySource[] {
  return getAllSources().filter((s) => s.category === category);
}

/** Per-category counts. */
export function getSourceCategoryCounts(): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const s of getAllSources()) {
    counts[s.category] = (counts[s.category] ?? 0) + 1;
  }
  return counts;
}

/** Total number of sources. */
export function getSourceCount(): number {
  return data.sources.length;
}

/** Last-updated timestamp from the data file. */
export function getSourcesLastUpdated(): string {
  return data.lastUpdated;
}
