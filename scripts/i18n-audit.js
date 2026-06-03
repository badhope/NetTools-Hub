const fs = require('fs');
const path = require('path');

const ROOT = '/workspace/net-tools-hub/src';
const i18n = fs.readFileSync(path.join(ROOT, 'lib/i18n.ts'), 'utf-8');
const enSection = i18n.split('en: {')[1].split('zh: {')[0];
const zhSection = i18n.split('zh: {')[1].split('ja: {')[0];
const jaSection = i18n.split('ja: {')[1].split('};')[0];
const extractKeys = (s) => Array.from(s.matchAll(/"([^"]+)":\s*"/g)).map((m) => m[1]);
const enKeys = extractKeys(enSection);
const zhKeys = extractKeys(zhSection);
const jaKeys = extractKeys(jaSection);

const files = [
  'components/landing-content.tsx',
  'components/explore-content.tsx',
  'components/top-nav.tsx',
  'components/sidebar.tsx',
  'components/search-bar.tsx',
  'components/sort-select.tsx',
  'components/project-list.tsx',
  'components/project-card.tsx',
  'components/language-switcher.tsx',
  'components/stats-bar.tsx',
  'components/set-html-lang.tsx',
  'app/error.tsx',
  'app/explore/error.tsx',
  'app/not-found.tsx',
];
const allText = files.map((f) => fs.readFileSync(path.join(ROOT, f), 'utf-8')).join('\n');

const usedKeys = new Set();
for (const m of allText.matchAll(/t\(lang,\s*"([^"]+)"/g)) usedKeys.add(m[1]);
for (const m of allText.matchAll(/t\(lang,\s*'([^']+)'/g)) usedKeys.add(m[1]);

console.log('Total EN keys:', enKeys.length);
console.log('Total ZH keys:', zhKeys.length);
console.log('Total JA keys:', jaKeys.length);
console.log('Total used keys:', usedKeys.size);
console.log('\n--- DEAD KEYS (defined in EN but never used) ---');
const dead = enKeys.filter((k) => !usedKeys.has(k));
for (const k of dead) console.log('  ' + k);

console.log('\n--- KEYS in ZH not in EN (mismatch!) ---');
for (const k of zhKeys) if (!enKeys.includes(k)) console.log('  ZH: ' + k);

console.log('\n--- KEYS in JA not in EN (mismatch!) ---');
for (const k of jaKeys) if (!enKeys.includes(k)) console.log('  JA: ' + k);

console.log('\n--- KEYS in EN not in ZH (mismatch!) ---');
for (const k of enKeys) if (!zhKeys.includes(k)) console.log('  EN: ' + k);

console.log('\n--- KEYS in EN not in JA (mismatch!) ---');
for (const k of enKeys) if (!jaKeys.includes(k)) console.log('  EN: ' + k);
