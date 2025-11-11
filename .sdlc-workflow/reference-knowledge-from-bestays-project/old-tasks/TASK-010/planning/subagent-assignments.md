# Subagent Assignments: US-021 Thai Localization

**Task:** TASK-010
**Story:** US-021
**Total Estimated Time:** 5.5 days

This document specifies which subagents to use for each phase of implementation, with detailed task assignments and execution order.

---

## Execution Order

```
Phase 1: DevOps (devops-infra) → 1 day
   ↓
Phase 2: Backend (dev-backend-fastapi) → 1.5 days
   ↓
Phase 3: Frontend (dev-frontend-svelte) → 2 days
   ↓
Phase 4: E2E Testing (playwright-e2e-tester) → 1 day
```

**Dependencies:**
- Phase 2 requires Phase 1 complete (database schema must exist)
- Phase 3 requires Phase 2 complete (API must support locale parameter)
- Phase 4 requires Phase 3 complete (frontend must be functional)

---

## Phase 1: DevOps Infrastructure

**Subagent:** `devops-infra`
**Estimated Time:** 1 day
**Branch:** `feat/TASK-010-US-021` (current)

### Tasks

#### Task 1.1: Create Alembic Migration
- **File:** `apps/server/alembic/versions/XXXX_add_locale_to_content_dictionary.py`
- **Requirements:**
  - Add `locale VARCHAR(2)` column (nullable)
  - Backfill `locale = 'en'` for existing rows
  - Set `locale NOT NULL`
  - Drop `UNIQUE(key)` constraint
  - Add `UNIQUE(key, locale)` constraint
  - Create index: `idx_content_dictionary_key_locale`
  - Include upgrade() and downgrade() functions

#### Task 1.2: Apply Migration to bestays_dev
- **Commands:**
  ```bash
  docker exec -it bestays-server-dev alembic upgrade head
  ```
- **Verification:**
  ```bash
  docker exec -it bestays-postgres-dev psql -U bestays_user -d bestays_dev \
    -c "\d content_dictionary"
  ```
- **Expected Output:**
  - Column `locale` exists with type `varchar(2)`
  - Constraint `content_dictionary_key_locale_unique` exists
  - Index `idx_content_dictionary_key_locale` exists

#### Task 1.3: Apply Migration to realestate_dev
- **Commands:** Same as Task 1.2 but for realestate database
- **Verification:** Same checks as Task 1.2

#### Task 1.4: Create Thai Seed Data for Bestays
- **File:** `apps/server/src/server/scripts/seed_thai_content_bestays.py`
- **Requirements:**
  - Define THAI_TRANSLATIONS dictionary with ~15 keys
  - Check for existing translations before inserting
  - Use product-agnostic patterns
  - Include main() function for execution
  - Add error handling and logging

#### Task 1.5: Create Thai Seed Data for Real Estate
- **File:** `apps/server/src/server/scripts/seed_thai_content_realestate.py`
- **Requirements:** Same as Task 1.4 but with real estate-specific translations

#### Task 1.6: Run Seed Scripts
- **Commands:**
  ```bash
  docker exec -it bestays-server-dev python -m server.scripts.seed_thai_content_bestays
  docker exec -it bestays-server-dev python -m server.scripts.seed_thai_content_realestate
  ```
- **Verification:**
  ```sql
  SELECT key, locale, value FROM content_dictionary WHERE locale = 'th' LIMIT 5;
  ```

#### Task 1.7: Update Infrastructure Validation Checklist
- **File:** `.claude/tasks/TASK-010/planning/infrastructure-validation.md`
- **Requirements:**
  - Mark completed migration tasks
  - Document any issues encountered
  - Update smoke test checklist

### Deliverables
- [ ] Migration file created and tested
- [ ] Both databases migrated successfully
- [ ] Thai seed data created for both products
- [ ] Seed scripts executed successfully
- [ ] Infrastructure validation checklist updated

