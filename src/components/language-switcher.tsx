'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { Lang, LANG_OPTIONS, t } from '@/lib/i18n';
import { useLang } from '@/components/lang-provider';

/**
 * Look up the listbox index of a given language. The two callers
 * (the lazy `useState` initializer in `LanguageSwitcher` and the
 * trigger-key handler that re-opens the listbox) need the same
 * `-1 → 0` clamp, and a previous pass had two subtly different
 * inline expressions (one `Math.max(0, findIndex(...))`, one
 * `findIndex(...) ?? 0` — the second was actually wrong because
 * `findIndex` returns `number`, not `number | undefined`, so `??`
 * never fired). Centralising here is one search-replace away from
 * a future fix.
 */
function highlightForLang(target: Lang): number {
  const idx = LANG_OPTIONS.findIndex((o) => o.value === target);
  return idx >= 0 ? idx : 0;
}

interface LanguageSwitcherProps {
  lang?: Lang;
  onChange?: ((lang: Lang) => void) | undefined;
}

/**
 * WAI-ARIA listbox pattern (`role="listbox"`).
 *
 * Keyboard contract:
 *  - `Enter` / `Space` / `ArrowDown` on the trigger: open the listbox
 *    and move focus to the *currently selected* option.
 *  - `ArrowDown` / `ArrowUp` inside the listbox: cycle through
 *    options, wrapping at the ends.
 *  - `Home` / `End`: jump to the first / last option.
 *  - `Enter` / `Space` inside the listbox: select the focused option
 *    and close.
 *  - `Escape` inside the listbox: close and return focus to the
 *    trigger without changing the language.
 *  - Click outside: close (no focus change).
 *
 * The visual styling is unchanged from the previous implementation;
 * this rewrite only adds the keyboard layer and the ARIA semantics
 * that screen readers (NVDA, VoiceOver, JAWS) need to expose the
 * widget as a listbox rather than as a bare cluster of buttons.
 *
 * If the caller does not pass an explicit `lang` / `onChange` pair,
 * the switcher falls back to the global `LangProvider` context so
 * the change propagates to every other component on the page.
 */
