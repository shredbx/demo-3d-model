import { test, expect } from '@playwright/test';

/**
 * Simple screenshot test for 3D models
 *
 * This test:
 * 1. Navigates to the homepage
 * 2. Waits for canvas to be visible
 * 3. Takes screenshots of both models
 *
 * No complex waiting logic - just simple time-based waits
 */

test.describe('3D Model Viewer - Simple Screenshots', () => {
  test('capture both model screenshots', async ({ page }) => {
    console.log('🚀 Starting screenshot test...');

    // Navigate to homepage
    await page.goto('http://localhost:5483');
    console.log('✅ Navigated to homepage');

    // Wait for canvas to be visible
    await page.waitForSelector('[data-testid="model-canvas"]', {
      state: 'visible',
      timeout: 10000
    });
    console.log('✅ Canvas is visible');

    // Wait 5 seconds for Dirt Bike to load
    console.log('⏳ Waiting 5 seconds for Dirt Bike to render...');
    await page.waitForTimeout(5000);

    // Verify Dirt Bike button is active
    const dirtBikeButton = page.locator('button:has-text("🏍️ Dirt Bike")');
    await expect(dirtBikeButton).toHaveClass(/active/);
    console.log('✅ Dirt Bike button is active');

    // Take screenshot of Dirt Bike
    await page.screenshot({
      path: 'apps/frontend/tests/e2e/screenshots/dirt-bike-model.png',
      fullPage: true
    });
    console.log('📸 Dirt Bike screenshot saved');

    // Click Road Bike button
    const roadBikeButton = page.locator('button:has-text("🏍️ Road Bike")');
    await roadBikeButton.click();
    console.log('🖱️ Clicked Road Bike button');

    // Wait 10 seconds for Road Bike to load (it's 33MB)
    console.log('⏳ Waiting 10 seconds for Road Bike to render...');
    await page.waitForTimeout(10000);

    // Verify Road Bike button is active
    await expect(roadBikeButton).toHaveClass(/active/);
    console.log('✅ Road Bike button is active');

    // Take screenshot of Road Bike
    await page.screenshot({
      path: 'apps/frontend/tests/e2e/screenshots/road-bike-model.png',
      fullPage: true
    });
    console.log('📸 Road Bike screenshot saved');

    console.log('✅ Test completed successfully!');
  });
});
