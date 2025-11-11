# Race Condition Hypothesis - Detailed Scenarios

**Date:** 2025-11-06  
**Phase:** RESEARCH  
**Task:** TASK-001 (US-001: Login Flow Validation)  
**Analyst:** File Search Specialist

---

## Executive Summary

This document identifies **4 specific race conditions** in the current Clerk mounting implementation, provides timeline diagrams for each, assesses impact, and offers reproduction steps where possible.

**Primary Race Condition:** Timeout fires before clerk.load() completes, causing `mountSignIn()` to be called on incomplete SDK initialization.

**Secondary Issues:** Double-load conflicts, $effect multi-trigger, and cleanup timing.

---

## Race Condition #1: Timeout vs Load Completion

### Description

The 5-second timeout in `onMount()` races against `clerk.load()` promise resolution. If the timeout wins, `mounted` is set to `true` before Clerk SDK is ready, triggering `$effect` to call `mountSignIn()` prematurely.

### Code Location

`apps/frontend/src/routes/login/+page.svelte` (lines 60-75)

```typescript
if (!clerk.loaded) {
  const loadTimeout = setTimeout(() => {
    console.warn('Clerk load timeout - proceeding anyway');
    isLoading = false;
    mounted = true; // ⚠️ Sets mounted before load completes
  }, 5000);

  try {
    await clerk.load(); // May take > 5s
    clearTimeout(loadTimeout);
  } catch (loadError) {
    clearTimeout(loadTimeout);
    console.error('Clerk load error:', loadError);
    // Continue anyway - might still work
  }
}
```

### Timeline Diagram

#### Scenario A: Timeout Wins (FAILURE)

```
Time    | Layout Thread              | Login Page Thread           | Clerk SDK State
--------|----------------------------|-----------------------------|-----------------
0ms     | onMount starts             |                             | Not loaded
50ms    | initializeClerk() starts   |                             | Loading...
100ms   | clerk.load() in progress   | User navigates to /login    | Loading...
150ms   |                            | onMount starts              | Loading...
160ms   |                            | Check: clerk.loaded = false | Loading...
165ms   |                            | Start 5s timeout            | Loading...
170ms   |                            | Call clerk.load() again     | Loading...
        |                            | (duplicate call!)           |
2000ms  | clerk.load() still pending | Timeout countdown...        | Loading...
4000ms  | (slow network)             | Timeout countdown...        | Loading...
5165ms  | clerk.load() still pending | ⚠️ TIMEOUT FIRES            | Loading...
        |                            | mounted = true              |
        |                            | isLoading = false           |
5170ms  | clerk.load() still pending | $effect triggers            | Loading...
        |                            | ⚠️ mountSignIn() called     |
        |                            | SDK NOT READY - FAILS       |
6000ms  | clerk.load() COMPLETES     | Form broken, user confused  | ✅ Loaded
        | (too late)                 | Empty white box shown       | (but not mounted)
```

**Result:** Form doesn't appear, user sees blank space or spinner forever.

---

#### Scenario B: Load Wins (SUCCESS)

```
Time    | Layout Thread              | Login Page Thread           | Clerk SDK State
--------|----------------------------|-----------------------------|-----------------
0ms     | onMount starts             |                             | Not loaded
50ms    | initializeClerk() starts   |                             | Loading...
100ms   | clerk.load() in progress   |                             | Loading...
500ms   | ✅ clerk.load() COMPLETES  |                             | ✅ Loaded
600ms   |                            | User navigates to /login    | Loaded
650ms   |                            | onMount starts              | Loaded
660ms   |                            | Check: clerk.loaded = TRUE  | Loaded
        |                            | Skip load, clear timeout    |
        |                            | mounted = true              |
        |                            | isLoading = false           |
670ms   |                            | $effect triggers            | Loaded
        |                            | ✅ mountSignIn() succeeds   |
        |                            | Form appears correctly      |
```

