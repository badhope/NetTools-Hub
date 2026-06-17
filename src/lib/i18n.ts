// ============================================================================
// NetTools Hub — i18n
// ============================================================================
//
// Three-language copy table. Keys are flat dotted strings; the
// `t()` function looks the active language up first, then falls
// back to English, then to the key itself. The key-as-fallback
// rule means a missing key surfaces as `taxonomy.kind` in the
// page rather than `undefined`, which is a useful failure mode
// for the maintainer ("oh, I forgot to translate that one")
// and never a runtime exception.
//
// Adding a new key: define it in **all three** language blocks
// before referencing it from a component. The validator script
// (`scripts/validate-projects.mjs`) does not enforce this — it
// runs over `data/`, not `src/` — so the discipline is purely
// a code-review convention.
// ============================================================================

export type Lang = 'en' | 'zh' | 'ja';

const translations: Record<Lang, Record<string, string>> = {
  en: {
    // ---- Brand / top nav -------------------------------------------------
    'site.title': 'NetTools Hub',
    'nav.home': 'Home',
    'nav.menu': 'Menu',
    'nav.close': 'Close',
    'nav.index': 'Index',
    'nav.switch_language': 'Switch language',
    'nav.back_to_kind': 'Back to {kind}',
    'editorial.edition': 'Edition I · {date}',
    'editorial.open_atlas': 'Open the index',

    // ---- Multi-level navigation (taxonomy) -------------------------------
    'taxonomy.kind': 'Kind',
    'taxonomy.platform': 'Platform',
    'taxonomy.all': 'All',
    'taxonomy.count': '{n} entries',
    'taxonomy.index': 'Index',
    'taxonomy.tree': 'Browse the tree',
    'breadcrumb.root': 'explore',

    // ---- Project card / detail metric labels -----------------------------
    'metric.stars': 'Stars',
    'metric.forks': 'Forks',
    'metric.language': 'Language',
    'metric.license': 'License',
    'metric.last_commit': 'Last commit',

    // ---- Lifecycle / editorial verdicts ----------------------------------
    'status.active': 'active',
    'status.stale': 'stale',
    'status.archived': 'archived',
    'verdict.recommended': 'recommended',
    'verdict.neutral': 'neutral',
    'verdict.caution': 'caution',
    'verdict.avoid': 'avoid',

    // ---- A11y / error / 404 ----------------------------------------------
    'a11y.main': 'Main content',
    '404.folio': '404',
    '404.description': 'This page does not exist.',
    '404.back': '← Back to home',
    'error.folio': 'Error',
    'error.title': 'Error',
    'error.description': 'An unexpected error occurred. Please try again.',
    'error.retry': 'Try again',
    'error.explore_folio': 'Explore — error',
    'error.explore_title': 'Failed to load',
    'error.explore_desc': 'Something went wrong while loading the index.',
    'error.explore_retry': 'Retry',

    // ---- Related projects ------------------------------------------------
    'related.title': 'Related Projects',

    // ---- Accessibility ---------------------------------------------------
    'a11y.skip_to_content': 'Skip to main content',
    'a11y.switch_to_light': 'Switch to light mode',
    'a11y.switch_to_dark': 'Switch to dark mode',
    'a11y.opens_new_tab': 'opens in new tab',

    // ---- Footer -----------------------------------------------------------
    'footer.disclaimer_title': 'Disclaimer',
    'footer.disclaimer_text':
      'This site (NetTools Hub) is a personally maintained link index. It only collects repository addresses and editorial descriptions of third-party open-source projects. This site does not host, distribute, endorse, or operate any linked software. Inclusion is not recommendation. Use any project linked from this site at your own risk. Full terms at',
    'footer.disclaimer_end': '.',
    'footer.maintainer': 'Maintainer',
    'footer.maintainer_desc': 'Single-maintainer, non-commercial',
    'footer.source': 'Source',
    'footer.source_desc': 'Static · MIT · No tracking',
    'footer.last_indexed': 'Last indexed',
    'footer.last_indexed_desc': 'Auto-refreshed via GitHub Actions',
    'footer.license': 'License',
    'footer.build': 'Build · static export',
    'footer.privacy': 'No cookies · No analytics · No ads',

    'theme.light': 'Light',
    'theme.dark': 'Dark',

    // ---- PWA ----------------------------------------------------------------
    'pwa.install_title': 'Install NetTools Hub',
    'pwa.install_desc': 'Install as an app for quick access and offline support.',
    'pwa.install_btn': 'Install',
    'pwa.dismiss_btn': 'Not now',
    'pwa.dismiss_label': 'Dismiss install prompt',

    // ---- Detail page ------------------------------------------------------
    'detail.timeline': 'Timeline',
    'detail.tags': 'Tags',
    'detail.highlights': 'Highlights',
    'detail.notes': 'Notes',
    'detail.view_repo': 'View Repository',
    'detail.homepage': 'Homepage',
    'detail.added': 'Added',
    'detail.by': 'by',
    'detail.view_project': 'View {name}',

    // ---- ARIA labels ------------------------------------------------------
    'aria.breadcrumb': 'Breadcrumb',
    'aria.main_content': 'Main content',
    'aria.introduction': 'Introduction',
    'aria.browse_by_kind': 'Browse by kind',
    'aria.how_maintained': 'How the index is maintained',

    // ---- Stat labels ------------------------------------------------------
    'stat.projects': 'Projects',
    'stat.kinds': 'Kinds',
    'stat.total_stars': 'Total stars',
    'stat.last_indexed': 'Last indexed',

    // ---- Landing page content --------------------------------------------
    'landing.index_label': 'Index',
    'landing.browse_by_kind': 'Browse by kind',
    'landing.how_maintained': 'How the index is maintained',
    'landing.facts': 'Facts',
    'landing.hero_pre': 'A field manual of',
    'landing.hero_mid': 'open-source network tools,',
    'landing.hero_organised_by': 'organised by',
    'landing.hero_kind': 'kind',
    'landing.hero_and_by': 'and by',
    'landing.hero_platform': 'platform',
    'landing.hero_intro':
      'NetTools Hub is a personal link index, not a directory service and not a proxy. We do not host, distribute, endorse, or operate any project linked from this page. Use at your own risk;',
    'landing.read_disclaimer': 'read the full disclaimer',
    'landing.before_installing': 'before installing anything.',
    'landing.fact_type': 'Type',
    'landing.fact_type_value': 'Static, no backend',
    'landing.fact_maintainer': 'Maintainer',
    'landing.fact_license': 'License',
    'landing.fact_edition': 'Edition',
    'landing.fact_stack': 'Stack',
    'landing.fact_stack_value': 'Next.js · TypeScript · Tailwind v4',
    'landing.maintained_desc':
      'The {code} file is the only source of truth. The schema and entry format are documented in',
    'landing.maintained_validator': '; the validator is',
    'landing.maintained_refresh':
      '; the live metadata is refreshed by a scheduled GitHub Action every Sunday 03:00 UTC.',

    // ---- Explore page meta ------------------------------------------------
    'explore.all_projects': 'All projects',
    'explore.total_stars': 'total stars',
    'explore.sorted_by_stars': 'sorted by stars',
    'explore.back_to_index': '← back to index',
    'explore.back_to_kind': '← back to {kind}',
    'explore.meta_index': '[ index ]',
    'explore.meta_detail': '[ detail ]',
    'explore.stars': 'stars',
  },
  zh: {
    'site.title': 'NetTools Hub',
    'nav.home': '首页',
    'nav.menu': '菜单',
    'nav.close': '关闭',
    'nav.index': '索引',
    'nav.switch_language': '切换语言',
    'nav.back_to_kind': '返回 {kind}',
    'editorial.edition': '第一版 · {date}',
    'editorial.open_atlas': '打开索引',

    'taxonomy.kind': '类别',
    'taxonomy.platform': '平台',
    'taxonomy.all': '全部',
    'taxonomy.count': '{n} 条',
    'taxonomy.index': '索引',
    'taxonomy.tree': '浏览树形索引',
    'breadcrumb.root': 'explore',

    'metric.stars': '星数',
    'metric.forks': '复刻',
    'metric.language': '语言',
    'metric.license': '许可证',
    'metric.last_commit': '最后提交',

    'status.active': '活跃',
    'status.stale': '不活跃',
    'status.archived': '已归档',
    'verdict.recommended': '推荐',
    'verdict.neutral': '中性',
    'verdict.caution': '谨慎',
    'verdict.avoid': '不推荐',

    'a11y.main': '主内容',
    '404.folio': '404',
    '404.description': '该页面不存在。',
    '404.back': '← 返回首页',
    'error.folio': '错误',
    'error.title': '错误',
    'error.description': '出现意外错误，请重试。',
    'error.retry': '重试',
    'error.explore_folio': '探索 — 错误',
    'error.explore_title': '加载失败',
    'error.explore_desc': '加载索引时出现问题。',
    'error.explore_retry': '重新尝试',

    'related.title': '相关项目',

    'a11y.skip_to_content': '跳转到主内容',
    'a11y.switch_to_light': '切换到亮色模式',
    'a11y.switch_to_dark': '切换到暗色模式',
    'a11y.opens_new_tab': '在新标签页打开',

    'footer.disclaimer_title': '免责声明',
    'footer.disclaimer_text':
      '本站点（NetTools Hub）是一个个人维护的链接索引，仅收录第三方开源项目的仓库地址与一段编辑性说明。本站不托管、不分发、不背书、不运营任何被链接的软件；收录即非推荐。使用任何通过本站跳转到的项目，风险由使用者自行承担。完整条款见',
    'footer.disclaimer_end': '。',
    'footer.maintainer': '维护者',
    'footer.maintainer_desc': '个人维护，非商业',
    'footer.source': '源码',
    'footer.source_desc': '静态 · MIT · 无追踪',
    'footer.last_indexed': '最后索引',
    'footer.last_indexed_desc': '通过 GitHub Actions 自动刷新',
    'footer.license': '许可证',
    'footer.build': '构建 · 静态导出',
    'footer.privacy': '无 Cookie · 无分析 · 无广告',

    'theme.light': '亮色',
    'theme.dark': '暗色',

    'pwa.install_title': '安装 NetTools Hub',
    'pwa.install_desc': '安装为应用以获得快速访问和离线支持。',
    'pwa.install_btn': '安装',
    'pwa.dismiss_btn': '暂不',
    'pwa.dismiss_label': '关闭安装提示',

    'detail.timeline': '时间线',
    'detail.tags': '标签',
    'detail.highlights': '亮点',
    'detail.notes': '备注',
    'detail.view_repo': '查看仓库',
    'detail.homepage': '主页',
    'detail.added': '添加时间',
    'detail.by': '作者',
    'detail.view_project': '查看{name}',

    'aria.breadcrumb': '面包屑导航',
    'aria.main_content': '主内容',
    'aria.introduction': '介绍',
    'aria.browse_by_kind': '按分类浏览',
    'aria.how_maintained': '索引维护方式',

    'stat.projects': '项目数',
    'stat.kinds': '分类数',
    'stat.total_stars': '总星标',
    'stat.last_indexed': '最后索引',

    // ---- Landing page content --------------------------------------------
    'landing.index_label': '索引',
    'landing.browse_by_kind': '按分类浏览',
    'landing.how_maintained': '索引维护方式',
    'landing.facts': '事实',
    'landing.hero_pre': '',
    'landing.hero_mid': '个开源网络工具手册，',
    'landing.hero_organised_by': '按',
    'landing.hero_kind': '类别',
    'landing.hero_and_by': '与',
    'landing.hero_platform': '平台',
    'landing.hero_intro':
      'NetTools Hub 是一个个人维护的链接索引，不是目录服务，也不是代理。我们不托管、不分发、不背书、不运营任何被链接的项目。使用风险自负；',
    'landing.read_disclaimer': '阅读完整免责声明',
    'landing.before_installing': '后再安装任何内容。',
    'landing.fact_type': '类型',
    'landing.fact_type_value': '静态，无后端',
    'landing.fact_maintainer': '维护者',
    'landing.fact_license': '许可证',
    'landing.fact_edition': '版本',
    'landing.fact_stack': '技术栈',
    'landing.fact_stack_value': 'Next.js · TypeScript · Tailwind v4',
    'landing.maintained_desc': '{code} 文件是唯一的数据来源。架构与条目格式详见',
    'landing.maintained_validator': '；验证器为',
    'landing.maintained_refresh': '；元数据由 GitHub Action 每周日 UTC 03:00 自动刷新。',

    // ---- Explore page meta ------------------------------------------------
    'explore.all_projects': '全部项目',
    'explore.total_stars': '总星标',
    'explore.sorted_by_stars': '按星标排序',
    'explore.back_to_index': '← 返回索引',
    'explore.back_to_kind': '← 返回{kind}',
    'explore.meta_index': '[ 索引 ]',
    'explore.meta_detail': '[ 详情 ]',
    'explore.stars': '星标',
  },
  ja: {
    'site.title': 'NetTools Hub',
    'nav.home': 'ホーム',
    'nav.menu': 'メニュー',
    'nav.close': '閉じる',
    'nav.index': '索引',
    'nav.switch_language': '言語切替',
    'nav.back_to_kind': '{kind} に戻る',
    'editorial.edition': '初版 · {date}',
    'editorial.open_atlas': '索引を開く',

    'taxonomy.kind': '種別',
    'taxonomy.platform': 'プラットフォーム',
    'taxonomy.all': 'すべて',
    'taxonomy.count': '{n} 件',
    'taxonomy.index': '索引',
    'taxonomy.tree': 'ツリーを閲覧',
    'breadcrumb.root': 'explore',

    'metric.stars': 'スター',
    'metric.forks': 'フォーク',
    'metric.language': '言語',
    'metric.license': 'ライセンス',
    'metric.last_commit': '最終コミット',

    'status.active': '稼働中',
    'status.stale': '停滞',
    'status.archived': 'アーカイブ',
    'verdict.recommended': '推奨',
    'verdict.neutral': '中立',
    'verdict.caution': '注意',
    'verdict.avoid': '非推奨',

    'a11y.main': 'メインコンテンツ',
    '404.folio': '404',
    '404.description': 'このページは存在しません。',
    '404.back': '← ホームへ戻る',
    'error.folio': 'エラー',
    'error.title': 'エラー',
    'error.description': '予期しないエラーが発生しました。再試行してください。',
    'error.retry': '再試行',
    'error.explore_folio': '探索 — エラー',
    'error.explore_title': '読み込み失敗',
    'error.explore_desc': '索引の読み込み中に問題が発生しました。',
    'error.explore_retry': '再試行',

    'related.title': '関連プロジェクト',

    'a11y.skip_to_content': 'メインコンテンツへスキップ',
    'a11y.switch_to_light': 'ライトモードに切り替え',
    'a11y.switch_to_dark': 'ダークモードに切り替え',
    'a11y.opens_new_tab': '新しいタブで開く',

    'footer.disclaimer_title': '免責事項',
    'footer.disclaimer_text':
      '本サイト（NetTools Hub）は個人が維持するリンクインデックスです。第三者のオープンソースプロジェクトのリポジトリアドレスと編集説明のみを収録しています。本サイトはリンク先のソフトウェアをホスト、配布、推奨、運営しません。収録は推奨を意味しません。本サイトからリンクされたプロジェクトの使用は、利用者自身の責任で行ってください。完全な条項は',
    'footer.disclaimer_end': '。',
    'footer.maintainer': 'メンテナ',
    'footer.maintainer_desc': '個人運営、非営利',
    'footer.source': 'ソース',
    'footer.source_desc': '静的 · MIT · トラッキングなし',
    'footer.last_indexed': '最終インデックス',
    'footer.last_indexed_desc': 'GitHub Actions による自動更新',
    'footer.license': 'ライセンス',
    'footer.build': 'ビルド · 静的エクスポート',
    'footer.privacy': 'Cookie なし · アナリティクスなし · 広告なし',

    'theme.light': 'ライト',
    'theme.dark': 'ダーク',

    'pwa.install_title': 'NetTools Hub をインストール',
    'pwa.install_desc':
      'アプリとしてインストールすると、クイックアクセスとオフラインサポートが利用できます。',
    'pwa.install_btn': 'インストール',
    'pwa.dismiss_btn': '後で',
    'pwa.dismiss_label': 'インストール案内を閉じる',

    'detail.timeline': 'タイムライン',
    'detail.tags': 'タグ',
    'detail.highlights': 'ハイライト',
    'detail.notes': 'ノート',
    'detail.view_repo': 'リポジトリを見る',
    'detail.homepage': 'ホームページ',
    'detail.added': '追加日',
    'detail.by': 'by',
    'detail.view_project': '{name}を見る',

    'aria.breadcrumb': 'パンくずリスト',
    'aria.main_content': 'メインコンテンツ',
    'aria.introduction': 'イントロダクション',
    'aria.browse_by_kind': '種類別に閲覧',
    'aria.how_maintained': 'インデックスの維持方法',

    'stat.projects': 'プロジェクト',
    'stat.kinds': '種類',
    'stat.total_stars': '総スター数',
    'stat.last_indexed': '最終インデックス',

    // ---- Landing page content --------------------------------------------
    'landing.index_label': '索引',
    'landing.browse_by_kind': '種類別に閲覧',
    'landing.how_maintained': 'インデックスの維持方法',
    'landing.facts': '事実',
    'landing.hero_pre': '',
    'landing.hero_mid': '個のオープンソースネットワークツールのマニュアル、',
    'landing.hero_organised_by': '',
    'landing.hero_kind': '種類',
    'landing.hero_and_by': '・',
    'landing.hero_platform': 'プラットフォーム',
    'landing.hero_intro':
      'NetTools Hub は個人が維持するリンクインデックスであり、ディレクトリサービスでもプロキシでもありません。リンク先のプロジェクトをホスト、配布、推奨、運営しません。自己責任でご利用ください；',
    'landing.read_disclaimer': '完全な免責事項を読む',
    'landing.before_installing': 'インストール前に。',
    'landing.fact_type': 'タイプ',
    'landing.fact_type_value': '静的、バックエンドなし',
    'landing.fact_maintainer': 'メンテナ',
    'landing.fact_license': 'ライセンス',
    'landing.fact_edition': 'エディション',
    'landing.fact_stack': 'スタック',
    'landing.fact_stack_value': 'Next.js · TypeScript · Tailwind v4',
    'landing.maintained_desc': '{code} ファイルが唯一の情報源です。スキーマとエントリ形式は',
    'landing.maintained_validator': 'に記載、バリデータは',
    'landing.maintained_refresh':
      '、メタデータは GitHub Action で毎週日曜 UTC 03:00 に更新されます。',

    // ---- Explore page meta ------------------------------------------------
    'explore.all_projects': 'すべてのプロジェクト',
    'explore.total_stars': '総スター',
    'explore.sorted_by_stars': 'スター順',
    'explore.back_to_index': '← 索引に戻る',
    'explore.back_to_kind': '← {kind}に戻る',
    'explore.meta_index': '[ 索引 ]',
    'explore.meta_detail': '[ 詳細 ]',
    'explore.stars': 'スター',
  },
};

