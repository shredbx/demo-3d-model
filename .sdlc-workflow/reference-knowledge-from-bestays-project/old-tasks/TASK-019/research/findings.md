# TASK-019 Research Findings - Login & Logout Flow (US-028)

**Research Date:** November 10, 2025  
**Task:** US-028 - Login & Logout Flow Implementation  
**Status:** Complete

---

## 1. EXISTING CLERK INTEGRATION

### 1.1 Clerk Configuration
**Location:** `/apps/frontend/src/lib/clerk.ts`

**Current State:**
- Clerk SDK is initialized as a singleton
- Publishable key loaded from `VITE_CLERK_PUBLISHABLE_KEY` environment variable
- Provides `initializeClerk()`, `getClerkToken()`, `isSignedIn()`, and `getCurrentClerkUser()` helper functions
- Uses `@clerk/clerk-js` v5.102.1

**Key Functions:**
```typescript
export async function initializeClerk(): Promise<void>
export async function getClerkToken(): Promise<string | null>
export function isSignedIn(): boolean
export function getCurrentClerkUser()
```

**Integration Points:**
- Called from root layout (`+layout.svelte`)
- Provides token for API requests
- Handles session state

---

## 2. AUTHENTICATION FLOW - CURRENT IMPLEMENTATION

### 2.1 Root Layout (`+layout.svelte`)
**Location:** `/apps/frontend/src/routes/+layout.svelte`

**Architecture:**
- Initializes Clerk on app mount
- Sets up listener for Clerk auth state changes
- Syncs user state with backend (fetches role via `GET /api/v1/users/me`)
- Handles role-based redirects on login/signup pages

**Key Pattern:** Provider Pattern + Initialization Hook
- Uses TanStack Query for data fetching
- Syncs Clerk auth state with local auth store
- Provides global chat interface

**Auth State Synchronization:**
```typescript
onMount(async () => {
  await initializeClerk();
  clerk.addListener(async ({ user: clerkUser }) => {
    if (clerkUser) {
      await authStore.fetchUser();  // Fetch role from backend
      if (currentPath === '/login' || currentPath === '/signup') {
        await redirectAfterAuth();   // Role-based redirect
      }
    } else {
      authStore.clearUser();         // Clear on logout
    }
  });
  await authStore.initialize();      // Check existing session
});
```

### 2.2 Auth Store (`auth.svelte.ts`)
**Location:** `/apps/frontend/src/lib/stores/auth.svelte.ts`

**Pattern:** Svelte 5 Runes + Reactive State

**State Management:**
```typescript
user: User | null
isLoading: boolean
error: string | null
isSignedIn: boolean (derived from user)
isAdmin: boolean (derived from user.role === 'admin')
isAgent: boolean (derived from user.role === 'agent')
isUser: boolean (derived from user.role === 'user')
```

**Key Methods:**
- `fetchUser()` - Calls `GET /api/v1/users/me` to get user role from backend
- `clearUser()` - Clears user state (called on logout)
- `initialize()` - Checks if user is signed in and fetches profile

**Important:** Does NOT handle Clerk logout - Clerk SDK handles that directly

### 2.3 Login Page (`/login/+page.svelte`)
**Location:** `/apps/frontend/src/routes/login/+page.svelte`

**Architecture:**
- Uses Clerk's pre-built sign-in component via `clerk.mountSignIn()`
- Implements sophisticated retry logic with exponential backoff (4 attempts max)
- Handles network resilience and offline detection
- Shows loading states with retry countdown

**Network Resilience Features:**
- Offline detection (fast fail if no internet)
- Exponential backoff retry: 0s, 2s, 4s, 8s delays
- Timeout handling: 5s per attempt, 24s total max
- Structured error logging (classified error types: offline, timeout, sdk_not_available, mount_failed, server_error)
- User-friendly error messages for each error type

**Key Pattern:** Imperative onMount + Exponential Backoff Retry
- Direct Clerk SDK mounting (not reactive)
- Auto-redirect if already signed in
- Handles mounting failures gracefully

