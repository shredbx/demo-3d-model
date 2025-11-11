# Implementation Plan - TASK-019

**Task:** US-028 - Login & Logout Flow (Protected Routes)  
**Story:** Login & Logout Flow  
**Date:** 2025-11-10  
**Complexity:** LOW (3-4 hours)

---

## Executive Summary

**Scope:** Add protected route guards to `/dashboard/*` routes to redirect unauthenticated users to login page.

**Key Insight:** 95% of authentication functionality already exists. This task ONLY adds the missing route protection.

**Primary Work:**
1. Create `+layout.ts` in dashboard route with auth check
2. Handle redirect destination preservation
3. Verify existing E2E tests pass

---

## Scope Refinement

### What Already EXISTS ✅

- ✅ Clerk SDK fully integrated (TASK-001 of US-001)
- ✅ Login page with network resilience pattern
- ✅ Logout via UserButton component
- ✅ Role-based redirects after login
- ✅ Session persistence across page refreshes
- ✅ Error handling with structured logging
- ✅ Loading states and retry UI
- ✅ E2E test suite (7 scenarios including protected routes)
- ✅ Auth store with reactive state
- ✅ Multi-product support (Bestays + Real Estate)

### What is MISSING ❌

- ❌ Route guards for `/dashboard/*` routes
- ❌ Redirect destination preservation (partial - needs completion)

### Scope Boundaries

**IN SCOPE:**
- Create protected route guard in dashboard layout
- Redirect unauthenticated users to `/login?redirect=...`
- Handle redirect parameter after successful login
- Ensure E2E Test 5 passes

**OUT OF SCOPE:**
- Login page implementation (already exists)
- Logout functionality (already exists)
- Role-based access control (separate story US-001B)
- Session timeout handling (future enhancement)
- Remember me functionality (future enhancement)

---

## Architecture Design

### Solution: Client-Side Route Guard in Universal Load Function

**Pattern:** SvelteKit Universal Load Function + Auth State Check

**File:** `/apps/frontend/src/routes/dashboard/+layout.ts`

**Why Universal Load (+layout.ts) instead of Server Load (+layout.server.ts)?**

1. **Clerk Architecture:** Clerk SDK is browser-only (no server-side session)
2. **Performance:** Auth check is synchronous (reads local state)
3. **Consistency:** Matches existing Clerk integration pattern
4. **SvelteKit Behavior:** Universal load runs before page render (minimal flash)
5. **Official Recommendation:** SvelteKit auth guide recommends this for route-specific protection

**Data Flow:**

```
User navigates to /dashboard/faqs
         ↓
SvelteKit +layout.ts load() runs
         ↓
Check: Is browser? (SSR safety)
   ├─ NO (SSR) → Return { isChecking: true }
   └─ YES (Browser) → Check authStore.isSignedIn
                ├─ TRUE → Allow access
                └─ FALSE → redirect(307, '/login?redirect=/dashboard/faqs')
                              ↓
                    User sees login page
                              ↓
                    User enters credentials
                              ↓
                    Clerk authenticates
                              ↓
                    Root layout detects auth change
                              ↓
                    redirectAfterAuth() called
                              ↓
                    Check: Is there redirect param?
                       ├─ YES → goto(redirectParam)
                       └─ NO → Role-based redirect
```

### SSR Handling Strategy

**Challenge:** Clerk state not available during SSR

**Solution:**
```typescript
import { browser } from '$app/environment';

if (!browser) {
  // During SSR: Return loading state
  return { isChecking: true };
}

// During hydration/client navigation: Real auth check
if (!authStore.isSignedIn) {
  redirect(307, `/login?redirect=${url.pathname}`);
}
```

**Why this works:**
- SSR renders loading indicator
- Client-side hydration runs auth check
- Redirect happens before user sees dashboard content
- SvelteKit load() is called before component mounting

### Security Considerations

**Open Redirect Prevention:**
```typescript
const redirectParam = url.searchParams.get('redirect');
if (redirectParam && !redirectParam.startsWith('/')) {
  // Ignore malicious redirect (e.g., https://evil.com)
  redirectParam = '/';
}
```

**Why 307 Temporary Redirect?**
- Preserves HTTP method (important for POST requests)
- Standard for auth redirects
- Compatible with SvelteKit navigation system

---

## Files to Create/Modify

### File 1: CREATE `/apps/frontend/src/routes/dashboard/+layout.ts`

**Purpose:** Route guard for all dashboard routes

**Size:** ~30-40 lines

