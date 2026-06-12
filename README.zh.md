# NetTools Hub · 网络工具集线

> **⚠️ 请先阅读 [DISCLAIMER.md](./DISCLAIMER.md)**
> 本仓库是一个**纯链接索引** —— 不托管、不分发、不背书、不运营
> 任何被链接的软件。被收录**不构成背书**。使用风险自担。

一本**收录 210 个活跃维护的开源网络工具**的“现场手册”：代理、VPN
核心、DNS 服务器、GitHub 加速、监控代理、安全工具 —— 按 **kind（种类）**
和 **platform（运行平台）** 两维分类，**用 URL 路径下钻**（没有无限
滚动，没有前端状态机）。

```
/                                ← 首页
/explore                         ← 全部 210 项，按 kind → stars 排序
/explore/k/proxy                 ← 按 kind 下钻（8 个 kind）
/explore/k/proxy/p/desktop       ← 按 kind + platform 进一步下钻（6 个 platform）
```

整个站点是一个**预渲染的静态包**：无后端、无数据库、无追踪、无广告、
无统计。托管在 **GitHub Pages**。数据集中在一个 JSON 文件
([`data/projects.json`](./data/projects.json))，元数据由 GitHub Action
**每周自动刷新**。

> 相关文档：[🇬🇧 `README.md`](./README.md) · 🇨🇳 `README.zh.md`（你在这里）·
> [🇯🇵 `README.ja.md`](./README.ja.md)

---

## 这是什么？

每次重装系统，我都会跑去 GitHub 重新翻一遍：*哪个 Clash 内核还活着、
sing-box 和 Xray 哪个更轻、有没有更轻量的 V2Ray 实现、WireGuard 哪
个 UI 最干净*。这个站点是我自己的备忘，顺便公开了。

它**不是** VPN 服务，**不是** 代理提供方，**不是** 任何被收录工具
的托管平台。它就是一个**链接索引** —— 每条记录都是一个真实的
`<a href>` 指向真实的 GitHub 仓库。请阅读
[DISCLAIMER.md](./DISCLAIMER.md)。

---

## 8 大 kind × 6 大 platform

整个目录建立在两个**正交**的分类轴上 —— 它们直接决定 URL 层次：

| `kind`（URL: `/explore/k/<kind>/`） | 数量 | `platform`（URL: `.../p/<platform>/`） | 数量 |
|---|---:|---|---:|
| `proxy` 代理核心与客户端 | 78 | `desktop` | 102 |
| `vpn` VPN 服务端与客户端 | 19 | `mobile` | 56 |
| `dns` 递归、权威、过滤 | 18 | `cli` | 81 |
| `acceleration` GitHub 加速、镜像、隧道 | 31 | `server` | 134 |
| `security` WAF、IDS、IPS、蜜罐 | 21 | `browser` | 38 |
| `monitoring` 监控、指标、可观测 | 14 | `router` | 23 |
| `ops` 部署、编排、管理 | 12 | | |
| `tools` 实用脚本、端口扫描、调试 | 17 | | |

一个项目可以打多个 `platform` 标签（比如一个代理同时支持 `desktop`
和 `cli`）。URL 层次就是这两个维度的笛卡尔积，所以每一对
`(kind, platform)` 都是一个独立的静态页面。两个动态路由都接入了
`generateStaticParams`，构建产物一共 1 + 8 + 8 × 6 = **57 个预渲染
页面**。

---

## 快速开始

### 普通用户

1. 打开 **<https://badhope.github.io/NetTools-Hub/>**
2. **通过 URL 下钻**：
   - `/explore` —— 全部 210 项
   - `/explore/k/proxy` —— 所有代理
   - `/explore/k/proxy/p/desktop` —— 仅桌面端代理
3. **或用左侧树形侧边栏**：第一层是 kind，第二层是 platform。
4. **点击行**跳转到项目的 GitHub 仓库。

响应式设计（桌面、平板、手机）。右上角的语言切换器随时切换
**英文 / 中文 / 日文** —— URL 会追加 `?lang=zh` 或 `?lang=ja`。

### 贡献者

```bash
git clone https://github.com/badhope/NetTools-Hub.git
cd NetTools-Hub
pnpm install --frozen-lockfile   # Node 22+ & pnpm 10+
pnpm dev                          # http://localhost:8080
```

构建静态站点：

```bash
pnpm build        # 输出到 ./out（静态导出）
pnpm start        # 本地预览 http://localhost:8080
```

提交前自检数据：

