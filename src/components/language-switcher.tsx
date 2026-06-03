"use client";

import { useState, useEffect, useRef } from "react";
import { Lang, LANG_OPTIONS, t } from "@/lib/i18n";

interface LanguageSwitcherProps {
  lang: Lang;
  onChange?: (lang: Lang) => void;
}

export function LanguageSwitcher({ lang, onChange }: LanguageSwitcherProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  // LANG_OPTIONS is a module-level constant and always has at least one
  // element (en, zh, ja) — the `!` documents that invariant; under
  // noUncheckedIndexedAccess, `LANG_OPTIONS[0]` would otherwise be
  // `{ value, label } | undefined`.
  const current =
    LANG_OPTIONS.find((o) => o.value === lang) ?? LANG_OPTIONS[0]!;

  useEffect(() => {
    if (!open) return;
    const onClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="inline-flex h-9 items-center gap-1.5 border border-dim px-3 font-mono text-[11px] uppercase tracking-[0.18em] text-fg-2 transition-colors hover:border-accent hover:text-accent"
        aria-label={t(lang, "nav.switch_language")}
        aria-expanded={open}
      >
        <span>{current.label}</span>
        <svg
          className={`h-3 w-3 transition-transform duration-200 ${
            open ? "rotate-180" : ""
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="square"
            strokeLinejoin="miter"
            d="M6 9l6 6 6-6"
          />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 min-w-[160px] border border-line bg-bg-elev p-1 shadow-xl">
          {LANG_OPTIONS.map((opt) => {
            const active = opt.value === lang;
            return (
              <button
                key={opt.value}
                onClick={() => {
                  onChange?.(opt.value);
                  setOpen(false);
                }}
                className={`flex w-full items-center justify-between gap-3 px-3 py-2 text-left font-mono text-[11px] uppercase tracking-[0.18em] transition-colors ${
                  active
                    ? "text-accent"
                    : "text-fg-2 hover:bg-bg-sunk hover:text-fg"
                }`}
              >
                <span>{opt.label}</span>
                {active && (
                  <svg
                    className="h-3 w-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="square"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
