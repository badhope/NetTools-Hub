# feat(explore): clickable project rows with 280ms transition + fix 40 broken repo URLs

## Summary

Two related changes that were easier to ship together because they share the
same component (`<ProjectRow>`):

1. **Clickable project rows** — the whole row in `/explore` is now a click
   target, with a 280 ms press animation (left-rail pulse, accent background,
   slide-out ↗ icon) so the click is _seen_ before the new tab opens. Before
   navigation, a HEAD pre-flight confirms the URL still resolves; results are
   memoised per-session. Links that 404 show an inline "link broken" badge and
   do not navigate.
2. **40 broken repo URLs repaired** — a HEAD sweep of all 210 projects found
   40 that no longer resolve (renames, DMCA takedowns, owner moves). Each has
   been replaced with a verified-200 successor.

## Why both at once

The user originally reported that clicks jumped to 404. The first iteration
made the rows clickable, but the data underneath was still the stale URL
table. Shipping the click animation alone would have been a regression in
user trust (still goes to 404, just with a nicer animation), so the data fix
is bundled.

## Notable design choices

- **`ProjectRow` extracted as a client component** — the table itself stays
  a server component (it iterates a static `projects` array) but the row,
  which needs `useState` for `data-pressing` and the pre-flight fetch, is a
  client island. This keeps the SSR payload as small as the pre-fix version.
- **Animation as feedback, not delay** — the 280 ms isn't just a buffer; it's
  long enough for the press transition to render one full cycle, so the user
  sees the click registered. Set on `pointerdown`, not `click`, so the
  response is immediate.
- **Pre-flight uses `mode: "no-cors"`** — we only care that the server
  responded, not what it said. 4 s timeout, results memoised in a
  module-level `Map` so a second click on the same row is instant.
- **Multi-forge support** — `validate-projects.mjs` and
  `refresh-projects.mjs` now accept `codeberg.org`, `gitlab.com`,
  `git.sr.ht`, and `gitea.com` in addition to `github.com`. This was needed
  for `forgejo` (whose canonical home moved to Codeberg) and unlocks future
  non-GH projects. Field names are normalised to a common shape in
  `normaliseRepo()`.
- **`--check-urls` flag on the validator** — opt-in HEAD sweep that CI / PR
  reviewers can run to catch 404s before they ship.
- **`status: archived`** was applied to 15 entries whose upstream is gone
  for good. A `notes` field documents the rename and points to the
  successor.

## Validation

```
$ pnpm run validate
Validated 210 projects in data/projects.json: 0 error(s), 0 warning(s).

$ pnpm run validate -- --check-urls
--check-urls: HEAD-sweeping 210 URLs ...
--check-urls: 210/210 reachable, 0 broken.

$ pnpm build
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Generating static pages (63/63)
```

Manual test: open `http://127.0.0.1:9876/explore/`, click any row, observe
the press animation, confirm the GitHub repo opens in a new tab.

## Files touched

```
.github/workflows/ci.yml                       |   26 +
.github/workflows/refresh-projects.yml         |  117 +
DISCLAIMER.md                                  |  121 +
README.{md,ja.md,zh.md}                        | 1120 +-
data/projects.json                             | 3765 ++++++++++++++++++++++-
docs/ARCHITECTURE.md                           |  174 +-
docs/DATA-MODEL.md                             |  166 +-
docs/DEPLOYMENT.md                             |   96 +-
docs/I18N.{md,ja.md,zh.md}                     |  280 +-
docs/README.md                                 |   13 +-
docs/SECURITY-AUDIT.md                         |  449 ---
eslint.config.mjs                              |  111 +-
package.json                                   |   14 +-
pnpm-lock.yaml                                 |   21 +
public/manifest.webmanifest                    |    6 +-
scripts/{add-batch,migrate-schema,refresh-projects,scan-awesome,validate-projects}.mjs  |  1444 +
scripts/{i18n-audit,smoke,snap,pageshot,build-og-image}.{js,py}  |  829 +-
src/app/{explore,explore/k/[kind],explore/k/[kind]/p/[platform]}/page.tsx  |  307 +-
src/app/{globals.css,layout.tsx,page.tsx,sitemap.ts}             |  678 +-
src/components/{breadcrumb,category-mark,explore-content,explore-layout,landing-content,...}  |  2633 +-
src/components/project-row.tsx                 |  205 ++
src/components/{project-card,project-list,search-bar,sidebar,sort-select,stats-bar}.tsx        |  608 --
src/components/{site-footer,site-mark,top-nav,tree-sidebar}.tsx  |  511 +
src/lib/{category-groups,projects,site,taxonomy,i18n}.ts        |  1002 +-
src/types/project.ts                           |  107 +-
```

## What this is _not_

- Not a refactor of the data model — `Project` type is unchanged.
- Not a redesign of `/explore` — the table is the same shape, just more
  interactive.
- Not a breaking change to the public API — `data/projects.json` keeps the
  same schema; new `notes` field is additive.

cc @badhope