### Success Criteria
- ✅ Both databases have `locale` column with composite UNIQUE constraint
- ✅ Both databases have Thai translations seeded
- ✅ No errors during migration or seeding
- ✅ Rollback tested and working

---

## Phase 2: Backend API

**Subagent:** `dev-backend-fastapi`
**Estimated Time:** 1.5 days
**Dependencies:** Phase 1 complete
**Branch:** `feat/TASK-010-US-021` (continue)

### Tasks

#### Task 2.1: Update SQLAlchemy Model
- **File:** `apps/server/src/server/models/content.py`
- **Requirements:**
  - Add `locale = Column(String(2), nullable=False, default='en')`
  - Update `__table_args__` with composite UniqueConstraint
  - Add Index for (key, locale)
  - Update `__repr__` to include locale

#### Task 2.2: Update Pydantic Schemas
- **File:** `apps/server/src/server/schemas/content.py`
- **Requirements:**
  - Define `Locale = Literal['en', 'th']` type
  - Add `locale: Locale` field to ContentBase
  - Add `locale: Locale` field to ContentUpdate
  - Add validator for locale (must be 'en' or 'th')

#### Task 2.3: Update ContentService
- **File:** `apps/server/src/server/services/content_service.py`
- **Requirements:**
  - Update `get_content()` to accept `locale` parameter
  - Implement fallback logic: (key, locale) → (key, 'en') → 404
  - Update `_get_cache_key()` to include product and locale
  - Update `update_content()` to accept `locale` parameter
  - Invalidate cache only for affected locale
  - Add `PRODUCT_NAME = os.getenv("PRODUCT_NAME", "bestays")`
  - Keep CACHE_TTL and jitter logic

#### Task 2.4: Update API Endpoint
- **File:** `apps/server/src/server/api/v1/endpoints/content.py`
- **Requirements:**
  - Add `locale: Locale = Query('en')` to GET endpoint
  - Add `locale` to PUT endpoint request body
  - Pass locale to service layer functions
  - Update docstrings to mention fallback logic

#### Task 2.5: Write Unit Tests
- **File:** `apps/server/tests/test_content_service.py`
- **Requirements:**
  - Test fallback logic (Thai missing → returns English)
  - Test cache invalidation (only affected locale)
  - Test multi-product isolation (cache keys different)
  - Test locale validation (reject invalid locales)
  - Test composite UNIQUE constraint enforcement
  - Achieve >90% coverage

### Deliverables
- [ ] Updated models, schemas, service, endpoint
- [ ] Unit tests passing with >90% coverage
- [ ] API accepts `?locale=en` and `?locale=th`
- [ ] Fallback logic working as expected
- [ ] Cache keys isolated by product and locale

### Success Criteria
- ✅ GET /api/v1/content/{key}?locale=th returns Thai content
- ✅ GET /api/v1/content/{key}?locale=en returns English content
- ✅ GET /api/v1/content/{key}?locale=th falls back to English if missing
- ✅ PUT /api/v1/content/{key} with locale='th' only invalidates Thai cache
- ✅ All unit tests passing

---

## Phase 3: Frontend Routes & Components

**Subagent:** `dev-frontend-svelte`
**Estimated Time:** 2 days
**Dependencies:** Phase 2 complete
**Branch:** `feat/TASK-010-US-021` (continue)

### Tasks

#### Task 3.1: Create i18n Context
- **Files:**
  - `apps/frontend/src/lib/i18n/context.svelte.ts`
  - `apps/frontend/src/lib/i18n/types.ts`
- **Requirements:**
  - Define `Locale` type ('en' | 'th')
  - Implement `LocaleContext` class with `$state`
  - Export `setLocaleContext()` and `getLocaleContext()`
  - Total ~50 lines across both files
  - Follow Svelte 5 runes patterns

#### Task 3.2: Create Root Redirect
- **File:** `apps/frontend/src/routes/+page.svelte`
- **Requirements:**
  - Redirect to `/en` on mount
  - Use `goto()` with `replaceState: true`
  - Show loading state while redirecting

