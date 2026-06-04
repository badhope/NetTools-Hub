export type Lang = "en" | "zh" | "ja";

const translations: Record<Lang, Record<string, string>> = {
  en: {
    "site.title": "NetTools Hub",
    "features.title": "At a glance",
    "features.subtitle": "Discover, search, and filter the network tools you need — all in one place",
    "features.curated": "{total}+ Curated Projects",
    "features.curated_desc": "Covering proxy cores, GUI clients, subscription management, GitHub acceleration, DNS tools and 6 themed groups",
    "features.search": "Smart Search",
    "features.search_desc": "Search by project name, author, tag, or description to quickly find what you need",
    "features.sort": "Multi-Dimensional Sort",
    "features.sort_desc": "Sort by Stars, name, or last update to find the hottest and latest projects",
    "features.responsive": "Fully Responsive",
    "features.responsive_desc": "Perfectly adapted for desktop, tablet, and mobile — browse anywhere",
    "features.maintained": "Actively Maintained",
    "features.maintained_desc": "Only includes actively updated projects, outdated ones are removed",
    "features.stars": "{stars}+ Total Stars",
    "features.stars_desc": "High-quality open-source projects with clear community recognition",
    "categories.title": "Browse by Group",
    "categories.subtitle": "6 themed groups covering the full network toolchain — click into any group to dive deeper",
    "footer.text": "NetTools Hub · Network Tools Navigation Platform",
    "footer.disclaimer": "This site only collects and organizes open-source project information. No services are provided.",
    "explore.title": "Explore - NetTools Hub",
    "explore.description": "Browse and search {total}+ curated network tools across 6 themed groups. Filter by proxy, VPN, Clash, DNS, security tools and more.",
    "sidebar.all_projects": "All Projects",
    "sidebar.nav_label": "Category navigation",
    "stats.projects": "projects",
    "stats.categories": "categories",
    "stats.total_stars": "total stars",
    "search.placeholder": "Search projects, authors, tags...",
    "search.aria_label": "Search projects",
    "search.clear": "Clear search",
    "search.shortcut_hint": "Press / to search",
    "sort.aria_label": "Sort by",
    "sort.default": "Default",
    "sort.stars": "⭐ Stars",
    "sort.name": "🔤 Name",
    "sort.updated": "🕐 Updated",
    "list.found": "Found {count} projects",
    "list.results_count": "{count} results",
    "empty.title": "No projects to show",
    "empty.description": "Try removing the search keyword or selecting a different category.",
    "empty.clear": "Clear filters",
    "category.header": "{name}",
    "group.proxy": "Proxy Core",
    "group.accel": "Acceleration",
    "group.ops": "Deploy & Ops",
    "group.config": "Config & DNS",
    "group.tools": "Tools & Test",
    "group.security": "Security & More",
    "nav.categories": "Categories",
    "nav.home": "Home",
    "nav.explore": "Explore",
    "nav.menu": "Menu",
    "nav.close": "Close",
    "nav.show_header": "Show header",
    "nav.switch_language": "Switch language",
    "card.open_external": "Open on GitHub",
    "card.forks": "{count} forks",
    "card.license": "License: {name}",
    "nav.scroll_top": "Scroll back to top",
    "a11y.main": "Main content",
    "404.folio": "Folio 404",
    "404.description": "This category or page does not exist",
    "404.back": "← Back to Home",
    "error.description": "An unexpected error occurred. Please try again.",
    "error.retry": "Try Again",
    "error.explore_desc": "Something went wrong while loading the project list.",
    "error.explore_retry": "Retry",
    // Editorial atlas chrome (design-language strings, not page content).
    "editorial.eyebrow": "An Atlas of",
    "editorial.subtitle":
      "A curated compendium of {total}+ open-source network tools, organised into six thematic groups and indexed for daily reference.",
    "editorial.last_indexed": "Last indexed",
    "editorial.open_atlas": "Open the Atlas",
    "editorial.continue_reading": "Continue reading",
    "editorial.plate": "Plate {n}",
    "editorial.section.why": "Why this atlas",
    "editorial.section.groups": "The six groups",
    "editorial.section.begin": "Begin reading",
    "editorial.section.curated": "Curated entries",
    "editorial.colophon": "Colophon",
    "editorial.compiled_by": "Compiled by",
    "editorial.edition": "Edition I · {date}",
    "editorial.divider": "Folio {n} · {groups} groups · {cats} categories · {stars} cumulative stars",
    "editorial.summary": "{n} entries · {m} categories · indexed daily",
    "editorial.compendium": "— Compendium",
    "editorial.hero_title": "Network Tools",
    "editorial.hero_atlas": "An Atlas",
    "cta.title": "Ready to dive in?",
    "cta.description": "Every entry links to its source — start exploring the curated atlas.",
    "error.folio": "Folio — error",
    "error.explore_folio": "Folio — explore / error",
  },
  zh: {
    "site.title": "NetTools Hub",
    "features.title": "一览",
    "features.subtitle": "发现、搜索、筛选你需要的网络工具 — 一站式搞定",
    "features.curated": "{total}+ 个精选项目",
    "features.curated_desc": "涵盖代理核心、GUI 客户端、订阅管理、GitHub 加速、DNS 工具等 6 大主题分组",
    "features.search": "智能搜索",
    "features.search_desc": "按项目名称、作者、标签或描述搜索，快速找到你需要的工具",
    "features.sort": "多维排序",
    "features.sort_desc": "按星数、名称或更新时间排序，找到最热门和最新的项目",
    "features.responsive": "全端适配",
    "features.responsive_desc": "完美适配桌面端、平板和手机 — 随时随地浏览",
    "features.maintained": "持续维护",
    "features.maintained_desc": "仅收录活跃更新的项目，淘汰过时项目",
    "features.stars": "{stars}+ 总星数",
    "features.stars_desc": "高质量开源项目，拥有清晰的社区认可度",
    "categories.title": "按主题浏览",
    "categories.subtitle": "6 大主题分组覆盖网络工具全链路 — 点击进入任意分组深入探索",
    "footer.text": "NetTools Hub · 网络工具导航平台",
    "footer.disclaimer": "本网站仅收集整理开源项目信息，不提供任何服务。",
    "explore.title": "探索 - NetTools Hub",
    "explore.description": "浏览搜索 {total}+ 个精选网络工具,涵盖 6 大主题分组。按代理、VPN、Clash、DNS、安全工具等筛选。",
    "sidebar.all_projects": "全部项目",
    "sidebar.nav_label": "分类导航",
    "stats.projects": "个项目",
    "stats.categories": "个分类",
    "stats.total_stars": "总星数",
    "search.placeholder": "搜索项目、作者、标签...",
    "search.aria_label": "搜索项目",
    "search.clear": "清除搜索",
    "search.shortcut_hint": "按 / 搜索",
    "sort.aria_label": "排序方式",
    "sort.default": "默认",
    "sort.stars": "⭐ 星数",
    "sort.name": "🔤 名称",
    "sort.updated": "🕐 更新",
    "list.found": "找到 {count} 个项目",
    "list.results_count": "{count} 条结果",
    "empty.title": "没有可显示的项目",
    "empty.description": "尝试清除搜索关键词或选择其他分类。",
    "empty.clear": "清除筛选",
    "category.header": "{name}",
    "group.proxy": "代理核心",
    "group.accel": "网络加速",
    "group.ops": "部署与运维",
    "group.config": "配置与解析",
    "group.tools": "工具与测试",
    "group.security": "安全与汇总",
    "nav.categories": "分类",
    "nav.home": "首页",
    "nav.explore": "探索",
    "nav.menu": "菜单",
    "nav.close": "关闭",
    "nav.show_header": "显示顶栏",
    "nav.switch_language": "切换语言",
    "card.open_external": "在 GitHub 上打开",
    "card.forks": "{count} forks",
    "card.license": "许可证: {name}",
    "nav.scroll_top": "滚回顶部",
    "a11y.main": "主要内容",
    "404.folio": "第 404 卷",
    "404.description": "该分类或页面不存在",
    "404.back": "← 返回首页",
    "error.description": "发生了意外错误，请重试。",
    "error.retry": "重试",
    "error.explore_desc": "加载项目列表时出现问题。",
    "error.explore_retry": "重试",
    // Editorial atlas chrome.
    "editorial.eyebrow": "一本",
    "editorial.subtitle":
      "一本收录 {total}+ 个开源网络工具的图鉴，按六大主题分组整理，每日索引更新。",
    "editorial.last_indexed": "最近索引",
    "editorial.open_atlas": "打开图鉴",
    "editorial.continue_reading": "继续阅读",
    "editorial.plate": "第 {n} 章",
    "editorial.section.why": "为什么需要这本图鉴",
    "editorial.section.groups": "六大分组",
    "editorial.section.begin": "开始阅读",
    "editorial.section.curated": "精选条目",
    "editorial.colophon": "版权页",
    "editorial.compiled_by": "编纂",
    "editorial.edition": "第一版 · {date}",
    "editorial.divider": "第 {n} 卷 · {groups} 大主题 · {cats} 个分类 · 累计 {stars} 星",
    "editorial.summary": "{n} 个条目 · {m} 个分类 · 每日更新",
    "editorial.compendium": "— 概览",
    "editorial.hero_title": "网络工具",
    "editorial.hero_atlas": "图鉴",
    "cta.title": "准备好开始探索？",
    "cta.description": "每一条目都指向其源仓库 — 立即开启精选图鉴之旅。",
    "error.folio": "错误页",
    "error.explore_folio": "探索页错误",
  },
  ja: {
    "site.title": "NetTools Hub",
    "features.title": "本章について",
    "features.subtitle": "必要なネットワークツールを発見、検索、フィルタリング — すべて一箇所で",
    "features.curated": "{total}+ 厳選プロジェクト",
    "features.curated_desc": "プロキシコア、GUIクライアント、サブスクリプション管理、GitHub高速化、DNSツールなど6テーマグループをカバー",
    "features.search": "スマート検索",
    "features.search_desc": "プロジェクト名、作者、タグ、説明文で検索。すぐに必要なツールが見つかります",
    "features.sort": "多次元ソート",
    "features.sort_desc": "スター数、名前、更新日でソート。最も人気のプロジェクトを発見",
    "features.responsive": "全端末対応",
    "features.responsive_desc": "デスクトップ、タブレット、スマートフォンに完全対応",
    "features.maintained": "継続メンテナンス",
    "features.maintained_desc": "積極的に更新されているプロジェクトのみを収録",
    "features.stars": "{stars}+ 総スター数",
    "features.stars_desc": "高品質なオープンソースプロジェクト、コミュニティの認知度も明確",
    "categories.title": "テーマで探す",
    "categories.subtitle": "6テーマグループがネットワークツールチェーンを網羅 — 任意のグループをクリックして深掘り",
    "footer.text": "NetTools Hub · ネットワークツールナビゲーションプラットフォーム",
    "footer.disclaimer": "このサイトはオープンソースプロジェクト情報を収集整理するだけです。サービスは提供していません。",
    "explore.title": "探索 - NetTools Hub",
    "explore.description": "{total}+の厳選ネットワークツールを6テーマグループから閲覧・検索。プロキシ、VPN、Clash、DNS、セキュリティツールでフィルタリング。",
    "sidebar.all_projects": "全プロジェクト",
    "sidebar.nav_label": "カテゴリナビゲーション",
    "stats.projects": "プロジェクト",
    "stats.categories": "カテゴリ",
    "stats.total_stars": "総スター数",
    "search.placeholder": "プロジェクト、作者、タグを検索...",
    "search.aria_label": "プロジェクト検索",
    "search.clear": "検索をクリア",
    "search.shortcut_hint": "/ を押して検索",
    "sort.aria_label": "並び替え",
    "sort.default": "デフォルト",
    "sort.stars": "⭐ スター",
    "sort.name": "🔤 名前",
    "sort.updated": "🕐 更新",
    "list.found": "{count} 件のプロジェクトが見つかりました",
    "list.results_count": "{count} 件の結果",
    "empty.title": "表示できるプロジェクトがありません",
    "empty.description": "検索キーワードをクリアするか、別のカテゴリを選んでください。",
    "empty.clear": "フィルターをクリア",
    "category.header": "{name}",
    "group.proxy": "プロキシコア",
    "group.accel": "高速化",
    "group.ops": "デプロイと運用",
    "group.config": "設定とDNS",
    "group.tools": "ツールとテスト",
    "group.security": "セキュリティ他",
    "nav.categories": "カテゴリ",
    "nav.home": "ホーム",
    "nav.explore": "探索",
    "nav.menu": "メニュー",
    "nav.close": "閉じる",
    "nav.show_header": "ヘッダーを表示",
    "nav.switch_language": "言語を切り替え",
    "card.open_external": "GitHub で開く",
    "card.forks": "{count} forks",
    "card.license": "ライセンス: {name}",
    "nav.scroll_top": "ページの先頭へ戻る",
    "a11y.main": "メインコンテンツ",
    "404.folio": "第 404 巻",
    "404.description": "このカテゴリまたはページは存在しません",
    "404.back": "← ホームに戻る",
    "error.description": "予期せぬエラーが発生しました。もう一度お試しください。",
    "error.retry": "再試行",
    "error.explore_desc": "プロジェクト一覧の読み込み中にエラーが発生しました。",
    "error.explore_retry": "再試行",
    // Editorial atlas chrome.
    "editorial.eyebrow": "一巻の",
    "editorial.subtitle":
      "{total}+ のオープンソース・ネットワークツールを 6 つのテーマで編纂。毎日索引を更新。",
    "editorial.last_indexed": "最終索引",
    "editorial.open_atlas": "図鑑を開く",
    "editorial.continue_reading": "続きを読む",
    "editorial.plate": "第 {n} 章",
    "editorial.section.why": "本図鑑について",
    "editorial.section.groups": "六つのテーマ",
    "editorial.section.begin": "読み始める",
    "editorial.section.curated": "精選エントリ",
    "editorial.colophon": "奥付",
    "editorial.compiled_by": "編纂",
    "editorial.edition": "初版 · {date}",
    "editorial.divider": "第 {n} 巻 · {groups} テーマ · {cats} カテゴリ · 累計 {stars} スター",
    "editorial.summary": "{n} エントリ · {m} カテゴリ · 毎日更新",
    "editorial.compendium": "— 全書",
    "editorial.hero_title": "ネットワークツール",
    "editorial.hero_atlas": "図鑑",
    "cta.title": "探索を始めますか？",
    "cta.description": "各エントリはソースリポジトリへリンク — 精選図鑑を今すぐ開きましょう。",
    "error.folio": "エラー",
    "error.explore_folio": "探索エラー",
  },
};

