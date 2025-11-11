# Implementation Specification - Clerk Mounting Race Condition Fix

**Date:** 2025-11-06  
**Phase:** PLANNING  
**Task:** TASK-001 (US-001: Login Flow Validation)  
**For:** Implementation Subagents (dev-frontend-svelte)

---

## Overview

This document provides detailed, line-by-line implementation specifications for fixing the Clerk authentication race condition. Implementation agents should follow these specifications exactly to ensure the solution works as designed.

**Primary File:** `apps/frontend/src/routes/login/+page.svelte`  
**Changes:** Refactor onMount, remove $effect, add progress UI  
**Estimated LOC:** -30 removed, +80 added (net: +50 lines, more robust)

**Key Updates from Initial Plan:**
- Added retry logic with exponential backoff (4 attempts)
- Added error type differentiation (offline, timeout, blocked, etc.)
- Added offline detection with navigator.onLine
- Enhanced progress UI showing retry attempts

---

## File: apps/frontend/src/routes/login/+page.svelte

**Location:** `/Users/solo/Projects/_repos/bestays/apps/frontend/src/routes/login/+page.svelte`

### Change 1: Update State Variables (Lines 38-42)

**CURRENT:**
```typescript
let signInDiv = $state<HTMLDivElement | null>(null);
let isLoading = $state(true);
let error = $state<string | null>(null);
let mounted = $state(false);  // ← REMOVE THIS LINE
let errorMessage = $state<string | null>(null);
```

**NEW:**
```typescript
let signInDiv = $state<HTMLDivElement | null>(null);
let isLoading = $state(true);
let error = $state<string | null>(null);
let errorMessage = $state<string | null>(null);
let loadingTime = $state(0); // ← ADD: Track elapsed seconds for progress UI
let attemptNumber = $state(0); // ← ADD: Current retry attempt (1-4)
let retryDelay = $state(0); // ← ADD: Seconds until next retry
```

**Rationale:**
- `mounted` flag is unnecessary (onMount already tells us component is mounted)
- `loadingTime` enables progress UI feedback for slow networks
- `attemptNumber` shows user which retry attempt is running
- `retryDelay` shows countdown timer between retries

---

### Change 2: Add Derived State (After Line 42)

**ADD NEW CODE:**
```typescript
// Derived states for progressive UI feedback
let showProgressMessage = $derived(loadingTime > 3 && attemptNumber === 0);
let showRetryInfo = $derived(attemptNumber > 1);
```

**Rationale:**
- `showProgressMessage` shows after 3s on first attempt only
- `showRetryInfo` shows when retrying (attempt 2+)
- Uses Svelte 5 $derived rune (correct pattern)
- Progressive disclosure: simple message first, more detail on retry

---

### Change 3: Add Helper Functions (Before onMount)

**INSERT BEFORE LINE 50:**

#### 3a. Error Type Definitions

```typescript
/**
 * Network error types for differentiated handling.
 *
 * Pattern: Error Classification
 * Purpose: Provide user-friendly, context-specific error messages
 *
 * Reference: .claude/skills/frontend-network-resilience/SKILL.md
 */
type NetworkErrorType =
  | 'offline'           // No internet connection (navigator.onLine = false)
  | 'timeout'           // All retry attempts exhausted
  | 'sdk_not_available' // Clerk script didn't load (blocked or CDN down)
  | 'mount_failed'      // SDK ready but mounting failed
  | 'server_error';     // Backend API failure (after auth)

interface NetworkError {
  type: NetworkErrorType;
  message: string;
  canRetry: boolean;
}

/**
 * Structured log entry for error tracking.
 *
 * Pattern: Structured Logging
 * Purpose: Capture full context for debugging without exposing to user
 *
 * Security: Never shown to user, only logged internally
 */
interface ErrorLogEntry {
  timestamp: string;           // ISO 8601 timestamp
  errorType: NetworkErrorType;  // Classified error type
  attemptNumber: number;        // Which retry attempt failed (1-4)
  totalAttempts: number;        // Total attempts configured
  elapsedTime: number;          // Time spent in ms
  networkOnline: boolean;       // navigator.onLine at time of error
  clerkAvailable: boolean;      // Was clerk SDK loaded?
  clerkLoaded: boolean;         // Was clerk.loaded true?
  userAgent: string;            // Browser info
  url: string;                  // Current page URL
  context: string;              // Additional context
}
```

#### 3b. Structured Logging Function

