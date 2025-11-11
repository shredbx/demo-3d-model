# TASK-003: RBAC Core Components

**Story:** US-001B - Role-Based Access Control and Audit Logging
**Task:** TASK-003 - Create RBAC core components (permissions, decorators, role service)
**Status:** IN_PROGRESS
**Created:** 2025-11-07

---

## What Needs to Be Done

Create the foundational RBAC infrastructure for the Bestays backend:

1. **Permission System** (`apps/server/api/auth/permissions.py`)
   - Define Permission enum with all resource permissions
   - Create ROLE_PERMISSIONS mapping (role → list of permissions)

2. **Permission Decorator** (`apps/server/api/auth/decorators.py`)
   - `@require_permission(Permission.X)` decorator for FastAPI routes
   - Automatic permission checking with proper error handling

3. **Role Service** (`apps/server/api/services/role_service.py`)
   - `has_permission(user, permission)` - Check if user has permission
   - `check_role(user, role)` - Check if user has specific role
   - `get_permissions(role)` - Get all permissions for a role

4. **Update Dependencies** (`apps/server/api/deps.py`)
   - Add `get_current_user_with_permission` dependency
   - Integrate permission checking into existing auth flow

5. **Tests** (`apps/server/tests/test_rbac.py`)
   - Test permission decorator
   - Test role service methods
   - Test different role scenarios
   - Performance test (<1ms for permission checks)

---

## Which Files to Modify

**New Files:**
- `apps/server/src/server/api/auth/__init__.py`
- `apps/server/src/server/api/auth/permissions.py`
- `apps/server/src/server/api/auth/decorators.py`
- `apps/server/src/server/api/services/role_service.py`
- `apps/server/tests/test_rbac.py`

**Modified Files:**
- `apps/server/src/server/api/deps.py` (add permission checking dependencies)

---

## Which Subagent to Use

**Subagent:** `dev-backend-fastapi`

This task involves pure backend Python code (FastAPI, SQLAlchemy patterns, Clean Architecture).

---

## Acceptance Criteria for Task

1. ✅ Permission enum created with all resource permissions (property, user, audit)
2. ✅ ROLE_PERMISSIONS mapping correctly assigns permissions to roles
3. ✅ `@require_permission` decorator works on FastAPI routes
4. ✅ Role service provides utility methods (has_permission, check_role, get_permissions)
5. ✅ Permission checks are performant (<1ms, in-memory lookups only)
6. ✅ Tests pass with good coverage
7. ✅ File headers follow project patterns
8. ✅ Type hints throughout
9. ✅ Proper error handling (HTTPException with clear messages)

---

## Context

**Current State:**
- User authentication with Clerk is working (US-001 completed)
- User model has `role` field (guest, user, agent, admin) - but note: actual roles are (user, agent, admin)
- Database ready for migrations (PostgreSQL with Alembic)
- Existing auth dependencies in `deps.py` and `clerk_deps.py`

**Architecture Context:**
- Follow Clean Architecture patterns (see existing code)
- Use Dependency Injection via FastAPI Depends()
- Integration with Clerk authentication (already in place)
- Single-company platform (no ownership model, just audit WHO did WHAT)

**Performance Requirement:**
- Permission checks MUST be <1ms (in-memory role-permission mapping, NO database calls)

**Do NOT:**
- Modify database schema (TASK-002 handles that)
- Update existing endpoints yet (future task)
- Implement audit logging (future task)
- Add any database queries to permission checking logic

---

## Implementation Guidelines

1. **Follow Existing Patterns:**
   - File headers: See `apps/server/src/server/core/security.py`
   - Dependencies: See `apps/server/src/server/api/deps.py`
   - Auth patterns: See `apps/server/src/server/api/clerk_deps.py`

2. **Role Hierarchy:**
   - `admin`: All permissions
   - `agent`: Property view/create/update, user view
   - `user`: Property view only
   - `guest`: No permissions (future use)

3. **Permission Naming Convention:**
   - Format: `{resource}:{action}`
   - Examples: `property:view`, `property:create`, `user:update`

4. **Error Handling:**
   - Use HTTPException with status 403 for permission denied
   - Clear error messages: "Permission denied: property:update required"

5. **Extensibility:**
   - Easy to add new permissions
   - Easy to add new roles
   - Easy to modify role-permission mappings

---

## Notes

- This task lays the foundation for RBAC but doesn't integrate with endpoints yet
- TASK-002 will create the audit_log table (separate concern)
- Future tasks will integrate these components into actual endpoints
- The user model already exists with role field - see `apps/server/src/server/models/user.py`
