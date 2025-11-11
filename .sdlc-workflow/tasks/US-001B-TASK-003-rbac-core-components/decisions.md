# Technical Decisions: US-001B-TASK-003

**Task:** RBAC Core Components
**Date:** 2025-11-07

---

## Decision Log

### Decision 1: In-Memory Permission Mapping vs Database

**Context:**
- Need to check permissions on every API request
- Performance requirement: <1ms per check
- Roles and permissions are relatively static (not user-configurable)

**Options Considered:**
1. **Database lookup** - Query role_permissions table on each check
2. **In-memory mapping** - Python dict mapping roles to permissions
3. **Cached database** - Query once, cache in Redis/memory

**Decision: In-memory mapping (Option 2)**

**Rationale:**
- Simplest implementation (no external dependencies)
- Fastest performance (<1ms guaranteed, sub-microsecond actually)
- Roles and permissions are code-defined, not runtime-configured
- Follows existing pattern in clerk_deps.py (role checks are in code)
- No cache invalidation complexity
- Easy to test and maintain

**Trade-offs:**
- Less flexible (need code deploy to change permissions)
- Acceptable because: Bestays doesn't need runtime permission configuration, roles are fixed

---

### Decision 2: Permission Enum vs String Constants

**Context:**
- Need to define permission identifiers
- Want type safety and autocomplete
- Want to avoid typos

**Options Considered:**
1. **String constants** - `PROPERTY_VIEW = "property:view"`
2. **Permission enum** - `Permission.PROPERTY_VIEW = "property:view"`
3. **Dataclass** - Permission objects with metadata

**Decision: Permission Enum (Option 2)**

**Rationale:**
- Type safety (mypy/IDE can catch typos)
- Autocomplete in IDEs
- Standard Python pattern for fixed sets of values
- Easy to iterate over all permissions
- Follows Python best practices

**Trade-offs:**
- Slightly more verbose than strings
- But: Provides better developer experience and catches errors at development time

---

### Decision 3: Decorator Pattern vs Dependency Injection

**Context:**
- Need to apply permission checks to FastAPI routes
- FastAPI supports both decorators and Depends()

**Options Considered:**
1. **Custom decorator** - `@require_permission(Permission.X)`
2. **Dependency function** - `Depends(check_permission(Permission.X))`
3. **Both** - Provide both interfaces

**Decision: Both (Option 3)**

**Rationale:**
- Decorator is cleaner for simple cases: `@require_permission(Permission.PROPERTY_VIEW)`
- Dependency is more flexible for complex logic
- Provides best of both worlds
- Decorator can wrap the dependency pattern internally

**Implementation:**
- Primary: Decorator pattern for ease of use
- Future: Can add dependency injection if needed
- Decorator checks user from existing auth dependency chain

---

### Decision 4: Role Service Location

**Context:**
- Need to provide utility methods for permission checking
- Choosing between services/ directory or auth/ directory

**Options Considered:**
1. **apps/server/api/services/role_service.py** - With other services
2. **apps/server/api/auth/role_service.py** - Grouped with auth code
3. **apps/server/core/rbac.py** - In core utilities

**Decision: apps/server/api/services/role_service.py (Option 1)**

**Rationale:**
- Consistent with existing project structure (services/ exists)
- Services contain business logic (permission checking is business logic)
- Easier discoverability (developers look in services/ for logic)
- auth/ directory for auth-specific dependencies and permissions definitions

**Trade-offs:**
- Auth code split across auth/ and services/
- But: Clear separation of concerns (definitions vs logic)

---

## Future Considerations

### Runtime Permission Configuration

**When to revisit:**
- If Bestays needs customer-configurable permissions (unlikely)
- If roles become more dynamic (e.g., custom agent roles)

**Migration path:**
- Add database table for role_permissions
- Add caching layer (Redis)
- Keep in-memory as fallback
- Add admin UI to manage permissions

### Audit Integration

**Next steps:**
- TASK-004 will integrate audit logging with permission checks
- Permission denied attempts should be logged
- Successful permission checks on sensitive operations should be logged

---

**Last Updated:** 2025-11-07