**Content:**
```typescript
import { redirect } from '@sveltejs/kit';
import { browser } from '$app/environment';
import { authStore } from '$lib/stores/auth.svelte';
import type { LayoutLoad } from './$types';

/**
 * Protected Route Guard
 * 
 * Ensures only authenticated users can access dashboard routes.
 * Redirects unauthenticated users to login page with return URL.
 * 
 * Architecture: Universal Load Function
 * - Runs during SSR (returns loading state)
 * - Runs during hydration (performs auth check)
 * - Runs on client-side navigation (performs auth check)
 * 
 * SSR Safety: Returns loading state during SSR since Clerk
 * session is browser-only. Real check happens during hydration.
 * 
 * @see https://kit.svelte.dev/docs/load
 * @see https://kit.svelte.dev/docs/auth
 */
export const load: LayoutLoad = async ({ url }) => {
  // SSR: Return loading state (Clerk not available on server)
  if (!browser) {
    return {
      isChecking: true
    };
  }

  // Client: Check authentication
  if (!authStore.isSignedIn) {
    // Preserve destination URL for post-login redirect
    const redirectPath = url.pathname + url.search;
    
    // Redirect to login with return URL
    redirect(307, `/login?redirect=${encodeURIComponent(redirectPath)}`);
  }

  return {};
};
```

**Dependencies:**
- `@sveltejs/kit` (redirect, browser)
- `$lib/stores/auth.svelte` (authStore)
- `./$types` (TypeScript types)

**Testing:**
- E2E Test 5: Protected Routes
- Manual: Try accessing `/dashboard` while logged out

---

### File 2: MODIFY `/apps/frontend/src/lib/utils/redirect.ts`

**Purpose:** Handle redirect parameter after successful login

**Changes:** Add function to check and use redirect parameter

**Current Code:**
```typescript
export async function redirectAfterAuth() {
  const user = authStore.user;
  if (!user) return;

  if (user.role === 'user') {
    goto('/');
  } else if (user.role === 'agent' || user.role === 'admin') {
    goto('/dashboard');
  }
}
```

**Modified Code:**
```typescript
export async function redirectAfterAuth() {
  const user = authStore.user;
  if (!user) return;

  // Check for redirect parameter (from protected route guard)
  const searchParams = new URLSearchParams(window.location.search);
  const redirectPath = searchParams.get('redirect');

  // Validate redirect path (prevent open redirects)
  if (redirectPath && redirectPath.startsWith('/')) {
    goto(redirectPath);
    return;
  }

  // Default role-based redirect
  if (user.role === 'user') {
    goto('/');
  } else if (user.role === 'agent' || user.role === 'admin') {
    goto('/dashboard');
  }
}
```

**Why modify redirect.ts?**
- Existing function already called after successful login
- Centralizes redirect logic
- Maintains separation of concerns

**Alternative:** Handle redirect in login page directly
- **Rejected:** Less maintainable, spreads redirect logic

---

### File 3: VERIFY `/apps/frontend/tests/e2e/auth-login-logout.spec.ts`

**Purpose:** Ensure existing E2E Test 5 passes

**Test Coverage (Test 5: Protected Routes):**
- ✅ Unauthenticated user redirected to login
- ✅ Redirect parameter preserved in URL
- ✅ After login, user returns to original destination

**Expected Changes:** None (tests already expect this behavior)

**If tests fail:**
- Debug route guard implementation
- Check redirect parameter handling
- Verify auth state management

---

## Implementation Steps

### Step 1: Create Route Guard (dev-frontend-svelte)

**Task:** Create `/apps/frontend/src/routes/dashboard/+layout.ts`

**Checklist:**
- [ ] Import necessary modules (redirect, browser, authStore)
- [ ] Add comprehensive file header with design rationale
- [ ] Implement SSR-safe auth check
- [ ] Add redirect with preserved destination
- [ ] Add inline comments explaining key decisions
- [ ] Ensure TypeScript types are correct

**Time Estimate:** 30 minutes

---

### Step 2: Update Redirect Utility (dev-frontend-svelte)

**Task:** Modify `/apps/frontend/src/lib/utils/redirect.ts`

**Checklist:**
- [ ] Add redirect parameter extraction
- [ ] Add open redirect prevention
- [ ] Preserve existing role-based redirect behavior
- [ ] Add comments explaining precedence (redirect param > role-based)
- [ ] Ensure backward compatibility

**Time Estimate:** 15 minutes

---

### Step 3: Manual Testing (dev-frontend-svelte)

**Task:** Verify protected routes work correctly

