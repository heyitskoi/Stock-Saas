import { test, expect } from '@playwright/test';

test('stock dashboard shows departments and allows adding one', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Add Department' }).click();
  await page.getByPlaceholder('Department Name').fill('QA');
  await page.getByRole('button', { name: 'Add' }).click();
  await expect(page.getByRole('button', { name: 'QA' })).toBeVisible();
});

test('add item form fields present', async ({ page }) => {
  await page.goto('/add');
  await expect(page.locator('input#name')).toBeVisible();
  await expect(page.locator('input#quantity')).toBeVisible();
  await expect(page.locator('input#threshold')).toBeVisible();
});
