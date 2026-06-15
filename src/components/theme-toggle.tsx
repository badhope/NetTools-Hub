'use client';

import { useSyncExternalStore, useCallback, useEffect } from 'react';

const STORAGE_KEY = 'theme';
type Theme = 'dark' | 'light';

function getSnapshot(): Theme {
  return (localStorage.getItem(STORAGE_KEY) as Theme) || 'dark';
}

/**
 * The server snapshot always returns 'dark' so the SSR output is
 * deterministic. After hydration `useSyncExternalStore` swaps to
 * the real `getSnapshot` and re-renders if the local value differs.
 */
function getServerSnapshot(): Theme {
  return 'dark';
}

/**
 * Listen for changes from *other* tabs and from our own toggle.
 * `useSyncExternalStore` calls `subscribe` once per mount and
 * invokes the listener whenever the snapshot might have changed.
 */
function subscribe(callback: () => void): () => void {
  const onStorage = (e: StorageEvent) => {
    if (e.key === STORAGE_KEY) callback();
  };
  window.addEventListener('storage', onStorage);
  return () => window.removeEventListener('storage', onStorage);
}

/**
 * Theme toggle with proper hydration handling.
 *
 * `useSyncExternalStore` is the canonical pattern for
 * "read-from-DOM/localStorage-on-client, deterministic-on-server":
 * the server snapshot is always 'dark' (matching the SSR markup),
 * and the client snapshot is the localStorage value. React itself
 * handles the hydration mismatch, so we never need a setState-in-
 * effect to bridge the two.
 */
export function ThemeToggle() {
  const theme = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  // Keep <html data-theme=…> in sync. The setter only runs on the
  // client (this component is gated by `mounted` in the parent
  // layout, see `top-nav.tsx`) and is a no-op when the attribute
  // is already correct, so it does not produce cascading renders.
  useEffect(() => {
    if (document.documentElement.getAttribute('data-theme') !== theme) {
      document.documentElement.setAttribute('data-theme', theme);
    }
  }, [theme]);

  const toggle = useCallback(() => {
    const next: Theme = theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem(STORAGE_KEY, next);
    document.documentElement.setAttribute('data-theme', next);
    // Notify our own store (storage events don't fire in the
    // originating tab) so `getSnapshot` re-runs and React re-renders.
    window.dispatchEvent(new StorageEvent('storage', { key: STORAGE_KEY }));
  }, [theme]);

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
