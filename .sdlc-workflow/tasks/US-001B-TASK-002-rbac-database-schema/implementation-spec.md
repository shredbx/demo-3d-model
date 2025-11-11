# Implementation Specification: RBAC Database Schema

**Task:** US-001B-TASK-002
**Subagent:** dev-backend-fastapi
**Created:** 2025-11-06

---

## Overview

Create Alembic migration and SQLAlchemy models to support RBAC audit logging infrastructure. This includes:
1. audit_log table for tracking all property operations
2. properties table with audit tracking fields
3. SQLAlchemy models (AuditLog, Property)
4. System user seed data

---

## Current State Analysis

**Database:**
- Current migration: `add_chat_config_tables` (head)
- Properties table: DOES NOT EXIST (confirmed via database check)
- Users table: EXISTS (from US-001 authentication)
- PostgreSQL extensions: pgvector enabled

**Models Directory:**
- Location: `/Users/solo/Projects/_repos/bestays/apps/server/src/server/models/`
- Existing models: user.py, chat.py, chat_config.py, faq.py, webhook_event.py, base.py
- Pattern reference: user.py (excellent example with file headers, type hints, docstrings)

**Alembic:**
- Location: `/Users/solo/Projects/_repos/bestays/apps/server/alembic/versions/`
- Latest migration: `20251025_enable_pgvector_extension.py`
- Pattern reference: `20251025_add_faq_tables.py` (comprehensive example)

---

## Implementation Requirements

### 1. Create Alembic Migration

**File:** `apps/server/alembic/versions/[timestamp]_add_rbac_audit_tables.py`

**Naming Convention:**
- Use format: `YYYYMMDD_HHMM-{short_description}.py`
- Example: `20251106_1430-add_rbac_audit_tables.py`

**Migration Content:**

```python
"""add_rbac_audit_tables

Create RBAC audit logging infrastructure.

Tables created:
- audit_log: Track all property operations (who, what, when, where)
- properties: Core properties table with audit tracking fields

Revision ID: add_rbac_audit_tables
Revises: add_faq_tables
Create Date: [current_datetime]
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = 'add_rbac_audit_tables'
down_revision: Union[str, None] = 'add_faq_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create audit_log and properties tables with proper indexes."""

    # =========================================================================
    # 1. Audit Log Table
    # =========================================================================
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique audit log entry ID'),
        sa.Column('entity_type', sa.String(length=50), nullable=False, comment='Type of entity (e.g., property, user)'),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID of the entity that was modified'),
        sa.Column('action', sa.String(length=50), nullable=False, comment='Action performed (create, update, delete, publish)'),
        sa.Column('performed_by', sa.Integer(), nullable=True, comment='User ID who performed the action'),
        sa.Column('performed_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp of action'),
        sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='JSON object with before/after values'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='IP address of user (IPv4/IPv6)'),
        sa.Column('user_agent', sa.Text(), nullable=True, comment='Browser user agent string'),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id'], name='fk_audit_log_performed_by', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Audit log for tracking all entity changes'
    )

    # Create indexes for common query patterns
    op.create_index('idx_audit_log_entity', 'audit_log', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_log_performed_by', 'audit_log', ['performed_by'])
    op.create_index('idx_audit_log_performed_at', 'audit_log', [sa.text('performed_at DESC')])

    # =========================================================================
    # 2. Properties Table
    # =========================================================================
    op.create_table(
        'properties',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique property ID'),
        sa.Column('title', sa.String(length=255), nullable=False, comment='Property title'),
        sa.Column('description', sa.Text(), nullable=True, comment='Property description'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false', comment='Is property published and visible'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='User who created the property'),
        sa.Column('updated_by', sa.Integer(), nullable=True, comment='User who last updated the property'),
        sa.Column('published_by', sa.Integer(), nullable=True, comment='User who published the property'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Last update timestamp'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_properties_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_properties_updated_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['published_by'], ['users.id'], name='fk_properties_published_by', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Properties table with audit tracking'
    )

    # Create indexes
    op.create_index('idx_properties_is_published', 'properties', ['is_published'])
    op.create_index('idx_properties_created_by', 'properties', ['created_by'])

    # =========================================================================
    # 3. Seed System User
    # =========================================================================
    op.execute("""
        INSERT INTO users (clerk_user_id, email, role, created_at, updated_at)
        VALUES ('system_00000000000000000000', 'system@bestays.app', 'admin', NOW(), NOW())
        ON CONFLICT (clerk_user_id) DO NOTHING;
    """)

def downgrade() -> None:
    """Drop tables and indexes."""
    # Drop system user first
    op.execute("DELETE FROM users WHERE clerk_user_id = 'system_00000000000000000000'")

    # Drop tables (cascades will handle foreign keys)
    op.drop_table('properties')
    op.drop_table('audit_log')
```

