"use client";

/**
 * SetHtmlLang
 * ------------
 * Static export (`output: "export"`) means every page is pre-rendered, so we
 * cannot read the `?lang=` query parameter server-side and emit the right
 * `<html lang="...">` per request. This tiny client component runs as soon as
 * the page is parsed and synchronises `document.documentElement.lang` with
 * the value the user picked via the language switcher.
 *
 * It also re-runs on `popstate` (browser back/forward) and on a custom
 * `nethub:langchange` event that the language switcher dispatches after a
 * `history.replaceState`, so navigation between pages stays consistent.
 *
 * Falls back to `navigator.language` on first visit, then to `en`.
 */
import { useEffect } from "react";

const SUPPORTED = ["en", "zh", "ja"] as const;
type Supported = (typeof SUPPORTED)[number];

function resolveLang(): Supported {
  if (typeof window === "undefined") return "en";
  try {
    const url = new URL(window.location.href);
    const fromQuery = url.searchParams.get("lang");
    if (fromQuery && (SUPPORTED as readonly string[]).includes(fromQuery)) {
      return fromQuery as Supported;
    }
  } catch {
    /* ignore */
  }
  const stored = window.localStorage?.getItem("nethub.lang");
  if (stored && (SUPPORTED as readonly string[]).includes(stored)) {
    return stored as Supported;
  }
  const browser = window.navigator?.language?.toLowerCase() ?? "";
  if (browser.startsWith("zh")) return "zh";
  if (browser.startsWith("ja")) return "ja";
  return "en";
}

export function SetHtmlLang() {
  useEffect(() => {
    const apply = () => {
      const lang = resolveLang();
      if (document.documentElement.lang !== lang) {
        document.documentElement.lang = lang;
      }
    };
    apply();
    window.addEventListener("popstate", apply);
    window.addEventListener("nethub:langchange", apply as EventListener);
    return () => {
      window.removeEventListener("popstate", apply);
      window.removeEventListener("nethub:langchange", apply as EventListener);
    };
  }, []);
  return null;
}

export default SetHtmlLang;
