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
    <div className="relative w-full sm:w-72">
      <svg
        className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.5}
      >
        <path
          strokeLinecap="square"
          d="M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z"
        />
        <path strokeLinecap="square" d="M21 21l-5-5" />
      </svg>
      <input
        type="search"
        value={inputValue}
        onChange={(e) => handleInput(e.target.value)}
        placeholder={t(lang, "search.placeholder")}
        className="w-full border border-dim bg-transparent py-2 pl-9 pr-8 font-sans text-sm text-fg placeholder:font-mono placeholder:text-[11px] placeholder:uppercase placeholder:tracking-[0.18em] placeholder:text-muted focus:border-accent focus:outline-none"
        aria-label={t(lang, "search.aria_label")}
      />
      {inputValue && (
        <button
          onClick={() => handleInput("")}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-muted hover:text-accent"
          aria-label={t(lang, "search.clear")}
        >
          <svg
            className="h-3.5 w-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="square"
              d="M6 6l12 12M18 6L6 18"
            />
          </svg>
        </button>
      )}
    </div>
  );
}
