# TASK-004 Implementation Specification

## Objective

Implement audit logging system components:
1. AuditService - Core business logic
2. AuditMiddleware - Automatic mutation capture
3. Audit Context - Thread-safe context propagation
4. Integration with main app
5. Comprehensive tests

## Existing Code Context

### AuditLog Model (Already Exists)
Location: `apps/server/src/server/models/audit.py`

```python
class AuditLog(Base):
    __tablename__ = "audit_log"

    id: UUID (PK)
    entity_type: str (indexed)
    entity_id: UUID (indexed)
    action: str
    performed_by: Optional[int] (FK to users.id, indexed)
    performed_at: datetime (indexed)
    changes: Optional[dict] (JSONB)
    ip_address: Optional[str]
    user_agent: Optional[str]

    # Relationship
    user: User (lazy="select")
```

### Service Pattern (Reference)
Location: `apps/server/src/server/api/services/role_service.py`, `apps/server/src/server/services/user_service.py`

**Key Patterns:**
- File header with ARCHITECTURE, PATTERNS USED, DEPENDENCIES, INTEGRATION, TESTING
- Class-based services with static/instance methods
- Async methods for database operations
- Type hints for all parameters/returns
- Comprehensive docstrings with examples
- Singleton instance export

### Main App Structure
Location: `apps/server/src/server/main.py`

**Current Middleware Order:**
1. Rate limiting (via app.state.limiter)
2. CORS (via CORSMiddleware)
3. Exception handlers
4. **NEW: Audit middleware should go here**
5. Routers

## Implementation Details

### 1. Audit Context (`apps/server/src/server/api/context/audit.py`)

```python
"""
Audit Context - Thread-Safe Request Context

ARCHITECTURE:
  Layer: Infrastructure (Context Management)
  Pattern: Context Variables (Python stdlib)

PATTERNS USED:
  - ContextVars: Thread-safe per-request storage
  - Immutable Context: Set once per request

DEPENDENCIES:
  External: contextvars (stdlib)
  Internal: None

INTEGRATION:
  - Middleware: Sets context at request start
  - Services: Read context when creating audit logs

TESTING:
  - Test File: tests/test_audit.py
  - Coverage Target: 100% (simple getters/setters)
"""

from contextvars import ContextVar
from typing import Optional

# Thread-safe context for audit information
audit_context: ContextVar[dict] = ContextVar('audit_context', default={})

def set_audit_context(
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> None:
    """Set audit context for current request.

    Called by middleware at request start to propagate context
    throughout the request lifecycle.

    Args:
        user_id: User ID from authenticated request
        ip_address: Client IP address
        user_agent: Browser user agent string

    Example:
        set_audit_context(
            user_id=123,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0..."
        )
    """
    audit_context.set({
        'user_id': user_id,
        'ip_address': ip_address,
        'user_agent': user_agent
    })

def get_audit_context() -> dict:
    """Get current audit context.

    Returns:
        dict: Current audit context with keys:
            - user_id: Optional[int]
            - ip_address: Optional[str]
            - user_agent: Optional[str]

    Example:
        context = get_audit_context()
        user_id = context.get('user_id')
    """
    return audit_context.get()

def clear_audit_context() -> None:
    """Clear audit context (for testing).

    Not typically used in production - context is automatically
    isolated per request by contextvars.
    """
    audit_context.set({})
```

### 2. Audit Service (`apps/server/src/server/api/services/audit_service.py`)

