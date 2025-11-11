# Subagent Implementation Directive

**Task:** TASK-017 (US-026 MVP Homepage)
**Subagent:** dev-frontend-svelte
**Phase:** IMPLEMENTATION
**Date:** 2025-11-09

---

## Mission

Implement the MVP homepage for Bestays following the EXACT specifications in the planning document.

**Goal:** Create a functional homepage that resolves the current 404 error at `/[lang]`.

---

## Specifications Location

**READ THIS FIRST:** `/Users/solo/Projects/_repos/bestays/.claude/tasks/TASK-017/planning/implementation-plan.md`

This file contains:
- Complete component code (copy precisely)
- Implementation order (5 components)
- Quality gates checklist
- Testing requirements
- Success criteria

---

## Files to Create (in this exact order)

### 1. Data Loader (15 min)
**File:** `apps/frontend/src/routes/[lang]/+page.ts`
**Code:** Lines 75-106 in implementation-plan.md
**Note:** API returns `{ "properties": [...] }` NOT `{ "items": [...] }`

### 2. Hero Section (30 min)
**File:** `apps/frontend/src/lib/components/HeroSection.svelte`
**Code:** Lines 130-192 in implementation-plan.md
**Note:** Includes slot for SearchBar component

### 3. Search Bar (45 min)
**File:** `apps/frontend/src/lib/components/SearchBar.svelte`
**Code:** Lines 218-349 in implementation-plan.md
**Note:** Navigates to /[lang]/properties with query params

### 4. Property Grid (20 min)
**File:** `apps/frontend/src/lib/components/PropertyGrid.svelte`
**Code:** Lines 373-446 in implementation-plan.md
**Note:** Reuses existing PropertyCard component

### 5. Homepage Layout (20 min)
**File:** `apps/frontend/src/routes/[lang]/+page.svelte`
**Code:** Lines 464-542 in implementation-plan.md
**Note:** Integrates all components + meta tags

---

## Critical Requirements

**Svelte 5 Runes:**
- Use `$props()` for component props
- Use `$state()` for reactive state
- Use `$derived()` for computed values

**SSR Compatibility:**
- No browser-only APIs (window, document)
- Data loading in +page.ts (runs on server)
- No client-side navigation guards

**Styling:**
- Tailwind CSS 4 utilities
- Responsive breakpoints: mobile/tablet/desktop
- Brand colors: `#0a4349`, `#999d70`, red-600

**Localization:**
- All text must be localized (EN/TH)
- Use locale from context or props

**API Response Format:**
```json
{
  "properties": [...]  // NOT "items"
}
```

---

## Implementation Order

**Step 1:** Create `+page.ts` (data loader)
- Copy code exactly from spec
- Test API response: `curl http://localhost:8011/api/v1/properties?limit=8`

**Step 2:** Create `HeroSection.svelte`
- Copy code exactly from spec
- Verify gradient background renders

**Step 3:** Create `SearchBar.svelte`
- Copy code exactly from spec
- Test form state updates
- Test navigation to /properties

**Step 4:** Create `PropertyGrid.svelte`
- Copy code exactly from spec
- Verify PropertyCard import works

**Step 5:** Create `+page.svelte` (homepage layout)
- Copy code exactly from spec
- Integrate all components
- Verify meta tags

**Step 6:** Polish & Test (30 min)
- Check responsive breakpoints
- Verify locale switching
- Test search navigation
- Check SSR rendering (view page source)
- No console errors

---

## Commit Strategy

```bash
# After each major component
git add <file>
git commit -m "feat: add <component> for homepage (US-026 TASK-017)

Subagent: dev-frontend-svelte
Product: bestays
Files: <path>

<Brief description>

Story: US-026
Task: TASK-017

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Success Criteria

**Functional:**
- ✅ Homepage loads at `/en` and `/th` (no 404)
- ✅ Hero displays with localized text
- ✅ Search bar navigates to /properties with query params
- ✅ Property grid displays 8 featured properties
- ✅ All content localized (EN/TH)

**Technical:**
- ✅ SSR renders content (no flicker)
- ✅ Responsive design works
- ✅ Error handling (graceful degradation)
- ✅ Proper meta tags (SEO)
- ✅ No console errors

**Performance:**
- ✅ First Contentful Paint < 1.5s
- ✅ No layout shifts

---

## Implementation Report

**After completion, create:**
`/Users/solo/Projects/_repos/bestays/.claude/tasks/TASK-017/implementation/implementation-report.md`

**Include:**
1. List of files created/modified
2. Any deviations from spec (with justification)
3. Issues encountered and resolutions
4. Screenshots (optional)
5. Testing results
6. Next steps (e.g., E2E testing)

---

## Quality Gates to Pass

From planning-quality-gates skill:

1. **Network Operations:** ✅ API error handling implemented
2. **Frontend SSR/UX:** ✅ SSR-compatible, no client APIs
3. **Testing Requirements:** ⏭️ E2E tests (next phase)
4. **Official Documentation:** ✅ Svelte 5 runes validated
5. **Dependencies:** ✅ PropertyCard component exists

---

## Start Implementation Now

**Command:**
```bash
# Verify branch
git branch --show-current
# Should show: feat/TASK-017-US-026

# Start implementing in order 1 → 2 → 3 → 4 → 5
```

**DO NOT:**
- ❌ Deviate from specifications without justification
- ❌ Skip components or change order
- ❌ Use outdated Svelte patterns (use Svelte 5 runes)
- ❌ Skip error handling
- ❌ Skip localization

**DO:**
- ✅ Copy code exactly as specified
- ✅ Test each component incrementally
- ✅ Commit after each major component
- ✅ Document any issues in implementation report
- ✅ Verify homepage loads successfully at the end

---

**READY TO START:** Begin with Step 1 (create +page.ts)
