import { test, expect } from '@playwright/test';

const sampleItems = [
  { id: 1, name: 'Widget', quantity: 10, min_par: 2, category_id: 1, department_id: 1, stock_code: 'W-1', status: 'available' }
];

test('dashboard workflow login -> view -> add -> issue', async ({ page }) => {
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
  await page.route('**/items/add', route => route.fulfill({ status: 200, body: '{}' }));
  await page.route('**/items/issue', route => route.fulfill({ status: 200, body: '{}' }));

  await page.goto('/login');
  await page.fill('#email', 'user@example.com');
  await page.fill('#password', 'pw');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL('/');
  await expect(page.getByText('Widget')).toBeVisible();

  await page.goto('/add');
  await page.fill('#name', 'New Item');
  await page.fill('#quantity', '5');
  await page.fill('#threshold', '1');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL('/');

  await page.goto('/issue');
  await page.fill('#name', 'Widget');
  await page.fill('#quantity', '2');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL('/');
});
