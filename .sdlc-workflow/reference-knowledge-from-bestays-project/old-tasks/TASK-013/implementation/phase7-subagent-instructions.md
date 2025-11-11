# Phase 7: Testing & Validation - Subagent Instructions

**TASK:** TASK-013 (US-023)
**Phase:** IMPLEMENTATION - Phase 7
**Subagent:** dev-backend-fastapi
**Date:** 2025-11-09

---

## Mission

Implement comprehensive test suite for Property V2 API following the complete specification in `phase7-testing-spec.md`.

## Complete Specification

**READ THIS FIRST:** `.claude/tasks/TASK-013/implementation/phase7-testing-spec.md` (4,800 lines with complete code examples)

This file contains:
- All 7 test files with complete working code
- Fixture definitions
- Test cases with assertions
- Performance validation tests
- Coverage requirements

## Files to Create/Update

### 1. Update Existing File
- `/Users/solo/Projects/_repos/bestays/apps/server/tests/conftest.py`
  - Add Property V2 fixtures (test_amenities, test_policies, test_property, property_factory)
  - Add authenticated clients (user_client, admin_client) with dependency overrides
  - Keep existing fixtures intact

### 2. Create New Test Files

1. `/Users/solo/Projects/_repos/bestays/apps/server/tests/models/test_property_v2.py` (6 tests)
   - Property creation, soft delete, relationships, cascade delete
   - Amenity/Policy translation relationships

2. `/Users/solo/Projects/_repos/bestays/apps/server/tests/schemas/test_property_v2.py` (10 tests)
   - PropertyCreate validation (title, description, price, enums)
   - PropertyUpdate partial validation
   - Nested model validation (PhysicalSpecs, LocationDetails)

3. `/Users/solo/Projects/_repos/bestays/apps/server/tests/services/test_property_service.py` (20 tests)
   - list_properties (filters, pagination, locale, translation fallback)
   - get_property_by_id (found, not found, soft delete exclusion)
   - create_property (valid, invalid amenity IDs)
   - update_property (ownership checks)
   - delete_property (soft delete)
   - Translation management (get_all_translations, update_translations)

4. `/Users/solo/Projects/_repos/bestays/apps/server/tests/api/v1/test_properties.py` (15 tests)
   - GET /api/v1/properties (list, filters, pagination)
   - GET /api/v1/properties/{id} (found, not found, locale)
   - POST /api/v1/properties (admin only, validation)
   - PUT /api/v1/properties/{id} (owner/admin)
   - DELETE /api/v1/properties/{id}
   - GET /api/v1/properties/{id}/translations
   - PUT /api/v1/properties/{id}/translations/{locale}

5. `/Users/solo/Projects/_repos/bestays/apps/server/tests/api/v1/test_amenities.py` (3 tests)
   - GET /api/v1/amenities (en, th, category filter)

6. `/Users/solo/Projects/_repos/bestays/apps/server/tests/api/v1/test_policies.py` (3 tests)
   - GET /api/v1/policies (en, th, category filter)

## Implementation Checklist

### Step 1: Read Specification
- [ ] Read `phase7-testing-spec.md` completely
- [ ] Understand fixture requirements
- [ ] Note authentication override patterns
- [ ] Review test data requirements

### Step 2: Update conftest.py
- [ ] Add test_amenities fixture (3 amenities with EN/TH translations)
- [ ] Add test_policies fixture (2 policies with EN/TH translations)
- [ ] Add test_property fixture (1 property with TH translations)
- [ ] Add property_factory fixture (on-demand property creation)
- [ ] Add user_client fixture (authenticated as test_user)
- [ ] Add admin_client fixture (authenticated as admin_user)
- [ ] Keep existing fixtures (test_user, admin_user already exist)

### Step 3: Create Model Tests
- [ ] Create test_property_v2.py in tests/models/
- [ ] Implement 6 tests from specification
- [ ] Run: `pytest tests/models/test_property_v2.py -v`

### Step 4: Create Schema Tests
- [ ] Create test_property_v2.py in tests/schemas/
- [ ] Implement 10 validation tests from specification
- [ ] Run: `pytest tests/schemas/test_property_v2.py -v`

### Step 5: Create Service Tests
- [ ] Create test_property_service.py in tests/services/
- [ ] Implement 20 service layer tests from specification
- [ ] Run: `pytest tests/services/test_property_service.py -v`

### Step 6: Create API Endpoint Tests
- [ ] Create test_properties.py in tests/api/v1/
- [ ] Create test_amenities.py in tests/api/v1/
- [ ] Create test_policies.py in tests/api/v1/
- [ ] Implement all endpoint tests from specification
- [ ] Run: `pytest tests/api/v1/test_properties.py -v`

