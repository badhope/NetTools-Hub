# Architecture

A short tour of how the codebase is wired together.

## 1. High-level flow

```
data/projects.json
        │
        ▼
 scripts/validate-projects.mjs   ← CI gate; idempotent
 scripts/refresh-projects.mjs    ← scheduled (weekly, via GitHub Actions)
 scripts/scan-awesome.mjs        ← optional candidate miner
        │
        ▼
 src/lib/projects.ts             ← pre-computed indexes (Map / frozen arrays)
        │
        ▼
 src/lib/taxonomy.ts             ← human-readable labels (en / zh / ja)
 src/lib/i18n.ts                 ← UI string table
        │
        ▼
 src/components/*.tsx            ← pure UI; takes props
        │
        ▼
 src/app/explore/k/[kind]/p/[platform]/page.tsx   ← static export
 src/app/explore/k/[kind]/page.tsx
 src/app/explore/page.tsx
 src/app/page.tsx
        │
        ▼
 next build (output: "export", generateStaticParams for k×p)
        │
        ▼
 out/                            ← static HTML + /NetTools-Hub/_next/*
        │
        ▼
 GitHub Pages
```

The whole site is a single pre-rendered bundle. There is **no
server runtime**, no auth, no database, no API. Every page is
HTML on disk before a request ever arrives.

## 2. URL tree

The exploration surface is a strict 2-level hierarchy derived from
the two orthogonal taxonomies on each project:

| Path | Filter |
|---|---|
| `/explore` | no filter (all 210) |
| `/explore/k/<kind>` | one of `proxy / vpn / dns / acceleration / security / monitoring / ops / tools` |
| `/explore/k/<kind>/p/<platform>` | kind + one of `desktop / mobile / cli / server / browser / router` |

`generateStaticParams` is wired into both dynamic pages, so the
build emits a complete set of static HTML:

- 8 kind pages
- 8 × 6 = 48 kind+platform pages
- 1 root page
- 1 sitemap.xml
- 1 manifest.webmanifest
- 1 robots.txt
- 3 landing variants (en / zh / ja, via the `?lang=` query)

Static export + `trailingSlash: true` = every page has a real
`.html` counterpart and a directory index, which is what GitHub
Pages needs.

The URL is the navigation state. There is no `?category=` query,
no client-side router, no infinite scroll, no facet panel. The
sidebar is a tree of real `<a href="…">` links; the back/forward
buttons work; deep links are stable URLs.

## 3. i18n

- All UI strings live in **`src/lib/i18n.ts`** as a 3-column table
  (`en` / `zh` / `ja`) of ~36 keys, plus a `taxonomy.ts` table
  for the kind/platform labels.
- The current language is read from `?lang=` URL param at runtime,
  with `localStorage` as a sticky preference and `navigator.language`
  as the final fallback. The first render is always English (to
  match the static prerender and avoid a React 19 #418 hydration
  mismatch); the real language swaps in on the first effect tick
  via `useClientLang`.
- The `t(lang, key, params?)` function supports `{var}` interpolation.
- The English variant of every URL is the canonical one (no query);
  the other two languages opt in via `?lang=`. The `<link rel="alternate">`
  block in the layout and the sitemap both reflect this.

## 4. Data model

`data/projects.json` is the **single source of truth**. The
schema is versioned (`schemaVersion: 2`); see
[`DATA-MODEL.md`](./DATA-MODEL.md) for the field-by-field
reference.

The two orthogonal taxonomies are:

- **`kind`** — the *what* (proxy / VPN / DNS / acceleration / …).
  Single-valued, drives the first URL segment.
- **`platform`** — the *where* (desktop / mobile / CLI / server /
  browser / router). Multi-valued, drives the second URL segment.

A `category` string is kept as a flat third axis (the editorial
sub-bucket) for the human-friendly grouping in the project table
and the JSON-LD payload; it does not affect the URL.

## 5. Why a static export?

- **Free hosting** via GitHub Pages.
- **CDN-friendly** — every page is pre-rendered HTML.
- **No backend to maintain** — nothing to hack, no database to
  back up, no rate-limit footguns.
