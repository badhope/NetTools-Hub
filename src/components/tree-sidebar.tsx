"use client";

import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { withLang, t } from "@/lib/i18n";
import { kindLabel, platformLabel } from "@/lib/taxonomy";
import type { ProjectKind, ProjectPlatform } from "@/types/project";

interface TreeSidebarProps {
  /** Path of the current request: [kind?, platform?]. */
  current: { kind?: ProjectKind; platform?: ProjectPlatform };
  /** Counts for the kind-level buckets. */
  kindCounts: Record<string, number>;
  /** Counts for the kind+platform buckets. */
  kindPlatformCounts: Record<string, number>;
  /** Total project count (for the "All" link). */
  total: number;
  lang: Lang;
}

/**
 * Tree-style sidebar.
 *
 * Renders a 2-level navigation:
 *   explore/
 *   ├── (all)                              [210]
 *   ├── proxy/                             [ N ]
 *   │   ├── (all platforms)                [ N ]
 *   │   ├── desktop                        [ N ]
 *   │   ├── mobile                         [ N ]
 *   │   ├── cli                            [ N ]
 *   │   ├── server                         [ N ]
 *   │   ├── browser                        [ N ]
 *   │   └── router                         [ N ]
 *   ├── vpn/                               [ N ]
 *   │   └── ... (same children)
 *   └── ...
 *
 * Each leaf is a real `<Link>` so the URL hierarchy is the
 * navigation state (back/forward, share-by-link, deep linking all
 * work for free).
 */
export function TreeSidebar({
  current,
  kindCounts,
  kindPlatformCounts,
  total,
  lang,
}: TreeSidebarProps) {
  const isKindActive = (k: ProjectKind) => current.kind === k;
  const isPlatformActive = (p: ProjectPlatform) => current.platform === p;
  const isRoot = !current.kind;

  // The kind list is the order they appear in the data layer.
  // Keeping it stable across renders lets the browser pre-warm the
  // row positions for the keyboard navigation.
  const kinds: ProjectKind[] = [
    "proxy", "vpn", "dns", "acceleration", "security", "monitoring", "ops", "tools",
  ];
  const platforms: ProjectPlatform[] = [
    "desktop", "mobile", "cli", "server", "browser", "router",
  ];

  return (
    <nav
      aria-label={t(lang, "taxonomy.tree")}
      className="w-full lg:w-72 lg:shrink-0"
    >
      <div className="border border-line bg-bg-elev/40 p-3">
        <div className="manual-index mb-2 px-1" data-index={t(lang, "taxonomy.tree").toUpperCase()}>
          <span className="px-1">{t(lang, "taxonomy.tree")}</span>
        </div>
        <ul className="text-[12.5px]">
          {/* Root: "all projects" */}
          <li>
            <Link
              href={withLang(lang, "/explore")}
              data-current={isRoot ? "true" : undefined}
              className="tree-row flex items-center justify-between gap-2 py-1 pr-2 text-fg-2 hover:text-fg"
              style={{ ["--depth" as string]: 0 }}
            >
              <span className="flex items-center gap-1.5 truncate">
                <span className="text-muted">/</span>
                <span className="truncate">{t(lang, "taxonomy.all")}</span>
              </span>
              <span className="shrink-0 text-[10px] text-muted">
                {String(total).padStart(3, "0")}
              </span>
            </Link>
          </li>

          {kinds.map((k) => {
            const kCount = kindCounts[k] || 0;
            if (kCount === 0) return null;
            const kActive = isKindActive(k);
            return (
              <li key={k}>
                {/* Kind row */}
                <Link
                  href={withLang(lang, `/explore/k/${k}`)}
                  data-current={kActive && !current.platform ? "true" : undefined}
                  className="tree-row flex items-center justify-between gap-2 py-1 pr-2 text-fg-2 hover:text-fg"
                  style={{ ["--depth" as string]: 0 }}
                >
                  <span className="flex items-center gap-1.5 truncate">
                    <span className="text-muted">├─</span>
                    <span className="truncate">{kindLabel(k, lang)}</span>
                    <span className="text-[10px] text-muted">/{k}</span>
                  </span>
                  <span className="shrink-0 text-[10px] text-muted">
                    {String(kCount).padStart(3, "0")}
                  </span>
                </Link>

                {/* Platform children — only shown when the kind is active,
                 * to keep the tree from running off the screen on the
                 * "all" view. The user can click into the kind to see
                 * the per-platform drill-down. */}
                {kActive && (
                  <ul>
                    <li>
                      <Link
                        href={withLang(lang, `/explore/k/${k}`)}
                        data-current={kActive && !current.platform ? "true" : undefined}
                        className="tree-row flex items-center justify-between gap-2 py-1 pr-2 text-fg-2 hover:text-fg"
                        style={{ ["--depth" as string]: 1 }}
                      >
                        <span className="flex items-center gap-1.5 truncate">
                          <span className="text-muted">│  *</span>
                          <span className="truncate">{t(lang, "taxonomy.all")}</span>
                        </span>
                        <span className="shrink-0 text-[10px] text-muted">
                          {String(kCount).padStart(3, "0")}
                        </span>
                      </Link>
                    </li>
                    {platforms.map((p) => {
                      const kpCount = kindPlatformCounts[`${k}|${p}`] || 0;
                      if (kpCount === 0) return null;
                      const pActive = isPlatformActive(p);
                      return (
                        <li key={p}>
                          <Link
                            href={withLang(lang, `/explore/k/${k}/p/${p}`)}
                            data-current={pActive ? "true" : undefined}
                            className="tree-row flex items-center justify-between gap-2 py-1 pr-2 text-fg-2 hover:text-fg"
                            style={{ ["--depth" as string]: 1 }}
                          >
                            <span className="flex items-center gap-1.5 truncate">
                              <span className="text-muted">│  ├─</span>
                              <span className="truncate">{platformLabel(p, lang)}</span>
                              <span className="text-[10px] text-muted">/{p}</span>
                            </span>
                            <span className="shrink-0 text-[10px] text-muted">
                              {String(kpCount).padStart(3, "0")}
                            </span>
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </li>
            );
          })}
        </ul>
      </div>

      {/* Path display — a literal `pwd` for the current page. */}
      <div className="mt-3 border border-line bg-bg-sunk/60 p-2 text-[11px] text-muted">
        <span className="text-accent-2">$</span>{" "}
        <span className="text-fg-2">pwd</span>{" "}
        <span>
          /explore
          {current.kind ? `/${current.kind}` : ""}
          {current.platform ? `/${current.platform}` : ""}
        </span>
      </div>
    </nav>
  );
}
