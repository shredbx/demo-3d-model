# Implementation Plan: US-021 Thai Localization

**Story:** US-021 - Thai Localization & Locale Switching
**Task:** TASK-010
**Product:** bestays (implement first) → realestate (porting task)
**Complexity:** Medium
**Estimated Time:** 5.5 days

---

## Overview

Enable Thai language support for the Bestays platform by adding locale support to the content management system. This builds on the foundation established in US-020 (Homepage Editable Content) by extending the database schema, API, and frontend to handle multiple locales.

**Key Components:**
1. Database: Add `locale` column with composite UNIQUE constraint
2. Backend: Accept `?locale=` parameter with fallback logic
3. Frontend: Restructure routes to `/[lang]/` pattern
4. i18n: Custom Svelte 5 context using runes (~50 lines)
5. Component: LocaleSwitcher for EN|TH toggle

---

## Architecture Decisions

### Decision 1: [lang] Parameter Routing (APPROVED by Svelte MCP)

**Choice:** Use SvelteKit's `[lang]` parameter routing instead of external i18n library.

**Rationale:**
- Native SvelteKit pattern (validated against official docs)
- SSR-friendly (locale determined server-side)
- SEO-friendly (crawlable URLs: `/en/`, `/th/`)
- No bundle size overhead
- Simple to implement and maintain

**File Structure:**
```
routes/
  +page.svelte           → Redirect to /en (default)
  [lang]/
    +layout.svelte       → Locale provider (setContext)
    +layout.ts           → Validate lang param, return { locale }
    +page.svelte         → Homepage (uses locale context)
    +page.ts             → SSR load with locale parameter
```

**Alternative Considered:** External libraries (svelte-i18n, paraglide)
**Why Rejected:** Overkill for simple EN/TH switching, adds bundle size, complicates SSR

---

### Decision 2: Custom Svelte 5 Context (~50 lines)

**Choice:** Build custom i18n context using Svelte 5 runes and context API.

**Implementation:**
```typescript
// lib/i18n/context.svelte.ts
type Locale = 'en' | 'th';

class LocaleContext {
  locale = $state<Locale>('en');
  
  setLocale(newLocale: Locale) {
    this.locale = newLocale;
  }
}

const LOCALE_KEY = Symbol('locale');

export function setLocaleContext(initialLocale: Locale) {
  const ctx = new LocaleContext();
  ctx.locale = initialLocale;
  setContext(LOCALE_KEY, ctx);
  return ctx;
}

export function getLocaleContext() {
  return getContext<LocaleContext>(LOCALE_KEY);
}
```

**Rationale:**
- Leverages Svelte 5 reactivity system
- Type-safe with TypeScript
- No external dependencies
- Follows official Svelte patterns

---

### Decision 3: Cache Key Format Change

**Old Format (US-020):** `content:{key}`
**New Format (US-021):** `content:{product}:{locale}:{key}`

**Rationale:**
- Prevents cache collision between products (lesson from US-020)
- Isolates locale-specific content
- Enables independent cache invalidation per locale
- Supports multi-product architecture

**Migration Strategy:**
- Backend supports BOTH formats during transition (backward compatibility)
- Old cache keys expire naturally (TTL: 1hr)
- Clear all cache keys after deployment (safe operation)

---

### Decision 4: Phased Database Migration

**Approach:** Safe 3-step migration to avoid downtime.

**Steps:**
1. Add nullable `locale` column
2. Backfill existing rows with 'en'
3. Set NOT NULL constraint + composite UNIQUE(key, locale)

**Rationale:**
- Zero downtime deployment
- Existing API calls continue working
- Rollback-friendly (can revert constraint changes)

**Alternative Considered:** Add NOT NULL immediately
**Why Rejected:** Requires API deployment in lockstep with migration (risky)

---

### Decision 5: Fallback Logic for Missing Translations

**Behavior:**
1. Try to fetch (key, locale) from database
2. If not found AND locale != 'en', try (key, 'en')
3. If still not found, return 404

**Rationale:**
- Graceful degradation (users always see content)
- Allows incremental Thai translation rollout
- Prevents empty content areas
- Aligns with AC-4 (Fallback Logic)

---

## Implementation Steps

### Phase 1: DevOps Infrastructure (devops-infra) - 1 day

**Subagent:** `devops-infra`
**Branch:** `feat/TASK-010-US-021` (current)