- **Trivial to fork** — change the `homepage` and re-deploy.
- **Schema v2 + schemaVersion field** means a future migration
  can be cut over without breaking existing forks.

## 6. Why Tailwind v4?

- **Zero CSS bundle** for unused classes (via
  `@tailwindcss/postcss`).
- **Design tokens** live in `src/app/globals.css` as a single
  `@theme { … }` block — easy to keep the "field manual" palette
  consistent.
- No runtime CSS-in-JS cost.

The design system is documented inline in `src/app/globals.css`
at the top of the file (no separate design-system.md to drift).

## 7. Why no React state library?

The site has zero global state beyond the current `?lang=` URL
param. We use `useState` for purely local UI (mobile-drawer open
flag, language-switcher listbox highlight, etc.). The data layer
is module-level frozen arrays — see `src/lib/projects.ts`.

## 8. Automation pipeline

| Trigger | Script | What it does |
|---|---|---|
| Cron (Sun 03:00 UTC) | `scripts/refresh-projects.mjs` | Hits the GitHub REST API for every project, updates `stars` / `forks` / `license` / `lastCommit`, derives `status` from `lastCommit`, auto-commits & pushes if the file is dirty |
| Manual (`workflow_dispatch`) | `scripts/refresh-projects.mjs` | Same as above, on demand |
| Push to `data/projects.json` | `scripts/refresh-projects.mjs` | Same as above, fires within minutes to clean up new entries |
| `pnpm run scan` | `scripts/scan-awesome.mjs` | Mines 7 hand-picked `awesome-*` repos and emits `data/candidates.json` for the maintainer to review |
| `pnpm run validate` | `scripts/validate-projects.mjs` | Pure-Node schema validator; runs in CI as a separate `validate-data` job; idempotent, exit 0/1/2 |

The refresh workflow uses `git diff --exit-code` to decide whether
to commit; partial GitHub API failures on a single project are
logged and skipped (the project's existing fields are kept
untouched), so a single 404 cannot poison the whole run.

## 9. Folder layout

| Path | Purpose |
|---|---|
| `src/app/` | Next.js App Router pages: `/`, `/explore`, `/explore/k/[kind]`, `/explore/k/[kind]/p/[platform]`, `/not-found`, `/error`, `/explore/error`, `/robots.ts`, `/sitemap.ts` |
| `src/components/` | Reusable UI: `top-nav`, `tree-sidebar`, `project-table`, `explore-layout`, `landing-content`, `breadcrumb`, `language-switcher`, `set-html-lang`, `site-footer`, `site-mark` |
| `src/lib/` | Pure modules: `projects.ts` (data access + frozen indexes), `i18n.ts` (trilingual table), `taxonomy.ts` (kind/platform label table), `site.ts` (identity constants), `utils.ts`, `use-client-lang.ts` |
| `src/types/` | TypeScript types: `project.ts` (the single source of truth for the data shape) |
| `data/projects.json` | 210 curated projects (the content) |
| `public/` | Static assets: `favicon.ico`, `og-image.png`, `icon-192/512.png`, `manifest.webmanifest` |
| `scripts/` | Node + Python utilities: `validate-projects.mjs`, `refresh-projects.mjs`, `scan-awesome.mjs`, `migrate-schema.mjs`, `add-batch.mjs`, plus optional `smoke.py` / `snap.py` / `pageshot.py` (require `playwright`) |
| `docs/` | User-facing documentation |

## 10. Disclaimer placement

The disclaimer is surfaced in **three** places, all kept in sync:

1. The repo root: [`DISCLAIMER.md`](../DISCLAIMER.md) — the full
   legal text, ~150 lines, 8 sections.
2. The three top-level READMEs ([`README.md`](../README.md),
   [`README.zh.md`](../README.zh.md),
   [`README.ja.md`](../README.ja.md)) — a 3-line excerpt at the
   very top with a "read first" callout.
3. The site footer ([`src/components/site-footer.tsx`](../src/components/site-footer.tsx))
   — one paragraph that points back to the full text.

The footer disclaimer is a **server component** (no client JS
needed), uses a left border + `kicker` label so it is visually
unmissable, and lives above the site metadata (not buried at
the bottom of the page).
