import { test, expect } from '@playwright/test';

test('stock dashboard shows departments', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Systems Stock' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Systems' })).toBeVisible();
});

test('add item form fields present', async ({ page }) => {
  await page.goto('/add');
  await expect(page.locator('input#name')).toBeVisible();
  await expect(page.locator('input#quantity')).toBeVisible();
  await expect(page.locator('input#threshold')).toBeVisible();
});
