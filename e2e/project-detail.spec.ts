import { test, expect } from '@playwright/test';

test.describe('Project Detail Page', () => {
  test('should load project detail successfully', async ({ page }) => {
    // Navigate to explore and click first project
    await page.goto('/explore');
    const firstCard = page.locator('a[href*="/explore/project/"]').first();
    await firstCard.click();

    // Should show project details — the project name is rendered
    // as the page's main heading.
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('should show the "View Repository" link pointing at GitHub', async ({ page }) => {
    await page.goto('/explore');
    const firstCard = page.locator('a[href*="/explore/project/"]').first();
    await firstCard.click();

    const repoLink = page.locator('a[href*="github.com"]').first();
    await expect(repoLink).toBeVisible();
  });

  test('should show related projects section when present', async ({ page }) => {
    await page.goto('/explore');
    const firstCard = page.locator('a[href*="/explore/project/"]').first();
    await firstCard.click();

    // The detail page renders a "Related Projects" section
    // when the project has at least one related entry. We
    // assert on the *label text* rather than a data attribute
    // so the test is robust to styling changes.
    const relatedHeading = page.getByText(/Related Projects|相关项目|相关プロジェクト/);
    await expect(relatedHeading).toBeVisible();
  });

  test('should show a back link to the kind page', async ({ page }) => {
    await page.goto('/explore');
    const firstCard = page.locator('a[href*="/explore/project/"]').first();
    await firstCard.click();

    // The detail page renders a "Back to <kind>" link in the
    // actions row.
    const backLink = page.locator('a[href*="/explore/k/"]');
    await expect(backLink.first()).toBeVisible();
  });
});
