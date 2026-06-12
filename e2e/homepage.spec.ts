import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/NetTools Hub/);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should display language switcher', async ({ page }) => {
    await page.goto('/');
    const langSwitcher = page.locator('[data-testid="language-switcher"]');
    await expect(langSwitcher).toBeVisible();
  });

  test('should switch language to Chinese', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="language-switcher"]');
    await page.click('button:has-text("中文")');
    await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN');
  });

  test('should navigate to explore page', async ({ page }) => {
    await page.goto('/');
    await page.click('a[href="/explore"]');
    await expect(page).toHaveURL(/\/explore/);
    await expect(page.locator('h1')).toContainText('Explore');
  });
});
