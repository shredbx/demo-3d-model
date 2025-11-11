# Planning Phase Summary: TASK-010 (US-021)

**Story:** US-021 - Thai Localization & Locale Switching
**Task:** TASK-010
**Date:** 2025-11-08
**Planning Time:** 2.5 hours

---

## Architecture Decisions

### 1. [lang] Parameter Routing ✅
**Decision:** Use SvelteKit's native `[lang]` parameter routing
**Rationale:** SSR-friendly, SEO-friendly, no external dependencies, validated against Svelte MCP official docs
**Alternative Rejected:** External i18n libraries (svelte-i18n, paraglide) - too heavy for simple EN/TH switching

### 2. Custom Svelte 5 Context (~50 lines) ✅
**Decision:** Build custom i18n context using runes and context API
**Rationale:** Minimal bundle size, type-safe, follows official Svelte 5 patterns
**Implementation:** `LocaleContext` class with `$state` rune

### 3. Cache Key Format Change ✅
**Old:** `content:{key}`
**New:** `content:{product}:{locale}:{key}`
**Rationale:** Prevents multi-product collision (lesson from US-020), isolates locale-specific content
**Migration:** Backend supports both formats during transition

### 4. Phased Database Migration (Zero Downtime) ✅
**Approach:** Add nullable → Backfill → Set NOT NULL → Add composite UNIQUE constraint
**Rationale:** Safe, rollback-friendly, existing API calls continue working

### 5. Fallback Logic (AC-4) ✅
**Behavior:** Try (key, locale) → Try (key, 'en') → 404
**Rationale:** Graceful degradation, allows incremental Thai translation rollout

---

## Quality Gates Status

| Gate | Status | Notes |
|------|--------|-------|
| #1: Network Operations | ✅ PASS | Retry logic, error handling, offline detection in place |
| #2: Frontend SSR/UX | ✅ PASS | SSR-compatible, no hydration mismatch, locale server-side |
| #3: Testing Requirements | ✅ PASS | Comprehensive E2E + unit tests, all ACs covered |
| #4: Deployment Safety | ✅ PASS | Zero downtime migration, clear rollback plan |
| #5: Acceptance Criteria | ✅ PASS | All 5 ACs mapped to implementation and tests |
| #6: Dependencies | ✅ PASS | No external deps, US-020 complete |
| #7: Official Documentation | ✅ PASS | All patterns validated against Svelte MCP, PostgreSQL, FastAPI docs |
| #8: Multi-Product Validation | ✅ PASS | Shared infrastructure, clear porting strategy, cache isolation |

**Overall Verdict:** ✅ READY FOR IMPLEMENTATION

---

## Implementation Complexity

**Estimated Time:** 5.5 days

**Breakdown:**
- Phase 1: DevOps (devops-infra) - 1 day
  - Database migration, seed data, infrastructure validation
  
- Phase 2: Backend (dev-backend-fastapi) - 1.5 days
  - Models, schemas, service layer, API endpoint, unit tests
  
- Phase 3: Frontend (dev-frontend-svelte) - 2 days
  - i18n context, route restructure, LocaleSwitcher, component updates
  
- Phase 4: E2E Testing (playwright-e2e-tester) - 1 day
  - All ACs validated, multi-product isolation tests

**Risk Level:** MEDIUM

**Critical Risks Mitigated:**
1. Cache invalidation complexity - Comprehensive unit tests, clear cache key pattern
2. Multi-product cache collision - Cache keys include product identifier
3. Thai character encoding - PostgreSQL UTF-8 verified, Thai in seed data
4. SSR hydration mismatch - Locale determined server-side

---

## Files to Modify/Create

**Total:** 20 files (10 new, 10 modified)

### New Files (10)

**Backend (3):**
1. `apps/server/alembic/versions/XXXX_add_locale_to_content_dictionary.py`
2. `apps/server/src/server/scripts/seed_thai_content_bestays.py`
3. `apps/server/src/server/scripts/seed_thai_content_realestate.py`

