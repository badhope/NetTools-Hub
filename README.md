# 🛠️ NetTools Hub

> **一个我自己用的网络工具导航站**。收录了 120+ 还在活跃维护的
> 开源网络工具 —— 代理、VPN、Clash 系列、GitHub 加速、DNS、安全、监控。
> 不托管任何东西,只做跳转。

起因是每次我重新装系统,都要重新去 GitHub 翻一遍"现在 Clash 哪个
仓库还活着、Sing-box 比 Xray 好在哪、有没有更轻的 V2Ray 实现"。
这个站是我给自己做的备忘,顺便公开了。

---

## 收录的类别

- **代理协议**:Clash / Mihomo / Sing-box / V2Ray / Xray / Shadowsocks / Hysteria / TUIC
- **VPN**:WireGuard / OpenVPN / IPSec / 算法实现
- **DNS**:CoreDNS / SmartDNS / AdGuardHome / mosdns
- **GitHub 加速**:各种镜像、raw 加速、clone 加速
- **安全**:WAF / IDS / IPS / 蜜罐
- **监控**:Smokeping / Prometheus exporters / Uptime Kuma
- **辅助**:Hosts 编辑器 / 端口扫描 / 路由跟踪

每条都有:仓库地址、license、最近一次 release 时间、是否还在维护。

## i18n

- [English](README.md) · [简体中文](README.zh.md) · [日本語](README.ja.md)

界面是 i18n 的,但**每条收录说明都是中文写的** —— 因为我
只懂中文。翻译需要从社区收集,贡献指南在 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 🎯 What is NetTools Hub?

**NetTools Hub** is a **static navigation website** that helps you discover and compare actively-maintained open-source network tools. All data lives in a single JSON file ([`data/projects.json`](./data/projects.json)) and the site is automatically built and deployed to **GitHub Pages** — no backend, no database, no tracking, no ads.

| 💡 What it is | ❌ What it is NOT |
|---|---|
| A curated **directory** of network tool projects | Not a VPN service or proxy provider |
| A **searchable catalog** with filters and sorting | Not a hosting platform for the listed tools |
| A **static site** built with Next.js + React | Not a SaaS / paid product |
| **100% free & open source** under MIT | Not a content scraper (data is hand-curated) |
| **Internationalised UI** (EN / 中文 / 日本語) | Not limited to a single language or region |

---

## 🚀 Quick start

### 👤 As a user (just want to find a tool)

1. **Open the live site** 👉 <https://badhope.github.io/NetTools-Hub/>
2. **Browse or search** — pick a themed group from the sidebar (e.g. *Proxy Core*, *Acceleration*, *Deploy & Ops*), then refine by sub-category, or type keywords into the search bar (search by name, author, tag, or description).
3. **Click a card** to jump to the project's GitHub repo and read the docs.

The site is fully responsive and works on **desktop / tablet / mobile**. A language switcher (top right) lets you toggle between **English / 中文 / 日本語** at any time.

### 🛠️ As a developer / contributor (want to run or modify it)

```bash
git clone https://github.com/badhope/NetTools-Hub.git
cd NetTools-Hub
pnpm install --frozen-lockfile   # requires Node 22+ & pnpm 10+
pnpm dev                          # http://localhost:8080
```

To build the static site locally:

```bash
pnpm build        # produces ./out (static export)
pnpm start        # serve the build at http://localhost:8080
```

Then read [`CONTRIBUTING.md`](./CONTRIBUTING.md) for how to add a project, propose a fix, or submit a PR.

### 🚢 As a maintainer (want to fork & deploy your own)

This repo ships with a ready-to-use **GitHub Actions** workflow. After forking:

1. Go to **Settings → Pages**
2. Set **Source** to **GitHub Actions**
3. Push to `main` — `.github/workflows/deploy.yml` will build and deploy automatically.

Your fork will be live at `https://<your-username>.github.io/NetTools-Hub/`.

