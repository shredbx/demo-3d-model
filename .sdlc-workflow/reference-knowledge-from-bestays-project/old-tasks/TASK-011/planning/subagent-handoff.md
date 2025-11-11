# Subagent Handoff: TASK-011 Locale Switch Refresh Fix

**Agent:** dev-frontend-svelte
**Task:** TASK-011 - Fix Locale Switch Refresh Bug
**Story:** US-021
**Branch:** fix/TASK-011-US-021

---

## Your Mission

Fix the locale switching bug where content doesn't update immediately when users switch between EN and TH locales. Add explicit SvelteKit load invalidation to force content refresh.

---

## What You Need to Do

### 1. Update LocaleSwitcher Component

**File:** `apps/frontend/src/lib/components/LocaleSwitcher.svelte`

**Changes:**

1. Add import at top:
```typescript
import { invalidateAll } from '$app/navigation';
```

2. Make `switchLocale()` function async and add invalidation:
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

3. Update file header NOTES section to include:
```markdown
  - Uses invalidateAll() to force load function re-run on locale switch (TASK-011)
```

**That's it!** This is a simple one-file change.

---

## Why This Works

**The Problem:**
- `goto()` changes URL from `/en` to `/th`
- SvelteKit load function in `+page.ts` should re-run
- BUT SvelteKit caches the result and doesn't detect the locale dependency
- Content stays in old locale until manual refresh

**The Solution:**
- `invalidateAll()` explicitly tells SvelteKit: "all data is stale"
- Forces ALL load functions (layout + page) to re-run
- Load function fetches content with new locale parameter
- Content updates automatically

---

## Testing Instructions

### Manual Testing (Both Products)

**Bestays (`localhost:5183`):**
1. Visit `http://localhost:5183/en`
2. Verify page shows English content (e.g., "Welcome to Best...")
3. Click "TH" button in header
4. **CRITICAL CHECK:** Content should immediately change to Thai (ยินดีต้อนรับสู่...)
5. **NO MANUAL REFRESH NEEDED**
6. Click "EN" button
7. Content should immediately change back to English
8. Test browser back/forward buttons - content should match locale

**Real Estate (`localhost:5184`):**
- Repeat same steps as above

**Success Criteria:**
- ✅ Locale switch updates content immediately
- ✅ No manual page refresh needed
- ✅ Browser navigation works correctly

---

### Manual Test Script

Run this test and report results:

```bash
# Test Plan: TASK-011 Locale Switch Refresh

PRODUCT: Bestays
URL: http://localhost:5183

TEST 1: EN → TH Switch
1. Visit /en
2. Verify: h1 contains "Welcome" or "Best"
3. Click: [data-testid="locale-button-th"]
4. Verify: URL changed to /th
5. Verify: h1 now contains "ยินดีต้อนรับสู่" (without manual refresh)
RESULT: [ ] PASS [ ] FAIL

TEST 2: TH → EN Switch
1. From /th page
2. Click: [data-testid="locale-button-en"]
3. Verify: URL changed to /en
4. Verify: h1 now contains "Welcome" (without manual refresh)
RESULT: [ ] PASS [ ] FAIL

TEST 3: Browser Back/Forward
1. Visit /en, switch to /th, switch to /en
2. Click browser back button (should go to /th)
3. Verify: Content is Thai
4. Click browser forward button (should go to /en)
5. Verify: Content is English
RESULT: [ ] PASS [ ] FAIL

TEST 4: Rapid Switching
1. Rapidly click TH → EN → TH → EN → TH (5 times)
2. Verify: No errors in console
3. Verify: Content matches final locale
RESULT: [ ] PASS [ ] FAIL

---

PRODUCT: Real Estate
URL: http://localhost:5184

[Repeat TEST 1-4 above]
RESULT: [ ] PASS [ ] FAIL
```

---

## Implementation Checklist

- [ ] Add `import { invalidateAll }` to LocaleSwitcher.svelte
- [ ] Make `switchLocale()` async
- [ ] Add `await invalidateAll()` after `await goto()`
- [ ] Update file header NOTES section
- [ ] Manual test on bestays (localhost:5183)
- [ ] Manual test on realestate (localhost:5184)
- [ ] Verify no console errors
- [ ] Commit changes with proper message

---

## Commit Message Format

```
fix: locale switch updates content without manual refresh (US-021 TASK-011)

Subagent: dev-frontend-svelte
Product: bestays (portable to realestate)
Files: apps/frontend/src/lib/components/LocaleSwitcher.svelte

Added invalidateAll() after locale navigation to force SvelteKit
load functions to re-run with new locale parameter. This ensures
content updates immediately when switching between EN and TH
without requiring manual page refresh.

Technical Details:
- Import invalidateAll from $app/navigation
- Make switchLocale() async
- Call invalidateAll() after goto() navigation
- Forces +page.ts load function to re-fetch locale-specific content

Fixes: Locale switch bug where content stayed in old language until
manual refresh (reported during TASK-010 validation)

Story: US-021
Task: TASK-011

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Expected Output

After implementation, report back with:

1. **Manual Test Results:**
   - Bestays: PASS/FAIL for each test
   - Real Estate: PASS/FAIL for each test

2. **Console Errors:** Any errors during testing?

3. **Commit Hash:** SHA of your commit

4. **Files Modified:**
   - `apps/frontend/src/lib/components/LocaleSwitcher.svelte`

---

## Reference Files

**Load Function (for context):**
- `apps/frontend/src/routes/[lang]/+page.ts` - Gets invalidated by invalidateAll()

**Page Component (for context):**
- `apps/frontend/src/routes/[lang]/+page.svelte` - Receives updated data

**Story Documentation:**
- `.sdlc-workflow/stories/homepage/US-021-locale-switching.md`
- `.claude/tasks/TASK-011/README.md`
- `.claude/tasks/TASK-011/planning/solution-spec.md`

---

## Success Criteria

Your implementation is successful when:
- ✅ Users can switch locales without manual refresh
- ✅ Content updates immediately on locale switch
- ✅ Browser navigation works correctly
- ✅ No console errors
- ✅ Works on both products (bestays + realestate)

---

## Questions?

If anything is unclear:
1. Read `.claude/tasks/TASK-011/planning/solution-spec.md` for technical details
2. Reference SvelteKit docs: https://kit.svelte.dev/docs/modules#$app-navigation-invalidateall
3. Check existing implementation in `LocaleSwitcher.svelte`

---

**Time Estimate:** 15-30 minutes for implementation + testing
**Risk Level:** LOW (simple change, standard SvelteKit pattern)
**Rollback Plan:** Revert commit if any issues

**Ready to start!** 🚀
