import Link from 'next/link';
import { COPYRIGHT_YEAR, SITE_OWNER } from '@/lib/site';
import { getLastUpdated } from '@/lib/projects';

/**
 * 站点底栏
 *
 * 三块内容（自上而下）：
 *  1. **免责声明** —— 法律意义上的硬性声明，每页都要有，不能省略。
 *  2. **维护元信息** —— 最后索引时间、维护者、源码仓库、License。
 *  3. **构建指纹** —— 静态站点、无追踪、无 cookie、无广告。
 *
 * 设计取舍：
 *  - server component，无 client JS；
 *  - 免责文案使用 `border-top` + 小标题 `kicker` 让它显眼，
 *    不能埋在角落；
 *  - 不复用 hero 的"editorial"色板，使用更冷的灰色阶，
 *    让"法律声明"和"营销/内容"在视觉上明确分层。
 */
export function SiteFooter() {
  const lastUpdated = getLastUpdated();
  return (
    <footer className="border-t border-line bg-bg-sunk/60">
      <div className="mx-auto max-w-7xl px-5 py-10 sm:px-8">
        {/* === Block 1 — Disclaimer ================================== */}
        <div className="mb-8 border-l-2 border-dim pl-4">
          <p className="kicker mb-2">Disclaimer · 免责声明</p>
          <p className="max-w-4xl text-[13px] leading-relaxed text-fg-2">
            本站点（NetTools Hub）是一个
            <strong className="text-fg">个人维护的链接索引</strong>，
            仅收录第三方开源项目的仓库地址与一段编辑性说明。
            <strong className="text-fg">本站不托管、不分发、不背书、不运营</strong>
            任何被链接的软件；收录即非推荐。 使用任何通过本站跳转到的项目，
            <strong className="text-fg">风险由使用者自行承担</strong>。 完整条款见{' '}
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
            <p className="kicker mb-2">Maintainer</p>
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
            <p className="mt-1 text-[11.5px] text-muted">Single-maintainer, non-commercial</p>
          </div>
          <div>
            <p className="kicker mb-2">Source</p>
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
            <p className="mt-1 text-[11.5px] text-muted">Static · MIT · No tracking</p>
          </div>
          <div>
            <p className="kicker mb-2">Last indexed</p>
            <p className="font-mono text-[12.5px] text-fg">{lastUpdated}</p>
            <p className="mt-1 text-[11.5px] text-muted">Auto-refreshed via GitHub Actions</p>
          </div>
          <div>
            <p className="kicker mb-2">License</p>
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
          <span>Build · static export · zero JS on this view</span>
          <span>No cookies · No analytics · No ads</span>
        </div>
      </div>
    </footer>
  );
}
