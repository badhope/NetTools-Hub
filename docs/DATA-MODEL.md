# Data Model

`data/projects.json` is the **single source of truth** for the directory. This document describes its schema in depth.

> 🇬🇧 English (default) — additional translations planned; the schema is JSON keys + TypeScript types, so English serves most readers.

---

## 1. Top-level shape

```ts
// The top-level shape of data/projects.json.
type ProjectsFile = {
  lastUpdated: string;                       // ISO-8601 date (e.g. "2026-06-01")
  schemaVersion: string;                     // SemVer of the data shape itself
                                             // (independent of the app version in
                                             // package.json — they are unrelated
                                             // concepts and only intentionally synced
                                             // at release time). Bump on any change
                                             // to the JSON shape (added/renamed/
                                             // removed fields) so future
                                             // data-validation tooling can migrate.
  categories: Record<string, Category>;     // keyed by Category.id
  projects: Project[];                       // already includes the slug
                                             // field used for routing
};
```

## 2. The `Category` type

```ts
type Category = {
  id: string;              // matches the key in `categories` (e.g. "proxy-core")
  name: string;            // human-readable English name (e.g. "Proxy Core")
  icon: string;            // a single emoji
  description?: string;    // 1-line description for tooltips
  group: GroupId;          // which of the 6 themed groups it belongs to
  order?: number;          // display order within its group
};
```

The 6 valid `GroupId` values are:

| `group` | English name | Icon |
|---|---|---|
| `proxy` | Proxy Core | 🔌 |
| `accel` | Acceleration | 🚀 |
| `ops` | Deploy & Ops | 🐳 |
| `config` | Config & DNS | ⚙️ |
| `tools` | Tools & Test | 🧰 |
| `security` | Security & More | 🛡️ |

## 3. The `Project` type

```ts
type Project = {
  id: string;              // unique slug, lower-kebab (e.g. "sing-box")
  name: string;            // display name
  description: string;     // 1-line description (≤ 140 chars)
  url: string;             // canonical URL (usually the GitHub repo)
  homepage?: string;       // optional homepage (often the docs)
  category: string;        // foreign key into `categories` (e.g. "proxy-core")
  tags: string[];          // 0–5 lowercase tokens (e.g. ["proxy", "ss"])
  language: string;        // primary language ("Go", "Rust", …)
  stars: number;           // GitHub stars at the time of curation
  lastUpdate: string;      // ISO-8601 date of the most recent commit
  license: string;         // SPDX identifier ("MIT", "Apache-2.0", …)
  author?: string;         // GitHub username
  featured?: boolean;      // if true, appears on the landing page
};
```

### 3.1 Field rules

| Field | Rule |
|---|---|
| `id` | Lower-kebab, must be globally unique. Try `<tool-name>` first. |
| `name` | Match the project's own name exactly (case-sensitive where it matters). |
| `description` | ≤ 140 chars. Plain text, no markdown. |
| `url` | Must be HTTPS. GitHub repos preferred. |
| `category` | Must match an `id` in `categories`. |
| `tags` | 0–5 items. Lowercase, single-word or hyphenated. No #hashtags. |
| `language` | The single most-used language. Approximations OK ("Shell" for bash scripts). |
| `stars` | A snapshot. Update on re-curation. |
| `lastUpdate` | The date of the most recent commit, NOT release. Format `YYYY-MM-DD`. |
| `license` | An [SPDX identifier](https://spdx.org/licenses/). |
| `author` | GitHub username without `@`. Required for display in the card. |
| `featured` | `true` only for the 3–6 most popular / canonical tools in a category. |

## 4. Validation

The CI runs `pnpm build` which TypeScript-checks the entire `data/projects.json` against `src/types/project.ts`. If a field is missing or wrong, the build fails and the PR cannot merge.

## 5. Local helper scripts

None — the data is small enough to edit by hand. A future improvement may add a `pnpm validate-data` script.
