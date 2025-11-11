# Svelte 5 Best Practices for External SDK Mounting

**Date:** 2025-11-06  
**Phase:** RESEARCH  
**Task:** TASK-001 (US-001: Login Flow Validation)  
**Analyst:** File Search Specialist

---

## Executive Summary

This document analyzes Svelte 5 rune patterns for mounting external SDK UIs (like Clerk), drawing from the existing codebase and Svelte 5 best practices.

**Key Finding:** For external SDK mounting, **imperative onMount** is simpler and more predictable than **reactive $effect** when dealing with one-time initialization.

---

## Svelte 5 Runes Overview

### Core Reactive Primitives

| Rune | Purpose | Use Case | Example |
|------|---------|----------|---------|
| `$state` | Mutable reactive state | Component state | `let count = $state(0)` |
| `$derived` | Computed value | Derived state | `let double = $derived(count * 2)` |
| `$effect` | Side effect | React to changes | `$effect(() => console.log(count))` |
| `$effect.pre` | Pre-render effect | Before DOM update | `$effect.pre(() => ...)` |
| `$props` | Component props | Type-safe props | `let { name }: Props = $props()` |

---

## $effect vs onMount: When to Use Each

### onMount: Imperative, One-Time Setup

**Use when:**
- ✅ External SDK initialization (Clerk, Stripe, Google Maps)
- ✅ DOM manipulation that happens once
- ✅ Event listener setup
- ✅ Async data fetching on mount

**Characteristics:**
- Runs **once** when component mounts
- Explicit control flow
- Predictable timing
- Returns cleanup function (runs on unmount only)

**Example from Codebase:**

`apps/frontend/src/routes/clerk-debug/+page.svelte` (lines 12-42)

```typescript
onMount(async () => {
  // Check environment
  envKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || 'NOT SET';

  if (!clerk) {
    status = '❌ Clerk SDK not initialized';
    return;
  }

  clerkAvailable = true;

  try {
    await clerk.load(); // ✅ One-time async operation
    clerkLoaded = true;
    clerkUser = clerk.user;
    
    status = clerk.user 
      ? `✅ Clerk loaded successfully` 
      : '✅ Clerk loaded successfully (Not signed in)';
  } catch (err: any) {
    clerkError = err.message;
    status = `❌ Clerk failed to load: ${clerkError}`;
  }
});
```

