# TASK-011: Fix Locale Switch Refresh Bug

**Story:** US-021 - Thai Localization & Locale Switching
**Type:** Bug Fix
**Status:** Not Started
**Branch:** fix/TASK-011-US-021

---

## Problem Statement

When users switch between locales (EN ↔ TH) using the LocaleSwitcher component, the page URL changes but the content does not update until a manual page refresh. This breaks the expected UX where locale switching should immediately display content in the selected language.

**User Report:**
> "switching language - page not reloads or changes not re-applied before refresh"

---

## Current Behavior

1. User visits `/en` homepage → Sees English content ✅
2. User clicks "TH" button → URL changes to `/th` ✅
3. **BUG:** Content remains in English ❌
4. User manually refreshes page → Thai content now displays ✅

---

## Expected Behavior

1. User visits `/en` homepage → Sees English content ✅
2. User clicks "TH" button → URL changes to `/th` ✅
3. **EXPECTED:** Content automatically updates to Thai ✅
4. No manual refresh needed ✅

---

## Root Cause Analysis

### Current Implementation

**LocaleSwitcher.svelte (line 46-53):**
```typescript
function switchLocale(newLocale: Locale) {
  // Remove current locale from path
  const currentPath = $page.url.pathname.replace(/^\/(en|th)/, '');

  // Navigate to new locale with same path
  goto(`/${newLocale}${currentPath || ''}`);
}
```

**+page.ts Load Function (line 46-87):**
```typescript
export const load: PageLoad = async ({ fetch, parent }) => {
  const { locale } = await parent();

  const [titleRes, descRes] = await Promise.all([
    fetch(`${API_BASE_URL}/api/v1/content/homepage.title?locale=${locale}`),
    fetch(`${API_BASE_URL}/api/v1/content/homepage.description?locale=${locale}`)
  ]);

  return {
    title: titleData.value,
    description: descData.value
  };
};
```

**+page.svelte (line 45-46):**
```typescript
let title = $state(data.title);
let description = $state(data.description);
```

### Why It's Not Working

**SvelteKit Behavior:**
- `goto()` performs client-side navigation
- By default, SvelteKit **does** re-run load functions on navigation
- HOWEVER, SvelteKit may cache load results if it considers them "still valid"
- The `parent()` call in `+page.ts` might be returning cached locale data

**Possible Issues:**
1. **Load function not invalidating:** SvelteKit thinks the data is still valid and doesn't re-fetch
2. **Reactive state not updating:** Svelte 5 runes might not be detecting the prop change
3. **Parent data cached:** The `{ locale }` from `await parent()` might be stale

---

## Solution Options

### Option 1: Add `invalidateAll()` (RECOMMENDED)

**Approach:** Explicitly invalidate all load functions after navigation.

**Implementation:**
```typescript
// LocaleSwitcher.svelte
import { invalidateAll } from '$app/navigation';

async function switchLocale(newLocale: Locale) {
  const currentPath = $page.url.pathname.replace(/^\/(en|th)/, '');

  // Navigate to new locale
  await goto(`/${newLocale}${currentPath || ''}`);

  // Force all load functions to re-run
  await invalidateAll();
}
```

**Pros:**
- Follows SvelteKit patterns and best practices
- Works with all load functions (layout + page)
- Maintains client-side navigation benefits (faster than full refresh)
- Type-safe

**Cons:**
- Slightly more complex than Option 2
- May re-fetch more data than necessary (invalidates ALL load functions)

**Validation:**
- User switches locale → Load function re-runs → Content updates immediately
- E2E test: Click TH → Verify content changes without manual refresh

---

### Option 2: Use `location.href` for Full Page Reload (SIMPLE)

**Approach:** Replace SvelteKit navigation with native browser navigation.

**Implementation:**
```typescript
// LocaleSwitcher.svelte
function switchLocale(newLocale: Locale) {
  const currentPath = $page.url.pathname.replace(/^\/(en|th)/, '');

  // Full page reload with new locale
  window.location.href = `/${newLocale}${currentPath || ''}`;
}
```

**Pros:**
- Simplest solution (guaranteed to work)
- No SvelteKit behavior assumptions
- No cache invalidation concerns

**Cons:**
- Full page reload (slower, visible flash)
- Loses SvelteKit's instant client-side navigation
- Not as elegant or modern

**Validation:**
- User switches locale → Full page reload → Content displays in new locale

---

