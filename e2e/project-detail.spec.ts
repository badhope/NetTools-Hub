import { test, expect } from '@playwright/test';

test.describe('Project Detail Page', () => {
  test('should load project detail successfully', async ({ page }) => {
    // Navigate to explore and click first project
    await page.goto('/explore');
    const firstProjectLink = page.locator('[data-testid="project-row"]').first().locator('a');
    await firstProjectLink.click();
    
    // Should show project details
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('[data-testid="project-description"]')).toBeVisible();
  });

  test('should display project metadata', async ({ page }) => {
    await page.goto('/explore');
    const firstProjectLink = page.locator('[data-testid="project-row"]').first().locator('a');
    await firstProjectLink.click();
    
    // Should show stars, forks, language
    await expect(page.locator('[data-testid="stars"]')).toBeVisible();
    await expect(page.locator('[data-testid="language"]')).toBeVisible();
  });

  test('should navigate back to explore', async ({ page }) => {
    await page.goto('/explore');
    const firstProjectLink = page.locator('[data-testid="project-row"]').first().locator('a');
    await firstProjectLink.click();
    
    // Click back button
    await page.click('[data-testid="back-button"]');
    await expect(page).toHaveURL(/\/explore/);
  });

  test('should display related projects', async ({ page }) => {
    await page.goto('/explore');
    const firstProjectLink = page.locator('[data-testid="project-row"]').first().locator('a');
    await firstProjectLink.click();
    
    // Should show related projects section
    const relatedSection = page.locator('[data-testid="related-projects"]');
    await expect(relatedSection).toBeVisible();
  });
});
