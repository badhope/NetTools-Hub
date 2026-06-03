"use client";

import { useState, useRef, useEffect } from "react";
import { t, Lang } from "@/lib/i18n";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  lang: Lang;
}

export function SearchBar({ value, onChange, lang }: SearchBarProps) {
  const [inputValue, setInputValue] = useState(value);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync local input state with the parent's debounced value. The two-way
  // mirror (parent.value → inputValue via useEffect, inputValue → parent
  // via debounced onChange) is the standard pattern for a debounced
  // controlled input: the input must update on every keystroke (otherwise
  // the user sees the input lag behind their typing) while the parent
  // state lags by 300ms for the actual search filter.
  //
  // React 19's `react-hooks/set-state-in-effect` rule would normally flag
  // the setInputValue call below, but in this case the cascade is bounded
  // — the useEffect only fires when `value` actually changes (via the
  // exhaustive-deps array), and setting inputValue to a string-equal
  // value is a no-op in React. The standard escape hatch is to disable
  // the rule for this single setState call; the comment above documents
  // why.
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    setInputValue(value);
  }, [value]);
  /* eslint-enable react-hooks/set-state-in-effect */

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const handleInput = (next: string) => {
    setInputValue(next);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => onChange(next), 300);
  };

  return (
    <div className="relative w-full max-w-xs">
      <svg
        className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#6e7681]"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      <input
        type="text"
        value={inputValue}
        onChange={(e) => handleInput(e.target.value)}
        placeholder={t(lang, "search.placeholder")}
        className="w-full rounded-lg border border-[#30363d] bg-[#0d1117] py-2 pl-10 pr-8 text-sm text-[#e6edf3] placeholder:text-[#6e7681] focus:border-[#58a6ff] focus:outline-none focus:ring-1 focus:ring-[#58a6ff]"
        aria-label={t(lang, "search.aria_label")}
      />
      {inputValue && (
        <button
          onClick={() => handleInput("")}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-[#6e7681] hover:text-[#e6edf3]"
          aria-label={t(lang, "search.clear")}
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}
