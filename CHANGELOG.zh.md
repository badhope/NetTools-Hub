# 变更日志

**NetTools Hub** 所有值得注意的变更都记录在本文件中。

本文件格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/spec/v2.0.0.html) 规范。

> 🇨🇳 简体中文 · 🇬🇧 [English](./CHANGELOG.md) · 🇯🇵 [日本語](./CHANGELOG.ja.md)

---

## [未发布]

### 计划中

- 搜索历史与已保存搜索（基于浏览器 localStorage）
- 模糊搜索"你是不是想找…"建议
- 新增项目的 RSS / Atom 订阅
- 各语言独立 CHANGELOG（已与 i18n 同步计划）

---

## [0.3.0] – 2026-06-02

### 变更（UI 细节打磨 - 第三轮）

- **顶栏精简**：移除重复的 `Categories` 下拉菜单，只保留最右边的 hamburger 抽屉。explore 页面移除 `← Home` 边框按钮。主 CTA 在 landing 是 `Explore`，在 explore 是 `Home`。
- **语言切换器重写**：3 个内联按钮（EN/中文/日本語）→ 单个 Globe 图标 + 下拉菜单（点击外部关闭）。移动端抽屉底部也提供语言切换器，方便在抽屉内直接切换。
- **侧边栏瘦身**：`w-64` (256 px) → `w-[232px]`。移除底部那一行单薄的 footer 文字。
- **首页**：原本"21 个专业分类"网格改为 **6 大主题分组卡片**（代理核心 · 网络加速 · 部署与运维 · 配置与解析 · 工具与测试 · 安全与汇总），每个分组内列出其下子分类。卡片 padding 由 p-6 升到 p-7。section 文案改为"Browse by Group / 按主题浏览"。
- **首页 footer**：logo + 站点名 + tagline + 免责信息，间距更合理。
- **i18n**：英文 / 中文 / 日文同步按新的 6 分组心智模型更新（"21 个分类" → "6 大主题分组"）。

---

## [0.2.0] – 2026-06-02

### 新增

- **顶栏组件** (`src/components/top-nav.tsx`)，landing 和 explore 共享。
- **分组定义** (`src/lib/category-groups.ts`)：6 个逻辑集群，合计 21 个子分类。
- 新增 i18n 键 `group.*` 与 `nav.*`（en / zh / ja 三语）。
- 顶栏**多级下拉菜单**：桌面悬停，移动端 hamburger 抽屉；支持点击外部关闭、ARIA 标签。

### 变更

- **项目列表** 按分组集群重新组织，区块间距加大。
- **项目卡片**：p-6 padding、2 个标签 + `+N` 溢出指示、左侧渐变边条、移除冗余 forks、`line-clamp` 限制标题/描述、底部分隔线分隔 meta 区。

---

## [0.1.1] – 2026-06-02

### 修复

- `next.config.ts`：启用 `trailingSlash: true`，使 Next.js 生成 `explore/index.html` 而非 `explore.html`，子路径路由在 GitHub Pages 上正常生效。
- CSS 资源在 `/NetTools-Hub/_next/...` 下正确解析。

---

## [0.1.0] – 2026-06-01

### 新增

- 首次公开发布。
- 120+ 个精选网络工具，覆盖 21 个分类，全部存放在 `data/projects.json`。
- 首页（hero、特性、分类网格、行动召唤、footer）。
- 探索页（侧边栏、搜索、排序下拉、项目网格）。
- 三语 UI：英文 / 中文 / 日文。
- 完全响应式（桌面、平板、手机）。
- `sitemap.xml` 与 `robots.txt`。
- GitHub Actions 自动部署到 GitHub Pages。
- 深色主题，GitHub 风格设计令牌。
- MIT 许可证。

---

[未发布]: https://github.com/badhope/NetTools-Hub/compare/d835693...HEAD
[0.3.0]: https://github.com/badhope/NetTools-Hub/compare/31dc5d0...d835693
[0.2.0]: https://github.com/badhope/NetTools-Hub/compare/6de3ca2...31dc5d0
[0.1.1]: https://github.com/badhope/NetTools-Hub/compare/f7e258b...6de3ca2
[0.1.0]: https://github.com/badhope/NetTools-Hub/releases/tag/3c58bc5
