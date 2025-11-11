# Implementation Plan: Property V2 Schema Migration

**TASK:** TASK-013
**Story:** US-023
**Date:** 2025-11-09
**Author:** Claude Code (Coordinator)

---

## Overview

This document provides a step-by-step execution plan for implementing Property V2 schema with hybrid localization. The plan is divided into 7 phases with clear subagent assignments and validation checkpoints.

**Total Estimated Time:** 6-8 hours (development + testing)

---

## Implementation Phases

### Phase 1: Create Support Tables (Amenities & Policies)

**Objective:** Create amenity and policy master lists with translations

**Duration:** 30 minutes

**Subagent:** `devops-database` (migration) + `dev-backend-fastapi` (seed data)

**Tasks:**

1. **Create Migration File** (devops-database)
   ```bash
   cd apps/server
   alembic revision -m "create_amenities_and_policies_tables"
   ```

   - Create `amenities` table
   - Create `amenity_translations` table
   - Create `policies` table
   - Create `policy_translations` table
   - Create indexes
   - See: `migration-spec.md` sections 2-5

2. **Create Seed Data Script** (dev-backend-fastapi)
   ```python
   # apps/server/app/scripts/seed_amenities_policies.py
   ```

   - Insert common amenities (air_conditioning, wifi, pool, etc.)
   - Insert EN translations
   - Insert TH translations
   - Insert common policies (pets_allowed, lease_duration, etc.)
   - Insert EN/TH translations

3. **Run Migration**
   ```bash
   alembic upgrade head
   python -m app.scripts.seed_amenities_policies
   ```

**Validation Checkpoints:**
- ✅ All 4 tables created
- ✅ Indexes exist (`idx_amenities_category`, `idx_policies_category`)
- ✅ Seed data inserted (verify 20+ amenities, 10+ policies)
- ✅ Translations exist for EN and TH

**Success Criteria:**
```sql
SELECT COUNT(*) FROM amenities;  -- Should return 20+
SELECT COUNT(*) FROM amenity_translations;  -- Should return 40+ (20 × 2 locales)
```

---

### Phase 2: Create Properties Table

**Objective:** Create main properties table with JSONB fields and pgvector columns

**Duration:** 45 minutes

**Subagent:** `devops-database`

**Tasks:**

1. **Add to Migration File**
   - Create `properties` table (see `migration-spec.md` section 6)
   - Create `property_translations` table (see `migration-spec.md` section 7)
   - Create `update_updated_at_column()` trigger function
   - Add triggers to both tables
   - Add table comments

2. **Run Migration**
   ```bash
   alembic upgrade head
   ```

3. **Verify pgvector Extension**
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   -- If not exists, run: CREATE EXTENSION IF NOT EXISTS vector;
   ```

**Validation Checkpoints:**
- ✅ `properties` table exists with all columns
- ✅ `property_translations` table exists
- ✅ Foreign keys to `users` table work
- ✅ Triggers created (`update_properties_updated_at`)
- ✅ CHECK constraints enforced (try invalid transaction_type)
- ✅ Vector columns exist (type: `vector(1536)`)

**Success Criteria:**
```sql
-- Test insert
INSERT INTO properties (title, description, transaction_type, property_type, rent_price, currency)
VALUES ('Test', 'Test description', 'rent', 'villa', 3000000, 'THB')
RETURNING id;
-- Should succeed

-- Test constraint
INSERT INTO properties (title, description, transaction_type, property_type, currency)
VALUES ('Test', 'Test', 'rent', 'villa', 'THB');
-- Should fail: rent_price required for rent transaction

