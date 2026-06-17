'use client';

import Link from 'next/link';
import { TopNav } from '@/components/top-nav';
import { t, withLang, type Lang } from '@/lib/i18n';
import { PROJECT_COUNT, TOTAL_STARS, SITE_OWNER, COPYRIGHT_YEAR } from '@/lib/site';
import { getAllProjects, getKindCounts, getLastUpdated } from '@/lib/projects';
import { kindLabel } from '@/lib/taxonomy';
import type { ProjectKind } from '@/types/project';
import { KIND_ORDER } from '@/lib/constants';
import { formatStars } from '@/lib/utils';
import { useLang } from '@/components/lang-provider';

const KIND_BLURB: Record<Lang, Record<ProjectKind, string>> = {
  en: {
    proxy: 'Cores & clients (Clash / Mihomo / sing-box / V2Ray / Xray).',
    vpn: 'Wire protocols (WireGuard / OpenVPN / IPsec / Tailscale / ZeroTier).',
    dns: 'Resolvers, filters, sinkholes.',
    acceleration: 'GitHub / Docker mirror, reverse proxy, tunnel.',
    security: 'WAF, IDS / IPS, fail2ban, honeypots.',
    monitoring: 'Prometheus / Grafana / Uptime Kuma / Netdata.',
    ops: 'Container, Kubernetes, self-hosted control planes.',
    tools: 'CLI utilities, network test, data transfer.',
  },
  zh: {
    proxy: '核心与客户端（Clash / Mihomo / sing-box / V2Ray / Xray）。',
    vpn: '有线协议（WireGuard / OpenVPN / IPsec / Tailscale / ZeroTier）。',
    dns: '解析器、过滤器、黑洞。',
    acceleration: 'GitHub / Docker 镜像、反向代理、隧道。',
    security: 'WAF、IDS / IPS、fail2ban、蜜罐。',
    monitoring: 'Prometheus / Grafana / Uptime Kuma / Netdata。',
    ops: '容器、Kubernetes、自托管控制平面。',
    tools: 'CLI 工具、网络测试、数据传输。',
  },
  ja: {
    proxy: 'コアとクライアント（Clash / Mihomo / sing-box / V2Ray / Xray）。',
    vpn: 'ワイヤープロトコル（WireGuard / OpenVPN / IPsec / Tailscale / ZeroTier）。',
    dns: 'リゾルバ、フィルタ、シンクホール。',
    acceleration: 'GitHub / Docker ミラー、リバースプロキシ、トンネル。',
    security: 'WAF、IDS / IPS、fail2ban、ハニーポット。',
    monitoring: 'Prometheus / Grafana / Uptime Kuma / Netdata。',
    ops: 'コンテナ、Kubernetes、セルフホスト制御平面。',
    tools: 'CLI ユーティリティ、ネットワークテスト、データ転送。',
  },
};

/**
 * Landing content.
 *
 * The site is a directory; the landing page is a *table of
 * contents* with a hero, a one-line description, a stat bar, and
 * a kind-card grid. No marketing copy, no "atlas" metaphor, no
 * gradients, no round-corner card with a coloured rail — those
 * are gone with the editorial direction this design replaces.
 *
 * The component is a client component that reads the active
 * language from the `LangProvider` context — that is how the
 * language switcher in the top nav re-renders the kind-card
 * labels, the "open the index" CTA, and the rest of the
 * chrome without a full page reload.
 */
