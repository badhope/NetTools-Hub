import type { Lang } from '@/lib/i18n';

/**
 * Serialise a JSON-LD payload for inline `<script type="application/ld+json">`
 * injection.
 *
 * `JSON.stringify` does NOT escape `<`, `>`, or `&`, so a project
 * description that contained `</script><script>alert(1)</script>`
 * (e.g. pasted by a contributor editing `data/projects.json`) would
 * break out of the JSON-LD `<script>` context. This helper is the
 * standard mitigation: emit the offending characters as their
 * `\uXXXX` escape form, which `JSON.parse` decodes back to the
 * original byte sequence when crawlers read the page.
 *
 * (We deliberately do not also escape U+2028 / U+2029. They used
 * to be a parse hazard in pre-ES2019 `JSON.parse`, but every
 * modern search-engine crawler ships with a current V8, so the
 * two extra `replace` passes would just be cargo-cult code.)
 */
export function safeJsonLd(payload: unknown): string {
  return JSON.stringify(payload)
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e')
    .replace(/&/g, '\\u0026');
}

/**
 * Compact a number for display: 999 → "999", 1_500 → "1.5k",
 * 999_500 → "1.0M", 2_440_390 → "2.4M".
 *
 * Uses `Intl.NumberFormat` with `notation: "compact"` so that the
 * `k`/`M` thresholds are picked by the platform's own CLDR data
 * (no hand-rolled rounding bug at the `999.5k` boundary).
 */
export function formatNumber(num: number, lang: Lang = 'en'): string {
  try {
    return new Intl.NumberFormat(lang, {
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(num);
  } catch {
    // Older runtimes may not support compact notation. Fall back
    // to a hand-rolled formatter that is at least correct at the
    // boundary (round *before* formatting so 999_500 → 1M, not
    // 1000.0k).
    if (num >= 999_500) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_500) return `${(num / 1_000).toFixed(1)}k`;
    return num.toString();
  }
}

/**
 * Format star count for display: 999 → "999", 1_500 → "1.5K",
 * 1_500_000 → "1.5M".
 */
export function formatStars(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}
