# Changelog

All notable changes to **NetTools Hub** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> 🇬🇧 English (default) · 🇨🇳 [简体中文](./CHANGELOG.zh.md) · 🇯🇵 [日本語](./CHANGELOG.ja.md)

---

## [Unreleased]

### Planned
- Search history & saved searches (per-browser localStorage)
- "Did you mean…?" fuzzy search suggestions
- RSS / Atom feed for new project additions
- Per-language CHANGELOG (zh/ja) so the file is not English-only

### Added
- **Release Drafter** workflow: auto-drafts the next GitHub Release from Conventional Commits
- **CITATION.cff**: enables GitHub's "Cite this repository" button
- **Issue template** improvements: `question.yml` now nudges Q&A to Discussions; `config.yml` adds direct Q&A / Ideas / Security links
- Git tag `v0.3.0` is the new baseline for future release drafts

---

## [0.3.0] – 2026-06-02

### Changed (UI — round 3 polish)
- **Top nav** slimmed: removed the duplicate `Categories` dropdown — only the rightmost hamburger drawer remains. Removed the `← Home` border button on the explore page. Primary CTA is now `Explore` on the landing page and `Home` on the explore page.
- **Language switcher** rewritten: 3 inline buttons (EN/中文/日本語) → a single Globe icon with a click-outside-closing dropdown. The mobile drawer also exposes the switcher at the bottom for in-drawer language switching.
- **Sidebar** slimmed: `w-64` (256 px) → `w-[232px]`. Removed the lonely single-line footer text at the bottom.
- **Landing page**: the "21 Professional Categories" grid is replaced by **6 themed-group cards** (Proxy Core · Acceleration · Deploy & Ops · Config & DNS · Tools & Test · Security & More), each listing its sub-categories. Cards get more padding (p-6 → p-7). Section copy refreshed to "Browse by Group".
- **Landing footer**: logo + title + tagline + disclaimer, properly spaced.
- **i18n**: aligned en/zh/ja strings with the new group-based mental model (e.g. "21 categories" → "6 themed groups").

---

## [0.2.0] – 2026-06-02

### Added
- **Top nav component** (`src/components/top-nav.tsx`) shared between landing and explore.
- **Category groups** (`src/lib/category-groups.ts`): 6 logical clusters, 21 sub-categories total.
- New i18n keys `group.*` and `nav.*` across en / zh / ja.
- **Multi-level dropdown** in the top nav: hover on desktop, hamburger sheet on mobile, with click-outside dismissal and ARIA labels.

### Changed
- **Project list** re-grouped by category cluster with large section spacing.
- **Project card**: `p-6` padding, 2 tags + `+N` overflow indicator, colour-coded left border, dropped redundant meta (forks), `line-clamp` on title/description, meta row separated by border.
- **Sidebar**: 21 categories grouped into 6 logical clusters, each collapsible; cleaner hierarchy with breathing room.

---

## [0.1.1] – 2026-06-02

### Fixed
- `next.config.ts`: enable `trailingSlash: true` so Next.js emits `explore/index.html` instead of `explore.html`, making sub-path routing work on GitHub Pages.
- CSS assets resolved at `/NetTools-Hub/_next/...` correctly.

---

## [0.1.0] – 2026-06-01

### Added
- Initial public release.
- 120+ curated network tools across 21 categories in `data/projects.json`.
- Landing page (hero, features, category grid, call-to-action, footer).
- Explore page (sidebar, search bar, sort dropdown, project grid).
- Trilingual UI: English / 中文 / 日本語.
- Responsive layout (desktop, tablet, mobile).
- `sitemap.xml` & `robots.txt`.
- GitHub Actions auto-deploy to GitHub Pages.
- Dark theme with GitHub-style design tokens.
- MIT License.

---

[Unreleased]: https://github.com/badhope/NetTools-Hub/compare/d835693...HEAD
[0.3.0]: https://github.com/badhope/NetTools-Hub/compare/31dc5d0...d835693
[0.2.0]: https://github.com/badhope/NetTools-Hub/compare/6de3ca2...31dc5d0
[0.1.1]: https://github.com/badhope/NetTools-Hub/compare/f7e258b...6de3ca2
[0.1.0]: https://github.com/badhope/NetTools-Hub/releases/tag/3c58bc5
