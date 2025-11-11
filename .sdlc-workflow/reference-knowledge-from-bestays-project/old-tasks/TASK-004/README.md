# Task: TASK-004 - Audit Logging System

**Story:** US-001B - Role-Based Access Control Implementation
**Type:** feat
**Status:** IN_PROGRESS
**Created:** 2025-11-07
**Branch:** feat/TASK-002-US-001B (shared)

## Description

Implement automatic audit logging middleware and service to track all entity changes in the audit_log table.

## Objectives

1. Create audit logging service
2. Implement FastAPI middleware for automatic logging
3. Add audit context to requests
4. Create audit helper functions
5. Test audit trail generation

## Technical Requirements

### Audit Service
```python
class AuditService:
    async def log_action(
        entity_type: str,
        entity_id: UUID,
        action: str,
        performed_by: int,
        changes: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> AuditLog:
        """Log an action to the audit_log table"""

    async def get_entity_history(
        entity_type: str,
        entity_id: UUID
    ) -> list[AuditLog]:
        """Get audit history for an entity"""
```

### Middleware
```python
class AuditMiddleware:
    """Automatically log API requests that modify data"""

    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, request: Request, call_next):
        # Capture request details
        # Execute request
        # If success and is mutation, log to audit
```

### Context Manager
```python
@contextmanager
def audit_context(user: User, request: Request):
    """Provide audit context for operations"""
    yield AuditContext(
        user=user,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
```

## Acceptance Criteria

- [ ] Audit service can log actions to database
- [ ] Middleware automatically logs POST/PUT/DELETE requests
- [ ] Property changes are tracked with before/after values
- [ ] User actions include IP and user agent
- [ ] Audit history can be retrieved by entity
- [ ] System user is used for automated operations

## Files to Create/Modify

- `apps/server/src/server/api/services/audit_service.py` - Audit service
- `apps/server/src/server/api/middleware/audit.py` - Audit middleware
- `apps/server/src/server/api/context/audit.py` - Audit context
- `apps/server/src/server/main.py` - Register middleware
- `apps/server/tests/test_audit.py` - Audit tests

## Dependencies

- TASK-002: audit_log table exists
- TASK-003: RBAC components for user context
- SQLAlchemy models (AuditLog)
- FastAPI middleware system

## Notes

The audit system should:
- Be transparent to endpoint developers
- Automatically capture changes
- Include enough context for compliance
- Not significantly impact performance
- Handle errors gracefully (don't break requests if audit fails)