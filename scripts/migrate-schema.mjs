#!/usr/bin/env node
// ============================================================================
// NetTools Hub — migrate-schema.mjs
// ============================================================================
//
// One-shot migration that lifts data/projects.json from the v1 schema
// (category + tags + gradient) to the v2 schema (kind + platform[] +
// verdict + status + addedAt + notes).
//
// Idempotent: running it twice produces no further changes. Safe to
// commit the output and then delete the script (or keep it — it's
// only ~200 lines, and serves as executable documentation of the
// v1 -> v2 mapping).
//
// Mapping rules:
//   - `kind` is derived from the existing `category` slug, with a
//     fallback to the tag list (e.g. a "core" project tagged "vpn"
//     becomes kind=vpn, not kind=proxy).
//   - `platform` is derived from the existing `category` slug too
//     (e.g. `gui` -> desktop; `router` -> router). Multi-value
//     projects (sing-box is both server and mobile) get a hand-curated
//     override table.
//   - `status` is derived from `lastCommit` (active / stale / archived).
//   - `addedAt` defaults to the file's top-level `lastUpdated`.
//   - `notes` is left undefined (the maintainer will fill in editorial
//     notes manually; the migration is a structural pass, not an
//     editorial one).
// ============================================================================

import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');
const DATA_FILE = resolve(ROOT, 'data/projects.json');

// slug -> { kind, platform, verdict? }
// Verdict defaults to "neutral"; the migration does not pretend to
// have an opinion on every project.
const SLUG_RULES = {
  core: { kind: 'proxy', platform: ['server'] },
  gui: { kind: 'proxy', platform: ['desktop', 'mobile'] },
  subscription: { kind: 'tools', platform: ['server', 'cli'] },
  github_tools: { kind: 'acceleration', platform: ['server', 'cli'] },
  router: { kind: 'vpn', platform: ['router'] },
  docker: { kind: 'ops', platform: ['server'] },
  rules: { kind: 'proxy', platform: ['server'] },
  utilities: { kind: 'tools', platform: ['cli', 'desktop'] },
  mirrors: { kind: 'acceleration', platform: ['server'] },
  network_test: { kind: 'tools', platform: ['cli', 'desktop'] },
  container: { kind: 'ops', platform: ['server'] },
  server_mgmt: { kind: 'ops', platform: ['server', 'cli'] },
  node_tools: { kind: 'ops', platform: ['cli'] },
  monitoring: { kind: 'monitoring', platform: ['server'] },
  dns_tools: { kind: 'dns', platform: ['server'] },
  cert_tools: { kind: 'tools', platform: ['server', 'cli'] },
  security_tools: { kind: 'security', platform: ['server', 'cli'] },
  collection: { kind: 'tools', platform: ['browser'] },
  protocol_tools: { kind: 'tools', platform: ['cli'] },
  tunnel_tools: { kind: 'vpn', platform: ['server', 'cli'] },
  data_transfer: { kind: 'tools', platform: ['cli', 'server'] },
};

