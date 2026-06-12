import { test, expect } from '@playwright/test';

test.describe('Responsive Design', () => {
  test.describe('Mobile viewport', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test('should display mobile navigation', async ({ page }) => {
      await page.goto('/');
      const mobileNav = page.locator('[data-testid="mobile-nav"]');
      await expect(mobileNav).toBeVisible();
    });

    test('should stack project table on mobile', async ({ page }) => {
      await page.goto('/explore');
      
      // Table should be visible but in mobile layout
      const table = page.locator('[data-testid="project-table"]');
      await expect(table).toBeVisible();
      
      // Check if table has mobile-specific styling
      const firstRow = page.locator('[data-testid="project-row"]').first();
      const display = await firstRow.evaluate(el => window.getComputedStyle(el).display);
      expect(display).toBe('block');
    });
  });

  test.describe('Tablet viewport', () => {
    test.use({ viewport: { width: 768, height: 1024 } });

    test('should display tablet layout', async ({ page }) => {
      await page.goto('/explore');
      
      // Should show both sidebar and content
      const sidebar = page.locator('[data-testid="sidebar"]');
      const content = page.locator('[data-testid="main-content"]');
      
      await expect(sidebar).toBeVisible();
      await expect(content).toBeVisible();
    });
  });

  test.describe('Desktop viewport', () => {
    test.use({ viewport: { width: 1920, height: 1080 } });

    test('should display desktop layout', async ({ page }) => {
      await page.goto('/explore');
      
      // Should show full table with all columns
      const table = page.locator('[data-testid="project-table"]');
      await expect(table).toBeVisible();
      
      // Check table has desktop layout
      const firstRow = page.locator('[data-testid="project-row"]').first();
      const display = await firstRow.evaluate(el => window.getComputedStyle(el).display);
      expect(display).toBe('table-row');
    });
  });
});
