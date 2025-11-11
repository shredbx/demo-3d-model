# Multi-Product Test Plan: US-021 Thai Localization

**Task:** TASK-010
**Story:** US-021
**Date:** 2025-11-08

Comprehensive test matrix for validating Thai localization across both products (bestays + realestate).

---

## Test Strategy

**Approach:** Test SHARED infrastructure on both products to ensure no collisions.

**Products:**
1. **bestays** - Primary implementation
2. **realestate** - Porting task (TASK-011)

**Test Levels:**
- Unit Tests (Backend service layer)
- E2E Tests (Frontend flows)
- Integration Tests (Cross-product isolation)
- Manual Smoke Tests (Visual verification)

---

## Unit Tests (Backend)

### Test Suite: `apps/server/tests/test_content_service.py`

**Coverage Target:** >90%

| Test Case | Description | Expected Result |
|-----------|-------------|----------------|
| test_get_content_english | Get English content | Returns correct English value |
| test_get_content_thai | Get Thai content | Returns correct Thai value |
| test_fallback_to_english | Request missing Thai translation | Returns English value |
| test_invalid_locale | Request with invalid locale | Raises validation error |
| test_cache_key_format | Verify cache key includes product | Key matches `content:{product}:{locale}:{key}` |
| test_cache_invalidation_thai | Update Thai content | Only Thai cache invalidated |
| test_cache_invalidation_english | Update English content | Only English cache invalidated |
| test_multi_product_isolation | Bestays vs Realestate cache | Different cache keys |
| test_composite_unique_constraint | Insert duplicate (key, locale) | Raises IntegrityError |
| test_create_content_both_locales | Create EN and TH for same key | Both created successfully |

---

## E2E Tests (Frontend)

### Test File 1: `locale-switching.spec.ts`

**Tests:** AC-1, AC-2, AC-5

| Test Case | Steps | Expected Result |
|-----------|-------|----------------|
| **AC-1: Default Locale** | 1. Navigate to `/`<br>2. Wait for redirect | URL changes to `/en`<br>English content displays |
| **AC-2: EN → TH Switch** | 1. Start on `/en`<br>2. Click "TH" button<br>3. Wait for navigation | URL changes to `/th`<br>Thai content displays<br>LocaleSwitcher shows "TH" as active |
| **AC-2: TH → EN Switch** | 1. Start on `/th`<br>2. Click "EN" button<br>3. Wait for navigation | URL changes to `/en`<br>English content displays<br>LocaleSwitcher shows "EN" as active |
| **AC-5: Locale Persistence** | 1. Navigate to `/th/`<br>2. Click link to another page (e.g., `/th/about`)<br>3. Navigate back to homepage | URL remains `/th/...`<br>Thai content persists |

### Test File 2: `locale-fallback.spec.ts`

**Tests:** AC-3, AC-4

| Test Case | Steps | Expected Result |
|-----------|-------|----------------|
| **AC-3: Independent Editing** | 1. Login as admin<br>2. Edit Thai content for "hero.title"<br>3. Navigate to `/en`<br>4. Check English content | Only Thai updated<br>English unchanged<br>Cache invalidated for Thai only |
| **AC-4: Fallback Logic** | 1. Request Thai content for key without Thai translation<br>2. Check displayed content | English content displayed<br>No error shown<br>Graceful degradation |

### Test File 3: `multi-product-locale.spec.ts`

**Tests:** Multi-product isolation

| Test Case | Steps | Expected Result |
|-----------|-------|----------------|
| **Cache Isolation** | 1. Edit bestays Thai content<br>2. Check realestate Thai content<br>3. Verify cache keys | Bestays cache: `content:bestays:th:*`<br>Realestate cache: `content:realestate:th:*`<br>No collision |
| **Database Isolation** | 1. Query bestays_dev for Thai content<br>2. Query realestate_dev for Thai content | Different counts<br>Product-specific content<br>No shared rows |

---

## Multi-Product Test Matrix

### Bestays Product Tests

