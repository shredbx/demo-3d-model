# Task: TASK-005 - Update Existing Endpoints with RBAC

**Story:** US-001B - Role-Based Access Control Implementation
**Type:** refactor
**Status:** NOT_STARTED
**Created:** 2025-11-06
**Branch:** refactor/TASK-005-US-001B

## Description

Refactor existing API endpoints to use the new granular permission system and add audit logging to all data modifications.

## Objectives

1. Replace role-based checks with permission-based checks
2. Add audit logging to all CRUD operations
3. Update property endpoints with audit fields
4. Add created_by/updated_by tracking
5. Update API documentation

## Endpoints to Update

### Health Check Endpoints
```python
# /api/v1/health/secure
# FROM:
dependencies=[Depends(require_admin)]

# TO:
dependencies=[Depends(require_permission(Permission.SYSTEM_ADMIN))]
```

### User Endpoints
```python
# /api/v1/users/me
# Add audit logging for profile updates
audit = Depends(audit_action("update_profile"))
```

### Property Endpoints (Future)
```python
# /api/v1/properties (POST)
dependencies=[Depends(require_permission(Permission.CREATE_PROPERTY))]
audit = Depends(audit_action("create_property"))

# /api/v1/properties/{id} (PUT)
dependencies=[Depends(require_permission(Permission.EDIT_PROPERTY))]
audit = Depends(audit_action("update_property"))

# /api/v1/properties/{id} (DELETE)
dependencies=[Depends(require_permission(Permission.DELETE_PROPERTY))]
audit = Depends(audit_action("delete_property"))

# /api/v1/properties/{id}/publish (POST)
dependencies=[Depends(require_permission(Permission.PUBLISH_PROPERTY))]
audit = Depends(audit_action("publish_property"))
```

## Code Changes Required

### Before (Current)
```python
@router.get("/secure", dependencies=[Depends(require_admin)])
async def secure_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": "Admin access granted", "user": current_user.email}
```

### After (With RBAC)
```python
@router.get(
    "/secure",
    dependencies=[Depends(require_permission(Permission.SYSTEM_ADMIN))]
)
async def secure_endpoint(
    current_user: User = Depends(get_current_user),
    audit: AuditDependency = Depends(audit_action("access_secure_endpoint"))
):
    # Log the access
    audit("system", "secure_endpoint", {"accessed_by": current_user.email})

    return {"message": "Admin access granted", "user": current_user.email}
```

## Acceptance Criteria

- [ ] All role checks replaced with permission checks
- [ ] Audit logging added to data modifications
- [ ] created_by/updated_by populated on creates/updates
- [ ] OpenAPI documentation updated
- [ ] No breaking changes to API contracts
- [ ] All existing tests still pass
- [ ] New tests for permission checks

## Files to Modify

- `apps/server/api/routers/health.py` - Update admin endpoint
- `apps/server/api/routers/users.py` - Add audit logging
- `apps/server/api/deps/__init__.py` - Export new dependencies
- `apps/server/tests/` - Update tests for new permissions

## Dependencies

- TASK-002 completed (database ready)
- TASK-003 completed (permission system ready)
- TASK-004 completed (audit system ready)

## Migration Strategy

1. Update one endpoint at a time
2. Test each endpoint thoroughly
3. Update API documentation
4. Verify no breaking changes
5. Update integration tests

## Notes

This is a refactoring task that updates existing code to use the new RBAC system. Must ensure backward compatibility and no breaking changes to API contracts.