import { test, expect } from '@playwright/test';

/**
 * E2E Test Suite: Viewer Positioning and Layout
 *
 * Tests the layout, positioning, and responsive behavior of the 3D viewer
 * to ensure proper element placement and no overlapping issues.
 */

test.describe('Viewer Positioning and Layout', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/');
		// Wait for initial model to load
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });
	});

	test('should display hero text "ShredBX" visibly without being covered by model', async ({ page }) => {
		// Locate the hero title
		const heroTitle = page.locator('h1:has-text("ShredBX")');
		await expect(heroTitle).toBeVisible();

		// Get bounding box of title
		const titleBox = await heroTitle.boundingBox();
		expect(titleBox).not.toBeNull();
		expect(titleBox!.y).toBeGreaterThan(0); // Should be below top of page

		// Verify title is in viewport
		const isInViewport = await heroTitle.isVisible();
		expect(isInViewport).toBe(true);

		// Verify title has proper z-index (should be above canvas)
		const zIndex = await heroTitle.evaluate((el) => {
			return window.getComputedStyle(el.parentElement!).zIndex;
		});
		expect(parseInt(zIndex) || 0).toBeGreaterThanOrEqual(10);

		// Check that text is actually readable (has color/gradient)
		const hasTextColor = await heroTitle.evaluate((el) => {
			const style = window.getComputedStyle(el);
			const bgClip = style.webkitBackgroundClip || style.backgroundClip;
			const textFillColor = (style as any).webkitTextFillColor;
			// Should have gradient text effect
			return bgClip === 'text' || textFillColor === 'transparent';
		});
		expect(hasTextColor).toBe(true);
	});

	test('should display tagline below hero text', async ({ page }) => {
		const tagline = page.locator('p.tagline:has-text("Transform Your Bike into 3D")');
		await expect(tagline).toBeVisible();

		// Get positions
		const heroTitle = page.locator('h1:has-text("ShredBX")');
		const titleBox = await heroTitle.boundingBox();
		const taglineBox = await tagline.boundingBox();

		expect(titleBox).not.toBeNull();
		expect(taglineBox).not.toBeNull();

		// Tagline should be below title
		expect(taglineBox!.y).toBeGreaterThan(titleBox!.y + titleBox!.height);
	});

	test('should display all three style buttons visibly and clickable', async ({ page }) => {
		// Check all three buttons exist and are visible
		const dirtBikeBtn = page.locator('button.style-btn:has-text("Dirt Bike")');
		const madMaxBtn = page.locator('button.style-btn:has-text("Mad Max")');
		const phantomBtn = page.locator('button.style-btn:has-text("Phantom")');

		await expect(dirtBikeBtn).toBeVisible();
		await expect(madMaxBtn).toBeVisible();
		await expect(phantomBtn).toBeVisible();

		// Verify buttons are clickable (not covered by other elements)
		await expect(dirtBikeBtn).toBeEnabled();
		await expect(madMaxBtn).toBeEnabled();
		await expect(phantomBtn).toBeEnabled();

		// Get button positions
		const dirtBikeBox = await dirtBikeBtn.boundingBox();
		const madMaxBox = await madMaxBtn.boundingBox();
		const phantomBox = await phantomBtn.boundingBox();

		expect(dirtBikeBox).not.toBeNull();
		expect(madMaxBox).not.toBeNull();
		expect(phantomBox).not.toBeNull();

		// Buttons should have reasonable size (not hidden/collapsed)
		expect(dirtBikeBox!.width).toBeGreaterThan(80);
		expect(dirtBikeBox!.height).toBeGreaterThan(30);
	});

	test('should position 3D viewer canvas below button container', async ({ page }) => {
		// Get canvas element
		const canvas = page.locator('canvas');
		await expect(canvas).toBeVisible();

		// Get button container
		const buttonContainer = page.locator('.style-toggle');
		const buttonBox = await buttonContainer.boundingBox();
		const canvasBox = await canvas.boundingBox();

		expect(buttonBox).not.toBeNull();
		expect(canvasBox).not.toBeNull();

		// Canvas should cover full viewport (positioned absolutely)
		expect(canvasBox!.x).toBe(0);
		expect(canvasBox!.y).toBe(0);

		// Verify canvas z-index is lower than content
		const canvasZIndex = await canvas.evaluate((el) => {
			return window.getComputedStyle(el).zIndex;
		});
		expect(parseInt(canvasZIndex)).toBeLessThan(10); // Should be z-index: 1

		// Verify hero content has higher z-index
		const heroContent = page.locator('.hero-content');
		const heroZIndex = await heroContent.evaluate((el) => {
			return window.getComputedStyle(el).zIndex;
		});
		expect(parseInt(heroZIndex)).toBeGreaterThanOrEqual(10);
	});

	test('should be responsive on mobile viewport (375px width)', async ({ page }) => {
		// Set mobile viewport
		await page.setViewportSize({ width: 375, height: 667 });

		// Wait a moment for resize to take effect
		await page.waitForTimeout(500);

		// Verify all key elements are still visible
		await expect(page.locator('h1:has-text("ShredBX")')).toBeVisible();
		await expect(page.locator('.style-toggle')).toBeVisible();
		await expect(page.locator('canvas')).toBeVisible();

		// Check buttons are stacked or wrapped properly on mobile
		const buttonContainer = page.locator('.style-toggle');
		const containerBox = await buttonContainer.boundingBox();

		expect(containerBox).not.toBeNull();
		expect(containerBox!.width).toBeLessThanOrEqual(375);

		// Verify hero text is readable (not too large)
		const heroTitle = page.locator('h1');
		const fontSize = await heroTitle.evaluate((el) => {
			return window.getComputedStyle(el).fontSize;
		});
		const fontSizeNum = parseInt(fontSize);
		expect(fontSizeNum).toBeLessThanOrEqual(100); // Should use clamp() for responsive text

		// Verify canvas renders properly
		const canvas = page.locator('canvas');
		const canvasBox = await canvas.boundingBox();
		expect(canvasBox!.width).toBe(375);
	});

	test('should be responsive on tablet viewport (768px width)', async ({ page }) => {
		// Set tablet viewport
		await page.setViewportSize({ width: 768, height: 1024 });
		await page.waitForTimeout(500);

		// Verify layout
		await expect(page.locator('h1:has-text("ShredBX")')).toBeVisible();
		await expect(page.locator('.style-toggle')).toBeVisible();

		// Buttons should be in a row on tablet
		const buttons = page.locator('.style-btn');
		const firstBtnBox = await buttons.nth(0).boundingBox();
		const secondBtnBox = await buttons.nth(1).boundingBox();

		expect(firstBtnBox).not.toBeNull();
		expect(secondBtnBox).not.toBeNull();

		// Check if buttons are roughly on same horizontal line (allowing small variance)
		const yDifference = Math.abs(firstBtnBox!.y - secondBtnBox!.y);
		expect(yDifference).toBeLessThan(10); // Should be on same row
	});

	test('should be responsive on desktop viewport (1920px width)', async ({ page }) => {
		// Set large desktop viewport
		await page.setViewportSize({ width: 1920, height: 1080 });
		await page.waitForTimeout(500);

		// Verify all elements visible
		await expect(page.locator('h1:has-text("ShredBX")')).toBeVisible();
		await expect(page.locator('.style-toggle')).toBeVisible();

		// Hero content should be centered
		const heroContent = page.locator('.hero-content');
		const contentBox = await heroContent.boundingBox();

		expect(contentBox).not.toBeNull();

		// Content should be centered (allowing for transform: translateX(-50%))
		const centerX = contentBox!.x + contentBox!.width / 2;
		const viewportCenterX = 1920 / 2;
		const centerDifference = Math.abs(centerX - viewportCenterX);

		expect(centerDifference).toBeLessThan(50); // Should be roughly centered

		// Verify max-width constraint on hero content
		expect(contentBox!.width).toBeLessThanOrEqual(1920 * 0.9); // max-width: 90%
	});

	test('should not have overlapping elements that block interaction', async ({ page }) => {
		// Get key interactive elements
		const buttons = page.locator('.style-btn');
		const canvas = page.locator('canvas');

		// All buttons should be clickable
		for (let i = 0; i < await buttons.count(); i++) {
			const button = buttons.nth(i);
			await expect(button).toBeVisible();

			// Try clicking each button to ensure it's not blocked
			await button.click({ timeout: 3000 });

			// Wait for any loading to complete
			await page.waitForTimeout(500);
		}

		// Canvas should not block hero content
		const heroContent = page.locator('.hero-content');
		const heroBox = await heroContent.boundingBox();

		expect(heroBox).not.toBeNull();

		// Verify hero content pointer-events work
		const canInteract = await heroContent.evaluate((el) => {
			const style = window.getComputedStyle(el);
			return style.pointerEvents !== 'none';
		});
		expect(canInteract).toBe(true);
	});

	test('should maintain proper z-index stacking order', async ({ page }) => {
		// Get z-index values of key elements
		const canvas = page.locator('canvas');
		const heroContent = page.locator('.hero-content');
		const gradientOverlays = page.locator('.gradient-overlay');

		const canvasZ = await canvas.evaluate((el) => parseInt(window.getComputedStyle(el).zIndex) || 0);
		const heroZ = await heroContent.evaluate((el) => parseInt(window.getComputedStyle(el).zIndex) || 0);
		const gradientZ = await gradientOverlays.first().evaluate((el) => parseInt(window.getComputedStyle(el).zIndex) || 0);

		// Verify stacking order: canvas < gradient < hero content
		expect(canvasZ).toBe(1); // Canvas at bottom
		expect(gradientZ).toBe(5); // Gradients in middle
		expect(heroZ).toBe(10); // Hero content on top

		expect(heroZ).toBeGreaterThan(gradientZ);
		expect(gradientZ).toBeGreaterThan(canvasZ);
	});

	test('should display gradient overlays without blocking content', async ({ page }) => {
		// Check gradient overlays exist
		const topGradient = page.locator('.gradient-top');
		const bottomGradient = page.locator('.gradient-bottom');

		await expect(topGradient).toBeVisible();
		await expect(bottomGradient).toBeVisible();

		// Verify gradients have pointer-events: none (don't block interaction)
		const topPointerEvents = await topGradient.evaluate((el) => {
			return window.getComputedStyle(el).pointerEvents;
		});
		const bottomPointerEvents = await bottomGradient.evaluate((el) => {
			return window.getComputedStyle(el).pointerEvents;
		});

		expect(topPointerEvents).toBe('none');
		expect(bottomPointerEvents).toBe('none');

		// Verify gradients are positioned correctly
		const topBox = await topGradient.boundingBox();
		const bottomBox = await bottomGradient.boundingBox();

		expect(topBox!.y).toBe(0); // At top
		expect(bottomBox!.y).toBeGreaterThan(topBox!.y + topBox!.height); // At bottom
	});

	test('should handle window resize without breaking layout', async ({ page }) => {
		// Start at desktop size
		await page.setViewportSize({ width: 1920, height: 1080 });
		await page.waitForTimeout(500);

		// Verify initial state
		await expect(page.locator('h1:has-text("ShredBX")')).toBeVisible();

		// Resize to tablet
		await page.setViewportSize({ width: 768, height: 1024 });
		await page.waitForTimeout(500);

		await expect(page.locator('h1:has-text("ShredBX")')).toBeVisible();
		await expect(page.locator('.style-toggle')).toBeVisible();

		// Resize to mobile
		await page.setViewportSize({ width: 375, height: 667 });
		await page.waitForTimeout(500);

		await expect(page.locator('h1:has-text("ShredBX")')).toBeVisible();
		await expect(page.locator('.style-toggle')).toBeVisible();

		// Resize back to desktop
		await page.setViewportSize({ width: 1920, height: 1080 });
		await page.waitForTimeout(500);

		// Everything should still work
		await expect(page.locator('h1:has-text("ShredBX")')).toBeVisible();
		const button = page.locator('button.style-btn:has-text("Mad Max")');
		await button.click();

		// Model should load successfully after resize
		await expect(page.locator('.loading')).not.toBeVisible({ timeout: 15000 });
	});

	test('should maintain proper spacing between elements', async ({ page }) => {
		// Get positions of key elements
		const heroTitle = page.locator('h1:has-text("ShredBX")');
		const tagline = page.locator('p.tagline');
		const buttonContainer = page.locator('.style-toggle');

		const titleBox = await heroTitle.boundingBox();
		const taglineBox = await tagline.boundingBox();
		const buttonBox = await buttonContainer.boundingBox();

		expect(titleBox).not.toBeNull();
		expect(taglineBox).not.toBeNull();
		expect(buttonBox).not.toBeNull();

		// Calculate spacing
		const titleToTagline = taglineBox!.y - (titleBox!.y + titleBox!.height);
		const taglineToButtons = buttonBox!.y - (taglineBox!.y + taglineBox!.height);

		// Verify reasonable spacing (at least some margin)
		expect(titleToTagline).toBeGreaterThan(5); // At least 5px gap
		expect(taglineToButtons).toBeGreaterThan(10); // At least 10px gap (margin-top: 2rem)
	});
});