```python
"""
Audit Service - Change Tracking Business Logic

ARCHITECTURE:
  Layer: Service (Business Logic)
  Pattern: Service Layer + Repository Pattern

PATTERNS USED:
  - Service Layer: Encapsulates audit business logic
  - Repository Pattern: Database access abstraction
  - Context Pattern: Read audit context from contextvars

DEPENDENCIES:
  External: sqlalchemy
  Internal:
    - server.models.audit (AuditLog model)
    - server.api.context.audit (audit context)

INTEGRATION:
  - Middleware: Automatically calls log_action()
  - Manual: Can be called directly from endpoints
  - Context: Reads user info from audit_context

TESTING:
  - Test File: tests/test_audit.py
  - Coverage Target: 90%
  - Test async database operations with fixtures
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.api.context.audit import get_audit_context
from server.models.audit import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging operations.

    Provides methods to create audit logs and retrieve entity history.
    Automatically reads user context from audit_context.
    """

    @staticmethod
    async def log_action(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
        action: str,
        performed_by: Optional[int] = None,
        changes: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[AuditLog]:
        """Log an action to the audit_log table.

        If context parameters (performed_by, ip_address, user_agent) are
        not provided, they will be read from the current audit context.

        Args:
            db: Database session
            entity_type: Type of entity (e.g., 'property', 'user')
            entity_id: UUID of the entity
            action: Action performed (create, update, delete, publish)
            performed_by: User ID (defaults to context user_id)
            changes: JSONB with before/after values
            ip_address: IP address (defaults to context ip_address)
            user_agent: User agent (defaults to context user_agent)

        Returns:
            Created AuditLog record, or None if error

        Example:
            audit_log = await AuditService.log_action(
                db=db,
                entity_type="property",
                entity_id=property.id,
                action="create",
                changes={"new": property_data}
            )
        """
        try:
            # Read from context if not provided
            context = get_audit_context()
            if performed_by is None:
                performed_by = context.get('user_id')
            if ip_address is None:
                ip_address = context.get('ip_address')
            if user_agent is None:
                user_agent = context.get('user_agent')

            # Create audit log record
            audit_log = AuditLog(
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                performed_by=performed_by,
                changes=changes,
                ip_address=ip_address,
                user_agent=user_agent
            )

            db.add(audit_log)
            await db.commit()
            await db.refresh(audit_log)

            logger.info(
                f"Audit log created: {entity_type}:{entity_id} "
                f"action={action} user={performed_by}"
            )

            return audit_log

        except Exception as e:
            # Fail-safe: Log error but don't break the request
            logger.error(f"Failed to create audit log: {e}", exc_info=True)
            await db.rollback()
            return None

    @staticmethod
    async def get_entity_history(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
        limit: int = 100
    ) -> list[AuditLog]:
        """Get audit history for an entity.

        Returns most recent audit logs first (DESC order).

        Args:
            db: Database session
            entity_type: Type of entity (e.g., 'property')
            entity_id: UUID of the entity
            limit: Maximum number of records to return (default 100)

        Returns:
            List of AuditLog records, newest first

        Example:
            history = await AuditService.get_entity_history(
                db=db,
                entity_type="property",
                entity_id=property_id,
                limit=50
            )
        """
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id
            )
            .order_by(AuditLog.performed_at.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())


# Helper functions for common operations

async def audit_property_create(
    db: AsyncSession,
    property_id: UUID,
    property_data: dict,
    user_id: Optional[int] = None
) -> Optional[AuditLog]:
    """Helper for property creation audit.

    Args:
        db: Database session
        property_id: UUID of created property
        property_data: Property data (for changes.new)
        user_id: Override user_id (defaults to context)

    Returns:
        Created AuditLog or None
    """
    return await AuditService.log_action(
        db=db,
        entity_type="property",
        entity_id=property_id,
        action="create",
        performed_by=user_id,
        changes={"new": property_data}
    )


async def audit_property_update(
    db: AsyncSession,
    property_id: UUID,
    before: dict,
    after: dict,
    user_id: Optional[int] = None
) -> Optional[AuditLog]:
    """Helper for property update audit.

    Args:
        db: Database session
        property_id: UUID of updated property
        before: Property data before update
        after: Property data after update
        user_id: Override user_id (defaults to context)

    Returns:
        Created AuditLog or None
    """
    return await AuditService.log_action(
        db=db,
        entity_type="property",
        entity_id=property_id,
        action="update",
        performed_by=user_id,
        changes={"before": before, "after": after}
    )


async def audit_property_delete(
    db: AsyncSession,
    property_id: UUID,
    property_data: dict,
    user_id: Optional[int] = None
) -> Optional[AuditLog]:
    """Helper for property deletion audit.

    Args:
        db: Database session
        property_id: UUID of deleted property
        property_data: Property data (for changes.deleted)
        user_id: Override user_id (defaults to context)

    Returns:
        Created AuditLog or None
    """
    return await AuditService.log_action(
        db=db,
        entity_type="property",
        entity_id=property_id,
        action="delete",
        performed_by=user_id,
        changes={"deleted": property_data}
    )


# Singleton instance
audit_service = AuditService()
```

### 3. Audit Middleware (`apps/server/src/server/api/middleware/audit.py`)

```python
"""
Audit Middleware - Automatic Mutation Capture

ARCHITECTURE:
  Layer: Middleware (Infrastructure)
  Pattern: Starlette BaseHTTPMiddleware

PATTERNS USED:
  - Middleware Pattern: Intercept requests/responses
  - Context Pattern: Set audit context for request
  - Fail-Safe Pattern: Don't break requests on audit failure

DEPENDENCIES:
  External: starlette
  Internal:
    - server.api.context.audit (set_audit_context)
    - server.api.services.audit_service (AuditService)

INTEGRATION:
  - main.py: Registered after CORS middleware
  - All endpoints: Automatically logs mutations

TESTING:
  - Test File: tests/test_audit.py
  - Coverage Target: 85%
  - Test mutation capture, read-only skip, errors
"""

import logging
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from server.api.context.audit import set_audit_context

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log mutations.

    Behavior:
    - Sets audit context (user, IP, user agent) at request start
    - Logs mutations (POST, PUT, PATCH, DELETE) on success
    - Skips read-only requests (GET, OPTIONS, HEAD)
    - Fails gracefully if audit logging fails

    Performance:
    - <1ms overhead for read-only requests (context set only)
    - <10ms overhead for mutations (includes database write)
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request and log mutations.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint in chain

        Returns:
            Response from downstream handler
        """
        # Extract user info from request (if authenticated)
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id

        # Extract IP address
        ip_address = request.client.host if request.client else None

        # Extract user agent
        user_agent = request.headers.get("user-agent")

        # Set audit context for this request
        set_audit_context(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Skip audit logging for read-only requests
        if request.method in ("GET", "OPTIONS", "HEAD"):
            return await call_next(request)

        # Execute request
        response = await call_next(request)

        # Only log successful mutations (2xx status codes)
        if 200 <= response.status_code < 300:
            # Future: Extract entity info from response and log
            # For now, just set context (services will use it)
            logger.debug(
                f"Mutation logged: {request.method} {request.url.path} "
                f"status={response.status_code} user={user_id}"
            )

        return response
```