export function LandingContent() {
  const { lang } = useLang();
  const projects = getAllProjects();
  const counts = getKindCounts();
  const lastUpdated = getLastUpdated();
  return (
    <div className="min-h-screen bg-bg text-fg">
      <TopNav variant="landing" kindCounts={counts} total={projects.length} />
      <main
        id="main"
        aria-label={t(lang, 'aria.main_content')}
        className="mx-auto max-w-7xl px-5 py-10 sm:px-8 sm:py-14"
      >
        {/* ============================================================
         *  Hero
         * ============================================================ */}
        <section aria-label={t(lang, 'aria.introduction')} className="border-b border-line pb-10">
          <div className="manual-index mb-3" data-index="00">
            <span>{t(lang, 'landing.index_label')}</span>
          </div>
          <h1 className="max-w-4xl text-[2rem] font-semibold leading-[1.1] tracking-tight sm:text-[2.5rem]">
            {t(lang, 'landing.hero_pre')} <span className="text-accent-2">{PROJECT_COUNT}</span>{' '}
            {t(lang, 'landing.hero_mid')}
            <br className="hidden sm:inline" />
            {t(lang, 'landing.hero_organised_by')}{' '}
            <Link href={withLang(lang, '/explore/k/proxy')} className="link-editorial">
              {t(lang, 'landing.hero_kind')}
            </Link>{' '}
            {t(lang, 'landing.hero_and_by')}{' '}
            <Link href={withLang(lang, '/explore/k/proxy/p/desktop')} className="link-editorial">
              {t(lang, 'landing.hero_platform')}
            </Link>
          </h1>
          <p className="mt-4 max-w-3xl text-[14.5px] leading-relaxed text-fg-2">
            {t(lang, 'landing.hero_intro')}{' '}
            <Link
              href="https://github.com/badhope/NetTools-Hub/blob/main/DISCLAIMER.md"
              target="_blank"
              rel="noopener noreferrer"
              className="link-editorial"
            >
              {t(lang, 'landing.read_disclaimer')}
            </Link>{' '}
            {t(lang, 'landing.before_installing')}
          </p>

          {/* Stat bar — one line of "facts about the index" */}
          <div className="mt-6 grid grid-cols-2 gap-3 border-y border-line py-3 sm:grid-cols-4">
            <Stat label={t(lang, 'stat.projects')} value={String(PROJECT_COUNT)} />
            <Stat label={t(lang, 'stat.kinds')} value={String(KIND_ORDER.length)} />
            <Stat label={t(lang, 'stat.total_stars')} value={formatStars(TOTAL_STARS)} />
            <Stat label={t(lang, 'stat.last_indexed')} value={lastUpdated} />
          </div>
        </section>

        {/* ============================================================
         *  Table of contents — 8 kind cards in a 2×4 grid
         * ============================================================ */}
        <section aria-label={t(lang, 'aria.browse_by_kind')} className="mt-10">
          <div className="manual-index mb-4" data-index="01">
            <span>{t(lang, 'landing.browse_by_kind')}</span>
          </div>
          <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {KIND_ORDER.map((k) => {
              const n = counts[k] || 0;
              if (n === 0) return null;
              return (
                <li key={k}>
                  <Link
                    href={withLang(lang, `/explore/k/${k}`)}
                    className="kind-card block border border-line bg-bg-elev/40 p-4 transition-colors hover:border-accent hover:bg-bg-sunk"
                  >
                    <div className="flex items-baseline justify-between">
                      <span className="font-mono text-[10.5px] text-muted">/{k}</span>
                      <span className="font-mono text-[10.5px] text-muted">
                        {String(n).padStart(3, '0')}
                      </span>
                    </div>
                    <p className="mt-2 text-[15px] font-medium text-fg">{kindLabel(k, lang)}</p>
                    <p className="mt-1 text-[12.5px] leading-relaxed text-fg-2">
                      {KIND_BLURB[lang][k]}
                    </p>
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
          aria-label={t(lang, 'aria.how_maintained')}
          className="mt-12 grid grid-cols-1 gap-8 border-t border-line pt-8 lg:grid-cols-3"
        >
          <div className="lg:col-span-2">
            <div className="manual-index mb-3" data-index="02">
              <span>{t(lang, 'landing.how_maintained')}</span>
            </div>
            <p className="max-w-3xl text-[14px] leading-relaxed text-fg-2">
              {t(lang, 'landing.maintained_desc', { code: 'data/projects.json' })}{' '}
              <Link
                href="https://github.com/badhope/NetTools-Hub/blob/main/docs/data-model.md"
                target="_blank"
                rel="noopener noreferrer"
                className="link-editorial"
              >
                docs/data-model.md
              </Link>
              {t(lang, 'landing.maintained_validator')}{' '}
              <code className="font-mono text-fg">scripts/validate-projects.mjs</code>
              {t(lang, 'landing.maintained_refresh')}
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
              <span>{t(lang, 'landing.facts')}</span>
            </div>
            <ul className="space-y-2 text-[13px] text-fg-2">
              <li>
                <span className="kicker mr-1">{t(lang, 'landing.fact_type')}</span>{' '}
                {t(lang, 'landing.fact_type_value')}
              </li>
              <li>
                <span className="kicker mr-1">{t(lang, 'landing.fact_maintainer')}</span>{' '}
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
                <span className="kicker mr-1">{t(lang, 'landing.fact_license')}</span> MIT
              </li>
              <li>
                <span className="kicker mr-1">{t(lang, 'landing.fact_edition')}</span>{' '}
                {COPYRIGHT_YEAR}
              </li>
              <li>
                <span className="kicker mr-1">{t(lang, 'landing.fact_stack')}</span>{' '}
                {t(lang, 'landing.fact_stack_value')}
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
    <div role="group" aria-label={label}>
      <p className="kicker">{label}</p>
      <p className="mt-0.5 font-mono text-[1.05rem] font-medium text-fg">{value}</p>
    </div>
  );
}