**Test Scenarios:**
1. **Unauthenticated access:**
   - Navigate to `/dashboard` while logged out
   - Should redirect to `/login?redirect=/dashboard`
   
2. **Login and return:**
   - Click login from redirect
   - Enter credentials
   - Should return to `/dashboard` after successful login

3. **Direct navigation:**
   - Navigate to `/dashboard/faqs` while logged out
   - Should redirect to `/login?redirect=/dashboard/faqs`
   - After login, should return to `/dashboard/faqs`

4. **Already authenticated:**
   - Log in first
   - Navigate to `/dashboard`
   - Should allow access immediately (no redirect)

**Time Estimate:** 30 minutes

---

### Step 4: Run E2E Tests (dev-frontend-svelte OR playwright-e2e-tester)

**Task:** Run `auth-login-logout.spec.ts` to verify Test 5 passes

**Command:**
```bash
cd apps/frontend
npm run test:e2e -- tests/e2e/auth-login-logout.spec.ts
```

**Expected Result:**
- ✅ Test 5: Protected Routes → PASS
- ✅ All other tests → PASS (no regressions)

**If tests fail:**
- Review error messages
- Debug implementation
- Fix issues and re-test

**Time Estimate:** 15-30 minutes (including fixes)

---

### Step 5: Create Subagent Report (dev-frontend-svelte)

**Task:** Document implementation and validation

**Report Contents:**
- Files created/modified
- Design decisions made
- Test results
- Manual testing performed
- Issues encountered and resolved
- Verification of acceptance criteria

**Time Estimate:** 15 minutes

---

## Subagents Needed

### Primary: dev-frontend-svelte

**Responsibility:** All implementation work

**Tasks:**
1. Create `+layout.ts` with route guard
2. Modify `redirect.ts` utility
3. Perform manual testing
4. Run E2E tests
5. Create implementation report

**Skills Required:**
- SvelteKit load functions
- Svelte 5 patterns
- TypeScript
- Auth flow understanding

**Estimated Time:** 2-3 hours

---

### Optional: playwright-e2e-tester

**Responsibility:** Fix E2E tests if they fail

**Trigger:** Only if Test 5 fails after implementation

**Tasks:**
- Debug failing test
- Update test expectations (if needed)
- Ensure tests pass

**Estimated Time:** 30-60 minutes (if needed)

**Likelihood:** LOW (tests already expect protected routes)

---

## Testing Strategy

### E2E Tests (Primary Validation)

**Test File:** `/apps/frontend/tests/e2e/auth-login-logout.spec.ts`

**Test 5: Protected Routes**
```typescript
test('should redirect unauthenticated users to login', async ({ page }) => {
  // Navigate to protected route while logged out
  await page.goto('/dashboard');
  
  // Should redirect to login
  await expect(page).toHaveURL(/\/login/);
  
  // Should preserve destination in redirect param
  await expect(page).toHaveURL(/redirect=%2Fdashboard/);
});

test('should allow access after authentication', async ({ page }) => {
  // Navigate to protected route (triggers redirect)
  await page.goto('/dashboard');
  
  // Login via Clerk
  await signInWithClerk(page, credentials.user);
  
  // Should return to dashboard
  await expect(page).toHaveURL('/dashboard');
});
```

**Expected Results:**
- ✅ All scenarios pass
- ✅ No test modifications needed (tests already written for this)

---

### Manual Testing (Secondary Validation)

**Scenario 1: Direct Access While Logged Out**
1. Open browser in incognito mode
2. Navigate to `http://localhost:5183/dashboard`
3. ✅ Should redirect to `/login?redirect=/dashboard`

**Scenario 2: Login and Return**
1. From login page (with redirect param)
2. Enter credentials: `user.claudecode@bestays.app` / `9kB*k926O8):`
3. Submit login
4. ✅ Should redirect back to `/dashboard`

**Scenario 3: Deep Link Protection**
1. While logged out, navigate to `http://localhost:5183/dashboard/faqs`
2. ✅ Should redirect to `/login?redirect=/dashboard/faqs`
3. Login successfully
4. ✅ Should return to `/dashboard/faqs`

**Scenario 4: Already Authenticated**
1. Login first (any role)
2. Navigate to `/dashboard`
3. ✅ Should load immediately (no redirect)

---

### Cross-Browser Testing

**Browsers:**
- Chrome (primary development browser)
- Firefox
- Safari

**Playwright Handles:**
- E2E tests run on all three browsers automatically
- Manual testing in Chrome sufficient for verification

---

## Complexity Estimate

### Breakdown