```typescript
/**
 * Log structured error for debugging and analytics.
 *
 * Pattern: Structured Logging
 * Purpose: Capture full context without exposing to user
 *
 * Security Model:
 * - Logs contain technical details (safe for internal use)
 * - User sees only friendly message from classifyNetworkError()
 * - Logs sent to console in dev, can be sent to Sentry/LogRocket in prod
 *
 * Future Integration:
 * - Replace console.error with Sentry.captureException()
 * - Add custom context to error tracking service
 * - Track metrics (retry success rate, most common errors)
 *
 * @param entry - Structured error log entry
 */
function logStructuredError(entry: ErrorLogEntry): void {
  // Console logging (always, for development)
  console.error('[Clerk Login Error]', {
    ...entry,
    // Add readable summary
    summary: `${entry.errorType} on attempt ${entry.attemptNumber}/${entry.totalAttempts} after ${entry.elapsedTime}ms`,
  });

  // TODO: Future Sentry integration
  // if (import.meta.env.PROD) {
  //   Sentry.captureException(new Error(entry.errorType), {
  //     level: 'error',
  //     tags: {
  //       errorType: entry.errorType,
  //       attemptNumber: entry.attemptNumber,
  //     },
  //     extra: entry,
  //   });
  // }

  // TODO: Future analytics integration
  // trackEvent('clerk_login_error', {
  //   error_type: entry.errorType,
  //   attempt_number: entry.attemptNumber,
  //   elapsed_time: entry.elapsedTime,
  // });
}
```

#### 3c. Error Classification Function

```typescript
/**
 * Classify network errors for user-friendly messaging.
 *
 * Pattern: Error Differentiation
 * Flow: Detect error type → Return appropriate message
 *
 * Security: Returns ONLY user-friendly message (no technical details)
 *
 * @param errorType - The type of network error
 * @returns NetworkError object with message and retry flag
 */
function classifyNetworkError(errorType: NetworkErrorType): NetworkError {
  switch (errorType) {
    case 'offline':
      return {
        type: 'offline',
        message: 'No internet connection. Please check your network and try again.',
        canRetry: true
      };

    case 'sdk_not_available':
      return {
        type: 'sdk_not_available',
        message: 'Authentication system blocked. Please disable ad blockers and refresh.',
        canRetry: true
      };

    case 'timeout':
      return {
        type: 'timeout',
        message: 'Connection is very slow. Please check your internet or try again later.',
        canRetry: true
      };

    case 'mount_failed':
      return {
        type: 'mount_failed',
        message: 'Login form failed to load. Please refresh the page.',
        canRetry: true
      };

    case 'server_error':
      return {
        type: 'server_error',
        message: 'Server error. Please try again.',
        canRetry: true
      };
  }
}
```

#### 3d. Clerk Ready Polling Function

```typescript
/**
 * Wait for Clerk SDK to be fully loaded (single attempt).
 *
 * Pattern: Polling with Timeout
 * Flow: Check clerk.loaded every 100ms, timeout after maxWaitMs
 *
 * This function trusts that +layout.svelte has initialized Clerk.
 * We just wait for the initialization to complete rather than
 * calling clerk.load() again (which could cause double-load).
 *
 * @param maxWaitMs - Maximum time to wait per attempt (default 5000ms)
 * @returns Promise<boolean> - true if ready, false if timeout
 */
async function waitForClerkReady(maxWaitMs = 5000): Promise<boolean> {
  const startTime = Date.now();

  // Poll clerk.loaded every 100ms
  while (!clerk?.loaded) {
    // Check if timeout reached
    if (Date.now() - startTime > maxWaitMs) {
      return false; // Timeout - caller should retry or fail
    }

    // Wait 100ms before next check
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  return true; // Ready!
}
```

#### 3e. Retry with Exponential Backoff Function