### Step 7: Run Full Test Suite
```bash
cd /Users/solo/Projects/_repos/bestays/apps/server
pytest tests/models/test_property_v2.py tests/schemas/test_property_v2.py tests/services/test_property_service.py tests/api/v1/test_properties.py tests/api/v1/test_amenities.py tests/api/v1/test_policies.py -v
```

### Step 8: Generate Coverage Report
```bash
pytest tests/models/test_property_v2.py tests/schemas/test_property_v2.py tests/services/test_property_service.py tests/api/v1/test_properties.py tests/api/v1/test_amenities.py tests/api/v1/test_policies.py \
  --cov=server.models.property_v2 \
  --cov=server.models.amenity \
  --cov=server.models.policy \
  --cov=server.schemas.property_v2 \
  --cov=server.schemas.amenity \
  --cov=server.schemas.policy \
  --cov=server.services.property_service \
  --cov=server.services.amenity_service \
  --cov=server.services.policy_service \
  --cov=server.api.v1.endpoints.properties \
  --cov=server.api.v1.endpoints.amenities \
  --cov=server.api.v1.endpoints.policies \
  --cov-report=term-missing \
  --cov-report=html
```

### Step 9: Performance Validation
- [ ] Add performance test (100 properties, <200ms query)
- [ ] Add N+1 query detection test
- [ ] Run: `pytest tests/ --durations=10`

### Step 10: Fix Any Failures
- [ ] If tests fail, debug and fix issues
- [ ] Check import paths
- [ ] Verify database schema matches models
- [ ] Ensure seed data loaded (amenities/policies)

## Critical Notes

### Database Setup
**IMPORTANT:** Tests require PostgreSQL test database with seed data:

```bash
# Run migration
cd /Users/solo/Projects/_repos/bestays/apps/server
PYTHONPATH=/Users/solo/Projects/_repos/bestays/apps/server/src alembic upgrade head

# Run seed script (amenities + policies)
PYTHONPATH=/Users/solo/Projects/_repos/bestays/apps/server/src python app/scripts/seed_amenities_policies.py
```

### Authentication Override Pattern
The spec uses dependency overrides for authentication. Example:

```python
@pytest_asyncio.fixture
async def user_client(db_session: AsyncSession, test_user: User) -> AsyncGenerator[AsyncClient, None]:
    """Test client authenticated as regular user."""
    from server.dependencies import get_current_user

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = lambda: override_get_db(db_session)
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
```

### Test User vs Regular User
**Existing fixtures:**
- `test_user` - role="user" (already exists)
- `admin_user` - role="admin" (already exists)

**Use these fixtures** in Property V2 tests (don't create new ones).

### Price Conversion
**CRITICAL:** Database stores prices in satang/cents, API returns THB/USD:
- Database: `rent_price=3000000` (30,000 THB in satang)
- API response: `rent_price=30000` (30,000 THB)

Test assertions must account for this conversion.

## Success Criteria

After implementation, verify:

- ✅ All 57+ tests pass
- ✅ Coverage >80% for:
  - server.models.property_v2
  - server.schemas.property_v2
  - server.services.property_service
  - server.api.v1.endpoints.properties
- ✅ No SQL N+1 queries (verified via logging)
- ✅ Property listing <200ms with 100 properties
- ✅ All error cases tested (404, 403, 422, 400)
- ✅ Translation fallback tested (locale → EN → field)
- ✅ Soft delete behavior verified
- ✅ Authorization checks work (admin/owner permissions)

## Deliverables

Provide in your final report:

1. **Test Results:**
   - Output of `pytest -v` (all tests)
   - Number of tests passed/failed
   - Any failures debugged and fixed

2. **Coverage Report:**
   - Output of `pytest --cov` command
   - Coverage percentage for each module
   - List of uncovered lines (if any)

3. **Performance Metrics:**
   - Query execution times
   - Number of SQL queries per endpoint
   - Confirmation of no N+1 queries

4. **Files Created:**
   - List of all 7 files created/updated
   - Line counts per file

5. **Issues Found:**
   - Any bugs discovered during testing
   - How they were fixed
   - Any schema/API changes required

6. **Phase 7 Completion Report:**
   - Create `.claude/tasks/TASK-013/implementation/phase7-completion-report.md`
   - Include all above information
   - Mark Phase 7 as COMPLETE

## Working Directory

All commands should be run from:
```bash
/Users/solo/Projects/_repos/bestays/apps/server
```

## Environment

Tests use PostgreSQL test database (not in-memory SQLite):
- Database: `bestays_test`
- URL: `postgresql+asyncpg://bestays_user:bestays_password@localhost:5433/bestays_test`

Ensure PostgreSQL is running via Docker Compose before running tests.

---

**Start implementation now. Follow the specification exactly. Report back with comprehensive results!**