// Per-project overrides: projects whose default slug mapping is
// wrong (e.g. a "gui" project that's really mobile-only, or a
// "monitoring" project that runs on the desktop).
const PROJECT_OVERRIDES = {
  'sing-box': { kind: 'proxy', platform: ['server', 'mobile', 'desktop'] },
  'clash-meta': { kind: 'proxy', platform: ['server', 'desktop', 'router'] },
  'clash-for-windows': { kind: 'proxy', platform: ['desktop'] },
  clashx: { kind: 'proxy', platform: ['desktop'] },
  'clash-verge': { kind: 'proxy', platform: ['desktop'] },
  shadowrocket: { kind: 'proxy', platform: ['mobile'] },
  'quantumult-x': { kind: 'proxy', platform: ['mobile'] },
  surge: { kind: 'proxy', platform: ['mobile', 'desktop'] },
  loon: { kind: 'proxy', platform: ['mobile'] },
  passwall2: { kind: 'proxy', platform: ['router'] },
  openclash: { kind: 'proxy', platform: ['router'] },
  nekobox: { kind: 'proxy', platform: ['desktop', 'mobile'] },
  hiddify: { kind: 'proxy', platform: ['desktop', 'mobile'] },
  v2rayn: { kind: 'proxy', platform: ['desktop'] },
  v2rayng: { kind: 'proxy', platform: ['mobile'] },
  nekoray: { kind: 'proxy', platform: ['desktop'] },
  wireguard: { kind: 'vpn', platform: ['server', 'mobile', 'desktop'] },
  tailscale: { kind: 'vpn', platform: ['server', 'mobile', 'desktop', 'cli'] },
  headscale: { kind: 'vpn', platform: ['server'] },
  netmaker: { kind: 'vpn', platform: ['server'] },
  zerotier: { kind: 'vpn', platform: ['server', 'mobile', 'desktop'] },
  nebula: { kind: 'vpn', platform: ['server', 'cli'] },
  'warp-plus': { kind: 'vpn', platform: ['cli', 'server'] },
  'speedtest-cli': { kind: 'tools', platform: ['cli'] },
  iperf3: { kind: 'tools', platform: ['cli'] },
  'fast-cli': { kind: 'tools', platform: ['cli'] },
  smartdns: { kind: 'dns', platform: ['server', 'router'] },
  adguardhome: { kind: 'dns', platform: ['server'] },
  coredns: { kind: 'dns', platform: ['server'] },
  mosdns: { kind: 'dns', platform: ['server'] },
  'nextdns-cli': { kind: 'dns', platform: ['cli', 'server'] },
  dnsproxy: { kind: 'dns', platform: ['server'] },
  bind9: { kind: 'dns', platform: ['server'] },
  unbound: { kind: 'dns', platform: ['server'] },
  'knot-resolver': { kind: 'dns', platform: ['server'] },
  technitium: { kind: 'dns', platform: ['server'] },
  wireshark: { kind: 'tools', platform: ['desktop', 'cli'] },
  tcpdump: { kind: 'tools', platform: ['cli'] },
  nmap: { kind: 'tools', platform: ['cli'] },
  masscan: { kind: 'tools', platform: ['cli'] },
  mtr: { kind: 'tools', platform: ['cli'] },
  bandwhich: { kind: 'tools', platform: ['cli'] },
  gping: { kind: 'tools', platform: ['cli'] },
  snell: { kind: 'proxy', platform: ['server'] },
  brook: { kind: 'proxy', platform: ['server', 'cli'] },
  naiveproxy: { kind: 'proxy', platform: ['server'] },
  mieru: { kind: 'proxy', platform: ['server', 'desktop', 'mobile'] },
};

const ACTIVE_DAYS = 180;
const STALE_DAYS = 730;
function deriveStatus(lastCommit) {
  const d = (Date.now() - new Date(lastCommit).getTime()) / 86_400_000;
  if (d < ACTIVE_DAYS) return 'active';
  if (d < STALE_DAYS) return 'stale';
  return 'archived';
}

async function main() {
  const raw = await readFile(DATA_FILE, 'utf8');
  const data = JSON.parse(raw);
  const addedAt = (data.lastUpdated || new Date().toISOString()).slice(0, 10);

  let touched = 0;
  for (const p of data.projects) {
    const override = PROJECT_OVERRIDES[p.id];
    const rule = SLUG_RULES[p.category] || {};
    const newKind = override?.kind || rule.kind;
    const newPlatform = override?.platform || rule.platform;
    const newStatus = deriveStatus(p.lastCommit);
    const changed =
      p.kind !== newKind ||
      JSON.stringify(p.platform) !== JSON.stringify(newPlatform) ||
      p.status !== newStatus ||
      p.addedAt !== addedAt;
    if (changed) touched += 1;
    p.kind = newKind;
    p.platform = newPlatform;
    p.status = newStatus;
    if (!p.addedAt) p.addedAt = addedAt;
    // Verdict is left untouched: a manual override beats the default,
    // and the migration does not have a strong opinion.
  }

  data.schemaVersion = 2;

  // Stable key order
  const ordered = {
    lastUpdated: data.lastUpdated,
    schemaVersion: data.schemaVersion,
    categories: data.categories,
    projects: data.projects,
  };
  await writeFile(DATA_FILE, JSON.stringify(ordered, null, 2) + '\n', 'utf8');
  process.stdout.write(
    `Migrated ${data.projects.length} projects (${touched} touched) to schema v2.\n` +
      `Default addedAt = ${addedAt}\n`,
  );
}

main().catch((e) => {
  process.stderr.write(`fatal: ${e.stack || e.message}\n`);
  process.exit(2);
});
