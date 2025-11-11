# Lessons Learned - Implementation Specification

**Date:** 2025-11-06
**Task:** TASK-001
**Phase:** Planning Review
**Purpose:** Capture patterns for future planning phases

---

## Context

During planning review for TASK-001, user identified critical gaps:
1. No retry logic with exponential backoff for network operations
2. No error type differentiation
3. No offline detection
4. Missing SSR/UX considerations checklist

**Goal:** Capture these patterns so future Plan agents automatically consider them during planning.

---

## Deliverables

### 1. Frontend Network Resilience Skill

**File:** `.claude/skills/frontend-network-resilience/SKILL.md`

**Purpose:** Provide detailed patterns for robust network operations in frontend code

**Contents:**

```markdown
---
description: Network resilience patterns for frontend - retry logic, exponential backoff, error handling, offline detection
tags: [frontend, network, resilience, retry, error-handling, UX]
related_skills: [frontend-svelte, dev-philosophy, dev-code-quality]
applies_to: [Plan, dev-frontend-svelte]
---

# Frontend Network Resilience Patterns

Comprehensive patterns for building robust network operations in frontend applications.

---

## Core Principles

1. **Never trust the network** - Always plan for failure
2. **Fail gracefully** - Degrade functionality, don't break completely
3. **Provide feedback** - User should know what's happening
4. **Auto-recover** - Retry transient failures automatically
5. **Differentiate errors** - Different errors need different messages

---

## Pattern 1: Exponential Backoff Retry

**When to Use:**
- Loading external SDKs (Clerk, Stripe, Google Maps)
- API calls to backend services
- Third-party API integrations
- CDN resource loading

**When NOT to Use:**
- User-initiated actions (use immediate retry with button instead)
- Real-time operations (WebSocket - use reconnection logic instead)
- Operations that must succeed exactly once (payments - use idempotency)

**Implementation Pattern:**

```typescript
/**
 * Retry an operation with exponential backoff
 *
 * @param operation - Async function to retry
 * @param maxAttempts - Maximum number of attempts (default: 4)
 * @param initialDelay - Initial delay in ms (default: 2000)
 * @param maxDelay - Maximum delay in ms (default: 30000)
 * @returns Result of operation or throws after all attempts exhausted
 */
async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  maxAttempts = 4,
  initialDelay = 2000,
  maxDelay = 30000
): Promise<T> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      // Last attempt - rethrow error
      if (attempt === maxAttempts) {
        throw error;
      }

      // Calculate delay with exponential backoff
      const delay = Math.min(
        initialDelay * Math.pow(2, attempt - 1),
        maxDelay
      );

      console.log(`Attempt ${attempt}/${maxAttempts} failed, retrying in ${delay}ms...`);

      // Wait before next attempt
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw new Error('All retry attempts exhausted');
}
```

**Usage Example:**

```typescript
// Loading external SDK with retry
const sdkLoaded = await retryWithBackoff(
  async () => {
    if (!sdk.loaded) {
      throw new Error('SDK not ready');
    }
    return true;
  },
  4,      // 4 attempts
  2000,   // Start with 2s delay
  30000   // Max 30s delay
);
```

**Backoff Schedule Examples:**

```
4 attempts, 2s initial:
  Attempt 1 → wait 2s → Attempt 2 → wait 4s → Attempt 3 → wait 8s → Attempt 4
  Total: ~14s

4 attempts, 3s initial:
  Attempt 1 → wait 3s → Attempt 2 → wait 6s → Attempt 3 → wait 12s → Attempt 4
  Total: ~21s

5 attempts, 2s initial:
  Attempt 1 → wait 2s → Attempt 2 → wait 4s → Attempt 3 → wait 8s →
  Attempt 4 → wait 16s → Attempt 5
  Total: ~30s