```typescript
/**
 * Load Clerk SDK with retry logic and exponential backoff.
 *
 * Pattern: Exponential Backoff Retry
 * Flow: Try → Wait → Retry → Wait longer → Retry → Fail
 *
 * Retry Strategy:
 * - Attempt 1: 0s wait + 5s timeout
 * - Attempt 2: 2s wait + 5s timeout
 * - Attempt 3: 4s wait + 5s timeout
 * - Attempt 4: 8s wait + 5s timeout
 * Total time: ~24 seconds maximum
 *
 * Reference: .claude/skills/frontend-network-resilience/SKILL.md
 * Industry standard: AWS SDK, Google Cloud, Stripe API
 *
 * @param maxAttempts - Number of attempts (default 4)
 * @param attemptTimeout - Timeout per attempt in ms (default 5000)
 * @returns Promise<{ success: boolean; error?: NetworkErrorType }>
 */
async function loadClerkWithRetry(
  maxAttempts = 4,
  attemptTimeout = 5000
): Promise<{ success: boolean; error?: NetworkErrorType }> {
  const overallStartTime = Date.now();

  // Check if offline first (fast fail)
  if (!navigator.onLine) {
    logStructuredError({
      timestamp: new Date().toISOString(),
      errorType: 'offline',
      attemptNumber: 0,
      totalAttempts: maxAttempts,
      elapsedTime: 0,
      networkOnline: false,
      clerkAvailable: !!clerk,
      clerkLoaded: clerk?.loaded || false,
      userAgent: navigator.userAgent,
      url: window.location.href,
      context: 'Fast fail: offline detected before first attempt'
    });
    return { success: false, error: 'offline' };
  }

  // Check if Clerk SDK is available
  if (!clerk) {
    logStructuredError({
      timestamp: new Date().toISOString(),
      errorType: 'sdk_not_available',
      attemptNumber: 0,
      totalAttempts: maxAttempts,
      elapsedTime: 0,
      networkOnline: navigator.onLine,
      clerkAvailable: false,
      clerkLoaded: false,
      userAgent: navigator.userAgent,
      url: window.location.href,
      context: 'Clerk SDK not loaded (blocked by extension or CDN failure)'
    });
    return { success: false, error: 'sdk_not_available' };
  }

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    // Update UI: show current attempt
    attemptNumber = attempt;

    // Reset loadingTime for this attempt
    loadingTime = 0;
    const attemptStartTime = Date.now();

    // Update loadingTime every second during this attempt
    const updateInterval = setInterval(() => {
      loadingTime = Math.floor((Date.now() - attemptStartTime) / 1000);
    }, 1000);

    // Try to load Clerk (5s timeout per attempt)
    const success = await waitForClerkReady(attemptTimeout);

    // Clear the interval
    clearInterval(updateInterval);
    const attemptElapsed = Date.now() - attemptStartTime;

    if (success) {
      // Success! Log for analytics
      console.log('[Clerk Login Success]', {
        timestamp: new Date().toISOString(),
        attemptNumber: attempt,
        totalAttempts: maxAttempts,
        elapsedTime: attemptElapsed,
        totalElapsedTime: Date.now() - overallStartTime,
        succeededOnRetry: attempt > 1,
      });

      // Reset UI state
      attemptNumber = 0;
      retryDelay = 0;
      return { success: true };
    }

    // Attempt failed - log it
    logStructuredError({
      timestamp: new Date().toISOString(),
      errorType: 'timeout',
      attemptNumber: attempt,
      totalAttempts: maxAttempts,
      elapsedTime: attemptElapsed,
      networkOnline: navigator.onLine,
      clerkAvailable: !!clerk,
      clerkLoaded: clerk?.loaded || false,
      userAgent: navigator.userAgent,
      url: window.location.href,
      context: attempt === maxAttempts
        ? 'Final attempt failed - giving up'
        : `Attempt ${attempt} failed - will retry`
    });

    // Last attempt failed - give up
    if (attempt === maxAttempts) {
      return { success: false, error: 'timeout' };
    }

    // Calculate exponential backoff delay: 2s, 4s, 8s
    const delay = 2000 * Math.pow(2, attempt - 1);

    // Show user the countdown
    retryDelay = Math.floor(delay / 1000);

    // Wait with countdown timer
    const countdownStart = Date.now();
    const countdownInterval = setInterval(() => {
      const elapsed = Date.now() - countdownStart;
      retryDelay = Math.max(0, Math.floor((delay - elapsed) / 1000));
    }, 100);

    await new Promise(resolve => setTimeout(resolve, delay));

    clearInterval(countdownInterval);
    retryDelay = 0;
  }

  // Should never reach here, but TypeScript needs it
  return { success: false, error: 'timeout' };
}
```

**Rationale:**

1. **Error Type Differentiation:**
   - Clear distinction between offline, blocked, timeout, etc.
   - Tailored error messages for each type
   - User knows exactly what went wrong and what to do

2. **Offline Detection:**
   - Fast fail if no internet connection
   - Saves user from waiting through all retries
   - Clear, actionable message

3. **Exponential Backoff:**
   - Industry standard pattern (AWS, Google Cloud, Stripe)
   - 4 attempts with increasing delays (0s, 2s, 4s, 8s)
   - Total ~24s maximum wait time
   - Handles transient network issues automatically

4. **Progress Feedback:**
   - Shows attempt number (1/4, 2/4, etc.)
   - Shows countdown between retries
   - Updates loading time during each attempt
   - User knows system is working, not frozen

5. **Reduced Per-Attempt Timeout:**
   - Changed from 10s single attempt to 5s per attempt
   - 4 × 5s = 20s total checking time
   - Faster failure detection
   - Better user experience on slow networks

**Svelte 5 Pattern:** All imperative logic (correct), state updates trigger reactive UI.

**Error Handling:** Returns result object, caller decides what to show user.

---

### Change 4: Replace onMount Logic (Lines 50-98)

**CURRENT (REMOVE ENTIRELY):**
```typescript
onMount(async () => {
  try {
    // Wait for clerk to be available (browser-only)
    if (!clerk) {
      error = 'Clerk is not available. Please refresh the page.';
      isLoading = false;
      return;
    }

    // Ensure Clerk is loaded before mounting (with timeout)
    if (!clerk.loaded) {
      const loadTimeout = setTimeout(() => {
        console.warn('Clerk load timeout - proceeding anyway');
        isLoading = false;
        mounted = true;
      }, 5000);

      try {
        await clerk.load();
        clearTimeout(loadTimeout);
      } catch (loadError) {
        clearTimeout(loadTimeout);
        console.error('Clerk load error:', loadError);
        // Continue anyway - might still work
      }
    }

    // Check if already signed in
    if (clerk.user) {
      console.log('Already signed in, redirecting...');
      try {
        await redirectAfterAuth();
        return;
      } catch (err: any) {
        // Show error instead of silent redirect
        errorMessage = err.message;
        isLoading = false;
        return;
      }
    }

    isLoading = false;
    mounted = true;
  } catch (err) {
    error = 'Failed to load authentication. Please refresh the page.';
    isLoading = false;
    console.error('Clerk initialization error:', err);
  }
});
```

