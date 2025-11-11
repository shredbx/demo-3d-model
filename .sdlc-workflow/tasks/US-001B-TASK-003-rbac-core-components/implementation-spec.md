# Implementation Specification: RBAC Core Components

**For Subagent:** dev-backend-fastapi
**Task:** US-001B-TASK-003
**Date:** 2025-11-07

---

## Overview

Create core RBAC infrastructure for FastAPI backend with permission system, decorators, and role service. This is pure backend work following Clean Architecture patterns.

**Performance Requirement:** Permission checks MUST be <1ms (in-memory only, NO database queries)

---

## Files to Create/Modify

### New Files

1. **`apps/server/src/server/api/auth/__init__.py`**
   - Empty init file to make auth/ a package
   - Export main classes/functions for easier imports

2. **`apps/server/src/server/api/auth/permissions.py`**
   - Permission enum with all resource permissions
   - ROLE_PERMISSIONS mapping (role → list of permissions)

3. **`apps/server/src/server/api/auth/decorators.py`**
   - `@require_permission(permission)` decorator
   - Integrates with FastAPI dependency injection

4. **`apps/server/src/server/api/services/role_service.py`**
   - `RoleService` class with static methods
   - `has_permission(user, permission)` - Boolean check
   - `check_role(user, role)` - Boolean check
   - `get_permissions(role)` - List of permissions

5. **`apps/server/tests/test_rbac.py`**
   - Comprehensive test suite for all RBAC components

### Modified Files

6. **`apps/server/src/server/api/deps.py`**
   - Add `get_current_user_with_permission(permission)` dependency factory
   - Optional: Add convenience functions for common permission patterns

---

## Detailed Specifications

### 1. Permission System (`permissions.py`)

```python
"""
RBAC Permission System

ARCHITECTURE:
  Layer: API (Auth)
  Pattern: Enum-based permission definitions + In-memory role mapping

PATTERNS USED:
  - Enum Pattern: Type-safe permission identifiers
  - Role-Permission Mapping: Static dict for O(1) lookups
  - Naming Convention: {resource}:{action} format

DEPENDENCIES:
  External: enum (stdlib)
  Internal: None (standalone)

INTEGRATION:
  - decorators.py: Uses Permission enum
  - role_service.py: Uses ROLE_PERMISSIONS mapping
  - deps.py: Permission checking in dependencies

TESTING:
  - Test File: tests/test_rbac.py
  - Coverage Target: 100% (simple data structures)

Permission Naming:
- Format: {resource}:{action}
- Resources: property, user, audit
- Actions: view, create, update, delete, publish

Role Hierarchy:
- admin: All permissions (superuser)
- agent: Property management + user view
- user: Property view only (browsing)
"""

from enum import Enum


class Permission(str, Enum):
    """Permission definitions for RBAC system.

    All permissions follow {resource}:{action} naming convention.
    Designed for in-memory lookup performance (<1ms requirement).
    """

    # Property permissions
    PROPERTY_VIEW = "property:view"
    PROPERTY_CREATE = "property:create"
    PROPERTY_UPDATE = "property:update"
    PROPERTY_DELETE = "property:delete"
    PROPERTY_PUBLISH = "property:publish"

    # User management permissions
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Audit permissions
    AUDIT_VIEW = "audit:view"


# Role-permission mapping for O(1) permission checks
# This is intentionally in-memory (not database) for <1ms performance
ROLE_PERMISSIONS: dict[str, list[Permission]] = {
    "admin": [
        # Property permissions (full access)
        Permission.PROPERTY_VIEW,
        Permission.PROPERTY_CREATE,
        Permission.PROPERTY_UPDATE,
        Permission.PROPERTY_DELETE,
        Permission.PROPERTY_PUBLISH,

        # User management (full access)
        Permission.USER_VIEW,
        Permission.USER_CREATE,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,

        # Audit (full access)
        Permission.AUDIT_VIEW,
    ],
    "agent": [
        # Property permissions (full management)
        Permission.PROPERTY_VIEW,
        Permission.PROPERTY_CREATE,
        Permission.PROPERTY_UPDATE,
        Permission.PROPERTY_PUBLISH,
        # Note: Agents CANNOT delete properties (admin only)

        # User management (view only)
        Permission.USER_VIEW,
        # Note: Agents CANNOT create/update/delete users
    ],
    "user": [
        # Property permissions (view only - browsing)
        Permission.PROPERTY_VIEW,
        # Note: Regular users CANNOT manage properties
    ],
}
```