-- Clean up
DELETE FROM properties WHERE title = 'Test';
```

---

### Phase 3: Create Indexes

**Objective:** Create all performance indexes (B-tree, GIN, partial)

**Duration:** 20 minutes (build time depends on data, but tables are empty)

**Subagent:** `devops-database`

**Tasks:**

1. **Add to Migration File**
   - See `migration-spec.md` section 8
   - Create B-tree indexes (transaction_price, type, listing, created_by, deleted_at)
   - Create GIN indexes (physical_specs, amenities, policies, location_details, tags)
   - Create property_translations indexes

2. **Run Migration**
   ```bash
   alembic upgrade head
   ```

3. **Verify Index Creation**
   ```sql
   SELECT indexname, indexdef FROM pg_indexes
   WHERE tablename = 'properties'
   ORDER BY indexname;
   ```

**Validation Checkpoints:**
- ✅ 11 indexes on `properties` table (including PK)
- ✅ 2 indexes on `property_translations`
- ✅ GIN indexes use `jsonb_path_ops`
- ✅ Partial indexes have WHERE clauses

**Success Criteria:**
```sql
-- Verify index usage
EXPLAIN SELECT * FROM properties
WHERE transaction_type = 'rent'
AND rent_price BETWEEN 2000000 AND 5000000
AND is_published = true
AND deleted_at IS NULL;
-- Should use idx_properties_transaction_price
```

**Note:** HNSW vector indexes NOT created in this phase (reserved for US-024)

---

### Phase 4: Create SQLAlchemy Models

**Objective:** Create ORM models for all tables

**Duration:** 1 hour

**Subagent:** `dev-backend-fastapi`

**Tasks:**

1. **Create Property Model**
   ```python
   # apps/server/app/models/property.py

   from sqlalchemy import Column, String, BigInteger, Boolean, Integer, Text, TIMESTAMP, CheckConstraint, ForeignKey
   from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
   from sqlalchemy.orm import relationship
   from pgvector.sqlalchemy import Vector
   from app.models.base import Base
   import uuid

   class Property(Base):
       __tablename__ = "properties"

       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       title = Column(String(255), nullable=False)
       # ... all columns from data-model-spec.md

       # Relationships
       translations = relationship("PropertyTranslation", back_populates="property", cascade="all, delete-orphan")
       created_by_user = relationship("User", foreign_keys=[created_by])
       updated_by_user = relationship("User", foreign_keys=[updated_by])
   ```

2. **Create PropertyTranslation Model**
   ```python
   class PropertyTranslation(Base):
       __tablename__ = "property_translations"

       id = Column(Integer, primary_key=True)
       property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
       locale = Column(String(5), nullable=False)
       field = Column(String(100), nullable=False)
       value = Column(Text, nullable=False)
       # ... timestamps

       # Relationships
       property = relationship("Property", back_populates="translations")
   ```

3. **Create Amenity + AmenityTranslation Models**
4. **Create Policy + PolicyTranslation Models**

**Validation Checkpoints:**
- ✅ All models inherit from `Base`
- ✅ Relationships defined correctly
- ✅ Timestamps auto-update (`updated_at`)
- ✅ Cascade deletes work (`ondelete="CASCADE"`)

**Success Criteria:**
```python
# Test in Python shell
from app.models.property import Property, PropertyTranslation
from app.database import SessionLocal

db = SessionLocal()

# Create property
prop = Property(
    title="Test",
    description="Test",
    transaction_type="rent",
    property_type="villa",
    rent_price=3000000,
    currency="THB"
)
db.add(prop)
db.commit()

# Add translation
trans = PropertyTranslation(
    property_id=prop.id,
    locale="th",
    field="title",
    value="ทดสอบ"
)
db.add(trans)
db.commit()

# Verify relationship
assert len(prop.translations) == 1
assert prop.translations[0].value == "ทดสอบ"

# Clean up
db.delete(prop)  # Should cascade delete translation
db.commit()
```

---

### Phase 5: Create Pydantic Schemas

**Objective:** Create request/response schemas for API validation

**Duration:** 1 hour

**Subagent:** `dev-backend-fastapi`

**Tasks:**

1. **Create Base Schemas**
   ```python
   # apps/server/app/schemas/property.py

   from pydantic import BaseModel, Field, ConfigDict
   from typing import Optional, List, Dict, Any
   from datetime import datetime
   from uuid import UUID

   # See api-design.md for full schemas:
   # - PropertyListQuery
   # - PhysicalSpecs
   # - LocationDetails
   # - ImageObject
   # - PropertyResponse
   # - PropertyCreate
   # - PropertyUpdate
   # - PaginationMeta
   # - PropertyListResponse
   # - PropertyDetailResponse
   ```

2. **Create Amenity/Policy Schemas**
   ```python
   # apps/server/app/schemas/amenity.py
   # apps/server/app/schemas/policy.py
   ```

3. **Add Validation**
   - Title: 10-255 chars
   - Description: 50-5000 chars
   - Prices: > 0 if present
   - Enums: transaction_type, property_type, currency, furnishing, condition
   - JSONB structure validation (rooms, sizes, etc.)

**Validation Checkpoints:**
- ✅ All schemas have `model_config = ConfigDict(from_attributes=True)`
- ✅ Field validations work (try invalid title length)
- ✅ Nested models work (PhysicalSpecs, LocationDetails)
- ✅ Optional fields handled correctly

**Success Criteria:**
```python
# Test validation
from app.schemas.property import PropertyCreate

