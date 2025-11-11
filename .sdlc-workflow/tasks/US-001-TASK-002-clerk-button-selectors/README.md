# Task: Fix Clerk Button Interaction Selectors in E2E Tests

**Task ID:** US-001-TASK-002
**User Story:** US-001 (Login Flow Validation)
**Created:** 2025-11-06
**Status:** IN_PROGRESS

---

## Problem Statement

E2E tests for login flow are failing because Playwright cannot interact with Clerk's authentication buttons. The buttons are marked with `aria-hidden="true"`, making them invisible to standard Playwright selectors.

**Error Pattern:**
```
locator resolved to <button type="submit" aria-hidden="true"></button>
- element is not visible
- retrying click action (times out after 30s)
```

**Impact:** 10 critical acceptance criteria tests are blocked:
- AC-2.1: Successful login with valid credentials
- AC-2.2: Invalid credentials show error
- AC-3.3: Authenticated user can access dashboard
- AC-4.1, AC-4.2, AC-4.3: Session persistence tests
- AC-5.1, AC-5.2, AC-5.3: Logout functionality tests

---

## Root Cause Analysis

From previous investigation (US-001-TASK-001):
- Clerk renders multiple button instances, some with `aria-hidden="true"` for accessibility
- Current selectors (`button:has-text("Continue")`, `button[type="submit"]`) match hidden elements first
- Playwright correctly refuses to click hidden elements

**Possible Clerk Rendering Methods:**
1. **Iframes** - Clerk UI in separate iframe context
2. **Shadow DOM** - Encapsulated web components
3. **Multiple DOM nodes** - Hidden + visible buttons for responsive/accessibility
4. **React Portal** - Dynamically mounted elsewhere in DOM

---

## Objectives

1. **Debug Clerk's DOM structure**
   - Identify if Clerk uses iframes, shadow DOM, or standard DOM
   - Find the correct visible button selectors
   - Document Clerk's UI architecture

2. **Fix test selectors**
   - Update `signInWithClerk()` helper function
   - Update email/password input selectors
   - Update continue/submit button selectors
   - Ensure selectors target visible elements only

3. **Validate solution**
   - All 10 blocked tests must pass
   - No timeout errors
   - Proper redirects after login/logout

4. **Document findings**
   - Which Clerk rendering method was detected
   - Which selector strategy worked
   - Future-proof selector patterns

---

## Files to Modify

**Test File:**
- `apps/frontend/tests/e2e/login.spec.ts`
  - `signInWithClerk()` helper (lines 76-109)
  - `signOut()` helper (lines 114-128)

**No application code changes needed** - the login implementation is correct.

---

## Investigation Approach

### Option A: Iframe Detection
```typescript
// Check for Clerk iframe
const clerkFrame = page.frameLocator('iframe[title*="Clerk"]');
const continueButton = clerkFrame.locator('button[type="submit"]');
```

### Option B: Shadow DOM Pierce
```typescript
// Pierce shadow DOM
const continueButton = page.locator('pierce/button[type="submit"]');
```

### Option C: Filter Visible Elements
```typescript
// Filter out hidden elements
const continueButton = page.locator('button:has-text("Continue")')
  .filter({ hasNot: page.locator('[aria-hidden="true"]') });
```

### Option D: Use Clerk Data Attributes
```typescript
// Use Clerk's specific attributes (discovered via codegen)
const continueButton = page.locator('[data-locator-id="continue"]');
```

### Recommended Tools:
1. **Playwright Codegen** - Inspect actual Clerk UI structure
   ```bash
   cd apps/frontend
   npx playwright codegen http://localhost:5183/login
   ```

2. **Headed browser** - See what Playwright sees
   ```bash
   npx playwright test login.spec.ts --headed --debug
   ```

3. **Clerk Documentation** - Official E2E testing patterns
   - https://clerk.com/docs/testing/playwright
   - Check if Clerk provides test utilities

---

## Success Criteria

- [ ] Identified Clerk's rendering method (iframe/shadow DOM/standard DOM)
- [ ] Updated `signInWithClerk()` helper with working selectors
- [ ] Updated `signOut()` helper with working selectors
- [ ] All 10 authentication tests pass without timeout
- [ ] Tests run reliably (no flakiness)
- [ ] Selectors are maintainable and well-documented

---

## Test Credentials

- **Email:** `user.claudecode@bestays.app`
- **Password:** `9kB*k926O8):`

These are real Clerk test account credentials (already updated in TASK-001).

---

## Subagent Assignment

**Subagent:** `playwright-e2e-tester`
**Scope:** Debug Clerk DOM structure and fix test selectors

**Context Provided:**
- Current test implementation
- Previous investigation findings
- Suggested debugging approaches
- Expected deliverables

---

## Related Work

- **US-001-TASK-001** - Initial E2E test fixes (identified the Clerk selector issue)
- **User Story US-001** - Login Flow Validation (parent story)

---

## Expected Deliverables

**Subagent Report Must Include:**
1. Clerk rendering method detected (iframe/shadow DOM/other)
2. Which selector strategy worked (frameLocator/pierce/filter/etc.)
3. Updated test code showing the fix
4. Test results showing which tests now pass
5. Any remaining failures with root causes

---

## Notes

- This is purely a test-side fix (no application code changes)
- Clerk component works correctly in browser (manual testing confirms)
- Issue is only with Playwright automation selectors
- Solution must be maintainable for future Clerk UI updates
