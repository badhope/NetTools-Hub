'use client';

import { useEffect } from 'react';
import { LANG_HTML_LANG } from '@/lib/i18n';
import { useClientLang } from '@/lib/use-client-lang';

/**
 * Keeps `<html lang>` in sync with the client-side language state.
 *
 * The static export prerenders the document with `<html lang="en">`
 * (see `app/layout.tsx`); the real language is resolved post-mount
 * by `useClientLang`, and we mirror that into `document.documentElement.lang`
 * here so assistive tech and the browser's hyphenation engine pick
 * the right language *immediately* after hydration, without waiting
 * for the next user interaction.
 *
 * `tabIndex={-1}` is *not* on this element; the actual skip-link
 * target is the `<main id="main">` deeper in the tree, and giving
 * `<html>` a tab stop would make Tab from the URL bar focus the
 * invisible language attribute before anything useful.
 */
export function SetHtmlLang() {
  const [lang] = useClientLang();
  useEffect(() => {
    document.documentElement.lang = LANG_HTML_LANG[lang];
  }, [lang]);
  return null;
}