**Error Types:**
```typescript
type NetworkErrorType =
  | 'offline'           // No internet connection
  | 'timeout'           // All retry attempts exhausted
  | 'sdk_not_available' // Clerk script didn't load (blocked or CDN down)
  | 'mount_failed'      // SDK ready but mounting failed
  | 'server_error'      // Backend API failure (after auth)
```

### 2.4 UserButton Component (`UserButton.svelte`)
**Location:** `/apps/frontend/src/lib/components/UserButton.svelte`

**Purpose:**
- Displays user profile and logout button via `clerk.mountUserButton()`
- Shows user email and role badge (from backend)
- Handles logout redirection to `/login`

**Key Code:**
```typescript
clerk.mountUserButton(userButtonDiv, {
  afterSignOutUrl: '/login',
});
```

---

## 3. ROLE-BASED REDIRECT LOGIC

### 3.1 Redirect Utility (`redirect.ts`)
**Location:** `/apps/frontend/src/lib/utils/redirect.ts`

**Pattern:** Role-Based Navigation

**Current Redirect Mapping:**
```typescript
if (user.role === 'user') {
  goto('/');                    // Regular users → homepage
} else if (user.role === 'agent' || user.role === 'admin') {
  goto('/dashboard');           // Agents & admins → dashboard
}
```

**Error Handling:**
- Throws detailed error messages based on error type:
  - 401 → "Authentication failed"
  - 404 → "User profile not found"
  - Network → "Unable to connect to server"

**Integration Points:**
- Called from login page on successful auth
- Called from layout listener when user signs in
- Called from navigation guards (if implemented)

---

## 4. BACKEND AUTHENTICATION

### 4.1 User Endpoints (`endpoints/users.py`)
**Location:** `/apps/server/src/server/api/v1/endpoints/users.py`

**Endpoints:**
- `GET /api/v1/users/me` - Get current authenticated user (Clerk-based)
- `GET /api/v1/users` - List users (admin-only)
- `GET /api/v1/users/{clerk_user_id}` - Get user by ID (admin-only)
- `PATCH /api/v1/users/{clerk_user_id}/role` - Update role (admin-only)
- `DELETE /api/v1/users/{clerk_user_id}` - Delete user (admin-only)

**Key Pattern:** REST + Role-Based Access Control

**Authentication Dependency:**
```python
@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_clerk_user),
) -> UserResponse:
```

**Security Features:**
- Prevents self-demotion from admin role
- Prevents self-deletion
- Returns 403 Forbidden for non-admin access to admin endpoints
- Returns 404 for non-existent users

### 4.2 User Model & Schema
**Location:** `/apps/server/src/server/models/user.py` and `/apps/server/src/server/schemas/user.py`

**User Schema:**
```python
class UserResponse:
    id: int
    clerk_user_id: str
    email: str
    role: 'admin' | 'agent' | 'user'
    created_at: str
    updated_at: str
```

**Roles:**
- `admin` - Full admin access to dashboards and user management
- `agent` - Agent/property manager access
- `user` - Regular customer access

---

## 5. PROTECTED ROUTES

### 5.1 Dashboard Layout
**Location:** `/apps/frontend/src/routes/dashboard/+layout.svelte`

**Current State:**
- Simple wrapper using `DashboardLayout` component
- NO auth guard currently implemented (needs to be added)

**Missing:** Route protection logic to redirect unauthenticated users to `/login`

### 5.2 Dashboard Routes
**Location:** `/apps/frontend/src/routes/dashboard/`

**Routes:**
- `/dashboard` - Dashboard home
- `/dashboard/ai-agent` - AI chat configuration
- `/dashboard/faqs` - FAQ management
- `/dashboard/faqs/[id]` - FAQ detail
- `/dashboard/faqs/new` - FAQ creation

**Protection Requirement:** All dashboard routes must be guarded (NOT currently protected)

---

## 6. E2E TESTS - EXISTING

### 6.1 Auth Login/Logout Test
**Location:** `/apps/frontend/tests/e2e/auth-login-logout.spec.ts`

