# TASK-006: Add Git Pre-Commit Hook Template

**Story:** US-017
**Status:** NOT_STARTED
**Assigned To:** devops-infra subagent
**Estimated Effort:** 1 hour
**Priority:** LOW (Optional)

---

## Objective

Create a git pre-commit hook template that validates branch names, providing native git validation as a complement to Claude's pre-tool-use hook.

---

## Context

**Note:** This is OPTIONAL. Git doesn't have a pre-checkout hook, so we'll use pre-commit which validates on first commit attempt.

**Limitation:** Doesn't prevent branch creation, only catches it on first commit.

**Primary Validation:** Claude's pre-tool-use hook (TASK-003)
**This Hook:** Backup/complement for manual git operations outside Claude

---

## What Needs to Be Done

1. Create hook template at `.git-hooks/pre-commit.template`
2. Hook calls `validate_branch.py`
3. Add installation instructions
4. Document optional nature

---

## Acceptance Criteria

- [ ] AC-1: Template created with validation logic
- [ ] AC-2: Template calls validate_branch.py
- [ ] AC-3: Installation instructions provided
- [ ] AC-4: Documented as optional
- [ ] AC-5: Works for manual git operations

---

See implementation-spec.md.

**Created:** 2025-11-07
