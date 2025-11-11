# US-019: User Login & Logout Flow

**Domain:** auth
**Feature:** login
**Scope:** flow
**Status:** READY
**Priority:** P0 (CRITICAL - MVP Blocker)
**Created:** 2025-11-08
**Default Product:** bestays
**Portable:** true
**Ported To:** []

> **Note:** This story corresponds to "US-012" in the Milestone 01 specification.

---

## Description

As a user (agent/admin/regular), I need to log in and log out securely so I can access product features and protect my account.

**Multi-Product Context:**
- Same login flow works for **both products** (Bestays + Real Estate)
- Different Clerk instances (sacred-mayfly-55 vs pleasant-gnu-25)
- Different redirect destinations based on product configuration
- UI theme follows product PRIMARY_COLOR

---

## Acceptance Criteria

### Login Page

- [ ] Login page displays at `/auth/login` route
- [ ] Login form components:
  - [ ] Email input (required, validated for email format)
  - [ ] Password input (required, min 8 characters, hidden text)
  - [ ] "Remember me" checkbox (optional)
  - [ ] "Log In" button (disabled while submitting)
  - [ ] "Forgot password?" link → `/auth/forgot-password`
  - [ ] "Don't have an account? Sign up" link → `/auth/sign-up`
- [ ] Form validation:
  - [ ] Show inline errors for invalid email format
  - [ ] Show error for empty password
  - [ ] Client-side validation before submit
  - [ ] Disable submit button during API call

### Login Flow

- [ ] Submit credentials to Clerk API via backend endpoint
- [ ] On success:
  - [ ] Store session token in httpOnly secure cookie
  - [ ] Redirect to `/cms/properties` (or original destination if redirected from protected page)
  - [ ] Show success toast: "Welcome back!"
