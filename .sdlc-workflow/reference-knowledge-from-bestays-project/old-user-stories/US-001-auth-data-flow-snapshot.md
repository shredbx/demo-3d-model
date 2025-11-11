# Authentication Data Flow - System Snapshot

**Story:** US-001 - Login Flow Validation
**Created:** 2025-11-07
**Status:** Current Implementation (as of US-001 completion)
**Purpose:** Reference document showing complete auth flow from credentials to role display

---

## Overview

This document captures the **exact data flow** of our authentication system as implemented and validated in US-001. It serves as a reference point for understanding the current implementation and detecting when changes occur.

**Use this document to:**
- Understand how authentication works today
- Reference when planning changes to auth flow
- Compare against future implementations
- Restore context when returning to auth-related work
- Onboard new developers (human or AI) to auth architecture

**Update this document when:**
- Auth flow changes significantly (Clerk replacement, new middleware, etc.)
- RBAC implementation changes (new roles, permission model changes)
- Backend authentication endpoints change
- Frontend state management pattern changes

---

## Authentication Data Flow: Credentials → Role Display

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: USER INTERACTION (Frontend - Login Page)                      │
└─────────────────────────────────────────────────────────────────────────┘

User visits: http://localhost:5183/login
    ↓
[apps/frontend/src/routes/login/+page.svelte]
    ↓
onMount: Check if Clerk SDK is ready
    ├─ Wait up to 5s for Clerk.load()
    ├─ Set loading state (isLoading = true)
    └─ Mount Clerk sign-in UI component into div

User enters credentials:
    ├─ Email: user.claudecode@bestays.app
    └─ Password: *********

User clicks: "Continue" button
    ↓

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: CLERK AUTHENTICATION (Third-Party)                            │
└─────────────────────────────────────────────────────────────────────────┘

Clerk SDK validates credentials
    ├─ POST https://clerk.com/api/v1/sign-in
    ├─ Validates email/password against Clerk database
    ├─ Generates JWT session token
    └─ Returns: { sessionId, userId, sessionToken }

Clerk updates client state:
    └─ clerk.user = { id, email, ... }

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: AUTH STATE DETECTION (Frontend - Layout Listener)             │
└─────────────────────────────────────────────────────────────────────────┘

[apps/frontend/src/routes/+layout.svelte:59-88]
    ↓
clerk.addListener() triggers on successful auth
    ↓
Listener detects: clerk.user is now populated
    ↓

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: FETCH USER PROFILE (Frontend → Backend)                       │
└─────────────────────────────────────────────────────────────────────────┘

[apps/frontend/src/lib/stores/auth.svelte.ts]
    ↓
authStore.fetchUser() called
    ↓
    ↓ HTTP Request
    ├─ Method: GET
    ├─ URL: http://localhost:8011/api/v1/users/me
    ├─ Headers: { Authorization: "Bearer <clerk-session-token>" }
    └─ Purpose: Get user role and business data

    ↓

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: BACKEND AUTHENTICATION (FastAPI)                              │
└─────────────────────────────────────────────────────────────────────────┘

[apps/server/api/clerk_deps.py] - get_current_user()
    ↓
Step 1: Validate Clerk JWT token
    ├─ Extract token from Authorization header
    ├─ Verify token signature with Clerk API
    ├─ Extract clerk_id from token claims
    └─ If invalid → 401 Unauthorized

Step 2: JIT User Provisioning
    ├─ Check if user exists in database (by clerk_id)
    ├─ If NOT exists:
    │   ├─ Create new user record
    │   ├─ Set role = "user" (default)
    │   └─ Save to PostgreSQL
    └─ If EXISTS:
        └─ Load user from database

Step 3: Return User Data
    ↓
Response (JSON):
{
  "clerk_id": "user_2...",
  "email": "user.claudecode@bestays.app",
  "role": "user",              ← ⭐ ROLE FIELD (source of truth)
  "created_at": "2025-11-05T...",
  "updated_at": "2025-11-06T..."
}

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 6: UPDATE FRONTEND STATE (Auth Store)                            │
└─────────────────────────────────────────────────────────────────────────┘

