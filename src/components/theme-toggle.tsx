'use client';

import { useEffect, useState, useCallback } from 'react';

/**
 * Theme toggle with proper hydration handling.
 *
 * The initial state is always 'dark' (matching the server-rendered HTML),
 * then we read localStorage in a useEffect and update if needed. This
 * prevents hydration mismatch errors when the user has previously selected
 * a different theme.
 */
export function ThemeToggle() {
  // Start with 'dark' to match SSR output exactly
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [mounted, setMounted] = useState(false);

  // After hydration, read the real theme from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('theme') as 'dark' | 'light' | null;
    const initial = stored || 'dark';
    setTheme(initial);
    document.documentElement.setAttribute('data-theme', initial);
    setMounted(true);
  }, []);

  // Update document attribute when theme changes
  useEffect(() => {
    if (mounted) {
      document.documentElement.setAttribute('data-theme', theme);
    }
  }, [theme, mounted]);

  const toggle = useCallback(() => {
    setTheme((prev) => {
      const next = prev === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', next);
      return next;
    });
  }, []);

  return (
    <button
      onClick={toggle}
      className="flex items-center gap-2 px-3 py-1.5 text-sm text-muted hover:text-fg transition-colors focus:outline-none focus:ring-2 focus:ring-accent/50"
      aria-label={theme === 'dark' ? '切换到亮色模式' : '切换到暗色模式'}
    >
      {theme === 'dark' ? (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        >
          <circle cx="8" cy="8" r="4" />
          <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.5 3.5l1.4 1.4M11.1 11.1l1.4 1.4M3.5 12.5l1.4-1.4M11.1 4.9l1.4-1.4" />
        </svg>
      ) : (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        >
          <path d="M13.5 8.5a5.5 5.5 0 1 1-6-6 4 4 0 0 0 6 6z" />
        </svg>
      )}
      <span className="font-mono text-xs uppercase tracking-wider">
        {theme === 'dark' ? '暗色' : '亮色'}
      </span>
    </button>
  );
}
