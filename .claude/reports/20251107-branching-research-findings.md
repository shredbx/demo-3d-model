# Branch Naming Research Findings

**Date:** 2025-11-07
**Issue:** Discrepancy between documented and actual branch naming conventions

---

## Research Summary

### What GIT_WORKFLOW.md Documents (Lines 11-22)
**Story-based naming:**
```
feature/US-XXX-short-description
```

Example:
```bash
git checkout -b feature/US-001-login-flow-validation
```

---

### What SDLC Workflow Plan Documents (`.sdlc-workflow/.plan/03-workflow-diagrams.md`)

**Task-based naming (line 71):**
```
feat/TASK-001-US-001-auth-login-admin
```

**Also referenced in line 421:**
```
git push origin feat/TASK-001-US-001-auth-login-admin
```

**Pattern:** `{type}/TASK-{number}-US-{story}-{description}`

---

### What Is Actually Being Used (From `git branch -a`)

**Actual branches in repository:**
```
feat/TASK-001-US-001
feat/TASK-002-US-001B
feat/TASK-003-US-001B
feat/TASK-004-US-001B
refactor/TASK-005-US-001B
test/TASK-006-US-001B
```

**Pattern:** `{type}/TASK-{number}-US-{story}`

---

## Findings

### 1. GIT_WORKFLOW.md is Outdated/Incorrect
- Documents story-based naming (`feature/US-XXX-description`)
- Does NOT match actual practice
- Does NOT match workflow plan

### 2. Workflow Plan Uses Task-Based Naming
- `.sdlc-workflow/.plan/03-workflow-diagrams.md` shows `feat/TASK-XXX-US-XXX` pattern
- This IS the intended design
- Each task gets its own branch

### 3. Actual Practice Matches Workflow Plan
- All current branches use `{type}/TASK-{number}-US-{story}` pattern
- Type prefixes: `feat`, `refactor`, `test` (not `feature`)
- Task ID comes first, then story ID
- Description is often omitted

### 4. Current Branch `feat/TASK-002-US-001B` is CORRECT
- Follows the actual intended pattern
- Matches all other branches in repo
- NOT a violation of intended workflow

---

## The Real Issue

The issue is **NOT** with our branching practice.

The issue is:
1. ❌ **GIT_WORKFLOW.md documents wrong convention**
2. ❌ **No validation script for branch names** (none exists)
3. ❌ **Pre-tool-use hook is placeholder** (no enforcement)
4. ✅ **Actual practice is correct and consistent**

---

## What Needs to Be Fixed

### 1. Update GIT_WORKFLOW.md
**Current (wrong):**
```markdown
**Branch Naming:**
- User story work: `feature/US-XXX-short-description`
```

**Should be:**
```markdown
**Branch Naming:**
- Task work: `{type}/TASK-{number}-US-{story}`
- Types: feat, fix, refactor, test, docs, chore
- Example: `feat/TASK-001-US-001`
```

### 2. Create Branch Name Validation Script
**File:** `.sdlc-workflow/scripts/validate_branch.py`
- Validate pattern: `{type}/TASK-{number}-US-{story}`
- Valid types: feat, fix, refactor, test, docs, chore
- Block invalid patterns

### 3. Enhance Pre-Tool-Use Hook
**File:** `.claude/hooks/pre_tool_use.py`
- Call `validate_branch.py` before git checkout operations
- Provide clear error messages
- Suggest correct pattern

### 4. Add Git Pre-Checkout Hook (Optional)
**File:** `.git/hooks/pre-checkout` (or template)
- Validate branch name before checkout
- Prevent creating branches with wrong pattern

---

## Recommendation

Create a user story: **SDLC Validation - Branch Naming Enforcement**

Tasks:
1. TASK-001: Update GIT_WORKFLOW.md with correct branch naming convention
2. TASK-002: Create `validate_branch.py` script
3. TASK-003: Enhance `pre_tool_use.py` hook with branch validation
4. TASK-004: Add git pre-checkout hook template (optional)
5. TASK-005: Update CLAUDE.md with branching clarification

Domain: `devops` or `infrastructure`
Type: `refactor` (fixing documentation + validation)
Priority: `medium` (prevents future confusion)

---

## Conclusion

**Current branch `feat/TASK-002-US-001B` is CORRECT.**

The problem is:
- Documentation is outdated (GIT_WORKFLOW.md)
- No validation enforces the correct pattern
- Need to align documentation with actual practice

**Action:** Create user story to fix documentation and add validation.
