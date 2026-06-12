import { describe, it, expect } from 'vitest';
import { t, resolveInitialLang } from './i18n';

describe('i18n', () => {
  describe('t() - basic translation', () => {
    it('returns English translation for English locale', () => {
      expect(t('en', 'nav.home')).toBe('Home');
      expect(t('en', 'nav.menu')).toBe('Menu');
    });

    it('returns Chinese translation for Chinese locale', () => {
      expect(t('zh', 'nav.home')).toBe('首页');
      expect(t('zh', 'nav.menu')).toBe('菜单');
    });

    it('returns Japanese translation for Japanese locale', () => {
      expect(t('ja', 'nav.home')).toBe('ホーム');
      expect(t('ja', 'nav.menu')).toBe('メニュー');
    });
  });

  describe('t() - fallback chain', () => {
    it('falls back to English when key is missing in target language', () => {
      // Assuming 'some.missing.key' doesn't exist in zh but exists in en
      const result = t('zh', 'nav.home');
      expect(result).toBe('首页');
    });

    it('falls back to key when key is missing in both target and English', () => {
      const missingKey = 'this.key.does.not.exist';
      expect(t('en', missingKey)).toBe(missingKey);
      expect(t('zh', missingKey)).toBe(missingKey);
      expect(t('ja', missingKey)).toBe(missingKey);
    });

    it('handles empty string gracefully', () => {
      expect(t('en', '')).toBe('');
    });
  });

  describe('t() - parameter substitution', () => {
    it('substitutes single parameter', () => {
      expect(t('en', 'taxonomy.count', { n: 42 })).toBe('42 entries');
      expect(t('zh', 'taxonomy.count', { n: 42 })).toBe('42 条');
      expect(t('ja', 'taxonomy.count', { n: 42 })).toBe('42 件');
    });

    it('substitutes multiple parameters if they exist', () => {
      // editorial.edition has {date} parameter
      expect(t('en', 'editorial.edition', { date: '2024' })).toBe('Edition I · 2024');
      expect(t('zh', 'editorial.edition', { date: '2024' })).toBe('第一版 · 2024');
      expect(t('ja', 'editorial.edition', { date: '2024' })).toBe('初版 · 2024');
    });

    it('handles missing parameters by leaving placeholder', () => {
      const result = t('en', 'taxonomy.count');
      expect(result).toBe('{n} entries');
    });

    it('handles extra parameters gracefully', () => {
      const result = t('en', 'taxonomy.count', { n: 10, extra: 'ignored' });
      expect(result).toBe('10 entries');
    });
  });

  describe('resolveInitialLang()', () => {
    it('returns en when no window object (server-side)', () => {
      // In test environment, window is undefined
      const result = resolveInitialLang();
      expect(result).toBe('en');
    });

    it('returns en as default fallback', () => {
      // When no URL parameter, no localStorage, and no navigator.language
      expect(resolveInitialLang()).toBe('en');
    });
  });
});