**Key Points:**
- String enum for JSON serialization compatibility
- Exhaustive role-permission mapping
- Comments explain role hierarchy
- No database dependencies (pure in-memory)

---

### 2. Permission Decorator (`decorators.py`)

```python
"""
RBAC Permission Decorators

ARCHITECTURE:
  Layer: API (Auth)
  Pattern: Decorator Pattern + Dependency Injection

PATTERNS USED:
  - Decorator Pattern: Clean syntax for route protection
  - Dependency Injection: Integrates with FastAPI Depends()
  - Closure: Permission parameter captured in decorator

DEPENDENCIES:
  External: fastapi, functools
  Internal:
    - server.api.auth.permissions (Permission enum)
    - server.api.services.role_service (RoleService)
    - server.models.user (User model)

INTEGRATION:
  - FastAPI routes: Applied as @require_permission decorator
  - auth dependencies: Gets current user from dependency chain
  - role_service: Delegates permission checking logic

TESTING:
  - Test File: tests/test_rbac.py
  - Coverage Target: 95% (high-risk auth code)

Usage:
    @router.post("/properties")
    @require_permission(Permission.PROPERTY_CREATE)
    async def create_property(
        current_user: User = Depends(get_clerk_user)
    ):
        # Only users with property:create permission can reach here
        pass

Security:
- Raises HTTPException 403 if permission denied
- Clear error messages for debugging
- Fails closed (deny by default)
"""

from functools import wraps
from typing import Callable

from fastapi import HTTPException, status

from server.api.auth.permissions import Permission
from server.api.services.role_service import RoleService
from server.models.user import User


def require_permission(permission: Permission) -> Callable:
    """Decorator to require a specific permission for route access.

    This decorator checks if the current user has the required permission
    before allowing access to the route handler.

    Args:
        permission: The required permission from Permission enum

    Returns:
        Decorator function that wraps the route handler

    Raises:
        HTTPException: 403 Forbidden if user lacks permission

    Example:
        @router.post("/properties")
        @require_permission(Permission.PROPERTY_CREATE)
        async def create_property(
            current_user: User = Depends(get_clerk_user)
        ):
            return {"status": "created"}

    Performance:
        - O(1) permission lookup via in-memory mapping
        - <1ms execution time (meets requirement)

    Security:
        - Fails closed (deny by default if role not found)
        - Clear error messages for debugging
        - Integrates with existing Clerk authentication
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            # FastAPI injects it via Depends(get_clerk_user)
            current_user = kwargs.get("current_user")

            if not current_user or not isinstance(current_user, User):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check permission using role service
            if not RoleService.has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value} required",
                )

            # Permission granted, proceed to route handler
            return await func(*args, **kwargs)

        return wrapper
    return decorator
```

**Key Points:**
- Integrates with FastAPI's Depends() pattern
- Extracts current_user from kwargs (injected by FastAPI)
- Delegates permission checking to RoleService
- Clear error messages with permission name
- Proper async/await handling

---

### 3. Role Service (`role_service.py`)

