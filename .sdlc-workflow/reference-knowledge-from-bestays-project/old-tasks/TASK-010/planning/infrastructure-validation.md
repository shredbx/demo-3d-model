# Multi-Product Infrastructure Validation

**Task:** TASK-010
**Story:** US-021
**Date:** 2025-11-08

This checklist ensures proper multi-product infrastructure setup for Thai localization.

---

## Products Affected

- [x] **bestays** (primary implementation)
- [ ] **realestate** (porting task to be created)

**Strategy:** Implement for bestays first, then port to realestate via TASK-011 (porting task).

---

## Shared Infrastructure

### Database Schema

- [ ] **bestays_dev:** locale column added
  - Command: `docker exec -it bestays-postgres-dev psql -U bestays_user -d bestays_dev -c "\d content_dictionary"`
  - Expected: Column `locale varchar(2) NOT NULL`
  
- [ ] **realestate_dev:** locale column added
  - Command: `docker exec -it bestays-postgres-dev psql -U realestate_user -d realestate_dev -c "\d content_dictionary"`
  - Expected: Column `locale varchar(2) NOT NULL`

- [ ] **bestays_dev:** Composite UNIQUE constraint exists
  - Command: `docker exec -it bestays-postgres-dev psql -U bestays_user -d bestays_dev -c "\d+ content_dictionary"`
  - Expected: `content_dictionary_key_locale_unique` constraint

- [ ] **realestate_dev:** Composite UNIQUE constraint exists
  - Command: Same as above for realestate_dev
  - Expected: `content_dictionary_key_locale_unique` constraint

- [ ] **bestays_dev:** Index exists on (key, locale)
  - Command: `docker exec -it bestays-postgres-dev psql -U bestays_user -d bestays_dev -c "\di+ idx_content_dictionary_key_locale"`
  - Expected: Index with columns (key, locale)

- [ ] **realestate_dev:** Index exists on (key, locale)
  - Command: Same as above for realestate_dev
  - Expected: Index with columns (key, locale)

### Redis Cache Keys

- [ ] Cache keys use product identifier
  - Format: `content:{product}:{locale}:{key}`
  - Example: `content:bestays:th:hero.title`
  - Verification: `docker exec -it bestays-redis-dev redis-cli KEYS "content:*"`

- [ ] No collision between products
  - Bestays keys: `content:bestays:*`
  - Real Estate keys: `content:realestate:*`
  - Verification: Check no overlap in keys

### Backend API

- [ ] CORS configured for BOTH frontends
  - Bestays: `http://localhost:5183`
  - Real Estate: `http://localhost:5184`
  - File: `apps/server/src/server/config.py`
  - Variable: `ALLOWED_ORIGINS`

- [ ] Product identifier configured
  - Environment variable: `PRODUCT_NAME`
  - Bestays: `PRODUCT_NAME=bestays`
  - Real Estate: `PRODUCT_NAME=realestate`
  - File: `.env.bestays` and `.env.realestate`

### Frontend

- [ ] Both products use same routing pattern
  - Bestays: `/en/`, `/th/`
  - Real Estate: `/en/`, `/th/`
  - Pattern: `routes/[lang]/`

- [ ] Both products use same i18n context
  - File: `lib/i18n/context.svelte.ts`
  - Same implementation, different content values

---

## Environment Validation

### .env.bestays

- [ ] No changes needed for US-021
- [ ] `PRODUCT_NAME=bestays` already set (US-020)
- [ ] Database URL correct: `postgresql://bestays_user:bestays_pass@postgres:5432/bestays_dev`
- [ ] Redis URL correct: `redis://redis:6379/0`

### .env.realestate

- [ ] No changes needed for US-021
- [ ] `PRODUCT_NAME=realestate` already set (US-020)
- [ ] Database URL correct: `postgresql://realestate_user:realestate_pass@postgres:5432/realestate_dev`
- [ ] Redis URL correct: `redis://redis:6379/0`

### CORS Configuration

- [ ] Both frontend URLs in ALLOWED_ORIGINS
  ```python
  ALLOWED_ORIGINS = [
      "http://localhost:5183",  # Bestays
      "http://localhost:5184",  # Real Estate
  ]
  ```