**Why this works:**
- No reactive dependencies (doesn't re-run)
- Clear async flow (await)
- Simple error handling
- Predictable behavior

---

### $effect: Reactive Side Effects

**Use when:**
- ✅ Reacting to state changes (not initialization)
- ✅ Syncing external state with component state
- ✅ DOM updates based on reactive data
- ✅ Auto-scroll when data changes

**Characteristics:**
- Runs **every time** dependencies change
- Automatic dependency tracking
- Cleanup runs before re-run or on unmount
- Can trigger multiple times

**Example from Codebase:**

`apps/frontend/src/lib/components/chat/MessageList.svelte` (lines 69-74)

```typescript
$effect(() => {
  // Re-run when messages length changes
  if (messages.length > 0) {
    scrollToBottom(); // ✅ Idempotent side effect
  }
});
```

**Why this works:**
- Idempotent operation (safe to run multiple times)
- Single dependency (messages.length)
- No async operations
- No complex state transitions

---

## Anti-Pattern: $effect for One-Time External SDK Mounting

### Current Login Page (Anti-Pattern)

**Location:** `apps/frontend/src/routes/login/+page.svelte` (lines 134-162)

```typescript
// ❌ ANTI-PATTERN: Too many dependencies for one-time operation
$effect(() => {
  if (signInDiv && mounted && clerk && !isLoading && !error) {
    // Mount Clerk UI (should only happen once)
    clerk.mountSignIn(signInDiv, { signUpUrl: '/signup' });
    
    return () => {
      clerk.unmountSignIn(signInDiv);
    };
  }
});
```

**Problems:**

1. **5 Reactive Dependencies:**
   - Any change to any dependency re-triggers
   - Mounting should be one-time, not reactive

2. **Non-Idempotent Operation:**
   - `mountSignIn()` creates DOM elements, event listeners
   - Calling multiple times can cause issues
   - Cleanup + remount = lost user input

3. **Complex Guard Logic:**
   - Hard to reason about when mount actually happens
   - Multiple states can change in unpredictable order

4. **Async Confusion:**
   - onMount is async, $effect is sync
   - Dependencies change asynchronously
   - Timing is unpredictable

---

## Recommended Pattern: Imperative onMount

### Pattern A: Direct Mounting After Load

**Best for:** Simple cases where SDK is ready immediately

```typescript
<script lang="ts">
import { onMount } from 'svelte';
import { clerk } from '$lib/clerk';

let signInDiv = $state<HTMLDivElement | null>(null);
let isLoading = $state(true);
let error = $state<string | null>(null);

onMount(async () => {
  try {
    // Wait for clerk to be ready (assume layout initialized it)
    if (!clerk || !clerk.loaded) {
      error = 'Authentication system not available';
      isLoading = false;
      return;
    }

    // Check if already signed in
    if (clerk.user) {
      await redirectAfterAuth();
      return;
    }

    // All checks passed, ready to mount
    isLoading = false;

    // Wait for DOM to be ready
    await tick();

    // Direct imperative mount - no reactivity needed
    if (signInDiv) {
      clerk.mountSignIn(signInDiv, { signUpUrl: '/signup' });
    } else {
      error = 'Unable to display login form';
    }
  } catch (err) {
    error = 'Failed to initialize authentication';
    console.error(err);
  } finally {
    isLoading = false;
  }

  // Cleanup on unmount
  return () => {
    if (signInDiv) {
      clerk.unmountSignIn(signInDiv);
    }
  };
});
</script>
```

**Advantages:**
- ✅ Runs once
- ✅ Explicit async flow
- ✅ Clear error handling
- ✅ No race conditions with reactive dependencies
- ✅ Cleanup guaranteed on unmount only

---

### Pattern B: Imperative Mount with Reactive Checks

**Best for:** When you need to react to state changes but mount only once

```typescript
<script lang="ts">
import { onMount, tick } from 'svelte';
import { clerk } from '$lib/clerk';

let signInDiv = $state<HTMLDivElement | null>(null);
let isMounted = $state(false); // Track if already mounted

async function mountClerkUI() {
  if (isMounted) return; // Guard against double-mount
  
  await tick(); // Ensure DOM ready
  
  if (signInDiv && clerk && clerk.loaded) {
    clerk.mountSignIn(signInDiv, { signUpUrl: '/signup' });
    isMounted = true;
  }
}

onMount(async () => {
  // Wait for clerk
  await ensureClerkReady();
  
  // Mount immediately
  await mountClerkUI();
  
  // Cleanup
  return () => {
    if (signInDiv && isMounted) {
      clerk.unmountSignIn(signInDiv);
      isMounted = false;
    }
  };
});

// Optional: React to signInDiv binding if needed
$effect(() => {
  if (signInDiv && !isMounted) {
    mountClerkUI(); // Safe because of isMounted guard
  }
});
</script>
```

**Advantages:**
- ✅ Primary mount in onMount (predictable)
- ✅ Fallback $effect for late DOM binding (rare edge case)
- ✅ Double-mount guard
- ✅ Clear separation of concerns

---

### Pattern C: State Machine Approach

**Best for:** Complex flows with multiple states

```typescript
<script lang="ts">
import { onMount } from 'svelte';
import { clerk } from '$lib/clerk';

type MountState = 
  | { status: 'initializing' }
  | { status: 'ready' }
  | { status: 'mounted' }
  | { status: 'error', message: string };

let mountState = $state<MountState>({ status: 'initializing' });
let signInDiv = $state<HTMLDivElement | null>(null);

onMount(async () => {
  try {
    // Phase 1: Check prerequisites
    if (!clerk?.loaded) {
      mountState = { status: 'error', message: 'SDK not ready' };
      return;
    }

    // Phase 2: Check auth state
    if (clerk.user) {
      await redirectAfterAuth();
      return;
    }

    // Phase 3: Ready to mount
    mountState = { status: 'ready' };
    await tick();

    // Phase 4: Mount
    if (signInDiv) {
      clerk.mountSignIn(signInDiv, { signUpUrl: '/signup' });
      mountState = { status: 'mounted' };
    }
  } catch (err) {
    mountState = { status: 'error', message: String(err) };
  }

  // Cleanup
  return () => {
    if (signInDiv && mountState.status === 'mounted') {
      clerk.unmountSignIn(signInDiv);
    }
  };
});
</script>

{#if mountState.status === 'initializing'}
  <LoadingSpinner />
{:else if mountState.status === 'error'}
  <ErrorDisplay message={mountState.message} />
{:else if mountState.status === 'ready' || mountState.status === 'mounted'}
  <div bind:this={signInDiv}></div>
{/if}
```

**Advantages:**
- ✅ Explicit state transitions
- ✅ Type-safe states (discriminated union)
- ✅ Easy to test
- ✅ Clear UI mapping to states

---

## Examples from Codebase

### Good Example: MessageList Auto-Scroll

**Location:** `apps/frontend/src/lib/components/chat/MessageList.svelte` (lines 69-74)

```typescript
$effect(() => {
  if (messages.length > 0) {
    scrollToBottom(); // ✅ Idempotent, safe to run multiple times
  }
});
```

**Why it's good:**
- Appropriate use of $effect (reacting to data changes)
- Idempotent operation
- Single dependency
- Simple logic

---

### Good Example: Clerk Debug Tool

**Location:** `apps/frontend/src/routes/clerk-debug/+page.svelte` (lines 12-42)

```typescript
onMount(async () => {
  // ✅ One-time initialization
  // ✅ Clear async flow
  // ✅ No reactive dependencies
  
  if (!clerk) {
    status = '❌ Clerk SDK not initialized';
    return;
  }

  try {
    await clerk.load();
    clerkLoaded = true;
    clerkUser = clerk.user;
    status = '✅ Clerk loaded successfully';
  } catch (err: any) {
    clerkError = err.message;
    status = `❌ Clerk failed to load`;
  }
});
```

**Why it's good:**
- Simple, straightforward onMount
- No unnecessary reactive logic
- Clear error handling
- Appropriate for one-time SDK load

---

### Bad Example: Login Page (Current)

**Location:** `apps/frontend/src/routes/login/+page.svelte` (lines 50-162)

**Problems:**
- ❌ Complex onMount with timeout workaround
- ❌ $effect with 5 dependencies for one-time operation
- ❌ Redundant mounted flag
- ❌ Silent error handling

**Should be:** Simple imperative onMount (Pattern A or B)

---

## Svelte 5 Documentation Patterns

### Official Guidance (Inferred from Runes)

**$effect is for reactive side effects, not initialization:**

```typescript
// ❌ WRONG: Using $effect for one-time setup
$effect(() => {
  if (element) {
    thirdPartyLib.mount(element); // Runs every time element changes!
  }
});

// ✅ RIGHT: Using onMount for one-time setup
onMount(() => {
  if (element) {
    thirdPartyLib.mount(element); // Runs once
  }
  
  return () => thirdPartyLib.unmount(element);
});
```

---

## Decision Matrix: $effect vs onMount

| Criteria | Use onMount | Use $effect |
|----------|-------------|-------------|
| **Operation runs once** | ✅ YES | ❌ NO |
| **Reacts to data changes** | ❌ NO | ✅ YES |
| **External SDK mounting** | ✅ YES | ❌ NO |
| **Idempotent operation** | Either | ✅ YES |
| **Non-idempotent operation** | ✅ YES | ❌ NO |
| **Async initialization** | ✅ YES | ⚠️ Possible but complex |
| **DOM ready check** | ✅ YES | ⚠️ Possible |
| **Cleanup on unmount only** | ✅ YES | ❌ NO (runs on re-trigger too) |

---

## Recommendations for Login Page

### Primary Recommendation: Pattern A (Simple Imperative)

**Why:**
1. Login form mounting is a **one-time operation**
2. Clerk SDK initialization is **async**
3. No need to **react to state changes** after mount
4. Simpler = fewer bugs

**Implementation:**
- Remove $effect entirely
- Move mounting logic into onMount
- Trust layout initialization (remove duplicate load)
- Remove timeout workaround
- Remove mounted flag

---

### Alternative: Pattern C (State Machine)

**Why:**
1. If we want **explicit state management**
2. Clear mapping between states and UI
3. Easier to test
4. Better error handling

**Trade-off:** More code, but more maintainable for complex flows

---

## Anti-Patterns to Avoid

### 1. Too Many Dependencies in $effect

```typescript
// ❌ ANTI-PATTERN
$effect(() => {
  if (a && b && c && !d && !e) { // 5 dependencies!
    doSomething();
  }
});
```

**Solution:** Derive a single computed value or use imperative logic

```typescript
// ✅ BETTER
const shouldDoSomething = $derived(a && b && c && !d && !e);

$effect(() => {
  if (shouldDoSomething) { // 1 dependency
    doSomething();
  }
});

// ✅ OR: Don't use $effect at all if one-time
onMount(() => {
  if (shouldDoSomething) {
    doSomething();
  }
});
```

---

### 2. Non-Idempotent Operations in $effect

```typescript
// ❌ ANTI-PATTERN: Event listener added multiple times
$effect(() => {
  element.addEventListener('click', handler);
});
```

**Solution:** Use onMount with cleanup

```typescript
// ✅ CORRECT
onMount(() => {
  element.addEventListener('click', handler);
  
  return () => {
    element.removeEventListener('click', handler);
  };
});
```

---

### 3. Async Operations in $effect

```typescript
// ❌ ANTI-PATTERN: Async in $effect
$effect(() => {
  // This won't work as expected
  async function load() {
    const data = await fetch('/api');
    state = data;
  }
  load();
});
```

**Solution:** Use onMount or derived state with separate loading trigger

```typescript
// ✅ BETTER
onMount(async () => {
  const data = await fetch('/api');
  state = data;
});
```

---

### 4. Redundant State Flags

```typescript
// ❌ ANTI-PATTERN: Unnecessary mounted flag
let mounted = $state(false);

onMount(() => {
  mounted = true; // Why? onMount already tells us we're mounted!
});

$effect(() => {
  if (mounted) {
    // Do something
  }
});
```

**Solution:** Just use onMount

```typescript
// ✅ BETTER
onMount(() => {
  // Do something directly
});
```

---

## Summary of Patterns

| Pattern | Complexity | Best For | Pros | Cons |
|---------|------------|----------|------|------|
| **Simple Imperative** | Low | Simple SDK mounting | Predictable, easy | May need tick() |
| **Imperative + Reactive** | Medium | Edge cases with late DOM | Handles edge cases | More complex |
| **State Machine** | High | Complex flows | Type-safe, testable | More code |

**For Login Page:** **Simple Imperative** is sufficient.

---

## Next Steps

The **findings-summary.md** document will synthesize this research with the race condition analysis to provide a complete implementation recommendation.

---

**End of Analysis**
