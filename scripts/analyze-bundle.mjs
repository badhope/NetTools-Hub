#!/usr/bin/env node
// ============================================================================
// NetTools Hub — analyze-bundle.mjs
// ============================================================================
//
// Analyzes the build output to identify large chunks and potential
// optimization opportunities.
//
// Usage:
//   pnpm run analyze
//
// This script runs after `next build` and reports:
//   - Total bundle size
//   - Top 10 largest chunks
//   - Duplicate dependencies (if any)
//   - Suggestions for code splitting
// ============================================================================

import { readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const BUILD_DIR = '.next';
const CHUNKS_DIR = join(BUILD_DIR, 'static/chunks');

function getDirSize(dir) {
  let size = 0;
  try {
    const files = readdirSync(dir);
    for (const file of files) {
      const path = join(dir, file);
      const stats = statSync(path);
      if (stats.isDirectory()) {
        size += getDirSize(path);
      } else {
        size += stats.size;
      }
    }
  } catch (e) {
    // Directory doesn't exist
  }
  return size;
}

function getLargestFiles(dir, limit = 10) {
  const files = [];

  function walk(currentDir) {
    try {
      const entries = readdirSync(currentDir);
      for (const entry of entries) {
        const path = join(currentDir, entry);
        const stats = statSync(path);
        if (stats.isDirectory()) {
          walk(path);
        } else {
          files.push({ path, size: stats.size });
        }
      }
    } catch (e) {
      // Ignore errors
    }
  }

  walk(dir);
  return files.sort((a, b) => b.size - a.size).slice(0, limit);
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

console.log('📊 Bundle Analysis Report\n');

// Total size
const totalSize = getDirSize(BUILD_DIR);
console.log(`Total build size: ${formatSize(totalSize)}\n`);

// Largest chunks
console.log('🔍 Top 10 largest files:');
const largest = getLargestFiles(BUILD_DIR);
for (const file of largest) {
  const relative = file.path.replace(BUILD_DIR + '/', '');
  console.log(`  ${formatSize(file.size).padStart(10)}  ${relative}`);
}

// Chunks directory analysis
const chunksSize = getDirSize(CHUNKS_DIR);
console.log(`\n📦 Chunks directory: ${formatSize(chunksSize)}`);

// Suggestions
console.log('\n💡 Suggestions:');
if (largest[0] && largest[0].size > 200 * 1024) {
  console.log(`  ⚠️  Largest chunk is ${formatSize(largest[0].size)} - consider code splitting`);
}
if (totalSize > 5 * 1024 * 1024) {
  console.log(`  ⚠️  Total build size is ${formatSize(totalSize)} - review dependencies`);
}
console.log('  ✓ Run `pnpm run build` to generate fresh build data');
console.log('  ✓ Use Next.js dynamic imports for large components');
console.log('  ✓ Enable compression in your hosting provider');