**Key Points:**
- Use `Integer()` for user foreign keys (user.id is INTEGER, not UUID)
- Use `SET NULL` on delete for audit fields (preserve audit trail even if user deleted)
- Use `JSONB` for changes field (faster queries than JSON)
- Create indexes for common query patterns
- Include proper comments for all columns
- System user uses fixed Clerk ID format

---

### 2. Create SQLAlchemy Models

#### File: `apps/server/src/server/models/audit.py`

**Pattern:** Follow `user.py` structure with comprehensive file header

```python
"""
Audit Log Model - Change Tracking System

ARCHITECTURE:
  Layer: Model (Data Access)
  Pattern: Active Record (SQLAlchemy ORM)

PATTERNS USED:
  - Active Record: Database operations via ORM
  - Audit Pattern: Track who, what, when, where for all changes
  - JSONB Storage: Flexible before/after comparison data

DEPENDENCIES:
  External: sqlalchemy, postgresql (JSONB support)
  Internal: server.core.database (Base class), server.models.user (FK)

INTEGRATION:
  - Database: audit_log table in PostgreSQL
  - Middleware: Future audit middleware will populate this
  - Properties: Tracks property changes via entity_type='property'

TESTING:
  - Coverage Target: 80% (standard model coverage)
  - Test File: tests/unit/test_audit_model.py

Attributes:
    id: UUID primary key
    entity_type: Type of entity being tracked (e.g., 'property')
    entity_id: UUID of the tracked entity
    action: Action performed (create, update, delete, publish)
    performed_by: User ID who performed action (nullable)
    performed_at: Timestamp of action
    changes: JSONB with before/after values
    ip_address: IP address of request
    user_agent: Browser user agent
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from server.core.database import Base


class AuditLog(Base):
    """
    Audit log model for tracking all entity changes in the system.

    This model captures comprehensive audit trails including:
    - What entity was changed (entity_type + entity_id)
    - What action was performed (create, update, delete, publish)
    - Who performed it (performed_by user reference)
    - When it happened (performed_at timestamp)
    - What changed (changes JSONB with before/after values)
    - Where it came from (ip_address, user_agent)

    Use Cases:
    - Compliance: GDPR, audit requirements
    - Security: Detect unauthorized changes
    - Debugging: Trace issues to specific operations
    - Analytics: Understand user behavior

    Query Patterns:
    - By entity: SELECT * WHERE entity_type = 'property' AND entity_id = ?
    - By user: SELECT * WHERE performed_by = ?
    - By time: SELECT * WHERE performed_at > ? ORDER BY performed_at DESC
    """

    __tablename__ = "audit_log"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique audit log entry ID"
    )

    # Entity identification
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of entity (e.g., property, user)"
    )

    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="ID of the entity that was modified"
    )

    # Action tracking
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Action performed (create, update, delete, publish)"
    )

    # User tracking (nullable for system operations)
    performed_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User ID who performed the action"
    )

    # Timestamp
    performed_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp of action"
    )

    # Change details
    changes: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="JSON object with before/after values"
    )

    # Request context
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IP address of user (IPv4/IPv6)"
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Browser user agent string"
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[performed_by],
        lazy="select"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<AuditLog(id={self.id}, "
            f"entity={self.entity_type}:{self.entity_id}, "
            f"action={self.action}, "
            f"performed_by={self.performed_by}, "
            f"performed_at={self.performed_at})>"
        )

    @property
    def display_action(self) -> str:
        """Human-readable action description."""
        actions = {
            "create": "Created",
            "update": "Updated",
            "delete": "Deleted",
            "publish": "Published",
            "unpublish": "Unpublished"
        }
        return actions.get(self.action, self.action.capitalize())
```

#### File: `apps/server/src/server/models/property.py`

