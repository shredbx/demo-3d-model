import { test, expect } from '@playwright/test';

/**
 * E2E Test: 3D Model Screenshots
 *
 * Purpose: Capture visual screenshots of both Dirt Bike and Road Bike models
 * to verify their positioning, appearance, and rendering quality.
 *
 * Context:
 * - Dirt Bike model: ~5MB, loads relatively fast
 * - Road Bike model: ~33MB, requires additional loading time
 * - Both models should be centered and properly positioned in the scene
 *
 * Test Flow:
 * 1. Navigate to homepage
 * 2. Wait for Dirt Bike model to fully render
 * 3. Capture Dirt Bike screenshot
 * 4. Switch to Road Bike
 * 5. Wait for Road Bike model to fully render (longer timeout)
 * 6. Capture Road Bike screenshot
 * 7. Verify both model buttons are present
 */

test.describe('3D Model Viewer - Visual Testing', () => {
  test.beforeEach(async ({ page }) => {
    // Increase default timeout for this test suite due to large model loading
    test.setTimeout(120000); // 2 minutes total timeout
  });

  test('should capture screenshots of both models', async ({ page }) => {
    // Step 1: Navigate to the homepage
    await page.goto('http://localhost:5483', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });

    // Step 2: Wait for initial Dirt Bike model to load
    console.log('Waiting for Dirt Bike model to load...');

    // Wait for the loading spinner to appear first (confirming load has started)
    await page.waitForSelector('[data-testid="loading-spinner"]', {
      state: 'visible',
      timeout: 10000
    });

    // Wait for the loading spinner to disappear (model loaded)
    await page.waitForSelector('[data-testid="loading-spinner"]', {
      state: 'hidden',
      timeout: 30000
    });

    // Additional wait for Three.js to fully render the scene
    // Three.js needs time after the GLB loads to:
    // - Initialize materials and textures
    // - Position the camera
    // - Render the first frame
    console.log('Waiting for Dirt Bike Three.js rendering...');
    await page.waitForTimeout(2000);

    // Verify canvas is visible before taking screenshot
    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible();

    // Step 3: Capture Dirt Bike screenshot
    console.log('Capturing Dirt Bike screenshot...');
    await page.screenshot({
      path: 'apps/frontend/tests/e2e/screenshots/dirt-bike-model.png',
      fullPage: true
    });

    // Step 4: Click the Road Bike button to switch models
    console.log('Switching to Road Bike model...');
    const roadBikeButton = page.locator('button:has-text("🏍️ Road Bike")');

    // Verify button exists before clicking
    await expect(roadBikeButton).toBeVisible();
    await roadBikeButton.click();

    // Step 5: Wait for Road Bike model to load (longer timeout due to 33MB size)
    console.log('Waiting for Road Bike model to load (this may take longer - 33MB file)...');

    // Wait for loading spinner to appear (confirming switch initiated)
    await page.waitForSelector('[data-testid="loading-spinner"]', {
      state: 'visible',
      timeout: 5000
    });

    // Wait for loading spinner to disappear (model loaded)
    // Road Bike is much larger, so increase timeout
    await page.waitForSelector('[data-testid="loading-spinner"]', {
      state: 'hidden',
      timeout: 60000 // 60 seconds for the 33MB model
    });

    // Additional wait for Three.js rendering (Road Bike needs more time)
    // The larger model requires more processing time for:
    // - Geometry parsing
    // - Texture decompression
    // - Material setup
    // - Initial render pass
    console.log('Waiting for Road Bike Three.js rendering...');
    await page.waitForTimeout(3000); // 3 seconds for the larger model

    // Verify canvas is still visible
    await expect(canvas).toBeVisible();

    // Step 6: Capture Road Bike screenshot
    console.log('Capturing Road Bike screenshot...');
    await page.screenshot({
      path: 'apps/frontend/tests/e2e/screenshots/road-bike-model.png',
      fullPage: true
    });

    // Step 7: Verify both model buttons are present and accessible
    console.log('Verifying both model buttons exist...');
    const dirtBikeButton = page.locator('button:has-text("🏍️ Dirt Bike")');

    await expect(dirtBikeButton).toBeVisible();
    await expect(roadBikeButton).toBeVisible();

    console.log('Screenshot test completed successfully!');
  });

  test('should handle model loading failures gracefully', async ({ page }) => {
    // Navigate to homepage
    await page.goto('http://localhost:5483', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });

    // Wait for initial load
    await page.waitForSelector('[data-testid="loading-spinner"]', {
      state: 'visible',
      timeout: 10000
    });

    // Check if error state appears (should not, but good to test)
    const hasError = await page.locator('[data-testid="error-message"]').count();

    if (hasError > 0) {
      const errorMessage = await page.locator('[data-testid="error-message"]').textContent();
      console.warn(`Warning: Error message detected: ${errorMessage}`);

      // Take screenshot of error state for debugging
      await page.screenshot({
        path: 'apps/frontend/tests/e2e/screenshots/error-state.png',
        fullPage: true
      });
    }

    // Verify loading completes or error is handled
    const loadingHidden = await page.waitForSelector('[data-testid="loading-spinner"]', {
      state: 'hidden',
      timeout: 30000
    }).catch(() => null);

    expect(loadingHidden !== null || hasError > 0).toBeTruthy();
  });

  test('should verify canvas dimensions are reasonable', async ({ page }) => {
    // Navigate to homepage
    await page.goto('http://localhost:5483', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });

    // Wait for loading to complete
    await page.waitForSelector('[data-testid="loading-spinner"]', {
      state: 'visible',
      timeout: 10000
    });
    await page.waitForSelector('[data-testid="loading-spinner"]', {
      state: 'hidden',
      timeout: 30000
    });

    // Get canvas dimensions
    const canvas = page.locator('canvas');
    const boundingBox = await canvas.boundingBox();

    // Verify canvas exists and has reasonable dimensions
    expect(boundingBox).not.toBeNull();

    if (boundingBox) {
      // Canvas should have non-zero dimensions
      expect(boundingBox.width).toBeGreaterThan(0);
      expect(boundingBox.height).toBeGreaterThan(0);

      // Canvas should not be too small (minimum 300x300)
      expect(boundingBox.width).toBeGreaterThanOrEqual(300);
      expect(boundingBox.height).toBeGreaterThanOrEqual(300);

      console.log(`Canvas dimensions: ${boundingBox.width}x${boundingBox.height}`);

      // Take a screenshot showing the canvas size
      await page.screenshot({
        path: 'apps/frontend/tests/e2e/screenshots/canvas-dimensions.png',
        fullPage: true
      });
    }
  });
});

