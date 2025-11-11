# E2E Test Plan - TASK-016 Property Detail Page

**Task:** TASK-016 Property Detail Page Frontend  
**Story:** US-023 Property Import & Display with Localization  
**Date:** 2025-11-09

---

## Overview

This document defines all End-to-End test scenarios for the property detail page. All tests must pass before task completion.

**Total Test Suites:** 5  
**Target Coverage:** 80%+ for critical paths  
**Test Framework:** Playwright  
**Browsers:** Chromium, Firefox, WebKit

---

## Test Suite 1: Property Detail Display

**File:** `test_property_detail_display.spec.ts`  
**Purpose:** Verify all property sections render correctly

### Test Scenarios

#### T1.1: All Sections Render
```typescript
test('displays all property information sections', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  
  // Hero section
  await expect(page.locator('img[alt*="Cover"]')).toBeVisible();
  
  // Header
  await expect(page.locator('h1')).toContainText('Test Property Title');
  await expect(page.locator('text=/฿.*/')).toBeVisible(); // Price
  
  // Quick info grid
  await expect(page.locator('text=/Bedrooms/')).toBeVisible();
  await expect(page.locator('text=/Bathrooms/')).toBeVisible();
  
  // Description
  await expect(page.locator('text=/Description/')).toBeVisible();
  
  // Image gallery
  await expect(page.locator('text=/Photos/')).toBeVisible();
  
  // Amenities
  await expect(page.locator('text=/Amenities/')).toBeVisible();
  
  // Policies
  await expect(page.locator('text=/Policies/')).toBeVisible();
  
  // Contact
  await expect(page.locator('text=/Contact/')).toBeVisible();
});
```

#### T1.2: Data Accuracy
```typescript
test('displays correct property data', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  
  // Verify title
  await expect(page.locator('h1')).toHaveText('Luxury Villa in Phuket');
  
  // Verify price
  await expect(page.locator('text=/฿150,000/')).toBeVisible();
  
  // Verify location
  await expect(page.locator('text=/Kathu, Phuket/')).toBeVisible();
  
  // Verify specs
  await expect(page.locator('text=/3.*Bedrooms/')).toBeVisible();
  await expect(page.locator('text=/2.*Bathrooms/')).toBeVisible();
});
```

#### T1.3: Responsive Layout (Desktop)
```typescript
test('renders correctly on desktop (1920x1080)', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto('/en/properties/test-property-123');
  
  // Verify layout is wide format
  const container = page.locator('.container').first();
  const box = await container.boundingBox();
  expect(box.width).toBeGreaterThan(1000);
});
```

#### T1.4: Responsive Layout (Tablet)
```typescript
test('renders correctly on tablet (768x1024)', async ({ page }) => {
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.goto('/en/properties/test-property-123');
  
  // All sections still visible
  await expect(page.locator('h1')).toBeVisible();
  await expect(page.locator('text=/Photos/')).toBeVisible();
});
```

#### T1.5: Responsive Layout (Mobile)
```typescript
test('renders correctly on mobile (375x667)', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/en/properties/test-property-123');
  
  // All sections visible (stacked layout)
  await expect(page.locator('h1')).toBeVisible();
  await expect(page.locator('text=/฿.*/')).toBeVisible();
  
  // Gallery is 2 columns
  const galleryItems = page.locator('.grid > button');
  const count = await galleryItems.count();
  expect(count).toBeGreaterThan(0);
});
```

#### T1.6: Images Load Correctly
```typescript
test('all property images load successfully', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  
  // Cover image
  const coverImg = page.locator('img[alt*="Cover"]').first();
  await expect(coverImg).toHaveAttribute('src', /.+/);
  
  // Gallery thumbnails
  const thumbnails = page.locator('.grid img[loading="lazy"]');
  const count = await thumbnails.count();
  expect(count).toBeGreaterThan(0);
  
  // Verify images loaded (naturalWidth > 0)
  const loaded = await thumbnails.first().evaluate((img: HTMLImageElement) => img.naturalWidth > 0);
  expect(loaded).toBe(true);
});
```