**NEW (REPLACE WITH):**
```typescript
/**
 * Mount Clerk sign-in component on page load with retry logic.
 *
 * Pattern: Imperative onMount + Exponential Backoff Retry
 * Flow: Retry load with backoff → Check auth → Mount UI directly
 *
 * Key Changes from Previous Implementation:
 * - No timeout workaround (eliminated race condition)
 * - No mounted flag (unnecessary complexity)
 * - No duplicate clerk.load() call (trust layout initialization)
 * - Direct imperative mounting (not reactive via $effect)
 * - Retry logic with exponential backoff (industry standard)
 * - Error type differentiation (offline, timeout, blocked, etc.)
 * - Offline detection (fast fail if no connection)
 * - Progress UI showing retry attempts and countdowns
 */
onMount(async () => {
  try {
    // CHECKPOINT 1: Load Clerk SDK with retry logic
    // This handles offline detection, retry with exponential backoff,
    // and differentiated error types
    const result = await loadClerkWithRetry(4, 5000); // 4 attempts, 5s each

    if (!result.success) {
      // All retry attempts failed - show appropriate error
      const networkError = classifyNetworkError(result.error!);
      error = networkError.message;
      isLoading = false;
      return;
    }

    // CHECKPOINT 2: Check if user is already signed in
    if (clerk.user) {
      // User is authenticated, redirect to appropriate page based on role
      try {
        await redirectAfterAuth();
        return; // Navigation happened, component will unmount
      } catch (err: any) {
        // Backend failure or redirect error
        errorMessage = err.message;
        isLoading = false;
        return;
      }
    }

    // CHECKPOINT 3: Mount Clerk UI directly (imperative, not reactive)
    isLoading = false; // Stop showing spinner
    await tick(); // Ensure DOM is fully ready

    // Verify signInDiv is bound
    if (!signInDiv) {
      logStructuredError({
        timestamp: new Date().toISOString(),
        errorType: 'mount_failed',
        attemptNumber: 0,
        totalAttempts: 1,
        elapsedTime: 0,
        networkOnline: navigator.onLine,
        clerkAvailable: !!clerk,
        clerkLoaded: clerk?.loaded || false,
        userAgent: navigator.userAgent,
        url: window.location.href,
        context: 'signInDiv ref not bound to DOM element'
      });

      const mountError = classifyNetworkError('mount_failed');
      error = mountError.message;
      return;
    }

    // DIRECT IMPERATIVE MOUNT - This is the key change
    // No $effect, no reactive dependencies, runs once
    try {
      clerk.mountSignIn(signInDiv, {
        signUpUrl: '/signup',
        // Note: No fallbackRedirectUrl - we handle redirects manually
        // based on user role via redirectAfterAuth()
      });

      // Log successful mount
      console.log('[Clerk Login Mount Success]', {
        timestamp: new Date().toISOString(),
        context: 'Sign-in component mounted successfully'
      });

    } catch (mountErr) {
      // Mounting failed - log structured error
      logStructuredError({
        timestamp: new Date().toISOString(),
        errorType: 'mount_failed',
        attemptNumber: 0,
        totalAttempts: 1,
        elapsedTime: 0,
        networkOnline: navigator.onLine,
        clerkAvailable: !!clerk,
        clerkLoaded: clerk?.loaded || false,
        userAgent: navigator.userAgent,
        url: window.location.href,
        context: `Clerk mountSignIn() threw exception: ${mountErr}`
      });

      // Show user-friendly error
      const mountError = classifyNetworkError('mount_failed');
      error = mountError.message;
    }

  } catch (err) {
    // Catch any unexpected errors
    logStructuredError({
      timestamp: new Date().toISOString(),
      errorType: 'server_error',
      attemptNumber: 0,
      totalAttempts: 1,
      elapsedTime: 0,
      networkOnline: navigator.onLine,
      clerkAvailable: !!clerk,
      clerkLoaded: clerk?.loaded || false,
      userAgent: navigator.userAgent,
      url: window.location.href,
      context: `Unexpected error in onMount: ${err}`
    });

    // Show user-friendly error
    const genericError = classifyNetworkError('server_error');
    error = genericError.message;
    isLoading = false;
  }

  // Cleanup function - runs only when component unmounts
  return () => {
    if (signInDiv) {
      clerk.unmountSignIn(signInDiv);
    }
  };
});
```

**Rationale:**

1. **Retry with Exponential Backoff:**
   - 4 attempts with 2s, 4s, 8s delays between attempts
   - Handles transient network failures automatically
   - Industry standard pattern (AWS, Google Cloud, Stripe)
   - Total ~24s maximum wait time
   - Auto-recovery reduces user frustration

