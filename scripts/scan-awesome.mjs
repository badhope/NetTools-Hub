#!/usr/bin/env node
// ============================================================================
// NetTools Hub — scan-awesome.mjs
// ============================================================================
//
// Pulls the README of a curated list of "awesome-*" repos, extracts
// GitHub repository URLs, and emits a JSON report of *candidates*
// not already present in data/projects.json. The output is a
// PR-ready diff that the maintainer can review and merge in.
//
// Why a script (and not a full auto-merge):
//   - Inclusion is *editorial*; the script cannot decide that a
//     new candidate is "good enough to link to" — only the
//     maintainer can.
//   - False positives are common (awesome lists include a lot of
//     awesome-but-unrelated stuff like general Linux networking
//     books). A review step is required.
//   - The output is a single JSON file (data/candidates.json)
//     plus a human-readable Markdown summary printed to stdout,
//     so the workflow can attach the summary as an artifact
//     without polluting the repo.
//
// Rate limiting & etiquette:
//   - GitHub's raw.githubusercontent.com endpoint does *not*
//     require auth but is heavily cached; a polite `sleep`
//     between fetches is still good citizenship.
//   - The script is read-only; it does not push.
//
// Failure modes:
//   - 404 on a source repo: logged, source dropped, others
//     continue. The script never aborts on a single source.
// ============================================================================

import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");
const DATA_FILE = resolve(ROOT, "data/projects.json");
const CANDIDATES_FILE = resolve(ROOT, "data/candidates.json");

// ----------------------------------------------------------------------------
// Configuration: the awesome-* repos we mine.
// ----------------------------------------------------------------------------
//
// We *could* auto-discover the awesome ecosystem via GitHub search,
// but that would (a) burn a lot of API budget, (b) return a lot of
// off-topic noise, and (c) be unstable across runs. A short hand-
// picked list is the right size: every repo in it is known to the
// maintainer, has been checked at least once, and is unlikely to
// drift away from the network-tools topic.
const SOURCES = [
  { repo: "awesome-selfhosted/awesome-selfhosted", topic: "selfhost" },
  { repo: "kitian616/awesome-vpn",                  topic: "vpn" },
  { repo: "rtfmk/awesome-network",                  topic: "network" },
  { repo: "caesar0301/awesome-pcaptools",           topic: "pcap" },
  { repo: "fabacab/awesome-cybersecurity-blueteam", topic: "security" },
  { repo: "mqyqingfeng/awesome-github",             topic: "github-accel" },
  { repo: "yuliskov/SmartTVDNS",                    topic: "dns" }, // example
];

