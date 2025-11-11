# TASK-004: Implement Audit Logging System for RBAC

## Overview

Implement comprehensive audit logging system to track all entity changes (create, update, delete) for compliance and security.

## Context

- **Previous Work:**
  - TASK-002: Created `audit_log` table and `AuditLog` model
  - TASK-003: Implemented RBAC components (permissions, decorators, RoleService)

- **Business Model:**
  - Single-company: All agents work for Bestays
  - Need automatic audit trail for compliance (GDPR, security, debugging)

## Task Description

Build the audit logging infrastructure to automatically capture:
- What entity was changed (entity_type + entity_id)
- What action was performed (create, update, delete, publish)
- Who performed it (user_id from request context)
- When it happened (timestamp)
- What changed (before/after JSONB)
- Where it came from (IP address, user agent)

## Components to Implement

### 1. Audit Service (`apps/server/src/server/api/services/audit_service.py`)
- `log_action()` - Create audit log entry
- `get_entity_history()` - Retrieve audit history for an entity
- Helper functions for common operations (property_create, property_update, etc.)

### 2. Audit Middleware (`apps/server/src/server/api/middleware/audit.py`)
- Automatically log mutations (POST, PUT, PATCH, DELETE)
- Skip read-only requests (GET, OPTIONS, HEAD)
- Capture request context (user, IP, user agent)
- Handle errors gracefully (don't break requests)

### 3. Audit Context (`apps/server/src/server/api/context/audit.py`)
- Thread-safe context propagation using `contextvars`
- Store user_id, ip_address, user_agent for current request
- Accessible from anywhere in request lifecycle

### 4. Main App Integration (`apps/server/src/server/main.py`)
- Add `AuditMiddleware` after CORS middleware
- Ensure proper ordering (CORS → Audit → Routes)

### 5. Tests (`apps/server/tests/test_audit.py`)
- Unit tests for AuditService methods
- Integration tests for middleware capturing mutations
- Context propagation tests
- Error handling tests
- Performance tests (middleware should not significantly slow down requests)

## Files to Create

```
apps/server/src/server/api/services/audit_service.py
apps/server/src/server/api/middleware/audit.py
apps/server/src/server/api/context/audit.py
apps/server/tests/test_audit.py
```

## Files to Modify

```
apps/server/src/server/main.py (add middleware)
apps/server/src/server/api/services/__init__.py (export audit_service)
apps/server/src/server/api/middleware/__init__.py (export AuditMiddleware)
```

## Existing Code Patterns to Follow

### Service Pattern (from `user_service.py`, `role_service.py`)
- Use class with static/instance methods
- Async methods for database operations
- Type hints for all parameters and returns
- Comprehensive docstrings with examples
- File header with architecture documentation

### Testing Pattern (from `test_rbac.py`)
- Pytest fixtures for test data
- Mock objects for dependencies
- Test edge cases (missing data, errors)
- Performance benchmarks where applicable

### Architecture Documentation Pattern
- File header with ARCHITECTURE, PATTERNS USED, DEPENDENCIES, INTEGRATION, TESTING sections
- Clear separation of concerns
- Examples in docstrings

## Success Criteria

1. ✅ AuditService can create audit log entries
2. ✅ AuditService can retrieve entity history with pagination
3. ✅ Middleware automatically logs mutations (POST, PUT, PATCH, DELETE)
4. ✅ Middleware skips read-only requests (GET, OPTIONS, HEAD)
5. ✅ Context properly propagates user info throughout request lifecycle
6. ✅ Helper functions simplify common audit operations
7. ✅ Tests pass with >85% coverage
8. ✅ No significant performance impact (<10ms overhead per request)
9. ✅ Errors in audit system don't break main application flow

## Dependencies

- **TASK-002:** AuditLog model must exist
- **TASK-003:** RBAC system must be functional
- **SQLAlchemy async:** For database operations
- **FastAPI/Starlette:** For middleware integration
- **Python contextvars:** For thread-safe context

## Related Documentation

- `.claude/specs/clerk-authentication-integration-spec.md` - Auth patterns
- `apps/server/src/server/models/audit.py` - AuditLog model schema
- `apps/server/src/server/api/services/role_service.py` - Service pattern example
- `apps/server/src/server/services/user_service.py` - Async service example
- FastAPI Middleware docs: https://fastapi.tiangolo.com/advanced/middleware/
- Python contextvars docs: https://docs.python.org/3/library/contextvars.html

## Subagent

**Type:** dev-backend-fastapi

**Skills Required:**
- `@backend-fastapi` - FastAPI patterns and architecture
- `@backend-async-python` - Async/await patterns
- `@backend-python-testing` - Pytest patterns
- `@dev-code-quality` - Code quality standards
- `@dev-philosophy` - Development philosophy
