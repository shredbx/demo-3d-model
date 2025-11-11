# Architectural Decisions: US-001-TASK-002

---

## Decision Log

### Decision 1: Create Separate Task for Clerk Selector Fix

**Date:** 2025-11-06
**Context:** TASK-001 identified the Clerk selector issue but grouped it with other fixes
**Decision:** Create dedicated TASK-002 for Clerk selector debugging and fix
**Rationale:**
- Clerk selector issue is distinct and complex (not a simple fix)
- Requires investigation phase (debug DOM structure)
- May involve different solution strategies (iframe vs shadow DOM vs filtering)
- Separate task folder provides clear focus and traceability

**Alternatives Considered:**
- Continue in TASK-001 folder - Rejected (mixed concerns, less clear audit trail)
- Fix manually without task folder - Rejected (violates SDLC workflow)

---

## Pending Decisions

### Question 1: Which Selector Strategy to Use?

**Options:**
- **A. Iframe Locator** - If Clerk uses iframe embedding
- **B. Pierce Selector** - If Clerk uses shadow DOM
- **C. Visible Filter** - If multiple DOM nodes exist (hidden + visible)
- **D. Data Attributes** - If Clerk provides test-specific attributes

**Decision Criteria:**
- Must work reliably across Clerk UI updates
- Must be maintainable by future developers
- Must not use hacky workarounds (like `force: true`)

**To Be Decided By:** playwright-e2e-tester subagent after debugging

---

## Technical Constraints

1. **Cannot modify Clerk configuration** - Using Clerk as-is
2. **Cannot change login page implementation** - App code is correct
3. **Must use standard Playwright APIs** - No custom browser extensions
4. **Test must be deterministic** - No flaky waits or race conditions

---

## Open Questions

- Does Clerk provide official Playwright test utilities?
- Are there Clerk-specific data attributes we should use?
- How stable is Clerk's UI structure across versions?

---

## References

- [Clerk Testing Documentation](https://clerk.com/docs/testing/overview)
- [Playwright Shadow DOM Testing](https://playwright.dev/docs/other-locators#css-locator)
- [Playwright Frames Documentation](https://playwright.dev/docs/frames)
- Previous investigation: US-001-TASK-001 subagent report