**Result:** Works as expected.

---

### Reproduction Steps

**Prerequisites:**
- Chrome DevTools Network Throttling
- Bestays app running locally

**Steps:**

1. Open Chrome DevTools (F12) → Network tab
2. Set throttling to "Slow 3G" (or custom: 500ms latency, 50kb/s)
3. Clear browser cache and reload
4. Open new incognito window
5. Navigate directly to `http://localhost:5183/login`
6. Observe behavior:
   - **Expected (bug):** Loading spinner for 5s → Empty white box
   - **Expected (fixed):** Loading spinner → Login form appears

**Alternative (Simulate Network Delay):**

1. In DevTools, go to Network tab → Right-click → Block request URL
2. Block `https://clerk.accounts.dev/*` for exactly 6 seconds
3. Unblock after 6 seconds
4. Navigate to `/login`
5. Timeout will fire at 5s, SDK loads at 6s (too late)

---

### Impact Assessment

**Severity:** 🔴 HIGH  
**Frequency:** Depends on network conditions  
**User Impact:**
- Users on slow networks (mobile, rural, developing countries) see broken login
- International users with high latency to Clerk's servers affected
- First-time visitors (no cached assets) more likely to hit this

**Business Impact:**
- Users can't log in → Can't use app
- Abandonment at login page
- Support tickets about "blank login page"
- Poor first impression

---

## Race Condition #2: Double clerk.load() Calls

### Description

Both `+layout.svelte` and `login/+page.svelte` may call `clerk.load()` simultaneously if user navigates to `/login` before layout initialization completes.

### Code Locations

**Layout:** `apps/frontend/src/routes/+layout.svelte` (line 62)
```typescript
await initializeClerk(); // Calls clerk.load()
```

**Login Page:** `apps/frontend/src/routes/login/+page.svelte` (line 68)
```typescript
if (!clerk.loaded) {
  await clerk.load(); // May call again
}
```

### Timeline Diagram

```
Time    | Layout Thread              | Login Page Thread           | Clerk SDK
--------|----------------------------|-----------------------------|-----------
0ms     | App starts                 |                             | Not loaded
10ms    | +layout.svelte onMount     |                             | Not loaded
20ms    | initializeClerk() starts   |                             | Not loaded
30ms    | ⚠️ clerk.load() CALL #1    |                             | Loading...
50ms    | (awaiting promise)         | User navigates to /login    | Loading...
60ms    | (awaiting promise)         | +page.svelte onMount        | Loading...
70ms    | (awaiting promise)         | Check: clerk.loaded = false | Loading...
80ms    | (awaiting promise)         | ⚠️ clerk.load() CALL #2     | Loading...
        |                            | (duplicate call!)           |
100ms   | clerk.load() #1 resolving  | clerk.load() #2 resolving   | Loading...
200ms   | ✅ CALL #1 completes       | ⏳ CALL #2 still pending    | Loaded
250ms   | listener registered        | ⚠️ CALL #2 completes        | ???
        |                            | (redundant)                 |
```

**Questions:**
- Does Clerk SDK handle duplicate load() calls safely?
- Do both promises resolve, or does one fail?
- Is internal state consistent?

---

### Potential Outcomes

**Best Case:** Clerk SDK internally prevents duplicate loads (likely)

**Worst Case:**
- Second load resets SDK state
- Event listeners duplicated
- Memory leaks
- Unpredictable behavior

---

### Testing Required

**Code Inspection:**
Check Clerk SDK source or documentation for:
- Is `clerk.load()` idempotent?
- Does it have internal guards against duplicate calls?
- What happens if called twice simultaneously?

**Manual Test:**
```javascript
// In browser console
await clerk.load();
await clerk.load(); // Safe?
console.log(clerk.loaded); // Still true?
```

---

### Impact Assessment