**Comprehensive Coverage:**
- **Test 1:** Login Page Display (page load, component load, form fields, back link)
- **Test 2:** Login Success (user, admin, agent roles with multi-product)
- **Test 3:** Login Failure (invalid credentials, form persistence, button state)
- **Test 4:** Logout Flow (logout success, session clear, button visibility)
- **Test 5:** Protected Routes (redirect to login, authenticated access, redirect params)
- **Test 6:** Session Persistence (reload, navigation across pages)
- **Test 7:** Multi-Product Isolation (separate sessions, independent logout)

**Test Credentials (Bestays):**
- User: `user.claudecode@bestays.app` / `9kB*k926O8):`
- Admin: `admin.claudecode@bestays.app` / `rHe/997?lo&l`
- Agent: `agent.claudecode@bestays.app` / `y>1T;)5s!X1X`

**Test Credentials (Real Estate):**
- User: `user.claudecode@realestate.dev` / `y>1T_)5h!X1X`
- Admin: `admin.claudecode@realestate.dev` / `rHe/997?lo&l`
- Agent: `agent.claudecode@realestate.dev` / `y>1T;)5s!X1X`

**Helper Functions:**
- `waitForClerkComponent()` - Waits for Clerk UI to load (handles loading state)
- `signInWithClerk()` - Two-step sign-in (email → password)
- `signOut()` - Clicks user button and signs out
- `isAuthenticated()` - Checks if navigating to dashboard redirects to login
- `clearSession()` - Clears cookies and storage between tests

**Key Pattern:** Page Object Model with async helpers

---

## 7. CLERK PRODUCTS CONFIGURATION

### 7.1 Multi-Product Setup
**Bestays Instance:**
- Instance ID: `sacred-mayfly-55.clerk.accounts.dev`
- Publishable Key: `pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk`
- Secret Key: `sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit`

**Real Estate Instance:**
- Instance ID: `pleasant-gnu-25.clerk.accounts.dev`
- Publishable Key: `pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ`
- Secret Key: `sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS`

**Separation Strategy:**
- Each product has independent Clerk instance
- Different publishable keys in .env per product
- Separate sessions (not shared between products)

---

## 8. DEPENDENCIES & INTEGRATION POINTS

### 8.1 Frontend Dependencies
```json
{
  "@clerk/clerk-js": "^5.102.1",
  "@tanstack/svelte-query": "^5",
  "svelte": "^5"
}
```

### 8.2 Backend Dependencies
```python
# Clerk validation (if needed)
# Currently using custom JWT tokens for internal auth
# Backend validates Clerk token via get_clerk_user dependency
```

### 8.3 Environment Variables
**Required:**
```
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
VITE_PRODUCT_NAME=Bestays
PUBLIC_PRODUCT_NAME=Bestays
```

---

## 9. TESTING PATTERNS & COVERAGE

### 9.1 Backend Tests
**Location:** `/apps/server/tests/api/v1/`

**Test Files:**
- `test_auth.py` - Login, logout, change password endpoints
- `test_clerk_auth.py` - Clerk token validation, JIT provisioning
- `test_users.py` - User endpoints (list, get, update, delete)

**Coverage Targets:**
- Auth endpoints: 95%+ (security-critical)
- User endpoints: 85%

**Key Test Scenarios:**
- Valid/invalid credentials
- Suspended user handling
- Token expiry
- Role-based access control
- Self-demotion prevention

### 9.2 Frontend Tests
**E2E Test Coverage:**
- Login page display and interactions
- Successful login with different roles
- Failed login error handling
- Logout flow and session clearing
- Protected route redirection
- Session persistence across navigations

---

## 10. CONSTRAINTS & GOTCHAS DISCOVERED

### 10.1 Clerk-Specific Constraints
1. **SDK Mounting is Imperative** - Must use `mountSignIn()` and `mountUserButton()`, not reactive patterns
2. **Async Initialization** - Clerk SDK loads asynchronously; code must wait for `clerk.loaded === true`
3. **No Double-Init** - Calling `clerk.load()` twice causes issues; trust layout initialization
4. **Component Cleanup** - Must unmount Clerk components on component destroy to prevent memory leaks
5. **Ad Blockers** - Can block Clerk SDK; login page handles gracefully with error messaging