---

## ✨ Features

- 🔍 **Smart search** — match by name, author, tag, or description (debounced 300 ms)
- 📊 **Multi-dimensional sort** — by ⭐ stars, name, or last update
- 🗂 **6 themed groups / 21 sub-categories** — Proxy Core, Acceleration, Deploy & Ops, Config & DNS, Tools & Test, Security & More
- 🌐 **Trilingual UI** — English / 中文 / 日本語 (switchable at runtime)
- 📱 **Fully responsive** — desktop, tablet, mobile (collapsible sidebar, hamburger drawer)
- ⚡ **Static export** — light-speed load from GitHub Pages CDN
- 🔒 **SEO ready** — `robots.txt`, `sitemap.xml`, OpenGraph, Twitter Card
- ♿ **Accessible** — ARIA labels, `focus-visible`, keyboard navigation
- 🎯 **Curated quality** — only projects active in the last 6 months
- 🌓 **Dark theme** by default, GitHub-style design tokens

---

## 📸 Preview

🌐 **Live demo**: <https://badhope.github.io/NetTools-Hub/>

The site has two main views:

- **`/`** — **Landing page** — hero, feature highlights, 6 themed-group cards, call-to-action
- **`/explore`** — **Browse & search** — sidebar with 6 themed groups (collapsible), real-time search, sort dropdown, project grid

---

## 🗂 Project structure

```
NetTools-Hub/
├── .github/
│   ├── ISSUE_TEMPLATE/         # Bug report, feature request, translation
│   ├── workflows/
│   │   └── deploy.yml          # GitHub Pages auto-deploy
│   ├── CODEOWNERS
│   ├── FUNDING.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── data/
│   └── projects.json           # 124 projects × 21 sub-categories (6 themed groups) (the source of truth)
├── docs/                       # Additional documentation
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout (metadata, fonts)
│   │   ├── page.tsx            # Landing page
│   │   ├── globals.css         # Tailwind v4 + custom theme tokens
│   │   ├── robots.ts           # /robots.txt
│   │   ├── sitemap.ts          # /sitemap.xml
│   │   ├── not-found.tsx       # 404
│   │   ├── error.tsx           # Global error boundary
│   │   └── explore/            # /explore — browse & search
│   ├── components/             # UI: sidebar, cards, search, sort, language switcher…
│   ├── lib/                    # i18n tables, data access, utils
│   └── types/                  # TypeScript types
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .npmrc                      # pnpm@10
├── .nvmrc                      # node 22
├── CHANGELOG.md                # All notable changes
├── CODE_OF_CONDUCT.md          # Contributor Covenant v2.1
├── CONTRIBUTING.md             # Full contributor guide
├── LICENSE                     # MIT
├── README.md                   # You are here (English)
├── README.zh.md                # 简体中文
├── README.ja.md                # 日本語
├── SECURITY.md                 # Vulnerability disclosure policy
├── eslint.config.mjs
├── next.config.ts              # output: "export" (static)
├── package.json
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
├── postcss.config.mjs          # Tailwind v4
└── tsconfig.json
```

---

## 🛠 Tech stack

| Layer | Choice | Why |
|---|---|---|
| Framework | **Next.js 16** (App Router) | Static export, RSC, file-based routing |
| UI | **React 19** | Latest stable |
| Styling | **Tailwind CSS v4** | `@import "tailwindcss"` + `@theme` tokens |
| Language | **TypeScript 5.9** | Strict mode |
| Package manager | **pnpm 10** | Fast, disk-efficient |
| Hosting | **GitHub Pages** | Free, fast CDN, no vendor lock-in |
| CI/CD | **GitHub Actions** | `actions/checkout@v4` + `pnpm/action-setup@v4` + `actions/deploy-pages@v4` |
| i18n | Hand-rolled trilingual table | Zero JS bundle overhead, runtime switch |

---