2. **Error Type Differentiation:**
   - Offline: "No internet connection. Please check your network."
   - Blocked: "Authentication system blocked. Please disable ad blockers."
   - Timeout: "Connection is very slow. Please check your internet."
   - Mount failed: "Login form failed to load. Please refresh."
   - Server error: "Server error. Please try again."
   - Each message is user-friendly and actionable

3. **Offline Detection:**
   - Fast fail with `navigator.onLine` check
   - Saves user from waiting through all retry attempts
   - Clear message about network being offline

4. **Progress UI:**
   - Shows attempt number (1/4, 2/4, 3/4, 4/4)
   - Shows countdown between retries
   - Updates loading time during each attempt
   - User knows system is working, not frozen

5. **No Timeout Workaround:**
   - Removed dangerous `setTimeout` that caused race condition
   - Proper async waiting with retry logic
   - No silent failures

6. **No Mounted Flag:**
   - Removed unnecessary state variable
   - onMount already guarantees component is mounted
   - Simplifies logic, reduces complexity

7. **No Duplicate Load:**
   - Removed `await clerk.load()` call
   - Trust layout to initialize Clerk
   - Just wait for `clerk.loaded` to become true with retry

8. **Direct Imperative Mounting:**
   - `clerk.mountSignIn()` called directly in onMount
   - Not triggered by reactive $effect
   - Runs once, predictably
   - Try-catch around mounting to handle SDK errors

9. **Cleanup Function:**
   - Returns cleanup from onMount (runs on unmount only)
   - Unmounts Clerk UI properly
   - Prevents memory leaks

**Svelte 5 Patterns Used:**
- `onMount` for one-time initialization ✅ (correct pattern)
- `await tick()` to ensure DOM ready ✅
- Cleanup function returned from onMount ✅
- NOT using `$effect` for SDK mounting ✅ (anti-pattern avoided)

**Network Resilience Patterns Used:**
- Exponential backoff retry ✅
- Error type differentiation ✅
- Offline detection ✅
- Progress feedback ✅
- User-friendly error messages ✅

---

### Change 5: Remove $effect Block (Lines 134-162)

**CURRENT (REMOVE ENTIRELY):**
```typescript
/**
 * Mount Clerk UI when div is ready.
 * 
 * Pattern: Reactive Effect (Svelte 5)
 * Flow: Watch for div availability → Mount Clerk component
 */
$effect(() => {
  if (signInDiv && mounted && clerk && !isLoading && !error) {
    try {
      const result = clerk.mountSignIn(signInDiv, {
        // Don't use fallbackRedirectUrl - we'll handle redirect manually
        // based on user role after auth
        signUpUrl: '/signup',
      });

      // Handle promise if mountSignIn returns one
      if (result && typeof result.catch === 'function') {
        result.catch((err: Error) => {
          error = 'Failed to load sign-in form. Please refresh the page.';
          console.error('Clerk mount error:', err);
        });
      }
    } catch (err) {
      error = 'Failed to load sign-in form. Please refresh the page.';
      console.error('Clerk mount error:', err);
    }

    // Cleanup function
    return () => {
      if (signInDiv) {
        clerk.unmountSignIn(signInDiv);
      }
    };
  }
});
```

**NEW:**
```typescript
// ❌ REMOVED - Mounting now happens directly in onMount (imperative pattern)
// No reactive effect needed for one-time SDK initialization
```