**Tasks:**
1. Create Alembic migration: `add_locale_to_content_dictionary.py`
   - Add `locale VARCHAR(2)` column (nullable)
   - Backfill `locale = 'en'` for existing rows
   - Set `locale NOT NULL`
   - Drop `UNIQUE(key)` constraint
   - Add `UNIQUE(key, locale)` constraint
   - Create index: `idx_content_dictionary_key_locale`

2. Apply migration to `bestays_dev` database
   - Verify constraint creation
   - Verify index creation
   - Test composite UNIQUE enforcement

3. Apply migration to `realestate_dev` database
   - Same verification steps
   - Ensure no cross-database contamination

4. Create Thai seed data for bestays:
   - File: `seed_thai_content_bestays.py`
   - Keys: `hero.title`, `hero.subtitle`, `features.title`, etc.
   - Thai translations for homepage content

5. Create Thai seed data for realestate:
   - File: `seed_thai_content_realestate.py`
   - Product-specific Thai translations

6. Update infrastructure validation checklist
   - Document cache key format change
   - Document CORS configuration (both frontends)
   - Document database changes

**Deliverables:**
- Migration file in `apps/server/alembic/versions/`
- Seed data scripts in `apps/server/src/server/scripts/`
- Both databases migrated and seeded
- Infrastructure validation checklist updated

---

### Phase 2: Backend API (dev-backend-fastapi) - 1.5 days

**Subagent:** `dev-backend-fastapi`
**Dependencies:** Phase 1 complete (database schema must exist)

**Tasks:**
1. Update SQLAlchemy model (`models/content.py`):
   - Add `locale` column: `Column(String(2), nullable=False, default='en')`
   - Update `__repr__` to include locale
   - Add composite unique constraint in declarative model

2. Update Pydantic schemas (`schemas/content.py`):
   - `ContentResponse`: Add `locale: str` field
   - `ContentUpdate`: Add `locale: str` field
   - Add locale validation (only 'en' or 'th')

3. Update ContentService (`services/content_service.py`):
   - Add `locale` parameter to `get_content(key: str, locale: str = 'en')`
   - Implement fallback logic: Try (key, locale) → Try (key, 'en') → 404
   - Update cache key format: `f"content:{product}:{locale}:{key}"`
   - Update `update_content()` to invalidate only affected locale cache
   - Add `get_product_from_config()` helper (reads from ENV)

4. Update API endpoint (`api/v1/endpoints/content.py`):
   - GET `/api/v1/content/{key}`: Add `locale: str = Query('en')` parameter
   - PUT `/api/v1/content/{key}`: Add `locale` to request body
   - Validate locale in ['en', 'th']
   - Pass product identifier to service layer

5. Write unit tests (`tests/test_content_service.py`):
   - Test fallback logic (Thai missing → returns English)
   - Test cache invalidation (only affected locale)
   - Test multi-product isolation (bestays cache != realestate cache)
   - Test locale validation (reject invalid locales)

**Deliverables:**
- Updated models, schemas, service, endpoint
- Comprehensive unit tests (>90% coverage)
- API supports `?locale=en` and `?locale=th`
- Fallback logic working
- Cache keys isolated by product and locale

---

### Phase 3: Frontend Routes & Components (dev-frontend-svelte) - 2 days

**Subagent:** `dev-frontend-svelte`
**Dependencies:** Phase 2 complete (API must support locale parameter)

**Tasks:**
1. Create i18n context (`lib/i18n/context.svelte.ts`):
   - Define `Locale` type ('en' | 'th')
   - Implement `LocaleContext` class with `$state`
   - Export `setLocaleContext()` and `getLocaleContext()`
   - ~40 lines total

2. Create i18n types (`lib/i18n/types.ts`):
   - Export `Locale` type
   - Export locale constants

3. Restructure routes:
   - **Root redirect** (`routes/+page.svelte`):
     - Detect default locale (browser preference or 'en')
     - Redirect to `/en` or `/th`
   
   - **Lang layout** (`routes/[lang]/+layout.ts`):
     - Validate `lang` param (must be 'en' or 'th')
     - If invalid → redirect to `/en`
     - Return `{ locale: lang }`
   
   - **Lang layout component** (`routes/[lang]/+layout.svelte`):
     - Call `setLocaleContext(data.locale)`
     - Render `{@render children()}`
   
   - **Homepage** (move `routes/+page.svelte` → `routes/[lang]/+page.svelte`):
     - Use existing homepage component
     - No changes needed (uses `data` from load)
   
   - **Homepage load** (`routes/[lang]/+page.ts`):
     - Get `locale` from parent layout
     - Pass `locale` to API calls: `fetch(`/api/v1/content/${key}?locale=${locale}`)`
     - Update all content fetch calls

