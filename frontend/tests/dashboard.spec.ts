import { test, expect } from '@playwright/test';

test('inventory dashboard has nav links', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Inventory Dashboard' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Add Item' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Issue Item' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Return Item' })).toBeVisible();
});

test('add item form fields present', async ({ page }) => {
  await page.goto('/add');
  await expect(page.locator('input#name')).toBeVisible();
  await expect(page.locator('input#quantity')).toBeVisible();
  await expect(page.locator('input#threshold')).toBeVisible();
});
