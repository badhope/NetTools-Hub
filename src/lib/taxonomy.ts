// ============================================================================
// NetTools Hub — Taxonomy label tables
// ============================================================================
//
// Display names for the multi-dimensional navigation axes (kind,
// platform). The label tables carry all three languages inline; the
// `kindLabel()` / `platformLabel()` helpers look up by language and
// fall back to English, then to the slug itself.
//
// Inlining the language data here (instead of in `i18n.ts`) means the
// labels travel with the taxonomy, so a refactor that adds a new
// `kind` only has to edit this file. The price is that the same
// string ("VPN") appears three times; that's a small price for
// cohesion.
// ============================================================================

import type { Lang } from '@/lib/i18n';
import type { ProjectKind, ProjectPlatform } from '@/types/project';

type Label = { en: string; zh: string; ja: string };

/** Internal slug -> human-readable label per kind. */
const KIND_LABELS: Record<ProjectKind, Label> = {
  proxy: { en: 'Proxy cores', zh: '代理核心', ja: 'プロキシコア' },
  vpn: { en: 'VPN', zh: 'VPN', ja: 'VPN' },
  dns: { en: 'DNS', zh: 'DNS', ja: 'DNS' },
  acceleration: { en: 'Acceleration', zh: '网络加速', ja: '高速化' },
  security: { en: 'Security', zh: '安全', ja: 'セキュリティ' },
  monitoring: { en: 'Monitoring', zh: '监控', ja: '監視' },
  ops: { en: 'Deploy & operations', zh: '部署与运维', ja: 'デプロイと運用' },
  tools: { en: 'Tools & utilities', zh: '工具与杂项', ja: 'ツールと雑多' },
};

/** Internal slug -> human-readable label per platform. */
const PLATFORM_LABELS: Record<ProjectPlatform, Label> = {
  desktop: { en: 'Desktop', zh: '桌面端', ja: 'デスクトップ' },
  mobile: { en: 'Mobile', zh: '手机端', ja: 'モバイル' },
  cli: { en: 'CLI', zh: '命令行', ja: 'コマンドライン' },
  server: { en: 'Server', zh: '服务端', ja: 'サーバー' },
  browser: { en: 'Browser', zh: '浏览器', ja: 'ブラウザ' },
  router: { en: 'Router', zh: '路由器', ja: 'ルーター' },
};

export function kindLabel(kind: ProjectKind, lang: Lang = 'en'): string {
  const labels = KIND_LABELS[kind];
  return labels ? (labels[lang] ?? labels.en) : kind;
}

export function platformLabel(plat: ProjectPlatform, lang: Lang = 'en'): string {
  const labels = PLATFORM_LABELS[plat];
  return labels ? (labels[lang] ?? labels.en) : plat;
}
