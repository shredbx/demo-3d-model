# Task Decisions: US-001B-TASK-002

This document records key architectural and implementation decisions made during this task.

---

## Decision 1: Use UUID for Audit Log Primary Key

**Date:** 2025-11-06
**Context:** Choosing primary key type for audit_log table

**Options Considered:**
1. Serial/BIGSERIAL (auto-increment integer)
2. UUID (gen_random_uuid())

**Decision:** UUID

**Rationale:**
- Consistent with modern best practices
- Prevents ID enumeration attacks
- Easier to merge data from multiple sources
- Future-proof for distributed systems
- PostgreSQL has native UUID support

**Trade-offs:**
- Slightly larger storage (16 bytes vs 8 bytes)
- Slightly slower indexing (negligible for audit logs)
- Worth it for security and flexibility

---

## Decision 2: JSONB for Changes Column

**Date:** 2025-11-06
**Context:** How to store before/after state of changes

**Options Considered:**
1. TEXT (JSON string)
2. JSON
3. JSONB

**Decision:** JSONB

**Rationale:**
- Binary format = faster queries
- Can index specific fields
- Automatic validation
- Better compression
- Standard in modern PostgreSQL apps

**Trade-offs:**
- Slightly slower writes (negligible)
- All benefits outweigh minimal cost

---

## Decision 3: Nullable performed_by Column

**Date:** 2025-11-06
**Context:** Should audit log require a user?

**Options Considered:**
1. NOT NULL (require user)
2. NULL allowed (optional user)

**Decision:** NULL allowed

**Rationale:**
- System operations may not have a user context
- Migrations and seeds are system-level
- Better to capture partial data than fail
- Can add system user later if needed

**Trade-offs:**
- Need to handle NULL in queries
- But provides flexibility for edge cases

---

## Decision 4: Properties Table - Create or Alter?

**Date:** 2025-11-06
**Context:** Properties table may or may not exist

**Options Considered:**
1. Assume exists, only ALTER
2. Assume doesn't exist, only CREATE
3. Check existence, CREATE or ALTER

**Decision:** Check existence dynamically in migration

**Rationale:**
- Project is in flux, unclear if properties table exists
- Migration should be idempotent
- Better DX - works regardless of current state
- Standard Alembic pattern

**Implementation:**
```python
# Check if table exists
conn = op.get_bind()
inspector = inspect(conn)
table_exists = 'properties' in inspector.get_table_names()

if table_exists:
    # Add columns
else:
    # Create table
```

---

## Decision 5: System User ID

**Date:** 2025-11-06
**Context:** What ID to use for system user?

**Options Considered:**
1. Auto-generate UUID
2. Fixed UUID across all environments
3. Special sentinel value like '00000000-0000-0000-0000-000000000000'

**Decision:** Fixed UUID via Clerk-compatible ID

**Rationale:**
- Clerk uses user_xxxxx format, so use 'system_00000000000000000000'
- Consistent across dev/staging/prod
- Easy to identify in logs
- Can be referenced in seed data
- ON CONFLICT DO NOTHING makes it safe to re-run

---

## Future Considerations

### Audit Log Retention Policy
- Not implemented in this task
- Future work: Auto-archive logs older than X months
- Consider: GDPR right-to-be-forgotten

### Audit Log Performance
- Current indexes should handle 100K-1M records easily
- Future optimization: Partitioning by date
- Future optimization: Separate hot/cold storage

### Property Table Evolution
- This task creates minimal schema
- Future tasks will add: location, pricing, amenities, etc.
- Audit fields will be ready from day 1
