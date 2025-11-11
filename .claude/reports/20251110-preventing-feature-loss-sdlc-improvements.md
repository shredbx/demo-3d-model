# Preventing Feature Loss: SDLC Improvements

**Date:** 2025-11-10
**Issue:** Editable homepage content (US-020) silently lost during homepage refactor (US-026)
**Impact:** Critical feature removed without documentation or awareness
**Status:** ⚠️ CRITICAL - Requires immediate SDLC process changes

---

## 🔍 Root Cause Analysis

### What Happened

**Timeline of Events:**

1. **US-020 (Nov 8, 2025)** - `feat: add data-testid attributes to editable content components`
   - Commit: `0c3d79f`
   - Created `EditableText.svelte` component
   - Integrated right-click context menu for admin/agent content editing
   - Added E2E tests: `tests/e2e/homepage-editable-content.spec.ts`
   - Homepage at `/[lang]/+page.svelte` **WITH** editable title & description

2. **US-021 (Nov 8-9, 2025)** - `feat: add locale routing and i18n context`
   - Commit: `4d03d6e` → `fd4bc2c`
   - Homepage moved to `/[lang]/+page.svelte`
   - **Editable content preserved** and working with locale support
   - E2E tests still passing

3. **US-026 (Nov 10, 2025)** - `feat: implement MVP homepage with hero, search, and property grid`
   - Commit: `c6265bc`
   - Homepage **COMPLETELY REPLACED** with new implementation
   - ❌ `EditableText` component removed
   - ❌ Content API integration removed
   - ❌ E2E tests still pass but test **nothing** (component doesn't exist!)
   - ❌ No documentation of feature removal
   - ❌ No warning to stakeholders

### The Problem

**US-026 performed a "clean slate" refactor without:**
1. Checking existing features in the file being replaced
2. Validating acceptance criteria from previous stories
3. Running cross-story dependency analysis
4. Updating or marking E2E tests as obsolete

**Result:** Feature loss went undetected because:
- Tests passed (but tested nothing)
- No acceptance criteria in file headers to validate against
- No "feature checklist" to verify preservation
- SDLC process had no "refactor safety checklist"

---

## 💡 Why This Happened

### Gap 1: No Acceptance Criteria in File Headers

**Current state:**
```svelte
<!--
Homepage - Bestays rental property homepage

ARCHITECTURE:
  Layer: Page Route
  Pattern: SvelteKit page with SSR data loading

SPEC: US-026 MVP Homepage
-->
```

**Missing:**
- ✅ What features MUST exist in this file
- ✅ What user interactions should work
- ✅ What acceptance criteria must pass

### Gap 2: No Test Guards for Component Existence

**Current E2E test:**
```typescript
test('should show edit context menu on right-click', async ({ page }) => {
  await page.goto('/en');
  await page.locator('[data-testid="editable-content-homepage.title"]').click({ button: 'right' });
  // ...
});
```

**Problem:** If component doesn't exist, test **fails silently** instead of warning about missing critical functionality.

### Gap 3: No Pre-Refactor Validation Checklist

**What should have happened before US-026:**
1. ✅ Read all `SPEC:` references in file header
2. ✅ Find all related stories (US-020, US-021)
3. ✅ Extract acceptance criteria from those stories
4. ✅ Verify new implementation preserves or explicitly removes features
5. ✅ Document any removed features with justification

### Gap 4: No Component Registry

**No way to answer:**
- "What features exist on the homepage?"
- "What stories contributed to this file?"
- "What acceptance criteria must this file satisfy?"

---

## 🛠️ SDLC Improvements (Required)

### 1. File Header Enhancement - Acceptance Criteria Section

**NEW REQUIRED FORMAT:**

```svelte
<!--
Homepage - Bestays rental property homepage

ARCHITECTURE:
  Layer: Page Route
  Pattern: SvelteKit page with SSR data loading

DEPENDENCIES:
  Internal: HeroSection, SearchBar, PropertyGrid, EditableText, i18n/context

ACCEPTANCE CRITERIA: (DO NOT REMOVE WITHOUT EXPLICIT USER APPROVAL)
  ✅ Hero section with search bar
  ✅ Property grid showing featured properties
  ✅ Admin/agent can right-click title to edit (US-020)
  ✅ Admin/agent can right-click description to edit (US-020)
  ✅ Content edits saved to database via API (US-020)
  ✅ Locale switcher changes content without refresh (US-021)
  ✅ SSR-compatible (no hydration mismatches) (US-021)

SPECS:
  - US-020: Homepage Editable Content
  - US-021: Thai Localization
  - US-026: MVP Homepage with Property Grid

VALIDATION:
  - E2E: tests/e2e/homepage-editable-content.spec.ts
  - E2E: tests/e2e/homepage-property-grid.spec.ts

NOTES:
  - SSR renders with initial 8 properties
  - Fully responsive layout
  - Localized content throughout
-->
```

**Key Addition:** `ACCEPTANCE CRITERIA` section that:
- Lists all "MUST HAVE" features
- References originating user story
- Requires explicit approval to remove
- Acts as validation checklist

### 2. Component-Level Acceptance Criteria

**Every component header must include:**

```svelte
<!--
EditableText Component - Right-click context menu for admin/agent content editing

ACCEPTANCE CRITERIA:
  ✅ Shows context menu on right-click for admin/agent only
  ✅ Regular users see no context menu
  ✅ Edit dialog opens with current content value
  ✅ Saves changes to API: PUT /api/v1/content/{contentKey}?locale={locale}
  ✅ Optimistic UI update (immediate, rolls back on error)
  ✅ Error toast shown on save failure
  ✅ Locale-aware (saves to correct language)

VALIDATION:
  - data-testid: "editable-content-{contentKey}"
  - E2E: tests/e2e/homepage-editable-content.spec.ts

SPEC: US-020 Homepage Editable Content
-->
```

### 3. E2E Test Enhancements - Existence Guards

**BEFORE:**
```typescript
test('should show edit context menu on right-click', async ({ page }) => {
  await page.goto('/en');
  await page.locator('[data-testid="editable-content-homepage.title"]').click({ button: 'right' });
  // Test passes if component exists, fails silently if it doesn't
});
```

**AFTER:**
```typescript
test('CRITICAL: editable content component must exist', async ({ page }) => {
  await page.goto('/en');

  // GUARD: Component existence check
  const editableTitle = page.locator('[data-testid="editable-content-homepage.title"]');
  await expect(editableTitle).toBeVisible({
    timeout: 5000,
    // CRITICAL: This test ensures US-020 feature still exists
    // If this fails, editable content was removed during refactor
    // See: US-020 Homepage Editable Content acceptance criteria
  });

  // Test functionality only if component exists
  await editableTitle.click({ button: 'right' });
  // ...
});

test('ACCEPTANCE: admin can edit homepage title (US-020)', async ({ page }) => {
  // Full flow validation against acceptance criteria
  // ...
});
```

**Key Changes:**
- Separate "existence guard" test
- Clear error messages referencing story
- Links to acceptance criteria
- Fails loudly with context if component missing

### 4. Pre-Refactor Checklist (Mandatory for Coordinators)

**Before ANY file refactor/replacement, coordinators MUST:**

```markdown
## Pre-Refactor Safety Checklist

**File:** `apps/frontend/src/routes/[lang]/+page.svelte`
**Story:** US-026 MVP Homepage

### Step 1: Identify Existing Features
- [ ] Read file header `ACCEPTANCE CRITERIA` section
- [ ] Read file header `SPECS` section (list all stories)
- [ ] Run: `git log --oneline -- <file_path>` (find all commits)
- [ ] List all features referenced in acceptance criteria

### Step 2: Cross-Reference Stories
For each story found:
- [ ] Read story acceptance criteria
- [ ] Read story definition of done
- [ ] Extract "MUST HAVE" features

### Step 3: Feature Preservation Decision
For each existing feature:
- [ ] ✅ Preserve: Include in new implementation
- [ ] ❌ Remove: Requires explicit user approval + documentation
- [ ] 🔄 Defer: Move to new story (document in story metadata)

### Step 4: Implementation Validation
After implementation:
- [ ] Validate ALL acceptance criteria still pass
- [ ] Run E2E tests: `npm run test:e2e -- <test_file>`
- [ ] Update file header with new acceptance criteria
- [ ] Document any removed features in commit message

### Step 5: Stakeholder Communication
If ANY feature removed:
- [ ] Create removal justification document
- [ ] Get explicit user approval
- [ ] Update affected E2E tests (mark as obsolete or update)
- [ ] Create follow-up story if deferred
```

**Enforcement:** Coordinator hook (`sdlc_guardian.py`) should require this checklist for file rewrites.

### 5. Planning Phase Enhancement

**Quality Gate Addition:**

```markdown
## Quality Gate 8: Feature Preservation Analysis

**Required for:** All tasks that modify existing files

**Checklist:**
1. [ ] List all files to be modified
2. [ ] For each file:
   - [ ] Extract `ACCEPTANCE CRITERIA` from header
   - [ ] Extract `SPECS` references
   - [ ] Read referenced stories
3. [ ] Decision matrix:
   - [ ] Which features MUST be preserved?
   - [ ] Which features can be removed? (justification required)
   - [ ] Which features will be enhanced?
4. [ ] Test validation plan:
   - [ ] Which E2E tests must still pass?
   - [ ] Which tests need updates?
   - [ ] Which tests should be marked obsolete?

**Output:** Feature preservation plan in `planning/feature-preservation.md`
```

### 6. Test Coverage Enhancement

**Requirement:** Every page component MUST have:

1. **Existence tests** for all critical features
2. **Acceptance criteria tests** for all user stories
3. **Regression tests** for all bug fixes

**Example test structure:**

```typescript
// tests/e2e/homepage.spec.ts

test.describe('Homepage Critical Features (Existence Guards)', () => {
  test('US-020: Editable content components exist', async ({ page }) => {
    await page.goto('/en');
    await expect(page.locator('[data-testid="editable-content-homepage.title"]')).toBeVisible();
    await expect(page.locator('[data-testid="editable-content-homepage.description"]')).toBeVisible();
  });

  test('US-026: Property grid exists', async ({ page }) => {
    await page.goto('/en');
    await expect(page.locator('[data-testid="property-grid"]')).toBeVisible();
  });
});

test.describe('Homepage Acceptance Criteria (US-020)', () => {
  test('AC1: Admin can right-click title to edit', async ({ page }) => {
    // Full acceptance criteria validation
  });

  test('AC2: Changes saved to database', async ({ page }) => {
    // Full acceptance criteria validation
  });
});
```

### 7. SDLC Process Updates

**New mandatory documents in task folders:**

```
.claude/tasks/TASK-XXX/
├── planning/
│   ├── feature-preservation.md  (NEW - for refactor tasks)
│   └── acceptance-criteria-mapping.md  (NEW - maps ACs to tests)
```

**`feature-preservation.md` template:**

```markdown
# Feature Preservation Analysis

**Story:** US-XXX
**Task:** TASK-XXX
**Type:** Refactor | Enhancement | New Feature

## Files to be Modified

### File: `apps/frontend/src/routes/[lang]/+page.svelte`

**Current Features (from file header):**
- ✅ Editable title (US-020)
- ✅ Editable description (US-020)
- ✅ Locale switcher (US-021)

**Decision Matrix:**
| Feature | Action | Justification | Approval |
|---------|--------|---------------|----------|
| Editable title | ❌ REMOVE | Not in MVP scope, defer to Phase 2 | ✅ User approved 2025-11-10 |
| Editable description | ❌ REMOVE | Not in MVP scope, defer to Phase 2 | ✅ User approved 2025-11-10 |
| Locale switcher | ✅ PRESERVE | Required for i18n | N/A |
| Property grid | ✅ ADD | New MVP feature | N/A |

**Follow-up Stories:**
- US-XXX: Re-implement editable homepage content (deferred to Phase 2)

**Test Updates:**
- `tests/e2e/homepage-editable-content.spec.ts` - Mark as `.skip` with comment
- `tests/e2e/homepage-property-grid.spec.ts` - New test file
```

---

## 📊 Impact Assessment

### Current Damage

**Lost Feature:**
- US-020: Homepage editable content
- 2 components deleted: `EditableText.svelte`, `EditContentDialog.svelte`
- 1 E2E test file obsolete: `homepage-editable-content.spec.ts`
- Backend API still exists but unused: `GET/PUT /api/v1/content/{key}`

**Detection Time:**
- Feature loss: **2 days** (Nov 10, detected by user)
- Test false positive: **Ongoing** (tests pass but don't validate feature)

### Potential Future Damage (Without Fixes)

**Risk Level: HIGH**

If SDLC improvements not implemented:
- Feature loss will happen again on next major refactor
- Test coverage will degrade without detection
- User stories will become "documentation only" (ignored during implementation)
- Technical debt will accumulate silently

---

## ✅ Implementation Roadmap

### Phase 1: Immediate (This Session)

- [x] Document root cause and SDLC gaps
- [ ] Create `.sdlc-workflow/guides/acceptance-criteria-headers.md` guide
- [ ] Create `.sdlc-workflow/guides/pre-refactor-checklist.md` template
- [ ] Update CLAUDE.md with new requirements

### Phase 2: Next Story

- [ ] Implement coordinator hook enhancement (block refactors without checklist)
- [ ] Create acceptance criteria header validator script
- [ ] Update all existing page/component headers with acceptance criteria

### Phase 3: Ongoing

- [ ] Every new file MUST include acceptance criteria in header
- [ ] Every refactor task MUST complete pre-refactor checklist
- [ ] Every E2E test MUST have existence guards
- [ ] Monthly audit: Validate all headers match current functionality

---

## 🎯 Success Metrics

**SDLC improvements successful if:**

1. **Zero feature loss** in next 10 user stories
2. **100% of files** have acceptance criteria in headers within 30 days
3. **All E2E tests** have existence guards within 30 days
4. **Pre-refactor checklists** completed for 100% of refactor tasks

**Tracking:**
- Add to `.sdlc-workflow/.plan/progress.md`
- Monthly review in coordinator reports

---

## 📝 Lessons Learned

### What Went Wrong

1. **Trust without verification:** Assumed new implementation included all features
2. **Test false positives:** Tests passed but validated nothing
3. **No feature registry:** No way to know what existed before
4. **Documentation disconnect:** User stories not referenced during refactors

### What We'll Do Differently

1. **Explicit is better than implicit:** Acceptance criteria MUST be in file headers
2. **Test for existence first:** E2E tests MUST verify component exists before testing behavior
3. **Preserve or document:** Features can only be removed with approval and documentation
4. **Cross-reference everything:** Always check related stories before refactoring

---

## 🔗 References

**Related Documents:**
- `.sdlc-workflow/guides/memory-print.md` - Memory print chain concept
- `.sdlc-workflow/tasks/README.md` - Task folder system
- `.claude/skills/planning-quality-gates/` - Current quality gates (needs Gate 8)

**Related Stories:**
- US-020: Homepage Editable Content (lost feature)
- US-021: Thai Localization (preserved)
- US-026: MVP Homepage (refactor that caused loss)

**Related Commits:**
- `0c3d79f`: feat: add data-testid attributes to editable content components
- `c6265bc`: feat: implement MVP homepage with hero, search, and property grid

---

**Next Actions:**
1. Create guide documents (Phase 1)
2. Update CLAUDE.md with new requirements
3. Decide: Restore US-020 feature OR formally defer with user approval
