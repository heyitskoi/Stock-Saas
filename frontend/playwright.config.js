/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config = {
  testDir: './tests',
  timeout: 60000,
  webServer: {
    command: 'npm run build && npx next start -p 3000',
    port: 3000,
    reuseExistingServer: true,
    timeout: 120 * 1000,
  },
  use: {
    baseURL: 'http://localhost:3000',
  },
};
module.exports = config;
