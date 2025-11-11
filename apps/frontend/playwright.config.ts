import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for ShredBX E2E tests
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
	testDir: './tests/e2e',
	fullyParallel: true,
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 2 : 0,
	workers: process.env.CI ? 1 : undefined,
	reporter: 'html',
	timeout: 60000, // 60 seconds per test (models can take time to load)
	expect: {
		timeout: 10000 // 10 seconds for assertions
	},

	use: {
		baseURL: 'http://localhost:5483',
		trace: 'on-first-retry',
		screenshot: 'only-on-failure',
		video: 'retain-on-failure'
	},

	projects: [
		{
			name: 'chromium',
			use: { ...devices['Desktop Chrome'] }
		},

		{
			name: 'firefox',
			use: { ...devices['Desktop Firefox'] }
		},

		{
			name: 'webkit',
			use: { ...devices['Desktop Safari'] }
		},

		// Mobile viewports
		{
			name: 'Mobile Chrome',
			use: { ...devices['Pixel 5'] }
		},
		{
			name: 'Mobile Safari',
			use: { ...devices['iPhone 12'] }
		}
	],

	// Run local dev server before starting tests
	webServer: {
		command: 'npm run dev',
		url: 'http://localhost:5483',
		reuseExistingServer: !process.env.CI,
		timeout: 120000
	}
});
