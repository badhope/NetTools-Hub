import type { ProjectKind, ProjectPlatform } from '@/types/project';

// ============================================================================
// NetTools Hub — Shared constants
// ============================================================================
//
// Centralised definitions for the kind and platform orderings used
// throughout the UI. Previously these were duplicated in multiple
// components (landing-content.tsx, top-nav.tsx, tree-sidebar.tsx),
// which made it easy to accidentally change the order in one place
// but not the others.
// ============================================================================

/** Canonical ordering of project kinds for display. */
export const KIND_ORDER: readonly ProjectKind[] = [
  'proxy',
  'vpn',
  'dns',
  'acceleration',
  'security',
  'monitoring',
  'ops',
  'tools',
] as const;

/** Canonical ordering of platforms for display. */
export const PLATFORM_ORDER: readonly ProjectPlatform[] = [
  'desktop',
  'mobile',
  'cli',
  'server',
  'browser',
  'router',
] as const;
