"use client";

import { t, Lang } from "@/lib/i18n";
import { SortOption } from "@/types/project";

interface SortSelectProps {
  value: SortOption;
  onChange: (value: SortOption) => void;
  lang: Lang;
}

export function SortSelect({ value, onChange, lang }: SortSelectProps) {
  return (
    // `relative` is required so the chevron can be absolutely
    // positioned without a `positioned ancestor` hop. The wrapper
    // itself is not styled beyond that — the visible chrome lives
    // on the native `<select>` for the widest possible browser
    // / OS support (mobile sheets, keyboard arrow nav, screen
    // reader virtual cursors all keep working without any custom
    // popover).
    <div className="relative inline-block">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as SortOption)}
        // `appearance-none` is what lets us draw the chevron
        // ourselves; padding-right is sized so the longest label
        // (e.g. "🕐 Updated" in EN) still leaves room for it. The
        // `cursor-pointer` is a small touch affordance — the
        // native select chevron on Firefox still appears on
        // hover, but the cursor hints that the whole pill is
        // clickable.
        className="h-[38px] cursor-pointer appearance-none border border-dim bg-transparent py-2 pl-3 pr-9 font-mono text-[11px] uppercase tracking-[0.18em] text-fg-2 transition-colors focus:border-accent focus:text-fg focus:outline-none hover:border-accent/60"
        aria-label={t(lang, "sort.aria_label")}
      >
        <option value="default">{t(lang, "sort.default")}</option>
        <option value="stars">{t(lang, "sort.stars")}</option>
        <option value="name">{t(lang, "sort.name")}</option>
        <option value="updated">{t(lang, "sort.updated")}</option>
      </select>
      {/* Chevron: classic caret, slightly larger (3.5px) and
       *  centered in its 38px-tall parent. `text-muted` keeps it
       *  visually subordinate to the label, and `pointer-events-none`
       *  ensures clicks pass through to the underlying `<select>`. */}
      <svg
        aria-hidden
        className="pointer-events-none absolute right-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.75}
      >
        <path strokeLinecap="square" d="M6 9l6 6 6-6" />
      </svg>
    </div>
  );
}