#### Task 3.3: Create [lang] Layout
- **Files:**
  - `apps/frontend/src/routes/[lang]/+layout.ts`
  - `apps/frontend/src/routes/[lang]/+layout.svelte`
- **Requirements:**
  - Validate `lang` param in +layout.ts
  - Redirect to `/en` if invalid
  - Call `setLocaleContext(data.locale)` in +layout.svelte
  - Include LocaleSwitcher in header

#### Task 3.4: Move Homepage to [lang] Route
- **Files:**
  - Move `apps/frontend/src/routes/+page.svelte` → `apps/frontend/src/routes/[lang]/+page.svelte`
  - Update `apps/frontend/src/routes/[lang]/+page.ts`
- **Requirements:**
  - Get locale from parent layout
  - Pass locale to all content API calls
  - Update SSR load pattern

#### Task 3.5: Create LocaleSwitcher Component
- **File:** `apps/frontend/src/lib/components/LocaleSwitcher.svelte`
- **Requirements:**
  - Display "EN | TH" toggle buttons
  - Get current locale from context
  - Navigate to `/{newLocale}{currentPath}` on click
  - Style active locale (bold or different color)
  - Handle edge cases (preserve query params)

#### Task 3.6: Update EditableText Component
- **File:** `apps/frontend/src/lib/components/ui/EditableText.svelte`
- **Requirements:**
  - Import `getLocaleContext()`
  - Get current locale from context
  - Pass locale to API calls when editing
  - Maintain existing edit functionality

#### Task 3.7: Update Content API Client
- **File:** `apps/frontend/src/lib/api/content.ts`
- **Requirements:**
  - Add `locale` parameter to `getContent()`
  - Add `locale` parameter to `updateContent()`
  - Include locale in query string or request body
  - Handle fallback responses gracefully

#### Task 3.8: Add LocaleSwitcher to Header
- **File:** `apps/frontend/src/routes/[lang]/+layout.svelte`
- **Requirements:**
  - Position in top-right corner
  - Ensure responsive design
  - Accessible (keyboard navigation)

### Deliverables
- [ ] i18n context created (~50 lines)
- [ ] Routes restructured with [lang] parameter
- [ ] LocaleSwitcher component functional
- [ ] EditableText uses locale context
- [ ] Homepage respects current locale
- [ ] All navigation preserves locale

### Success Criteria
- ✅ Visiting `/` redirects to `/en`
- ✅ Clicking "TH" button changes URL to `/th`
- ✅ Thai content displays when on `/th` route
- ✅ English content displays when on `/en` route
- ✅ Editing Thai content only updates Thai version
- ✅ Navigating to `/th/login` (when exists) preserves locale

---

## Phase 4: E2E Testing

**Subagent:** `playwright-e2e-tester`
**Estimated Time:** 1 day
**Dependencies:** Phase 3 complete
**Branch:** `feat/TASK-010-US-021` (continue)

### Tasks

#### Task 4.1: Write Locale Switching Tests
- **File:** `apps/frontend/tests/e2e/locale-switching.spec.ts`
- **Requirements:**
  - Test AC-1: Default locale redirect
  - Test AC-2: Locale switching EN ↔ TH
  - Test AC-5: Locale persistence across navigation
  - Include data-testid selectors
  - Implement test data cleanup

#### Task 4.2: Write Locale Fallback Tests
- **File:** `apps/frontend/tests/e2e/locale-fallback.spec.ts`
- **Requirements:**
  - Test AC-3: Independent locale editing
  - Test AC-4: Fallback for missing translations
  - Test cache invalidation
  - Verify only affected locale cache invalidated

#### Task 4.3: Write Multi-Product Tests
- **File:** `apps/frontend/tests/e2e/multi-product-locale.spec.ts`
- **Requirements:**
  - Test cache isolation between products
  - Test database isolation
  - Verify no cross-product contamination
  - Test on both bestays and realestate

#### Task 4.4: Implement Test Data Cleanup
- **Requirements:**
  - Delete test content keys after each test
  - Clear Redis cache for test keys
  - Use transactions where possible
  - Document cleanup strategy

