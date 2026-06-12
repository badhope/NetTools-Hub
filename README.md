# NetTools Hub

> **⚠️ Read first — [DISCLAIMER.md](./DISCLAIMER.md)**
> This site is a personal link index. It does not host, distribute,
> endorse, or operate any of the linked software. Inclusion is **not**
> an endorsement. Use at your own risk.

A field manual of 210 actively-maintained, open-source network tools
— proxies, VPN cores, DNS servers, GitHub accelerators, monitoring
agents, security utilities — organised by **kind** and by
**platform**, navigable by URL path (no infinite scroll, no JS
state).

```
/                                ← landing
/explore                         ← all 210, sorted
/explore/k/proxy                 ← kind drill-down (8 kinds)
/explore/k/proxy/p/desktop       ← kind + platform (6 platforms)
```

The site is a single pre-rendered static bundle. **No backend, no
database, no tracking, no ads, no analytics.** Hosted on **GitHub
Pages**. The data is one JSON file
([`data/projects.json`](./data/projects.json)). The metadata is
auto-refreshed weekly by a GitHub Action.

> See also: 🇬🇧 [`README.md`](./README.md) (you are here) ·
> 🇨🇳 [`README.zh.md`](./README.zh.md) · 🇯🇵 [`README.ja.md`](./README.ja.md)

---

## What is this?

Every time I re-install a system, I find myself re-asking the same
questions on GitHub: *which Clash core is still alive, how does
sing-box differ from Xray, is there a lighter V2Ray implementation,
what's the cleanest WireGuard UI*. This site is my personal cheat
sheet, made public.

It is **not** a VPN service. It is **not** a proxy provider. It is
**not** a hosting platform for any of the listed tools. It is a
**link index** — every entry is a real `<a href>` to a real GitHub
repo. See [DISCLAIMER.md](./DISCLAIMER.md).

---

## The 8 kinds × 6 platforms

The directory is built on two orthogonal taxonomies, which become
the URL hierarchy:

| `kind` (URL: `/explore/k/<kind>/`) | count | `platform` (URL: `.../p/<platform>/`) | count |
|---|---:|---|---:|
| `proxy` — proxy cores & clients | 78 | `desktop` | 102 |
| `vpn` — VPN servers & clients | 19 | `mobile` | 56 |
| `dns` — recursive, authoritative, filtering | 18 | `cli` | 81 |
| `acceleration` — GitHub acceleration, mirror tools, tunnels | 31 | `server` | 134 |
| `security` — WAF, IDS, IPS, honeypots | 21 | `browser` | 38 |
| `monitoring` — uptime, metrics, observability | 14 | `router` | 23 |
| `ops` — deploy, orchestration, management | 12 | | |
| `tools` — utility scripts, port scanners, debuggers | 17 | | |

A project can be tagged with multiple `platform` values (e.g. a
proxy might be both `desktop` and `cli`); the URL hierarchy is
driven by them, so every (kind, platform) pair is its own static
page. `generateStaticParams` is wired into both dynamic routes, so
the build emits 1 + 8 + 8 × 6 = 57 pre-rendered pages.

---

## Quick start

### As a user (just want to find a tool)

1. Open the live site → **<https://badhope.github.io/NetTools-Hub/>**
2. **Drill down by URL**:
   - `/explore` — all 210
   - `/explore/k/proxy` — every proxy
   - `/explore/k/proxy/p/desktop` — desktop-only proxies
3. **Or use the tree sidebar** on the left of every `/explore` page
   (kinds on level 1, platforms on level 2 under each kind).
4. **Click a row** to jump to the project's GitHub repo.

The site is responsive (desktop, tablet, mobile). The language
switcher is in the top-right; switch any time — the URL gains
`?lang=zh` or `?lang=ja`.

### As a contributor

```bash
git clone https://github.com/badhope/NetTools-Hub.git
cd NetTools-Hub
pnpm install --frozen-lockfile   # Node 22+ & pnpm 10+
pnpm dev                          # http://localhost:8080
```

To build the static site locally:

```bash
pnpm build        # produces ./out (static export)
pnpm start        # serve the build at http://localhost:8080
```

To validate the data before pushing:

```bash
pnpm run validate # runs scripts/validate-projects.mjs (CI also runs this)
```

To refresh project metadata from the GitHub API (uses
`GITHUB_TOKEN` if set, otherwise anonymous):

```bash
pnpm run refresh
```

To mine new candidates from `awesome-*` lists:

```bash
pnpm run scan     # writes data/candidates.json for review
```

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full guide.

### As a maintainer (fork & deploy)

This repo ships with a ready-to-use **GitHub Actions** workflow. After
forking:

1. **Settings → Pages → Source** = **GitHub Actions**
2. Push to `main` — `.github/workflows/deploy.yml` builds and deploys.
3. (Optional) Edit `basePath` in [`next.config.ts`](./next.config.ts)
   if you renamed the repo.

