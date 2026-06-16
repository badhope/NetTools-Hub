'use client';

import Link from 'next/link';
import { COPYRIGHT_YEAR, SITE_OWNER } from '@/lib/site';
import { getLastUpdated } from '@/lib/projects';
import { t } from '@/lib/i18n';
import { useLang } from '@/components/lang-provider';

/**
 * Site footer.
 *
 * Three blocks (top to bottom):
 *  1. **Disclaimer** — legal statement, every page must have it.
 *  2. **Meta / Sources** — last indexed, maintainer, repo, license.
 *  3. **Build fingerprint** — static export, no tracking, no cookies, no ads.
 *
 * Design choices:
 *  - Client component to read language from LangProvider;
 *  - Disclaimer uses `border-top` + `kicker` to make it visible;
 *  - Colder grey scale to visually separate "legal" from "content".
 */
export function SiteFooter() {
  const { lang } = useLang();
  const lastUpdated = getLastUpdated();
  return (
    <footer className="border-t border-line bg-bg-sunk/60">
      <div className="mx-auto max-w-7xl px-5 py-10 sm:px-8">
        {/* === Block 1 — Disclaimer ================================== */}
        <div className="mb-8 border-l-2 border-dim pl-4">
          <p className="kicker mb-2">{t(lang, 'footer.disclaimer_title')}</p>
          <p className="max-w-4xl text-[13px] leading-relaxed text-fg-2">
            {t(lang, 'footer.disclaimer_text')}{' '}
            <Link
              href="https://github.com/badhope/NetTools-Hub/blob/main/DISCLAIMER.md"
              className="link-editorial"
              target="_blank"
              rel="noopener noreferrer"
            >
              DISCLAIMER.md
            </Link>
            。
          </p>
        </div>

        {/* === Block 2 — Meta / Sources ============================== */}
        <div className="grid grid-cols-1 gap-6 border-t border-line pt-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <p className="kicker mb-2">{t(lang, 'footer.maintainer')}</p>
            <p className="font-mono text-[12.5px] text-fg">
              <Link
                href={`https://github.com/${SITE_OWNER}`}
                target="_blank"
                rel="noopener noreferrer"
                className="link-editorial"
              >
                @{SITE_OWNER}
              </Link>
            </p>
            <p className="mt-1 text-[11.5px] text-muted">{t(lang, 'footer.maintainer_desc')}</p>
          </div>
          <div>
            <p className="kicker mb-2">{t(lang, 'footer.source')}</p>
            <p className="font-mono text-[12.5px] text-fg">
              <Link
                href={`https://github.com/${SITE_OWNER}/NetTools-Hub`}
                target="_blank"
                rel="noopener noreferrer"
                className="link-editorial"
              >
                badhope/NetTools-Hub
              </Link>
            </p>
            <p className="mt-1 text-[11.5px] text-muted">{t(lang, 'footer.source_desc')}</p>
          </div>
          <div>
            <p className="kicker mb-2">{t(lang, 'footer.last_indexed')}</p>
            <p className="font-mono text-[12.5px] text-fg">{lastUpdated}</p>
            <p className="mt-1 text-[11.5px] text-muted">{t(lang, 'footer.last_indexed_desc')}</p>
          </div>
          <div>
            <p className="kicker mb-2">{t(lang, 'footer.license')}</p>
            <p className="font-mono text-[12.5px] text-fg">
              <Link
                href="https://github.com/badhope/NetTools-Hub/blob/main/LICENSE"
                target="_blank"
                rel="noopener noreferrer"
                className="link-editorial"
              >
                MIT
              </Link>
            </p>
            <p className="mt-1 text-[11.5px] text-muted">
              © {COPYRIGHT_YEAR} {SITE_OWNER}
            </p>
          </div>
        </div>

        {/* === Block 3 — Build fingerprint =========================== */}
        <div className="mt-8 flex flex-col items-start justify-between gap-2 border-t border-line pt-5 font-mono text-[10px] uppercase tracking-[0.2em] text-muted sm:flex-row sm:items-center">
          <span>{t(lang, 'footer.build')}</span>
          <span>{t(lang, 'footer.privacy')}</span>
        </div>
      </div>
    </footer>
  );
}
