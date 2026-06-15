'use client';

import { useSyncExternalStore, useCallback, useState } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

const DISMISS_KEY = 'pwa-install-dismissed';
const DISMISS_DAYS = 7;

/**
 * `useSyncExternalStore` snapshot for the "already installed"
 * signal — the browser's standalone-mode media query. The
 * snapshot is constant for the page lifetime, but the pattern
 * is still the right one because the value is *external* to
 * React (lives on the DOM) and is only available on the client.
 */
function getInstalledSnapshot(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches;
}
function getInstalledServerSnapshot(): boolean {
  return false;
}
function subscribeInstalled(_callback: () => void): () => void {
  // `display-mode` only changes on full app install/uninstall,
  // both of which trigger a navigation. No subscription needed.
  return () => {};
}

/**
 * `useSyncExternalStore` snapshot for the "user dismissed
 * recently" signal. The 7-day cooldown is anchored to
 * wall-clock time, so the snapshot is re-evaluated whenever
 * the storage event fires.
 */
function getDismissedSnapshot(): boolean {
  const raw = localStorage.getItem(DISMISS_KEY);
  if (!raw) return false;
  const at = Number(raw);
  if (!Number.isFinite(at)) return false;
  return (Date.now() - at) / (1000 * 60 * 60 * 24) < DISMISS_DAYS;
}
function getDismissedServerSnapshot(): boolean {
  return false;
}
function subscribeDismissed(callback: () => void): () => void {
  const onStorage = (e: StorageEvent) => {
    if (e.key === DISMISS_KEY) callback();
  };
  window.addEventListener('storage', onStorage);
  return () => window.removeEventListener('storage', onStorage);
}

/**
 * `useSyncExternalStore` snapshot for the deferred install
 * prompt event from the browser. The slot is a `window`
 * property so any number of subscribers can read the same
 * value.
 */
declare global {
  interface Window {
    __pwaPrompt?: BeforeInstallPromptEvent;
  }
}
function getPromptSnapshot(): BeforeInstallPromptEvent | null {
  return window.__pwaPrompt ?? null;
}
function getPromptServerSnapshot(): BeforeInstallPromptEvent | null {
  return null;
}
function subscribePrompt(callback: () => void): () => void {
  const onBeforeInstall = (e: Event) => {
    e.preventDefault();
    window.__pwaPrompt = e as BeforeInstallPromptEvent;
    callback();
  };
  const onInstalled = () => {
    delete window.__pwaPrompt;
    callback();
  };
  window.addEventListener('beforeinstallprompt', onBeforeInstall);
  window.addEventListener('appinstalled', onInstalled);
  return () => {
    window.removeEventListener('beforeinstallprompt', onBeforeInstall);
    window.removeEventListener('appinstalled', onInstalled);
  };
}

/**
 * PWA install prompt with proper hydration handling.
 *
 * All three external signals are bridged through
 * `useSyncExternalStore`:
 *
 *  - `isInstalled`     — matchMedia('(display-mode: standalone)').
 *  - `dismissed`       — localStorage with 7-day cooldown.
 *  - `deferredPrompt`  — the browser's `beforeinstallprompt` event.
 *
 * The server snapshot is always the "no prompt" branch, so SSR
 * markup is deterministic; React re-renders the client tree
 * once hydration completes and the real snapshots come in.
 */
export function PWAInstallPrompt() {
  const isInstalled = useSyncExternalStore(
    subscribeInstalled,
    getInstalledSnapshot,
    getInstalledServerSnapshot,
  );
  const dismissed = useSyncExternalStore(
    subscribeDismissed,
    getDismissedSnapshot,
    getDismissedServerSnapshot,
  );
  const deferredPrompt = useSyncExternalStore(
    subscribePrompt,
    getPromptSnapshot,
    getPromptServerSnapshot,
  );

  // Tracks whether the user just clicked "Install" in this
  // session. The browser's `appinstalled` event clears
  // `window.__pwaPrompt`, but we also want to hide the
  // prompt immediately on click, before the user completes
  // the OS-level install dialog. A `useState` for this is
  // fine because it only transitions user-driven, not on
  // hydration.
  const [installing, setInstalling] = useState(false);

  const handleInstall = useCallback(async () => {
    if (!deferredPrompt) return;
    setInstalling(true);
    await deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      delete window.__pwaPrompt;
    } else {
      setInstalling(false);
    }
  }, [deferredPrompt]);

  const handleDismiss = useCallback(() => {
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
    // Bump the dismiss store. `storage` events don't fire in
    // the originating tab, so we dispatch a synthetic one to
    // notify the subscription.
    window.dispatchEvent(new StorageEvent('storage', { key: DISMISS_KEY }));
  }, []);

  if (isInstalled || dismissed || !deferredPrompt || installing) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-sm rounded-none border border-line bg-bg-elev p-4 shadow-lg">
      <div className="mb-2 flex items-start justify-between gap-2">
        <h3 className="text-sm font-semibold text-fg">Install NetTools Hub</h3>
        <button
          onClick={handleDismiss}
          className="text-muted hover:text-fg"
          aria-label="Dismiss install prompt"
        >
          ✕
        </button>
      </div>
      <p className="mb-3 text-xs text-fg-2">
        Install as an app for quick access and offline support.
      </p>
      <div className="flex gap-2">
        <button
          onClick={handleInstall}
          className="flex-1 rounded-none border border-accent bg-accent px-3 py-1.5 text-xs font-medium text-bg hover:bg-accent/90"
        >
          Install
        </button>
        <button
          onClick={handleDismiss}
          className="flex-1 rounded-none border border-line px-3 py-1.5 text-xs font-medium text-fg-2 hover:border-fg-2 hover:text-fg"
        >
          Not now
        </button>
      </div>
    </div>
  );
}