// Keywords that suggest the project is in scope for the index.
// Match is case-insensitive and runs against the project name +
// description text (if extractable). Empty array = accept all.
const IN_SCOPE_KEYWORDS = [
  "proxy", "vpn", "wireguard", "clash", "v2ray", "xray",
  "shadowsocks", "trojan", "hysteria", "tuic", "ssr",
  "dns", "smartdns", "adguard", "coredns",
  "wire", "packet", "tcp", "udp", "nat", "ipv6", "bgp", "ospf",
  "load balancer", "reverse proxy", "nginx", "caddy", "traefik",
  "waf", "ids", "ips", "firewall", "honeypot",
  "monitoring", "uptime", "prometheus", "smokeping", "mtr", "iperf",
  "github", "mirror", "accelerat",
  "router", "openwrt", "lede",
  "docker", "kubernetes", "k3s",
  "subscription", "ssr-sub", "clash-sub", "v2ray-sub",
  "sniff", "capture", "pcap", "tcpdump", "wireshark",
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ----------------------------------------------------------------------------
// Extraction
// ----------------------------------------------------------------------------

/** Fetch a repo's default README as plain text. */
async function fetchReadme(ownerRepo) {
  const url = `https://raw.githubusercontent.com/${ownerRepo}/HEAD/README.md`;
  const res = await fetch(url, {
    headers: { "User-Agent": "nettools-hub-scanner" },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} on ${ownerRepo}`);
  return res.text();
}

/**
 * Extract GitHub repo URLs (`https://github.com/owner/repo`) from a
 * markdown document. Returns owner/repo strings, deduped, in the
 * order they appeared.
 */
function extractGithubRepos(markdown) {
  const seen = new Set();
  const out = [];
  // The single regex catches `https://github.com/owner/repo` with
  // optional trailing path / query / fragment / `.git`. We then
  // canonicalise to `owner/repo` and drop the rest.
  const re = /https?:\/\/github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)/g;
  let m;
  while ((m = re.exec(markdown)) !== null) {
    const owner = m[1];
    const repo = m[2].replace(/\.git$/, "");
    // Skip non-canonical entries: orgs, topics, "sponsors", etc.
    if (
      owner === "sponsors" ||
      owner === "orgs" ||
      owner === "settings" ||
      owner === "topics"
    ) continue;
    if (repo === "") continue;
    const key = `${owner}/${repo}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(key);
  }
  return out;
}

/** Cheap "is this in scope" check, based on repo name only (we
 *  don't fetch every candidate's description — that would burn
 *  the API budget the refresh script needs). */
function inScope(ownerRepo) {
  if (IN_SCOPE_KEYWORDS.length === 0) return true;
  const haystack = ownerRepo.toLowerCase();
  return IN_SCOPE_KEYWORDS.some((k) => haystack.includes(k));
}

// ----------------------------------------------------------------------------
// Main
// ----------------------------------------------------------------------------

async function main() {
  const startedAt = new Date().toISOString();
  const data = JSON.parse(await readFile(DATA_FILE, "utf8"));
  const known = new Set(
    data.projects.map((p) => {
      const u = new URL(p.url);
      return `${u.pathname.split("/")[1]}/${u.pathname.split("/")[2]}`.replace(
        /\.git$/,
        "",
      );
    }),
  );

  const allFound = new Map(); // owner/repo -> { sources: [...] }
  for (const src of SOURCES) {
    process.stdout.write(`scanning ${src.repo} ... `);
    try {
      const md = await fetchReadme(src.repo);
      const repos = extractGithubRepos(md);
      for (const r of repos) {
        if (!allFound.has(r)) allFound.set(r, { sources: [], topic: src.topic });
        allFound.get(r).sources.push(src.repo);
      }
      process.stdout.write(`${repos.length} github links\n`);
    } catch (e) {
      process.stdout.write(`FAIL (${e.message})\n`);
    }
    // 100 ms between source fetches — raw.githubusercontent.com is
    // CDN-fronted and will not actually care, but it keeps the
    // log readable when many sources are in flight.
    await sleep(100);
  }

  const candidates = [];
  for (const [ownerRepo, meta] of allFound) {
    if (known.has(ownerRepo)) continue;        // already indexed
    if (!inScope(ownerRepo)) continue;         // off-topic
    candidates.push({
      ownerRepo,
      url: `https://github.com/${ownerRepo}`,
      sources: meta.sources,
      topic: meta.topic,
    });
  }
  candidates.sort((a, b) => a.ownerRepo.localeCompare(b.ownerRepo));

  // Persist as a machine-readable file (the workflow attaches the
  // human summary as an artifact separately).
  const out = {
    generatedAt: startedAt,
    sourcesScanned: SOURCES.length,
    candidatesCount: candidates.length,
    candidates,
  };
  await writeFile(CANDIDATES_FILE, JSON.stringify(out, null, 2) + "\n", "utf8");

  // Human summary
  process.stdout.write(
    `\nFound ${candidates.length} candidate projects not in the index.\n` +
      `Report: data/candidates.json\n\n`,
  );
  for (const c of candidates.slice(0, 50)) {
    process.stdout.write(
      `  ${c.ownerRepo.padEnd(40)} topic=${c.topic.padEnd(14)} via ${c.sources[0]}\n`,
    );
  }
  if (candidates.length > 50) {
    process.stdout.write(`  ... and ${candidates.length - 50} more (see JSON)\n`);
  }
}

main().catch((e) => {
  process.stderr.write(`fatal: ${e.stack || e.message}\n`);
  process.exit(2);
});