### 4. Main App Integration

**File:** `apps/server/src/server/main.py`

**Changes:**
1. Import: `from server.api.middleware.audit import AuditMiddleware`
2. Add middleware after CORS (around line 108):
   ```python
   # Audit logging middleware (automatically log mutations)
   app.add_middleware(AuditMiddleware)
   ```

**Placement:** After CORS middleware, before exception handlers

### 5. Tests (`apps/server/tests/test_audit.py`)

**Test Coverage:**

1. **Audit Context Tests:**
   - `test_set_and_get_audit_context()` - Basic set/get
   - `test_audit_context_isolated()` - Verify thread-safety
   - `test_clear_audit_context()` - Clear functionality

2. **AuditService Tests:**
   - `test_log_action_basic()` - Create audit log with all params
   - `test_log_action_from_context()` - Create audit log from context
   - `test_log_action_handles_errors()` - Fail-safe behavior
   - `test_get_entity_history()` - Retrieve history
   - `test_get_entity_history_order()` - Verify DESC order
   - `test_get_entity_history_limit()` - Pagination

3. **Helper Function Tests:**
   - `test_audit_property_create()` - Property create helper
   - `test_audit_property_update()` - Property update helper
   - `test_audit_property_delete()` - Property delete helper

4. **Middleware Tests:**
   - `test_middleware_sets_context()` - Context propagation
   - `test_middleware_skips_readonly()` - Skip GET/OPTIONS/HEAD
   - `test_middleware_logs_mutations()` - POST/PUT/PATCH/DELETE
   - `test_middleware_handles_errors()` - Fail-safe behavior
   - `test_middleware_performance()` - <10ms overhead

**Test Pattern (follow test_rbac.py):**
```python
"""
Tests for Audit Logging System

Tests cover:
- Audit context (set/get/clear)
- AuditService methods (log_action, get_entity_history)
- Helper functions (audit_property_*)
- Middleware (context propagation, mutation capture)
- Error handling (fail-safe behavior)
- Performance (<10ms overhead)
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Fixtures
@pytest.fixture
async def audit_context():
    """Clean audit context for each test."""
    from server.api.context.audit import clear_audit_context
    clear_audit_context()
    yield
    clear_audit_context()

# Test example
@pytest.mark.asyncio
async def test_log_action_basic(db_session: AsyncSession):
    """Test creating audit log with all parameters."""
    # ... implementation
```

## File Header Template

Every new file should start with:

```python
"""
<Title> - <One-line description>

ARCHITECTURE:
  Layer: <Layer name>
  Pattern: <Pattern name>

PATTERNS USED:
  - <Pattern>: <Description>

DEPENDENCIES:
  External: <packages>
  Internal: <modules>

INTEGRATION:
  - <Component>: <How it integrates>

TESTING:
  - Test File: <path>
  - Coverage Target: <percentage>
"""
```

## Success Criteria Checklist

- [ ] `audit.py` context module created with set/get/clear functions
- [ ] `audit_service.py` created with AuditService class
- [ ] `audit_service.py` includes helper functions (property_create, etc.)
- [ ] `audit.py` middleware created with AuditMiddleware class
- [ ] `main.py` updated to register middleware after CORS
- [ ] `test_audit.py` created with comprehensive tests
- [ ] All tests pass with >85% coverage
- [ ] Performance benchmarks show <10ms overhead
- [ ] Error handling is fail-safe (doesn't break requests)
- [ ] Type hints on all functions
- [ ] Docstrings with examples on all public methods
- [ ] File headers follow project pattern

## Additional Notes

- **Performance:** Audit logging should not significantly impact request latency
- **Fail-Safe:** Errors in audit system must not break main application
- **Context Isolation:** Each request has isolated audit context (via contextvars)
- **Flexibility:** Middleware sets context, but manual calls are also supported
- **Future:** Middleware can be enhanced to extract entity info from response bodies