**Rationale:**
- $effect is for reactive side effects, not one-time operations
- Mounting Clerk UI is non-idempotent (can't run multiple times safely)
- 5 reactive dependencies caused unpredictable re-triggers
- Imperative onMount is simpler and more appropriate

**This is the CORE fix for the race condition.**

---

### Change 6: Update Loading UI Template (Lines 181-188)

**CURRENT:**
```svelte
{#if isLoading}
  <!-- Loading State -->
  <div class="bg-white rounded-xl shadow-lg p-8 flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p class="text-gray-600">Loading authentication...</p>
    </div>
  </div>
{/if}
```

**NEW:**
```svelte
{#if isLoading}
  <!-- Loading State with Progress Feedback and Retry Information -->
  <div class="bg-white rounded-xl shadow-lg p-8 flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p class="text-gray-600">Loading authentication...</p>

      <!-- Show retry attempt number -->
      {#if showRetryInfo}
        <p class="text-sm font-medium text-blue-600 mt-3">
          Attempt {attemptNumber}/4
        </p>
      {/if}

      <!-- Show progress message after 3 seconds (first attempt only) -->
      {#if showProgressMessage}
        <p class="text-sm text-gray-500 mt-2">
          This is taking longer than expected ({loadingTime}s)...
        </p>
        <p class="text-xs text-gray-400 mt-1">
          Please check your internet connection
        </p>
      {/if}

      <!-- Show countdown between retries -->
      {#if retryDelay > 0}
        <p class="text-sm text-orange-600 mt-3">
          Retrying in {retryDelay}s...
        </p>
        <p class="text-xs text-gray-400 mt-1">
          Connection appears slow, retrying automatically
        </p>
      {/if}
    </div>
  </div>
{/if}
```

**Rationale:**
- **Retry Attempt Counter:** Shows "Attempt 2/4" so user knows system is retrying
- **First Attempt Feedback:** Shows "taking longer than expected" after 3s (attempt 1 only)
- **Countdown Timer:** Shows "Retrying in 4s..." between attempts
- **Progressive Disclosure:** Simple message first, more detail as time passes
- **Reassurance:** User knows system is working, not frozen
- **Color Coding:** Blue for attempts, orange for countdown (visual distinction)

**Svelte 5 Pattern:** Uses `showRetryInfo`, `showProgressMessage` derived states (reactive, correct).

**UX Benefits:**
- User sees exactly what's happening at each stage
- No mysterious silent delays
- Countdown creates expectation of progress
- Reduces user frustration and page refreshes

---

## Edge Cases to Handle

### 1. User Closes Tab During Load

**Behavior:** Component unmounts, cleanup function runs  
**Handling:** Automatic via onMount cleanup return  
**Test:** Manual - close tab during slow load  
**Expected:** No console errors, clean unmount

### 2. User Navigates Away Before Mount Completes

**Behavior:** Component unmounts mid-initialization  
**Handling:** Automatic - async operations continue but state updates are safe  
**Test:** Click back button immediately after navigation  
**Expected:** No errors, clean unmount

### 3. Clerk SDK Throws Error During mountSignIn()

**Behavior:** Exception thrown  
**Handling:** Currently no try-catch around mountSignIn() itself  
**Recommendation:** ADD try-catch:

```typescript
try {
  clerk.mountSignIn(signInDiv, { signUpUrl: '/signup' });
} catch (mountErr) {
  error = 'Failed to display login form. Please refresh the page.';
  console.error('Clerk mount error:', mountErr);
}
```

### 4. signInDiv Becomes null After tick()

**Behavior:** Very unlikely (DOM shouldn't unbind that fast)  
**Handling:** Already checked with `if (!signInDiv)` guard  
**Test:** Add artificial delay, try to trigger  
**Expected:** Error message shown

### 5. Network Goes Offline During waitForClerkReady()

**Behavior:** clerk.loaded never becomes true  
**Handling:** Timeout after 10s, show error message  
**Test:** Disable network after page starts loading  
**Expected:** Error after 10s, actionable message

### 6. Multiple Rapid Navigations

**Behavior:** Component mounts, unmounts, remounts quickly  
**Handling:** Each mount gets its own onMount cycle  
**Test:** Rapidly click login link multiple times  
**Expected:** No race conditions, clean mount/unmount cycles

---

## Error Messages

All error messages should be:
- **User-friendly** (no technical jargon)
- **Actionable** (tell user what to do)
- **Specific** (explain what failed)
- **Consistent** (same tone throughout)

### Error Message Guidelines

| Error Scenario | Message | Why |
|----------------|---------|-----|
| Clerk SDK not available | "Authentication system not available. Please refresh the page." | Clear, actionable |
| clerk.loaded timeout | "Authentication system took too long to initialize. Please refresh the page or check your internet connection." | Explains issue, suggests solutions |
| signInDiv not bound | "Unable to display login form. Please refresh the page." | Simple, clear action |
| General initialization error | "Failed to initialize authentication. Please refresh the page." | Catch-all, still actionable |
| Backend/redirect error | (Uses errorMessage from redirectAfterAuth) | Context-specific |

---

## TypeScript Types

All types are already correctly defined. No changes needed.

**Verification:**
- `signInDiv: HTMLDivElement | null` ✅
- `isLoading: boolean` ✅
- `error: string | null` ✅
- `errorMessage: string | null` ✅
- `loadingTime: number` ✅
- `showProgressMessage: boolean` (derived) ✅
- `waitForClerkReady: (maxWaitMs?: number) => Promise<boolean>` ✅

---

## Svelte 5 Rune Patterns Used

### Correct Patterns ✅

1. **$state for mutable component state:**
   ```typescript
   let loadingTime = $state(0);
   ```

2. **$derived for computed values:**
   ```typescript
   let showProgressMessage = $derived(loadingTime > 3);
   ```

3. **onMount for one-time initialization:**
   ```typescript
   onMount(async () => { /* ... */ });
   ```

4. **Cleanup function from onMount:**
   ```typescript
   return () => { clerk.unmountSignIn(signInDiv); };
   ```

5. **tick() for DOM synchronization:**
   ```typescript
   await tick();
   ```

### Avoided Anti-Patterns ❌

1. **$effect for non-idempotent operations:** Removed
2. **Too many reactive dependencies:** Eliminated
3. **Redundant state flags:** Removed `mounted`
4. **Timeout workarounds for async:** Replaced with proper waiting

---

## Testing Hooks

To facilitate E2E testing, consider adding data attributes (OPTIONAL):

```svelte
<div 
  bind:this={signInDiv}
  data-testid="clerk-signin-container"
></div>
```

This allows Playwright to verify mounting:
```typescript
await expect(page.locator('[data-testid="clerk-signin-container"]')).toBeVisible();
```

**Decision:** Add if E2E tests need it, otherwise keep template clean.

---

## Logging and Observability

### Overview

This implementation includes **comprehensive structured logging** to ensure we can trace errors without debugging.

**Security Model:**
- ✅ **Users see:** Friendly, secure error messages (no technical details)
- ✅ **Logs contain:** Full technical context for debugging
- ✅ **Console in dev:** All logs visible for local debugging
- ✅ **Sentry-ready:** Can integrate error tracking service later

### Logged Events

#### 1. Success Events (console.log)

**Clerk SDK Load Success:**
```javascript
[Clerk Login Success] {
  timestamp: "2025-11-06T01:23:45.678Z",
  attemptNumber: 2,              // Succeeded on retry #2
  totalAttempts: 4,
  elapsedTime: 7234,             // This attempt took 7.2s
  totalElapsedTime: 11456,       // Total time including retries
  succeededOnRetry: true         // Was a retry needed?
}
```

**Clerk Mount Success:**
```javascript
[Clerk Login Mount Success] {
  timestamp: "2025-11-06T01:23:46.123Z",
  context: "Sign-in component mounted successfully"
}
```

#### 2. Error Events (console.error + logStructuredError)

**All error logs include:**
```typescript
{
  timestamp: string;           // ISO 8601
  errorType: NetworkErrorType; // offline|timeout|sdk_not_available|mount_failed|server_error
  attemptNumber: number;        // Which attempt (1-4, or 0 for fast-fail)
  totalAttempts: number;        // Total configured attempts
  elapsedTime: number;          // Time in ms for this attempt
  networkOnline: boolean;       // navigator.onLine at error time
  clerkAvailable: boolean;      // Was clerk SDK loaded?
  clerkLoaded: boolean;         // Was clerk.loaded true?
  userAgent: string;            // Browser info
  url: string;                  // Page URL
  context: string;              // Specific error context
}
```

**Example logged errors:**

**Offline (Fast Fail):**
```javascript
[Clerk Login Error] {
  timestamp: "2025-11-06T01:23:45.000Z",
  errorType: "offline",
  attemptNumber: 0,              // Before first attempt
  totalAttempts: 4,
  elapsedTime: 0,
  networkOnline: false,          // User is offline
  clerkAvailable: true,
  clerkLoaded: false,
  userAgent: "Mozilla/5.0 ...",
  url: "https://example.com/login",
  context: "Fast fail: offline detected before first attempt",
  summary: "offline on attempt 0/4 after 0ms"
}
```

**Timeout After Retries:**
```javascript
[Clerk Login Error] {
  timestamp: "2025-11-06T01:24:10.234Z",
  errorType: "timeout",
  attemptNumber: 4,              // Final attempt
  totalAttempts: 4,
  elapsedTime: 5123,             // This attempt took 5.1s
  networkOnline: true,           // Network shows online
  clerkAvailable: true,          // SDK loaded
  clerkLoaded: false,            // But never became ready
  userAgent: "Mozilla/5.0 ...",
  url: "https://example.com/login",
  context: "Final attempt failed - giving up",
  summary: "timeout on attempt 4/4 after 5123ms"
}
```

**Mount Failed:**
```javascript
[Clerk Login Error] {
  timestamp: "2025-11-06T01:23:48.567Z",
  errorType: "mount_failed",
  attemptNumber: 0,
  totalAttempts: 1,
  elapsedTime: 0,
  networkOnline: true,
  clerkAvailable: true,
  clerkLoaded: true,             // SDK ready, but mounting failed
  userAgent: "Mozilla/5.0 ...",
  url: "https://example.com/login",
  context: "Clerk mountSignIn() threw exception: TypeError: ...",
  summary: "mount_failed on attempt 0/1 after 0ms"
}
```

### Debugging Workflow

**When user reports "login not working":**

1. **Ask user to open DevTools Console** (F12 → Console tab)

2. **Look for error logs:**
   ```
   [Clerk Login Error] { ... }
   ```

3. **Analyze error fields:**
   - `errorType`: What category of failure?
   - `attemptNumber`: Did retries happen? How many?
   - `networkOnline`: Was network actually online?
   - `clerkAvailable`: Did SDK load?
   - `clerkLoaded`: Did SDK become ready?
   - `context`: Specific failure reason

4. **Common debugging scenarios:**

| errorType | networkOnline | clerkAvailable | clerkLoaded | Root Cause |
|-----------|---------------|----------------|-------------|------------|
| offline | false | - | - | User has no internet |
| sdk_not_available | true | false | false | Ad blocker or CDN down |
| timeout | true | true | false | Slow network, Clerk CDN issue |
| timeout | true | true | true | Race condition still exists (should not happen) |
| mount_failed | true | true | true | DOM issue or Clerk SDK bug |

5. **Follow-up questions based on error:**
   - **offline:** "Is your internet working? Can you load other websites?"
   - **sdk_not_available:** "Do you have an ad blocker? Can you disable it and refresh?"
   - **timeout:** "Is your connection slow? Try on a different network?"
   - **mount_failed:** "What browser are you using? Any console errors?"

### Production Error Tracking (Future)

**Currently:** Console-based logging (sufficient for MVP)

**Future Integration (Sentry):**

```typescript
function logStructuredError(entry: ErrorLogEntry): void {
  // Keep console logging for dev
  console.error('[Clerk Login Error]', { ...entry });

  // Add Sentry in production
  if (import.meta.env.PROD) {
    Sentry.captureException(new Error(entry.errorType), {
      level: 'error',
      fingerprint: [entry.errorType, entry.attemptNumber.toString()],
      tags: {
        errorType: entry.errorType,
        attemptNumber: entry.attemptNumber,
        networkOnline: entry.networkOnline,
        clerkLoaded: entry.clerkLoaded,
      },
      extra: entry,
    });
  }
}
```

**Benefits of Sentry integration:**
- Automatic error aggregation (group similar errors)
- Track frequency of each error type
- Monitor retry success rate
- Alert on error spikes
- User session replay
- Stack traces for unexpected errors

**Metrics to Track:**
- Error rate by type (offline vs timeout vs blocked)
- Retry success rate (how often does attempt 2 succeed?)
- Average time to successful mount
- Most common user agents with failures
- Geographic patterns (CDN issues in specific regions?)

### Privacy Considerations

**PII Handling:**
- ❌ Never log user email, name, ID
- ❌ Never log authentication tokens
- ✅ Log only technical diagnostics
- ✅ User agent (browser info) is safe
- ✅ URL is safe (no query params with tokens)

**Current implementation is PII-safe.**

---

## Performance Considerations

### Before (Current):

- Timeout fires at 5s regardless of actual load time
- $effect can trigger multiple times
- Potential mount/unmount cycles

### After (Proposed):

- Waits exactly as long as needed (no artificial delay)
- Mounts exactly once (no re-triggers)
- Faster on good connections (no 5s wait)
- Better feedback on slow connections (progress message)

**Expected Performance:**
- Fast networks: < 1s (improved)
- Slow networks: 3-6s (same, but better UX)
- Very slow networks: 10s timeout (vs 5s current, more generous)

---

## Accessibility Considerations

### Loading State

Current ARIA attributes are implicit. Consider adding (OPTIONAL):

```svelte
{#if isLoading}
  <div 
    class="bg-white rounded-xl shadow-lg p-8 flex items-center justify-center"
    role="status"
    aria-live="polite"
  >
    <div class="text-center">
      <div 
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"
        aria-hidden="true"
      ></div>
      <p class="text-gray-600">Loading authentication...</p>
      
      {#if showProgressMessage}
        <p class="text-sm text-gray-500 mt-2">
          This is taking longer than expected ({loadingTime}s)...
        </p>
      {/if}
    </div>
  </div>
{/if}
```

**Benefits:**
- Screen readers announce loading state
- Progress updates announced as they change
- Spinner marked as decorative

**Decision:** Add if accessibility audit recommends it.

---

## Rollback Plan

If issues are discovered after deployment:

### Immediate Rollback Steps

1. **Revert the commit:**
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

2. **Deploy previous version:**
   ```bash
   make rebuild
   make up
   ```

3. **Verify rollback:**
   - Test login page manually
   - Check error rates
   - Monitor support tickets

### What to Monitor

- Login success rate (should NOT decrease)
- Error rate on /login (should NOT increase)
- Support tickets about blank form (should decrease)
- Average load time (should be similar or better)

---

## Implementation Checklist

For implementation agent (dev-frontend-svelte):

- [ ] Remove `mounted` state variable (line 41)
- [ ] Add `loadingTime` state variable (after line 42)
- [ ] Add `showProgressMessage` derived state
- [ ] Add `waitForClerkReady()` helper function
- [ ] Replace onMount logic (lines 50-98)
- [ ] Remove $effect block entirely (lines 134-162)
- [ ] Update loading UI template (lines 181-188)
- [ ] Add try-catch around clerk.mountSignIn() (recommended)
- [ ] Test TypeScript compilation (no errors)
- [ ] Test ESLint (no errors, minimal warnings)
- [ ] Manual test with DevTools throttling
- [ ] Verify cleanup function works (check console on unmount)

---

## Questions for Code Review

Reviewers should verify:

1. Is `waitForClerkReady()` robust enough for all network conditions?
2. Is 10s timeout appropriate, or should it be configurable?
3. Should we add try-catch around `clerk.mountSignIn()`?
4. Should we add telemetry for load times?
5. Are error messages clear enough for users?
6. Do we need accessibility attributes on loading state?
7. Should we add data-testid for E2E tests?

---

## Success Criteria

Implementation is successful when:

- [ ] Code compiles without TypeScript errors
- [ ] ESLint passes with 0 errors, ≤ 5 warnings
- [ ] Login form appears on normal networks
- [ ] Login form appears on slow networks (with progress)
- [ ] Timeout shows clear error after 10s
- [ ] No console errors in browser
- [ ] Manual testing passes on Chrome, Firefox, Safari
- [ ] E2E tests pass (after written)

---

**Implementation Specification Complete ✅**

Ready for implementation by dev-frontend-svelte agent.

---

**End of Document**