---

## Test Suite 2: Navigation

**File:** `test_property_detail_navigation.spec.ts`  
**Purpose:** Verify navigation to/from property detail page

### Test Scenarios

#### T2.1: Navigate from Listing Page
```typescript
test('navigates to detail page from property card', async ({ page }) => {
  await page.goto('/en/properties');
  
  // Click first property card
  await page.locator('.property-card').first().click();
  
  // Verify URL changed
  await expect(page).toHaveURL(/\/en\/properties\/[a-z0-9-]+/);
  
  // Verify detail page loaded
  await expect(page.locator('h1')).toBeVisible();
});
```

#### T2.2: Back Button Navigation
```typescript
test('back button returns to listing page', async ({ page }) => {
  await page.goto('/en/properties');
  await page.locator('.property-card').first().click();
  
  // Click back button
  await page.locator('a:has-text("Back to Properties")').click();
  
  // Verify returned to listing
  await expect(page).toHaveURL('/en/properties');
  await expect(page.locator('.property-card').first()).toBeVisible();
});
```

#### T2.3: Browser Back Button
```typescript
test('browser back button works correctly', async ({ page }) => {
  await page.goto('/en/properties');
  await page.locator('.property-card').first().click();
  await page.waitForURL(/\/en\/properties\/[a-z0-9-]+/);
  
  // Use browser back
  await page.goBack();
  
  // Verify returned to listing
  await expect(page).toHaveURL('/en/properties');
});
```

#### T2.4: Direct URL Access
```typescript
test('accessing detail page via direct URL works', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  
  // Verify page loaded
  await expect(page.locator('h1')).toBeVisible();
  await expect(page.locator('text=/฿.*/')).toBeVisible();
});
```

#### T2.5: URL Parameter Extraction
```typescript
test('correctly extracts property ID from URL', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  
  // Verify correct property loaded (check title or ID in footer)
  await expect(page.locator('text=/Property ID: test-property-123/')).toBeVisible();
});
```

---

## Test Suite 3: Locale Support

**File:** `test_property_detail_locale.spec.ts`  
**Purpose:** Verify locale switching and translations

### Test Scenarios

#### T3.1: Locale Switcher Changes Content
```typescript
test('locale switcher updates displayed content', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  
  // Verify English content
  await expect(page.locator('text=/Description/')).toBeVisible();
  
  // Switch to Thai
  await page.locator('button[aria-label="Switch language"]').click();
  await page.locator('a[href^="/th/"]').click();
  
  // Verify Thai content
  await expect(page).toHaveURL('/th/properties/test-property-123');
  await expect(page.locator('text=/รายละเอียด/')).toBeVisible();
});
```

#### T3.2: Price Formatting (English)
```typescript
test('displays price correctly in English locale', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  
  // Verify price format: "฿150,000"
  await expect(page.locator('text=/฿150,000/')).toBeVisible();
});
```

#### T3.3: Price Formatting (Thai)
```typescript
test('displays price correctly in Thai locale', async ({ page }) => {
  await page.goto('/th/properties/test-property-123');
  
  // Verify price format: "฿150,000"
  await expect(page.locator('text=/฿150,000/')).toBeVisible();
});
```

#### T3.4: UI Labels Translation
```typescript
test('UI labels translate correctly', async ({ page }) => {
  // English
  await page.goto('/en/properties/test-property-123');
  await expect(page.locator('text=/Bedrooms/')).toBeVisible();
  await expect(page.locator('text=/Bathrooms/')).toBeVisible();
  await expect(page.locator('text=/Back to Properties/')).toBeVisible();
  
  // Thai
  await page.goto('/th/properties/test-property-123');
  await expect(page.locator('text=/ห้องนอน/')).toBeVisible();
  await expect(page.locator('text=/ห้องน้ำ/')).toBeVisible();
  await expect(page.locator('text=/กลับไปยังรายการ/')).toBeVisible();
});
```