```python
"""
Role Service - RBAC Business Logic

ARCHITECTURE:
  Layer: Service (Business Logic)
  Pattern: Service Pattern + Static Methods

PATTERNS USED:
  - Service Pattern: Encapsulates business logic
  - Static Methods: Stateless utility functions
  - In-Memory Lookup: O(1) performance for permission checks

DEPENDENCIES:
  External: None
  Internal:
    - server.api.auth.permissions (Permission enum, ROLE_PERMISSIONS)
    - server.models.user (User model)

INTEGRATION:
  - decorators.py: Calls has_permission()
  - deps.py: May use for permission checking
  - Future: Audit service will log permission checks

TESTING:
  - Test File: tests/test_rbac.py
  - Coverage Target: 100% (pure logic, no I/O)
  - Performance Test: <1ms for has_permission()

Performance:
- All methods use in-memory lookups (no database queries)
- O(1) for has_permission() via dict lookup
- O(1) for check_role() via string comparison
- O(1) for get_permissions() via dict lookup
"""

from server.api.auth.permissions import Permission, ROLE_PERMISSIONS
from server.models.user import User


class RoleService:
    """Service for role-based permission checking.

    Provides utility methods for checking user permissions and roles.
    All methods are static (stateless) and use in-memory lookups for
    <1ms performance.

    Design Philosophy:
    - Fail closed: Deny by default if role not found
    - Type safe: Use Permission enum, not strings
    - Performance: In-memory only, no database queries
    - Extensible: Easy to add new roles/permissions
    """

    @staticmethod
    def has_permission(user: User, permission: Permission) -> bool:
        """Check if user has a specific permission.

        This is the core permission checking method used throughout
        the application. It performs an in-memory lookup for O(1)
        performance.

        Args:
            user: User object with role attribute
            permission: Permission enum value to check

        Returns:
            bool: True if user's role has the permission, False otherwise

        Example:
            if RoleService.has_permission(user, Permission.PROPERTY_CREATE):
                # User can create properties
                pass

        Performance:
            - O(1) dict lookup via ROLE_PERMISSIONS mapping
            - <1ms execution time (typically <100μs)
            - No database queries

        Security:
            - Fails closed: Returns False if role not in mapping
            - Case-sensitive role matching (ensure consistent casing)
        """
        # Get permissions for user's role (returns empty list if role not found)
        role_perms = ROLE_PERMISSIONS.get(user.role, [])

        # Check if permission is in the role's permission list
        return permission in role_perms

    @staticmethod
    def check_role(user: User, role: str) -> bool:
        """Check if user has a specific role.

        Simple role comparison for cases where you need to check
        the exact role rather than permissions.

        Args:
            user: User object with role attribute
            role: Role string to check against

        Returns:
            bool: True if user has the specified role

        Example:
            if RoleService.check_role(user, "admin"):
                # User is an admin
                pass

        Note:
            Prefer has_permission() over check_role() when possible,
            as it's more flexible and maintainable.
        """
        return user.role == role

    @staticmethod
    def get_permissions(role: str) -> list[Permission]:
        """Get all permissions for a specific role.

        Useful for:
        - Displaying user capabilities in UI
        - Debugging permission issues
        - Admin interfaces showing role details

        Args:
            role: Role string to get permissions for

        Returns:
            list[Permission]: List of permissions for the role
                             (empty list if role not found)

        Example:
            perms = RoleService.get_permissions("agent")
            # [Permission.PROPERTY_VIEW, Permission.PROPERTY_CREATE, ...]

        Performance:
            - O(1) dict lookup
            - Returns reference to list (not a copy) for performance
        """
        return ROLE_PERMISSIONS.get(role, [])
```

**Key Points:**
- All static methods (no state)
- Clear docstrings with examples
- Performance notes in docstrings
- Fail closed (deny by default)
- Type hints throughout

---

### 4. Update Dependencies (`deps.py`)

**Add to existing `apps/server/src/server/api/deps.py`:**

```python
# Add import at top
from server.api.auth.permissions import Permission
from server.api.services.role_service import RoleService

# Add new dependency function at end of file
def require_permission_dependency(permission: Permission):
    """Factory function to create permission-checking dependencies.

    Creates a FastAPI dependency that checks if the current user
    has the required permission.

    Args:
        permission: Required permission

    Returns:
        Dependency function that returns the user if permitted

    Raises:
        HTTPException: 403 if user lacks permission

    Usage:
        @router.post("/properties")
        async def create_property(
            current_user: User = Depends(
                require_permission_dependency(Permission.PROPERTY_CREATE)
            )
        ):
            return {"status": "created"}

    Note:
        This is an alternative to the @require_permission decorator.
        Both approaches work - choose based on your preference:
        - Decorator: Cleaner syntax, more visible
        - Dependency: More composable, standard FastAPI pattern
    """
    async def dependency(
        current_user: User = Depends(get_clerk_user),
    ) -> User:
        if not RoleService.has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required",
            )
        return current_user

    return dependency
```

**Key Points:**
- Provides dependency injection alternative to decorator
- Factory pattern for creating permission-specific dependencies
- Integrates with existing get_clerk_user dependency
- Same error handling as decorator

---

### 5. Tests (`test_rbac.py`)