## ➕ Adding or editing a project

All content is in a **single JSON file** — no CMS, no migration scripts.

1. Open [`data/projects.json`](./data/projects.json).
2. Add or edit an entry following this schema (also typed in [`src/types/project.ts`](./src/types/project.ts)):

   ```json
   {
     "id": "sing-box",
     "name": "sing-box",
     "description": "Universal proxy platform…",
     "url": "https://github.com/SagerNet/sing-box",
     "category": "proxy-core",
     "tags": ["proxy", "shadowsocks", "trojan"],
     "language": "Go",
     "stars": 25000,
     "lastUpdate": "2026-05-30",
     "license": "MIT"
   }
   ```

3. Open a PR. The CI will deploy a preview on the next push to `main`.

> ✅ Inclusion criteria: active commits within the last 6 months, OSI-approved license, and a real-world use case. See the [contributing guide](./CONTRIBUTING.md) for the full guide.

---

## 📑 The 6 themed groups (21 sub-categories)

| Group | Icon | Sub-categories |
|---|---|---|
| **Proxy Core** | 🔌 | Proxy Cores · GUI Clients · Subscription Management · Protocol Tools |
| **Acceleration** | 🚀 | GitHub Acceleration · Router Plugins · Mirror Acceleration · Tunnel Tools |
| **Deploy & Ops** | 🐳 | Docker Deployment · Container Orchestration · Server Management · Node Tools · Monitoring |
| **Config & DNS** | ⚙️ | Rule Collections · DNS Tools · Certificate Tools |
| **Tools & Test** | 🧰 | Utilities · Network Testing · Data Transfer |
| **Security & More** | 🛡️ | Security Tools · Project Collections |

---

## 🌍 Internationalisation (i18n)

The site UI and this repository's documentation are available in three languages:

| Language | Code | UI translation | Docs |
|---|---|---|---|
| 🇬🇧 English (default) | `en` | ✅ | [`README.md`](./README.md) |
| 🇨🇳 简体中文 | `zh` | ✅ | [`README.zh.md`](./README.zh.md) |
| 🇯🇵 日本語 | `ja` | ✅ | [`README.ja.md`](./README.ja.md) |

To **add a new translation** or **improve an existing one**, please open a PR — see [`CONTRIBUTING.md` → "Adding or improving translations"](./CONTRIBUTING.md#-adding-or-improving-translations).

---

## 🤝 Contributing

We welcome PRs! See the contributing guide for:

- Local dev setup & scripts
- The data schema and how to add a project
- Code style, lint, and **Conventional Commits** (`feat:`, `fix:`, `docs:`, …)
- PR review process
- How to add or improve a translation

**Contributing guide:** [🇬🇧 English](CONTRIBUTING.md) · [🇨🇳 简体中文](CONTRIBUTING.zh.md) · [🇯🇵 日本語](CONTRIBUTING.ja.md)

By participating, you agree to follow the [Code of Conduct](./CODE_OF_CONDUCT.md).

## 🔐 Security

Found a vulnerability? **Do not open a public Issue.** Follow the private disclosure process in [`SECURITY.md`](./SECURITY.md) — we aim to acknowledge within **3 business days**.

## 💬 Support & community

Need help or have questions? See [`SUPPORT.md`](./.github/SUPPORT.md) for the recommended channels.

## 📄 License

Distributed under the [MIT License](./LICENSE).

---

## ⭐ Star history

If this project helped you discover a useful tool, consider giving it a star — it helps others find it too.

[![Star History Chart](https://api.star-history.com/svg?repos=badhope/NetTools-Hub&type=Date)](https://star-history.com/#badhope/NetTools-Hub&Date)

---

<div align="center">

Made with ❤️ · **NetTools Hub** · 🛠️ One-stop navigation for the open-source network-tools ecosystem · **English** · [简体中文](README.zh.md) · [日本語](README.ja.md)

</div>
