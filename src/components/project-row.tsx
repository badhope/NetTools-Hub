"use client";

import { useEffect, useRef, useState } from "react";
import type { Project } from "@/types/project";
import { platformLabel } from "@/lib/taxonomy";
import { Lang, t } from "@/lib/i18n";
import { formatNumber } from "@/lib/utils";

interface ProjectRowProps {
  project: Project;
  lang: Lang;
}

/**
 * Single project row in the /explore table.
 *
 * The whole row is clickable: clicking anywhere — the name, the
 * description, the platform badges, even the stars cell — opens
 * the upstream repository in a new tab. A short (~280 ms)
 * transition animation plays first, so the click is *seen* and
 * not silently lost: the row gets a brief `data-pressing` state
 * (left-rail pulse, accent background, slide-out `↗` icon)
 * before the new tab is opened. The delay is also useful on
 * touch devices, where the system would otherwise interpret a
 * long-press as a text-selection.
 *
 * Pre-flight check: before opening, we issue a 4 s HEAD request
 * to confirm the URL still resolves. Results are memoised per
 * session in a module-level Map so a second click is instant,
 * and rows that fail get a "link broken" badge so the user is
 * never sent to a 404. (The build-time validator in
 * `scripts/refresh-projects.mjs` already prunes 404s at deploy
 * time, so this is purely a safety net for links that die
 * between the schedule run and the user's click.)
 *
 * The name <a> is preserved with `target="_blank"` so that
 * right-click "Open in new tab", middle-click, and keyboard
 * navigation keep working.
 */
export function ProjectRow({ project: p, lang }: ProjectRowProps) {
  const [pressing, setPressing] = useState(false);
  const [linkState, setLinkState] = useState<"unknown" | "ok" | "broken">("unknown");
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, []);

  const preflight = (): Promise<boolean> => {
    if (linkCache.has(p.url)) {
      const cached = linkCache.get(p.url)!;
      if (cached !== "unknown") {
        // Restore from cache synchronously so the next render
        // shows the right state without a re-render.
        if (cached === "ok" && linkState !== "ok") setLinkState("ok");
        if (cached === "broken" && linkState !== "broken") setLinkState("broken");
      }
      return Promise.resolve(cached === "ok");
    }
    linkCache.set(p.url, "unknown");
    return new Promise<boolean>((resolve) => {
      try {
        // `no-cors` so a successful OPTIONS isn't blocked by
        // CORS; we only care that the server responded, not
        // what it said. 4 s is long enough for cold DNS, short
        // enough not to feel stuck.
        fetch(p.url, { method: "HEAD", mode: "no-cors", cache: "no-store", redirect: "follow" })
          .then((resp) => {
            // opaqueredirect / opaque responses count as OK
            const ok = resp.type === "opaque" || (resp.status >= 200 && resp.status < 400);
            linkCache.set(p.url, ok ? "ok" : "broken");
            setLinkState(ok ? "ok" : "broken");
            resolve(ok);
          })
          .catch(() => {
            linkCache.set(p.url, "broken");
            setLinkState("broken");
            resolve(false);
          });
      } catch {
        linkCache.set(p.url, "broken");
        setLinkState("broken");
        resolve(false);
      }
    });
  };

  const open = async () => {
    const ok = await preflight();
    if (!ok) return; // broken: stay on page, badge already shown
    window.open(p.url, "_blank", "noopener,noreferrer");
  };

  const navigate = () => {
    if (timerRef.current !== null) {
      window.clearTimeout(timerRef.current);
    }
    timerRef.current = window.setTimeout(() => {
      void open();
      timerRef.current = null;
    }, 280);
  };

  return (
    <tr
      className="proj-row"
      data-pressing={pressing ? "true" : undefined}
      data-link={linkState}
      onPointerDown={(e) => {
        // Don't hijack middle / right clicks; those are the
        // browser's "open in new tab" gestures.
        if (e.button !== 0) return;
        setPressing(true);
        navigate();
      }}
      onPointerUp={() => setPressing(false)}
      onPointerCancel={() => setPressing(false)}
      onPointerLeave={() => setPressing(false)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          setPressing(true);
          navigate();
        }
      }}
      tabIndex={0}
      role="link"
      aria-label={`${p.name} — open repository in a new tab`}
    >
      <td>
        <div className="name">
          <a
            href={p.url}
            target="_blank"
            rel="noopener noreferrer"
            title={`${p.name} — ${p.description}`}
            onClick={(e) => e.stopPropagation()}
          >
            {p.name}
          </a>
          <span className="ml-1 text-[10.5px] text-muted">@{p.author}</span>
          <span className="ext-icon" aria-hidden="true">
            ↗
          </span>
          {linkState === "broken" && (
            <span className="ml-2 text-[10px] text-accent-4" title="This link failed the pre-flight check">
              link broken
            </span>
          )}
        </div>
        <p className="desc mt-0.5">{p.description}</p>
        <p className="tag mt-0.5 truncate">
          {p.tags.slice(0, 6).map((tag) => `#${tag}`).join("  ")}
        </p>
      </td>
      <td className="hide-md">
        <div className="flex flex-wrap gap-1">
          {p.platform.map((plat) => (
            <span
              key={plat}
              className="badge"
              title={platformLabel(plat, lang)}
            >
              {plat}
            </span>
          ))}
        </div>
      </td>
      <td className="num text-right">
        {formatNumber(p.stars, lang)}
        {p.forks > 0 && (
          <span className="ml-1 text-muted">/ {formatNumber(p.forks, lang)}</span>
        )}
      </td>
      <td className="hide-md num">{p.lastCommit}</td>
      <td className="hide-md num">{p.license}</td>
      <td className="hide-md">
        <span className={`badge badge--${p.status}`}>
          {t(lang, `status.${p.status}`)}
        </span>
      </td>
      <td className="hide-md">
        {p.verdict && (
          <span className={`badge badge--${p.verdict}`}>
            {t(lang, `verdict.${p.verdict}`)}
          </span>
        )}
      </td>
    </tr>
  );
}

/**
 * Per-session link cache. We never persist this to localStorage
 * because (a) the build-time `scripts/refresh-projects.mjs`
 * already does the canonical HEAD sweep weekly, and (b) a stale
 * cache that disagrees with reality is worse than no cache —
 * users will see a "link broken" badge and re-click, which is
 * the right behaviour.
 */
const linkCache: Map<string, "unknown" | "ok" | "broken"> = new Map();
