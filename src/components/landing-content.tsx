import Link from 'next/link';
import { TopNav } from '@/components/top-nav';
import { Lang, withLang } from '@/lib/i18n';
import { PROJECT_COUNT, TOTAL_STARS, SITE_OWNER, COPYRIGHT_YEAR } from '@/lib/site';
import { getAllProjects, getKindCounts, getLastUpdated } from '@/lib/projects';
import { kindLabel } from '@/lib/taxonomy';
import type { ProjectKind } from '@/types/project';
import { KIND_ORDER } from '@/lib/constants';
import { formatStars } from '@/lib/utils';

const KIND_BLURB: Record<ProjectKind, string> = {
  proxy: 'Cores & clients (Clash / Mihomo / sing-box / V2Ray / Xray).',
  vpn: 'Wire protocols (WireGuard / OpenVPN / IPsec / Tailscale / ZeroTier).',
  dns: 'Resolvers, filters, sinkholes.',
  acceleration: 'GitHub / Docker mirror, reverse proxy, tunnel.',
  security: 'WAF, IDS / IPS, fail2ban, honeypots.',
  monitoring: 'Prometheus / Grafana / Uptime Kuma / Netdata.',
  ops: 'Container, Kubernetes, self-hosted control planes.',
  tools: 'CLI utilities, network test, data transfer.',
};

/**
 * Landing content.
 *
 * The site is a directory; the landing page is a *table of
 * contents* with a hero, a one-line description, a stat bar, and
 * a kind-card grid. No marketing copy, no "atlas" metaphor, no
 * gradients, no round-corner card with a coloured rail — those
 * are gone with the editorial direction this design replaces.
 */