- [ ] File: `apps/server/src/server/config.py`
- [ ] No changes needed (already configured in US-020)

---

## Migration Validation

### bestays_dev Migration

- [ ] Migration file created
  - File: `apps/server/alembic/versions/XXXX_add_locale_to_content_dictionary.py`
  
- [ ] Migration applied successfully
  - Command: `docker exec -it bestays-server-dev alembic upgrade head`
  - Expected output: `Running upgrade YYYY -> XXXX, Add locale column to content_dictionary table`

- [ ] Verification: locale column exists
  - Command: `docker exec -it bestays-postgres-dev psql -U bestays_user -d bestays_dev -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'content_dictionary' AND column_name = 'locale';"`
  - Expected: `locale | character varying(2) | NO`

- [ ] Verification: Composite UNIQUE constraint enforced
  - Command: `docker exec -it bestays-postgres-dev psql -U bestays_user -d bestays_dev -c "INSERT INTO content_dictionary (key, locale, value) VALUES ('test', 'en', 'Test'); INSERT INTO content_dictionary (key, locale, value) VALUES ('test', 'en', 'Duplicate');"`
  - Expected: Error (duplicate key violates unique constraint)

- [ ] Seed data inserted
  - Command: `docker exec -it bestays-server-dev python -m server.scripts.seed_thai_content_bestays`
  - Expected output: `Successfully seeded X Thai translations for Bestays`

- [ ] Verification: Thai content exists
  - Command: `docker exec -it bestays-postgres-dev psql -U bestays_user -d bestays_dev -c "SELECT key, locale, value FROM content_dictionary WHERE locale = 'th' LIMIT 5;"`
  - Expected: 5 rows with Thai content

- [ ] Index created
  - Command: `docker exec -it bestays-postgres-dev psql -U bestays_user -d bestays_dev -c "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'content_dictionary' AND indexname = 'idx_content_dictionary_key_locale';"`
  - Expected: Index definition returned

### realestate_dev Migration

- [ ] Migration applied successfully
  - Command: `docker exec -it bestays-server-dev alembic upgrade head`
  - Expected: Same as bestays_dev

- [ ] Verification: locale column exists
  - Command: Same as bestays_dev but for realestate_dev

- [ ] Verification: Composite UNIQUE constraint enforced
  - Command: Same as bestays_dev but for realestate_dev

- [ ] Seed data inserted
  - Command: `docker exec -it bestays-server-dev python -m server.scripts.seed_thai_content_realestate`
  - Expected output: `Successfully seeded X Thai translations for Real Estate`

- [ ] Verification: Thai content exists
  - Command: Same as bestays_dev but for realestate_dev

- [ ] Index created
  - Command: Same as bestays_dev but for realestate_dev

---

## Smoke Test Plan

### Bestays Product

- [ ] **Test 1:** `/en/` route loads
  - Navigate to: `http://localhost:5183/en/`
  - Expected: English homepage displays

- [ ] **Test 2:** `/th/` route loads
  - Navigate to: `http://localhost:5183/th/`
  - Expected: Thai homepage displays with Thai content

- [ ] **Test 3:** Locale switching EN → TH
  - Start on: `http://localhost:5183/en/`
  - Click: "TH" button
  - Expected: URL changes to `/th/`, Thai content displays

- [ ] **Test 4:** Locale switching TH → EN
  - Start on: `http://localhost:5183/th/`
  - Click: "EN" button
  - Expected: URL changes to `/en/`, English content displays

- [ ] **Test 5:** Thai characters display correctly
  - Navigate to: `http://localhost:5183/th/`
  - Expected: ยินดีต้อนรับสู่ Bestays (no garbled characters)

- [ ] **Test 6:** Cache isolation
  - Check Redis keys: `docker exec -it bestays-redis-dev redis-cli KEYS "content:bestays:*"`
  - Expected: Keys include `content:bestays:en:*` and `content:bestays:th:*`

### Real Estate Product (After Porting)

