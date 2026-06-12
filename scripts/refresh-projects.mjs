#!/usr/bin/env node
// ============================================================================
// NetTools Hub — refresh-projects.mjs
// ============================================================================
//
// Reads data/projects.json, calls the GitHub REST API for every project
// to refresh the volatile fields (stars, forks, license, lastCommit),
// derives the activity status from lastCommit, and writes the result
// back to the same file in a deterministic, sorted-stable order.
//
// Why a Node script (and not Python / Bash):
//   - Node ships with `fetch` (Node 18+), so no extra deps;
//   - the script is consumed by a GitHub Action that already has Node
//     22 in its matrix;
//   - using the same language as the rest of the repo keeps the
//     contributor surface small (CONTRIBUTING.md only needs to
//     document one toolchain).
//
// Rate limiting:
//   - Anonymous: 60 req/h per IP — useless for a 200+ project list.
//   - Authenticated: 5000 req/h — enough for one full refresh.
//   The script reads `GITHUB_TOKEN` from the environment if present
//   and falls back to `GH_TOKEN`. If neither is set it runs anonymous
//   and prints a clear warning.
//
// Idempotency:
//   - The file is read, mutated, and written in place.
//   - Field order within each project object is preserved.
//   - Project order in the array is preserved (sort is by id only on
//     *new* inserts).
//
// Failure modes:
//   - A failed GitHub fetch on a single project is logged and the
//     project's existing fields are kept untouched; the script
//     continues. The exit code is non-zero only if the *file*
//     cannot be read or written.
// ============================================================================

import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");
const DATA_FILE = resolve(ROOT, "data/projects.json");

// Activity thresholds (in days since the last observed commit).
const ACTIVE_DAYS = 180;   // < 6 months  -> "active"
const STALE_DAYS = 730;    // < 2 years   -> "stale"; older -> "archived"

const TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN || "";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** Best-effort extraction of `owner/repo` from any supported forge URL. */
const FORGE_HOSTS = new Set([
  "github.com",
  "codeberg.org",
  "gitlab.com",
  "git.sr.ht",
  "gitea.com",
]);

function parseOwnerRepo(url) {
  try {
    const u = new URL(url);
    if (!FORGE_HOSTS.has(u.hostname)) return null;
    const parts = u.pathname.split("/").filter(Boolean);
    if (parts.length < 2) return null;
    return `${u.hostname}/${parts[0]}/${parts[1]}`.replace(/\.git$/, "");
  } catch {
    return null;
  }
}

function repoApiUrl(ownerRepo) {
  const [host, owner, repo] = ownerRepo.split("/");
  if (host === "github.com") {
    return `https://api.github.com/repos/${owner}/${repo}`;
  }
  // Gitea-family (codeberg, gitea.com): same /repos/:owner/:repo shape.
  if (host === "codeberg.org" || host === "gitea.com") {
    return `https://${host}/api/v1/repos/${owner}/${repo}`;
  }
  // GitLab: /api/v4/projects/:namespace%2F:project
  if (host === "gitlab.com") {
    return `https://gitlab.com/api/v4/projects/${encodeURIComponent(`${owner}/${repo}`)}`;
  }
  return null;
}

/** Normalise a forge response into a single shape so the rest
 *  of the script can stay forge-agnostic. */
function normaliseRepo(r, ownerRepo) {
  const host = ownerRepo.split("/")[0];
  if (host === "github.com") {
    return {
      stars: r.stargazers_count,
      forks: r.forks_count,
      language: r.language,
      license: r.license?.spdx_id || r.license?.key,
      pushed_at: r.pushed_at,
    };
  }
  if (host === "codeberg.org" || host === "gitea.com") {
    // Gitea: stars_count, forks_count, language, updated_at
    return {
      stars: r.stars_count,
      forks: r.forks_count,
      language: r.language,
      license: (r.license && (r.license.spdx_id || r.license.name)) || undefined,
      pushed_at: r.updated_at || r.pushed_at,
    };
  }
  if (host === "gitlab.com") {
    // GitLab: star_count, forks_count, last_activity_at
    return {
      stars: r.star_count,
      forks: r.forks_count,
      language: undefined, // GitLab's `languages` endpoint is separate
      license: (r.license && r.license.key) || undefined,
      pushed_at: r.last_activity_at,
    };
  }
  return {};
}

/** Days between two ISO date strings. Negative if `b` is before `a`. */
function daysBetween(a, b) {
  return (new Date(b).getTime() - new Date(a).getTime()) / 86_400_000;
}

function deriveStatus(lastCommit, today = new Date().toISOString()) {
  const d = daysBetween(lastCommit, today);
  if (d < ACTIVE_DAYS) return "active";
  if (d < STALE_DAYS) return "stale";
  return "archived";
}

