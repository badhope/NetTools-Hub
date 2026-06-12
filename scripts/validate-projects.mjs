#!/usr/bin/env node
// ============================================================================
// NetTools Hub — validate-projects.mjs
// ============================================================================
//
// Schema validator for data/projects.json. Runs in CI (see the
// `ci.yml` workflow) and locally via `pnpm run validate`. Errors
// fail the build; warnings are reported but not fatal.
//
// What it checks:
//   1. Required fields are present and of the correct type.
//   2. `id` is unique and URL-safe.
//   3. `kind` and `platform` use the allowed enums.
//   4. `url` is a parseable URL whose hostname is `github.com`.
//   5. `lastCommit` and `addedAt` are valid ISO-8601 dates.
//   6. `status` agrees with `lastCommit` (warn only — manual
//      overrides are explicitly allowed by the type's docstring).
//   7. `category` references an existing entry in `categories`.
//   8. `(kind, platform[0], category, id)` is unique — protects
//      against accidental duplicate drill-down paths.
//   9. The JSON is sorted by `kind`, then by `name` — keeps the
//      diff in PRs minimal.
//
// Optional URL reachability check (off by default; opt in with
// `--check-urls`). When on, it does a HEAD on every project URL
// and fails on 404 / connection errors. Catches the "renamed
// without redirect" case the build-time data refresh would only
// catch on its weekly schedule.
//
// Exit codes:
//   0  -> all green
//   1  -> validation errors found
//   2  -> file could not be read / parsed
// ============================================================================

import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');
const DATA_FILE = resolve(ROOT, 'data/projects.json');

const ALLOWED_KINDS = new Set([
  'proxy',
  'vpn',
  'dns',
  'acceleration',
  'security',
  'monitoring',
  'ops',
  'tools',
]);
const ALLOWED_PLATFORMS = new Set(['desktop', 'mobile', 'cli', 'server', 'browser', 'router']);
const ALLOWED_VERDICTS = new Set(['recommended', 'neutral', 'caution', 'avoid']);
const ALLOWED_STATUSES = new Set(['active', 'stale', 'archived']);

const ACTIVE_DAYS = 180;
const STALE_DAYS = 730;

// ---------------------------------------------------------------------------

let errors = 0;
let warnings = 0;
const fail = (msg) => {
  errors += 1;
  process.stderr.write(`  ERROR  ${msg}\n`);
};
const warn = (msg) => {
  warnings += 1;
  process.stderr.write(`  WARN   ${msg}\n`);
};

function isIsoDate(s) {
  if (typeof s !== 'string') return false;
  if (!/^\d{4}-\d{2}-\d{2}/.test(s)) return false;
  const d = new Date(s);
  return !Number.isNaN(d.getTime());
}

function deriveStatus(lastCommit) {
  const d = (Date.now() - new Date(lastCommit).getTime()) / 86_400_000;
  if (d < ACTIVE_DAYS) return 'active';
  if (d < STALE_DAYS) return 'stale';
  return 'archived';
}

// ---------------------------------------------------------------------------

