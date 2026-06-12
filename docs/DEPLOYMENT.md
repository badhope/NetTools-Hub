# Deployment · 部署 · デプロイ

Forking and deploying your own instance of **NetTools Hub** takes about 5 minutes.

> 🇬🇧 English (default) — additional translations planned; the content is short, visual, and largely code-driven, so English serves most readers.

---

## 1. Prerequisites

- A **GitHub** account.
- **Node 22+** and **pnpm 10+** installed locally (only needed if
  you want to test the build).

---

## 2. Fork

Click **Fork** in the top-right of the repository page. GitHub creates a copy under your account:

```
https://github.com/<your-username>/NetTools-Hub
```

---

## 3. Configure the basePath (only if you change the repo name)

By default, the site is built to be served at:

```
https://<your-username>.github.io/NetTools-Hub/
```

This is set by `basePath: "/NetTools-Hub"` in [`next.config.ts`](../next.config.ts). If you **rename** your repo, you must update this value. For example, if you rename to `proxy-hub`:

```ts
// next.config.ts
const nextConfig: NextConfig = {
  output: 'export',
  basePath: '/proxy-hub', // ← match your new repo name
  trailingSlash: true,
  images: { unoptimized: true },
};
```

Then update the `homepage` in [`package.json`](../package.json):

```json
"homepage": "https://<your-username>.github.io/proxy-hub"
```

> 💡 Want to deploy to **your own domain** instead? See Section 5 below.

---

## 4. Enable GitHub Pages

In your fork:

1. Go to **Settings → Pages**
2. **Source**: **GitHub Actions**
3. Save

That's it. The next push to `main` (or the Actions tab on this very fork) will trigger `.github/workflows/deploy.yml`, which:

1. Sets up Node 22 + pnpm 10
2. Installs deps with `pnpm install --frozen-lockfile`
3. Audits production dependencies (`pnpm audit --prod --audit-level=high`)
4. Builds with `next build` (static export, ~63 pre-rendered pages)
5. Uploads the artifact
6. Deploys via `actions/deploy-pages@v4`

Your site will be live at `https://<your-username>.github.io/NetTools-Hub/` within a couple of minutes.

---

## 5. Custom domain

1. In your fork, create a file `public/CNAME` with your domain:

   ```
   proxy.example.com
   ```

2. In your DNS provider, add a CNAME record:

   ```
   proxy.example.com  →  <your-username>.github.io.
   ```

3. In **Settings → Pages → Custom domain**, enter `proxy.example.com` and wait for the green check.

4. (Optional) Enable **Enforce HTTPS** in the same page once the certificate is provisioned.

---

## 6. Customising the data

The entire directory is one file: [`data/projects.json`](../data/projects.json)
(210 curated projects, schema v2). See
[`docs/DATA-MODEL.md`](./DATA-MODEL.md) for the field-by-field
reference.

- To **add** a project, append an entry to the `projects` array.
  The kinds and platforms are closed enums; stick to the allowed
  values.
- To **remove** a project, delete its entry.
- To **edit** a project, change any field — the TypeScript types
  in [`src/types/project.ts`](../src/types/project.ts) are the
  source of truth.

After pushing your changes, the deploy workflow will publish the
new list within minutes.

### 6.1. Validate the data locally

```bash
pnpm run validate
```

Runs `scripts/validate-projects.mjs` against your local data file
and exits 0 / 1 / 2 for clean / validation-error / fatal. The
CI runs the same script in a separate `validate-data` job before
the build job, so a typo in the JSON fails the PR fast.

### 6.2. Refresh metadata from GitHub

The repo includes an automatic metadata refresher
([`scripts/refresh-projects.mjs`](../scripts/refresh-projects.mjs))
that hits the GitHub REST API and updates `stars` / `forks` /
`license` / `lastCommit` for every project. A scheduled
GitHub Action runs it every Sunday 03:00 UTC and auto-commits
the changes.

To run it locally with a higher rate limit, set `GITHUB_TOKEN`:

```bash
GITHUB_TOKEN=ghp_xxx pnpm run refresh
```

### 6.3. Mine new candidates from `awesome-*` lists

```bash
pnpm run scan
```

Reads 7 hand-picked `awesome-*` repos, filters by an
`IN_SCOPE_KEYWORDS` list, and writes
[`data/candidates.json`](../data/candidates.json) for the
maintainer to review. **It does not edit `data/projects.json`**
— it is a one-shot miner, not an auto-importer.

---

## 7. Local preview

```bash
git clone https://github.com/<your-username>/NetTools-Hub.git
cd NetTools-Hub
pnpm install --frozen-lockfile
pnpm dev                 # http://localhost:8080
```

To preview the production build:

```bash
pnpm build
pnpm start               # http://localhost:8080
```

---

## 8. URL tree (the new navigation)

The `/explore` surface is a 2-level hierarchy driven by the
data layer's two orthogonal taxonomies. Each level is its own
static page:

| URL                              | What it shows                                                                                                    |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `/explore`                       | All 210 projects, sorted by `kind` then by stars                                                                 |
| `/explore/k/<kind>`              | Projects filtered to one of the 8 kinds (proxy / vpn / dns / acceleration / security / monitoring / ops / tools) |
| `/explore/k/<kind>/p/<platform>` | That kind, further filtered to one of the 6 platforms (desktop / mobile / cli / server / browser / router)       |

The sidebar on every `/explore` page is a real tree of `<a>`
links — it is the URL hierarchy, not a stateful facet panel.
Drill-down, back/forward, deep links and share-by-link all work
for free.

`generateStaticParams` is wired into both dynamic pages, so the
build emits a complete set of static HTML (1 root + 8 kind + 48
kind+platform = 57 pre-rendered pages).

---

## 9. Troubleshooting

| Symptom                                           | Fix                                                                                                  |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `404` on every `_next/*` asset                    | `basePath` in `next.config.ts` doesn't match the repo name                                           |
| Sub-pages (`/explore`) give 404                   | Make sure `trailingSlash: true` is set in `next.config.ts`                                           |
| Action tab shows the run but Pages is still empty | Wait 1–2 minutes — `actions/deploy-pages` has a small post-deploy delay                              |
| Want to undo a deploy                             | Use **Actions → Deploy to GitHub Pages → Re-run jobs from failed**, or roll back the commit and push |
| `pnpm run validate` exits 1                       | The error is on stdout — read the `ERROR <project>` lines and fix the JSON                           |
| `pnpm run refresh` hits rate limits               | Set `GITHUB_TOKEN` in the env; anonymous calls are capped at 60/h                                    |
| A project shows as `archived` after refresh       | The repo was either deleted (404) or has no commit in the last 2 years — re-evaluate the inclusion   |

For more, see [`CONTRIBUTING.md`](../CONTRIBUTING.md) and [`ARCHITECTURE.md`](./ARCHITECTURE.md).
