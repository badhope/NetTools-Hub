"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  Lang,
  readLangFromUrl,
  resolveInitialLang,
  setLangAndPersist,
} from "@/lib/i18n";

/**
 * Client-only `Lang` state hook.
 *
 * ## Hydration contract
 *
 * The static export prerenders every page with `<html lang="en">` and
 * the English text (see `app/layout.tsx`). We do not know the user's
 * preferred language at build time, so the *client's first render*
 * (the one that runs during React's hydration phase) MUST agree with
 * the prerender or React 19 will throw error #418 / #423 ("text
 * content did not match" / "hydrating ...").
 *
 * The previous version used a lazy `useState<Lang>(() =>
 * resolveInitialLang())` initializer. That returned `"en"` on the
 * server (because `window` was undefined) but the *real* language on
 * the client's first render — a guaranteed hydration mismatch on
 * every deep-link visit (`?lang=zh`, `?lang=ja`).
 *
 * The correct shape is therefore:
 *   1. `useState<Lang>("en")` — the first client render matches the
 *      server HTML exactly.
 *   2. `useEffect(() => setLangState(resolveInitialLang()), [])` —
 *      after hydration, swap in the real language from URL →
 *      `localStorage` → `navigator`. The user sees a single-frame
 *      English flash, which is the documented React 19 trade-off
 *      for statically-rendered client-stateful content.
 *
 * ## Event coordination
 *
 * The hook also:
 *   - Listens to `popstate` so back/forward (`?lang=` rewrites via
 *     the browser history) updates the language without a remount.
 *   - Listens to `nethub:langchange` so any component that switches
 *     language via `setLangAndPersist` propagates the change to
 *     every other `useClientLang()` consumer on the page without
 *     prop-drilling.
 *
 * The two listeners are installed once on mount (empty dep array);
 * the listener bodies read the latest language through `langRef`
 * rather than the closure, so the listeners never need to be
 * re-attached when `lang` changes.
 */
export function useClientLang(): readonly [Lang, (next: Lang) => void] {
  // SSR-safe initial value: always English, matching the prerendered
  // HTML. The real language is applied in the mount effect below.
  const [lang, setLangState] = useState<Lang>("en");

  // Mirror `lang` into a ref so the mount-only event listeners can
  // read the latest value without re-subscribing on every change.
  const langRef = useRef<Lang>(lang);
  useEffect(() => {
    langRef.current = lang;
  }, [lang]);

  // One-time mount effect: apply the real language, then wire up
  // the two sources of subsequent language change (browser history
  // navigation, and the in-app `nethub:langchange` custom event).
  useEffect(() => {
    // 1) Apply the URL / storage / navigator-resolved language.
    //    `queueMicrotask` defers the `setLangState` to the next
    //    microtask tick so it is no longer *synchronous* with the
    //    effect body — the React 19 `react-hooks/set-state-in-effect`
    //    ESLint rule flags the synchronous form because it can
    //    cause a cascading render where the effect's own outcome
    //    (`resolveInitialLang()`) immediately schedules another
    //    re-render before the browser has painted. Wrapping the
    //    setState in a microtask keeps the rule happy *and* moves
    //    the work off the hydration path so it never blocks the
    //    first paint.
    queueMicrotask(() => {
      setLangState(resolveInitialLang());
    });

    // 2) `popstate` — back/forward in the browser history.
    const onPop = () => {
      const next = readLangFromUrl();
      if (next !== langRef.current) setLangState(next);
    };

    // 3) `nethub:langchange` — another `useClientLang` consumer
    //    called `setLangAndPersist` (e.g. the language switcher
    //    in the top nav). `setLangAndPersist` does the URL /
    //    storage / event triplet; we only need to mirror the
    //    result into local state.
    const onChange = (e: Event) => {
      const detail = (e as CustomEvent<{ lang: Lang }>).detail;
      if (detail?.lang && detail.lang !== langRef.current) {
        setLangState(detail.lang);
      }
    };

    window.addEventListener("popstate", onPop);
    window.addEventListener("nethub:langchange", onChange);
    return () => {
      window.removeEventListener("popstate", onPop);
      window.removeEventListener("nethub:langchange", onChange);
    };
  }, []);

  // UI-driven change. The local `setLangState(next)` is omitted
  // because `setLangAndPersist` dispatches `nethub:langchange`
  // which the listener above will pick up — doing both would just
  // schedule two identical updates.
  const setLangFromUi = useCallback((next: Lang) => {
    setLangAndPersist(next);
  }, []);

  return [lang, setLangFromUi] as const;
}