4. Create LocaleSwitcher component (`lib/components/LocaleSwitcher.svelte`):
   - Display "EN | TH" toggle buttons
   - Get current locale from context
   - On click: Navigate to `/{newLocale}{currentPath}`
   - Preserve path structure (e.g., `/en/login` → `/th/login`)
   - Style active locale (bold or underlined)

5. Update EditableText component (`lib/components/ui/EditableText.svelte`):
   - Import `getLocaleContext()`
   - Get current locale from context
   - Pass locale to API calls when editing

6. Update content API client (`lib/api/content.ts`):
   - Add `locale` parameter to `getContent(key, locale)`
   - Add `locale` parameter to `updateContent(key, value, locale)`
   - Handle fallback responses (English returned for missing Thai)

7. Add LocaleSwitcher to header:
   - Update `[lang]/+layout.svelte` to include LocaleSwitcher
   - Position in top-right corner

8. Update all navigation links:
   - Ensure links preserve locale: `href="/{locale}/about"`

**Deliverables:**
- i18n context (~50 lines)
- Restructured routes with [lang] parameter
- LocaleSwitcher component
- Updated EditableText to use locale context
- All homepage content respects current locale
- Locale switching works (AC-2)
- Default locale redirect works (AC-1)
- Locale persistence works (AC-5)

---

### Phase 4: E2E Testing (playwright-e2e-tester) - 1 day

**Subagent:** `playwright-e2e-tester`
**Dependencies:** Phase 3 complete (frontend must be functional)

**Tasks:**
1. Write `locale-switching.spec.ts`:
   - **Test 1: Default Locale (AC-1)**
     - Navigate to `/`
     - Verify redirect to `/en`
     - Verify English content displayed
   
   - **Test 2: Locale Switching (AC-2)**
     - Start on `/en`
     - Click "TH" button
     - Verify URL changes to `/th`
     - Verify Thai content displayed
     - Click "EN" button
     - Verify URL changes to `/en`
     - Verify English content displayed
   
   - **Test 5: Locale Persistence (AC-5)**
     - Navigate to `/th/`
     - Click link to `/th/login` (when login exists)
     - Verify still in Thai locale
     - Navigate back to homepage
     - Verify still on `/th/`

2. Write `locale-fallback.spec.ts`:
   - **Test 4: Fallback Logic (AC-4)**
     - Request Thai content for key without Thai translation
     - Verify English content returned
     - Verify no error thrown
   
   - **Test 3: Independent Editing (AC-3)**
     - Login as admin
     - Edit Thai content for key "hero.title"
     - Verify only Thai version updated
     - Navigate to `/en`
     - Verify English version unchanged
     - Verify cache invalidated only for Thai

3. Write `multi-product-locale.spec.ts`:
   - **Test 6: Multi-Product Isolation**
     - Edit bestays Thai content
     - Verify realestate Thai content unchanged
     - Verify cache keys include product identifier
     - Verify no cross-product contamination

4. Implement test data cleanup:
   - After each test: Delete test content keys
   - Clear Redis cache for test keys
   - Use transactions where possible

5. Run full test suite on both products:
   - Bestays: All tests pass
   - Real Estate: All tests pass (after porting)

**Deliverables:**
- 3 E2E test files with comprehensive scenarios
- Test data cleanup implemented
- All 5 Acceptance Criteria validated
- Multi-product isolation validated
- CI/CD integration (tests run on push)

---

## File Changes

### Files to CREATE (10 new files)

**Backend (3 files):**
1. `apps/server/alembic/versions/XXXX_add_locale_to_content_dictionary.py`
2. `apps/server/src/server/scripts/seed_thai_content_bestays.py`
3. `apps/server/src/server/scripts/seed_thai_content_realestate.py`

