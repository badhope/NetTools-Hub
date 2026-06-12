'use client';

import { useEffect, useState, useCallback } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

function getInitialState(): { isInstalled: boolean; showPrompt: boolean } {
  if (typeof window === 'undefined') {
    return { isInstalled: false, showPrompt: false };
  }
  // Check if already installed
  if (window.matchMedia('(display-mode: standalone)').matches) {
    return { isInstalled: true, showPrompt: false };
  }
  // Check if dismissed recently
  const dismissed = localStorage.getItem('pwa-install-dismissed');
  if (dismissed) {
    const daysSinceDismissed = (Date.now() - parseInt(dismissed)) / (1000 * 60 * 60 * 24);
    if (daysSinceDismissed < 7) {
      return { isInstalled: false, showPrompt: false };
    }
  }
  return { isInstalled: false, showPrompt: false };
}

export function PWAInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [{ isInstalled, showPrompt }, setState] = useState(getInitialState);

  useEffect(() => {
    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setState((prev) => ({ ...prev, showPrompt: true }));
    };

    // Listen for app installed event
    const handleAppInstalled = () => {
      setState({ isInstalled: true, showPrompt: false });
      setDeferredPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstall = useCallback(async () => {
    if (!deferredPrompt) return;

    await deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      setState({ isInstalled: true, showPrompt: false });
    }

    setDeferredPrompt(null);
  }, [deferredPrompt]);

  const handleDismiss = useCallback(() => {
    setState((prev) => ({ ...prev, showPrompt: false }));
    // Don't show again for 7 days
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
  }, []);

  if (isInstalled || !showPrompt) return null;

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
