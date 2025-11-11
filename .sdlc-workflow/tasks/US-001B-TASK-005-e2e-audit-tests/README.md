# Task: TASK-005 - E2E Audit Logging Tests

**Story:** US-001B - Role-Based Access Control Implementation
**Type:** test
**Status:** NOT_STARTED
**Created:** 2025-11-07
**Branch:** feat/TASK-002-US-001B (shared)

## Description

Create end-to-end tests for the audit logging system to verify that:
- Audit context is properly set by middleware
- Audit logs are created for all mutations
- Audit history can be retrieved
- The system fails gracefully without breaking requests

## Objectives

1. Test audit middleware context propagation
2. Test audit logging for CRUD operations
3. Test audit history retrieval
4. Test fail-safe behavior (audit errors don't break requests)
5. Test performance (<10ms overhead)

## Technical Requirements

### Test Files to Create

**Backend Integration Tests (`apps/server/tests/integration/test_audit_middleware.py`)**
```python
"""
Integration tests for audit middleware and audit logging.

Tests the full flow: Request → Middleware → Audit Context → Service → Database
"""

@pytest.mark.asyncio
async def test_audit_middleware_sets_context():
    """Test middleware sets audit context from request"""
    # Make authenticated request
    # Verify context contains user_id, ip_address, user_agent

@pytest.mark.asyncio
async def test_audit_log_created_for_mutation():
    """Test audit log created for POST/PUT/PATCH/DELETE"""
    # Make mutation request (e.g., update user role)
    # Verify audit_log record created
    # Verify correct entity_type, entity_id, action, performed_by

@pytest.mark.asyncio
async def test_audit_context_isolated_per_request():
    """Test each request has isolated audit context"""
    # Make concurrent requests with different users
    # Verify contexts don't mix

@pytest.mark.asyncio
async def test_get_entity_history():
    """Test retrieving audit history for an entity"""
    # Create entity
    # Update entity multiple times
    # Retrieve history
    # Verify all changes tracked in DESC order

@pytest.mark.asyncio
async def test_audit_failure_doesnt_break_request():
    """Test fail-safe behavior when audit logging fails"""
    # Mock audit service to raise exception
    # Make mutation request
    # Verify request succeeds (audit failure logged but not raised)

@pytest.mark.asyncio
async def test_read_only_requests_skip_audit():
    """Test GET requests don't create audit logs"""
    # Make GET request
    # Verify no audit log created (only context set)

@pytest.mark.asyncio
async def test_audit_middleware_performance():
    """Test middleware adds <10ms overhead"""
    # Make 100 requests
    # Measure average latency increase
    # Assert < 10ms overhead
```

**Frontend E2E Tests (`apps/frontend/tests/e2e/audit.spec.ts`)**
```typescript
/**
 * E2E tests for audit logging from frontend perspective
 */

test('admin action creates audit trail', async ({ page }) => {
  // Login as admin
  // Perform action (e.g., update user role)
  // Check backend audit_log table (via API)
  // Verify audit log exists with correct data
});

test('agent action creates audit trail', async ({ page }) => {
  // Login as agent
  // Create property
  // Verify audit log created
});

test('audit history visible in admin panel', async ({ page }) => {
  // Login as admin
  // Navigate to entity history view
  // Verify audit logs displayed
  // Verify chronological order
});
```

## Acceptance Criteria

### Backend Tests
- [ ] Middleware context propagation tested
- [ ] Audit log creation for mutations tested
- [ ] Audit history retrieval tested
- [ ] Context isolation (thread-safety) verified
- [ ] Fail-safe behavior tested
- [ ] Read-only requests verified to skip audit
- [ ] Performance benchmark (<10ms overhead) verified

### E2E Tests
- [ ] Admin actions create audit trail (visible in DB)
- [ ] Agent actions create audit trail
- [ ] Audit history visible in UI (future: when UI exists)

### Coverage
- [ ] Integration test coverage > 90%
- [ ] All critical paths tested
- [ ] Error scenarios covered

## Files to Create/Modify

### New Files
- `apps/server/tests/integration/test_audit_middleware.py` - Integration tests
- `apps/frontend/tests/e2e/audit.spec.ts` - E2E tests (optional if no UI yet)

### Modify
- `apps/server/tests/conftest.py` - Add audit test fixtures if needed

## Dependencies

### Completed Dependencies
- TASK-002: Database migrations (audit_log table exists) ✅
- TASK-003: RBAC components (for authenticated requests) ✅
- TASK-004: Audit logging system implementation ✅

### External Dependencies
- pytest-asyncio for async tests
- Playwright for E2E tests (already installed)
- Test database fixtures

## Testing Strategy

### Integration Tests (Backend)
**Goal:** Verify audit system works end-to-end within backend

**Approach:**
1. Use test database with audit_log table
2. Make real HTTP requests to FastAPI app
3. Check database for audit records
4. Test both success and failure paths

**Tools:**
- pytest with async support
- FastAPI TestClient (async)
- SQLAlchemy test fixtures

### E2E Tests (Frontend/Backend)
**Goal:** Verify audit logging from user perspective

**Approach:**
1. Playwright tests with authenticated sessions
2. Perform user actions
3. Verify audit logs via API or direct DB check
4. Test across different roles (admin, agent)

**Tools:**
- Playwright
- Test user accounts from Clerk
- Database inspection utilities

## Implementation Notes

### Test Database Setup
- Use `db_session` fixture from conftest.py
- Ensure audit_log table exists in test DB
- Clean audit_log table between tests

### Authentication in Tests
- Use test Clerk tokens for authenticated requests
- Test with different roles (admin, agent, user)
- Verify audit context includes correct user_id

### Performance Testing
- Use `time.perf_counter()` for precise timing
- Run 100 requests to get average
- Compare with/without audit middleware

### Fail-Safe Testing
- Mock `AuditService.log_action()` to raise exception
- Verify request succeeds despite audit failure
- Check logs for audit error messages

## Success Criteria Checklist

- [ ] All backend integration tests passing
- [ ] All E2E tests passing (if applicable)
- [ ] Test coverage > 90% for audit components
- [ ] Performance benchmark < 10ms overhead verified
- [ ] Fail-safe behavior confirmed (no request breakage)
- [ ] Context isolation (thread-safety) verified
- [ ] Documentation updated

## Notes

### Current State
- Audit logging system implemented (TASK-004) ✅
- Middleware registered in main.py ✅
- No existing tests for audit system ❌

### Why E2E Tests Matter
- Verify the entire flow works: Request → Middleware → Context → Service → DB
- Catch integration issues that unit tests miss
- Validate performance in realistic scenarios
- Ensure fail-safe behavior under error conditions

### Future Enhancements
After this task, consider:
- Audit log viewer UI in admin dashboard
- Audit log retention policies
- Audit log export/archiving
- Real-time audit monitoring
