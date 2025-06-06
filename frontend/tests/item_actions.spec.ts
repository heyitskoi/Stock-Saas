import { test, expect } from '@playwright/test';

const departments = [
  { id: 1, name: 'Systems', icon: 'Computer' },
  { id: 2, name: 'Accounts', icon: 'Briefcase' },
];

const categories = [
  { id: 1, name: 'Desktop', department_id: 1 },
  { id: 2, name: 'Supplies', department_id: 2 },
];

const sampleItems = [
  { id: 1, name: 'Widget', quantity: 5, min_par: 2, category_id: 1, department_id: 1, stock_code: 'W-1', status: 'available' },
];

async function setupRoutes(page) {
  await page.route('**/token', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ access_token: 'testtoken' })
  }));
  await page.route('**/departments/**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify(departments)
  }));
  await page.route('**/categories/**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify(categories)
  }));
  await page.route('**/items/status**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify(sampleItems)
  }));
}

test('edit item updates correctly', async ({ page }) => {
  await setupRoutes(page);
  await page.route('**/items/update', route => route.fulfill({ status: 200, body: '{}' }));

  await page.goto('/login');
  await page.fill('#email', 'user@example.com');
  await page.fill('#password', 'pw');
  await page.click('button[type=submit]');

  await page.goto('/edit?name=Widget');
  await page.fill('#newName', 'Updated Widget');
  await page.fill('#threshold', '3');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL('/');
});

test('delete item from dashboard', async ({ page }) => {
  await setupRoutes(page);
  await page.route('**/items/delete', route => route.fulfill({ status: 200, body: '{}' }));

  await page.goto('/login');
  await page.fill('#email', 'user@example.com');
  await page.fill('#password', 'pw');
  await page.click('button[type=submit]');

  await page.getByRole('button', { name: 'Systems' }).click();
  await page.getByRole('button', { name: 'Open menu' }).click();
  await page.getByRole('menuitem', { name: 'Delete' }).click();
  await page.getByRole('button', { name: 'Delete' }).click();
  await expect(page.getByText('Widget')).not.toBeVisible();
});

test('move item between departments and categories', async ({ page }) => {
  await setupRoutes(page);

  await page.goto('/login');
  await page.fill('#email', 'user@example.com');
  await page.fill('#password', 'pw');
  await page.click('button[type=submit]');

  await page.getByRole('button', { name: 'Systems' }).click();
  await page.getByRole('button', { name: 'Open menu' }).click();
  await page.getByRole('menuitem', { name: 'Move to another category' }).click();

  await page.getByLabel('Department').click();
  await page.getByRole('option', { name: 'Accounts' }).click();
  await page.getByLabel('Category').click();
  await page.getByRole('option', { name: 'Supplies' }).click();

  await page.getByRole('button', { name: 'Move Item' }).click();
  await expect(page.getByText('Widget')).not.toBeVisible();
});
