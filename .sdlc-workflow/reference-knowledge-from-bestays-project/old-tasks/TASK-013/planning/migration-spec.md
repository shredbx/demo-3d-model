# Migration Specification: Property V2 Schema

**TASK:** TASK-013
**Story:** US-023
**Date:** 2025-11-09
**Author:** Claude Code (Coordinator)

---

## Overview

This document specifies the production-ready Alembic migration for Property V2 schema. The migration is designed for zero-downtime deployment with comprehensive rollback procedures.

**Migration:** `2025_11_09_property_v2_schema`
**Revision ID:** `a8f2d1c9b4e3` (will be auto-generated)
**Down Revision:** Current head (previous migration)

---

## Pre-Migration Checklist

### Prerequisites

1. **Database Extensions**
   ```sql
   -- Verify pgvector is installed
   SELECT * FROM pg_extension WHERE extname = 'pgvector';
   -- If not installed: CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Permissions**
   ```sql
   -- Verify migration user has required privileges
   SELECT has_table_privilege('bestays_app', 'properties', 'CREATE');
   ```

3. **Backup**
   ```bash
   # Take full backup before migration
   pg_dump -h localhost -p 5433 -U bestays -Fc bestays > backup_pre_migration_$(date +%Y%m%d_%H%M%S).dump
   ```

4. **Disk Space**
   ```sql
   -- Verify available space (need ~300 MB for 10k properties + indexes)
   SELECT pg_size_pretty(pg_database_size('bestays'));
   ```

5. **Existing Tables Check**
   ```sql
   -- Verify no conflicting tables exist
   SELECT tablename FROM pg_tables
   WHERE schemaname = 'public'
   AND tablename IN ('properties', 'property_translations', 'amenities', 'amenity_translations', 'policies', 'policy_translations');
   -- Should return 0 rows
   ```

---

## Migration File

**File:** `apps/server/alembic/versions/2025_11_09_property_v2_schema.py`

```python
"""Property V2 schema with hybrid localization

Revision ID: a8f2d1c9b4e3
Revises: <previous_revision>
Create Date: 2025-11-09 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = 'a8f2d1c9b4e3'
down_revision: Union[str, None] = '<previous_revision>'  # Update this
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create Property V2 schema with:
    - properties table (JSONB fields, pgvector embeddings)
    - property_translations table
    - amenities + amenity_translations tables
    - policies + policy_translations tables
    - All indexes
    """

    # ==========================================
    # 1. CREATE HELPER FUNCTION
    # ==========================================

    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # ==========================================
    # 2. CREATE AMENITIES TABLE
    # ==========================================

    op.create_table(
        'amenities',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("category IN ('interior', 'exterior', 'building', 'area')", name='valid_amenity_category')
    )

    op.execute("""
        CREATE TRIGGER update_amenities_updated_at
        BEFORE UPDATE ON amenities
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    op.create_index('idx_amenities_category', 'amenities', ['category'], postgresql_where=sa.text('is_active = true'))

    # ==========================================
    # 3. CREATE AMENITY_TRANSLATIONS TABLE
    # ==========================================

    op.create_table(
        'amenity_translations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('amenity_id', sa.String(100), nullable=False),
        sa.Column('locale', sa.String(5), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['amenity_id'], ['amenities.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('amenity_id', 'locale', name='unique_amenity_translation'),
        sa.CheckConstraint("locale ~ '^[a-z]{2}(-[A-Z]{2})?$'", name='valid_locale_amenity')
    )

    op.execute("""
        CREATE TRIGGER update_amenity_translations_updated_at
        BEFORE UPDATE ON amenity_translations
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    # ==========================================
    # 4. CREATE POLICIES TABLE
    # ==========================================

    op.create_table(
        'policies',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('data_type', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("category IN ('lease_terms', 'house_rules', 'payment')", name='valid_policy_category'),
        sa.CheckConstraint("data_type IN ('boolean', 'integer', 'text', 'select')", name='valid_policy_data_type')
    )

    op.execute("""
        CREATE TRIGGER update_policies_updated_at
        BEFORE UPDATE ON policies
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    op.create_index('idx_policies_category', 'policies', ['category'], postgresql_where=sa.text('is_active = true'))

    # ==========================================
    # 5. CREATE POLICY_TRANSLATIONS TABLE
    # ==========================================

    op.create_table(
        'policy_translations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('policy_id', sa.String(100), nullable=False),
        sa.Column('locale', sa.String(5), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('policy_id', 'locale', name='unique_policy_translation'),
        sa.CheckConstraint("locale ~ '^[a-z]{2}(-[A-Z]{2})?$'", name='valid_locale_policy')
    )

    op.execute("""
        CREATE TRIGGER update_policy_translations_updated_at
        BEFORE UPDATE ON policy_translations
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    # ==========================================
    # 6. CREATE PROPERTIES TABLE
    # ==========================================

    op.create_table(
        'properties',
        # Primary Key
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),

        # Fallback Content (EN)
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),

        # Transaction & Type
        sa.Column('transaction_type', sa.String(20), nullable=False),
        sa.Column('property_type', sa.String(50), nullable=False),

        # Pricing
        sa.Column('rent_price', sa.BigInteger(), nullable=True),
        sa.Column('sale_price', sa.BigInteger(), nullable=True),
        sa.Column('lease_price', sa.BigInteger(), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='THB'),

        # JSONB Fields
        sa.Column('physical_specs', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('location_details', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('amenities', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('policies', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('contact_info', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),

        # Media
        sa.Column('cover_image', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('images', postgresql.ARRAY(postgresql.JSONB(astext_type=sa.Text())), nullable=False, server_default=sa.text("ARRAY[]::jsonb[]")),

        # Tags
        sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("ARRAY[]::text[]")),

        # Future: Semantic Search (pgvector)
        sa.Column('description_embedding_en', Vector(1536), nullable=True),
        sa.Column('description_embedding_th', Vector(1536), nullable=True),

        # Publication Status
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('listing_priority', sa.Integer(), nullable=False, server_default='0'),

        # Soft Delete
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),

        # Audit Trail
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign Keys
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),

        # Constraints
        sa.CheckConstraint("transaction_type IN ('rent', 'sale', 'lease')", name='valid_transaction_type'),
        sa.CheckConstraint(
            "property_type IN ('villa', 'condo', 'apartment', 'townhouse', 'house', 'commercial', 'land', 'office', 'retail', 'warehouse')",
            name='valid_property_type'
        ),
        sa.CheckConstraint("currency IN ('THB', 'USD', 'EUR', 'GBP', 'JPY')", name='valid_currency'),
        sa.CheckConstraint(
            """
            (transaction_type = 'rent' AND rent_price IS NOT NULL) OR
            (transaction_type = 'sale' AND sale_price IS NOT NULL) OR
            (transaction_type = 'lease' AND lease_price IS NOT NULL)
            """,
            name='valid_price_for_transaction'
        ),
        sa.CheckConstraint(
            """
            (rent_price IS NULL OR rent_price > 0) AND
            (sale_price IS NULL OR sale_price > 0) AND
            (lease_price IS NULL OR lease_price > 0)
            """,
            name='positive_prices'
        ),
        sa.CheckConstraint("listing_priority >= 0 AND listing_priority <= 999", name='valid_priority')
    )

    op.execute("""
        CREATE TRIGGER update_properties_updated_at
        BEFORE UPDATE ON properties
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    # Add comments
    op.execute("COMMENT ON TABLE properties IS 'Main properties table with hybrid localization (JSONB + translations table)'")
    op.execute("COMMENT ON COLUMN properties.rent_price IS 'Monthly rent in smallest currency unit (satang/cents)'")
    op.execute("COMMENT ON COLUMN properties.physical_specs IS 'JSONB: rooms, sizes, floors, year_built, etc.'")
    op.execute("COMMENT ON COLUMN properties.amenities IS 'JSONB: amenity IDs categorized by type (interior/exterior/building/area)'")
    op.execute("COMMENT ON COLUMN properties.description_embedding_en IS 'Future: vector embedding for semantic search (English)'")

    # ==========================================
    # 7. CREATE PROPERTY_TRANSLATIONS TABLE
    # ==========================================

    op.create_table(
        'property_translations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('property_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('locale', sa.String(5), nullable=False),
        sa.Column('field', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('property_id', 'locale', 'field', name='unique_translation'),
        sa.CheckConstraint("locale ~ '^[a-z]{2}(-[A-Z]{2})?$'", name='valid_locale'),
        sa.CheckConstraint(
            "field IN ('title', 'description', 'location_province', 'location_district', 'location_subdistrict', 'location_address')",
            name='valid_field'
        )
    )

    op.execute("""
        CREATE TRIGGER update_property_translations_updated_at
        BEFORE UPDATE ON property_translations
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("COMMENT ON TABLE property_translations IS 'Localized text for properties (title, description, location names)'")

    # ==========================================
    # 8. CREATE INDEXES (in optimal order)
    # ==========================================

    # Properties table indexes (B-tree)
    op.create_index(
        'idx_properties_transaction_price',
        'properties',
        ['transaction_type', 'rent_price', 'sale_price', 'lease_price'],
        postgresql_where=sa.text('is_published = true AND deleted_at IS NULL')
    )

    op.create_index(
        'idx_properties_type',
        'properties',
        ['property_type'],
        postgresql_where=sa.text('is_published = true AND deleted_at IS NULL')
    )

    op.create_index(
        'idx_properties_listing',
        'properties',
        [sa.text('listing_priority DESC'), sa.text('created_at DESC')],
        postgresql_where=sa.text('deleted_at IS NULL')
    )

    op.create_index(
        'idx_properties_created_by',
        'properties',
        ['created_by'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )

    op.create_index(
        'idx_properties_deleted_at',
        'properties',
        ['deleted_at'],
        postgresql_where=sa.text('deleted_at IS NOT NULL')
    )

    # Properties table indexes (GIN for JSONB)
    op.create_index(
        'idx_properties_physical_specs',
        'properties',
        ['physical_specs'],
        postgresql_using='gin',
        postgresql_ops={'physical_specs': 'jsonb_path_ops'}
    )

    op.create_index(
        'idx_properties_amenities',
        'properties',
        ['amenities'],
        postgresql_using='gin',
        postgresql_ops={'amenities': 'jsonb_path_ops'}
    )

    op.create_index(
        'idx_properties_policies',
        'properties',
        ['policies'],
        postgresql_using='gin',
        postgresql_ops={'policies': 'jsonb_path_ops'}
    )

    op.create_index(
        'idx_properties_location_details',
        'properties',
        ['location_details'],
        postgresql_using='gin',
        postgresql_ops={'location_details': 'jsonb_path_ops'}
    )

    # Tags index (GIN for arrays)
    op.create_index(
        'idx_properties_tags',
        'properties',
        ['tags'],
        postgresql_using='gin'
    )

    # Property translations indexes
    op.create_index(
        'idx_property_translations_lookup',
        'property_translations',
        ['property_id', 'locale']
    )

    op.create_index(
        'idx_property_translations_locale',
        'property_translations',
        ['locale']
    )

    # NOTE: Vector indexes (HNSW) NOT created yet - reserved for US-024
    # See indexing-strategy.md for specification


def downgrade() -> None:
    """
    Rollback Property V2 schema.

    WARNING: This will DELETE ALL property data!
    Only run if migration failed or in development.
    """

    # Drop indexes first (faster DROP TABLE)
    op.drop_index('idx_property_translations_locale', table_name='property_translations')
    op.drop_index('idx_property_translations_lookup', table_name='property_translations')
    op.drop_index('idx_properties_tags', table_name='properties')
    op.drop_index('idx_properties_location_details', table_name='properties')
    op.drop_index('idx_properties_policies', table_name='properties')
    op.drop_index('idx_properties_amenities', table_name='properties')
    op.drop_index('idx_properties_physical_specs', table_name='properties')
    op.drop_index('idx_properties_deleted_at', table_name='properties')
    op.drop_index('idx_properties_created_by', table_name='properties')
    op.drop_index('idx_properties_listing', table_name='properties')
    op.drop_index('idx_properties_type', table_name='properties')
    op.drop_index('idx_properties_transaction_price', table_name='properties')
    op.drop_index('idx_policies_category', table_name='policies')
    op.drop_index('idx_amenities_category', table_name='amenities')

    # Drop tables (in reverse order - translations first)
    op.drop_table('property_translations')
    op.drop_table('properties')
    op.drop_table('policy_translations')
    op.drop_table('policies')
    op.drop_table('amenity_translations')
    op.drop_table('amenities')

    # Drop helper function
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE')
```

---

## Post-Migration Validation

### 1. Table Existence Check

```sql
-- Verify all tables created
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN (
    'properties',
    'property_translations',
    'amenities',
    'amenity_translations',
    'policies',
    'policy_translations'
);
-- Should return 6 rows
```

### 2. Index Existence Check

```sql
-- Verify all indexes created
SELECT indexname FROM pg_indexes
WHERE schemaname = 'public'
AND tablename = 'properties';
-- Should return 11 indexes (including primary key)
```

### 3. Constraint Check

```sql
-- Verify constraints
SELECT conname, contype FROM pg_constraint
WHERE conrelid = 'properties'::regclass;
-- Should include CHECK, FOREIGN KEY constraints
```

### 4. Trigger Check

```sql
-- Verify triggers
SELECT tgname FROM pg_trigger
WHERE tgrelid = 'properties'::regclass;
-- Should include update_properties_updated_at
```

### 5. Insert Test Data

```sql
-- Test basic insert
INSERT INTO properties (title, description, transaction_type, property_type, rent_price, currency)
VALUES ('Test Villa', 'Test description', 'rent', 'villa', 3000000, 'THB')
RETURNING id;
-- Should succeed and return UUID
```

### 6. Query Performance Test

```sql
-- Test indexed query
EXPLAIN ANALYZE
SELECT * FROM properties
WHERE transaction_type = 'rent'
AND rent_price BETWEEN 2000000 AND 5000000
AND is_published = true
AND deleted_at IS NULL
LIMIT 24;
-- Should use idx_properties_transaction_price
-- Execution time should be < 50ms (even with no data)
```

---

## Risk Assessment

### Migration Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Migration failure (syntax error) | Low | Medium | Test in dev first, dry-run in staging |
| Disk space exhaustion | Low | High | Pre-flight check, monitor during migration |
| Foreign key violation (users table) | Low | High | Verify users table exists, use SET NULL |
| Long table lock | Medium | Medium | Migration is DDL-only (fast), no data operations |
| Index build timeout | Low | Medium | Create indexes AFTER tables (included in migration) |

### Estimated Migration Time

| Phase | Duration (Empty DB) | Duration (10k props) |
|-------|---------------------|----------------------|
| Create tables | < 1 second | < 1 second |
| Create triggers | < 1 second | < 1 second |
| Create B-tree indexes | < 5 seconds | ~30 seconds |
| Create GIN indexes | < 5 seconds | ~2 minutes |
| **Total** | **< 15 seconds** | **~3 minutes** |

**Downtime:** 0 seconds (no existing tables, DDL only)

---

## Rollback Procedures

### Scenario 1: Migration Failed Mid-Execution

```bash
# Alembic automatically rolls back on error
# Verify rollback completed:
alembic current
# Should show previous revision

# Manually inspect if needed:
psql -h localhost -p 5433 -U bestays -d bestays -c "\dt"
# Properties tables should NOT exist
```

### Scenario 2: Migration Succeeded but Need to Rollback

```bash
# Downgrade to previous revision
alembic downgrade -1

# WARNING: This deletes ALL properties data!
# Only use in development or if migration needs to be re-run
```

### Scenario 3: Partial Rollback (Keep Tables, Remove Indexes)

```sql
-- Manually drop indexes if causing performance issues
DROP INDEX CONCURRENTLY idx_properties_amenities;
DROP INDEX CONCURRENTLY idx_properties_physical_specs;
-- etc.

-- Tables remain intact
```

---

## Rollback Data Preservation

**If you need to rollback but preserve data:**

```bash
# 1. Export data before rollback
psql -h localhost -p 5433 -U bestays -d bestays -c "COPY properties TO STDOUT WITH CSV HEADER" > properties_backup.csv
psql -h localhost -p 5433 -U bestays -d bestays -c "COPY property_translations TO STDOUT WITH CSV HEADER" > translations_backup.csv

# 2. Rollback migration
alembic downgrade -1

# 3. Re-run migration (after fixes)
alembic upgrade head

# 4. Re-import data
psql -h localhost -p 5433 -U bestays -d bestays -c "COPY properties FROM STDIN WITH CSV HEADER" < properties_backup.csv
psql -h localhost -p 5433 -U bestays -d bestays -c "COPY property_translations FROM STDIN WITH CSV HEADER" < translations_backup.csv
```

---

## Running the Migration

### Development

```bash
# 1. Navigate to server
cd apps/server

# 2. Verify current revision
alembic current

# 3. Run migration
alembic upgrade head

# 4. Verify success
alembic current  # Should show new revision
psql -h localhost -p 5433 -U bestays -d bestays -c "\dt"  # List tables
```

### Staging

```bash
# 1. Take backup
make backup-db-staging

# 2. Run migration
make migrate-staging

# 3. Validate (see Post-Migration Validation section)

# 4. Test API endpoints
curl http://staging-api.bestays.app/api/v1/properties
```

### Production

```bash
# 1. Schedule maintenance window (optional - zero downtime expected)

# 2. Take backup
make backup-db-production

# 3. Dry-run validation (in separate transaction)
# Manually test migration in transaction then rollback

# 4. Run migration
make migrate-production

# 5. Monitor
# - Check slow query log
# - Monitor disk space
# - Verify API endpoints
# - Check error logs

# 6. Rollback plan ready (see Rollback Procedures above)
```

---

## Monitoring After Migration

### Key Metrics to Watch

1. **Database Size**
   ```sql
   SELECT pg_size_pretty(pg_database_size('bestays'));
   ```

2. **Table Sizes**
   ```sql
   SELECT
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
   FROM pg_tables
   WHERE schemaname = 'public'
   AND tablename LIKE 'propert%'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
   ```

3. **Index Usage**
   ```sql
   SELECT * FROM pg_stat_user_indexes
   WHERE tablename = 'properties'
   ORDER BY idx_scan DESC;
   ```

4. **Query Performance**
   ```sql
   -- Enable pg_stat_statements
   SELECT query, mean_exec_time, calls
   FROM pg_stat_statements
   WHERE query LIKE '%properties%'
   ORDER BY mean_exec_time DESC
   LIMIT 10;
   ```

---

## Success Criteria

**Migration Success:**
- ✅ All 6 tables created
- ✅ All indexes created (11 on properties table)
- ✅ All constraints active
- ✅ All triggers created
- ✅ Migration time < 5 minutes
- ✅ Zero errors in Alembic output

**Post-Migration:**
- ✅ Can insert property successfully
- ✅ Can query with filters < 200ms
- ✅ Translations join works correctly
- ✅ Foreign keys enforced (try invalid user_id)
- ✅ Soft delete works (deleted_at set)

**Rollback:**
- ✅ Downgrade completes without errors
- ✅ All tables removed
- ✅ Can re-run upgrade successfully

---

## Troubleshooting

### Error: "relation already exists"

```sql
-- Check existing tables
SELECT tablename FROM pg_tables WHERE tablename LIKE 'propert%';

-- Drop manually if needed (DEVELOPMENT ONLY!)
DROP TABLE IF EXISTS property_translations CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
-- etc.
```

### Error: "pgvector extension not found"

```sql
-- Install extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Error: "foreign key constraint fails"

```sql
-- Verify users table exists
SELECT * FROM pg_tables WHERE tablename = 'users';

-- If missing, run previous migrations first
alembic upgrade head
```

### Migration Hangs During Index Creation

```sql
-- Check locks (in separate terminal)
SELECT * FROM pg_locks WHERE NOT granted;

-- If stuck, cancel (in separate terminal)
SELECT pg_cancel_backend(<pid>);

-- Then investigate slow index build (may need more shared_buffers)
```

---

## References

- Alembic Documentation: https://alembic.sqlalchemy.org/
- PostgreSQL CREATE TABLE: https://www.postgresql.org/docs/current/sql-createtable.html
- pgvector Installation: https://github.com/pgvector/pgvector#installation

---

**Next Document:** api-design.md (FastAPI endpoint specifications)