/**
 * Test Configuration Notes:
 *
 * Timeouts:
 * - Dirt Bike: 2 seconds post-load (5MB model)
 * - Road Bike: 3 seconds post-load (33MB model)
 * - Overall test: 2 minutes (generous for CI environments)
 *
 * Screenshot Locations:
 * - apps/frontend/tests/e2e/screenshots/dirt-bike-model.png
 * - apps/frontend/tests/e2e/screenshots/road-bike-model.png
 * - apps/frontend/tests/e2e/screenshots/error-state.png (if errors occur)
 * - apps/frontend/tests/e2e/screenshots/canvas-dimensions.png
 *
 * Running the Test:
 * ```bash
 * cd apps/frontend
 * npm run test:e2e -- model-screenshots.spec.ts
 * ```
 *
 * Or run with UI mode for debugging:
 * ```bash
 * npm run test:e2e -- --ui model-screenshots.spec.ts
 * ```
 *
 * Expected Behavior:
 * - Test should pass if both models load successfully
 * - Screenshots should show centered, properly positioned models
 * - Canvas should be visible and have reasonable dimensions
 * - Both model switcher buttons should be present
 *
 * Common Issues:
 * 1. Road Bike timeout: Increase timeout if network is slow
 * 2. Canvas not visible: Check Three.js initialization in onMount
 * 3. Screenshots appear black: Increase post-load wait time
 * 4. Models not centered: Check camera positioning in Three.js setup
 */
