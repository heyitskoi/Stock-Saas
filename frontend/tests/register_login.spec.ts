import { test, expect } from '@playwright/test';

const sampleItems = [
  { id: 1, name: 'Widget', quantity: 5, min_par: 2, category_id: 1, department_id: 1, stock_code: 'W-1', status: 'available' }
];

test('register account then login as admin', async ({ page }) => {
  await page.route('**/auth/register', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ user: { id: 1, username: 'admin@example.com', tenant_id: 1 } })
  }));
  await page.route('**/token', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ access_token: 'testtoken' })
  }));
  await page.route('**/items/status**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify(sampleItems)
  }));

  await page.goto('/register');
  await page.fill('#email', 'admin@example.com');
  await page.fill('#password', 'pw');
  await page.fill('#confirmPassword', 'pw');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL('/login');

  await page.fill('#email', 'admin@example.com');
  await page.fill('#password', 'pw');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL('/');
  await expect(page.getByText('Widget')).toBeVisible();
});
