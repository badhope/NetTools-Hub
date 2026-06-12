import { test, expect } from '@playwright/test';

test.describe('Explore Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/explore');
  });

  test('should load explore page successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/Explore.*NetTools Hub/);
    await expect(page.locator('h1')).toContainText('Explore');
  });

  test('should display project table', async ({ page }) => {
    const table = page.locator('[data-testid="project-table"]');
    await expect(table).toBeVisible();
    
    // Should have at least one project row
    const rows = page.locator('[data-testid="project-row"]');
    await expect(rows.first()).toBeVisible();
  });

  test('should filter projects by search', async ({ page }) => {
    const searchInput = page.locator('[data-testid="search-input"]');
    await searchInput.fill('clash');
    
    // Wait for filtering to complete
    await page.waitForTimeout(500);
    
    // Should show filtered results
    const rows = page.locator('[data-testid="project-row"]');
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);
    
    // All visible rows should contain "clash"
    for (let i = 0; i < count; i++) {
      const text = await rows.nth(i).textContent();
      expect(text?.toLowerCase()).toContain('clash');
    }
  });

  test('should filter by category', async ({ page }) => {
    const categoryFilter = page.locator('[data-testid="category-filter"]');
    await categoryFilter.selectOption('proxy');
    
    // Wait for filtering
    await page.waitForTimeout(500);
    
    // Should show filtered results
    const rows = page.locator('[data-testid="project-row"]');
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should sort projects', async ({ page }) => {
    const sortSelect = page.locator('[data-testid="sort-select"]');
    await sortSelect.selectOption('stars');
    
    // Wait for sorting
    await page.waitForTimeout(500);
    
    // First row should have highest stars
    const firstRow = page.locator('[data-testid="project-row"]').first();
    const starsText = await firstRow.locator('[data-testid="stars"]').textContent();
    expect(starsText).toBeTruthy();
  });

  test('should navigate to project detail', async ({ page }) => {
    const firstProjectLink = page.locator('[data-testid="project-row"]').first().locator('a');
    const href = await firstProjectLink.getAttribute('href');
    
    await firstProjectLink.click();
    await expect(page).toHaveURL(new RegExp(href || ''));
    
    // Should show project details
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should display empty state when no results', async ({ page }) => {
    const searchInput = page.locator('[data-testid="search-input"]');
    await searchInput.fill('xyznonexistent123');
    
    await page.waitForTimeout(500);
    
    const emptyState = page.locator('[data-testid="empty-state"]');
    await expect(emptyState).toBeVisible();
  });
});
