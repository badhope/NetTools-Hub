import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/NetTools Hub/);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should display language switcher', async ({ page }) => {
    await page.goto('/');
    // The language switcher is a button with the
    // aria-label "Switch language" / "切换语言" / "言語切替".
    const langSwitcher = page.getByRole('button', {
      name: /Switch language|切换语言|言語切替/,
    });
    await expect(langSwitcher).toBeVisible();
  });

  test('should switch language to Chinese', async ({ page }) => {
    await page.goto('/');
    const langSwitcher = page.getByRole('button', {
      name: /Switch language|切换语言|言語切替/,
    });
    await langSwitcher.click();
    await page.getByRole('option', { name: '中文' }).click();
    await expect(page.locator('html')).toHaveAttribute('lang', 'zh-Hans');
  });

  test('should navigate to explore page', async ({ page }) => {
    await page.goto('/');
    // The landing page has a "kind" link in the hero that points
    // to the proxy kind page, plus a kind-card grid. Either is a
    // valid path into /explore; we click the kind card.
    const kindLink = page.locator('a[href*="/explore/k/"]').first();
    await kindLink.click();
    await expect(page).toHaveURL(/\/explore\/k\//);
  });
});
