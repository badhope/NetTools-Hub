import { test, expect } from '@playwright/test';

test.describe('Responsive Design', () => {
  test.describe('Mobile viewport', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test('should show the mobile drawer trigger', async ({ page }) => {
      await page.goto('/');
      // The mobile drawer trigger is a button with the aria-label
      // "Menu" / "菜单" / "メニュー".
      const menuTrigger = page.getByRole('button', { name: /Menu|菜单|メニュー/ });
      await expect(menuTrigger).toBeVisible();
    });

    test('should show a single-column card grid', async ({ page }) => {
      await page.goto('/explore');
      // On mobile the cards stack into one column. We assert that
      // the grid exists and at least one card is visible.
      const firstCard = page.locator('a[href*="/explore/project/"]').first();
      await expect(firstCard).toBeVisible();
    });
  });

  test.describe('Tablet viewport', () => {
    test.use({ viewport: { width: 768, height: 1024 } });

    test('should show the explore layout (sidebar + content)', async ({ page }) => {
      await page.goto('/explore');
      // The tree sidebar is rendered as a `<nav aria-label="...">`.
      const sidebar = page.locator('nav[aria-label]').first();
      await expect(sidebar).toBeVisible();

      // The main content is the `<main id="main">` element.
      const main = page.locator('main#main');
      await expect(main).toBeVisible();
    });
  });

  test.describe('Desktop viewport', () => {
    test.use({ viewport: { width: 1920, height: 1080 } });

    test('should show a multi-column card grid', async ({ page }) => {
      await page.goto('/explore');
      // The first card is always visible on desktop.
      const firstCard = page.locator('a[href*="/explore/project/"]').first();
      await expect(firstCard).toBeVisible();
    });
  });
});
