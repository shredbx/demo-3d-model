# TASK-005: Update CLAUDE.md and Supporting Docs

**Story:** US-017
**Status:** NOT_STARTED
**Assigned To:** devops-infra subagent
**Estimated Effort:** 1 hour
**Priority:** MEDIUM

---

## Objective

Update CLAUDE.md and supporting documentation to remove contradictory branch naming information and ensure consistency with the task-based pattern.

---

## Files to Update

1. **CLAUDE.md** - Main project documentation
   - Search for "feature/US-" mentions
   - Update all branching examples
   - Ensure consistency with GIT_WORKFLOW.md

2. **.claude/hooks/README.md** - Hook documentation
   - Document pre_tool_use.py now validates branches
   - Explain what happens when validation fails
   - Show example error messages

3. **.sdlc-workflow/scripts/README.md** - Scripts documentation
   - Add section on validate_branch.py
   - Document usage, exit codes
   - Explain how to extend

---

## Acceptance Criteria

- [ ] AC-1: No "feature/US-" pattern in CLAUDE.md
- [ ] AC-2: All examples use task-based pattern
- [ ] AC-3: Hook documentation updated
- [ ] AC-4: Scripts documentation updated
- [ ] AC-5: Consistency across all docs
- [ ] AC-6: Cross-references added

---

See implementation-spec.md for exact changes.

**Created:** 2025-11-07