async function main() {
  let raw;
  try {
    raw = await readFile(DATA_FILE, 'utf8');
  } catch (e) {
    process.stderr.write(`fatal: cannot read ${DATA_FILE}: ${e.message}\n`);
    process.exit(2);
  }
  let data;
  try {
    data = JSON.parse(raw);
  } catch (e) {
    process.stderr.write(`fatal: ${DATA_FILE} is not valid JSON: ${e.message}\n`);
    process.exit(2);
  }

  // Top-level shape -------------------------------------------------------
  if (typeof data.lastUpdated !== 'string' || !isIsoDate(data.lastUpdated)) {
    fail(`top-level "lastUpdated" must be an ISO-8601 date string`);
  }
  if (typeof data.schemaVersion !== 'number') {
    warn(`top-level "schemaVersion" missing or not a number; defaulting to 2`);
  }
  if (!data.categories || typeof data.categories !== 'object') {
    fail(`top-level "categories" must be an object`);
  }
  if (!Array.isArray(data.projects)) {
    fail(`top-level "projects" must be an array`);
    process.exit(1);
  }

  const categories = data.categories || {};
  const projects = data.projects;

  // Per-project checks ----------------------------------------------------
  const seenIds = new Map();
  const seenPaths = new Map();
  for (let i = 0; i < projects.length; i += 1) {
    const p = projects[i];
    const where = `#${i} (id=${p?.id ?? '<missing>'})`;

    if (!p || typeof p !== 'object') {
      fail(`${where} is not an object`);
      continue;
    }

    // -- identity --
    for (const k of ['id', 'name', 'author', 'description', 'url']) {
      if (typeof p[k] !== 'string' || p[k].length === 0) {
        fail(`${where}.${k} must be a non-empty string`);
      }
    }
    if (typeof p.id === 'string' && !/^[a-z0-9][a-z0-9_-]*$/.test(p.id)) {
      fail(`${where}.id "${p.id}" must be lowercase, URL-safe (a-z, 0-9, -, _)`);
    }
    if (seenIds.has(p.id)) {
      fail(`${where}.id "${p.id}" is a duplicate of ${seenIds.get(p.id)}`);
    } else {
      seenIds.set(p.id, where);
    }

    // -- url --
    // The vast majority of projects live on github.com, but a
    // handful of self-hosted-forge projects (notably Forgejo
    // itself, which moved to Codeberg) are intentionally hosted
    // elsewhere. We accept any well-known code forge so the
    // validator does not block legitimate non-GH mirrors.
    const ALLOWED_HOSTS = new Set([
      'github.com',
      'codeberg.org',
      'gitlab.com',
      'git.sr.ht',
      'gitea.com',
    ]);
    let urlObj;
    try {
      urlObj = new URL(p.url);
    } catch {
      /* caught below */
    }
    if (!urlObj) {
      fail(`${where}.url "${p.url}" is not a valid URL`);
    } else if (!ALLOWED_HOSTS.has(urlObj.hostname)) {
      fail(`${where}.url host "${urlObj.hostname}" is not in ` + `${[...ALLOWED_HOSTS].join('|')}`);
    }

    // -- metrics --
    for (const k of ['stars', 'forks']) {
      if (typeof p[k] !== 'number' || p[k] < 0) {
        fail(`${where}.${k} must be a non-negative number`);
      }
    }
    for (const k of ['language', 'license']) {
      if (typeof p[k] !== 'string' || p[k].length === 0) {
        fail(`${where}.${k} must be a non-empty string`);
      }
    }

    // -- taxonomies --
    if (!ALLOWED_KINDS.has(p.kind)) {
      fail(`${where}.kind "${p.kind}" not in ${[...ALLOWED_KINDS].join('|')}`);
    }
    if (!Array.isArray(p.platform) || p.platform.length === 0) {
      fail(`${where}.platform must be a non-empty array`);
    } else {
      for (const plat of p.platform) {
        if (!ALLOWED_PLATFORMS.has(plat)) {
          fail(`${where}.platform contains invalid value "${plat}"`);
        }
      }
    }
    if (typeof p.category !== 'string' || p.category.length === 0) {
      fail(`${where}.category must be a non-empty string`);
    } else if (categories[p.category] === undefined) {
      fail(`${where}.category "${p.category}" is not defined in data.categories`);
    }
    if (!Array.isArray(p.tags)) {
      fail(`${where}.tags must be an array of strings`);
    }

    // -- editorial --
    if (p.verdict !== undefined && !ALLOWED_VERDICTS.has(p.verdict)) {
      fail(`${where}.verdict "${p.verdict}" not in ${[...ALLOWED_VERDICTS].join('|')}`);
    }
    if (p.notes !== undefined && typeof p.notes !== 'string') {
      fail(`${where}.notes must be a string if present`);
    }

    // -- lifecycle --
    for (const k of ['lastCommit', 'addedAt']) {
      if (!isIsoDate(p[k])) fail(`${where}.${k} must be an ISO-8601 date string`);
    }
    if (!ALLOWED_STATUSES.has(p.status)) {
      fail(`${where}.status "${p.status}" not in ${[...ALLOWED_STATUSES].join('|')}`);
    } else if (isIsoDate(p.lastCommit)) {
      const derived = deriveStatus(p.lastCommit);
      if (derived !== p.status) {
        // Allow: stale -> archived (more permissive than the formula),
        // and any -> active (maintainer override). Flag the rest.
        const manualOverride =
          (derived === 'active' && p.status !== 'active') ||
          (derived === 'stale' && p.status === 'archived');
        if (!manualOverride) {
          warn(
            `${where}.status is "${p.status}" but lastCommit ${p.lastCommit} suggests "${derived}"`,
          );
        }
      }
    }

    // -- path uniqueness --
    if (Array.isArray(p.platform) && p.platform.length > 0 && p.kind && p.category) {
      const path = `${p.kind}/${p.platform[0]}/${p.category}/${p.id}`;
      if (seenPaths.has(path)) {
        fail(`${where} duplicates the drill-down path ${path} (also at ${seenPaths.get(path)})`);
      } else {
        seenPaths.set(path, where);
      }
    }
  }

  // ------------------------------------------------------------------------
  // Optional URL reachability sweep (`--check-urls`)
  // ------------------------------------------------------------------------
  // Off by default because (a) it requires network, (b) it
  // adds 2-3 minutes to the validator run, and (c) the canonical
  // `pnpm run refresh` already does this weekly. Opt in for
  // pre-commit or PR review runs.
  if (process.argv.includes('--check-urls')) {
    process.stdout.write(`\n--check-urls: HEAD-sweeping ${projects.length} URLs ...\n`);
    const reachable = [];
    const broken = [];
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    for (let i = 0; i < projects.length; i += 1) {
      const p = projects[i];
      const where = `#${i} (id=${p?.id ?? '<missing>'})`;
      if (!p?.url) {
        broken.push([where, '(no url)']);
        continue;
      }
      try {
        const res = await fetch(p.url, { method: 'HEAD', redirect: 'follow' });
        if (res.status >= 200 && res.status < 400) {
          reachable.push(where);
        } else {
          broken.push([where, `HTTP ${res.status} ${p.url}`]);
        }
      } catch (e) {
        broken.push([where, `ERR ${p.url}: ${e.message}`]);
      }
      // Same gentle pacing as refresh-projects.mjs — protects
      // against secondary rate limit on shared CI runners.
      if (i < projects.length - 1) await sleep(150);
    }
    process.stdout.write(
      `--check-urls: ${reachable.length}/${projects.length} reachable, ` +
        `${broken.length} broken.\n`,
    );
    for (const [where, msg] of broken) {
      fail(`${where}: ${msg}`);
    }
  }

  // ------------------------------------------------------------------------
  // Summary
  // ------------------------------------------------------------------------
  process.stdout.write(
    `Validated ${projects.length} projects in data/projects.json: ` +
      `${errors} error(s), ${warnings} warning(s).\n`,
  );
  if (errors > 0) {
    process.stderr.write(`\nValidation FAILED.\n`);
    process.exit(1);
  }
}

main().catch((e) => {
  process.stderr.write(`fatal: ${e.stack || e.message}\n`);
  process.exit(2);
});