```bash
pnpm run validate # 跑 scripts/validate-projects.mjs（CI 也会跑）
```

刷新项目的 GitHub 元数据（用 `GITHUB_TOKEN` 提频，无则匿名）：

```bash
pnpm run refresh
```

从 `awesome-*` 列表中挖新候选：

```bash
pnpm run scan     # 写到 data/candidates.json 等你审
```

完整流程见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

### 维护者（Fork & 部署）

仓库自带可用的 **GitHub Actions** 工作流。Fork 后：

1. **Settings → Pages → Source** 选 **GitHub Actions**
2. 推送到 `main` —— `.github/workflows/deploy.yml` 自动构建部署。
3. （可选）如果改了仓库名，记得改 [`next.config.ts`](./next.config.ts) 里的 `basePath`。

你的 fork 会部署到
`https://<用户名>.github.io/NetTools-Hub/`。完整步骤见
[`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md)。

---

## 特性

- **URL 路径导航** —— `/explore/k/<kind>/p/<platform>/`，没有无限
  滚动、没有前端状态机，深链直接可用
- **树形侧边栏** —— 第一层是 kind，第二层是 platform，移动端自动折叠
- **预渲染** —— 每一页都是静态 HTML；`out/` 包是 `pnpm build` 一次
  生成
- **三语 UI** —— English / 中文 / 日本語，运行时切换（或 `?lang=` 查询）
- **PWA** —— 可安装、有 manifest、正确的 `<html lang>` 与 OG 卡
- **SEO 完善** —— `robots.txt`、`sitemap.xml`、JSON-LD、`hreflang`、
  OpenGraph、Twitter Card
- **元数据自动刷新** —— 每周日 GitHub Action 更新 stars / forks /
  license / 最近 commit，从 “两年无 commit” 推导 `status: archived`
- **数据校验** —— 每个 PR 都会被
  `scripts/validate-projects.mjs` 在独立 CI 任务里扫一遍
- **现场手册设计** —— 冷调近黑配色、发丝线规、IBM Plex Sans + Mono、
  等宽数字、零阴影、零圆角
- **MIT 协议** —— 想 fork、改、再部署，随意

---

## 项目结构

```
NetTools-Hub/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   │   ├── deploy.yml          # GitHub Pages 自动部署
│   │   ├── refresh-projects.yml # 每周元数据刷新
│   │   └── ci.yml              # lint + typecheck + validate
│   ├── CODEOWNERS
│   ├── FUNDING.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── data/
│   ├── projects.json           # 210 个项目 × (kind + platform) ← 数据源
│   └── candidates.json         # 由 pnpm run scan 生成
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA-MODEL.md
│   ├── DEPLOYMENT.md
│   ├── I18N.md
│   ├── I18N.zh.md
│   └── I18N.ja.md
├── public/
│   ├── icon-192.png
│   ├── icon-512.png
│   ├── manifest.webmanifest
│   ├── og-image.png
│   └── robots.txt
├── scripts/
│   ├── validate-projects.mjs   # schema 校验（CI 跑）
│   ├── refresh-projects.mjs    # 每周 GitHub API 刷新
│   ├── scan-awesome.mjs        # awesome-* 候选挖掘
│   ├── migrate-schema.mjs      # v1 → v2 一次性迁移
│   ├── add-batch.mjs           # 手工补录（历史遗留）
│   ├── build-og-image.py       # 重新生成 og-image.png + 图标
│   ├── smoke.py                # Playwright 烟囱测试（手工）
│   ├── snap.py                 # Playwright 页面截图（手工）
│   └── pageshot.py             # Playwright 部署后检查（手工）
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # 根布局、字体、metadata、OG
│   │   ├── page.tsx            # 首页
│   │   ├── globals.css         # Tailwind v4 + 现场手册主题
│   │   ├── not-found.tsx
│   │   ├── error.tsx
│   │   ├── explore/            # /explore, /explore/k/<kind>/, /explore/k/<kind>/p/<platform>/
│   │   ├── robots.ts
│   │   └── sitemap.ts
│   ├── components/             # top-nav, tree-sidebar, project-table, …
│   ├── lib/                    # i18n, taxonomy, projects, site
│   └── types/
│       └── project.ts          # schema v2 类型定义
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .npmrc
├── .nvmrc                      # node 22
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── DISCLAIMER.md               # 完整免责声明（必读）
├── LICENSE                     # MIT
├── README.md                   # 英文（默认）
├── README.zh.md                # 你正在看这个
├── README.ja.md                # 日本語
├── SECURITY.md
├── eslint.config.mjs
├── next.config.ts              # output: "export" + basePath
├── package.json
├── pnpm-lock.yaml
├── postcss.config.mjs
└── tsconfig.json
```

---

## 技术栈

| 层级 | 选型 | 理由 |
|---|---|---|
| 框架 | **Next.js 16**（App Router） | 静态导出、RSC、文件路由 |
| UI | **React 19** | 最新稳定版 |
| 样式 | **Tailwind CSS v4** | `@import "tailwindcss"` + `@theme` 令牌 |
| 语言 | **TypeScript 5.9** | strict 模式 |
| 包管理 | **pnpm 10** | 快速、节省磁盘 |
| 托管 | **GitHub Pages** | 免费、CDN 快、无供应商锁定 |
| CI/CD | **GitHub Actions** | `actions/checkout@v4` + `pnpm/action-setup@v4` + `actions/deploy-pages@v4` |
| i18n | 手写三语对照表 | 零 JS bundle、运行时切换 |
| 字体 | **IBM Plex Sans + Mono** | 冷调、理性；等宽数字 |

---

## 添加 / 编辑项目

内容集中在一个 JSON 文件。完整 schema 见
[`docs/DATA-MODEL.md`](./docs/DATA-MODEL.md)，TypeScript 类型在
[`src/types/project.ts`](./src/types/project.ts)。一个最小条目：

```json
{
  "id": "sing-box",
  "name": "sing-box",
  "kind": "proxy",
  "platform": ["desktop", "cli", "server"],
  "category": "proxy-core",
  "description": "通用代理平台",
  "url": "https://github.com/SagerNet/sing-box",
  "language": "Go",
  "license": "MIT",
  "addedAt": "2024-04-01",
  "verdict": "best-in-class"
}
```

收录标准：近 6 个月有活跃 commit、OSI 认可的开源协议、有真实使用
场景。详见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

> `stars`、`forks`、`lastCommit`、`status` 这几个字段由
> `scripts/refresh-projects.mjs` 每周日**自动重新生成**，不需要手填。

---

## 自动化管线

| 触发 | 脚本 | 输出 |
|---|---|---|
| 定时任务（周日 03:00 UTC） | `scripts/refresh-projects.mjs` | 更新 `stars` / `forks` / `license` / `lastCommit` / `status`；有差异自动提交 |
| 手动 `workflow_dispatch` | 同上 | 同上 |
| `data/projects.json` 有 push | 同上（按 `paths:` 过滤） | 同上 |
| `pnpm run scan`（本地） | `scripts/scan-awesome.mjs` | 写 `data/candidates.json` 供维护者审阅 |
| `pnpm run validate`（CI） | `scripts/validate-projects.mjs` | 退出码 0/1/2；不通过则 PR 失败 |

刷新工作流用 `git diff --exit-code` 判断是否需要提交。单个项目调用
GitHub API 失败会被记日志并跳过，所以一个 404 不会拖垮整轮刷新。

---

## 国际化 (i18n)

| 语言 | 代码 | UI | 文档 |
|---|---|---|---|
| 🇬🇧 English（默认） | `en` | ✅ | [`README.md`](./README.md) |
| 🇨🇳 简体中文 | `zh` | ✅ | [`README.zh.md`](./README.zh.md) |
| 🇯🇵 日本語 | `ja` | ✅ | [`README.ja.md`](./README.ja.md) |

UI 字符串集中在 [`src/lib/i18n.ts`](./src/lib/i18n.ts)（一张约 36
键的三列表）。当前语言从 `?lang=` URL 参数读，并以 `localStorage`
作为粘性偏好。详见 [`docs/I18N.md`](./docs/I18N.md)。

---

## 贡献

欢迎 PR。完整流程见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)：

- 本地开发环境与脚本
- 数据 schema 与如何添加项目
- 代码风格、lint、**Conventional Commits**（`feat:`、`fix:`、`docs:`、…）
- PR 审核流程
- 如何添加或改进翻译

参与即视为同意遵守 [行为准则](./CODE_OF_CONDUCT.md)。

---

## 安全

发现漏洞？**请勿公开 Issue**。按 [`SECURITY.md`](./SECURITY.md)
私下披露，我们承诺在 **3 个工作日内**响应。

---

## 许可证

基于 [MIT 许可证](./LICENSE) 发布。

---

> NetTools Hub · 210 个开源网络工具的现场手册 · [English](README.md) ·
> 简体中文（你在这里）· [日本語](README.ja.md)