# Valid
data = PropertyCreate(
    title="Beautiful Villa",
    description="This is a beautiful villa with 3 bedrooms and a pool...",
    transaction_type="rent",
    property_type="villa",
    rent_price=30000,
    currency="THB",
    physical_specs={"rooms": {"bedrooms": 3}},
    location_details={},
    amenities={},
    policies={},
    contact_info={}
)
assert data.title == "Beautiful Villa"

# Invalid (title too short)
try:
    PropertyCreate(title="Villa", description="Short", ...)
except ValidationError as e:
    assert "at least 10 characters" in str(e)
```

---

### Phase 6: Create Service Layer & API Endpoints

**Objective:** Implement business logic and FastAPI routes

**Duration:** 3 hours

**Subagent:** `dev-backend-fastapi`

**Tasks:**

1. **Create PropertyService** (1.5 hours)
   ```python
   # apps/server/app/services/property_service.py

   class PropertyService:
       async def list_properties(query: PropertyListQuery, locale: str) -> tuple[List[Property], int]:
           # Build query with filters
           # Apply pagination (LIMIT/OFFSET)
           # JOIN property_translations
           # Aggregate translations: json_object_agg(field, value)
           # Merge translations into property objects
           # Return (properties, total_count)
           pass

       async def get_property_by_id(property_id: UUID, locale: str) -> Optional[Property]:
           # Point lookup
           # JOIN translations
           # Merge and return
           pass

       async def create_property(data: PropertyCreate, created_by: int) -> Property:
           # Validate amenity IDs exist
           # Validate policy IDs exist
           # Create property
           # Create translations if provided
           # Return created property
           pass

       async def update_property(property_id: UUID, data: PropertyUpdate, updated_by: int) -> Property:
           # Fetch existing property
           # Update fields (partial update)
           # Upsert translations if provided
           # Return updated property
           pass

       async def delete_property(property_id: UUID) -> bool:
           # Set deleted_at = CURRENT_TIMESTAMP
           # Return success
           pass

       def _merge_translations(property: Property, translations: Dict, locale: str) -> Property:
           # Apply translations to property object
           # Fallback: requested locale → EN → property field
           # Return merged property
           pass
   ```

2. **Create API Router** (1 hour)
   ```python
   # apps/server/app/api/v1/endpoints/properties.py

   from fastapi import APIRouter, Depends, Query, Path, Header
   from app.schemas.property import *
   from app.services.property_service import PropertyService

   router = APIRouter(prefix="/properties", tags=["properties"])

   @router.get("", response_model=PropertyListResponse)
   async def list_properties(
       query: PropertyListQuery = Depends(),
       locale: str = Query("en"),
       db: AsyncSession = Depends(get_db)
   ):
       service = PropertyService(db)
       properties, total = await service.list_properties(query, locale)
       # Return PropertyListResponse

   @router.get("/{id}", response_model=PropertyDetailResponse)
   async def get_property(
       id: UUID = Path(...),
       locale: str = Query("en"),
       db: AsyncSession = Depends(get_db)
   ):
       # ... implementation

   @router.post("", response_model=PropertyResponse, status_code=201)
   async def create_property(
       data: PropertyCreate,
       current_user: User = Depends(require_admin),
       db: AsyncSession = Depends(get_db)
   ):
       # ... implementation

   # ... PUT, DELETE, translations endpoints
   ```

3. **Create Amenity/Policy Endpoints** (30 minutes)
   ```python
   # apps/server/app/api/v1/endpoints/amenities.py
   # apps/server/app/api/v1/endpoints/policies.py
   ```

4. **Register Routers**
   ```python
   # apps/server/app/api/v1/router.py

   from app.api.v1.endpoints import properties, amenities, policies

   api_router.include_router(properties.router)
   api_router.include_router(amenities.router)
   api_router.include_router(policies.router)
   ```

**Validation Checkpoints:**
- ✅ All endpoints return correct status codes (200, 201, 404, 422)
- ✅ Validation errors handled (422 with detail)
- ✅ Authorization enforced (401, 403)
- ✅ Locale parameter works (EN/TH responses)
- ✅ Pagination works (correct total, page, pages)
- ✅ Filters work (transaction_type, price range, bedrooms, amenities)

**Success Criteria:**
```bash
# Test endpoints
curl http://localhost:8011/api/v1/properties?locale=th
# Should return empty list