Your fork is live at
`https://<your-username>.github.io/NetTools-Hub/`. See
[`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md) for full instructions.

---

## Features

- **URL-path navigation** — `/explore/k/<kind>/p/<platform>/`, no
  infinite scroll, no client-side state, deep links just work
- **Tree sidebar** — kinds on level 1, platforms on level 2, active
  node highlighted, collapses on mobile
- **Pre-rendered** — every page is static HTML; the `out/` bundle is
  one `pnpm build` away
- **Trilingual UI** — English / 中文 / 日本語, swap with the
  top-right language switcher or `?lang=` query
- **PWA** — installable, offline-friendly, with a manifest and
  proper `<html lang>` and OG card
- **SEO-ready** — `robots.txt`, `sitemap.xml`, JSON-LD, `hreflang`
  alternates, OpenGraph, Twitter Card
- **Auto-refreshed** — a weekly GitHub Action updates stars / forks
  / license / last commit, with `status: archived` derived from
  no-commit-in-2-years
- **Validated** — every PR is checked by
  `scripts/validate-projects.mjs` in a separate CI job
- **Field-manual design** — cool near-black palette, hairline
  rules, IBM Plex Sans + Mono, monospace numerics, no shadows, no
  rounded cards
- **MIT-licensed** — fork, modify, redeploy

---

## Project structure

```
NetTools-Hub/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   │   ├── deploy.yml          # GitHub Pages auto-deploy
│   │   ├── refresh-projects.yml # weekly metadata refresh
│   │   └── ci.yml              # lint + typecheck + validate
│   ├── CODEOWNERS
│   ├── FUNDING.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── data/
│   ├── projects.json           # 210 projects × (kind + platform)  ← source of truth
│   └── candidates.json         # generated by `pnpm run scan`
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
│   ├── validate-projects.mjs   # schema validator (CI)
│   ├── refresh-projects.mjs    # weekly GitHub API refresh
│   ├── scan-awesome.mjs        # awesome-* candidate miner
│   ├── migrate-schema.mjs      # one-shot v1 → v2
│   ├── add-batch.mjs           # hand-curated add-on (legacy)
│   ├── build-og-image.py       # regenerates og-image.png + icons
│   ├── smoke.py                # Playwright smoke test (manual)
│   ├── snap.py                 # Playwright page screenshots (manual)
│   └── pageshot.py             # Playwright deployment check (manual)
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # root layout, fonts, metadata, OG
│   │   ├── page.tsx            # landing page
│   │   ├── globals.css         # Tailwind v4 + field-manual theme
│   │   ├── not-found.tsx
│   │   ├── error.tsx
│   │   ├── explore/            # /explore, /explore/k/<kind>/, /explore/k/<kind>/p/<platform>/
│   │   ├── robots.ts
│   │   └── sitemap.ts
│   ├── components/             # top-nav, tree-sidebar, project-table, …
│   ├── lib/                    # i18n, taxonomy, projects, site
│   └── types/
│       └── project.ts          # schema v2 type definitions
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .npmrc
├── .nvmrc                      # node 22
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── DISCLAIMER.md               # full legal text
├── LICENSE                     # MIT
├── README.md                   # you are here (English)
├── README.zh.md                # 简体中文
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

## Tech stack

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
| Type | **IBM Plex Sans + Mono** | Cool, engineering feel; numerals tabular |

---

## Adding or editing a project

The content is a single JSON file. The schema is documented in full
at [`docs/DATA-MODEL.md`](./docs/DATA-MODEL.md); the TypeScript
type lives in [`src/types/project.ts`](./src/types/project.ts). A
minimal entry:

```json
{
  "id": "sing-box",
  "name": "sing-box",
  "kind": "proxy",
  "platform": ["desktop", "cli", "server"],
  "category": "proxy-core",
  "description": "Universal proxy platform",
  "url": "https://github.com/SagerNet/sing-box",
  "language": "Go",
  "license": "MIT",
  "addedAt": "2024-04-01",
  "verdict": "best-in-class"
}
```

Inclusion criteria: active commits within the last 6 months,
OSI-approved license, real-world use case. See
[`CONTRIBUTING.md`](./CONTRIBUTING.md).

> The `stars`, `forks`, `lastCommit` and `status` fields are
> **regenerated** by `scripts/refresh-projects.mjs` on Sundays — you
> do not have to maintain them by hand.

---

## The automation pipeline

| Trigger | Script | Output |
|---|---|---|
| Cron (Sun 03:00 UTC) | `scripts/refresh-projects.mjs` | Updates `stars` / `forks` / `license` / `lastCommit` / `status`; auto-commits if dirty |
| Manual `workflow_dispatch` | same | same |
| Push to `data/projects.json` | same (via `paths:` filter) | same |
| `pnpm run scan` (local) | `scripts/scan-awesome.mjs` | Writes `data/candidates.json` for maintainer review |
| `pnpm run validate` (CI) | `scripts/validate-projects.mjs` | Exits 0/1/2; fails the PR if validation fails |

The refresh workflow uses `git diff --exit-code` to decide whether
to commit. Partial GitHub API failures on a single project are
logged and skipped, so a 404 on one repo cannot poison the whole
run.

---

## Internationalisation (i18n)

| Language | Code | UI | Docs |
|---|---|---|---|
| 🇬🇧 English (default) | `en` | ✅ | [`README.md`](./README.md) |
| 🇨🇳 简体中文 | `zh` | ✅ | [`README.zh.md`](./README.zh.md) |
| 🇯🇵 日本語 | `ja` | ✅ | [`README.ja.md`](./README.ja.md) |

UI strings live in [`src/lib/i18n.ts`](./src/lib/i18n.ts) (a
3-column table of ~36 keys). The current language is read from
`?lang=` URL param, with `localStorage` as a sticky preference.
See [`docs/I18N.md`](./docs/I18N.md) for how to add a new language.

---

## Contributing

PRs welcome. See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for:

- Local dev setup & scripts
- The data schema and how to add a project
- Code style, lint, and **Conventional Commits** (`feat:`, `fix:`, `docs:`, …)
- PR review process
- How to add or improve a translation

By participating, you agree to follow the
[Code of Conduct](./CODE_OF_CONDUCT.md).

---

## Security

Found a vulnerability? **Do not open a public Issue.** Follow the
private disclosure process in [`SECURITY.md`](./SECURITY.md) — we aim
to acknowledge within **3 business days**.

---

## License

Distributed under the [MIT License](./LICENSE).

---

> NetTools Hub · A field manual of 210 open-source network tools ·
> English · [简体中文](README.zh.md) · [日本語](README.ja.md)
