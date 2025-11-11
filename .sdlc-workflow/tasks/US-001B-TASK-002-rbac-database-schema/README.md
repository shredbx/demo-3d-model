# Task: RBAC Database Schema - Migrations and Models

**Story:** US-001B - Role-Based Access Control and Audit Logging
**Task ID:** TASK-002
**Created:** 2025-11-06
**Status:** IN_PROGRESS

---

## Objective

Create Alembic migrations and SQLAlchemy models to support RBAC audit logging:
1. Add audit_log table for tracking all property operations
2. Add/update properties table with audit fields (created_by, updated_by, published_by)
3. Create SQLAlchemy models (AuditLog, Property)
4. Seed system user for automated imports

---

## Scope

### Files to Create

**Migrations:**
- `apps/server/alembic/versions/[timestamp]_add_rbac_audit_tables.py`

**Models:**
- `apps/server/src/server/models/audit.py` (new)
- `apps/server/src/server/models/property.py` (new or update if exists)

**Updates:**
- `apps/server/src/server/models/__init__.py` (export new models)

### Subagents Needed

- [x] `dev-backend-fastapi` for migrations and models

---

## Acceptance Criteria

- [ ] AC-1: Audit log table created with all required columns (id, entity_type, entity_id, action, performed_by, performed_at, changes, ip_address, user_agent)
- [ ] AC-2: Proper indexes created for query optimization (entity, performed_by, performed_at)
- [ ] AC-3: Properties table has audit fields (created_by, updated_by, published_by) with foreign keys to users
- [ ] AC-4: System user seeded (system@bestays.app, role: system)
- [ ] AC-5: Migration is reversible (downgrade works correctly)
- [ ] AC-6: SQLAlchemy models follow project patterns (file headers, type hints, docstrings)
- [ ] AC-7: Models properly registered in __init__.py
- [ ] AC-8: Local testing successful (migrate up, down, up again)

---

## Implementation Notes

### Pattern to Follow

**File Headers:**
Follow the pattern in `apps/server/src/server/models/user.py`:
- Architecture section (Layer, Pattern)
- Dependencies section (External, Internal)
- Integration section
- Testing notes

**Model Structure:**
- Use SQLAlchemy 2.0 style with `Mapped[]` type hints
- Use `mapped_column()` for all columns
- Add docstrings for all classes and methods
- Include `__tablename__` and `__table_args__`

**Migration Structure:**
- Use Alembic's naming convention
- Include proper upgrade() and downgrade() functions
- Add comments explaining each change
- Use raw SQL for complex operations (indexes, constraints)

### Database Schema Details

#### Audit Log Table
```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,           -- e.g., 'property'
    entity_id UUID NOT NULL,                     -- ID of the entity
    action VARCHAR(50) NOT NULL,                 -- create, update, delete, publish
    performed_by UUID REFERENCES users(id),      -- Who made the change
    performed_at TIMESTAMP NOT NULL DEFAULT NOW(), -- When
    changes JSONB,                               -- What changed (before/after)
    ip_address VARCHAR(45),                      -- IPv4/IPv6
    user_agent TEXT                              -- Browser info
);

-- Indexes for common queries
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_performed_by ON audit_log(performed_by);
CREATE INDEX idx_audit_log_performed_at ON audit_log(performed_at DESC);
```

#### Properties Table
Check if table exists. If yes, add columns. If no, create table.

**If EXISTS:**
```sql
ALTER TABLE properties
    ADD COLUMN created_by UUID REFERENCES users(id),
    ADD COLUMN updated_by UUID REFERENCES users(id),
    ADD COLUMN published_by UUID REFERENCES users(id);
```

**If NOT EXISTS:**
```sql
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_published BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    published_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### System User Seed
```sql
INSERT INTO users (clerk_user_id, email, role, created_at, updated_at)
VALUES
    ('system_00000000000000000000', 'system@bestays.app', 'admin', NOW(), NOW())
ON CONFLICT (clerk_user_id) DO NOTHING;
```

### Dependencies

- Depends on: US-001 (users table exists) ✅
- Blocks: TASK-003 (audit logging service)

### References

- User Story: `.sdlc-workflow/stories/auth/US-001B-rbac-and-audit-logging.md`
- Existing User Model: `apps/server/src/server/models/user.py`
- Existing Migrations: `apps/server/alembic/versions/`
- Skills: `@.claude/skills/dev-philosophy/`, `@.claude/skills/dev-code-quality/`

---

## Estimated Effort

**Time Estimate:** 2-3 hours

**Breakdown:**
- Migration creation: 45 min
- Model creation: 45 min
- Testing (local): 30 min
- Documentation: 30 min

---

## Context

This is the foundation for audit logging in the Bestays platform. The audit_log table will track all changes to properties (and other entities in the future), enabling:

1. **Compliance:** Track who made what changes for regulatory requirements
2. **Security:** Detect unauthorized access attempts
3. **Debugging:** Trace issues back to specific operations
4. **Analytics:** Understand user behavior patterns

The system user is needed for automated imports and batch operations where there's no human user to attribute changes to.

---

## Testing Instructions

After implementation, the backend subagent should:

1. **Run migration:**
   ```bash
   make migrate
   # Or: docker exec -it bestays-server-dev alembic upgrade head
   ```

2. **Verify tables created:**
   ```bash
   make shell-db
   \dt
   \d audit_log
   \d properties
   ```

3. **Test downgrade:**
   ```bash
   docker exec -it bestays-server-dev alembic downgrade -1
   ```

4. **Verify cleanup:**
   ```bash
   make shell-db
   \dt
   ```

5. **Test upgrade again:**
   ```bash
   make migrate
   ```

6. **Verify indexes:**
   ```sql
   SELECT indexname, indexdef FROM pg_indexes
   WHERE tablename IN ('audit_log', 'properties');
   ```

---

## Related Links

- Alembic Documentation: https://alembic.sqlalchemy.org/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- PostgreSQL UUID: https://www.postgresql.org/docs/current/datatype-uuid.html
- PostgreSQL JSONB: https://www.postgresql.org/docs/current/datatype-json.html