export function t(lang: Lang, key: string, params?: Record<string, string | number>): string {
  let text = translations[lang]?.[key] || translations.en[key] || key;
  if (params) {
    // `for…in` walks own keys without allocating an
    // `Object.entries()` array on every call. With ~5 keys per
    // call site and `t()` running on every render of the project
    // list, the array allocations add up to noticeable GC churn
    // (and `t()` is also called for the fallback path when a key
    // is missing in the active language).
    for (const k in params) {
      const v = params[k];
      if (v === undefined) continue;
      text = text.replace(`{${k}}`, String(v));
    }
  }
  return text;
}

export const LANG_OPTIONS: { value: Lang; label: string }[] = [
  { value: 'en', label: 'EN' },
  { value: 'zh', label: '中文' },
  { value: 'ja', label: '日本語' },
];

/**
 * Build a localized internal path. The English variant is the canonical
 * URL (no `?lang=` query) so that search engines and the sitemap
 * see a single, stable address; the other two languages opt in via
 * the `?lang=` query parameter. Centralising the rule here avoids
 * subtle bugs where one component forgets the `lang === "en"` check
 * and ends up with `/explore?lang=zh&lang=en` style URL soup.
 */
export function langParam(lang: Lang, path: string): string {
  return lang === 'en' ? path : `${path}?lang=${lang}`;
}

