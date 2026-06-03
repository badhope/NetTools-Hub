import type { Lang } from "@/lib/i18n";

/**
 * Compact a number for display: 999 → "999", 1_500 → "1.5k",
 * 999_500 → "1.0M", 2_440_390 → "2.4M".
 *
 * Uses `Intl.NumberFormat` with `notation: "compact"` so that the
 * `k`/`M` thresholds are picked by the platform's own CLDR data
 * (no hand-rolled rounding bug at the `999.5k` boundary).
 */
export function formatNumber(num: number, lang: Lang = "en"): string {
  try {
    return new Intl.NumberFormat(lang, {
      notation: "compact",
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
