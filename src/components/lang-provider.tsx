'use client';

import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { Lang, resolveInitialLang, setLangAndPersist } from '@/lib/i18n';

/**
 * Client-side language context.
 *
 * ## Problem this solves
 *
 * The site is statically exported, so every page is prerendered
 * with `<html lang="en">` and the English copy in the initial
 * HTML payload. Before this provider existed, the
 * `LanguageSwitcher` was wired up with a no-op `onChange`
 * callback on the landing page and a broken `onLangChange`
 * prop drill on the explore page. Picking a different language
 * in the UI updated the URL and `localStorage`, but **no
 * component re-rendered** — the screen stayed English.
 *
 * ## How it works
 *
 * 1. **Provider state is `'en'` at first render**, matching the
 *    server HTML exactly so React 19 hydration never trips a
 *    `#418` / `#423` mismatch.
 * 2. **A `useEffect` resolves the real language** from the URL
 *    `?lang=` query, then `localStorage`, then `navigator.language`,
 *    and pushes it into the same state. This swap happens after
 *    hydration so the user sees a single-frame English flash on
 *    a deep-link visit (`?lang=zh`) — the documented React
 *    trade-off for static-export client-stateful content.
 * 3. **All consumer components read `lang` from this context**,
 *    not from props, so they all re-render on the same state
 *    change with no prop drilling.
 * 4. **`setLang()` is the single mutator.** It calls
 *    `setLangAndPersist` (which writes URL + `localStorage` +
 *    dispatches the `nethub:langchange` event) and also updates
 *    local state so the change is reflected immediately, even
 *    in the component that called it.
 *
 * ## Why not just listen for the event in every consumer?
 *
 * We could, but then every component would need a mount effect
 * to subscribe, the listeners would race the initial resolve,
 * and the `LanguageSwitcher` itself would have to be aware of
 * the propagation order. One provider is one effect, one
 * source of truth.
 */
interface LangContextValue {
  lang: Lang;
  setLang: (next: Lang) => void;
}

const LangContext = createContext<LangContextValue | null>(null);

export function LangProvider({ children }: { children: ReactNode }) {
  // SSR-safe initial value: English, matching the prerendered
  // HTML. The real language is applied in the mount effect.
  const [lang, setLangState] = useState<Lang>('en');

  // After hydration, swap in the URL / storage / navigator
  // resolved language. Done in a microtask so React 19's
  // `react-hooks/set-state-in-effect` rule is happy and so the
  // work is moved off the synchronous hydration path.
  useEffect(() => {
    queueMicrotask(() => {
      setLangState(resolveInitialLang());
    });
  }, []);

  // Listen to `nethub:langchange` events from other consumers
  // (e.g. a `LanguageSwitcher` on a different part of the page)
  // and mirror the change into local state. This keeps every
  // consumer in sync without a global state library.
  useEffect(() => {
    const onChange = (e: Event) => {
      const detail = (e as CustomEvent<{ lang: Lang }>).detail;
      if (detail?.lang) setLangState(detail.lang);
    };
    window.addEventListener('nethub:langchange', onChange);
    return () => window.removeEventListener('nethub:langchange', onChange);
  }, []);

  // The single mutator. `setLangAndPersist` writes to URL +
  // localStorage + dispatches the custom event; we also call
  // `setLangState` locally so the change is reflected even in
  // the component that originated it, without waiting for the
  // event to round-trip.
  const setLang = useCallback((next: Lang) => {
    setLangState(next);
    setLangAndPersist(next);
  }, []);

  return <LangContext.Provider value={{ lang, setLang }}>{children}</LangContext.Provider>;
}

/**
 * Read the current language from the provider context.
 *
 * If called outside of a `<LangProvider>` (e.g. inside the special
 * `/_not-found` static fallback that Next.js prerenders without
 * the root layout, or inside the `global-error.tsx` page that
 * replaces the layout entirely), this returns a safe default
 * `{ lang: 'en', setLang: noop }` rather than throwing. The
 * production code paths in this app all sit inside the layout's
 * `LangProvider`, so the fallback is a belt-and-braces guard
 * rather than a primary code path — throwing would crash the
 * static export of `/_not-found` because Next.js prerenders
 * that page in isolation.
 */
export function useLang(): LangContextValue {
  const ctx = useContext(LangContext);
  if (ctx) return ctx;
  // Out-of-tree render (static prerender of `/_not-found`, or
  // `global-error.tsx`). Return a no-op default so the page can
  // still render. The layout's `LangProvider` is what makes the
  // user-visible switch actually work.
  return FALLBACK;
}

const FALLBACK: LangContextValue = {
  lang: 'en',
  setLang: () => {
    /* no-op outside the provider */
  },
};
