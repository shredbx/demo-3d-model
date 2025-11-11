# TASK-004 Decisions Log

## Decision 1: Use Middleware for Automatic Audit Logging

**Date:** 2025-11-07

**Context:**
Need to automatically capture audit logs for all mutations without requiring developers to manually call audit service in every endpoint.

**Options Considered:**
1. Manual audit calls in each endpoint
2. Middleware to automatically capture mutations
3. Database triggers

**Decision:** Use middleware (Option 2)

**Rationale:**
- **Pros:**
  - Automatic - no developer action required
  - Centralized - single place to maintain logic
  - Consistent - all mutations logged the same way
  - Python-level - can access request context easily
- **Cons:**
  - Adds overhead to every request (mitigated by skipping read-only requests)
  - Less granular control (can still be overridden if needed)

**Rejected Alternatives:**
- Manual calls: Too error-prone, developers will forget
- Database triggers: Hard to access request context (user, IP, user agent)

---

## Decision 2: Use contextvars for Thread-Safe Context Propagation

**Date:** 2025-11-07

**Context:**
Need to pass user_id, ip_address, user_agent from middleware to service layer without explicit parameter passing.

**Options Considered:**
1. Pass as parameters through every function
2. Store in request.state
3. Use contextvars (thread-safe context)

**Decision:** Use contextvars (Option 3)

**Rationale:**
- **Pros:**
  - Thread-safe in async environments
  - No parameter drilling
  - Pythonic and standard library
  - Isolated per-request (no cross-request contamination)
- **Cons:**
  - Slightly less explicit than parameter passing
  - Requires understanding of contextvars

**Rejected Alternatives:**
- Parameter passing: Too verbose, pollutes function signatures
- request.state: Not accessible in service layer without passing request object

---

## Decision 3: Fail-Safe Audit Logging

**Date:** 2025-11-07

**Context:**
If audit logging fails (database error, etc.), should we fail the request or continue?

**Decision:** Continue request, log error

**Rationale:**
- Audit logging is secondary concern - don't break primary functionality
- Log errors for monitoring and alerting
- Can fix issues and backfill audit logs later if needed
- Better user experience (request succeeds even if audit fails)

**Trade-off:**
- May miss audit logs if system is degraded
- Acceptable risk - audit is for compliance/debugging, not critical path

---

## Decision 4: Service Layer Architecture

**Date:** 2025-11-07

**Context:**
Should audit service be in `server/api/services/` or `server/services/`?

**Decision:** Place in `server/api/services/` (with role_service.py)

**Rationale:**
- Follows existing pattern for RBAC services
- API-specific service (tightly coupled to request/response cycle)
- Consistent with project structure
- Makes it clear this is part of the API layer, not domain services