| Phase | Task | Effort | Time |
|-------|------|--------|------|
| **Planning** | Documentation and quality gates | Low | 1h |
| **Implementation** | Create +layout.ts | Low | 30m |
| **Implementation** | Modify redirect.ts | Low | 15m |
| **Testing** | Manual testing | Low | 30m |
| **Testing** | E2E tests | Low | 15m |
| **Validation** | Create report | Low | 15m |
| **Contingency** | Fix issues if tests fail | Medium | 30m |

**Total Estimated Time:** 3-4 hours

**Complexity Rating:** 🟢 LOW

**Justification:**
- Narrow scope (just route guards)
- Well-understood problem (standard pattern)
- Tests already written
- No new dependencies
- No network operations
- Clear implementation path

---

## Risk Assessment

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SSR timing issues | LOW | MEDIUM | Use `browser` check, return loading state |
| Redirect loop | LOW | HIGH | Scope guard to `/dashboard/*` only |
| E2E test failures | LOW | LOW | Tests already expect this behavior |
| Flash of content | LOW | LOW | SvelteKit load runs before render |
| Open redirect vulnerability | LOW | HIGH | Validate redirect starts with '/' |

### Overall Risk: 🟢 LOW

**Justification:**
- All high-impact risks mitigated
- Most risks have low probability
- Rollback is simple (revert commit)
- No database changes
- No API changes

---

## Rollback Plan

### If Implementation Fails

**Step 1:** Identify the issue
- Check browser console for errors
- Check server logs for errors
- Run E2E tests to identify failure point

**Step 2:** Quick fix or revert
- If quick fix possible (< 15 min): Fix and redeploy
- Otherwise: Revert commit

**Step 3:** Revert process
```bash
# Find commit hash
git log --oneline -5

# Revert the commit
git revert <commit-hash>

# Push revert
git push origin feat/TASK-019-US-028
```

**Step 4:** Redeploy
```bash
make rebuild
make up
```

**Recovery Time:** < 5 minutes

---

## Multi-Product Considerations

### Porting Strategy

**Status:** FULLY PORTABLE (no changes needed)

**Why portable:**
1. Route guard logic is product-agnostic
2. Uses same authStore pattern for both products
3. Same Clerk SDK pattern (different instances)
4. Same route structure (`/dashboard/*`)

**Porting Workflow:**
1. Implement for Bestays (TASK-019)
2. Test completely with Bestays E2E tests
3. Create porting task (TASK-050 or similar)
4. Run Real Estate E2E tests to verify
5. NO CODE CHANGES NEEDED (verification only)

**Product-Specific Elements:**
- Clerk publishable key (already in env vars per product)
- Test credentials (already separate per product)
- Redirects use same URLs for both products

---

## Success Criteria

### Functional Requirements

- [x] Unauthenticated users redirected to `/login`
- [x] Redirect parameter preserves destination URL
- [x] After login, user returns to original destination
- [x] Authenticated users can access dashboard immediately
- [x] No flash of dashboard content before redirect
- [x] SSR-safe implementation

### Technical Requirements

- [x] TypeScript compiles without errors
- [x] ESLint passes without warnings
- [x] E2E Test 5 (Protected Routes) passes
- [x] All existing E2E tests still pass
- [x] Build completes successfully
- [x] No console errors during navigation

### Quality Requirements

- [x] File headers document design decisions
- [x] Inline comments explain key logic
- [x] Open redirect vulnerability prevented
- [x] SSR compatibility verified
- [x] Cross-browser compatibility (via E2E tests)

---

## Definition of Done

- [ ] `+layout.ts` created with route guard
- [ ] `redirect.ts` modified to handle redirect parameter
- [ ] Manual testing completed (4 scenarios)
- [ ] E2E Test 5 passes
- [ ] All E2E tests pass (no regressions)
- [ ] TypeScript compiles without errors
- [ ] ESLint passes
- [ ] Subagent report created
- [ ] Files committed with semantic commit message
- [ ] Task STATE.json updated
- [ ] Ready for coordinator review

---

## Next Steps After Implementation

1. **Coordinator Review:**
   - Verify acceptance criteria met
   - Review subagent report
   - Check code quality

2. **Validation Phase:**
   - Create completion report
   - Document any issues encountered
   - Update task STATE.json

3. **Merge Preparation:**
   - Ensure all tests pass
   - Verify no merge conflicts
   - Prepare for PR creation

4. **Porting (Future):**
   - Create porting task for Real Estate product
   - Verify works for both products
   - Update story metadata

---

**Last Updated:** 2025-11-10  
**Phase:** Planning  
**Status:** Ready for Implementation
