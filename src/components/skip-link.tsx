'use client';

import { t } from '@/lib/i18n';
import { useLang } from '@/components/lang-provider';

/**
 * Skip-to-content link, i18n-aware.
 *
 * The root layout is a Server Component and cannot call `useLang()`,
 * so this small client component reads the active language from the
 * `LangProvider` context and renders the translated label. Visually
 * hidden until focused (see `.skip-link` in globals.css).
 */
export function SkipLink() {
  const { lang } = useLang();
  return (
    <a href="#main" className="skip-link">
      {t(lang, 'a11y.skip_to_content')}
    </a>
  );
}
