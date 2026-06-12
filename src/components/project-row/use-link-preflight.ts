"use client";
import { useState, useCallback } from "react";

type LinkState = "unknown" | "ok" | "broken";

// Module-level cache shared across all rows
const linkCache = new Map<string, LinkState>();

export function useLinkPreflight(url: string) {
  const [linkState, setLinkState] = useState<LinkState>(() => {
    return linkCache.get(url) ?? "unknown";
  });

  const preflight = useCallback(async (): Promise<boolean> => {
    if (linkCache.has(url)) {
      const cached = linkCache.get(url)!;
      if (cached !== "unknown") {
        setLinkState(cached);
        return cached === "ok";
      }
    }
    linkCache.set(url, "unknown");
    try {
      const resp = await fetch(url, {
        method: "HEAD",
        mode: "no-cors",
        cache: "no-store",
        redirect: "follow",
      });
      const ok = resp.type === "opaque" || (resp.status >= 200 && resp.status < 400);
      linkCache.set(url, ok ? "ok" : "broken");
      setLinkState(ok ? "ok" : "broken");
      return ok;
    } catch {
      linkCache.set(url, "broken");
      setLinkState("broken");
      return false;
    }
  }, [url]);

  return { linkState, preflight };
}