```

---

## Pattern 2: Error Type Differentiation

**Error Taxonomy:**

```typescript
type NetworkErrorType =
  | 'offline'           // No internet connection
  | 'timeout'           // Request/load took too long
  | 'blocked'           // Blocked by browser/extension/firewall
  | 'not_found'         // Resource doesn't exist (404)
  | 'server_error'      // Server returned 5xx
  | 'unauthorized'      // Auth failed (401/403)
  | 'rate_limited'      // Too many requests (429)
  | 'network_error'     // Generic network failure
  | 'unknown';          // Unclassified error

interface NetworkError {
  type: NetworkErrorType;
  message: string;
  userMessage: string;  // User-friendly message
  canRetry: boolean;    // Should we offer retry?
  autoRetry: boolean;   // Should we auto-retry?
}
```

**Error Detection:**

```typescript
function classifyNetworkError(error: any): NetworkError {
  // Offline detection
  if (!navigator.onLine) {
    return {
      type: 'offline',
      message: 'Network offline',
      userMessage: 'No internet connection. Please check your network.',
      canRetry: true,
      autoRetry: false  // Don't auto-retry if offline
    };
  }

  // Timeout
  if (error.name === 'TimeoutError' || error.message?.includes('timeout')) {
    return {
      type: 'timeout',
      message: error.message,
      userMessage: 'Connection is very slow. Please check your internet.',
      canRetry: true,
      autoRetry: true  // Auto-retry timeouts
    };
  }

  // Blocked (CSP, ad blocker, CORS)
  if (error.message?.includes('blocked') ||
      error.message?.includes('CSP') ||
      error.name === 'SecurityError') {
    return {
      type: 'blocked',
      message: error.message,
      userMessage: 'Resource blocked. Please disable ad blockers.',
      canRetry: true,
      autoRetry: false  // User must fix blocker first
    };
  }

  // HTTP status codes
  if (error.status === 404) {
    return {
      type: 'not_found',
      message: error.message,
      userMessage: 'Resource not found.',
      canRetry: false,
      autoRetry: false
    };
  }

  if (error.status >= 500) {
    return {
      type: 'server_error',
      message: error.message,
      userMessage: 'Server error. Please try again later.',
      canRetry: true,
      autoRetry: true  // Server errors are often transient
    };
  }

  if (error.status === 401 || error.status === 403) {
    return {
      type: 'unauthorized',
      message: error.message,
      userMessage: 'Please sign in again.',
      canRetry: false,
      autoRetry: false
    };
  }

  if (error.status === 429) {
    return {
      type: 'rate_limited',
      message: error.message,
      userMessage: 'Too many requests. Please wait a moment.',
      canRetry: true,
      autoRetry: true  // With longer backoff
    };
  }

  // Generic network error
  return {
    type: 'network_error',
    message: error.message || 'Unknown error',
    userMessage: 'Network error. Please try again.',
    canRetry: true,
    autoRetry: true
  };
}
```

---

## Pattern 3: Offline Detection

**Implementation:**

```typescript
import { onMount } from 'svelte';

let isOnline = $state(true);