| Feature | Test | Status | Notes |
|---------|------|--------|-------|
| **EN Locale** | Navigate to `/en/` | ⏳ Pending | English content displays |
| **TH Locale** | Navigate to `/th/` | ⏳ Pending | Thai content displays |
| **Locale Switch EN→TH** | Click TH button on `/en` | ⏳ Pending | URL changes to `/th` |
| **Locale Switch TH→EN** | Click EN button on `/th` | ⏳ Pending | URL changes to `/en` |
| **Thai Content Editable** | Admin edits Thai content | ⏳ Pending | Only Thai version updated |
| **English Content Editable** | Admin edits English content | ⏳ Pending | Only English version updated |
| **Fallback Logic** | Request missing Thai translation | ⏳ Pending | Returns English |
| **Cache Isolation** | Check cache keys | ⏳ Pending | Includes `bestays` identifier |
| **Thai Characters** | View Thai content | ⏳ Pending | No garbled characters |
| **Locale Persistence** | Navigate between pages | ⏳ Pending | Locale preserved in URL |

### Real Estate Product Tests

| Feature | Test | Status | Notes |
|---------|------|--------|-------|
| **EN Locale** | Navigate to `/en/` | ⏳ Pending | English content displays |
| **TH Locale** | Navigate to `/th/` | ⏳ Pending | Thai content displays |
| **Locale Switch EN→TH** | Click TH button on `/en` | ⏳ Pending | URL changes to `/th` |
| **Locale Switch TH→EN** | Click EN button on `/th` | ⏳ Pending | URL changes to `/en` |
| **Thai Content Editable** | Admin edits Thai content | ⏳ Pending | Only Thai version updated |
| **English Content Editable** | Admin edits English content | ⏳ Pending | Only English version updated |
| **Fallback Logic** | Request missing Thai translation | ⏳ Pending | Returns English |
| **Cache Isolation** | Check cache keys | ⏳ Pending | Includes `realestate` identifier |
| **Thai Characters** | View Thai content | ⏳ Pending | No garbled characters |
| **Locale Persistence** | Navigate between pages | ⏳ Pending | Locale preserved in URL |

### Cross-Product Tests

| Feature | Test | Status | Notes |
|---------|------|--------|-------|
| **Cache Collision** | Edit bestays content, check realestate | ⏳ Pending | No collision detected |
| **Database Collision** | Query both databases | ⏳ Pending | Isolated content |
| **CORS Configuration** | Both frontends call API | ⏳ Pending | No CORS errors |
| **Redis Key Namespace** | Check all cache keys | ⏳ Pending | Product identifier in keys |

---

## Browser Compatibility Matrix

### Bestays Product

| Browser | EN Locale | TH Locale | Switching | Thai Chars | Status |
|---------|-----------|-----------|-----------|------------|--------|
| **Chrome** | ⏳ | ⏳ | ⏳ | ⏳ | Pending |
| **Firefox** | ⏳ | ⏳ | ⏳ | ⏳ | Pending |
| **Safari** | ⏳ | ⏳ | ⏳ | ⏳ | Pending |

### Real Estate Product

| Browser | EN Locale | TH Locale | Switching | Thai Chars | Status |
|---------|-----------|-----------|-----------|------------|--------|
| **Chrome** | ⏳ | ⏳ | ⏳ | ⏳ | Pending |
| **Firefox** | ⏳ | ⏳ | ⏳ | ⏳ | Pending |
| **Safari** | ⏳ | ⏳ | ⏳ | ⏳ | Pending |

---

## Manual Smoke Tests

### Pre-Deployment Checklist

**Bestays Product:**
- [ ] Visit `http://localhost:5183/`
- [ ] Verify redirect to `/en`
- [ ] Verify English content displays
- [ ] Click "TH" button
- [ ] Verify URL changes to `/th`
- [ ] Verify Thai content displays
- [ ] Verify Thai characters not garbled: ยินดีต้อนรับสู่ Bestays
- [ ] Click "EN" button
- [ ] Verify URL changes to `/en`
- [ ] Verify English content displays

**Real Estate Product:**
- [ ] Visit `http://localhost:5184/`
- [ ] Repeat all Bestays tests
- [ ] Verify different content from Bestays

**Cross-Product:**
- [ ] Login as admin on Bestays
- [ ] Edit Thai content: "hero.title"
- [ ] Navigate to Real Estate
- [ ] Verify Real Estate content unchanged
- [ ] Check Redis: `docker exec -it bestays-redis-dev redis-cli KEYS "content:*"`
- [ ] Verify separate cache keys for each product

---

## Performance Tests

### Cache Hit Rate

**Target:** >90%

**Test:**
1. Clear cache: `docker exec -it bestays-redis-dev redis-cli FLUSHDB`
2. Load `/en/` page (cache miss - populates cache)
3. Reload `/en/` page (cache hit)
4. Load `/th/` page (cache miss - populates cache)
5. Reload `/th/` page (cache hit)
6. Measure cache hit rate