**Frontend (4):**
4. `apps/frontend/src/lib/i18n/context.svelte.ts`
5. `apps/frontend/src/lib/i18n/types.ts`
6. `apps/frontend/src/routes/[lang]/+layout.svelte`
7. `apps/frontend/src/routes/[lang]/+layout.ts`
8. `apps/frontend/src/lib/components/LocaleSwitcher.svelte`

**E2E Tests (3):**
9. `apps/frontend/tests/e2e/locale-switching.spec.ts`
10. `apps/frontend/tests/e2e/locale-fallback.spec.ts`
11. `apps/frontend/tests/e2e/multi-product-locale.spec.ts`

### Modified Files (10)

**Backend (5):**
1. `apps/server/src/server/models/content.py`
2. `apps/server/src/server/services/content_service.py`
3. `apps/server/src/server/api/v1/endpoints/content.py`
4. `apps/server/src/server/schemas/content.py`
5. `apps/server/tests/test_content_service.py`

**Frontend (5):**
6. `apps/frontend/src/routes/+page.svelte`
7. `apps/frontend/src/routes/[lang]/+page.svelte` (moved from routes/+page.svelte)
8. `apps/frontend/src/routes/[lang]/+page.ts`
9. `apps/frontend/src/lib/components/ui/EditableText.svelte`
10. `apps/frontend/src/lib/api/content.ts`

---

## Subagents Required

### Phase 1: devops-infra (1 day)
**Tasks:**
- Create Alembic migration
- Apply migration to both databases (bestays_dev, realestate_dev)
- Create Thai seed data for both products
- Run seed scripts
- Update infrastructure validation checklist

**Deliverables:**
- Migration applied successfully
- Thai content seeded for both products
- Infrastructure validation complete

---

### Phase 2: dev-backend-fastapi (1.5 days)
**Tasks:**
- Update SQLAlchemy model (add locale field)
- Update Pydantic schemas (add locale validation)
- Update ContentService (locale param, fallback logic, cache keys)
- Update API endpoint (query parameter)
- Write unit tests (>90% coverage)

**Deliverables:**
- API accepts `?locale=en` and `?locale=th`
- Fallback logic working
- Cache keys isolated by product and locale
- Unit tests passing

---

### Phase 3: dev-frontend-svelte (2 days)
**Tasks:**
- Create i18n context (~50 lines)
- Restructure routes to `/[lang]/` pattern
- Create LocaleSwitcher component
- Update EditableText to use locale context
- Update content API client
- Add LocaleSwitcher to header

**Deliverables:**
- Default locale redirect works (AC-1)
- Locale switching works (AC-2)
- Locale persistence works (AC-5)
- All navigation preserves locale

---

### Phase 4: playwright-e2e-tester (1 day)
**Tasks:**
- Write locale switching tests (AC-1, AC-2, AC-5)
- Write locale fallback tests (AC-3, AC-4)
- Write multi-product isolation tests
- Implement test data cleanup
- Run full test suite on both products

**Deliverables:**
- All 5 ACs validated
- Multi-product isolation confirmed
- Test suite passing on Chrome, Firefox, Safari

---

## Multi-Product Strategy

**Approach:** Build for **bestays** first, then port to **realestate** via porting task.

### Products Affected
1. **bestays** - Primary implementation (TASK-010)
2. **realestate** - Porting task (TASK-011, to be created)

### Shared Infrastructure
- ✅ Database schema (both databases)
- ✅ Backend API (locale parameter)
- ✅ Cache key pattern (`content:{product}:{locale}:{key}`)
- ✅ Frontend routing pattern ([lang] parameter)
- ✅ i18n context (Svelte 5 runes)

### Product-Specific Elements
- ⚠️ Content values (different Thai translations)
- ⚠️ Redirect URLs (bestays.app vs realestate domain)
- ⚠️ Branding (logos, colors)
- ⚠️ Seed data (different keys)