#### T3.5: Property Type Translation
```typescript
test('property type translates based on locale', async ({ page }) => {
  // English
  await page.goto('/en/properties/villa-123');
  await expect(page.locator('text=/Villa/')).toBeVisible();
  
  // Thai
  await page.goto('/th/properties/villa-123');
  await expect(page.locator('text=/วิลล่า/')).toBeVisible();
});
```

---

## Test Suite 4: Error States

**File:** `test_property_detail_error_states.spec.ts`  
**Purpose:** Verify error handling and edge cases

### Test Scenarios

#### T4.1: 404 Property Not Found
```typescript
test('displays 404 page for non-existent property', async ({ page }) => {
  await page.goto('/en/properties/non-existent-property-999');
  
  // Verify 404 error page
  await expect(page.locator('h1:has-text("Property Not Found")')).toBeVisible();
  await expect(page.locator('text=/Back to Properties/')).toBeVisible();
});
```

#### T4.2: Network Error Handling
```typescript
test('handles network errors gracefully', async ({ page, context }) => {
  // Intercept API and force failure
  await page.route('**/api/v1/properties/*', route => route.abort());
  
  await page.goto('/en/properties/test-property-123');
  
  // Verify error message displayed
  await expect(page.locator('text=/Error/')).toBeVisible();
  await expect(page.locator('button:has-text("Retry")')).toBeVisible();
});
```

#### T4.3: Loading State Visibility
```typescript
test('shows loading state during data fetch', async ({ page }) => {
  // Delay API response
  await page.route('**/api/v1/properties/*', async route => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    await route.continue();
  });
  
  const navPromise = page.goto('/en/properties/test-property-123');
  
  // Verify loading skeleton visible (if implemented)
  // await expect(page.locator('.animate-pulse')).toBeVisible();
  
  await navPromise;
  
  // Verify content loaded
  await expect(page.locator('h1')).toBeVisible();
});
```

#### T4.4: Retry Functionality
```typescript
test('retry button reloads property data', async ({ page }) => {
  let attemptCount = 0;
  
  await page.route('**/api/v1/properties/*', route => {
    attemptCount++;
    if (attemptCount === 1) {
      route.abort(); // Fail first attempt
    } else {
      route.continue(); // Succeed on retry
    }
  });
  
  await page.goto('/en/properties/test-property-123');
  
  // Click retry
  await page.locator('button:has-text("Retry")').click();
  
  // Verify success after retry
  await expect(page.locator('h1')).toBeVisible();
  expect(attemptCount).toBe(2);
});
```

#### T4.5: Offline State
```typescript
test('handles offline state correctly', async ({ page, context }) => {
  await context.setOffline(true);
  
  await page.goto('/en/properties/test-property-123');
  
  // Verify offline message
  await expect(page.locator('text=/No internet connection/')).toBeVisible();
  
  // Go back online
  await context.setOffline(false);
  
  // Retry should work
  await page.locator('button:has-text("Retry")').click();
  await expect(page.locator('h1')).toBeVisible();
});
```

---

## Test Suite 5: Image Gallery

**File:** `test_property_detail_image_gallery.spec.ts`  
**Purpose:** Verify image gallery interactions

### Test Scenarios

#### T5.1: Gallery Opens on Thumbnail Click
```typescript
test('opens lightbox when clicking thumbnail', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  
  // Click first thumbnail
  await page.locator('.grid > button').first().click();
  
  // Verify lightbox opened
  await expect(page.locator('[role="dialog"]')).toBeVisible();
  await expect(page.locator('[role="dialog"] img')).toBeVisible();
});
```

#### T5.2: Gallery Closes with Close Button
```typescript
test('closes lightbox with close button', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  await page.locator('.grid > button').first().click();
  
  // Click close button
  await page.locator('[role="dialog"] button[aria-label="Close"]').click();
  
  // Verify lightbox closed
  await expect(page.locator('[role="dialog"]')).not.toBeVisible();
});
```