- [ ] On failure (invalid credentials):
  - [ ] Show error message: "Invalid email or password"
  - [ ] Keep form filled (don't clear password)
  - [ ] Re-enable submit button
- [ ] On network error:
  - [ ] Show error message: "Connection error. Please try again."
  - [ ] Implement retry logic (network resilience pattern)

### Logout Flow

- [ ] "Logout" button in CMS navigation bar
- [ ] Click logout:
  - [ ] Call `/api/auth/logout` endpoint
  - [ ] Clear session cookie
  - [ ] Redirect to `/` (homepage)
  - [ ] Show success toast: "Logged out successfully"

### Session Management

- [ ] If "Remember me" checked: session lasts 30 days
- [ ] If not checked: session lasts 7 days
- [ ] Session automatically renewed on activity
- [ ] Expired session redirects to login with message: "Session expired. Please log in again."

### Protected Routes

- [ ] Middleware checks authentication for `/cms/*` routes
- [ ] If unauthenticated:
  - [ ] Redirect to `/auth/login?redirect=/cms/...` (preserve original destination)
- [ ] If authenticated:
  - [ ] Allow access to protected route
  - [ ] Load user session data (role, email, name)

### Multi-Product Support

- [ ] **Bestays product:**
  - [ ] Uses Clerk instance: `sacred-mayfly-55.clerk.accounts.dev`
  - [ ] Redirects to Bestays dashboard after login
  - [ ] Theme: PRIMARY_COLOR=#FF6B6B
- [ ] **Real Estate product:**
  - [ ] Uses Clerk instance: `pleasant-gnu-25.clerk.accounts.dev`
  - [ ] Redirects to Real Estate dashboard after login
  - [ ] Theme: PRIMARY_COLOR=#4ECDC4
- [ ] No shared authentication (separate user bases)
- [ ] Test users created for both products (see test credentials)

### Testing

- [ ] E2E tests for **both products** (Bestays + Real Estate)
- [ ] Test successful login (valid credentials)
- [ ] Test failed login (invalid credentials)
- [ ] Test logout flow
- [ ] Test protected route redirect
- [ ] Test session persistence (remember me)
- [ ] Test session expiration
- [ ] Test network resilience (retry logic)
- [ ] Cross-browser testing (Chrome, Firefox, Safari)

---

## Technical Notes

### Architecture

**Frontend (SvelteKit):**
- Route: `apps/frontend/src/routes/auth/login/+page.svelte`
- Uses Svelte 5 runes ($state, $effect)
- Clerk SDK integration via `@clerk/clerk-sdk-node`
- Form validation with client-side checks
- Network resilience pattern (retry, exponential backoff)

**Backend (FastAPI):**
- Endpoint: `POST /api/auth/login`
- Validates credentials with Clerk API
- Sets httpOnly secure cookie with JWT token
- Returns user session data

**Database:**
- No user credentials stored (Clerk handles auth)
- User roles stored in `users` table (referenced by Clerk user_id)

### API Endpoints

**POST /api/auth/login**
```python
# Request
{
  "email": "user.claudecode@bestays.app",
  "password": "9kB*k926O8):",
  "remember_me": true
}

# Response (Success)
{
  "success": true,
  "user": {
    "id": "user_abc123",
    "email": "user.claudecode@bestays.app",
    "role": "user",
    "name": "Claude User"
  }
}

# Response (Failure)
{
  "success": false,
  "error": "Invalid email or password"
}
```

**POST /api/auth/logout**
```python
# Response
{
  "success": true
}
```

### Clerk Integration

**Bestays Clerk Configuration:**
- Account: `sacred-mayfly-55.clerk.accounts.dev`
- Publishable Key: `pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk`
- Secret Key: `sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit`

**Real Estate Clerk Configuration:**
- Account: `pleasant-gnu-25.clerk.accounts.dev`
- Publishable Key: `pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ`
- Secret Key: `sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS`

### Environment Variables

Required in `.env.bestays` and `.env.realestate`:
- `CLERK_SECRET_KEY` - Backend authentication
- `VITE_CLERK_PUBLISHABLE_KEY` - Frontend SDK initialization
- `PUBLIC_PRODUCT_NAME` - Display name ("Bestays" / "Best Real Estate")
- `PRIMARY_COLOR` - Theme color

### Test Credentials

**Bestays (sacred-mayfly-55):**
- User: `user.claudecode@bestays.app` / `9kB*k926O8):`
- Admin: `admin.claudecode@bestays.app` / `rHe/997?lo&l`
- Agent: `agent.claudecode@bestays.app` / `y>1T;)5s!X1X`

**Real Estate (pleasant-gnu-25):**
- User: `user.claudecode@realestate.dev` / `y>1T_)5h!X1X`
- Admin: `admin.claudecode@realestate.dev` / `rHe/997?lo&l`
- Agent: `agent.claudecode@realestate.dev` / `y>1T;)5s!X1X`

### Network Resilience Pattern

Apply `frontend-network-resilience` skill:
- Retry failed requests (3 attempts)
- Exponential backoff (1s, 2s, 4s)
- Show user-friendly error messages
- Offline detection (show warning banner)

### Security Considerations

- [ ] httpOnly cookies (prevent XSS)
- [ ] Secure flag (HTTPS only)
- [ ] SameSite=Lax (CSRF protection)
- [ ] Password never stored in frontend state after submit
- [ ] No credentials in URL params
- [ ] Session timeout enforced

---

## Related Stories

**Dependencies:**
- US-018: Multi-Product Infrastructure (COMPLETE)

**Blocks:**
- US-002: Homepage (needs login to show user-specific content)
- US-013: User Registration
- US-014: Password Reset
- US-015: Protected Routes (CMS Dashboard)

**Reference Implementations:**
- Old NextJS login: `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web` (research only)

---

## Tasks

### Phase 1: RESEARCH (TASK-001)
- Review old NextJS login implementation
- Identify Clerk integration patterns
- Document what needs to be reimplemented
- Check for reusable components

### Phase 2: PLANNING (TASK-002)
- Design SvelteKit login flow
- Apply 7 quality gates (network resilience, SSR, testing, etc.)
- Define component structure
- Design API endpoints
- Plan E2E test scenarios

### Phase 3: IMPLEMENTATION (TASK-003)
- Implement login page (dev-frontend-svelte)
- Implement backend endpoints (dev-backend-fastapi)
- Implement session middleware
- Test on BOTH products (Bestays + Real Estate)

### Phase 4: TESTING (TASK-004)
- E2E tests for both products (playwright-e2e-tester)
- Cross-browser testing
- Network resilience testing

### Phase 5: VALIDATION (TASK-005)
- Verify both Clerk instances work
- Verify separate user bases
- Mark story as COMPLETE

---

**Story Created:** 2025-11-08
**Corresponds to Milestone Spec:** US-012 (User Login & Logout)
**SDLC Workflow:** Full workflow required (RESEARCH → PLANNING → IMPLEMENTATION → TESTING → VALIDATION)
