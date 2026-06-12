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
    'editorial.edition': 'Edition I · {date}',
    'editorial.open_atlas': 'Open the index',

    // ---- Multi-level navigation (taxonomy + table) -----------------------
    'taxonomy.kind': 'Kind',
    'taxonomy.platform': 'Platform',
    'taxonomy.all': 'All',
    'taxonomy.count': '{n} entries',
    'taxonomy.index': 'Index',
    'taxonomy.tree': 'Browse the tree',
    'breadcrumb.root': 'explore',
    'table.col.name': 'Name',
    'table.col.platforms': 'Platforms',
    'table.col.stars': 'Stars',
    'table.col.last_commit': 'Last commit',
    'table.col.license': 'License',
    'table.col.status': 'Status',
    'table.col.verdict': 'Verdict',
    'table.empty': 'No entries match this filter.',

    // ---- Empty state -----------------------------------------------------
    'empty.title': 'No entries match this filter.',
    'empty.description': 'Try adjusting your filters or browse all projects.',
    'empty.back': '← Back to all projects',

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
    'error.description': 'An unexpected error occurred. Please try again.',
    'error.retry': 'Try again',
    'error.explore_folio': 'Explore — error',
    'error.explore_desc': 'Something went wrong while loading the index.',
    'error.explore_retry': 'Retry',

    // ---- Search & Filter -------------------------------------------------
    'search.placeholder': 'Search projects...',
    'search.results_count': '{count} results',
    'search.clear': 'Clear search',
    'search.clear_all': 'Clear all filters',
    'filter.all_languages': 'All languages',
    'sort.stars': 'Sort by stars',
    'sort.name': 'Sort by name',
    'sort.last_commit': 'Sort by last commit',

    // ---- Related projects ------------------------------------------------
    'related.title': 'Related Projects',

    // ---- Accessibility ---------------------------------------------------
    'a11y.skip_to_content': 'Skip to main content',
  },
  zh: {
    'site.title': 'NetTools Hub',
    'nav.home': '首页',
    'nav.menu': '菜单',
    'nav.close': '关闭',
    'nav.index': '索引',
    'nav.switch_language': '切换语言',
    'editorial.edition': '第一版 · {date}',
    'editorial.open_atlas': '打开索引',

    'taxonomy.kind': '类别',
    'taxonomy.platform': '平台',
    'taxonomy.all': '全部',
    'taxonomy.count': '{n} 条',
    'taxonomy.index': '索引',
    'taxonomy.tree': '浏览树形索引',
    'breadcrumb.root': 'explore',
    'table.col.name': '名称',
    'table.col.platforms': '平台',
    'table.col.stars': '星数',
    'table.col.last_commit': '最后提交',
    'table.col.license': '许可证',
    'table.col.status': '状态',
    'table.col.verdict': '编辑评',
    'table.empty': '没有匹配的项目。',

    'empty.title': '没有匹配的项目。',
    'empty.description': '请尝试调整筛选条件，或浏览全部项目。',
    'empty.back': '← 返回全部项目',

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
    'error.description': '出现意外错误，请重试。',
    'error.retry': '重试',
    'error.explore_folio': '探索 — 错误',
    'error.explore_desc': '加载索引时出现问题。',
    'error.explore_retry': '重新尝试',

    'search.placeholder': '搜索项目...',
    'search.results_count': '{count} 个结果',
    'search.clear': '清除搜索',
    'search.clear_all': '清除所有筛选',
    'filter.all_languages': '所有语言',
    'sort.stars': '按星标排序',
    'sort.name': '按名称排序',
    'sort.last_commit': '按最后提交排序',

    'related.title': '相关项目',

    'a11y.skip_to_content': '跳转到主内容',
  },
  ja: {
    'site.title': 'NetTools Hub',
    'nav.home': 'ホーム',
    'nav.menu': 'メニュー',
    'nav.close': '閉じる',
    'nav.index': '索引',
    'nav.switch_language': '言語切替',
    'editorial.edition': '初版 · {date}',
    'editorial.open_atlas': '索引を開く',

    'taxonomy.kind': '種別',
    'taxonomy.platform': 'プラットフォーム',
    'taxonomy.all': 'すべて',
    'taxonomy.count': '{n} 件',
    'taxonomy.index': '索引',
    'taxonomy.tree': 'ツリーを閲覧',
    'breadcrumb.root': 'explore',
    'table.col.name': '名称',
    'table.col.platforms': 'プラットフォーム',
    'table.col.stars': 'スター',
    'table.col.last_commit': '最終コミット',
    'table.col.license': 'ライセンス',
    'table.col.status': '状態',
    'table.col.verdict': '評価',
    'table.empty': '一致するエントリはありません。',

    'empty.title': '一致するエントリはありません。',
    'empty.description': 'フィルター条件を変更するか、すべてのプロジェクトをご覧ください。',
    'empty.back': '← すべてのプロジェクトに戻る',

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
    'error.description': '予期しないエラーが発生しました。再試行してください。',
    'error.retry': '再試行',
    'error.explore_folio': '探索 — エラー',
    'error.explore_desc': '索引の読み込み中に問題が発生しました。',
    'error.explore_retry': '再試行',

    'search.placeholder': 'プロジェクトを検索...',
    'search.results_count': '{count} 件の結果',
    'search.clear': '検索をクリア',
    'search.clear_all': 'すべてのフィルターをクリア',
    'filter.all_languages': 'すべての言語',
    'sort.stars': 'スター順',
    'sort.name': '名前順',
    'sort.last_commit': '最終コミット順',

    'related.title': '関連プロジェクト',

    'a11y.skip_to_content': 'メインコンテンツへスキップ',
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
