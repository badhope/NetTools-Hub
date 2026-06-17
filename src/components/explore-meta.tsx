'use client';

import Link from 'next/link';
import { useLang } from '@/components/lang-provider';
import { t, withLang } from '@/lib/i18n';
import { kindLabel } from '@/lib/taxonomy';
import { formatStars } from '@/lib/utils';
import type { ProjectKind } from '@/types/project';

interface ExploreMetaProps {
  variant: 'all' | 'kind' | 'platform' | 'project';
  count: number;
  totalStars?: number;
  kind?: ProjectKind;
  projectName?: string;
  projectStars?: number;
  projectLanguage?: string;
}

/**
 * Meta line for explore pages. Rendered as a client component
 * so it picks up the active language from LangProvider and
 * re-renders on language switch.
 */
export function ExploreMeta({
  variant,
  count,
  totalStars,
  kind,
  projectName,
  projectStars,
  projectLanguage,
}: ExploreMetaProps) {
  const { lang } = useLang();

  if (variant === 'project') {
    return (
      <p className="text-[12.5px] text-fg-2">
        <span className="font-mono text-muted">{t(lang, 'explore.meta_detail')}</span> {projectName}{' '}
        · {formatStars(projectStars ?? 0)} {t(lang, 'explore.stars')} ·{' '}
        <span className="font-mono text-muted">{projectLanguage}</span>
      </p>
    );
  }

  if (variant === 'all') {
    return (
      <p className="text-[12.5px] text-fg-2">
        <span className="font-mono text-muted">{t(lang, 'explore.meta_index')}</span>{' '}
        {t(lang, 'taxonomy.count', { n: count })} ·{' '}
        {totalStars !== undefined && (
          <>
            {formatStars(totalStars)} {t(lang, 'explore.total_stars')} ·{' '}
          </>
        )}
        <span className="font-mono text-muted">{t(lang, 'explore.sorted_by_stars')}</span>
      </p>
    );
  }

  if (variant === 'kind' && kind) {
    return (
      <p className="text-[12.5px] text-fg-2">
        <span className="font-mono text-muted">[ {kind} ]</span>{' '}
        {t(lang, 'taxonomy.count', { n: count })} ·{' '}
        <span className="font-mono text-muted">{t(lang, 'explore.sorted_by_stars')}</span> ·{' '}
        <Link href={withLang(lang, '/explore')} className="link-editorial">
          {t(lang, 'explore.back_to_index')}
        </Link>
      </p>
    );
  }

  // variant === 'platform' — kind is required
  if (variant === 'platform' && kind) {
    return (
      <p className="text-[12.5px] text-fg-2">
        <span className="font-mono text-muted">[ {kind} ]</span>{' '}
        {t(lang, 'taxonomy.count', { n: count })} ·{' '}
        <span className="font-mono text-muted">{t(lang, 'explore.sorted_by_stars')}</span> ·{' '}
        <Link href={withLang(lang, `/explore/k/${kind}`)} className="link-editorial">
          {t(lang, 'explore.back_to_kind', { kind: kindLabel(kind, lang) })}
        </Link>
      </p>
    );
  }

  return null;
}
