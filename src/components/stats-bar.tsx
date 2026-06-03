"use client";

import { t, Lang } from "@/lib/i18n";

interface StatsBarProps {
  projectCount: number;
  categoryCount: number;
  totalStars: number;
  lang: Lang;
}

interface StatProps {
  label: string;
  value: string;
  unit?: string;
}

function Stat({ label, value, unit }: StatProps) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
        {label}
      </span>
      <span className="font-display text-lg leading-none text-fg">
        {value}
        {unit && <span className="ml-0.5 text-sm text-fg-2">{unit}</span>}
      </span>
    </div>
  );
}

export function StatsBar({ projectCount, categoryCount, totalStars, lang }: StatsBarProps) {
  return (
    <div
      className="flex flex-wrap items-end gap-x-8 gap-y-3"
      role="status"
      aria-label={`${t(lang, "stats.projects")} · ${t(lang, "stats.categories")} · ${t(lang, "stats.total_stars")}`}
    >
      <Stat
        label={t(lang, "stats.projects")}
        value={String(projectCount)}
      />
      <Stat
        label={t(lang, "stats.categories")}
        value={String(categoryCount)}
      />
      <div className="hidden sm:block">
        <Stat
          label={t(lang, "stats.total_stars")}
          value={(totalStars / 1000000).toFixed(1)}
          unit="M"
        />
      </div>
    </div>
  );
}