**Expected:** 50% hit rate on first round (2 hits / 4 requests)
**Expected:** 100% hit rate on subsequent reloads

### API Response Time

**Target:** <100ms for cached content

**Test:**
1. Load `/en/` page
2. Measure API response time for each content fetch
3. Load `/th/` page
4. Measure API response time for each content fetch

**Expected:** <50ms for cache hits, <200ms for cache misses

---

## Test Data Management

### Seed Data

**Bestays Thai Translations:**
```
hero.title: "ยินดีต้อนรับสู่ Bestays"
hero.subtitle: "ค้นหาที่พักในฝันของคุณ"
features.title: "ทำไมต้องเลือก Bestays"
...
```

**Real Estate Thai Translations:**
```
hero.title: "ค้นหาอสังหาริมทรัพย์ในฝันของคุณ"
hero.subtitle: "บ้าน คอนโด และที่ดินกว่า 10,000 รายการ"
...
```

### Test Data Cleanup

**After Each Test:**
```typescript
// Delete test content keys
await page.evaluate(async () => {
  const testKeys = ['test-key-1', 'test-key-2'];
  for (const key of testKeys) {
    await fetch(`/api/v1/content/${key}`, { method: 'DELETE' });
  }
});

// Clear test cache keys
await page.evaluate(async () => {
  await fetch('/api/v1/cache/clear?pattern=content:*:test-*');
});
```

---

## Acceptance Criteria Validation

| AC | Description | Test File | Test Case | Status |
|----|-------------|-----------|-----------|--------|
| AC-1 | Default Locale | locale-switching.spec.ts | test_default_locale_redirect | ⏳ |
| AC-2 | Locale Switching | locale-switching.spec.ts | test_locale_switch_en_to_th<br>test_locale_switch_th_to_en | ⏳ |
| AC-3 | Independent Editing | locale-fallback.spec.ts | test_independent_locale_editing | ⏳ |
| AC-4 | Fallback Logic | locale-fallback.spec.ts | test_fallback_to_english | ⏳ |
| AC-5 | Locale Persistence | locale-switching.spec.ts | test_locale_persistence | ⏳ |

---

## Regression Tests

### US-020 Functionality (Must Not Break)

- [ ] Editable content still works
- [ ] Edit dialog opens
- [ ] Content saves successfully
- [ ] Cache invalidates correctly
- [ ] RBAC still enforced (admin/agent only)

### Existing Homepage (Must Not Break)

- [ ] Homepage loads
- [ ] Hero section displays
- [ ] Features section displays
- [ ] Footer displays
- [ ] All images load

---

## Test Execution Schedule

### Phase 1: Unit Tests (Backend)
**When:** After Phase 2 (Backend API) complete
**Duration:** 1 hour
**Executor:** dev-backend-fastapi subagent

### Phase 2: E2E Tests (Frontend)
**When:** After Phase 3 (Frontend) complete
**Duration:** 3 hours
**Executor:** playwright-e2e-tester subagent

### Phase 3: Manual Smoke Tests
**When:** After all E2E tests pass
**Duration:** 30 minutes
**Executor:** Human (user)

### Phase 4: Performance Tests
**When:** After smoke tests pass
**Duration:** 1 hour
**Executor:** Human or automated script

---

## Test Results Summary

**Unit Tests:**
- Total: ____ tests
- Passed: ____ tests
- Failed: ____ tests
- Coverage: _____%

**E2E Tests:**
- Total: ____ tests
- Passed: ____ tests
- Failed: ____ tests
- Browsers: Chrome ✓, Firefox ✓, Safari ✓

**Manual Smoke Tests:**
- Bestays: ✓ / ✗
- Real Estate: ✓ / ✗
- Cross-Product: ✓ / ✗

**Performance Tests:**
- Cache Hit Rate: _____%
- API Response Time: ____ms

**Overall Status:** ✅ PASS / ❌ FAIL

---

## Issues Found

| ID | Description | Severity | Status | Resolution |
|----|-------------|----------|--------|------------|
| | | | | |

---

## Sign-Off

**Test Execution Complete:**
- [ ] All unit tests pass
- [ ] All E2E tests pass
- [ ] Manual smoke tests pass
- [ ] Performance tests pass
- [ ] No regressions detected

**Approved By:**
- Developer: _________________ Date: _________
- QA: _________________ Date: _________
- Product Owner: _________________ Date: _________
