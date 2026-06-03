"use client";

import { useState, useEffect, useRef } from "react";
import { Lang, LANG_OPTIONS } from "@/lib/i18n";

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
        className="inline-flex h-10 items-center gap-1.5 rounded-lg border border-[#30363d] bg-[#161b22] px-3 text-sm text-[#8b949e] transition-colors hover:border-[#58a6ff] hover:text-[#e6edf3]"
        aria-label="Switch language"
        aria-expanded={open}
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <circle cx="12" cy="12" r="9" />
          <path d="M3 12h18M12 3a14 14 0 010 18M12 3a14 14 0 000 18" />
        </svg>
        <span className="hidden sm:inline">{current.label}</span>
        <svg
          className={`h-3 w-3 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 min-w-[140px] overflow-hidden rounded-xl border border-[#30363d] bg-[#0d1117] p-1 shadow-2xl shadow-black/40">
          {LANG_OPTIONS.map((opt) => {
            const active = opt.value === lang;
            return (
              <button
                key={opt.value}
                onClick={() => {
                  onChange?.(opt.value);
                  setOpen(false);
                }}
                className={`flex w-full items-center justify-between gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  active
                    ? "bg-[#161b22] text-[#58a6ff]"
                    : "text-[#8b949e] hover:bg-[#161b22] hover:text-[#e6edf3]"
                }`}
              >
                <span>{opt.label}</span>
                {active && (
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
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