export function t(
  lang: Lang,
  key: string,
  params?: Record<string, string | number>,
): string {
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
  { value: "en", label: "EN" },
  { value: "zh", label: "中文" },
  { value: "ja", label: "日本語" },
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
  return lang === "en" ? path : `${path}?lang=${lang}`;
}

/**
 * Like {@link langParam}, but safe to call on a path that already
 * carries a query string (e.g. `/explore?category=core`). The
 * `?lang=` is then appended with `&` so we never end up with the
 * `?category=core?lang=zh` double-question-mark bug that the static
 * sitemap hit and rolled back once already.
 */
export function withLang(lang: Lang, path: string): string {
  if (lang === "en") return path;
  return path.includes("?") ? `${path}&lang=${lang}` : `${path}?lang=${lang}`;
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
 * triplet in lockstep — there were three near-duplicate copies of
 * this 12-line function in `landing-content`, `explore-content`, and
 * the two `*error.tsx` files, and a previous pass had landed
 * `landing` and `explore` with subtly different URL-rewrite
 * implementations (one used `URLSearchParams`, one used a `URL`
 * object). This is the single source of truth now.
 */
export function setLangAndPersist(newLang: Lang): void {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  if (newLang === "en") url.searchParams.delete("lang");
  else url.searchParams.set("lang", newLang);
  window.history.replaceState({}, "", url.toString());
  try {
    window.localStorage.setItem(LANG_STORAGE_KEY, newLang);
  } catch {
    /* storage may be disabled */
  }
  window.dispatchEvent(
    new CustomEvent("nethub:langchange", { detail: { lang: newLang } }),
  );
}

/**
 * `localStorage` key for the user's preferred language. Kept as a
 * single constant so it's trivial to grep and rename.
 */
export const LANG_STORAGE_KEY = "nethub.lang";

/**
 * Resolve the initial client-side language using the same precedence
 * as `set-html-lang`:
 *   1. `?lang=` query string (deep link / canonical URL wins).
 *   2. `localStorage` (sticky user preference).
 *   3. `navigator.language` family match.
 *   4. English (the i18n fallback).
 *
 * Lives next to `setLangAndPersist` so the read-side and write-side
 * of the language switch share the same key name and the same
 * precedence — we had drifted before (one file only checked URL,
 * one only checked storage, one only checked navigator) and a user
 * landing on `/?lang=zh` with no storage set would see English for
 * a frame.
 */
export function resolveInitialLang(): Lang {
  if (typeof window === "undefined") return "en";
  const fromUrl = readLangFromUrl();
  if (fromUrl) return fromUrl;
  try {
    const stored = window.localStorage.getItem(LANG_STORAGE_KEY);
    if (stored === "en" || stored === "zh" || stored === "ja") return stored;
  } catch {
    /* storage may be disabled */
  }
  if (typeof navigator !== "undefined") {
    const lang = navigator.language.toLowerCase();
    if (lang.startsWith("zh")) return "zh";
    if (lang.startsWith("ja")) return "ja";
  }
  return "en";
}

/**
 * BCP-47 tags for each language. Used to drive `<html lang>`,
 * `<link rel="alternate" hreflang>` and the OpenGraph `locale` field.
 * Keeping them next to the `Lang` union makes it impossible to ship
 * a translation in a new language without also declaring its locale.
 */
export const LANG_HTML_LANG: Record<Lang, string> = {
  en: "en",
  zh: "zh-Hans",
  ja: "ja",
};

export const LANG_OG_LOCALE: Record<Lang, string> = {
  en: "en_US",
  zh: "zh_CN",
  ja: "ja_JP",
};

/**
 * Read the current language from the URL `?lang=` query parameter.
 *
 * Safe to call on the server (returns `"en"`) and on the client
 * (returns the URL value when valid, otherwise `"en"`).
 *
 * Why this lives in the i18n module: the same `output: "export"`
 * static-page constraint means every page that wants to honour
 * `?lang=` must read the URL client-side. Duplicating the parse
 * logic in each component (LandingContent, ExploreContent, the
 * error pages, the not-found page) is brittle — a single source of
 * truth keeps the fallback rules aligned.
 */
export function readLangFromUrl(): Lang {
  if (typeof window === "undefined") return "en";
  try {
    const url = new URL(window.location.href);
    const v = url.searchParams.get("lang");
    if (v === "en" || v === "zh" || v === "ja") return v;
  } catch {
    /* ignore: invalid URL or restricted env */
  }
  return "en";
}