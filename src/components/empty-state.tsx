import { Lang, t } from '@/lib/i18n';
import Link from 'next/link';

interface EmptyStateProps {
  title?: string;
  description?: string;
  lang: Lang;
}

/**
 * Generic empty state component for when no projects match
 * the current filters. Provides a clear message and a link
 * back to the full project list.
 */
export function EmptyState({ title, description, lang }: EmptyStateProps) {
  return (
    <div className="py-16 text-center" role="status" aria-label="No results">
      <p className="kicker">{title ?? t(lang, 'empty.title')}</p>
      <p className="mt-2 text-fg-2">{description ?? t(lang, 'empty.description')}</p>
      <Link href="/explore" className="link-editorial mt-4 inline-block">
        {t(lang, 'empty.back')}
      </Link>
    </div>
  );
}