/**
 * Like {@link langParam}, but safe to call on a path that already
 * carries a query string. The `?lang=` is then appended with `&`
 * so we never end up with a double-question-mark bug.
 */
export function withLang(lang: Lang, path: string): string {
  if (lang === 'en') return path;
  return path.includes('?') ? `${path}&lang=${lang}` : `${path}?lang=${lang}`;
}

/**
 * Apply a new language across the whole client:
 *   1. Write the URL `?lang=` query (delete it for English, since
 *      English is the canonical URL for the static-export sitemap).
 *   2. Persist to `localStorage` so the next visit keeps it, with a
 *      `try/catch` because storage can be disabled in private windows
 *      and we don't want the language switch to throw in that case.
 *   3. Dispatch a `nethub:langchange` custom event so sibling
 *      components (e.g. `set-html-lang`) can react without a
 *      prop-drilling subscription tree.
 *
 * Centralising this in one place keeps the URL / storage / event
 * triplet in lockstep.
 */
export function setLangAndPersist(newLang: Lang): void {
  if (typeof window === 'undefined') return;
  const url = new URL(window.location.href);
  if (newLang === 'en') url.searchParams.delete('lang');
  else url.searchParams.set('lang', newLang);
  window.history.replaceState({}, '', url.toString());
  try {
    window.localStorage.setItem(LANG_STORAGE_KEY, newLang);
  } catch {
    /* storage may be disabled */
  }
  window.dispatchEvent(new CustomEvent('nethub:langchange', { detail: { lang: newLang } }));
}

