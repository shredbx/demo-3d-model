# TASK-002: Create Branch Validation Script

**Story:** US-017 - SDLC Branch Naming Validation
**Status:** NOT_STARTED
**Assigned To:** devops-infra subagent
**Estimated Effort:** 2-3 hours
**Priority:** HIGH (blocking TASK-003)

---

## Objective

Create a Python script that validates git branch names follow the task-based naming convention: `{type}/TASK-{number}-US-{story}[-optional-description]`

---

## Context

During US-001B implementation, we discovered that GIT_WORKFLOW.md documents the wrong branching pattern (story-based) while actual practice correctly uses task-based branching. This task creates the validation script that will be used by the pre-tool-use hook to enforce the correct pattern.

**Research Findings:** `.claude/reports/20251107-branching-research-findings.md`

---

## What Needs to Be Done

1. Create validation script at `.sdlc-workflow/scripts/validate_branch.py`
2. Implement regex-based validation for branch names
3. Support all valid branch types (feat, fix, refactor, test, docs, chore)
4. Handle special case (main branch)
5. Provide clear, actionable error messages
6. Implement proper exit codes (0=valid, 1=invalid, 2=error)
7. Ensure performance < 100ms
8. Create comprehensive unit tests

---

## Valid Branch Patterns

**Pattern:** `{type}/TASK-{number}-US-{story}[-optional-description]`

**Valid Types:**
- `feat` - New features
- `fix` - Bug fixes
- `refactor` - Code improvements
- `test` - Test additions
- `docs` - Documentation
- `chore` - Build/tooling

**Examples:**
- ✅ `feat/TASK-001-US-001`
- ✅ `fix/TASK-042-US-001B` (letter suffix on story ID)
- ✅ `refactor/TASK-005-US-001B-cleanup` (optional description)
- ✅ `test/TASK-010-US-002`
- ✅ `main` (special case)
- ❌ `feature/US-001-description` (old pattern - must reject)
- ❌ `feat/some-branch` (missing task/story IDs)
- ❌ `TASK-001` (missing type prefix)

---

## Acceptance Criteria

- [ ] **AC-1:** Script exists at `.sdlc-workflow/scripts/validate_branch.py`
- [ ] **AC-2:** Script validates all 6 branch types (feat, fix, refactor, test, docs, chore)
- [ ] **AC-3:** Script accepts "main" as valid branch
- [ ] **AC-4:** Script rejects old pattern "feature/US-XXX-description"
- [ ] **AC-5:** Script exits with code 0 (valid), 1 (invalid), 2 (error)
- [ ] **AC-6:** Error messages show correct pattern with examples
- [ ] **AC-7:** Performance < 100ms for single validation
- [ ] **AC-8:** Unit tests achieve >90% code coverage
- [ ] **AC-9:** All current branches in repo (6 branches) validate as valid
- [ ] **AC-10:** Script is executable (`chmod +x`)
- [ ] **AC-11:** Script has shebang line (`#!/usr/bin/env python3`)
- [ ] **AC-12:** Error messages identify specific validation failure

---

## Exit Code Specification

```python
EXIT_VALID = 0      # Branch name is valid
EXIT_INVALID = 1    # Branch name violates pattern
EXIT_ERROR = 2      # Script error (git not available, etc.)
```

**Usage:**
```bash
.sdlc-workflow/scripts/validate_branch.py
echo $?  # 0 = valid, 1 = invalid, 2 = error
```

---

## Error Message Requirements

Error messages must be:
1. **Actionable** - Tell user exactly what's wrong
2. **Helpful** - Show correct pattern with examples
3. **Specific** - Identify which part of pattern failed

**Example Error Message:**
```
❌ Branch 'feature/US-001-login' uses old story-based naming.

Expected pattern: {type}/TASK-{number}-US-{story}[-description]

Valid examples:
  feat/TASK-001-US-001
  fix/TASK-042-US-001B
  refactor/TASK-005-US-001B-cleanup

Valid types: feat, fix, refactor, test, docs, chore
```

---

## Technical Constraints

- **Language:** Python 3.10+
- **Dependencies:** Standard library only (no external packages)
- **Performance:** < 100ms execution time
- **Compatibility:** Must work on macOS, Linux
- **Testing:** pytest for unit tests

---

## Implementation Details

See `implementation-spec.md` for detailed technical specification.

---

## Test Strategy

See `test-strategy.md` for comprehensive test plan.

---

## Dependencies

**Requires:**
- Python 3.10+ (already available)
- Git (already available)
- pytest (for testing)

**Blocks:**
- TASK-003 (hook enhancement needs this script)
- TASK-006 (git hook template needs this script)

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Unit tests passing with >90% coverage
- [ ] All current branches validate successfully
- [ ] Script is executable and has proper shebang
- [ ] Performance benchmark shows < 100ms
- [ ] Documentation complete (docstrings, comments)
- [ ] Code reviewed by coordinator
- [ ] Subagent report saved to task folder

---

## Files to Create/Modify

**New Files:**
- `.sdlc-workflow/scripts/validate_branch.py` (main script)
- `tests/test_validate_branch.py` (unit tests)

**Modified Files:**
- None (this task only creates new files)

---

## Related Documentation

- Research: `.claude/reports/20251107-branching-research-findings.md`
- Story: `.sdlc-workflow/stories/infrastructure/US-017-infrastructure-sdlc-branch-naming-validation.md`
- Workflow Plan: `.sdlc-workflow/.plan/03-workflow-diagrams.md`

---

**Created:** 2025-11-07
**Last Updated:** 2025-11-07
