# Data Model

`data/projects.json` is the **single source of truth** for the directory. This document describes its schema in depth.

> 🇬🇧 English (default) — additional translations planned; the schema is JSON keys + TypeScript types, so English serves most readers.

---

## 1. Top-level shape

```ts
// The top-level shape of data/projects.json (schema v2).
type ProjectsFile = {
  lastUpdated: string; // ISO-8601 timestamp; bumped on
  // every write by refresh-projects.mjs
  schemaVersion: number; // Bumped on breaking changes
  categories: Record<string, Category>; // editorial metadata, keyed by
  // Category.id (legacy field; the
  // `kind` / `platform` axes are now
  // the primary classification)
  projects: Project[]; // the actual entries
};
```

## 2. The `Category` type

```ts
type Category = {
  name: string; // human-readable name, e.g. "GUI clients"
  description: string; // 1-line description
  color: string[]; // two colours, kept for forward-compat
  // (the new design no longer paints them,
  // but the field stays so existing data
  // does not need a migration for it)
};
```

Categories are a _flat_ enumeration (a third classification axis on
top of `kind` and `platform`); they survive the v1 → v2 schema change
unchanged because they represent a different concern — editorial
bucketing (GUI clients vs CLI tools vs subscription managers), not
the _what_ or the _where_.

## 3. The `Project` type

```ts
type Project = {
  // -- Identity -----------------------------------------------------------
  id: string; // unique slug, lowercase kebab/snake (e.g. "sing-box")
  name: string; // display name (matches the upstream repo)
  author: string; // GitHub username, no leading "@"
  description: string; // 1-line description (≤ 140 chars)
  url: string; // canonical GitHub URL
  homepage?: string; // optional docs / project homepage

  // -- Metrics (refreshed by scripts/refresh-projects.mjs) ----------------
  stars: number; // GitHub stars
  forks: number; // GitHub forks
  language: string; // primary language ("Go", "Rust", …)
  license: string; // SPDX identifier ("MIT", "Apache-2.0", …)

  // -- Taxonomies ---------------------------------------------------------
  kind: ProjectKind; // the "what" — drives the first path segment
  platform: ProjectPlatform[]; // the "where" — drives the second segment
  category: string; // foreign key into `categories` (e.g. "gui")
  tags: string[]; // 0-8 lowercase tokens

  // -- Editorial ----------------------------------------------------------
  notes?: string; // 1-2 sentence personal take (optional)
  verdict?: ProjectVerdict; // recommended | neutral | caution | avoid

  // -- Lifecycle ----------------------------------------------------------
  lastCommit: string; // ISO-8601 date of the most recent commit
  addedAt: string; // ISO-8601 date the entry was first added
  status: ProjectStatus; // active | stale | archived (derived)
};
```

### 3.1 Field rules

| Field         | Rule                                                                |
| ------------- | ------------------------------------------------------------------- |
| `id`          | Lowercase, URL-safe (`a-z`, `0-9`, `-`, `_`). Must be unique.       |
| `name`        | Match the upstream repo's own name.                                 |
| `description` | ≤ 140 chars, plain text, no markdown.                               |
| `url`         | HTTPS, GitHub preferred.                                            |
| `kind`        | One of 8 values (see below).                                        |
| `platform`    | Non-empty array; each entry is one of 6 values (see below).         |
| `category`    | Foreign key into the top-level `categories` object.                 |
| `tags`        | 0-8 items. Lowercase, single-word or hyphenated.                    |
| `language`    | The most-used language. "Shell" for bash scripts.                   |
| `license`     | An [SPDX identifier](https://spdx.org/licenses/).                   |
| `lastCommit`  | Date of the most recent commit (NOT release). `YYYY-MM-DD`.         |
| `addedAt`     | Date first added to the index. `YYYY-MM-DD`.                        |
| `status`      | `active` (lastCommit < 180d), `stale` (180d-2y), `archived` (> 2y). |
| `verdict`     | Editorial sign-off, optional but encouraged.                        |
| `notes`       | Free text, optional.                                                |

### 3.2 Allowed enum values

**`kind`** (8 values, drives `/explore/k/<kind>/`):

| Slug           | English             | 中文       | 日本語         |
| -------------- | ------------------- | ---------- | -------------- |
| `proxy`        | Proxy cores         | 代理核心   | プロキシコア   |
| `vpn`          | VPN                 | VPN        | VPN            |
| `dns`          | DNS                 | DNS        | DNS            |
| `acceleration` | Acceleration        | 网络加速   | 高速化         |
| `security`     | Security            | 安全       | セキュリティ   |
| `monitoring`   | Monitoring          | 监控       | 監視           |
| `ops`          | Deploy & operations | 部署与运维 | デプロイと運用 |
| `tools`        | Tools & utilities   | 工具与杂项 | ツールと雑多   |

**`platform`** (6 values, drives `/explore/k/<kind>/p/<platform>/`):

| Slug      | English | 中文   | 日本語         |
| --------- | ------- | ------ | -------------- |
| `desktop` | Desktop | 桌面端 | デスクトップ   |
| `mobile`  | Mobile  | 手机端 | モバイル       |
| `cli`     | CLI     | 命令行 | コマンドライン |
| `server`  | Server  | 服务端 | サーバー       |
| `browser` | Browser | 浏览器 | ブラウザ       |
| `router`  | Router  | 路由器 | ルーター       |

## 4. Validation

The CI runs `pnpm run validate` (script: [`scripts/validate-projects.mjs`](../scripts/validate-projects.mjs)) on every PR. The validator enforces:

- required fields are present and of the right type;
- `id` is unique and URL-safe;
- `kind` and `platform` are in the allowed enums;
- `url` is a `github.com` URL;
- `lastCommit` and `addedAt` are valid ISO-8601 dates;
- `category` references an existing entry in `categories`;
- `(kind, platform[0], category, id)` is unique — protects the
  URL tree from accidental duplicate drill-down paths;
- a warning (non-fatal) is emitted when the manually-set `status`
  disagrees with the formula `active < 180d < stale < 2y < archived`.

## 5. The automation pipeline

Three scripts in `scripts/`, all runnable locally and from CI:

| Script                  | What it does                                                                                                                   | When it runs                                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| `validate-projects.mjs` | Schema validator (no I/O, no network)                                                                                          | every PR, every push                                             |
| `refresh-projects.mjs`  | Calls the GitHub API, refreshes `stars` / `forks` / `license` / `lastCommit`, derives `status`, writes the file back           | weekly Sun 03:00 UTC, plus every push that touches the data file |
| `scan-awesome.mjs`      | Mines a hand-picked list of `awesome-*` repos, extracts GitHub URLs, emits `data/candidates.json` for the maintainer to review | on demand (`pnpm run scan`)                                      |

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the broader picture.
