import Link from 'next/link';
import { Lang, withLang, t } from '@/lib/i18n';
import { kindLabel, platformLabel } from '@/lib/taxonomy';

interface Crumb {
  label: string;
  href?: string;
}

interface BreadcrumbProps {
  /** Crumbs rendered left-to-right. The last one is the current page
   *  and is rendered without a link. */
  trail: Crumb[];
  lang: Lang;
}

/**
 * Breadcrumb — a textual `path` you can read, not a UI widget
 * you have to hover. Each segment is a link except the last,
 * which is the current page.
 *
 *   explore  /  proxy  /  desktop
 *   ─────────────────────────────────
 *   38 entries · last commit 2026-05-30
 */
export function Breadcrumb({ trail, lang }: BreadcrumbProps) {
  return (
    <div className="flex flex-col gap-1">
      <nav
        aria-label="Breadcrumb"
        className="flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5 font-mono text-[11.5px]"
      >
        <span className="text-accent-2">$</span>
        <span className="text-muted">cd</span>
        {trail.map((c, i) => (
          <span key={i} className="flex items-baseline gap-1.5">
            <span className="text-muted">/</span>
            {c.href ? (
              <Link href={withLang(lang, c.href)} className="text-fg-2 hover:text-accent">
                {c.label}
              </Link>
            ) : (
              <span className="text-fg">{c.label}</span>
            )}
          </span>
        ))}
      </nav>
    </div>
  );
}

/** Convenience constructor: the `explore` root crumb. */
export function rootCrumb(lang: Lang): Crumb {
  return { label: t(lang, 'breadcrumb.root'), href: '/explore' };
}

/** Convenience: kind crumb. */
export function kindCrumb(lang: Lang, kind: string): Crumb {
  return {
    label: `${kindLabel(kind as never, lang)} (${kind})`,
    href: `/explore/k/${kind}`,
  };
}

/** Convenience: platform crumb (last, no link). */
export function platformCrumb(lang: Lang, kind: string, platform: string): Crumb {
  return {
    label: `${platformLabel(platform as never, lang)} (${platform})`,
  };
}