/**
 * `localStorage` key for the user's preferred language. Kept as a
 * single constant so it's trivial to grep and rename.
 */
export const LANG_STORAGE_KEY = 'nethub.lang';

/**
 * Resolve the initial client-side language using the same precedence
 * as `set-html-lang`:
 *   1. `?lang=` query string (deep link / canonical URL wins).
 *   2. `localStorage` (sticky user preference).
 *   3. `navigator.language` family match.
 *   4. English (the i18n fallback).
 */
export function resolveInitialLang(): Lang {
  if (typeof window === 'undefined') return 'en';
  const fromUrl = readLangFromUrl();
  if (fromUrl) return fromUrl;
  try {
    const stored = window.localStorage.getItem(LANG_STORAGE_KEY);
    if (stored === 'en' || stored === 'zh' || stored === 'ja') return stored;
  } catch {
    /* storage may be disabled */
  }
  if (typeof navigator !== 'undefined') {
    const lang = navigator.language.toLowerCase();
    if (lang.startsWith('zh')) return 'zh';
    if (lang.startsWith('ja')) return 'ja';
  }
  return 'en';
}

/**
 * BCP-47 tags for each language. Used to drive `<html lang>`,
 * `<link rel="alternate" hreflang>` and the OpenGraph `locale` field.
 * Keeping them next to the `Lang` union makes it impossible to ship
 * a translation in a new language without also declaring its locale.
 */
export const LANG_HTML_LANG: Record<Lang, string> = {
  en: 'en',
  zh: 'zh-Hans',
  ja: 'ja',
};

export const LANG_OG_LOCALE: Record<Lang, string> = {
  en: 'en_US',
  zh: 'zh_CN',
  ja: 'ja_JP',
};

/**
 * Read the current language from the URL `?lang=` query parameter.
 *
 * Safe to call on the server (returns `"en"`) and on the client
 * (returns the URL value when valid, otherwise `"en"`).
 */
export function readLangFromUrl(): Lang {
  if (typeof window === 'undefined') return 'en';
  try {
    const url = new URL(window.location.href);
    const v = url.searchParams.get('lang');
    if (v === 'en' || v === 'zh' || v === 'ja') return v;
  } catch {
    /* ignore: invalid URL or restricted env */
  }
  return 'en';
}