onMount(() => {
  // Initial check
  isOnline = navigator.onLine;

  // Listen for online/offline events
  const handleOnline = () => { isOnline = true; };
  const handleOffline = () => { isOnline = false; };

  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);

  return () => {
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  };
});
```

**Usage in Components:**

```svelte
{#if !isOnline}
  <div class="offline-banner">
    ⚠️ No internet connection. Some features may not work.
  </div>
{/if}

<button
  onclick={handleAction}
  disabled={!isOnline}
>
  Submit
</button>
```

---

## Pattern 4: Progressive Loading with Feedback

**For External SDK Loading:**

```svelte
<script lang="ts">
  let loadingState = $state<'idle' | 'loading' | 'ready' | 'error'>('idle');
  let loadingTime = $state(0);
  let attemptNumber = $state(0);
  let error = $state<NetworkError | null>(null);

  // Show progress message after 3s
  let showProgress = $derived(loadingTime > 3);

  async function loadSDK() {
    loadingState = 'loading';
    loadingTime = 0;

    // Update loading time every second
    const interval = setInterval(() => {
      loadingTime++;
    }, 1000);

    try {
      await retryWithBackoff(
        async () => {
          attemptNumber++;
          // SDK load logic
          if (!sdk.loaded) throw new Error('Not ready');
          return true;
        },
        4,
        2000
      );

      clearInterval(interval);
      loadingState = 'ready';
    } catch (err) {
      clearInterval(interval);
      loadingState = 'error';
      error = classifyNetworkError(err);
    }
  }
</script>

{#if loadingState === 'loading'}
  <div class="loading-container">
    <Spinner />

    {#if attemptNumber > 1}
      <p>Connecting... (attempt {attemptNumber}/4)</p>
    {:else if showProgress}
      <p>This is taking longer than expected ({loadingTime}s)...</p>
    {:else}
      <p>Loading...</p>
    {/if}
  </div>
{:else if loadingState === 'error'}
  <ErrorMessage
    error={error}
    onRetry={error.canRetry ? loadSDK : undefined}
  />
{/if}
```

---

## Pattern 5: SSR-Friendly Network Operations

**Guidelines:**

1. **Never call network operations during SSR**
   ```typescript
   // ❌ BAD - Will fail during SSR
   const data = await fetch('/api/data');

   // ✅ GOOD - Only runs client-side
   onMount(async () => {
     const data = await fetch('/api/data');
   });
   ```

2. **Provide initial loading state in SSR HTML**
   ```svelte
   <!-- This renders during SSR -->
   <div class="content">
     {#if data}
       <DataDisplay {data} />
     {:else}
       <!-- This spinner is in SSR HTML -->
       <Spinner />
       <p>Loading content...</p>
     {/if}
   </div>
   ```

3. **Handle hydration gracefully**
   ```typescript
   let data = $state(null);
   let isLoading = $state(true); // true during SSR and hydration

   onMount(async () => {
     // This runs after hydration
     data = await loadData();
     isLoading = false;
   });
   ```

---

## Planning Checklist

When planning any feature with network operations, ensure:

### Network Operation Requirements
- [ ] Retry logic with exponential backoff specified
- [ ] Number of attempts and timing justified (e.g., 4 attempts, 2s initial)
- [ ] Error types are differentiated with appropriate messages
- [ ] Offline state is detected and handled
- [ ] Timeout values are specified and justified
- [ ] Manual retry option provided (button)
- [ ] Loading states defined for all durations (0-3s, 3-10s, 10s+)

### SSR/Hydration Requirements
- [ ] Network operations only in onMount or client-side code
- [ ] Initial loading state present in SSR HTML
- [ ] No flash of incorrect content (FOUC) during hydration
- [ ] Progressive enhancement considered

### UX Requirements
- [ ] User sees feedback within 1s (spinner, progress indicator)
- [ ] Progress message shown if loading > 3s
- [ ] Error messages are user-friendly and actionable
- [ ] User can retry without full page refresh
- [ ] Graceful degradation if JS disabled (where possible)

---

## Testing Requirements

All network operations must include tests for:

1. **Success scenario** - Normal network conditions
2. **Slow network** - Simulated 3G (3-5s response time)
3. **Very slow network** - Extreme latency (8-10s)
4. **Offline** - No internet connection
5. **Timeout** - No response within timeout period
6. **Intermittent failure** - Fails first 2 attempts, succeeds on 3rd
7. **Persistent failure** - Fails all retry attempts
8. **Error types** - 401, 403, 404, 429, 500, 503

**Playwright Example:**

```typescript
test('SDK loads with retry on slow network', async ({ page, context }) => {
  // Simulate slow 3G
  await context.route('**/clerk.sdk.js', async (route) => {
    await new Promise(resolve => setTimeout(resolve, 4000));
    await route.continue();
  });

  await page.goto('/login');

  // Should show loading state
  await expect(page.locator('.spinner')).toBeVisible();

  // Should show progress message after 3s
  await expect(page.locator('text=Taking longer')).toBeVisible({ timeout: 4000 });

  // Should eventually load
  await expect(page.locator('.clerk-sign-in')).toBeVisible({ timeout: 10000 });
});
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Single Timeout Without Retry

```typescript
// BAD - Gives up after one timeout
const loaded = await waitForSDK(10000);
if (!loaded) {
  showError('Failed to load');
}
```

```typescript
// GOOD - Retries with backoff
const loaded = await retryWithBackoff(
  () => waitForSDK(5000),
  4,
  2000
);
```

### ❌ Mistake 2: Generic Error Messages

```typescript
// BAD - Same message for all errors
catch (error) {
  showError('Something went wrong. Please try again.');
}
```

```typescript
// GOOD - Differentiated messages
catch (error) {
  const networkError = classifyNetworkError(error);
  showError(networkError.userMessage);

  if (networkError.canRetry) {
    showRetryButton();
  }
}
```

### ❌ Mistake 3: Ignoring Offline State

```typescript
// BAD - Attempts network call while offline
async function loadData() {
  return await fetch('/api/data');
}
```

```typescript
// GOOD - Checks offline state first
async function loadData() {
  if (!navigator.onLine) {
    throw new Error('offline');
  }
  return await fetch('/api/data');
}
```

### ❌ Mistake 4: Network Calls During SSR

```typescript
// BAD - Will fail during SSR
const data = await fetch('/api/data');
```

```typescript
// GOOD - Only client-side
let data = $state(null);

onMount(async () => {
  data = await fetch('/api/data');
});
```

---

## References

- [MDN: Exponential Backoff](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API/Using_IndexedDB#using_experimental_features)
- [Google Cloud: Retry Strategy](https://cloud.google.com/iot/docs/how-tos/exponential-backoff)
- [AWS: Error Retries and Exponential Backoff](https://docs.aws.amazon.com/general/latest/gr/api-retries.html)
- [SvelteKit: Load Functions](https://kit.svelte.dev/docs/load)

---

**Last Updated:** 2025-11-06
**Applies To:** All frontend network operations
**Mandatory:** YES - Plan agents must reference this during planning
```

---

### 2. Planning Quality Gates Skill

**File:** `.claude/skills/planning-quality-gates/SKILL.md`

**Purpose:** Provide mandatory checklist for Plan agents to verify before completing planning phase

**Contents:**

```markdown
---
description: Mandatory quality gates and checklists for planning phase - ensures comprehensive planning
tags: [planning, quality, checklist, SDLC, architecture]
related_skills: [dev-philosophy, dev-code-quality, frontend-network-resilience]
applies_to: [Plan]
mandatory: true
---

# Planning Quality Gates

Mandatory checklist for Plan agents to verify before completing planning phase.

**Usage:** Plan agents MUST reference this skill and verify all applicable checks before delivering planning artifacts.

---

## Overview

This skill ensures that planning phase produces comprehensive, production-ready specifications that consider:
- Network resilience
- Error handling
- SSR/UX implications
- Testing requirements
- Deployment safety

---

## Quality Gate 1: Network Operations

**Applies When:** Plan involves:
- External SDK loading (Clerk, Stripe, Google Maps, etc.)
- API calls to backend services
- Third-party API integrations
- CDN resource loading
- WebSocket connections

**Mandatory Checks:**

### Retry Logic
- [ ] Retry strategy is specified (number of attempts, timing)
- [ ] Exponential backoff pattern is used (or justified why not)
- [ ] Total wait time is reasonable (typically 10-40s)
- [ ] Justification provided for retry parameters

**Examples:**
- ✅ "4 attempts with 2s, 4s, 8s backoff (total ~24s)"
- ✅ "No retry - idempotent payment operation, user must confirm"
- ❌ "Use retry logic" (too vague)

### Error Handling
- [ ] Error types are differentiated (offline, timeout, blocked, server_error, etc.)
- [ ] User-friendly error messages defined for each type
- [ ] Manual retry option provided (button)
- [ ] Auto-retry vs manual retry decision is documented

**Example:**
```typescript
Errors to handle:
- offline: "No internet connection. Please check your network."
- timeout: "Connection is very slow. Retrying automatically..."
- blocked: "Resource blocked. Please disable ad blockers."
- server_error: "Server error. We're working on it."
```

### Timeout Strategy
- [ ] Timeout values specified (e.g., 5s per attempt)
- [ ] Total timeout justified (e.g., 4 × 5s = 20s total)
- [ ] Per-attempt vs total timeout clarified
- [ ] Timeout behavior specified (fail vs retry)

### Offline Detection
- [ ] Offline state detection planned (`navigator.onLine`)
- [ ] Offline behavior specified (show banner, disable actions, etc.)
- [ ] Online/offline event listeners planned

### Loading States
- [ ] Loading states defined for all time ranges:
  - 0-1s: Immediate feedback (spinner visible)
  - 1-3s: Basic loading indicator
  - 3-10s: Progress message ("Taking longer than expected...")
  - 10s+: Error state or extended wait message
- [ ] Loading time tracking implemented
- [ ] Progress indicators visible to user

---

## Quality Gate 2: Frontend SSR/UX

**Applies When:** Plan involves:
- SvelteKit pages/routes
- Components that load data
- Client-side only operations
- Progressive enhancement

**Mandatory Checks:**

### SSR Compatibility
- [ ] Network operations only in `onMount` or client-side code
- [ ] Initial loading state present in SSR HTML
- [ ] No server-side `fetch` unless in `+page.server.ts` load function
- [ ] Browser-only APIs guarded (`window`, `document`, `localStorage`)

**Example:**
```typescript
// ✅ SSR-safe
let data = $state(null);
let isLoading = $state(true); // Renders in SSR HTML

onMount(async () => {
  data = await fetch('/api/data');
  isLoading = false;
});
```

### Hydration Transition
- [ ] No flash of incorrect content (FOUC)
- [ ] Loading state visible during hydration
- [ ] Smooth transition from SSR to hydrated state
- [ ] No layout shifts during hydration

### Progressive Enhancement
- [ ] Core content visible without JavaScript (where possible)
- [ ] Graceful degradation if JS disabled
- [ ] Critical actions work without JavaScript (where possible)
- [ ] `<noscript>` fallback provided (if applicable)

### User Feedback
- [ ] User sees feedback within 1 second
- [ ] Loading indicators are visible and clear
- [ ] Error messages are user-friendly and actionable
- [ ] Success states are communicated clearly

---

## Quality Gate 3: Testing Requirements

**Applies When:** All plans (mandatory)

**Mandatory Checks:**

### Test Coverage
- [ ] Unit tests specified (if new functions/utilities)
- [ ] E2E tests specified for user-facing features
- [ ] Test scenarios cover happy path and error cases
- [ ] Performance benchmarks defined (if applicable)

### Error Scenario Testing
- [ ] Success scenario tested
- [ ] Slow network scenario tested (3G simulation)
- [ ] Offline scenario tested
- [ ] Timeout scenario tested
- [ ] Error recovery tested (retry logic)
- [ ] Persistent failure tested (all retries exhausted)

### Browser Compatibility
- [ ] Target browsers specified (Chrome, Firefox, Safari, Edge)
- [ ] Browser-specific issues considered
- [ ] Polyfills identified (if needed)
- [ ] Mobile browsers tested

---

## Quality Gate 4: Deployment Safety

**Applies When:** Plan involves code changes (always)

**Mandatory Checks:**

### Risk Assessment
- [ ] Risk level assessed (low, medium, high)
- [ ] Blast radius identified (which features affected)
- [ ] Rollback plan specified
- [ ] Deployment window identified (low-traffic time)

### Feature Flags
- [ ] Feature flag considered (for high-risk changes)
- [ ] Gradual rollout strategy (if applicable)
- [ ] A/B testing strategy (if applicable)

### Monitoring
- [ ] Success metrics defined
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Performance monitoring (if applicable)
- [ ] User analytics (if applicable)

### Documentation
- [ ] API changes documented
- [ ] User-facing changes documented
- [ ] Team notified of changes
- [ ] Runbook updated (for operations)

---

## Quality Gate 5: Acceptance Criteria

**Applies When:** All plans (mandatory)

**Mandatory Checks:**

### Technical Criteria
- [ ] All technical requirements have acceptance criteria
- [ ] Success metrics are measurable
- [ ] Quality gates are defined (TypeScript, ESLint, tests, etc.)
- [ ] Performance benchmarks specified (if applicable)

### User Story Mapping
- [ ] All user story acceptance criteria addressed
- [ ] Edge cases identified and handled
- [ ] Error scenarios covered
- [ ] Accessibility requirements met

### Definition of Done
- [ ] Code complete
- [ ] Tests passing (unit, integration, E2E)
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] User acceptance testing complete

---

## Quality Gate 6: Dependencies and Prerequisites

**Applies When:** All plans (mandatory)

**Mandatory Checks:**

### External Dependencies
- [ ] Third-party libraries identified and versions specified
- [ ] API dependencies documented
- [ ] Environment variables required
- [ ] Infrastructure requirements (if any)

### Internal Dependencies
- [ ] Dependent tasks/stories identified
- [ ] Blocking issues documented
- [ ] Team coordination needs specified

### Technical Debt
- [ ] Technical debt created is documented
- [ ] Future improvements identified
- [ ] Workarounds are justified

---

## Planning Phase Completion Checklist

Before submitting planning artifacts, verify:

### Artifacts Complete
- [ ] solution-architecture.md created
- [ ] implementation-spec.md created with file-by-file details
- [ ] test-plan.md created with all test scenarios
- [ ] acceptance-criteria.md created with DoD
- [ ] planning-summary.md created for user review

### Quality Gates Passed
- [ ] Network Operations quality gate passed (if applicable)
- [ ] Frontend SSR/UX quality gate passed (if applicable)
- [ ] Testing Requirements quality gate passed
- [ ] Deployment Safety quality gate passed
- [ ] Acceptance Criteria quality gate passed
- [ ] Dependencies quality gate passed

### Reviewability
- [ ] Plan is clear and comprehensive
- [ ] Code examples provided (before/after)
- [ ] Diagrams included (text-based)
- [ ] Rationale explained for key decisions
- [ ] Alternatives considered and documented

### Implementability
- [ ] Implementation agents can execute without additional design decisions
- [ ] File paths and line numbers specified
- [ ] Edge cases and error scenarios covered
- [ ] Testing instructions are clear

---

## When to Skip Quality Gates

Some quality gates may not apply to all tasks. Document exemptions:

**Example:**
```
Quality Gate: Network Operations
Status: SKIPPED
Reason: This task only adds static content (no network operations)
```

**Mandatory Gates (Never Skip):**
- Testing Requirements
- Acceptance Criteria
- Dependencies

**Conditional Gates (Skip if Not Applicable):**
- Network Operations (only if no network calls)
- Frontend SSR/UX (only for backend-only tasks)

---

## References

- frontend-network-resilience skill
- dev-philosophy skill
- dev-code-quality skill
- CLAUDE.md Core Directives

---

**Last Updated:** 2025-11-06
**Mandatory:** YES
**Applies To:** All Plan agent tasks
```

---

### 3. CLAUDE.md Updates

**File:** `CLAUDE.md`

**Section:** Core Directives - ALWAYS REQUIRED

**Add New Subsection:**

```markdown
### Planning Quality Gates Requirement

**MANDATORY:** All Plan agents must reference and apply planning quality gates from `@.claude/skills/planning-quality-gates/` skill.

**When to Use:**
- Every planning phase (TASK-XXX)
- Before completing planning artifacts
- Before presenting plan to user for approval

**Quality Gates:**
1. **Network Operations** - Retry logic, error handling, offline detection
2. **Frontend SSR/UX** - SSR compatibility, hydration, progressive enhancement
3. **Testing Requirements** - Coverage, error scenarios, browsers
4. **Deployment Safety** - Risk assessment, rollback, monitoring
5. **Acceptance Criteria** - Technical criteria, user story mapping, DoD
6. **Dependencies** - External/internal deps, technical debt

**Pattern:**
1. Plan agent designs solution
2. Plan agent references planning-quality-gates skill
3. Plan agent verifies all applicable quality gates
4. Plan agent documents any skipped gates with justification
5. Plan agent delivers comprehensive planning artifacts

**Purpose:**
- Catch architectural gaps early (before implementation)
- Ensure production-ready specifications
- Maintain consistency across all planning phases
- Reduce rework from missing considerations

**Skills to Reference:**
- `@.claude/skills/planning-quality-gates/` (mandatory checklist)
- `@.claude/skills/frontend-network-resilience/` (network operations)
- `@.claude/skills/dev-philosophy/` (core principles)
- `@.claude/skills/dev-code-quality/` (quality standards)
```

---

### 4. Memory MCP Storage

Store the following entities and observations:

**Entity 1: NetworkResiliencePatterns**
```
Type: TechnicalPattern
Observations:
- Always use exponential backoff retry for network operations
- Typical pattern: 4 attempts with 2s, 4s, 8s delays (total ~24s)
- Differentiate error types: offline, timeout, blocked, server_error, unauthorized
- Detect offline state using navigator.onLine
- Provide manual retry button in addition to auto-retry
- Show progress messages after 3 seconds of loading
- Per-attempt timeout typically 5s, total timeout 20-40s
```

**Entity 2: FrontendSSRPatterns**
```
Type: TechnicalPattern
Observations:
- Network operations only in onMount or client-side code
- Initial loading state must be in SSR HTML (no FOUC)
- Loading indicators visible during hydration
- Progressive enhancement where possible
- Guard browser-only APIs (window, document, localStorage)
```

**Entity 3: PlanningQualityGates**
```
Type: SDLCProcess
Observations:
- Plan agents must reference planning-quality-gates skill
- Six mandatory quality gates: Network, SSR/UX, Testing, Deployment, Acceptance, Dependencies
- Document skipped gates with justification
- Verify all gates before delivering planning artifacts
- Located in .claude/skills/planning-quality-gates/SKILL.md
```

---

## Implementation Instructions for devops-infra Subagent

### Task Summary
Create two new skills and update CLAUDE.md with planning quality requirements based on lessons learned from TASK-001 planning review.

### Files to Create

1. `.claude/skills/frontend-network-resilience/SKILL.md`
   - Copy full content from "Contents" section above
   - Ensure proper formatting and code blocks

2. `.claude/skills/planning-quality-gates/SKILL.md`
   - Copy full content from "Contents" section above
   - Ensure proper formatting and checklists

### Files to Update

3. `CLAUDE.md`
   - Locate "### Core Skills - Required for All Subagents" section
   - Add new subsection "### Planning Quality Gates Requirement" AFTER Core Skills section
   - Copy content from "Add New Subsection" above

### Validation

After creating files:
- [ ] Both SKILL.md files have proper frontmatter (---)
- [ ] Code blocks are properly formatted
- [ ] Checklists render correctly (- [ ] format)
- [ ] CLAUDE.md update is in correct location
- [ ] Files are committed with proper message

### Success Criteria

- Two new skills created and properly formatted
- CLAUDE.md updated with new core directive
- All markdown renders correctly
- Commit message follows format: `feat(skills): add planning quality gates and network resilience patterns`

---

**End of Specification**