**Severity:** 🟡 MEDIUM  
**Frequency:** Common on first page load to `/login`  
**User Impact:**
- Likely minimal if Clerk SDK handles it gracefully
- Possible edge cases with event listeners or session state

**Recommendation:** Eliminate redundancy by trusting layout initialization.

---

## Race Condition #3: $effect Multi-Trigger

### Description

The `$effect` block has 5 reactive dependencies. Any change to any dependency causes the effect to re-run, potentially unmounting and remounting Clerk UI multiple times in quick succession.

### Code Location

`apps/frontend/src/routes/login/+page.svelte` (lines 134-162)

```typescript
$effect(() => {
  // 5 dependencies:
  if (signInDiv && mounted && clerk && !isLoading && !error) {
    // Mount Clerk UI
    clerk.mountSignIn(signInDiv, { signUpUrl: '/signup' });
    
    // Cleanup on re-run or unmount
    return () => {
      if (signInDiv) {
        clerk.unmountSignIn(signInDiv);
      }
    };
  }
});
```

### Reactive Dependency Analysis

| Dependency | Type | Changes When | Frequency |
|------------|------|--------------|-----------|
| `signInDiv` | DOM ref | Element bound/unbound | 1-2 times |
| `mounted` | boolean | Set in onMount | Once |
| `clerk` | object | Never (singleton) | Never |
| `isLoading` | boolean | true → false in onMount | Once |
| `error` | string\|null | Set on error | 0-N times |

**Expected Triggers:** 2-3 times total
1. Initial render (signInDiv binds)
2. onMount completes (mounted + isLoading change)
3. Possibly one more on full state reconciliation

**Problematic Scenarios:**

1. **DOM Re-Render:**
   - Svelte re-renders component (e.g., parent state change)
   - `signInDiv` unbinds → becomes null
   - $effect cleanup runs → unmountSignIn()
   - New div element binds
   - $effect runs again → mountSignIn()
   - **Result:** Flickering UI, form resets

2. **Error Toggle:**
   - Initialization succeeds, error = null
   - Mount happens
   - Later, some validation sets error = 'message'
   - $effect condition becomes false
   - Cleanup runs → unmountSignIn()
   - Form disappears unexpectedly

---

### Timeline Diagram: Rapid Multi-Trigger

```
Time    | State Changes                          | $effect Behavior           | User Sees
--------|----------------------------------------|----------------------------|-------------
0ms     | Component mounts                       |                            | Loading...
10ms    | signInDiv binds, but mounted=false     | Condition false, no mount  | Loading...
100ms   | onMount completes:                     |                            |
        | mounted=true, isLoading=false          |                            |
110ms   | All conditions true                    | ✅ Mount Clerk UI          | Login form
500ms   | (User typing in form)                  |                            | Login form
550ms   | Parent component re-renders            |                            |
560ms   | signInDiv UNBINDS (null)               | ⚠️ Cleanup: unmountSignIn | Form vanishes!
570ms   | signInDiv RE-BINDS (new element)       | ⚠️ Mount again             | Form reappears
        |                                        |                            | (Input cleared)
```

**Result:** Form flickers, user loses typed input, frustrating UX.

---

### Reproduction Steps

**Difficult to reproduce reliably** - requires triggering Svelte re-render.

**Possible Methods:**

1. **Fast Network Toggle:**
   - Open DevTools → Network → Toggle offline/online rapidly
   - May trigger error state changes

2. **Force Re-Render:**
   - Add a prop to login page from layout
   - Change prop value from DevTools
   - Observe if form remounts

3. **Use React DevTools Profiler Equivalent for Svelte:**
   - Monitor component render cycles
   - Look for unexpected re-renders

---

### Impact Assessment

**Severity:** 🟡 MEDIUM  
**Frequency:** Low (requires specific re-render conditions)  
**User Impact:**
- Form resets, losing user input
- Flickering UI
- Confusion

