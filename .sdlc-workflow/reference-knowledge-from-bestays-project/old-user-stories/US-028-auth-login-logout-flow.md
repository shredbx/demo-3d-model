# US-028: Login & Logout Flow

**Domain:** auth
**Feature:** login-logout
**Scope:** flow
**Status:** READY
**Priority:** P0 (MVP Blocker)
**Created:** 2025-11-10
**Default Product:** bestays
**Portable:** true
**Ported To:** []

---

## Description

Implement complete login and logout functionality for the Bestays platform using Clerk authentication. This includes proper session management, protected routes, role-based redirects after login, and secure logout with session cleanup.

**User Flow:**
1. User clicks "Login" button
2. Clerk login modal appears
3. User enters credentials (email/password or social login)
4. After successful authentication, user is redirected based on role:
   - Admin → /admin/dashboard
   - Agent → /agent/dashboard
   - User → /home
5. User can logout from any page
6. After logout, user is redirected to homepage and session is cleared

---

## Acceptance Criteria

- [ ] Login button triggers Clerk authentication modal
- [ ] Successful login redirects user based on role (admin/agent/user)
- [ ] Protected routes redirect unauthenticated users to login
- [ ] Logout button clears session and redirects to homepage
- [ ] Session persists across page refreshes
- [ ] Error handling for failed logins (invalid credentials, network errors)
- [ ] Loading states during authentication
- [ ] E2E tests cover login/logout flows for all roles
- [ ] Works in Chrome, Firefox, Safari

---

## Technical Notes

**Dependencies:**
- Clerk SDK (already integrated via TASK-001 of US-001)
- Role-based access control (US-001B - partially complete)
- Test accounts: user.claudecode@bestays.app, admin.claudecode@bestays.app, agent.claudecode@bestays.app

**Constraints:**
- Must use Clerk authentication (no custom auth)
- Must follow Network Resilience Pattern (retry logic, error handling)
- Must be SSR-compatible (SvelteKit)
- Must work with existing role detection from backend

**Integration Points:**
- Frontend: SvelteKit routes with Clerk components
- Backend: FastAPI endpoints for role validation
- Database: User roles stored in PostgreSQL

---

## Related Stories

- US-001: Login Flow Validation (E2E tests foundation)
- US-001B: RBAC Implementation (role-based redirects depend on this)
- US-018: Multi-Product Infrastructure (Clerk setup for both products)

---

## Tasks

[Automatically populated by system - do not edit manually]
