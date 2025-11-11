# E2E Testing Round 2 Review: US-020 & US-021

**Date:** 2025-11-08
**Reviewer:** playwright-e2e-tester
**Agent Role:** End-to-End Testing Specialist

---

## Verification Results

### High Priority 1: Test Data Management Strategy

**Status:** ✅ FIXED (US-020) / ⚠️ PARTIAL (US-021)

**What I Found in US-020:**
The story now includes a comprehensive "Testing Considerations" section (lines 1306-1386) with:

```bash
# Option 1: Transaction rollback (preferred, faster)
# - Wrap each test in BEGIN/ROLLBACK transaction
# - Requires test-specific database configuration

# Option 2: Manual cleanup (simple, slower)
DELETE FROM content_dictionary WHERE key NOT IN ('homepage.title', 'homepage.description');
UPDATE content_dictionary SET value = 'Welcome to Bestays', ...
```

**What I Found in US-021:**
- No explicit test data management section
- Test examples show manual navigation but no cleanup strategy
- Multi-locale tests would need to reset BOTH EN and TH content between tests

**Satisfactory:**
- ✅ US-020: YES - Clear, practical strategies with code examples
- ⚠️ US-021: PARTIAL - Missing explicit test data strategy for multi-locale scenario

---

### High Priority 2: Locator Strategy

**Status:** ✅ FIXED (US-020) / ❌ NOT FIXED (US-021)

**What I Found in US-020:**
Explicit locator strategy documented (lines 1332-1355):

```typescript
// RULE: Use data-testid for all testable elements
// Priority: data-testid > role > text content

<div data-testid="editable-content-{contentKey}">
<Dialog data-testid="edit-content-dialog">
<Textarea data-testid="content-value-input" />
<Button data-testid="save-button">Save</Button>
```

**E2E usage:**
```typescript
await page.locator('[data-testid="editable-content-homepage.title"]').click({ button: 'right' });
await page.locator('[data-testid="edit-content-dialog"]').waitFor();
```

**What I Found in US-021:**
Test examples use **fragile locators**:
- ❌ `page.locator('button:has-text("TH")')` - text-based (breaks with locale changes)
- ❌ `page.locator('h1')` - element-based (no unique identifier)
- ❌ `page.locator('textarea')` - element-based (breaks with multiple textareas)
- ❌ `page.locator('a:has-text("เข้าสู่ระบบ")')` - Thai text (fragile for i18n tests)

**Missing:**
- No `data-testid` attributes in component examples
- No guidance on how to test locale switcher buttons reliably
- No strategy for testing Thai text content without hardcoding Thai strings

**Satisfactory:**
- ✅ US-020: YES - Clear priority hierarchy, concrete examples
- ❌ US-021: NO - Uses anti-patterns (text selectors, element selectors without IDs)

---

### High Priority 3: Flakiness Risks - Explicit Wait Strategies

**Status:** ✅ FIXED (US-020) / ⚠️ PARTIAL (US-021)

**What I Found in US-020:**
Comprehensive wait strategy documented (lines 1357-1372):

```typescript
// Wait for dialog to close (optimistic update complete)
await page.locator('[data-testid="edit-content-dialog"]').waitFor({ state: 'hidden' });

// Wait for network idle (cache invalidation complete)
await page.waitForLoadState('networkidle');

// THEN reload and verify
await page.reload();
await expect(page.locator('h1')).toContainText('New value');
```

**Addresses:**
- ✅ Cache invalidation waits
- ✅ Optimistic update completion
- ✅ SSR load waits
- ✅ Network state verification

**What I Found in US-021:**
Test examples show basic navigation but no explicit waits:

```typescript
// Click TH button
await page.locator('button:has-text("TH")').click();

// URL changes to /th
await expect(page).toHaveURL(/\/th$/);  // ⚠️ Race condition possible

// Thai content visible
await expect(page.locator('h1')).toContainText('ยินดีต้อนรับสู่ Bestays');  // ⚠️ No wait for SSR
```

**Missing:**
- No wait for SSR after locale switch (route load)
- No wait for network idle after locale change
- No guidance on waiting for locale-specific content to load
- No wait strategy for cache invalidation on locale switch

**Satisfactory:**
- ✅ US-020: YES - Comprehensive, correct Playwright patterns
- ⚠️ US-021: PARTIAL - Basic expectations but missing crucial waits for locale transitions

---

## Overall Decision

**Decision:** 🟡 APPROVE WITH MINOR SUGGESTIONS

**Rationale:**

**US-020: EXCELLENT** ✅
- All 3 of my high-priority concerns fully addressed
- Testing Considerations section is comprehensive and practical
- data-testid strategy is clear with concrete examples
- Wait strategies are correct Playwright patterns
- Test data management shows both approaches (transaction rollback + manual cleanup)
- Edge cases documented
- Ready for implementation

**US-021: NEEDS MINOR IMPROVEMENTS** ⚠️
- Test examples provided but lack testing guidance that US-020 has
- Fragile locators used in examples (text-based, element-based)
- Missing explicit wait strategies for locale transitions
- No test data management strategy for multi-locale scenario
- However, these are fixable during implementation if Plan agent knows to follow US-020 patterns

**Overall Confidence:** High that US-020 will produce reliable tests. Medium that US-021 will require rework if implementers follow the flawed examples verbatim.

---

## Remaining Concerns

### US-021 Specific Issues:

1. **Locator Strategy Not Applied:**
   - Test examples use anti-patterns (text selectors, element selectors)
   - Should use `data-testid` like US-020
   - Suggested fixes:
     ```typescript
     // BAD (current)
     await page.locator('button:has-text("TH")').click();

     // GOOD (should be)
     await page.locator('[data-testid="locale-switcher-th"]').click();
     ```

2. **Missing Wait Strategies for Locale Transitions:**
   - Locale switch triggers SSR route load + data refetch
   - Should add explicit waits:
     ```typescript
     await page.locator('[data-testid="locale-switcher-th"]').click();

     // Wait for route change to complete
     await page.waitForURL(/\/th$/);

     // Wait for SSR load
     await page.waitForLoadState('networkidle');

     // THEN verify content
     await expect(page.locator('[data-testid="homepage-title"]')).toContainText('ยินดีต้อนรับสู่ Bestays');
     ```

3. **Test Data Management for Multi-Locale:**
   - US-020 shows how to reset single-locale content
   - US-021 needs strategy for resetting BOTH locales:
     ```sql
     -- Reset both EN and TH content
     DELETE FROM content_dictionary WHERE key NOT IN ('homepage.title', 'homepage.description');

     -- Reset EN
     UPDATE content_dictionary SET value = 'Welcome to Bestays' WHERE key = 'homepage.title' AND locale = 'en';

     -- Reset TH
     UPDATE content_dictionary SET value = 'ยินดีต้อนรับสู่ Bestays' WHERE key = 'homepage.title' AND locale = 'th';
     ```

4. **Testing Thai Text Without Hardcoding:**
   - Current examples hardcode Thai strings in tests
   - Better approach: Use data-testid and verify presence, not exact text:
     ```typescript
     // Instead of checking exact Thai text (fragile):
     await expect(page.locator('h1')).toContainText('ยินดีต้อนรับสู่ Bestays');

     // Better: Check that element exists and is not empty:
     const title = page.locator('[data-testid="homepage-title"]');
     await expect(title).toBeVisible();
     await expect(title).not.toBeEmpty();

     // Or use data-locale attribute to verify correct locale loaded:
     await expect(page.locator('[data-locale="th"]')).toBeVisible();
     ```

---

## Suggestions (Optional Improvements)

### For Both Stories:

1. **Page Object Model Recommendation:**
   - Add guidance to create Page Objects for maintainability:
     ```typescript
     // tests/e2e/pages/HomePage.ts
     export class HomePage {
       constructor(private page: Page) {}

       async goto(locale: 'en' | 'th' = 'en') {
         await this.page.goto(`http://localhost:5183/${locale}`);
         await this.page.waitForLoadState('networkidle');
       }

       async getTitle() {
         return this.page.locator('[data-testid="homepage-title"]');
       }

       async switchLocale(locale: 'en' | 'th') {
         await this.page.locator(`[data-testid="locale-switcher-${locale}"]`).click();
         await this.page.waitForURL(new RegExp(`\/${locale}$`));
         await this.page.waitForLoadState('networkidle');
       }
     }
     ```

2. **Fixture for Database Reset:**
   - Recommend creating Playwright fixture for test data management:
     ```typescript
     // tests/e2e/fixtures/database.ts
     import { test as base } from '@playwright/test';

     export const test = base.extend({
       resetDatabase: async ({}, use) => {
         // Setup: Reset DB before test
         await resetContentDictionary();
         await use();
         // Teardown: Optional cleanup
       }
     });
     ```

3. **Network Idle Timeout Configuration:**
   - Recommend explicit timeout config for CI:
     ```typescript
     test.use({
       actionTimeout: 10000,
       navigationTimeout: 30000,
     });

     await page.waitForLoadState('networkidle', { timeout: 30000 });
     ```

### For US-021 Specifically:

4. **Add Testing Considerations Section:**
   - US-021 should have same section as US-020 covering:
     - Test data management for multi-locale scenario
     - Locator strategy for locale switcher buttons
     - Wait strategies for locale transitions
     - Edge cases specific to i18n (invalid locale, fallback logic)

---

## Sign-Off

**Agent:** playwright-e2e-tester
**Decision:** 🟡 APPROVE WITH SUGGESTIONS
**Confidence:** High for US-020 | Medium for US-021

**Approval Conditions:**
1. ✅ US-020 is ready for implementation as-is
2. ⚠️ US-021 should either:
   - Add Testing Considerations section (similar to US-020), OR
   - Ensure Plan agent knows to apply US-020 patterns to US-021 tests

**Bottom Line:**
My Round 1 feedback was addressed comprehensively in US-020. US-021 would benefit from the same treatment, but the issues are minor and fixable during implementation if the team follows US-020 as the template.

I approve both stories for progression to implementation, with the expectation that US-021's test implementation will follow US-020's testing patterns.

**Date:** 2025-11-08
**Reviewed By:** playwright-e2e-tester (Round 2)

---

## Summary for Coordinator

**Status:** ✅ APPROVED (with minor improvement suggestions for US-021)

**What Was Fixed Well:**
- ✅ Test data management strategy (US-020)
- ✅ Locator strategy with data-testid (US-020)
- ✅ Explicit wait patterns (US-020)
- ✅ Edge case documentation (US-020)

**What Could Be Better:**
- ⚠️ US-021 lacks the same Testing Considerations section
- ⚠️ US-021 test examples use fragile locators
- ⚠️ US-021 missing locale-transition wait strategies

**Recommendation:**
Proceed to implementation. Ensure US-021 implementers follow US-020's testing patterns. Consider adding a Testing Considerations section to US-021 for consistency.

**Risk Level:** LOW - Issues are minor and addressable during implementation.