```python
"""
Tests for RBAC System

Tests cover:
- Permission enum and ROLE_PERMISSIONS mapping
- RoleService methods (has_permission, check_role, get_permissions)
- Permission decorator functionality
- Performance requirements (<1ms)
- Different role scenarios
- Edge cases (unknown roles, missing permissions)
"""

import pytest
from unittest.mock import Mock
from fastapi import HTTPException

from server.api.auth.permissions import Permission, ROLE_PERMISSIONS
from server.api.auth.decorators import require_permission
from server.api.services.role_service import RoleService
from server.models.user import User


# --- Test Data Fixtures ---

@pytest.fixture
def admin_user():
    """Mock admin user for testing."""
    user = Mock(spec=User)
    user.role = "admin"
    user.id = 1
    user.clerk_user_id = "user_admin123"
    user.email = "admin@bestays.app"
    return user


@pytest.fixture
def agent_user():
    """Mock agent user for testing."""
    user = Mock(spec=User)
    user.role = "agent"
    user.id = 2
    user.clerk_user_id = "user_agent456"
    user.email = "agent@bestays.app"
    return user


@pytest.fixture
def regular_user():
    """Mock regular user for testing."""
    user = Mock(spec=User)
    user.role = "user"
    user.id = 3
    user.clerk_user_id = "user_user789"
    user.email = "user@bestays.app"
    return user


# --- Permission System Tests ---

def test_permission_enum_values():
    """Test that Permission enum has expected values."""
    assert Permission.PROPERTY_VIEW.value == "property:view"
    assert Permission.PROPERTY_CREATE.value == "property:create"
    assert Permission.USER_VIEW.value == "user:view"
    assert Permission.AUDIT_VIEW.value == "audit:view"


def test_role_permissions_structure():
    """Test that ROLE_PERMISSIONS has all expected roles."""
    assert "admin" in ROLE_PERMISSIONS
    assert "agent" in ROLE_PERMISSIONS
    assert "user" in ROLE_PERMISSIONS
    assert isinstance(ROLE_PERMISSIONS["admin"], list)


def test_admin_has_all_permissions():
    """Test that admin role has all permissions."""
    admin_perms = ROLE_PERMISSIONS["admin"]

    # Admin should have all property permissions
    assert Permission.PROPERTY_VIEW in admin_perms
    assert Permission.PROPERTY_CREATE in admin_perms
    assert Permission.PROPERTY_UPDATE in admin_perms
    assert Permission.PROPERTY_DELETE in admin_perms
    assert Permission.PROPERTY_PUBLISH in admin_perms

    # Admin should have all user permissions
    assert Permission.USER_VIEW in admin_perms
    assert Permission.USER_CREATE in admin_perms
    assert Permission.USER_UPDATE in admin_perms
    assert Permission.USER_DELETE in admin_perms

    # Admin should have audit permissions
    assert Permission.AUDIT_VIEW in admin_perms


def test_agent_permissions_subset():
    """Test that agent has correct permission subset."""
    agent_perms = ROLE_PERMISSIONS["agent"]

    # Agent can manage properties
    assert Permission.PROPERTY_VIEW in agent_perms
    assert Permission.PROPERTY_CREATE in agent_perms
    assert Permission.PROPERTY_UPDATE in agent_perms
    assert Permission.PROPERTY_PUBLISH in agent_perms

    # Agent CANNOT delete properties
    assert Permission.PROPERTY_DELETE not in agent_perms

    # Agent can view users
    assert Permission.USER_VIEW in agent_perms

    # Agent CANNOT manage users
    assert Permission.USER_CREATE not in agent_perms
    assert Permission.USER_UPDATE not in agent_perms
    assert Permission.USER_DELETE not in agent_perms


def test_user_permissions_minimal():
    """Test that regular user has minimal permissions."""
    user_perms = ROLE_PERMISSIONS["user"]

    # User can only view properties
    assert Permission.PROPERTY_VIEW in user_perms

    # User CANNOT manage properties
    assert Permission.PROPERTY_CREATE not in user_perms
    assert Permission.PROPERTY_UPDATE not in user_perms
    assert Permission.PROPERTY_DELETE not in user_perms
    assert Permission.PROPERTY_PUBLISH not in user_perms

    # User CANNOT access user management
    assert Permission.USER_VIEW not in user_perms


# --- RoleService Tests ---

def test_has_permission_admin(admin_user):
    """Test admin user has all permissions."""
    assert RoleService.has_permission(admin_user, Permission.PROPERTY_VIEW)
    assert RoleService.has_permission(admin_user, Permission.PROPERTY_CREATE)
    assert RoleService.has_permission(admin_user, Permission.PROPERTY_DELETE)
    assert RoleService.has_permission(admin_user, Permission.USER_UPDATE)
    assert RoleService.has_permission(admin_user, Permission.AUDIT_VIEW)


def test_has_permission_agent(agent_user):
    """Test agent user has correct permissions."""
    # Agent can view and create properties
    assert RoleService.has_permission(agent_user, Permission.PROPERTY_VIEW)
    assert RoleService.has_permission(agent_user, Permission.PROPERTY_CREATE)

    # Agent CANNOT delete properties
    assert not RoleService.has_permission(agent_user, Permission.PROPERTY_DELETE)

    # Agent CANNOT manage users
    assert not RoleService.has_permission(agent_user, Permission.USER_CREATE)


def test_has_permission_regular_user(regular_user):
    """Test regular user has minimal permissions."""
    # User can view properties
    assert RoleService.has_permission(regular_user, Permission.PROPERTY_VIEW)

    # User CANNOT create properties
    assert not RoleService.has_permission(regular_user, Permission.PROPERTY_CREATE)

    # User CANNOT access user management
    assert not RoleService.has_permission(regular_user, Permission.USER_VIEW)


def test_has_permission_unknown_role():
    """Test has_permission fails closed for unknown roles."""
    unknown_user = Mock(spec=User)
    unknown_user.role = "unknown"

    # Should deny all permissions for unknown roles
    assert not RoleService.has_permission(unknown_user, Permission.PROPERTY_VIEW)


def test_check_role(admin_user, agent_user, regular_user):
    """Test check_role method."""
    assert RoleService.check_role(admin_user, "admin")
    assert not RoleService.check_role(admin_user, "agent")

    assert RoleService.check_role(agent_user, "agent")
    assert not RoleService.check_role(agent_user, "admin")

    assert RoleService.check_role(regular_user, "user")
    assert not RoleService.check_role(regular_user, "admin")


def test_get_permissions():
    """Test get_permissions returns correct permission lists."""
    admin_perms = RoleService.get_permissions("admin")
    assert len(admin_perms) > 0
    assert Permission.PROPERTY_VIEW in admin_perms

    agent_perms = RoleService.get_permissions("agent")
    assert len(agent_perms) > 0
    assert len(agent_perms) < len(admin_perms)  # Agent has fewer perms

    unknown_perms = RoleService.get_permissions("unknown")
    assert unknown_perms == []  # Empty list for unknown roles


# --- Performance Tests ---

import time


def test_has_permission_performance(admin_user):
    """Test that permission check is <1ms (actual requirement)."""
    iterations = 1000

    start = time.perf_counter()
    for _ in range(iterations):
        RoleService.has_permission(admin_user, Permission.PROPERTY_VIEW)
    end = time.perf_counter()

    avg_time_ms = ((end - start) / iterations) * 1000

    # Must be <1ms per check
    assert avg_time_ms < 1.0, f"Permission check too slow: {avg_time_ms:.4f}ms"

    # Typically should be <0.01ms (10μs)
    print(f"\nAverage permission check time: {avg_time_ms:.4f}ms")


# --- Decorator Tests ---

@pytest.mark.asyncio
async def test_require_permission_decorator_allows_access(admin_user):
    """Test decorator allows access when user has permission."""

    @require_permission(Permission.PROPERTY_CREATE)
    async def protected_route(current_user: User):
        return {"status": "success"}

    # Should not raise exception
    result = await protected_route(current_user=admin_user)
    assert result == {"status": "success"}


@pytest.mark.asyncio
async def test_require_permission_decorator_denies_access(regular_user):
    """Test decorator denies access when user lacks permission."""

    @require_permission(Permission.PROPERTY_CREATE)
    async def protected_route(current_user: User):
        return {"status": "success"}

    # Should raise 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        await protected_route(current_user=regular_user)

    assert exc_info.value.status_code == 403
    assert "property:create" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_require_permission_decorator_no_user():
    """Test decorator denies access when no user provided."""

    @require_permission(Permission.PROPERTY_VIEW)
    async def protected_route(current_user: User = None):
        return {"status": "success"}

    # Should raise 401 Unauthorized
    with pytest.raises(HTTPException) as exc_info:
        await protected_route(current_user=None)

    assert exc_info.value.status_code == 401


# --- Integration Scenarios ---

def test_scenario_admin_full_access(admin_user):
    """Scenario: Admin can do everything."""
    # Property management
    assert RoleService.has_permission(admin_user, Permission.PROPERTY_VIEW)
    assert RoleService.has_permission(admin_user, Permission.PROPERTY_CREATE)
    assert RoleService.has_permission(admin_user, Permission.PROPERTY_UPDATE)
    assert RoleService.has_permission(admin_user, Permission.PROPERTY_DELETE)
    assert RoleService.has_permission(admin_user, Permission.PROPERTY_PUBLISH)

    # User management
    assert RoleService.has_permission(admin_user, Permission.USER_VIEW)
    assert RoleService.has_permission(admin_user, Permission.USER_CREATE)
    assert RoleService.has_permission(admin_user, Permission.USER_UPDATE)
    assert RoleService.has_permission(admin_user, Permission.USER_DELETE)

    # Audit
    assert RoleService.has_permission(admin_user, Permission.AUDIT_VIEW)


def test_scenario_agent_property_management(agent_user):
    """Scenario: Agent can manage properties but not delete them."""
    # Can view, create, update, publish
    assert RoleService.has_permission(agent_user, Permission.PROPERTY_VIEW)
    assert RoleService.has_permission(agent_user, Permission.PROPERTY_CREATE)
    assert RoleService.has_permission(agent_user, Permission.PROPERTY_UPDATE)
    assert RoleService.has_permission(agent_user, Permission.PROPERTY_PUBLISH)

    # Cannot delete (admin only)
    assert not RoleService.has_permission(agent_user, Permission.PROPERTY_DELETE)


def test_scenario_user_browse_only(regular_user):
    """Scenario: Regular user can only browse properties."""
    # Can view
    assert RoleService.has_permission(regular_user, Permission.PROPERTY_VIEW)

    # Cannot manage
    assert not RoleService.has_permission(regular_user, Permission.PROPERTY_CREATE)
    assert not RoleService.has_permission(regular_user, Permission.PROPERTY_UPDATE)
    assert not RoleService.has_permission(regular_user, Permission.PROPERTY_DELETE)
    assert not RoleService.has_permission(regular_user, Permission.PROPERTY_PUBLISH)

    # Cannot access admin features
    assert not RoleService.has_permission(regular_user, Permission.USER_VIEW)
    assert not RoleService.has_permission(regular_user, Permission.AUDIT_VIEW)
```