**Recommendation:** Reduce reactive dependencies, use more explicit mounting logic.

---

## Race Condition #4: Cleanup Timing Issues

### Description

The $effect cleanup function (`unmountSignIn`) may run at inappropriate times, such as during navigation but before the new page loads, causing brief visual glitches.

### Code Location

`apps/frontend/src/routes/login/+page.svelte` (lines 156-160)

```typescript
return () => {
  if (signInDiv) {
    clerk.unmountSignIn(signInDiv);
  }
};
```

### Scenario: Navigation During Mount

```
Time    | User Action                  | $effect State               | DOM State
--------|------------------------------|-----------------------------|--------------
0ms     | User on /login, form mounted | Conditions true, mounted    | Form visible
100ms   | User clicks "Back to Home"   | Still mounted               | Form visible
110ms   | Navigation starts            | Still mounted               | Form visible
120ms   | Login component unmounting   | ⚠️ Cleanup runs             | Form removed
130ms   | Transition animation running | Cleanup complete            | Element gone
200ms   | Home page loads              |                             | New page
```

**Issue:** Between 120ms-200ms, user may see:
- Blank space where form was
- Layout shift
- Broken transition animation

---

### Impact Assessment

**Severity:** 🟢 LOW  
**Frequency:** Every navigation away from login  
**User Impact:**
- Brief visual glitch during navigation
- Not blocking, but unprofessional

**Recommendation:** Ensure cleanup is synchronous and transitions are smooth.

---

## Summary of Race Conditions

| # | Name | Severity | Likelihood | User Impact | Fix Priority |
|---|------|----------|------------|-------------|--------------|
| 1 | Timeout vs Load | 🔴 HIGH | Medium | Form doesn't appear | **P0** |
| 2 | Double Load | 🟡 MEDIUM | High | Possible inconsistency | P1 |
| 3 | Multi-Trigger | 🟡 MEDIUM | Low | Form resets | P1 |
| 4 | Cleanup Timing | 🟢 LOW | High | Visual glitch | P2 |

---

## Root Causes

### 1. Distrust of Async Operations

**Evidence:** 5-second timeout "just in case" load takes too long

**Problem:** Adds complexity and creates new failure modes instead of handling the actual async operation properly.

**Solution:** Trust the promise, add proper loading states and user feedback.

---

### 2. Over-Reactive Dependencies

**Evidence:** 5 dependencies in $effect, any change re-triggers

**Problem:** Svelte 5 runes are fine-grained reactive. Too many dependencies = too many triggers.

**Solution:** Use explicit imperative mounting after async initialization completes.

---

### 3. Redundant Initialization

**Evidence:** Both layout and page call clerk.load()

**Problem:** Violates "single source of truth" principle.

**Solution:** Layout owns initialization, page trusts it's complete.

---

### 4. Complex State Management

**Evidence:** Multiple boolean flags (mounted, isLoading, error) controlling single mount operation

**Problem:** More state = more potential for inconsistency.

**Solution:** Simplify to single state machine or direct imperative flow.

---

## Recommendations for Planning Phase

### Immediate Actions (Fix Race Condition #1)

1. **Remove timeout workaround**
2. **Trust layout initialization**
3. **Add proper loading UI with progress indication**
4. **Show user-friendly message if load takes > 5s (but don't timeout)**

### Medium-Term (Reduce Complexity)

1. **Simplify $effect dependencies to 1-2 max**
2. **Consider imperative mounting instead of reactive**
3. **Eliminate duplicate load() calls**

### Long-Term (Robust Pattern)

1. **Implement proper state machine for mount lifecycle**
2. **Add telemetry to track actual load times**
3. **Create loading skeleton UI for perceived performance**

---

## Next Steps

The **svelte5-patterns.md** document will research recommended patterns for implementing the solutions above.

The **findings-summary.md** will synthesize all research and provide actionable implementation plan for planning phase.

---

**End of Analysis**