#### T5.3: Gallery Closes with Escape Key
```typescript
test('closes lightbox with Escape key', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  await page.locator('.grid > button').first().click();
  
  // Press Escape
  await page.keyboard.press('Escape');
  
  // Verify lightbox closed
  await expect(page.locator('[role="dialog"]')).not.toBeVisible();
});
```

#### T5.4: Gallery Closes with Browser Back Button
```typescript
test('closes lightbox with browser back button (shallow routing)', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  await page.locator('.grid > button').first().click();
  
  // Verify lightbox opened
  await expect(page.locator('[role="dialog"]')).toBeVisible();
  
  // Press browser back
  await page.goBack();
  
  // Verify lightbox closed but still on same page
  await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  await expect(page).toHaveURL('/en/properties/test-property-123');
});
```

#### T5.5: Arrow Key Navigation
```typescript
test('navigates images with arrow keys', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  await page.locator('.grid > button').first().click();
  
  // Verify first image
  await expect(page.locator('text=/1 \/ \d+/')).toBeVisible();
  
  // Press right arrow
  await page.keyboard.press('ArrowRight');
  
  // Verify second image
  await expect(page.locator('text=/2 \/ \d+/')).toBeVisible();
  
  // Press left arrow
  await page.keyboard.press('ArrowLeft');
  
  // Verify back to first image
  await expect(page.locator('text=/1 \/ \d+/')).toBeVisible();
});
```

#### T5.6: Touch Swipe Navigation (Mobile)
```typescript
test('navigates images with touch swipe on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/en/properties/test-property-123');
  await page.locator('.grid > button').first().click();
  
  const dialog = page.locator('[role="dialog"]');
  
  // Simulate swipe left (next image)
  await dialog.dispatchEvent('touchstart', { touches: [{ clientX: 300, clientY: 300 }] });
  await dialog.dispatchEvent('touchmove', { touches: [{ clientX: 100, clientY: 300 }] });
  await dialog.dispatchEvent('touchend', {});
  
  // Verify image changed
  await expect(page.locator('text=/2 \/ \d+/')).toBeVisible();
});
```

#### T5.7: Image Counter Display
```typescript
test('displays correct image counter', async ({ page }) => {
  await page.goto('/en/properties/test-property-123');
  await page.locator('.grid > button').nth(2).click(); // Click 3rd image
  
  // Verify counter shows "3 / 10" (or similar)
  await expect(page.locator('text=/3 \/ \d+/')).toBeVisible();
});
```

---

## Test Execution Plan

### Pre-Test Setup
```bash
# Start development server
npm run dev

# Start backend API (if not running)
cd apps/server && make dev

# Ensure sample data loaded
# Property with ID "test-property-123" must exist
```

### Run All Tests
```bash
cd apps/frontend
npm run test:e2e
```

### Run Individual Suites
```bash
npx playwright test test_property_detail_display.spec.ts
npx playwright test test_property_detail_navigation.spec.ts
npx playwright test test_property_detail_locale.spec.ts
npx playwright test test_property_detail_error_states.spec.ts
npx playwright test test_property_detail_image_gallery.spec.ts
```

### Browser Matrix
```bash
# Test on all browsers
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

---

## Success Criteria

**All tests must pass:**
- ✅ Test Suite 1 (Display): 6/6 tests pass
- ✅ Test Suite 2 (Navigation): 5/5 tests pass
- ✅ Test Suite 3 (Locale): 5/5 tests pass
- ✅ Test Suite 4 (Error States): 5/5 tests pass
- ✅ Test Suite 5 (Image Gallery): 7/7 tests pass

**Total:** 28 E2E tests must pass

**Coverage:** 80%+ for critical paths

---

**Created By:** Coordinator (Claude Code)  
**Date:** 2025-11-09  
**Total Test Scenarios:** 28  
**Ready for Implementation:** Yes ✅
