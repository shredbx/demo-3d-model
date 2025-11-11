# Test Plan - Clerk Mounting Race Condition Fix

**Date:** 2025-11-06  
**Phase:** PLANNING  
**Task:** TASK-001 (US-001: Login Flow Validation)  
**For:** QA and Testing Teams

---

## Overview

This document defines the comprehensive testing strategy for validating the Clerk authentication race condition fix. Tests cover E2E scenarios, performance benchmarks, browser compatibility, and manual testing checklists.

**Primary Goal:** Verify that login form appears reliably on all network speeds with no race conditions.

**Secondary Goal:** Ensure no regressions in existing authentication flows.

---

## Test Strategy

### Test Pyramid

```
                    Manual Testing (10%)
                   /                    \
              E2E Tests (30%)         Browser Testing
             /                \
    Integration Tests (30%)   Performance Tests
   /                        \
Unit Tests (30%)           Accessibility Tests
```

---

## 1. Unit Tests

### 1.1 waitForClerkReady() Function Tests

**Location:** `apps/frontend/src/routes/login/+page.spec.ts` (create if not exists)

**Test Cases:**

#### Test 1.1.1: Returns true when Clerk is already loaded
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('waitForClerkReady', () => {
  it('should return true immediately if clerk.loaded is true', async () => {
    // Mock clerk as already loaded
    const mockClerk = { loaded: true };
    
    // Call function
    const result = await waitForClerkReady(1000);
    
    // Assert
    expect(result).toBe(true);
  });
});
```

#### Test 1.1.2: Returns true when Clerk loads within timeout
```typescript
it('should return true when clerk.loaded becomes true within timeout', async () => {
  // Mock clerk as not loaded initially
  const mockClerk = { loaded: false };
  
  // Simulate clerk.loaded becoming true after 500ms
  setTimeout(() => {
    mockClerk.loaded = true;
  }, 500);
  
  // Call function with 2s timeout
  const result = await waitForClerkReady(2000);
  
  // Assert
  expect(result).toBe(true);
});
```

#### Test 1.1.3: Returns false when timeout reached
```typescript
it('should return false when timeout is reached', async () => {
  // Mock clerk as never loading
  const mockClerk = { loaded: false };
  
  // Call function with short timeout
  const result = await waitForClerkReady(500);
  
  // Assert
  expect(result).toBe(false);
});
```

#### Test 1.1.4: Updates loadingTime state correctly
```typescript
it('should update loadingTime every second', async () => {
  const mockClerk = { loaded: false };
  let loadingTimeValue = 0;
  
  // Mock loadingTime state update
  const updateLoadingTime = (val: number) => {
    loadingTimeValue = val;
  };
  
  // Start waitForClerkReady with 3s timeout
  setTimeout(() => { mockClerk.loaded = true; }, 2500);
  
  await waitForClerkReady(3000);
  
  // Assert loadingTime was updated (should be 2 or 3)
  expect(loadingTimeValue).toBeGreaterThanOrEqual(2);
});
```

**Priority:** HIGH  
**Estimated Time:** 2 hours

---

## 2. E2E Tests (Playwright)

### 2.1 Normal Network Speed Tests

**Location:** `apps/frontend/tests/e2e/login.spec.ts`

#### Test 2.1.1: Login form loads successfully on fast connection

```typescript
import { test, expect } from '@playwright/test';

test('login form should appear within 2 seconds on normal network', async ({ page }) => {
  // Navigate to login page
  await page.goto('/login');
  
  // Wait for form to appear (should be fast)
  const signInContainer = page.locator('[data-testid="clerk-signin-container"]');
  await expect(signInContainer).toBeVisible({ timeout: 2000 });
  
  // Verify Clerk form elements are present
  await expect(page.locator('input[type="email"]')).toBeVisible();
});
```

**Acceptance Criteria:** AC-1 (< 2s load time)  
**Priority:** P0 (Critical)

---

#### Test 2.1.2: No race condition errors in console

```typescript
test('no console errors during login form mount', async ({ page }) => {
  const consoleErrors: string[] = [];
  
  // Capture console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  
  // Navigate and mount form
  await page.goto('/login');
  await page.waitForSelector('[data-testid="clerk-signin-container"]');
  
  // Wait a bit more for any delayed errors
  await page.waitForTimeout(1000);
  
  // Assert no errors
  expect(consoleErrors).toHaveLength(0);
});
```

**Acceptance Criteria:** AC-2 (100% mount success)  
**Priority:** P0 (Critical)

---

### 2.2 Slow Network Tests

**Setup:** Use Playwright network throttling

```typescript
import { test, expect, chromium } from '@playwright/test';