- [ ] **Test 1:** `/en/` route loads
  - Navigate to: `http://localhost:5184/en/`
  - Expected: English homepage displays

- [ ] **Test 2:** `/th/` route loads
  - Navigate to: `http://localhost:5184/th/`
  - Expected: Thai homepage displays

- [ ] **Test 3:** Locale switching works
  - Same as Bestays tests

- [ ] **Test 4:** Thai characters display correctly
  - Same as Bestays test

- [ ] **Test 5:** Cache isolation from Bestays
  - Check Redis keys: `docker exec -it bestays-redis-dev redis-cli KEYS "content:realestate:*"`
  - Expected: Separate keys from bestays

### Cross-Product Validation

- [ ] **Test 1:** Editing bestays content doesn't affect realestate
  - Edit: Bestays Thai content for `hero.title`
  - Verify: Real Estate `hero.title` unchanged
  - Check: Cache keys `content:bestays:th:hero.title` and `content:realestate:th:hero.title` are different

- [ ] **Test 2:** Cache keys isolated by product
  - Command: `docker exec -it bestays-redis-dev redis-cli KEYS "content:*"`
  - Expected: Keys grouped by product (`bestays` vs `realestate`)
  - No overlap

- [ ] **Test 3:** Database isolation
  - Query bestays_dev: `SELECT count(*) FROM content_dictionary WHERE locale = 'th';`
  - Query realestate_dev: `SELECT count(*) FROM content_dictionary WHERE locale = 'th';`
  - Expected: Different counts (product-specific content)

---

## Rollback Verification

### Database Rollback

- [ ] Rollback migration tested
  - Command: `docker exec -it bestays-server-dev alembic downgrade -1`
  - Expected: `locale` column dropped, old UNIQUE constraint restored

- [ ] Re-apply migration works
  - Command: `docker exec -it bestays-server-dev alembic upgrade head`
  - Expected: Migration re-applies successfully

### Cache Rollback

- [ ] Old cache keys still work during transition
  - Backend supports both `content:{key}` and `content:{product}:{locale}:{key}`
  - Verify: Backend can read old format keys

- [ ] Cache clear procedure documented
  - Command: `docker exec -it bestays-redis-dev redis-cli FLUSHDB`
  - Impact: All cache cleared, repopulates from database

---

## Deployment Checklist

### Pre-Deployment

- [ ] All infrastructure validation tests pass
- [ ] Both databases migrated successfully
- [ ] Thai seed data inserted for both products
- [ ] Backend unit tests pass (>90% coverage)
- [ ] Frontend E2E tests pass (all ACs validated)

### Deployment Steps

1. [ ] Apply database migration (off-peak hours)
2. [ ] Deploy backend with locale support
3. [ ] Deploy frontend with [lang] routing
4. [ ] Run smoke tests on both products
5. [ ] Monitor cache hit rate and error logs

### Post-Deployment

- [ ] Smoke tests pass on both products
- [ ] Cache hit rate >90%
- [ ] No error rate increase
- [ ] Thai characters display correctly
- [ ] Locale switching works smoothly
- [ ] No cache collisions detected

---

## Issues Encountered

| Date | Issue | Resolution | Impact |
|------|-------|------------|--------|
| | | | |

---

## Sign-Off

**DevOps Phase:**
- [ ] All database migrations applied successfully
- [ ] Thai seed data inserted for both products
- [ ] Infrastructure validation complete
- Signed: _________________ Date: _________

**Backend Phase:**
- [ ] API supports locale parameter
- [ ] Fallback logic implemented
- [ ] Unit tests passing
- Signed: _________________ Date: _________

**Frontend Phase:**
- [ ] Routes restructured
- [ ] Locale switching functional
- [ ] Components updated
- Signed: _________________ Date: _________

**E2E Testing Phase:**
- [ ] All ACs validated
- [ ] Multi-product isolation confirmed
- [ ] Test suite passing
- Signed: _________________ Date: _________

**Final Approval:**
- [ ] All phases complete
- [ ] Smoke tests pass
- [ ] Ready for production deployment
- Signed: _________________ Date: _________
