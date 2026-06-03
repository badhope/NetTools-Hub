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

/**
 * Format the cumulative-stars number for the landing-page hero.
 *
 * English uses Western compact notation ("1.2M"); Chinese and
 * Japanese read more naturally in their native unit ("120万"),
 * which the CLDR `compact` notation does *not* emit for `zh` / `ja`
 * (it still picks the Latin "M" / "k" suffixes). We hand-format
 * the East-Asian variant in the locale-specific script to keep the
 * editorial tone consistent across languages.
 */
export function formatTotalStars(num: number, lang: Lang = "en"): string {
  if (lang === "zh" || lang === "ja") {
    // 1_000_000 → 100万 (one million, in the CJK unit convention).
    // We render an integer when the division is exact and one
    // decimal otherwise (e.g. 1.4万 for 14_000).
    if (num >= 10_000) {
      const v = num / 10_000;
      const text = Number.isInteger(v) ? v.toString() : v.toFixed(1);
      return `${text}万`;
    }
    if (num >= 1_000) {
      const v = num / 1_000;
      const text = Number.isInteger(v) ? v.toString() : v.toFixed(1);
      return `${text}千`;
    }
    return num.toString();
  }
  return formatNumber(num, lang);
}
