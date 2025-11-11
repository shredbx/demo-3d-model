# E2E Test Handoff - US-021 Locale Switching

**Agent:** playwright-e2e-tester
**Task:** TASK-010 (US-021 Thai Localization)
**Branch:** feat/TASK-010-US-021
**Date:** 2025-11-09

---

## Mission

Create comprehensive E2E tests for US-021 locale switching functionality. All implementation is complete and manually tested. We need automated tests to ensure no regressions.

---

## What's Implemented (Working)

✅ **Database:**
- `content_dictionary` table has `locale` column
- Thai translations exist for `homepage.title` and `homepage.description`

✅ **Backend:**
- `GET /api/v1/content/{key}?locale=en|th` returns correct locale
- Fallback logic: Missing Thai → returns English
- Invalid locale → 422 validation error

✅ **Frontend:**
- Routes: `/en` and `/th` (root `/` redirects to `/en`)
- Locale switcher with EN | TH buttons in header
- Content updates immediately when switching locales (fixed in TASK-011)
- SSR + hydration working correctly
- EditContentDialog shows current locale

✅ **Manual Testing:**
- Both Bestays and Real Estate products tested
- Locale switching works without page refresh
- Content isolation verified (editing TH doesn't affect EN)

---

## Test Requirements

### Test File Location

Create: `apps/frontend/tests/e2e/locale-switching.spec.ts`

### Test Scenarios (4 Required)

#### 1. Basic Locale Switching (EN ↔ TH)

**AC-1: Default Locale**
```typescript
test('Homepage defaults to /en and shows English content', async ({ page }) => {
  // Visit root URL
  // Verify redirect to /en
  // Verify English content visible
});
```

**AC-2: Switch to Thai**
```typescript
test('User can switch to Thai locale', async ({ page }) => {
  // Start on /en
  // Click TH button
  // Verify URL changes to /th
  // Verify Thai content visible
  // Verify locale switcher highlights TH as active
});
```

**AC-2b: Switch back to English**
```typescript
test('User can switch back to English from Thai', async ({ page }) => {
  // Start on /th
  // Click EN button
  // Verify URL changes to /en
  // Verify English content visible
  // Verify locale switcher highlights EN as active
});
```

#### 2. Content Updates Without Refresh

```typescript
test('Locale switch updates content immediately (no manual refresh needed)', async ({ page }) => {
  // Visit /en, verify English content
  // Click TH button
  // Wait for URL change to /th
  // Verify Thai content appears (no page.reload() needed)
  // Click EN button
  // Verify English content appears immediately
});
```

#### 3. Admin Editing - Locale Isolation

**AC-3: Independent Locale Editing**
```typescript
test('Admin can edit Thai content independently (EN unchanged)', async ({ page }) => {
  // Login as admin (use existing login helper)
  // Navigate to /th
  // Edit homepage.title in Thai
  // Save changes
  // Verify Thai content updated
  // Navigate to /en
  // Verify English content UNCHANGED (isolation verified)
});

test('Admin can edit English content independently (TH unchanged)', async ({ page }) => {
  // Login as admin
  // Navigate to /en
  // Edit homepage.title in English
  // Save changes
  // Verify English content updated
  // Navigate to /th
  // Verify Thai content UNCHANGED
});
```

#### 4. Edge Cases

**Invalid Locale**
```typescript
test('Invalid locale returns 404', async ({ page }) => {
  const response = await page.goto('http://localhost:5183/fr');
  expect(response?.status()).toBe(404);
});
```

**Direct URL Access**
```typescript
test('Direct access to /th works without redirect', async ({ page }) => {
  await page.goto('http://localhost:5183/th');
  await expect(page).toHaveURL(/\/th$/);
  // Verify Thai content (not redirected to /en)
});
```

---

## Technical Details

### URLs to Test

**Bestays Product:**
- Root: `http://localhost:5183/`
- English: `http://localhost:5183/en`
- Thai: `http://localhost:5183/th`

**Real Estate Product:**
- Root: `http://localhost:5184/`
- English: `http://localhost:5184/en`
- Thai: `http://localhost:5184/th`

### Expected Content

**English (locale=en):**
- Title: "Welcome to Bestays" (or similar)
- Description: "Your trusted platform..." (or similar)

**Thai (locale=th):**
- Title: "ยินดีต้อนรับสู่ Bestays"
- Description: "แพลตฟอร์มที่คุณไว้วางใจ..."

### Locators to Use

**Locale Switcher:**
```typescript
// EN button
page.locator('[data-testid="locale-button-en"]')
// OR if data-testid not added yet:
page.locator('button:has-text("EN")')

// TH button
page.locator('[data-testid="locale-button-th"]')
// OR:
page.locator('button:has-text("TH")')
```

**Content:**
```typescript
// Title
page.locator('h1').first()

// Description
page.locator('p').first()
```

**Edit Dialog:**
```typescript
// Dialog
page.locator('[data-testid="edit-content-dialog"]')

// Locale indicator
page.locator('[data-testid="locale-indicator"]')
// Should contain: "English (en)" or "Thai (th)"

// Textarea
page.locator('[data-testid="content-value-input"]')

// Save button
page.locator('[data-testid="save-button"]')
```

### Wait Strategies

**After clicking locale switcher:**
```typescript
// Wait for URL change
await page.waitForURL(/\/th$/);

// Wait for network idle (SSR content loaded)
await page.waitForLoadState('networkidle');

// THEN verify content
await expect(page.locator('h1')).toContainText('ยินดีต้อนรับ');
```

**After editing content:**
```typescript
// Click save
await page.locator('[data-testid="save-button"]').click();

// Wait for dialog to close
await page.locator('[data-testid="edit-content-dialog"]').waitFor({ state: 'hidden' });

// Wait for network (cache invalidation)
await page.waitForLoadState('networkidle');

// Reload to verify persistence
await page.reload();
await expect(page.locator('h1')).toContainText('Updated content');
```

---

## Test Data Management

**Important:** Tests should NOT modify the database permanently.

### Option 1: Database Reset (Recommended)

Create a helper to reset content to seed state after each test:

```typescript
async function resetContentDictionary() {
  // SQL to reset to seed state
  // Restore both EN and TH content for homepage.title and homepage.description
}

test.afterEach(async () => {
  await resetContentDictionary();
});
```

### Option 2: Use Unique Test Data

Instead of editing `homepage.title`, create test-specific keys:
- `test.homepage.title.en`
- `test.homepage.title.th`

Clean up after tests.

---

## Authentication

**Use existing test credentials:**

```typescript
import { test as base, expect } from '@playwright/test';

// Login helper (from existing tests)
async function loginAsAdmin(page: Page) {
  await page.goto('http://localhost:5183/en/login');
  await page.fill('input[name="email"]', 'admin.claudecode@bestays.app');
  await page.fill('input[name="password"]', 'rHe/997?lo&l');
  await page.click('button:has-text("Sign In")');
  await page.waitForURL(/\/en$/);  // Redirects to homepage after login
}
```

---

## Success Criteria

✅ All 4 test scenarios pass
✅ Tests run in < 2 minutes total
✅ Zero flaky tests (must be deterministic)
✅ Test both Bestays and Real Estate products
✅ Tests can run in CI/CD (no manual intervention)

---

## Deliverables

1. **Test File:** `apps/frontend/tests/e2e/locale-switching.spec.ts`
2. **Test Report:** `.claude/tasks/TASK-010/testing/e2e-test-results.md`
   - Test execution summary
   - Screenshots of any failures
   - Performance notes (test execution time)

---

## References

- **US-021 Story:** `.sdlc-workflow/stories/homepage/US-021-locale-switching.md`
- **Acceptance Criteria:** Lines 1069-1100 of US-021 story
- **Implementation Summary:** `.claude/tasks/TASK-011/COMPLETION-SUMMARY.md`
- **Existing E2E Tests:** `apps/frontend/tests/e2e/auth-login-logout.spec.ts` (for patterns)

---

## Notes

- Implementation is 100% complete and manually validated
- This is pure test automation work (no implementation changes needed)
- Focus on stability and determinism (no flaky tests!)
- If you encounter missing `data-testid` attributes, add them to components before writing tests

---

**Ready to implement!** 🚀
