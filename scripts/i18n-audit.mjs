#!/usr/bin/env node
// ============================================================================
// NetTools Hub — i18n-audit.mjs
// ============================================================================
//
// Validates that all three language dictionaries (en, zh, ja)
// have identical key sets. Missing keys are reported as errors;
// extra keys (present in one language but not another) are also
// errors. Exit code 1 if any mismatch is found.
//
// Usage:
//   pnpm run i18n:audit
//
// This script is run in CI to catch translation drift before
// it reaches production.
// ============================================================================

import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const i18nPath = resolve(__dirname, '../src/lib/i18n.ts');

// Extract the translations object from the TypeScript source.
// We parse it as a JS object by stripping the type annotations.
const source = readFileSync(i18nPath, 'utf-8');

// Match each language block: `en: { ... }, zh: { ... }, ja: { ... }`
const langBlocks = ['en', 'zh', 'ja'];
const keysByLang = {};

for (const lang of langBlocks) {
  // Find the block for this language
  const blockRegex = new RegExp(`${lang}:\\s*\\{([^}]+)\\}`, 's');
  const match = source.match(blockRegex);
  if (!match) {
    console.error(`❌ Could not find ${lang} block in i18n.ts`);
    process.exit(2);
  }

  const blockContent = match[1];
  // Extract all keys: "key.name": "value"
  const keyRegex = /"([^"]+)":\s*"[^"]*"/g;
  const keys = new Set();
  let m;
  while ((m = keyRegex.exec(blockContent)) !== null) {
    keys.add(m[1]);
  }
  keysByLang[lang] = keys;
}

// Compare key sets
const enKeys = keysByLang.en;
let errors = 0;

for (const lang of ['zh', 'ja']) {
  const langKeys = keysByLang[lang];

  // Keys in English but missing in this language
  for (const key of enKeys) {
    if (!langKeys.has(key)) {
      console.error(`❌ ${lang} missing key: "${key}"`);
      errors++;
    }
  }

  // Keys in this language but not in English (extra keys)
  for (const key of langKeys) {
    if (!enKeys.has(key)) {
      console.error(`❌ ${lang} has extra key: "${key}" (not in en)`);
      errors++;
    }
  }
}

// Summary
const enCount = enKeys.size;
const zhCount = keysByLang.zh.size;
const jaCount = keysByLang.ja.size;

console.log(`\n📊 i18n key counts:`);
console.log(`   en: ${enCount}`);
console.log(`   zh: ${zhCount}`);
console.log(`   ja: ${jaCount}`);

if (errors > 0) {
  console.error(`\n❌ Found ${errors} i18n mismatch(es).`);
  process.exit(1);
} else {
  console.log(`\n✅ All ${enCount} keys are present in all three languages.`);
  process.exit(0);
}
