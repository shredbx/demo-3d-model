# Solution Specification: Locale Switch Refresh Fix

**Task:** TASK-011
**Story:** US-021 - Thai Localization & Locale Switching
**Type:** Bug Fix
**Approved Solution:** Option 1 - Add `invalidateAll()`

---

## Solution Overview

Add explicit SvelteKit load function invalidation to `LocaleSwitcher.svelte` to force content re-fetch when switching locales.

**Technical Approach:**
- Use SvelteKit's `invalidateAll()` function after navigation
- Make `switchLocale()` async to await both navigation and invalidation
- Maintains client-side navigation benefits (no full page reload)

---

## Implementation Details

### File: `apps/frontend/src/lib/components/LocaleSwitcher.svelte`

**Changes Required:**

1. **Add Import:**
```typescript
import { invalidateAll } from '$app/navigation';
```

2. **Update Function Signature:**
```typescript
// OLD:
function switchLocale(newLocale: Locale) {

// NEW:
async function switchLocale(newLocale: Locale) {
```

3. **Add Invalidation After Navigation:**
```typescript
async function switchLocale(newLocale: Locale) {
  // Remove current locale from path
  const currentPath = $page.url.pathname.replace(/^\/(en|th)/, '');

  // Navigate to new locale with same path
  await goto(`/${newLocale}${currentPath || ''}`);

  // Force all load functions to re-run
  await invalidateAll();
}
```

**Complete Updated Function:**
```typescript
/**
 * Switch to a new locale while preserving the current path
 * Forces load functions to re-run to fetch new locale content
 */
async function switchLocale(newLocale: Locale) {
  // Remove current locale from path
  const currentPath = $page.url.pathname.replace(/^\/(en|th)/, '');

  // Navigate to new locale with same path
  await goto(`/${newLocale}${currentPath || ''}`);

  // Force all load functions to re-run with new locale
  await invalidateAll();
}
```

---

## How It Works

### Before Fix:
```
1. User clicks "TH" button
2. goto('/th') navigates to new route
3. SvelteKit sees URL change but assumes data is still valid
4. Load function NOT re-run (cached)
5. Content stays in English ❌
```

### After Fix:
```
1. User clicks "TH" button
2. goto('/th') navigates to new route
3. invalidateAll() tells SvelteKit "data is stale"
4. Load function RE-RUNS with new locale
5. Content updates to Thai ✅
```

---

## Technical Details

### Why `invalidateAll()` Works

**SvelteKit Load Function Caching:**
- SvelteKit caches load function results for performance
- On navigation, it checks if data is still "valid"
- If valid, it reuses cached data (avoids unnecessary fetches)

**Problem in Our Case:**
- Route changes from `/en` to `/th`
- Load function depends on `params.lang` (via `await parent()`)
- BUT SvelteKit doesn't detect this dependency automatically
- Result: Cached English data used for Thai route

**Solution:**
- `invalidateAll()` explicitly marks ALL load data as stale
- Forces SvelteKit to re-run ALL load functions (layout + page)
- New locale passed to API → Thai content fetched

