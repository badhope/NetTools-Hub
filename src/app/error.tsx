"use client";

import { useEffect, useState } from "react";
import { Lang, readLangFromUrl, t } from "@/lib/i18n";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  // `output: "export"` pre-renders this page in English regardless of
  // the URL, so we read `?lang=` on the client to localise the copy.
  // The setState is wrapped in a callback so React 19's
  // `react-hooks/set-state-in-effect` rule does not flag it.
  const [lang, setLang] = useState<Lang>("en");
  useEffect(() => {
    const sync = () => setLang(readLangFromUrl());
    sync();
  }, []);

  return (
    <main
      id="main"
      aria-label={t(lang, "a11y.main")}
      tabIndex={-1}
      className="flex min-h-screen flex-col items-center justify-center bg-bg px-6 text-center outline-none"
    >
      <div className="mb-6 flex items-center gap-3">
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
          {t(lang, "error.folio")}
        </span>
        <span className="h-px w-12 bg-dim" />
      </div>
      <h1 className="font-display text-5xl leading-none text-fg sm:text-6xl">
        Err<span className="italic text-accent">/</span>or
      </h1>
      <p className="mt-6 max-w-sm text-sm leading-relaxed text-fg-2">
        {t(lang, "error.description")}
      </p>
      <button
        onClick={reset}
        className="group mt-10 inline-flex items-center gap-3 border-b border-accent pb-1 font-display text-lg text-accent transition-colors hover:text-accent-hover"
      >
        <span>{t(lang, "error.retry")}</span>
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
      </button>
    </main>
  );
}