### Option 3: Make Load Function Depend on URL Parameter (ALTERNATIVE)

**Approach:** Add URL parameter to force cache invalidation.

**Implementation:**
```typescript
// LocaleSwitcher.svelte
function switchLocale(newLocale: Locale) {
  const currentPath = $page.url.pathname.replace(/^\/(en|th)/, '');

  // Add timestamp to bust cache
  goto(`/${newLocale}${currentPath || ''}?t=${Date.now()}`);
}

// +page.ts
export const load: PageLoad = async ({ fetch, parent, url }) => {
  const { locale } = await parent();

  // url.searchParams automatically makes this dependent on URL changes
  console.log('Load running with timestamp:', url.searchParams.get('t'));

  // ... rest of load function
};
```

**Pros:**
- Guaranteed cache invalidation
- Still uses SvelteKit navigation

**Cons:**
- Hacky (timestamp in URL is ugly)
- Pollutes browser history
- Not a standard pattern

**Validation:**
- User switches locale → URL includes timestamp → Load function re-runs → Content updates

---

## Recommended Solution

**OPTION 1: Add `invalidateAll()`**

**Rationale:**
- This is the **official SvelteKit pattern** for forcing load functions to re-run
- Maintains modern client-side navigation UX
- Clear, explicit, and type-safe
- Documented in SvelteKit docs as best practice

**Implementation Plan:**
1. Update `LocaleSwitcher.svelte` to use `invalidateAll()`
2. Test locale switching in both products (bestays + realestate)
3. Add E2E test to verify content updates without manual refresh
4. Document pattern for future locale-dependent features

---

## Acceptance Criteria

- [ ] AC-1: User switches from EN → TH → Content updates immediately (no refresh needed)
- [ ] AC-2: User switches from TH → EN → Content updates immediately (no refresh needed)
- [ ] AC-3: Browser back/forward buttons work correctly with locale changes
- [ ] AC-4: Locale switching works on all pages that use locale (not just homepage)
- [ ] AC-5: E2E test validates automatic content update on locale switch

---

## Testing Strategy

### Manual Testing
1. Visit `http://localhost:5183/en`
2. Verify English content displays
3. Click "TH" button
4. **VERIFY:** Thai content displays immediately (no manual refresh)
5. Click "EN" button
6. **VERIFY:** English content displays immediately
7. Test browser back button → Previous locale content displays
8. Test on all locale-aware pages (homepage, dashboard, etc.)

### E2E Testing
```typescript
// tests/e2e/locale-switching.spec.ts (UPDATE)
test('Content updates immediately on locale switch without manual refresh', async ({ page }) => {
  await page.goto('http://localhost:5183/en');

  // Verify English content
  await expect(page.locator('h1')).toContainText('Welcome to Best');

  // Switch to Thai
  await page.locator('[data-testid="locale-button-th"]').click();

  // Wait for navigation
  await page.waitForURL(/\/th$/);

  // Verify Thai content WITHOUT manual refresh
  await expect(page.locator('h1')).toContainText('ยินดีต้อนรับสู่');

  // Switch back to English
  await page.locator('[data-testid="locale-button-en"]').click();
  await page.waitForURL(/\/en$/);

  // Verify English content restored
  await expect(page.locator('h1')).toContainText('Welcome to Best');
});
```

---

## Files to Modify

1. **apps/frontend/src/lib/components/LocaleSwitcher.svelte**
   - Add `import { invalidateAll } from '$app/navigation'`
   - Update `switchLocale()` to be async and call `invalidateAll()`

2. **apps/frontend/tests/e2e/*.spec.ts**
   - Add test for immediate content update on locale switch
   - Verify no manual refresh required

---

## Estimated Effort

- **Research:** 0.5 hours (DONE via this analysis)
- **Implementation:** 0.5 hours (update LocaleSwitcher + add tests)
- **Testing:** 1 hour (manual + E2E validation on both products)
- **Total:** 2 hours

---

## Dependencies

- **Blocks:** None
- **Blocked By:** None (can be implemented immediately)
- **Related:** TASK-010 (original locale switching implementation)

---

## Notes

- This bug was discovered during manual validation of TASK-010
- The issue affects UX significantly (users must manually refresh to see translated content)
- Fix is straightforward and low-risk
- Should be prioritized before E2E testing phase of TASK-010 is marked complete

---

**Status:** Awaiting user approval on solution approach
**Next Step:** Get user confirmation on Option 1 (recommended) or Option 2 (simpler)
