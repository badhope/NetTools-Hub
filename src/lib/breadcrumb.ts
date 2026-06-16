// ============================================================================
// Breadcrumb helpers — server-callable constructors
// ============================================================================
//
// These are pure-data helpers that produce `Crumb` objects. They live in a
// server-compatible file (no `'use client'`) so that server components
// (the `/explore/*` pages) can call them at render time. The `Breadcrumb`
// component itself consumes the resulting array and re-renders with the
// active language from the client-side `LangProvider` context.
// ============================================================================

import type { Lang } from './i18n';
import { t } from './i18n';
import { kindLabel, platformLabel } from './taxonomy';

export interface Crumb {
  label: string;
  href?: string;
}

/** Convenience constructor: the `explore` root crumb. */
export function rootCrumb(lang: Lang): Crumb {
  return { label: t(lang, 'breadcrumb.root'), href: '/explore' };
}

/** Convenience: kind crumb. */
export function kindCrumb(lang: Lang, kind: string): Crumb {
  return {
    label: `${kindLabel(kind as never, lang)} (${kind})`,
    href: `/explore/k/${kind}`,
  };
}

/** Convenience: platform crumb (last, no link). */
export function platformCrumb(lang: Lang, kind: string, platform: string): Crumb {
  return {
    label: `${platformLabel(platform as never, lang)} (${platform})`,
  };
}