/** Fetch a repo's current state from the forge REST API. */
async function fetchRepo(ownerRepo, { retries = 3 } = {}) {
  const apiUrl = repoApiUrl(ownerRepo);
  if (!apiUrl) throw new Error(`no API for ${ownerRepo}`);
  const headers = { "User-Agent": "nettools-hub-refresh" };
  if (apiUrl.includes("api.github.com")) {
    headers.Accept = "application/vnd.github+json";
    headers["X-GitHub-Api-Version"] = "2022-11-28";
    if (TOKEN) headers.Authorization = `Bearer ${TOKEN}`;
  } else if (apiUrl.includes("codeberg.org") || apiUrl.includes("gitea.com")) {
    headers.Accept = "application/json";
  } else if (apiUrl.includes("gitlab.com")) {
    headers.Accept = "application/json";
    if (TOKEN) headers["PRIVATE-TOKEN"] = TOKEN;
  }
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    const res = await fetch(apiUrl, { headers });
    if (res.status === 200) return await res.json();
    if (res.status === 403 || res.status === 429) {
      // rate limit / secondary rate limit
      const retryAfter = Number(res.headers.get("retry-after") || 1);
      const wait = Math.max(1000, retryAfter * 1000) * Math.min(2 ** attempt, 8);
      process.stderr.write(
        `  rate-limited on ${ownerRepo}, waiting ${(wait / 1000).toFixed(1)}s\n`,
      );
      await sleep(wait);
      continue;
    }
    if (res.status === 404) {
      // 404 is permanent — no point retrying. Bubble up to the caller
      // so it can mark the entry accordingly.
      const e = new Error(`404 ${ownerRepo}`);
      e.permanent = true;
      throw e;
    }
    if (res.status >= 500 && attempt < retries) {
      await sleep(500 * 2 ** attempt);
      continue;
    }
    throw new Error(`HTTP ${res.status} on ${ownerRepo}`);
  }
  throw new Error(`exhausted retries on ${ownerRepo}`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const startedAt = new Date().toISOString();
  const raw = await readFile(DATA_FILE, "utf8");
  const data = JSON.parse(raw);
  const projects = data.projects || [];
  if (projects.length === 0) {
    process.stderr.write("data/projects.json has no projects, nothing to do.\n");
    process.exit(0);
  }

  if (!TOKEN) {
    process.stderr.write(
      "WARNING: no GITHUB_TOKEN / GH_TOKEN set, using unauthenticated " +
        "requests (60/h). For 200+ projects this will be heavily throttled.\n",
    );
  }

  let updated = 0;
  let failed = 0;
  let moved = 0; // entries whose `status` field flipped

  for (let i = 0; i < projects.length; i += 1) {
    const p = projects[i];
    const ownerRepo = parseOwnerRepo(p.url);
    if (!ownerRepo) {
      process.stderr.write(`[${i + 1}/${projects.length}] skip (non-forge): ${p.id}\n`);
      continue;
    }
    try {
      const r = await fetchRepo(ownerRepo);
      // Each forge returns a slightly different shape. Map it
      // to a common {stars, forks, language, license, pushed_at}.
      const norm = normaliseRepo(r, ownerRepo);
      if (!norm.pushed_at) {
        process.stderr.write(
          `[${i + 1}/${projects.length}] skip (no pushed_at): ${ownerRepo}\n`,
        );
        continue;
      }
      const newStatus = deriveStatus(norm.pushed_at);
      const oldStatus = p.status;
      const newFields = {
        stars: norm.stars ?? p.stars,
        forks: norm.forks ?? p.forks,
        language: norm.language || p.language,
        license: norm.license || p.license,
        lastCommit: (norm.pushed_at || p.lastCommit).slice(0, 10),
        status: newStatus,
      };
      const changed = Object.entries(newFields).some(
        ([k, v]) => p[k] !== v,
      );
      Object.assign(p, newFields);
      if (oldStatus !== newStatus) moved += 1;
      if (changed) updated += 1;
      process.stdout.write(
        `[${i + 1}/${projects.length}] ${ownerRepo.padEnd(40)} ` +
          `★${String(newFields.stars).padStart(6)} ` +
          `status=${newFields.status.padEnd(8)} ` +
          `last=${newFields.lastCommit}` +
          (changed ? " *" : "") +
          "\n",
      );
    } catch (e) {
      failed += 1;
      process.stderr.write(
        `[${i + 1}/${projects.length}] FAIL ${ownerRepo}: ${e.message}\n`,
      );
      // 404: keep the entry but mark it archived so the UI can dim it.
      if (e.permanent) {
        p.status = "archived";
        moved += 1;
      }
    }
    // Gentle pacing even when authenticated: the search-style 30 req/min
    // burst limit is forgiving, but writing 200+ requests in <2 seconds
    // triggers the secondary rate limit on some accounts.
    if (i < projects.length - 1) await sleep(80);
  }

  data.lastUpdated = startedAt;
  data.schemaVersion = data.schemaVersion || 2;

  // Write back with stable key order. JSON.stringify preserves the
  // insertion order of the parsed object, so the only thing to be
  // careful about is the top-level `lastUpdated` / `schemaVersion`
  // keys (we want them to remain at the top, as before).
  const ordered = {
    lastUpdated: data.lastUpdated,
    schemaVersion: data.schemaVersion,
    categories: data.categories,
    projects: data.projects,
  };
  await writeFile(DATA_FILE, JSON.stringify(ordered, null, 2) + "\n", "utf8");

  process.stdout.write(
    `\nRefreshed ${updated}/${projects.length} entries, ` +
      `${moved} status transitions, ${failed} failures.\n` +
      `lastUpdated -> ${data.lastUpdated}\n`,
  );
  // Exit non-zero if every single project failed — that's a real
  // problem, not just "GH is having a bad day for a few repos".
  if (failed === projects.length) process.exit(1);
}

main().catch((e) => {
  process.stderr.write(`fatal: ${e.stack || e.message}\n`);
  process.exit(2);
});