export function LanguageSwitcher(props: LanguageSwitcherProps) {
  const ctx = useLang();
  const lang = props.lang ?? ctx.lang;
  const onChange = props.onChange ?? ctx.setLang;
  const [open, setOpen] = useState(false);
  // The *visual* highlight index is separate from the *selected*
  // language: the user can arrow-key through options without having
  // committed to one yet. Committing happens on Enter/Space/click.
  // Initialise to the currently-selected language so re-opening the
  // menu lands on whatever they last picked — matching the
  // behaviour of every native `<select>`.
  //
  // Lifted out of the lazy initializer below to keep the function
  // body tiny and to share the same clamp logic with the
  // trigger-key handler in `onTriggerKey`.
  const [highlight, setHighlight] = useState<number>(() => highlightForLang(lang));
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const optionRefs = useRef<(HTMLButtonElement | null)[]>([]);

  // LANG_OPTIONS is a module-level constant and always has at least
  // one element (en, zh, ja) — the `!` documents that invariant;
  // under noUncheckedIndexedAccess, `LANG_OPTIONS[0]` would otherwise
  // be `{ value, label } | undefined`.
  const current = LANG_OPTIONS.find((o) => o.value === lang) ?? LANG_OPTIONS[0]!;

  const close = useCallback((returnFocus = false) => {
    setOpen(false);
    if (returnFocus) triggerRef.current?.focus();
  }, []);

  const select = useCallback(
    (value: Lang) => {
      onChange?.(value);
      close(true);
    },
    [onChange, close],
  );

  // Click-outside closes the menu without disturbing focus. We
  // intentionally do *not* return focus to the trigger on click-out
  // (that would be jarring — the user clicked somewhere else on
  // purpose). Escape is the keyboard equivalent of the same intent
  // but, per the listbox spec, *does* return focus to the trigger.
  useEffect(() => {
    if (!open) return;
    // `pointerdown` covers both mouse and touch in one event
    // (mousedown is deprecated on iOS Safari 13+ and is the
    // documented "click outside" pattern in the Pointer Events
    // spec). We listen on the document, not the container, so
    // taps on any element outside the menu dismiss it.
    const onPointer = (e: PointerEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('pointerdown', onPointer);
    return () => document.removeEventListener('pointerdown', onPointer);
  }, [open]);

  // Whenever the listbox opens, focus the highlighted option. The
  // highlight is initialised to the currently-selected language, so a
  // user re-opening the menu lands on whatever they last picked —
  // matching the behaviour of every native `<select>`.
  useEffect(() => {
    if (!open) return;
    optionRefs.current[highlight]?.focus();
    // We only want to re-focus on the *open* transition, not every
    // time `highlight` changes while the menu is open (that would
    // re-focus the option under the user's cursor and feel "stuck").
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const onTriggerKey = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setHighlight(highlightForLang(lang));
      setOpen(true);
    }
  };

  const onListKey = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const last = LANG_OPTIONS.length - 1;
    const move = (next: number) => {
      e.preventDefault();
      const wrapped = (next + LANG_OPTIONS.length) % LANG_OPTIONS.length;
      setHighlight(wrapped);
      optionRefs.current[wrapped]?.focus();
    };
    switch (e.key) {
      case 'ArrowDown':
        move(highlight + 1);
        return;
      case 'ArrowUp':
        move(highlight - 1);
        return;
      case 'Home':
        move(0);
        return;
      case 'End':
        move(last);
        return;
      case 'Escape':
        e.preventDefault();
        close(true);
        return;
      case 'Tab':
        // Tabbing away from the menu closes it but does NOT return
        // focus to the trigger — the user is moving on, and the
        // browser is already taking focus wherever they intended.
        setOpen(false);
        return;
      default:
        return;
    }
  };

  return (
    <div ref={containerRef} className="relative">
      <button
        ref={triggerRef}
        type="button"
        onClick={() => setOpen((v) => !v)}
        onKeyDown={onTriggerKey}
        className="inline-flex h-9 items-center gap-1.5 border border-dim px-3 font-mono text-[11px] uppercase tracking-[0.18em] text-fg-2 transition-colors hover:border-accent hover:text-accent"
        aria-label={t(lang, 'nav.switch_language')}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span>{current.label}</span>
        <svg
          className={`h-3 w-3 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
          aria-hidden
        >
          <path strokeLinecap="square" strokeLinejoin="miter" d="M6 9l6 6 6-6" />
        </svg>
      </button>

      {open && (
        <div
          role="listbox"
          aria-label={t(lang, 'nav.switch_language')}
          // `LANG_OPTIONS[highlight]!` — the invariant that
          // `0 <= highlight < LANG_OPTIONS.length` is maintained
          // by the `move()` and `highlightForLang()` helpers, and
          // the type-narrowing `!` documents it explicitly for
          // `noUncheckedIndexedAccess`. (The previous version
          // used `?? "en"` as a defensive fallback, but the only
          // way `highlight` is out of range is a bug in this
          // file, in which case the wrong value is no better than
          // crashing loudly during development.)
          aria-activedescendant={`lang-opt-${LANG_OPTIONS[highlight]!.value}`}
          onKeyDown={onListKey}
          className="absolute right-0 top-full z-50 mt-2 min-w-[160px] border border-line bg-bg-elev p-1 shadow-xl"
        >
          {LANG_OPTIONS.map((opt, idx) => {
            const active = opt.value === lang;
            const focused = idx === highlight;
            return (
              <button
                key={opt.value}
                id={`lang-opt-${opt.value}`}
                ref={(el) => {
                  optionRefs.current[idx] = el;
                }}
                type="button"
                role="option"
                aria-selected={active}
                tabIndex={focused ? 0 : -1}
                onMouseEnter={() => setHighlight(idx)}
                onClick={() => select(opt.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    select(opt.value);
                  }
                }}
                className={`flex w-full items-center justify-between gap-3 px-3 py-2 text-left font-mono text-[11px] uppercase tracking-[0.18em] transition-colors ${
                  active
                    ? 'text-accent'
                    : focused
                      ? 'bg-bg-sunk text-fg'
                      : 'text-fg-2 hover:bg-bg-sunk hover:text-fg'
                }`}
              >
                <span>{opt.label}</span>
                {active && (
                  <svg
                    className="h-3 w-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                    aria-hidden
                  >
                    <path strokeLinecap="square" d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
