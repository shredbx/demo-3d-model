# Task: TASK-002 - RBAC Database Migrations

**Story:** US-001B - Role-Based Access Control Implementation
**Type:** feat
**Status:** NOT_STARTED
**Created:** 2025-11-06
**Branch:** feat/TASK-002-US-001B

## Description

Implement database migrations for RBAC support including audit log table and property audit fields.

## Objectives

1. Create Alembic migration for audit_log table
2. Add audit fields to properties table (created_by, updated_by, published_by)
3. Create indexes for performance
4. Add foreign key constraints
5. Create system_user for imports

## Technical Requirements

### Audit Log Table
```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    performed_by UUID REFERENCES users(id),
    performed_at TIMESTAMP DEFAULT NOW(),
    changes JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Indexes for performance
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_performed_by ON audit_log(performed_by);
CREATE INDEX idx_audit_log_performed_at ON audit_log(performed_at DESC);
```

### Property Audit Fields
```sql
ALTER TABLE properties
ADD COLUMN created_by UUID REFERENCES users(id),
ADD COLUMN updated_by UUID REFERENCES users(id),
ADD COLUMN published_by UUID REFERENCES users(id);
```

### System User
Create a system user for data imports and automated actions.

## Acceptance Criteria

- [ ] Alembic migration created and tested
- [ ] Migration can be rolled back cleanly
- [ ] Indexes created for query performance
- [ ] Foreign key constraints properly set
- [ ] System user created in seed data
- [ ] Migration tested with existing data

## Files to Modify

- `apps/server/alembic/versions/` - New migration file
- `apps/server/api/models/audit.py` - SQLAlchemy model
- `apps/server/api/models/property.py` - Add audit fields

## Dependencies

- SQLAlchemy models defined
- Alembic configured
- User table exists (from US-001)

## Notes

This is the foundation for all RBAC features. Must be deployed before any other RBAC tasks.