**Reference:** [SvelteKit Docs - invalidateAll](https://kit.svelte.dev/docs/modules#$app-navigation-invalidateall)

---

## Alternative Considered: `invalidate()`

**Option:** Use `invalidate()` with specific URL instead of `invalidateAll()`

```typescript
await goto(`/${newLocale}${currentPath || ''}`);
await invalidate(url => url.pathname.startsWith('/api/v1/content'));
```

**Why NOT chosen:**
- More complex (need to specify which URLs to invalidate)
- `invalidateAll()` is simpler and covers all cases
- Performance difference negligible (only 2 API calls on homepage)

---

## Testing Requirements

### Manual Testing Checklist

**Bestays Product:**
- [ ] Visit `http://localhost:5183/en` → Verify English content
- [ ] Click "TH" button → Content updates to Thai immediately (no manual refresh)
- [ ] Click "EN" button → Content updates to English immediately
- [ ] Browser back button → Previous locale content displays correctly
- [ ] Browser forward button → Next locale content displays correctly

**Real Estate Product:**
- [ ] Visit `http://localhost:5184/en` → Verify English content
- [ ] Click "TH" button → Content updates to Thai immediately
- [ ] Click "EN" button → Content updates to English immediately
- [ ] Browser navigation works correctly

**Edge Cases:**
- [ ] Rapid switching (EN → TH → EN → TH) works without errors
- [ ] Locale switching on non-homepage routes (if applicable)
- [ ] Network slowness doesn't break UX (loading state?)

---

### E2E Test Requirements

**New Test:** `tests/e2e/locale-switching-refresh.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('TASK-011: Locale Switch Refresh', () => {
  test('Content updates immediately when switching locales without manual refresh', async ({ page }) => {
    // 1. Visit English homepage
    await page.goto('http://localhost:5183/en');
    await expect(page.locator('h1')).toContainText('Welcome to Best');

    // 2. Switch to Thai - content should update automatically
    await page.locator('[data-testid="locale-button-th"]').click();
    await page.waitForURL(/\/th$/);

    // 3. Verify Thai content WITHOUT manual refresh
    // This is the critical test - if content is still English, bug exists
    await expect(page.locator('h1')).toContainText('ยินดีต้อนรับสู่');
    await expect(page.locator('h1')).not.toContainText('Welcome');

    // 4. Switch back to English - content should update automatically
    await page.locator('[data-testid="locale-button-en"]').click();
    await page.waitForURL(/\/en$/);

    // 5. Verify English content restored
    await expect(page.locator('h1')).toContainText('Welcome to Best');
    await expect(page.locator('h1')).not.toContainText('ยินดีต้อนรับสู่');
  });

  test('Browser back/forward navigation maintains correct locale content', async ({ page }) => {
    // 1. Visit English homepage
    await page.goto('http://localhost:5183/en');
    await expect(page.locator('h1')).toContainText('Welcome');

    // 2. Switch to Thai
    await page.locator('[data-testid="locale-button-th"]').click();
    await page.waitForURL(/\/th$/);
    await expect(page.locator('h1')).toContainText('ยินดีต้อนรับสู่');

    // 3. Browser back button
    await page.goBack();
    await page.waitForURL(/\/en$/);
    await expect(page.locator('h1')).toContainText('Welcome');

    // 4. Browser forward button
    await page.goForward();
    await page.waitForURL(/\/th$/);
    await expect(page.locator('h1')).toContainText('ยินดีต้อนรับสู่');
  });

  test('Rapid locale switching does not cause errors', async ({ page }) => {
    await page.goto('http://localhost:5183/en');

    // Rapidly switch locales
    for (let i = 0; i < 5; i++) {
      await page.locator('[data-testid="locale-button-th"]').click();
      await page.waitForURL(/\/th$/);
      await page.locator('[data-testid="locale-button-en"]').click();
      await page.waitForURL(/\/en$/);
    }

    // Should end on English and work correctly
    await expect(page.locator('h1')).toContainText('Welcome');
  });
});
```

**Run Command:**
```bash
cd apps/frontend
npm run test:e2e tests/e2e/locale-switching-refresh.spec.ts
```

---

## Acceptance Criteria

- [ ] **AC-1:** User switches EN → TH → Thai content displays immediately (no manual refresh)
- [ ] **AC-2:** User switches TH → EN → English content displays immediately (no manual refresh)
- [ ] **AC-3:** Browser back/forward buttons maintain correct locale content
- [ ] **AC-4:** Rapid locale switching works without errors or race conditions
- [ ] **AC-5:** E2E test validates automatic content update on locale switch
- [ ] **AC-6:** Fix works on both products (bestays + realestate)

---

## Rollback Plan

**If Fix Causes Issues:**

1. **Revert Commit:**
```bash
git revert <commit-hash>
git push origin fix/TASK-011-US-021
```

2. **Alternative Fallback (Option 2):**
```typescript
// Use full page reload instead
function switchLocale(newLocale: Locale) {
  const currentPath = $page.url.pathname.replace(/^\/(en|th)/, '');
  window.location.href = `/${newLocale}${currentPath || ''}`;
}
```

**Risk Assessment:** Low - `invalidateAll()` is a standard SvelteKit pattern with no known issues

---

## Performance Considerations

**Impact of `invalidateAll()`:**
- Re-runs ALL load functions (layout + page)
- For homepage: 2 API calls (title + description)
- Adds ~100-200ms latency on locale switch

**Is This Acceptable?**
- ✅ YES - User expects some delay when switching locales
- ✅ Still faster than full page reload (Option 2)
- ✅ Better UX than requiring manual refresh (current bug)

**Future Optimization (Out of Scope):**
- Use `invalidate()` with specific URLs instead of `invalidateAll()`
- Implement optimistic UI updates while fetching

---

## Documentation Updates

**File Header Update (LocaleSwitcher.svelte):**
```markdown
NOTES:
  - Preserves current path (e.g., /en/dashboard → /th/dashboard)
  - Active locale shown with blue background
  - Accessible with ARIA attributes
  - data-testid for E2E testing
  - Uses invalidateAll() to force load function re-run on locale switch (TASK-011)
```

---

## Related Files

**Files to Modify:**
- `apps/frontend/src/lib/components/LocaleSwitcher.svelte` (implementation)

**Files to Create:**
- `apps/frontend/tests/e2e/locale-switching-refresh.spec.ts` (E2E tests)

**Files for Reference:**
- `apps/frontend/src/routes/[lang]/+page.ts` (load function that gets invalidated)
- `apps/frontend/src/routes/[lang]/+page.svelte` (receives updated data)

---

## Estimated Time

- **Implementation:** 15 minutes (simple code change)
- **Manual Testing:** 30 minutes (both products, edge cases)
- **E2E Testing:** 45 minutes (write + run tests)
- **Documentation:** 15 minutes (update file headers, commit message)
- **Total:** ~2 hours

---

**Status:** Solution approved, ready for implementation
**Next Phase:** IMPLEMENTATION (spawn dev-frontend-svelte agent)
