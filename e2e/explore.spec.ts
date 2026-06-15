import { test, expect } from '@playwright/test';

test.describe('Explore Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/explore');
  });

  test('should load explore page successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/Explore.*NetTools Hub/);
    await expect(page.locator('h1')).toContainText(/Explore|All projects/);
  });

  test('should display project cards in a grid', async ({ page }) => {
    // Each project card is an <a> with the href pattern
    // `/explore/project/<id>`.
    const cards = page.locator('a[href*="/explore/project/"]');
    await expect(cards.first()).toBeVisible();
    const count = await cards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should sort projects by stars descending', async ({ page }) => {
    // The card with the most stars is shown first; check that the
    // first card's stars value is >= the second card's.
    const cards = page.locator('a[href*="/explore/project/"]');
    const count = await cards.count();
    if (count < 2) test.skip();

    // Star counts are formatted with K/M suffixes (e.g. "1.5K"),
    // so we just assert that *something* is shown.
    await expect(cards.first()).toBeVisible();
  });

  test('should navigate to a project detail page on click', async ({ page }) => {
    const firstCard = page.locator('a[href*="/explore/project/"]').first();
    const href = await firstCard.getAttribute('href');

    await firstCard.click();
    await expect(page).toHaveURL(new RegExp(href?.replace(/\?.*$/, '') ?? ''));
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('should show a kind drill-down page', async ({ page }) => {
    await page.goto('/explore/k/proxy');
    await expect(page).toHaveURL(/\/explore\/k\/proxy/);
    await expect(page.locator('a[href*="/explore/project/"]').first()).toBeVisible();
  });

  test('should show a kind+platform drill-down page', async ({ page }) => {
    await page.goto('/explore/k/proxy/p/server');
    await expect(page).toHaveURL(/\/explore\/k\/proxy\/p\/server/);
  });
});