[apps/frontend/src/lib/stores/auth.svelte.ts]
    ↓
authStore.user = response.data
    ├─ user.clerk_id
    ├─ user.email
    ├─ user.role         ← ⭐ ROLE STORED IN FRONTEND STATE
    └─ ...

authStore reactive state updates (Svelte 5 $derived):
    ├─ isSignedIn = true
    ├─ isAdmin = (user.role === 'admin')
    ├─ isAgent = (user.role === 'agent')
    └─ isUser = (user.role === 'user')

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 7: ROLE-BASED REDIRECT (Redirect Utility)                        │
└─────────────────────────────────────────────────────────────────────────┘

[apps/frontend/src/lib/utils/redirect.ts:43-83]
    ↓
redirectAfterAuth(authStore) called
    ↓
Switch on user.role:
    ├─ "user"  → goto('/')           (home page)
    ├─ "agent" → goto('/dashboard')  (agent dashboard)
    ├─ "admin" → goto('/dashboard')  (admin dashboard)
    └─ unknown → goto('/')           (fallback)

Page navigation occurs
    ↓

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 8: RENDER USER ROLE (UserButton Component)                       │
└─────────────────────────────────────────────────────────────────────────┘

[apps/frontend/src/lib/components/UserButton.svelte]
    ↓
Component subscribes to: authStore.user (Svelte 5 runes)
    ↓
Render role badge in profile dropdown:

{#if authStore.user.role === 'admin'}
  <span class="bg-red-500 text-white px-2 py-0.5 rounded-full">
    Admin
  </span>    ← ⭐ RED BADGE DISPLAYED

{:else if authStore.user.role === 'agent'}
  <span class="bg-blue-500 text-white px-2 py-0.5 rounded-full">
    Agent
  </span>    ← ⭐ BLUE BADGE DISPLAYED

{:else}
  <span class="text-gray-600 capitalize">
    {authStore.user.role}
  </span>    ← PLAIN TEXT FOR REGULAR USERS
{/if}

User sees role indicator in profile dropdown ✅
    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ END: User authenticated with role displayed in UI                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Data Entities

| Entity | Source | Fields | Purpose |
|--------|--------|--------|---------|
| **Clerk User** | Clerk SDK (third-party) | `id`, `email`, `sessionToken` | Third-party auth identity |
| **Backend User** | PostgreSQL (database) | `clerk_id`, `email`, `role`, `created_at` | Business data + RBAC |
| **Auth Store** | Svelte Runes (frontend state) | `user`, `isSignedIn`, `isAdmin`, `isAgent` | Reactive UI state |

---

## Critical Integration Points

### 1. Clerk Token → Backend User
**Location:** `apps/server/api/clerk_deps.py`

**Responsibilities:**
- Validates JWT token from Clerk
- Verifies token signature with Clerk API
- Maps `clerk_id` to database user record
- JIT provisioning if user doesn't exist (creates new user with role="user")

**Security:**
- Every backend request validates JWT
- Token expiration enforced
- RBAC permissions checked at API level

### 2. Backend User → Frontend State
**Location:** `apps/frontend/src/lib/stores/auth.svelte.ts`

**Responsibilities:**
- Fetches user profile after Clerk auth (`GET /api/v1/users/me`)
- Populates `authStore.user` with role and business data
- Enables role-based UI rendering
- Provides reactive `$derived` values for role checks

**Pattern:**
- Svelte 5 runes (`$state`, `$derived`, `$effect`)
- Single source of truth for auth state
- Reactive updates propagate to all components

### 3. Auth Store → UI Components
**Locations:** All Svelte components

**Pattern:**
- Components import and reference `authStore`
- Reactive subscriptions via Svelte 5 runes
- Automatic re-rendering on state changes
- No manual subscription/unsubscription needed

**Example:**
```svelte
<script>
  import { authStore } from '$lib/stores/auth.svelte';
</script>

{#if authStore.isAdmin}
  <AdminPanel />
{/if}
```

---

## Current Implementation Files

| File | Role | Pattern | Notes |
|------|------|---------|-------|
| `apps/frontend/src/routes/login/+page.svelte` | Login UI | Svelte 5 page | Mounts Clerk sign-in component |
| `apps/frontend/src/routes/+layout.svelte` | Global Clerk init | Svelte 5 layout | Listens for auth state changes |
| `apps/frontend/src/lib/clerk.ts` | Clerk SDK singleton | Singleton | Initializes Clerk globally |
| `apps/frontend/src/lib/stores/auth.svelte.ts` | Auth state | Svelte 5 runes | Single source of truth for auth |
| `apps/frontend/src/lib/utils/redirect.ts` | Role-based routing | Utility | Redirects based on user role |
| `apps/frontend/src/lib/components/UserButton.svelte` | User dropdown | Svelte 5 component | Displays role badge |
| `apps/server/api/clerk_deps.py` | Token validation | FastAPI dependency | JWT validation + JIT provisioning |
| `apps/server/models/user.py` | User model | SQLAlchemy | Database schema |
| `apps/server/services/user_service.py` | User CRUD | Service layer | Business logic |

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Login page load time** | ~2.5s | Includes Clerk SDK loading from CDN |
| **Clerk SDK overhead** | 200-500ms | Industry standard for third-party auth |
| **Backend auth call** | <100ms | JWT validation + database lookup |
| **Total auth flow** | ~3s | From "click login" to "role displayed" |

**Bottlenecks:**
- Clerk SDK load from CDN (unavoidable, third-party)
- First-time JIT provisioning (creates database user)

**Optimizations applied:**
- Clerk loaded globally in +layout.svelte (loaded once)
- Auth state cached in authStore (no repeated backend calls)
- Database queries use indexes on `clerk_id`

---

## Security Model

### Authentication
- **Provider:** Clerk (third-party)
- **Token type:** JWT
- **Token validation:** Every backend request
- **Session management:** Clerk handles refresh tokens

### Authorization (RBAC)
- **Roles:** `user`, `agent`, `admin`
- **Enforcement:** Backend API level (FastAPI dependencies)
- **Frontend:** UI hints only (not security boundary)

### JIT Provisioning
- **First login:** User auto-created in database
- **Default role:** `user` (safe default)
- **First admin:** Bootstrap script or manual database update

### Trust Model
- **Backend trusts:** Clerk JWT signature (after validation)
- **Frontend trusts:** Backend `/api/v1/users/me` response
- **UI trusts:** authStore.user (reactive state)

**Security boundaries:**
- Frontend → Backend: JWT token in Authorization header
- Backend → Database: Role-based permissions enforced
- Backend → Clerk: API key authentication

---

## Known Issues & Trade-offs

### Issue 1: Double Initialization (Low Severity)
**Location:** `+layout.svelte` + `login/+page.svelte`

**Problem:** Both files initialize Clerk, potential for conflicts.

**Status:** Low priority, works correctly but redundant.

**Future improvement:** Remove login page initialization, rely on layout only.

### Issue 2: Client-Side Redirect Aborts
**Location:** Protected route navigation

**Problem:** Playwright sees `ERR_ABORTED` when auth guard redirects.

**Status:** Expected behavior, handled in E2E tests with `.catch()`.

**Not a bug:** SvelteKit's client-side routing pattern.

### Issue 3: Clerk UI Selector Changes
**Location:** E2E tests (`login.spec.ts`)

**Problem:** Clerk component structure changed, tests use outdated selectors.

**Status:** Tests updated to handle visible elements only (filter `aria-hidden="true"`).

**Mitigation:** Use Playwright codegen to inspect actual Clerk UI structure.

### Trade-off 1: Vendor Lock-in (Clerk)
**Decision:** Use Clerk for authentication.

**Pros:**
- Fast development (no auth implementation needed)
- Security handled by experts
- Built-in MFA, social auth, etc.

**Cons:**
- Vendor lock-in (migration cost if switching providers)
- Third-party dependency (SDK load time, downtime risk)
- Cost scales with users

**When to revisit:** If Clerk pricing becomes prohibitive OR we need custom auth flows Clerk doesn't support.

### Trade-off 2: JIT Provisioning
**Decision:** Auto-create users on first login (role="user").

**Pros:**
- No pre-registration needed
- Seamless onboarding
- Clerk handles user management

**Cons:**
- Cannot pre-assign roles before first login
- First admin must be bootstrapped manually
- Race conditions if same user logs in twice simultaneously

**When to revisit:** If we need invitation-based signup with pre-assigned roles.

### Trade-off 3: Frontend Role Display
**Decision:** Show role badges in UserButton dropdown.

**Pros:**
- Clear visual indicator for testing
- Easy to verify RBAC is working
- No separate admin panel needed for basic role check

**Cons:**
- Exposes role to user (may be undesirable in production)
- Users may question why they're "user" vs "admin"

**When to revisit:** If we want to hide role from end users (keep for internal tools only).

---

## Testing Strategy

### E2E Tests (Playwright)
**File:** `apps/frontend/tests/e2e/login.spec.ts`

**Coverage:**
- Successful login with valid credentials
- Invalid credentials error handling
- Protected route access control
- Session persistence across reload/navigation
- Logout functionality
- Error handling (Clerk failure, backend down)
- Performance (page load <2.5s)

**Test Accounts:**
- `user.claudecode@bestays.app` → role: `user`
- `agent.claudecode@bestays.app` → role: `agent`
- `admin.claudecode@bestays.app` → role: `admin`

### Backend Tests (pytest)
**File:** `apps/server/tests/test_clerk_auth.py`

**Coverage:** 95%

**Test scenarios:**
- JWT validation success/failure
- JIT user provisioning
- RBAC permission checks
- Invalid token handling
- Missing token handling

### Manual Testing
**Browsers:** Chrome, Firefox, Safari

**Scenarios:**
- Login with each role
- Verify redirect destinations
- Check role badge display
- Test error states (network offline, backend down)

---

## Change Detection

**If you're reading this document and the implementation has changed, update this snapshot:**

1. **Create new snapshot:** `US-XXX-auth-data-flow-snapshot.md` (with new story ID)
2. **Reference old snapshot:** Link to this document for comparison
3. **Document changes:** What changed, why, and trade-offs
4. **Update Memory MCP:** Store new auth flow pattern for future sessions

**Signs the implementation has changed:**
- New auth provider (not Clerk)
- Different JWT validation approach
- RBAC model changes (new roles, permissions)
- Auth state management changes (not Svelte runes)
- Different redirect logic

**Preservation strategy:**
- Keep old snapshots (git history preservation)
- Create new snapshot per major auth change
- Use semantic versioning in snapshot filenames if helpful

---

## Documentation Sources

This snapshot was generated from SDLC documentation (not source code inspection):

1. **User Story:** `.sdlc-workflow/stories/auth/US-001-login-flow-validation.md`
2. **Task Reports:**
   - `.sdlc-workflow/tasks/US-001-TASK-001-login-e2e-tests/subagent-report-frontend.md`
   - `.sdlc-workflow/tasks/US-001-TASK-003-role-badge-indicator/README.md`
3. **Git Commits:**
   - `38eac7a` - Complete login flow validation
   - `c25150c` - Fix Clerk mounting race condition
   - `bd06960` - Implement RBAC components
   - `98bb438` - Resolve Clerk button interaction issues

**Methodology:** Context restoration from SDLC docs only (demonstrates Memory Print Chain).

---

## Related Documentation

- **User Story:** `US-001-login-flow-validation.md` (acceptance criteria, testing requirements)
- **Architecture:** (future) `.claude/docs/architecture/auth-flow.md`
- **Integration Spec:** (future) `.claude/docs/integrations/clerk-authentication.md`
- **RBAC Story:** `US-001B-rbac-and-audit-logging.md` (extended RBAC implementation)

---

## Revision History

| Date | Changes | Reason |
|------|---------|--------|
| 2025-11-07 | Initial snapshot created | Preserve US-001 implementation context |

---

**Next update:** When auth flow changes significantly (US-XXX implementation).