test.describe('Slow Network Scenarios', () => {
  test.use({
    // Simulate Slow 3G
    contextOptions: {
      offline: false,
      downloadThroughput: (50 * 1024) / 8, // 50 Kbps
      uploadThroughput: (50 * 1024) / 8,
      latency: 2000, // 2s latency
    },
  });

  // Tests go here
});
```

#### Test 2.2.1: Form appears on slow 3G network

```typescript
test('login form should appear even on slow 3G', async ({ page }) => {
  // Navigate to login
  await page.goto('/login');
  
  // Wait for loading spinner
  await expect(page.locator('text=Loading authentication...')).toBeVisible();
  
  // Wait for form to appear (generous timeout for slow network)
  const signInContainer = page.locator('[data-testid="clerk-signin-container"]');
  await expect(signInContainer).toBeVisible({ timeout: 15000 });
  
  // Verify form is functional
  await expect(page.locator('input[type="email"]')).toBeVisible();
});
```

**Acceptance Criteria:** AC-2 (100% mount success)  
**Priority:** P0 (Critical)

---

#### Test 2.2.2: Progress message appears after 3 seconds

```typescript
test('progress message should appear after 3 seconds', async ({ page }) => {
  await page.goto('/login');
  
  // Wait 3 seconds
  await page.waitForTimeout(3000);
  
  // Verify progress message appears
  await expect(page.locator('text=/This is taking longer than expected/')).toBeVisible();
  
  // Verify elapsed time is shown
  await expect(page.locator('text=/\\(\\d+s\\)/')).toBeVisible();
});
```

**Acceptance Criteria:** AC-4 (User-friendly loading feedback)  
**Priority:** P1 (High)

---

#### Test 2.2.3: No timeout error before 10 seconds

```typescript
test('should not show timeout error before 10 seconds', async ({ page }) => {
  await page.goto('/login');
  
  // Wait 9 seconds (just before timeout)
  await page.waitForTimeout(9000);
  
  // Verify NO error message is shown
  const errorMessage = page.locator('text=/took too long to initialize/');
  await expect(errorMessage).not.toBeVisible();
});
```

**Acceptance Criteria:** AC-2 (Proper timeout handling)  
**Priority:** P1 (High)

---

### 2.3 Extreme Network Conditions

#### Test 2.3.1: Timeout error after 10 seconds

```typescript
test('should show timeout error if loading takes > 10 seconds', async ({ page }) => {
  // Simulate extreme slowness (offline initially)
  await page.context().setOffline(true);
  
  await page.goto('/login', { waitUntil: 'commit' });
  
  // Wait 11 seconds
  await page.waitForTimeout(11000);
  
  // Verify timeout error is shown
  await expect(page.locator('text=/took too long to initialize/')).toBeVisible();
  
  // Verify refresh button is present
  await expect(page.locator('button', { hasText: 'Refresh Page' })).toBeVisible();
});
```

**Acceptance Criteria:** AC-4 (Clear error messages)  
**Priority:** P1 (High)

---

#### Test 2.3.2: Offline detection

```typescript
test('should show error when completely offline', async ({ page }) => {
  await page.context().setOffline(true);
  
  await page.goto('/login', { waitUntil: 'commit' });
  
  // Should show error within 10s
  await expect(page.locator('text=/took too long to initialize/')).toBeVisible({ timeout: 11000 });
});
```

**Acceptance Criteria:** AC-4 (Error handling)  
**Priority:** P2 (Medium)

---

### 2.4 Authentication State Tests

#### Test 2.4.1: Already signed in redirects correctly (user role)

```typescript
test('should redirect to homepage if user already signed in as regular user', async ({ page }) => {
  // Mock Clerk auth state (user role)
  await page.addInitScript(() => {
    window.localStorage.setItem('clerk-mock-user', JSON.stringify({
      role: 'user',
      email: 'user@example.com'
    }));
  });
  
  await page.goto('/login');
  
  // Should redirect to homepage
  await expect(page).toHaveURL('/');
});
```

**Acceptance Criteria:** AC-3 (Role-based redirects)  
**Priority:** P0 (Critical)

---

#### Test 2.4.2: Already signed in redirects correctly (agent role)

```typescript
test('should redirect to dashboard if signed in as agent', async ({ page }) => {
  // Mock Clerk auth state (agent role)
  await page.addInitScript(() => {
    window.localStorage.setItem('clerk-mock-user', JSON.stringify({
      role: 'agent',
      email: 'agent@example.com'
    }));
  });
  
  await page.goto('/login');
  
  // Should redirect to dashboard
  await expect(page).toHaveURL('/dashboard');
});
```

**Acceptance Criteria:** AC-3 (Role-based redirects)  
**Priority:** P0 (Critical)

---

#### Test 2.4.3: Already signed in redirects correctly (admin role)

```typescript
test('should redirect to dashboard if signed in as admin', async ({ page }) => {
  // Mock Clerk auth state (admin role)
  await page.addInitScript(() => {
    window.localStorage.setItem('clerk-mock-user', JSON.stringify({
      role: 'admin',
      email: 'admin@example.com'
    }));
  });
  
  await page.goto('/login');
  
  // Should redirect to dashboard
  await expect(page).toHaveURL('/dashboard');
});
```

**Acceptance Criteria:** AC-3 (Role-based redirects)  
**Priority:** P0 (Critical)

---

### 2.5 Navigation Tests

#### Test 2.5.1: Back button during loading

```typescript
test('back button during loading should not cause errors', async ({ page }) => {
  // Navigate to home first
  await page.goto('/');
  
  // Navigate to login
  await page.goto('/login');
  
  // Immediately go back (before form mounts)
  await page.goBack();
  
  // Should be on homepage, no errors
  await expect(page).toHaveURL('/');
  
  // Check console for errors
  const errors = await page.evaluate(() => {
    return (window as any).__consoleErrors || [];
  });
  expect(errors).toHaveLength(0);
});
```

**Acceptance Criteria:** AC-2 (Robust mounting)  
**Priority:** P2 (Medium)

---

#### Test 2.5.2: Multiple rapid navigations

```typescript
test('multiple rapid navigations should not cause race conditions', async ({ page }) => {
  // Navigate to login multiple times rapidly
  for (let i = 0; i < 5; i++) {
    await page.goto('/');
    await page.goto('/login');
  }
  
  // Final navigation should work correctly
  await page.goto('/login');
  await expect(page.locator('[data-testid="clerk-signin-container"]')).toBeVisible({ timeout: 5000 });
});
```

**Acceptance Criteria:** AC-2 (No race conditions)  
**Priority:** P2 (Medium)

---

## 3. Performance Tests

### 3.1 Load Time Benchmarks

**Tool:** Playwright with performance API

```typescript
test('measure login page load time on normal network', async ({ page }) => {
  await page.goto('/login');
  
  const performanceTiming = await page.evaluate(() => {
    return {
      navigationStart: performance.timing.navigationStart,
      domContentLoaded: performance.timing.domContentLoadedEventEnd,
      loadComplete: performance.timing.loadEventEnd,
    };
  });
  
  const loadTime = performanceTiming.loadComplete - performanceTiming.navigationStart;
  
  // Assert load time < 2s (AC-1)
  expect(loadTime).toBeLessThan(2000);
  
  console.log(`Login page load time: ${loadTime}ms`);
});
```

**Acceptance Criteria:** AC-1 (< 2s load time)  
**Priority:** P0 (Critical)

---

### 3.2 Clerk SDK Initialization Time

```typescript
test('measure clerk.load() time', async ({ page }) => {
  await page.goto('/login');
  
  const clerkLoadTime = await page.evaluate(() => {
    return (window as any).__clerkLoadTime || 0;
  });
  
  // Log for analysis
  console.log(`Clerk SDK load time: ${clerkLoadTime}ms`);
  
  // Should be reasonable (< 5s on normal network)
  expect(clerkLoadTime).toBeLessThan(5000);
});
```

**Priority:** P1 (High)

---

## 4. Browser Compatibility Tests

### 4.1 Target Browsers

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Chrome Mobile (Android)
- Safari Mobile (iOS)

### 4.2 Test Matrix

Run all E2E tests on each browser:

```typescript
test.describe('Browser Compatibility', () => {
  const browsers = ['chromium', 'firefox', 'webkit'];
  
  for (const browserType of browsers) {
    test(`login form works on ${browserType}`, async () => {
      const browser = await chromium.launch(); // Replace with browserType
      const page = await browser.newPage();
      
      await page.goto('/login');
      await expect(page.locator('[data-testid="clerk-signin-container"]')).toBeVisible();
      
      await browser.close();
    });
  }
});
```

**Priority:** P1 (High)  
**Estimated Time:** 3 hours

---

## 5. Manual Testing Checklist

### 5.1 Network Conditions

Test on each network condition using Chrome DevTools:

- [ ] **Fast 3G** (1.6 Mbps, 150ms latency)
  - Form appears < 2s
  - No errors in console
  - Form is functional

- [ ] **Slow 3G** (400 Kbps, 400ms latency)
  - Progress message appears after 3s
  - Form eventually appears
  - No timeout errors before 10s

- [ ] **Offline**
  - Timeout error appears after 10s
  - Error message is clear
  - Refresh button works

---

### 5.2 User Flows

- [ ] **First-time visitor (no cache)**
  - Navigate to /login from Google
  - Form appears reliably
  - No blank screen

- [ ] **Returning visitor (cache)**
  - Navigate to /login
  - Faster load time (cached assets)
  - Form works correctly

- [ ] **Bookmarked login page**
  - Open /login directly (not from home)
  - Layout and page initialize correctly
  - Form appears (no race condition)

- [ ] **Signed-in user navigates to /login**
  - Redirected to appropriate page (based on role)
  - No form shown
  - Smooth redirect

---

### 5.3 Navigation Scenarios

- [ ] **Back button during loading**
  - Navigate to /login
  - Click back before form appears
  - No errors, clean navigation

- [ ] **Forward button after back**
  - Go back from /login
  - Click forward
  - Form reappears correctly

- [ ] **Refresh page during loading**
  - Navigate to /login
  - Refresh immediately
  - Form eventually appears

- [ ] **Close tab during loading**
  - Navigate to /login
  - Close tab before form loads
  - No hanging requests (check DevTools Network)

---

### 5.4 Error Scenarios

- [ ] **Clerk SDK unavailable**
  - Block Clerk CDN in DevTools
  - Navigate to /login
  - Error message shown
  - Refresh button works

- [ ] **Backend unavailable (signed-in user)**
  - Sign in successfully
  - Stop backend server
  - Navigate to /login
  - ErrorBoundary shown with retry option

- [ ] **Slow backend response**
  - Throttle backend API
  - Navigate to /login as signed-in user
  - Wait for redirect or error
  - User sees feedback

---

### 5.5 Visual Regression

- [ ] **Loading spinner appearance**
  - Centered correctly
  - Smooth animation
  - Appropriate size

- [ ] **Progress message styling**
  - Appears after 3s
  - Clear, readable text
  - Not overlapping spinner

- [ ] **Error message styling**
  - Red background for errors
  - Clear text
  - Refresh button styled correctly

- [ ] **Clerk form styling**
  - Matches site design
  - Responsive on mobile
  - No layout shifts

---

### 5.6 Mobile Device Testing

- [ ] **iPhone (Safari iOS)**
  - Form appears
  - Touch interactions work
  - No mobile-specific errors

- [ ] **Android (Chrome Mobile)**
  - Form appears
  - Touch interactions work
  - No mobile-specific errors

- [ ] **Tablet (iPad)**
  - Form appears
  - Layout is appropriate
  - No errors

---

## 6. Acceptance Criteria Mapping

### AC-1: Login form loads in < 2 seconds (normal network)

**Tests:**
- Test 2.1.1: Login form loads successfully on fast connection
- Test 3.1: Load time benchmarks

**How to Verify:**
1. Run Playwright test with performance measurement
2. Assert load time < 2000ms
3. Manually test with DevTools Performance tab

---

### AC-2: Component mounts 100% of the time (no race condition)

**Tests:**
- Test 2.1.2: No race condition errors in console
- Test 2.2.1: Form appears on slow 3G network
- Test 2.5.2: Multiple rapid navigations

**How to Verify:**
1. Run E2E tests 100 times (stress test)
2. Mount success rate should be 100%
3. No race condition errors in logs

---

### AC-3: Role-based redirects work correctly

**Tests:**
- Test 2.4.1: User role redirect
- Test 2.4.2: Agent role redirect
- Test 2.4.3: Admin role redirect

**How to Verify:**
1. Sign in as each role
2. Navigate to /login
3. Verify redirect to correct page

---

### AC-4: Error handling displays user-friendly messages

**Tests:**
- Test 2.3.1: Timeout error after 10 seconds
- Test 2.3.2: Offline detection
- Manual testing: Error scenarios

**How to Verify:**
1. Trigger each error condition
2. Verify error message is clear
3. Verify actionable button is present

---

## 7. Test Execution Plan

### Phase 1: Unit Tests (Day 1, AM)

- Write unit tests for waitForClerkReady()
- Run with vitest
- Achieve 100% coverage for new function
- Fix any issues found

---

### Phase 2: E2E Tests (Day 1, PM)

- Write Playwright tests for normal network
- Write Playwright tests for slow network
- Write Playwright tests for authentication state
- Run locally, verify all pass

---

### Phase 3: Manual Testing (Day 2, AM)

- Test on Chrome with various network conditions
- Test on Firefox
- Test on Safari
- Complete manual checklist

---

### Phase 4: Browser Compatibility (Day 2, PM)

- Run E2E test suite on all target browsers
- Fix any browser-specific issues
- Verify consistent behavior

---

### Phase 5: Performance Validation (Day 3, AM)

- Run performance benchmarks
- Measure load times in various conditions
- Compare with baseline (before fix)
- Document improvements

---

### Phase 6: Staging Deployment (Day 3, PM)

- Deploy to staging environment
- Run full test suite against staging
- Monitor for 24-48 hours
- Collect metrics

---

### Phase 7: Production Deployment (Day 4+)

- Deploy during low-traffic window
- Monitor error rates
- Run smoke tests
- Track login success rate

---

## 8. Success Metrics

### Quantitative Metrics

| Metric | Before Fix | Target After Fix | How to Measure |
|--------|-----------|------------------|----------------|
| Login form mount success rate | ~95% | 100% | E2E test stress run (100 iterations) |
| Average load time (normal) | 1.5s | < 2s | Performance API |
| Average load time (slow 3G) | Timeout at 5s | 3-6s | Throttled E2E tests |
| Blank form error rate | 5% | 0% | Error monitoring |
| Support tickets (login issues) | 10/week | < 2/week | Support system |

---

### Qualitative Metrics

- [ ] No user reports of blank login form
- [ ] Users understand progress messages
- [ ] Error messages are actionable
- [ ] Overall login UX improved

---

## 9. Bug Reporting Template

If issues are found during testing:

```markdown
**Bug Title:** [Concise description]

**Severity:** Critical / High / Medium / Low

**Test Case:** [Which test revealed the bug]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happened]

**Environment:**
- Browser: [Chrome 120, etc.]
- Network: [Fast 3G, Slow 3G, etc.]
- Device: [Desktop, iPhone 14, etc.]

**Screenshots/Videos:**
[Attach if applicable]

**Console Errors:**
```
[Paste console errors]
```

**Additional Context:**
[Any other relevant information]
```

---

## 10. Test Automation

### CI/CD Integration

Add to CI pipeline:

```yaml
# .github/workflows/test.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

**Priority:** P1 (High)  
**Estimated Time:** 1 hour

---

**Test Plan Complete ✅**

Ready for execution by QA team and implementation agents.

---

**End of Document**