**Frontend (4 files):**
4. `apps/frontend/src/lib/i18n/context.svelte.ts`
5. `apps/frontend/src/lib/i18n/types.ts`
6. `apps/frontend/src/routes/[lang]/+layout.svelte`
7. `apps/frontend/src/routes/[lang]/+layout.ts`
8. `apps/frontend/src/lib/components/LocaleSwitcher.svelte`

**E2E Tests (3 files):**
9. `apps/frontend/tests/e2e/locale-switching.spec.ts`
10. `apps/frontend/tests/e2e/locale-fallback.spec.ts`
11. `apps/frontend/tests/e2e/multi-product-locale.spec.ts`

### Files to MODIFY (10 files)

**Backend (5 files):**
1. `apps/server/src/server/models/content.py` - Add locale field
2. `apps/server/src/server/services/content_service.py` - Locale param, fallback logic
3. `apps/server/src/server/api/v1/endpoints/content.py` - Query param
4. `apps/server/src/server/schemas/content.py` - Add locale field
5. `apps/server/tests/test_content_service.py` - Add locale tests

**Frontend (5 files):**
6. `apps/frontend/src/routes/+page.svelte` - Redirect logic
7. `apps/frontend/src/routes/[lang]/+page.svelte` - Move from routes/+page.svelte
8. `apps/frontend/src/routes/[lang]/+page.ts` - Add locale param to loads
9. `apps/frontend/src/lib/components/ui/EditableText.svelte` - Use locale context
10. `apps/frontend/src/lib/api/content.ts` - Add locale parameter

**Total:** 20 files (10 new, 10 modified)

---

## Testing Strategy

### Unit Tests (Backend)

**Coverage Target:** >90%

**Scenarios:**
- Locale validation (reject invalid locales)
- Fallback logic (Thai missing → English)
- Cache invalidation (only affected locale)
- Multi-product isolation (cache keys include product)
- Database constraints (UNIQUE on key + locale)

### E2E Tests (Frontend)

**Coverage:** All 5 Acceptance Criteria

**Test Matrix:**
- Default locale redirect
- Locale switching (EN ↔ TH)
- Independent locale editing
- Fallback for missing translations
- Locale persistence across navigation
- Multi-product isolation

**Browsers:** Chrome, Firefox, Safari (via Playwright)

**Cleanup Strategy:**
- Delete test content keys after each test
- Clear Redis cache for test keys
- Use database transactions where possible

### Manual Testing

**Smoke Tests (Post-Deployment):**
- [ ] Bestays `/en/` route works
- [ ] Bestays `/th/` route works
- [ ] Real Estate `/en/` route works
- [ ] Real Estate `/th/` route works
- [ ] Cache isolation verified (no collision)
- [ ] Thai characters display correctly

---

## Complexity Estimate

**Total Time:** 5.5 days

**Breakdown:**
- Phase 1 (DevOps): 1 day
- Phase 2 (Backend): 1.5 days
- Phase 3 (Frontend): 2 days
- Phase 4 (E2E Testing): 1 day

**Risk Level:** Medium

**Risks:**
1. Cache invalidation complexity (HIGH severity, MEDIUM likelihood)
2. Thai character encoding (MEDIUM severity, LOW likelihood)
3. SSR/CSR hydration mismatch (MEDIUM severity, LOW likelihood)
4. Multi-product cache collision (CRITICAL severity, MEDIUM likelihood)

See `risks-and-mitigations.md` for detailed risk analysis.

---

## Dependencies

### External Dependencies
- None (no new packages required)

### Internal Dependencies
- US-020 (Homepage Editable Content) - ✅ COMPLETE
- Foundation: database, API, caching, components all in place

### Technical Debt Introduced
- Minimal: Cache key format change requires coordination with deployment
- Migration strategy allows graceful transition

---

## Success Criteria

**Definition of Done:**
- [ ] All 5 Acceptance Criteria validated by E2E tests
- [ ] Both databases migrated and seeded
- [ ] Both products tested (bestays + realestate)
- [ ] No cache collisions detected
- [ ] Thai content editable by admin/agent roles
- [ ] Fallback logic works for missing translations
- [ ] Code reviewed and approved
- [ ] Documentation updated

**Performance Targets:**
- Locale switching < 100ms
- Cache hit rate > 90% for both locales
- No increase in page load time

**Rollback Plan:**
- Revert frontend deployment (remove [lang] routing)
- Backend continues supporting both cache formats
- Database migration can be rolled back (drop constraint, drop column)