#### Task 4.5: Run Full Test Suite
- **Requirements:**
  - Run on Chrome, Firefox, Safari
  - Verify all tests pass on bestays
  - Verify all tests pass on realestate (after porting)
  - Generate test coverage report

### Deliverables
- [ ] 3 E2E test files with comprehensive scenarios
- [ ] Test data cleanup implemented
- [ ] All 5 Acceptance Criteria validated
- [ ] Multi-product isolation validated
- [ ] CI/CD integration configured

### Success Criteria
- ✅ All AC tests passing
- ✅ Multi-product tests passing
- ✅ No test data leakage
- ✅ Tests run in CI/CD pipeline
- ✅ Coverage report shows >80% frontend coverage

---

## Commit Strategy

### Commit Pattern

```
<type>: <description> (US-021 TASK-010-<semantic-name>)

Subagent: <which-subagent>
Product: bestays
Files: <comma-separated-list>

<detailed description>

Story: US-021
Task: TASK-010-<semantic-name>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit Sequence

**Phase 1 (DevOps):**
```
feat: add locale column to content_dictionary (US-021 TASK-010-locale-migration)

Subagent: devops-infra
Product: bestays
Files: alembic migration, seed scripts

- Add locale column with composite UNIQUE constraint
- Seed Thai translations for both products
- Apply migration to both databases

Story: US-021
Task: TASK-010-locale-migration
```

**Phase 2 (Backend):**
```
feat: add locale parameter to content API (US-021 TASK-010-backend-locale-api)

Subagent: dev-backend-fastapi
Product: bestays
Files: models, schemas, service, endpoint, tests

- Accept ?locale= query parameter
- Implement fallback logic (Thai → English)
- Update cache key format with product and locale
- Unit tests for fallback and multi-product isolation

Story: US-021
Task: TASK-010-backend-locale-api
```

**Phase 3 (Frontend):**
```
feat: implement [lang] routing and locale switching (US-021 TASK-010-frontend-i18n)

Subagent: dev-frontend-svelte
Product: bestays
Files: i18n context, routes, LocaleSwitcher, EditableText

- Create custom i18n context with Svelte 5 runes
- Restructure routes to /[lang]/ pattern
- Add LocaleSwitcher component for EN|TH toggle
- Update EditableText to use locale context

Story: US-021
Task: TASK-010-frontend-i18n
```

**Phase 4 (E2E Tests):**
```
test: add E2E tests for locale switching (US-021 TASK-010-e2e-locale-tests)

Subagent: playwright-e2e-tester
Product: bestays
Files: locale-switching.spec.ts, locale-fallback.spec.ts, multi-product-locale.spec.ts

- Validate all 5 Acceptance Criteria
- Test multi-product isolation
- Implement test data cleanup

Story: US-021
Task: TASK-010-e2e-locale-tests
```

---

## Communication Between Phases

### Phase 1 → Phase 2
**Handoff Document:** Migration completion report
- Database schema changes applied
- Seed data inserted
- Verification queries run
- Any issues encountered

### Phase 2 → Phase 3
**Handoff Document:** API specification
- Endpoint URLs with locale parameter
- Request/response schemas
- Fallback logic behavior
- Cache key format

### Phase 3 → Phase 4
**Handoff Document:** Frontend implementation notes
- Route structure
- Component hierarchy
- data-testid selectors for testing
- Known edge cases

---

## Summary

**Total Subagents:** 4
**Total Estimated Time:** 5.5 days
**Total Files Changed:** 20 (10 new, 10 modified)

**Subagent Breakdown:**
1. `devops-infra` - 1 day (database migration, seed data)
2. `dev-backend-fastapi` - 1.5 days (API updates, service layer)
3. `dev-frontend-svelte` - 2 days (routes, components, i18n)
4. `playwright-e2e-tester` - 1 day (E2E validation)

**Dependencies Clear:** Each phase builds on the previous, enabling parallel work within phases but sequential execution across phases.
