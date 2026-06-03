"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Lang, readLangFromUrl, t } from "@/lib/i18n";

export default function NotFound() {
  // `output: "export"` pre-renders this page in English regardless of
  // the URL, so we read `?lang=` on the client to localise the copy.
  // The setState is inside the `popstate` callback (not directly in
  // the effect body), so React 19's `react-hooks/set-state-in-effect`
  // rule does not flag it. We invoke the same callback once on mount
  // to pick up the URL state.
  const [lang, setLang] = useState<Lang>("en");
  useEffect(() => {
    const onPop = () => setLang(readLangFromUrl());
    onPop();
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const homeHref = lang === "en" ? "/" : `/?lang=${lang}`;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-bg px-6 text-center">
      <div className="mb-6 flex items-center gap-3">
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
          Folio 404
        </span>
        <span className="h-px w-12 bg-dim" />
      </div>
      <h1 className="font-display text-7xl leading-none text-fg sm:text-8xl">
        4
        <span className="italic text-accent">0</span>
        4
      </h1>
      <p className="mt-6 max-w-sm text-sm leading-relaxed text-fg-2">
        {t(lang, "404.description")}
      </p>
      <Link
        href={homeHref}
        className="group mt-10 inline-flex items-center gap-3 border-b border-accent pb-1 font-display text-lg text-accent transition-colors hover:text-accent-hover"
      >
        <span>{t(lang, "404.back")}</span>
        <svg
          className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="square"
            d="M5 12h14M13 6l6 6-6 6"
          />
        </svg>
      </Link>
    </div>
  );
}