### Blast Radius
**MEDIUM** - Shared database schema changes, both products need frontend restructure

### Smoke Tests Required
- ✅ Bestays: EN/TH routes, locale switching, cache isolation
- ✅ Real Estate: EN/TH routes, locale switching, cache isolation
- ✅ Cross-product: No cache collision, database isolation

---

## Planning Artifacts Created

1. ✅ `implementation-plan.md` - Comprehensive implementation guide (5.5 days)
2. ✅ `quality-gates-analysis.md` - All 8 gates analyzed and passed
3. ✅ `architecture-spec.md` - Database, backend, frontend specs with code samples
4. ✅ `subagent-assignments.md` - Detailed task assignments for 4 subagents
5. ✅ `infrastructure-validation.md` - Multi-product checklist with verification commands
6. ✅ `multi-product-test-plan.md` - Comprehensive test matrix for both products
7. ✅ `risks-and-mitigations.md` - 6 risks with mitigations and contingency plans

**Total Planning Docs:** 7 comprehensive documents

---

## Ready for Implementation

### ✅ YES - All prerequisites met

**Checklist:**
- [x] All 8 quality gates pass
- [x] Architecture designed and documented
- [x] Risks identified and mitigated
- [x] Subagents assigned with clear tasks
- [x] File changes documented (20 files)
- [x] Multi-product strategy defined
- [x] Test coverage planned (>90% backend, all ACs frontend)
- [x] Deployment strategy documented (zero downtime)
- [x] Rollback procedures defined

---

## Next Steps

### 1. User Review and Approval
- Review planning artifacts
- Approve architecture decisions
- Confirm risk mitigations acceptable
- Confirm 5.5 day estimate acceptable

### 2. Phase 1: DevOps (devops-infra)
**Command to spawn:**
```bash
# Spawn devops-infra subagent
# Task: Database migration and seed data
```

**What to provide:**
- `planning/implementation-plan.md` (Phase 1 section)
- `planning/architecture-spec.md` (Database Schema section)
- `planning/infrastructure-validation.md` (Migration validation checklist)

### 3. Sequential Execution
- Phase 1 → Phase 2 → Phase 3 → Phase 4
- Each phase validates previous phase complete before starting

### 4. Porting Task (After TASK-010 complete)
- Create TASK-011: Port Thai localization to realestate
- Use porting checklist from multi-product workflow
- Adapt product-specific elements (content, branding, redirects)

---

## Key Success Metrics

**Technical:**
- ✅ All 5 Acceptance Criteria validated
- ✅ Cache hit rate >90%
- ✅ API response time <100ms (cached)
- ✅ Unit test coverage >90%
- ✅ E2E tests pass on 3 browsers
- ✅ No cache collisions between products

**Business:**
- ✅ Thai users can switch language
- ✅ Thai content editable by admin/agent
- ✅ Graceful fallback for missing translations
- ✅ Zero downtime deployment
- ✅ Both products functional after deployment

---

## Estimated Timeline

**Start Date:** TBD
**End Date:** TBD (Start + 5.5 days)

**Milestones:**
- Day 1: Database migration complete (Phase 1)
- Day 2.5: Backend API complete (Phase 2)
- Day 4.5: Frontend complete (Phase 3)
- Day 5.5: E2E tests complete (Phase 4)

**Final Deliverable:** Thai localization working on bestays, ready to port to realestate

---

## Questions for User

1. **Timeline Approval:** Is 5.5 days acceptable for this feature?
2. **Risk Acceptance:** Are the identified risks and mitigations acceptable?
3. **Multi-Product Strategy:** Approve building for bestays first, then porting to realestate?
4. **Proceed to Implementation:** Ready to spawn devops-infra subagent for Phase 1?

---

**Planning Complete:** ✅
**Quality Gates:** 8/8 PASS
**Ready for Implementation:** YES
**Waiting for:** User approval to proceed