curl -X POST http://localhost:8011/api/v1/properties \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Villa", ...}'
# Should return 201 Created

curl http://localhost:8011/api/v1/properties/<id>?locale=th
# Should return property with Thai translations
```

---

### Phase 7: Testing & Validation

**Objective:** Comprehensive testing (unit, integration, E2E)

**Duration:** 2 hours

**Subagent:** `dev-backend-fastapi` (unit/integration) + `playwright-e2e-tester` (E2E)

**Tasks:**

1. **Unit Tests - Models** (30 minutes)
   ```python
   # apps/server/tests/models/test_property.py

   def test_property_creation():
       # Test basic property creation
       # Test constraints (invalid transaction_type)
       # Test soft delete (deleted_at)
       pass

   def test_property_translations():
       # Test translation relationship
       # Test cascade delete
       pass
   ```

2. **Unit Tests - Schemas** (20 minutes)
   ```python
   # apps/server/tests/schemas/test_property.py

   def test_property_create_validation():
       # Test title length validation
       # Test price validation
       # Test enum validation
       pass
   ```

3. **Integration Tests - Service Layer** (40 minutes)
   ```python
   # apps/server/tests/services/test_property_service.py

   async def test_list_properties():
       # Create test properties
       # Test filters (transaction_type, price, bedrooms)
       # Test pagination
       # Test locale (EN/TH)
       pass

   async def test_create_property_with_translations():
       # Create property with EN + TH
       # Fetch with locale=th
       # Verify Thai title/description returned
       pass

   async def test_translation_fallback():
       # Create property with only EN
       # Fetch with locale=th
       # Verify EN fallback
       pass
   ```

4. **Integration Tests - API Endpoints** (30 minutes)
   ```python
   # apps/server/tests/api/v1/test_properties.py

   async def test_list_properties_endpoint(client: TestClient):
       # Test GET /properties
       # Test filters
       # Test pagination headers
       pass

   async def test_create_property_endpoint(admin_client: TestClient):
       # Test POST /properties (admin)
       # Test 403 for non-admin
       pass

   async def test_property_detail_endpoint(client: TestClient):
       # Test GET /properties/{id}
       # Test 404 for missing property
       pass
   ```

5. **E2E Tests - Frontend Integration** (Optional, if frontend ready)
   ```typescript
   // apps/frontend/tests/e2e/properties.spec.ts

   test('list properties with Thai locale', async ({ page }) => {
       await page.goto('/properties?locale=th');
       await expect(page.locator('h1')).toContainText('รายการทรัพย์สิน');
   });
   ```

**Validation Checkpoints:**
- ✅ All unit tests pass (models, schemas)
- ✅ All integration tests pass (service, API)
- ✅ Test coverage > 80% for critical paths
- ✅ No SQL N+1 queries (verify with SQL logging)
- ✅ Query performance < 200ms (verified in tests)

**Success Criteria:**
```bash
# Run tests
cd apps/server
pytest tests/ -v --cov=app --cov-report=term-missing