```python
"""
Property Model - Real Estate Listings

ARCHITECTURE:
  Layer: Model (Data Access)
  Pattern: Active Record (SQLAlchemy ORM)

PATTERNS USED:
  - Active Record: Database operations via ORM
  - Audit Pattern: Track created_by, updated_by, published_by
  - Soft Publishing: is_published flag for draft/published states

DEPENDENCIES:
  External: sqlalchemy, postgresql (UUID support)
  Internal: server.core.database (Base class), server.models.user (FK)

INTEGRATION:
  - Database: properties table in PostgreSQL
  - Audit Log: Changes tracked in audit_log table
  - Users: Foreign keys to users for audit tracking

TESTING:
  - Coverage Target: 85% (core business entity)
  - Test File: tests/unit/test_property_model.py

Attributes:
    id: UUID primary key
    title: Property title
    description: Property description
    is_published: Published status (draft vs published)
    created_by: User who created the property
    updated_by: User who last updated
    published_by: User who published
    created_at: Creation timestamp
    updated_at: Last update timestamp
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from server.core.database import Base


class Property(Base):
    """
    Property model for real estate listings.

    This is the core business entity representing properties listed on the platform.
    Includes audit tracking fields to maintain history of who created, updated, and
    published each property.

    Future Enhancements:
    - Location data (address, coordinates, neighborhood)
    - Pricing information (price, currency, pricing model)
    - Amenities (bedrooms, bathrooms, square footage)
    - Media (photos, videos, virtual tours)
    - Availability (booking calendar, status)

    Current Scope:
    - Basic fields for TASK-002 (title, description, publish status)
    - Audit tracking fields (created_by, updated_by, published_by)
    - Foundation for future property management features
    """

    __tablename__ = "properties"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique property ID"
    )

    # Basic property information
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Property title"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Property description"
    )

    # Publishing status
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        index=True,
        comment="Is property published and visible"
    )

    # Audit tracking fields
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who created the property"
    )

    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who last updated the property"
    )

    published_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who published the property"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="Creation timestamp"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="select"
    )

    updater: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by],
        lazy="select"
    )

    publisher: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[published_by],
        lazy="select"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Property(id={self.id}, "
            f"title={self.title[:50]}..., "
            f"is_published={self.is_published})>"
        )

    @property
    def is_draft(self) -> bool:
        """Check if property is in draft state."""
        return not self.is_published

    def publish(self, user_id: int) -> None:
        """Publish the property."""
        self.is_published = True
        self.published_by = user_id
        self.updated_by = user_id

    def unpublish(self, user_id: int) -> None:
        """Unpublish the property (return to draft)."""
        self.is_published = False
        self.updated_by = user_id
```

---

### 3. Update Models __init__.py

**File:** `apps/server/src/server/models/__init__.py`

Add these imports:

```python
from server.models.audit import AuditLog
from server.models.property import Property

# Update __all__ list
__all__ = [
    # ... existing exports ...
    "AuditLog",
    "Property",
]
```

---

## Testing Requirements

After implementation, run these tests:

### 1. Migration Test
```bash
# Upgrade
docker exec bestays-server-dev alembic upgrade head

# Verify
docker exec bestays-db-dev psql -U postgres -d bestays_dev -c "\d audit_log"
docker exec bestays-db-dev psql -U postgres -d bestays_dev -c "\d properties"

# Downgrade
docker exec bestays-server-dev alembic downgrade -1

# Re-upgrade
docker exec bestays-server-dev alembic upgrade head
```

### 2. Model Import Test
```bash
docker exec bestays-server-dev python -c "from server.models import AuditLog, Property; print('✅ Models import successfully')"
```

### 3. Database Verification
```sql
-- Check system user
SELECT * FROM users WHERE email = 'system@bestays.app';

-- Check indexes
SELECT indexname, indexdef FROM pg_indexes
WHERE tablename IN ('audit_log', 'properties')
ORDER BY tablename, indexname;

-- Check foreign keys
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f'
AND conrelid IN ('audit_log'::regclass, 'properties'::regclass);
```

---

## Success Criteria

- [ ] Migration file created with proper naming and structure
- [ ] audit_log table created with all columns and indexes
- [ ] properties table created with audit fields
- [ ] System user seeded successfully
- [ ] AuditLog model created with file header and proper types
- [ ] Property model created with file header and proper types
- [ ] Models registered in __init__.py
- [ ] Migration upgrade succeeds
- [ ] Migration downgrade succeeds
- [ ] Migration re-upgrade succeeds
- [ ] Models can be imported without errors
- [ ] All foreign keys and indexes verified in database

---

## References

- Task README: `.sdlc-workflow/tasks/US-001B-TASK-002-rbac-database-schema/README.md`
- User Story: `.sdlc-workflow/stories/auth/US-001B-rbac-and-audit-logging.md`
- Pattern Examples:
  - User Model: `apps/server/src/server/models/user.py`
  - FAQ Migration: `apps/server/alembic/versions/20251025_add_faq_tables.py`
- Skills:
  - `@.claude/skills/dev-philosophy/` - Development philosophy
  - `@.claude/skills/dev-code-quality/` - Code quality standards
  - `@.claude/skills/backend-fastapi/` - FastAPI patterns and architecture
