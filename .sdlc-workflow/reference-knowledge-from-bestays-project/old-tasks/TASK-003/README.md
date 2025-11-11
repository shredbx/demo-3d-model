# Task: TASK-003 - Core RBAC Components

**Story:** US-001B - Role-Based Access Control Implementation
**Type:** feat
**Status:** IN_PROGRESS
**Created:** 2025-11-07
**Branch:** feat/TASK-002-US-001B (shared with TASK-002)

## Description

Implement core RBAC components including permission decorators, role checking utilities, and base authorization patterns for the FastAPI backend.

## Objectives

1. Create permission decorator for FastAPI routes
2. Implement role checking utilities
3. Create base authorization service
4. Add RBAC to existing endpoints
5. Create permission constants/enums

## Technical Requirements

### Permission Decorator
```python
@require_permission(Permission.PROPERTY_CREATE)
async def create_property(...):
    pass
```

### Role Utilities
```python
class RoleService:
    def has_permission(user: User, permission: Permission) -> bool
    def check_role(user: User, role: Role) -> bool
    def get_permissions(role: Role) -> list[Permission]
```

### Permission Enum
```python
class Permission(str, Enum):
    # Property permissions
    PROPERTY_VIEW = "property:view"
    PROPERTY_CREATE = "property:create"
    PROPERTY_UPDATE = "property:update"
    PROPERTY_DELETE = "property:delete"
    PROPERTY_PUBLISH = "property:publish"

    # User management
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Admin only
    AUDIT_VIEW = "audit:view"
```

## Acceptance Criteria

- [ ] Permission decorator works on FastAPI routes
- [ ] Role checking utilities implemented
- [ ] Permission enum with all permissions
- [ ] Role-permission mapping defined
- [ ] Tests for permission checking
- [ ] Documentation for RBAC usage

## Files to Create/Modify

- `apps/server/api/auth/permissions.py` - Permission enum and mappings
- `apps/server/api/auth/decorators.py` - Permission decorator
- `apps/server/api/services/role_service.py` - Role checking utilities
- `apps/server/api/deps.py` - Update dependencies for RBAC
- `apps/server/tests/test_rbac.py` - RBAC tests

## Dependencies

- TASK-002: Database migrations (audit_log table)
- Clerk authentication (already integrated)
- User model with role field

## Notes

This task implements the core authorization logic that will be used throughout the application. The permission system should be:
- Easy to use (decorators)
- Performant (<1ms checks)
- Extensible (easy to add new permissions)
- Well-tested

**Next:** TASK-004 will implement audit logging using these components.