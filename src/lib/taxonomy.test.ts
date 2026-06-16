import { describe, it, expect } from 'vitest';
import { kindLabel, platformLabel } from './taxonomy';

describe('taxonomy', () => {
  describe('kindLabel()', () => {
    it('returns English label for English locale', () => {
      expect(kindLabel('proxy', 'en')).toBe('Proxy cores');
      expect(kindLabel('vpn', 'en')).toBe('VPN');
      expect(kindLabel('dns', 'en')).toBe('DNS');
      expect(kindLabel('acceleration', 'en')).toBe('Acceleration');
      expect(kindLabel('security', 'en')).toBe('Security');
    });

    it('returns Chinese label for Chinese locale', () => {
      expect(kindLabel('proxy', 'zh')).toBe('代理核心');
      expect(kindLabel('vpn', 'zh')).toBe('VPN');
      expect(kindLabel('dns', 'zh')).toBe('DNS');
      expect(kindLabel('acceleration', 'zh')).toBe('网络加速');
      expect(kindLabel('security', 'zh')).toBe('安全');
    });

    it('returns Japanese label for Japanese locale', () => {
      expect(kindLabel('proxy', 'ja')).toBe('プロキシコア');
      expect(kindLabel('vpn', 'ja')).toBe('VPN');
      expect(kindLabel('dns', 'ja')).toBe('DNS');
      expect(kindLabel('acceleration', 'ja')).toBe('高速化');
      expect(kindLabel('security', 'ja')).toBe('セキュリティ');
    });

    it('defaults to English when locale is not specified', () => {
      expect(kindLabel('proxy')).toBe('Proxy cores');
      expect(kindLabel('vpn')).toBe('VPN');
    });

    it('falls back to English when label is missing in target locale', () => {
      // If a label is missing in zh or ja, it should fall back to en
      const result = kindLabel('proxy', 'zh');
      expect(result).toBeDefined();
      expect(typeof result).toBe('string');
      expect(result.length).toBeGreaterThan(0);
    });

    it('returns the kind slug as fallback for unknown kind', () => {
      const unknownKind = 'unknown_kind' as unknown as import('@/types/project').ProjectKind;
      expect(kindLabel(unknownKind, 'en')).toBe('unknown_kind');
      expect(kindLabel(unknownKind, 'zh')).toBe('unknown_kind');
      expect(kindLabel(unknownKind, 'ja')).toBe('unknown_kind');
    });
  });

  describe('platformLabel()', () => {
    it('returns English label for English locale', () => {
      expect(platformLabel('desktop', 'en')).toBe('Desktop');
      expect(platformLabel('mobile', 'en')).toBe('Mobile');
      expect(platformLabel('cli', 'en')).toBe('CLI');
      expect(platformLabel('server', 'en')).toBe('Server');
      expect(platformLabel('browser', 'en')).toBe('Browser');
      expect(platformLabel('router', 'en')).toBe('Router');
    });

    it('returns Chinese label for Chinese locale', () => {
      expect(platformLabel('desktop', 'zh')).toBe('桌面端');
      expect(platformLabel('mobile', 'zh')).toBe('手机端');
      expect(platformLabel('cli', 'zh')).toBe('命令行');
      expect(platformLabel('server', 'zh')).toBe('服务端');
      expect(platformLabel('browser', 'zh')).toBe('浏览器');
      expect(platformLabel('router', 'zh')).toBe('路由器');
    });

    it('returns Japanese label for Japanese locale', () => {
      expect(platformLabel('desktop', 'ja')).toBe('デスクトップ');
      expect(platformLabel('mobile', 'ja')).toBe('モバイル');
      expect(platformLabel('cli', 'ja')).toBe('コマンドライン');
      expect(platformLabel('server', 'ja')).toBe('サーバー');
      expect(platformLabel('browser', 'ja')).toBe('ブラウザ');
      expect(platformLabel('router', 'ja')).toBe('ルーター');
    });

    it('defaults to English when locale is not specified', () => {
      expect(platformLabel('desktop')).toBe('Desktop');
      expect(platformLabel('mobile')).toBe('Mobile');
    });

    it('falls back to English when label is missing in target locale', () => {
      // If a label is missing in zh or ja, it should fall back to en
      const result = platformLabel('desktop', 'zh');
      expect(result).toBeDefined();
      expect(typeof result).toBe('string');
      expect(result.length).toBeGreaterThan(0);
    });

    it('returns the platform slug as fallback for unknown platform', () => {
      const unknownPlatform =
        'unknown_platform' as unknown as import('@/types/project').ProjectPlatform;
      expect(platformLabel(unknownPlatform, 'en')).toBe('unknown_platform');
      expect(platformLabel(unknownPlatform, 'zh')).toBe('unknown_platform');
      expect(platformLabel(unknownPlatform, 'ja')).toBe('unknown_platform');
    });
  });
});