export function LandingContent({ lang = 'en' as Lang }: { lang?: Lang }) {
  const projects = getAllProjects();
  const counts = getKindCounts();
  const lastUpdated = getLastUpdated();
  return (
    <div className="min-h-screen bg-bg text-fg">
      <TopNav lang={lang} variant="landing" kindCounts={counts} total={projects.length} />
      <main
        id="main"
        aria-label="Main content"
        className="mx-auto max-w-7xl px-5 py-10 sm:px-8 sm:py-14"
      >
        {/* ============================================================
         *  Hero
         * ============================================================ */}
        <section aria-label="Introduction" className="border-b border-line pb-10">
          <div className="manual-index mb-3" data-index="00">
            <span>Index</span>
          </div>
          <h1 className="max-w-4xl text-[2rem] font-semibold leading-[1.1] tracking-tight sm:text-[2.5rem]">
            A field manual of <span className="text-accent-2">{PROJECT_COUNT}</span> open-source
            network tools,
            <br className="hidden sm:inline" />
            organised by{' '}
            <Link href={withLang(lang, '/explore/k/proxy')} className="link-editorial">
              kind
            </Link>{' '}
            and by{' '}
            <Link href={withLang(lang, '/explore/k/proxy/p/desktop')} className="link-editorial">
              platform
            </Link>
            .
          </h1>
          <p className="mt-4 max-w-3xl text-[14.5px] leading-relaxed text-fg-2">
            NetTools Hub is a personal link index, not a directory service and not a proxy. We do
            not host, distribute, endorse, or operate any project linked from this page. Use at your
            own risk;{' '}
            <Link
              href="https://github.com/badhope/NetTools-Hub/blob/main/DISCLAIMER.md"
              target="_blank"
              rel="noopener noreferrer"
              className="link-editorial"
            >
              read the full disclaimer
            </Link>{' '}
            before installing anything.
          </p>

          {/* Stat bar — one line of "facts about the index" */}
          <div className="mt-6 grid grid-cols-2 gap-3 border-y border-line py-3 sm:grid-cols-4">
            <Stat label="Projects" value={String(PROJECT_COUNT)} />
            <Stat label="Kinds" value={String(KIND_ORDER.length)} />
            <Stat label="Total stars" value={formatStars(TOTAL_STARS)} />
            <Stat label="Last indexed" value={lastUpdated} />
          </div>
        </section>

        {/* ============================================================
         *  Table of contents — 8 kind cards in a 2×4 grid
         * ============================================================ */}
        <section aria-label="Browse by kind" className="mt-10">
          <div className="manual-index mb-4" data-index="01">
            <span>Browse by kind</span>
          </div>
          <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {KIND_ORDER.map((k) => {
              const n = counts[k] || 0;
              if (n === 0) return null;
              return (
                <li key={k}>
                  <Link
                    href={withLang(lang, `/explore/k/${k}`)}
                    className="block border border-line bg-bg-elev/40 p-4 transition-colors hover:border-accent hover:bg-bg-sunk"
                  >
                    <div className="flex items-baseline justify-between">
                      <span className="font-mono text-[10.5px] text-muted">/{k}</span>
                      <span className="font-mono text-[10.5px] text-muted">
                        {String(n).padStart(3, '0')}
                      </span>
                    </div>
                    <p className="mt-2 text-[15px] font-medium text-fg">{kindLabel(k, lang)}</p>
                    <p className="mt-1 text-[12.5px] leading-relaxed text-fg-2">{KIND_BLURB[k]}</p>
                  </Link>
                </li>
              );
            })}
          </ul>
        </section>

        {/* ============================================================
         *  How the index is maintained
         * ============================================================ */}
        <section
          aria-label="How the index is maintained"
          className="mt-12 grid grid-cols-1 gap-8 border-t border-line pt-8 lg:grid-cols-3"
        >
          <div className="lg:col-span-2">
            <div className="manual-index mb-3" data-index="02">
              <span>How the index is maintained</span>
            </div>
            <p className="max-w-3xl text-[14px] leading-relaxed text-fg-2">
              The <code className="font-mono text-fg">data/projects.json</code> file is the only
              source of truth. The schema and entry format are documented in{' '}
              <Link
                href="https://github.com/badhope/NetTools-Hub/blob/main/docs/data-model.md"
                target="_blank"
                rel="noopener noreferrer"
                className="link-editorial"
              >
                docs/data-model.md
              </Link>
              ; the validator is{' '}
              <code className="font-mono text-fg">scripts/validate-projects.mjs</code>; the live
              metadata is refreshed by a scheduled GitHub Action every Sunday 03:00 UTC.
            </p>
            <pre className="mt-3 overflow-x-auto border border-line bg-bg-sunk/60 p-3 font-mono text-[12px] leading-relaxed text-fg-2">
              {`#   validate   the data file
pnpm run validate
#   refresh    stars / forks / license / lastCommit
pnpm run refresh
#   mine       candidates from awesome-* repos
pnpm run scan
#   preview    the site locally
pnpm run dev`}
            </pre>
          </div>
          <aside>
            <div className="manual-index mb-3" data-index="03">
              <span>Facts</span>
            </div>
            <ul className="space-y-2 text-[13px] text-fg-2">
              <li>
                <span className="kicker mr-1">Type</span> Static, no backend
              </li>
              <li>
                <span className="kicker mr-1">Maintainer</span>{' '}
                <Link
                  href={`https://github.com/${SITE_OWNER}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="link-editorial"
                >
                  @{SITE_OWNER}
                </Link>
              </li>
              <li>
                <span className="kicker mr-1">License</span> MIT
              </li>
              <li>
                <span className="kicker mr-1">Edition</span> {COPYRIGHT_YEAR}
              </li>
              <li>
                <span className="kicker mr-1">Stack</span> Next.js · TypeScript · Tailwind v4
              </li>
            </ul>
          </aside>
        </section>
      </main>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div role="group" aria-label={`${label} statistic`}>
      <p className="kicker" aria-label="Label">
        {label}
      </p>
      <p className="mt-0.5 font-mono text-[1.05rem] font-medium text-fg" aria-label="Value">
        {value}
      </p>
    </div>
  );
}
