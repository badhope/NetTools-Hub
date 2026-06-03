"use client";

import { useState, useRef, useEffect, useImperativeHandle, forwardRef } from "react";
import { t, Lang } from "@/lib/i18n";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  lang: Lang;
  shortcutHint: string;
}

export interface SearchBarHandle {
  focus: () => void;
}

export const SearchBar = forwardRef<SearchBarHandle, SearchBarProps>(function SearchBar(
  { value, onChange, lang, shortcutHint },
  ref,
) {
  const [inputValue, setInputValue] = useState(value);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Expose `focus()` to the parent so the global `/` shortcut in
  // explore-content can drive focus into the search box without
  // the search box having to know about the global keymap.
  useImperativeHandle(
    ref,
    () => ({
      focus: () => inputRef.current?.focus(),
    }),
    [],
  );

  // Sync local input state with the parent's debounced value. The two-way
  // mirror (parent.value → inputValue via useEffect, inputValue → parent
  // via debounced onChange) is the standard pattern for a debounced
  // controlled input: the input must update on every keystroke (otherwise
  // the user sees the input lag behind their typing) while the parent
  // state lags by 300ms for the actual search filter.
  useEffect(() => {
    setInputValue(value);
  }, [value]);

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

  // The `<kbd>` is a screen-reader-friendly hint that the input can
  // be reached with `/`. We render it inside the placeholder-area
  // only when the input is empty, so the user does not see both
  // placeholder text and a hint at the same time.
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
        ref={inputRef}
        type="search"
        value={inputValue}
        onChange={(e) => handleInput(e.target.value)}
        placeholder={t(lang, "search.placeholder")}
        className="w-full border border-dim bg-transparent py-2 pl-9 pr-8 font-sans text-sm text-fg placeholder:font-mono placeholder:text-[11px] placeholder:uppercase placeholder:tracking-[0.18em] placeholder:text-muted focus:border-accent focus:outline-none"
        aria-label={`${t(lang, "search.aria_label")} (${shortcutHint})`}
      />
      {!inputValue && (
        <kbd
          aria-hidden
          className="pointer-events-none absolute right-3 top-1/2 hidden -translate-y-1/2 rounded-sm border border-dim px-1.5 py-0.5 font-mono text-[10px] text-muted sm:inline"
        >
          /
        </kbd>
      )}
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
});