# Should show:
# - All tests passed
# - Coverage > 80%
# - No slow tests (> 1s)
```

---

## Timeline Summary

| Phase | Duration | Subagent | Dependencies |
|-------|----------|----------|--------------|
| 1. Support Tables | 30 min | devops-database, dev-backend-fastapi | None |
| 2. Properties Table | 45 min | devops-database | Phase 1 |
| 3. Indexes | 20 min | devops-database | Phase 2 |
| 4. SQLAlchemy Models | 1 hour | dev-backend-fastapi | Phase 3 |
| 5. Pydantic Schemas | 1 hour | dev-backend-fastapi | Phase 4 |
| 6. Service + API | 3 hours | dev-backend-fastapi | Phase 5 |
| 7. Testing | 2 hours | dev-backend-fastapi, playwright-e2e-tester | Phase 6 |
| **Total** | **8.5 hours** | - | - |

**Critical Path:** Phases 1 → 2 → 3 → 4 → 5 → 6 → 7 (sequential)

---

## Risk Mitigation

### Risk 1: Migration Failure

**Mitigation:**
- Test migration in development first
- Take database backup before production migration
- Have rollback plan ready (see `migration-spec.md`)

### Risk 2: Performance Issues

**Mitigation:**
- Load test with 10k sample properties
- Monitor slow query log during testing
- Use EXPLAIN ANALYZE to verify index usage

### Risk 3: Translation Complexity

**Mitigation:**
- Start with simple 2-locale support (EN, TH)
- Use fallback chain (requested → EN → property field)
- Test all fallback scenarios in integration tests

### Risk 4: Subagent Handoff Issues

**Mitigation:**
- Clear phase boundaries (migration → models → API)
- Each phase has validation checkpoints
- Coordinator reviews all subagent outputs

---

## Success Criteria (Overall)

**Technical:**
- ✅ All migrations run without errors
- ✅ All indexes created and used by queries
- ✅ Property listing query < 200ms (24 properties)
- ✅ All tests pass (unit, integration, E2E)
- ✅ Test coverage > 80%

**Functional:**
- ✅ Can create property with EN + TH translations
- ✅ List endpoint returns correct locale
- ✅ Fallback to EN works when TH missing
- ✅ Filters work (transaction_type, price, bedrooms, amenities)
- ✅ Pagination works correctly
- ✅ Soft delete works (deleted_at set)

**Quality:**
- ✅ No SQL N+1 queries
- ✅ No bloated JSONB (amenities stored as IDs)
- ✅ Clean separation (models, schemas, services, routes)
- ✅ Comprehensive error handling (404, 422, 403)
- ✅ API documentation auto-generated (FastAPI /docs)

---

## Post-Implementation

### Monitoring (First Week)

1. **Query Performance**
   ```sql
   -- Check slow queries
   SELECT query, mean_exec_time, calls
   FROM pg_stat_statements
   WHERE query LIKE '%properties%'
   ORDER BY mean_exec_time DESC;
   ```

2. **Index Usage**
   ```sql
   -- Verify indexes are used
   SELECT * FROM pg_stat_user_indexes
   WHERE tablename = 'properties'
   ORDER BY idx_scan DESC;
   ```

3. **Cache Hit Ratio**
   ```sql
   -- Should be > 95%
   SELECT * FROM pg_statio_user_tables
   WHERE relname = 'properties';
   ```

### Documentation

1. **Update API Docs**
   - FastAPI auto-generates OpenAPI docs at `/docs`
   - Add examples to schema docstrings
   - Update README with new endpoints

2. **Update Frontend Docs**
   - Document API usage patterns
   - Add TypeScript types for API responses
   - Document localization flow

3. **Update DevOps Docs**
   - Add migration instructions to deployment guide
   - Document rollback procedures
   - Add monitoring dashboards

---

## Next Steps (Future User Stories)

### US-024: Semantic Search (pgvector)

**Dependencies:** TASK-013 complete

**Tasks:**
- Generate embeddings for existing properties (OpenAI API)
- Create HNSW indexes on `description_embedding_en/th`
- Create semantic search endpoint (`GET /properties/search/semantic`)
- Implement embedding generation on property create/update

**Estimated Time:** 4-6 hours

### US-025: Property Import (CSV/API)

**Dependencies:** TASK-013 complete

**Tasks:**
- Create bulk import endpoint
- Parse CSV with property data
- Validate and transform to schema
- Handle errors gracefully

**Estimated Time:** 3-4 hours

---

## References

- Data Model: `data-model-spec.md`
- Indexing: `indexing-strategy.md`
- Migration: `migration-spec.md`
- API Design: `api-design.md`
- System Design: `system-design.md`

---

**Next Document:** trade-offs-analysis.md (Architectural decision documentation)
