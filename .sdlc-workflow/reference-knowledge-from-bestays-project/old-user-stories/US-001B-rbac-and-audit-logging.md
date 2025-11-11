# User Story: US-001B - Role-Based Access Control and Audit Logging

**Status:** IN_PROGRESS
**Domain:** auth
**Type:** feature
**Priority:** high
**Created:** 2025-11-06
**Estimated Complexity:** High (database schema, backend services, audit infrastructure)

---

## Story

**As a** system administrator
**I want** comprehensive audit logging and role-based access control for all property operations
**So that** we can track who made what changes, maintain compliance, and enforce proper authorization

---

## Background

With authentication working (US-001), we need to add:
1. **Audit Logging** - Track all property changes (who, what, when, why)
2. **RBAC Infrastructure** - Database schema to support role-based permissions
3. **System User** - For automated imports and system operations

This foundation enables:
- Compliance requirements (who changed what property data)
- Security auditing (detect unauthorized access attempts)
- Debugging (trace issues to specific operations)
- Business intelligence (understand user behavior patterns)

---

## Current Implementation

Currently we have:
- Users table with role column (admin, agent, user)
- Basic authentication via Clerk
- No audit trail for changes
- No tracking of who created/modified properties

---

## Acceptance Criteria

### Functional Requirements

- [ ] **AC-1:** Audit log captures all property operations (create, update, delete, publish)
- [ ] **AC-2:** Audit log records: who (user), what (action), when (timestamp), where (IP), how (user agent)
- [ ] **AC-3:** Properties table tracks created_by, updated_by, published_by
- [ ] **AC-4:** System user exists for automated imports (system@bestays.app)

### Technical Requirements

- [ ] **AC-5:** Database migration creates audit_log table with proper indexes
- [ ] **AC-6:** Database migration adds audit fields to properties table (or creates if doesn't exist)
- [ ] **AC-7:** SQLAlchemy models created for AuditLog and Property
- [ ] **AC-8:** Migration is reversible (downgrade works correctly)
- [ ] **AC-9:** Proper foreign key constraints and cascading behavior

### Quality Gates

- [ ] **AC-10:** Migration tested locally (upgrade and downgrade)
- [ ] **AC-11:** Models follow project patterns (file headers, type hints)
- [ ] **AC-12:** Database indexes optimized for query patterns

---

## Technical Notes

### Database Schema

#### Audit Log Table
```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    performed_by UUID REFERENCES users(id),
    performed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    changes JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT
);

CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_performed_by ON audit_log(performed_by);
CREATE INDEX idx_audit_log_performed_at ON audit_log(performed_at DESC);
```

#### Properties Table Audit Fields
```sql
ALTER TABLE properties
    ADD COLUMN created_by UUID REFERENCES users(id),
    ADD COLUMN updated_by UUID REFERENCES users(id),
    ADD COLUMN published_by UUID REFERENCES users(id);
```

Or if properties table doesn't exist:
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

### Integration Points

- **User Model:** Foreign keys to users table for audit tracking
- **Alembic:** Migration system for schema changes
- **SQLAlchemy:** ORM models for type-safe database access

---

## Testing Strategy

### Migration Tests

- [ ] Test upgrade: `alembic upgrade head`
- [ ] Verify tables created with correct schema
- [ ] Verify indexes created
- [ ] Test downgrade: `alembic downgrade -1`
- [ ] Verify cleanup is complete
- [ ] Test upgrade again to ensure repeatability

### Model Tests

- [ ] Test AuditLog model CRUD operations
- [ ] Test Property model with audit fields
- [ ] Test foreign key constraints
- [ ] Test JSONB changes field

---

## Dependencies

### External Dependencies

- PostgreSQL with UUID support (gen_random_uuid)
- Alembic for migrations
- SQLAlchemy for ORM

### Internal Dependencies

- US-001: User authentication and role system (COMPLETED)

### Blocks

- US-002: Property listing implementation (needs properties table)
- Future audit reporting features

---

## Tasks Breakdown

1. **TASK-001:** Research existing database schema and patterns
2. **TASK-002:** Create database migrations and models
3. **TASK-003:** Create audit logging service
4. **TASK-004:** Add audit middleware to FastAPI
5. **TASK-005:** Add E2E tests for audit logging

---

## Definition of Done

- [ ] All acceptance criteria met and verified
- [ ] Migration tested locally (upgrade/downgrade)
- [ ] Models follow project conventions
- [ ] Code review completed
- [ ] Documentation updated
- [ ] No migration conflicts with existing tables

---

## Notes

### System User

Create a system user for automated operations:
- ID: Fixed UUID for consistency across environments
- Email: system@bestays.app
- Name: System Import
- Role: system (or admin)

This user is used for:
- Batch imports from external systems
- Automated data migrations
- System maintenance operations

### Audit Log Retention

Consider future policy for:
- How long to retain audit logs
- Archiving old logs to cold storage
- GDPR compliance (user data deletion)

---

**Template Version:** 1.0
**Last Updated:** 2025-11-06
