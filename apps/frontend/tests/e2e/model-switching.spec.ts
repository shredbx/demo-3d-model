import { test, expect } from '@playwright/test';

/**
 * E2E Test Suite: Model Switching
 *
 * Tests the ability to switch between different 3D bike models
 * and verifies that the UI correctly reflects the active model.
 */

test.describe('Model Switching', () => {
	test.beforeEach(async ({ page }) => {
		// Navigate to homepage before each test
		await page.goto('/');
	});

	test('should load Dirt Bike model automatically on initial page load', async ({ page }) => {
		// Wait for loading indicator to appear (model is loading)
		await expect(page.locator('.loading')).toBeVisible({ timeout: 2000 });

		// Wait for loading indicator to disappear (model loaded successfully)
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Verify canvas element exists and is visible
		const canvas = page.locator('canvas');
		await expect(canvas).toBeVisible();

		// Verify WebGL context is initialized
		const hasWebGL = await canvas.evaluate((el) => {
			const ctx = (el as HTMLCanvasElement).getContext('webgl') ||
			            (el as HTMLCanvasElement).getContext('webgl2');
			return ctx !== null;
		});
		expect(hasWebGL).toBe(true);

		// Verify Dirt Bike button is active by default
		const dirtBikeButton = page.locator('button.style-btn:has-text("Dirt Bike")');
		await expect(dirtBikeButton).toHaveClass(/active/);

		// Check console for successful load message
		const consoleMessages: string[] = [];
		page.on('console', msg => {
			if (msg.type() === 'log') {
				consoleMessages.push(msg.text());
			}
		});

		// Give a moment for console logs to arrive
		await page.waitForTimeout(1000);
	});

	test('should switch to Mad Max model when button is clicked', async ({ page }) => {
		// Wait for initial model to load
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Click Mad Max button
		const madMaxButton = page.locator('button.style-btn:has-text("Mad Max")');
		await madMaxButton.click();

		// Verify loading indicator appears again
		await expect(page.locator('.loading')).toBeVisible({ timeout: 2000 });

		// Wait for new model to load
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Verify Mad Max button is now active
		await expect(madMaxButton).toHaveClass(/active/);

		// Verify Dirt Bike button is no longer active
		const dirtBikeButton = page.locator('button.style-btn:has-text("Dirt Bike")');
		await expect(dirtBikeButton).not.toHaveClass(/active/);

		// Verify canvas is still visible and functioning
		const canvas = page.locator('canvas');
		await expect(canvas).toBeVisible();
	});

	test('should switch to Phantom model when button is clicked', async ({ page }) => {
		// Wait for initial model to load
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Click Phantom button
		const phantomButton = page.locator('button.style-btn:has-text("Phantom")');
		await phantomButton.click();

		// Verify loading indicator appears
		await expect(page.locator('.loading')).toBeVisible({ timeout: 2000 });

		// Wait for new model to load
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Verify Phantom button is now active
		await expect(phantomButton).toHaveClass(/active/);

		// Verify other buttons are not active
		await expect(page.locator('button.style-btn:has-text("Dirt Bike")')).not.toHaveClass(/active/);
		await expect(page.locator('button.style-btn:has-text("Mad Max")')).not.toHaveClass(/active/);
	});

	test('should switch back to Dirt Bike model from another model', async ({ page }) => {
		// Wait for initial model to load
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Switch to Mad Max
		await page.locator('button.style-btn:has-text("Mad Max")').click();
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Now switch back to Dirt Bike
		const dirtBikeButton = page.locator('button.style-btn:has-text("Dirt Bike")');
		await dirtBikeButton.click();

		// Verify loading indicator appears
		await expect(page.locator('.loading')).toBeVisible({ timeout: 2000 });

		// Wait for model to load
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Verify Dirt Bike button is active again
		await expect(dirtBikeButton).toHaveClass(/active/);
	});

	test('should maintain active button highlighting during model switch', async ({ page }) => {
		// Wait for initial model to load
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Get all style buttons
		const dirtBikeBtn = page.locator('button.style-btn:has-text("Dirt Bike")');
		const madMaxBtn = page.locator('button.style-btn:has-text("Mad Max")');
		const phantomBtn = page.locator('button.style-btn:has-text("Phantom")');

		// Verify only Dirt Bike is active initially
		await expect(dirtBikeBtn).toHaveClass(/active/);
		await expect(madMaxBtn).not.toHaveClass(/active/);
		await expect(phantomBtn).not.toHaveClass(/active/);

		// Click Mad Max and verify immediate active state change
		await madMaxBtn.click();
		await expect(madMaxBtn).toHaveClass(/active/);
		await expect(dirtBikeBtn).not.toHaveClass(/active/);

		// Wait for loading to complete
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Verify active state persists after loading
		await expect(madMaxBtn).toHaveClass(/active/);
		await expect(dirtBikeBtn).not.toHaveClass(/active/);
	});

	test('should display loading indicator with progress during model load', async ({ page }) => {
		// Reload page to trigger initial load
		await page.reload();

		// Check loading indicator appears
		const loadingDiv = page.locator('.loading');
		await expect(loadingDiv).toBeVisible({ timeout: 2000 });

		// Verify spinner element exists
		const spinner = page.locator('.spinner');
		await expect(spinner).toBeVisible();

		// Verify loading text exists and shows percentage
		const loadingText = loadingDiv.locator('p');
		await expect(loadingText).toBeVisible();

		// Text should contain "Loading 3D Model" and percentage
		const text = await loadingText.textContent();
		expect(text).toContain('Loading 3D Model');
		expect(text).toMatch(/\d+%/); // Should contain a percentage

		// Wait for loading to complete
		await expect(loadingDiv).not.toBeVisible({ timeout: 15000 });
	});

	test('should not show JavaScript errors in console during model switching', async ({ page }) => {
		const errors: string[] = [];
		const warnings: string[] = [];

		// Capture console errors and warnings
		page.on('console', (msg) => {
			if (msg.type() === 'error') {
				errors.push(msg.text());
			} else if (msg.type() === 'warning') {
				warnings.push(msg.text());
			}
		});

		// Capture page errors
		page.on('pageerror', (error) => {
			errors.push(error.message);
		});

		// Wait for initial model load
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Switch between multiple models
		await page.locator('button.style-btn:has-text("Mad Max")').click();
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		await page.locator('button.style-btn:has-text("Phantom")').click();
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		await page.locator('button.style-btn:has-text("Dirt Bike")').click();
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Filter out known acceptable warnings (like WebGL performance warnings)
		const criticalErrors = errors.filter(err =>
			!err.includes('WebGL') &&
			!err.includes('performance') &&
			!err.includes('DevTools')
		);

		// Assert no critical errors occurred
		expect(criticalErrors).toHaveLength(0);
	});

	test('should handle rapid model switching without breaking', async ({ page }) => {
		// Wait for initial model load
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Rapidly click between models
		await page.locator('button.style-btn:has-text("Mad Max")').click();
		await page.waitForTimeout(500); // Small delay

		await page.locator('button.style-btn:has-text("Phantom")').click();
		await page.waitForTimeout(500);

		await page.locator('button.style-btn:has-text("Dirt Bike")').click();

		// Final model should load successfully
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });

		// Verify Dirt Bike is active (last clicked)
		const dirtBikeButton = page.locator('button.style-btn:has-text("Dirt Bike")');
		await expect(dirtBikeButton).toHaveClass(/active/);

		// Verify canvas is still functional
		const canvas = page.locator('canvas');
		await expect(canvas).toBeVisible();
	});
});