### 10.2 Architecture Constraints
1. **Separate Sessions per Product** - Each Clerk instance has independent sessions (not shared)
2. **Backend Role Authority** - Role always comes from backend (`GET /api/v1/users/me`), not Clerk
3. **No Manual Token Management** - Clerk auto-manages tokens; never manually parse or refresh
4. **Redirect After Auth** - User should be redirected immediately after sign-in success

### 10.3 Missing/Partial Implementation
1. **Protected Route Guards** - No SvelteKit `load()` functions to guard dashboard routes
2. **Logout Redirect** - UserButton already set to redirect to `/login` after signout
3. **Session Timeout** - No explicit session timeout handling (relies on Clerk's token expiry)
4. **Remember Me** - Not implemented (can be added via Clerk persistence options)

### 10.4 Testing Considerations
1. **Real Clerk Test Accounts** - Tests use actual Clerk test environment (not mocked)
2. **Timing Issues** - Clerk component mounting is slow; tests use generous timeouts (5-30s)
3. **Network Dependency** - Tests require internet connection to reach Clerk CDN
4. **Product Isolation** - Tests run sequentially per product to avoid session conflicts

---

## 11. RECOMMENDATIONS FOR IMPLEMENTATION

### 11.1 Priority 1 - Core Auth Flow (Already Implemented)
✅ Clerk SDK initialization and mounting
✅ Login page with Clerk sign-in component
✅ Logout via UserButton
✅ Role-based redirects
✅ Session persistence
✅ Network resilience (retry logic, offline detection)

### 11.2 Priority 2 - Protected Routes (TO DO)
- Add SvelteKit `load()` functions to guard `/dashboard/*` routes
- Redirect to `/login` if not authenticated
- Preserve redirect destination for post-login navigation
- Show loading UI while checking auth state

### 11.3 Priority 3 - Error Handling & UX
- Already implemented: Structured error logging and user-friendly messages
- Retry UI with countdown
- Offline detection with offline mode
- Loading spinners and skeleton screens

### 11.4 Priority 4 - Testing
- E2E test suite already covers main scenarios
- Unit tests for auth store
- Integration tests for redirect logic
- Performance tests for Clerk initialization

---

## 12. FILE LOCATIONS SUMMARY

| Purpose | Location |
|---------|----------|
| Clerk initialization | `/apps/frontend/src/lib/clerk.ts` |
| Root layout | `/apps/frontend/src/routes/+layout.svelte` |
| Auth store | `/apps/frontend/src/lib/stores/auth.svelte.ts` |
| Login page | `/apps/frontend/src/routes/login/+page.svelte` |
| UserButton component | `/apps/frontend/src/lib/components/UserButton.svelte` |
| Redirect logic | `/apps/frontend/src/lib/utils/redirect.ts` |
| Dashboard layout | `/apps/frontend/src/routes/dashboard/+layout.svelte` |
| Backend user endpoints | `/apps/server/src/server/api/v1/endpoints/users.py` |
| E2E tests | `/apps/frontend/tests/e2e/auth-login-logout.spec.ts` |
| Backend auth tests | `/apps/server/tests/api/v1/test_auth.py` |
| Backend Clerk tests | `/apps/server/tests/api/v1/test_clerk_auth.py` |

---

## 13. IMPLEMENTATION APPROACH

### 13.1 Phases
1. **RESEARCH** (Complete) - Understand existing patterns and integration points
2. **PLANNING** - Design protected route guards and error handling
3. **IMPLEMENTATION** - Add route protection, handle edge cases
4. **TESTING** - E2E and integration testing
5. **VALIDATION** - Verify all acceptance criteria met

### 13.2 Key Decisions Identified
1. **Route Guard Pattern** - Use SvelteKit `load()` functions (standard approach)
2. **Error Handling** - Leverage existing structured logging pattern
3. **Session Validation** - Call `authStore.initialize()` on app mount (already done)
4. **Redirect Strategy** - Preserve destination via query param (already in tests)

---

**Next Steps:** Move to Planning phase to design detailed acceptance criteria and implementation architecture.