**Key Points:**
- Comprehensive test coverage (fixtures, unit tests, integration scenarios)
- Performance test for <1ms requirement
- Tests for all roles (admin, agent, user)
- Edge cases (unknown roles, missing permissions)
- Clear test names describing what they test
- Uses pytest and mocks (no database required)

---

## Implementation Guidelines

1. **Follow Existing Patterns:**
   - File headers: Use architecture documentation headers (see security.py example)
   - Type hints: Full type annotations throughout
   - Docstrings: Google-style docstrings with Args/Returns/Examples
   - Error handling: HTTPException with appropriate status codes

2. **Clean Architecture:**
   - permissions.py: Pure data definitions (no logic)
   - decorators.py: API layer (FastAPI integration)
   - role_service.py: Business logic layer
   - No circular dependencies

3. **Performance:**
   - In-memory lookups only (no database queries)
   - Dict-based lookups for O(1) access
   - No external API calls
   - Target: <1ms per permission check (typically <100μs)

4. **Security:**
   - Fail closed (deny by default)
   - Clear error messages for debugging
   - Type safety via enums
   - No role name typos via enum usage

5. **Extensibility:**
   - Easy to add new permissions to enum
   - Easy to modify role-permission mappings
   - Clear structure for future enhancements

---

## Testing Requirements

Run tests with:
```bash
cd apps/server
pytest tests/test_rbac.py -v
```

Expected results:
- All tests pass
- Performance test shows <1ms (typically <0.01ms)
- No warnings or errors

---

## Success Criteria

- [ ] All 5 files created/modified as specified
- [ ] Permission enum complete with all resource permissions
- [ ] ROLE_PERMISSIONS mapping correctly assigns permissions to roles
- [ ] `@require_permission` decorator works on async route handlers
- [ ] RoleService provides all utility methods
- [ ] Tests pass with good coverage (aim for 95%+)
- [ ] Performance requirement met (<1ms permission checks)
- [ ] File headers follow project patterns
- [ ] Type hints throughout all code
- [ ] Proper error handling with HTTPException
- [ ] No database queries in permission checking logic

---

## Notes

- User model already exists with role field: `user`, `agent`, `admin` (NOT `guest`)
- Existing auth uses Clerk via `get_clerk_user` dependency
- This task creates infrastructure only - no endpoint integration yet
- Future tasks will use these components in actual API routes
- Performance is critical - this runs on EVERY protected API call

---

**END OF SPECIFICATION**
