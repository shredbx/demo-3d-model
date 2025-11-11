# User Story: US-017 - SDLC Branch Naming Validation

**Status:** READY
**Domain:** infrastructure
**Type:** refactor
**Priority:** medium
**Created:** 2025-11-07
**Estimated Complexity:** Medium (3-4 days)

---

## Story

**As a** developer working on the Bestays project
**I want** clear, validated, and enforced branch naming conventions
**So that** git history is consistent, automation works correctly, and team members understand the workflow

---

## Background

### Why This Is Needed

During US-001B implementation (RBAC + Audit Logging), we discovered a critical discrepancy:
- **GIT_WORKFLOW.md** documents story-based branching (`feature/US-XXX-description`)
- **Actual practice** uses task-based branching (`feat/TASK-XXX-US-XXX`)
- **SDLC workflow plan** (`.sdlc-workflow/.plan/03-workflow-diagrams.md`) specifies task-based branching
- **No validation** exists to enforce any pattern

### Current State

1. ✅ **Actual practice is correct** - All current branches use `{type}/TASK-XXX-US-XXX` pattern
2. ❌ **Documentation is wrong** - GIT_WORKFLOW.md documents incorrect convention
3. ❌ **No validation** - Pre-tool-use hook is placeholder, no branch name validation
4. ❌ **Git hooks missing** - No pre-checkout validation in git hooks
5. ❌ **No automated enforcement** - Easy to create branches with wrong pattern

### What Problems This Solves

- **Confusion:** New developers don't know which pattern to use
- **Inconsistency:** Without validation, wrong patterns can be introduced
- **Automation failure:** Scripts expect specific patterns, wrong names break automation
- **Audit trail:** Inconsistent naming makes it hard to trace work back to tasks/stories
- **CI/CD:** Pipelines may rely on branch naming patterns for routing

### Business Value

- **Reduced onboarding time:** Clear, enforced conventions
- **Better traceability:** Consistent branch names → better git history
- **Automation reliability:** Scripts work predictably
- **Quality gates:** Catch mistakes early (before they reach CI/CD)

---

## Current Implementation

### Research Findings

**See:** `.claude/reports/20251107-branching-research-findings.md` (comprehensive analysis)

#### What GIT_WORKFLOW.md Says (WRONG)

**File:** `.sdlc-workflow/GIT_WORKFLOW.md` (lines 11-22)

```markdown
**Branch Naming:**
- User story work: `feature/US-XXX-short-description`
- Hotfixes: `hotfix/short-description`
- Experiments: `experiment/short-description`
```

Example given: `git checkout -b feature/US-001-login-flow-validation`

#### What SDLC Workflow Plan Says (CORRECT)

**File:** `.sdlc-workflow/.plan/03-workflow-diagrams.md` (line 71)

```
feat/TASK-001-US-001-auth-login-admin
```

Pattern: `{type}/TASK-{number}-US-{story}-{description}`

Also line 421:
```
git push origin feat/TASK-001-US-001-auth-login-admin
```

#### What Is Actually Used (CORRECT)

**From `git branch -a`:**
```
feat/TASK-001-US-001
feat/TASK-002-US-001B
feat/TASK-003-US-001B
feat/TASK-004-US-001B
refactor/TASK-005-US-001B
test/TASK-006-US-001B
```

**Pattern:** `{type}/TASK-{number}-US-{story}`

**Valid types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

### Architecture

```
SDLC Workflow Branching
│
├─ main (production-ready)
│
└─ Task branches (one per task)
    ├─ feat/TASK-001-US-XXX (new features)
    ├─ fix/TASK-002-US-XXX (bug fixes)
    ├─ refactor/TASK-003-US-XXX (code improvements)
    ├─ test/TASK-004-US-XXX (test additions)
    ├─ docs/TASK-005-US-XXX (documentation)
    └─ chore/TASK-006-US-XXX (tooling/build)
```

**Key Design Decisions:**
1. One branch per **task** (not per story)
2. Multiple tasks for same story → multiple branches
3. Task ID comes first (TASK-XXX), story ID second (US-XXX)
4. Description optional (most branches omit it)
5. Type prefix indicates work category

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| `.sdlc-workflow/GIT_WORKFLOW.md` | Git workflow documentation | ❌ Documents wrong pattern |
| `.sdlc-workflow/.plan/03-workflow-diagrams.md` | SDLC workflow design | ✅ Correct pattern |
| `.claude/hooks/pre_tool_use.py` | Pre-tool validation hook | ❌ Placeholder only |
| `.sdlc-workflow/scripts/validate_sdlc.py` | Commit message validation | ✅ Works but doesn't validate branches |
| `.git/hooks/pre-checkout` | Git branch validation | ❌ Doesn't exist |

---

## Identified Issues

### 1. **GIT_WORKFLOW.md Documents Wrong Convention**

**Location:** `.sdlc-workflow/GIT_WORKFLOW.md:11-22`

**Problem:**
Documents story-based naming (`feature/US-XXX-description`) when actual practice and workflow design use task-based naming (`{type}/TASK-XXX-US-XXX`).

**Severity:** High (misleading documentation)

**Impact:**
- New developers follow wrong pattern
- Creates inconsistency
- Contradicts actual workflow design

**Root Cause:**
Documentation written before task-based workflow was fully designed. Never updated to match actual implementation.

### 2. **No Branch Name Validation**

**Location:** `.sdlc-workflow/scripts/` (missing file)

**Problem:**
No script exists to validate branch names follow the correct pattern. Easy to create branches with any name.

**Severity:** High (no enforcement)

**Impact:**
- Can create `feature/US-XXX` (wrong pattern)
- Can create `feat/some-description` (missing task/story IDs)
- No feedback when creating incorrect branches

**Root Cause:**
Validation script was never created. Focus was on commit message validation only.

### 3. **Pre-Tool-Use Hook Is Placeholder**

**Location:** `.claude/hooks/pre_tool_use.py:1-23`

**Problem:**
Hook exists but does nothing - just passes through all tool calls without validation.

```python
def main():
    """Allow all tool use - this is a placeholder hook."""
    sys.exit(0)
```

**Severity:** Medium (infrastructure gap)

**Impact:**
- No pre-validation of git operations
- Can't catch mistakes before they happen
- Hook infrastructure exists but unused

**Root Cause:**
Hook was created as placeholder with intention to add validation later. Never implemented.

### 4. **Git Hooks Not Configured**

**Location:** `.git/hooks/` (missing files)

**Problem:**
No git pre-checkout hook to validate branch names when creating/switching branches.

**Severity:** Low (optional but helpful)

**Impact:**
- No native git validation
- Relies only on Claude hook
- Manual git operations bypass validation

**Root Cause:**
Git hooks are optional in our workflow. Not prioritized.

---

## Acceptance Criteria

### Functional Requirements

- [ ] **AC-1:** GIT_WORKFLOW.md documents correct branch naming pattern (`{type}/TASK-XXX-US-XXX`)
- [ ] **AC-2:** Branch validation script correctly validates all current branches as valid
- [ ] **AC-3:** Branch validation script rejects invalid patterns with clear error messages
- [ ] **AC-4:** Pre-tool-use hook calls branch validation before git checkout operations

### Technical Requirements

- [ ] **AC-5:** Validation script supports all valid types (feat, fix, refactor, test, docs, chore)
- [ ] **AC-6:** Validation script handles edge cases (main branch, hotfix branches if applicable)
- [ ] **AC-7:** Hook provides actionable error messages with correct pattern examples
- [ ] **AC-8:** Validation is fast (<100ms) to avoid slowing down workflow

### Quality Gates

- [ ] **AC-9:** All validation logic has unit tests (>90% coverage)
- [ ] **AC-10:** Integration tests verify hook blocks invalid branch names
- [ ] **AC-11:** Documentation is clear, with examples of valid and invalid patterns
- [ ] **AC-12:** CLAUDE.md updated with clarified branching section

---

## Technical Notes

### Technologies Used

- **Language:** Python 3.10+
- **Framework:** Standard library (no external dependencies)
- **Patterns:** Validation pattern, Hook pattern, Exit code conventions

### Validation Logic

**Valid Pattern:** `^(feat|fix|refactor|test|docs|chore)/TASK-\d+-US-\d+[A-Z]?(-[\w-]+)?$`

**Examples:**
- ✅ `feat/TASK-001-US-001`
- ✅ `fix/TASK-042-US-001B`
- ✅ `refactor/TASK-005-US-001B-cleanup`
- ✅ `test/TASK-010-US-002`
- ✅ `main` (special case)
- ❌ `feature/US-001-description` (wrong pattern from old docs)
- ❌ `feat/some-branch` (missing task/story IDs)
- ❌ `TASK-001` (missing type prefix)

### Integration Points

- **Pre-Tool-Use Hook:** Calls validation before git checkout
- **Commit Validation:** `validate_sdlc.py` already validates commits
- **Session Start Hook:** Could display current branch validity status
- **Git Hooks:** Optional git pre-checkout hook for native validation

---

## Testing Strategy

### Unit Tests

**File:** `tests/test_validate_branch.py`

- [ ] Test valid branch patterns (all types)
- [ ] Test invalid branch patterns (missing parts)
- [ ] Test edge cases (main, special characters)
- [ ] Test error message clarity
- [ ] Test performance (<100ms)

### Integration Tests

**File:** `tests/integration/test_branch_validation_hook.py`

- [ ] Test hook blocks invalid git checkout attempts
- [ ] Test hook allows valid branch names
- [ ] Test error messages appear in Claude interface
- [ ] Test validation works with pre_tool_use.py integration

### E2E Tests

- [ ] Manually test creating branch with wrong name → blocked with error
- [ ] Manually test creating branch with correct name → succeeds
- [ ] Verify all existing branches pass validation
- [ ] Test validation in CI environment

---

## Documentation Requirements

### 1. Updated Git Workflow Documentation

**Location:** `.sdlc-workflow/GIT_WORKFLOW.md`

**Contents:**
- Correct branch naming pattern with examples
- Explanation of task-based vs story-based branching
- Clear examples of valid and invalid patterns
- Rationale for the chosen pattern
- How validation works and how to handle errors

### 2. Validation Script Documentation

**Location:** `.sdlc-workflow/scripts/README.md` (update)

**Contents:**
- Purpose of `validate_branch.py`
- How to run it manually
- Exit codes and their meanings
- Integration with hooks
- How to add new valid branch types

### 3. Hook Documentation

**Location:** `.claude/hooks/README.md` (update)

**Contents:**
- Pre-tool-use hook now validates branches
- How branch validation integrates
- Error messages and how to fix them
- Performance characteristics

### 4. CLAUDE.md Update

**Location:** `CLAUDE.md`

**Contents:**
- Clarify branching section with correct pattern
- Remove contradictory information
- Add reference to validation enforcement
- Update examples throughout

---

## Dependencies

### External Dependencies

None - uses Python standard library only

### Internal Dependencies

- `.claude/hooks/pre_tool_use.py` - Hook infrastructure
- `.sdlc-workflow/scripts/` - Script directory structure
- Git repository - Branch operations

### Blocked By

None - can proceed immediately

### Blocks

- Future automation that relies on consistent branch naming
- CI/CD pipelines that parse branch names
- Git history analysis tools

---

## Tasks Breakdown

This user story will be broken down into tasks:

### TASK-001: Research & Document Current State ✅
**Status:** COMPLETED
**Deliverables:**
- `.claude/reports/20251107-branching-research-findings.md`
- `.claude/reports/20251107-git-branching-audit.md`

### TASK-002: Create Branch Validation Script
**Estimate:** 2-3 hours
**Deliverables:**
- `.sdlc-workflow/scripts/validate_branch.py`
- Unit tests in `tests/test_validate_branch.py`
- Documentation in script header

**Requirements:**
- Validate pattern: `{type}/TASK-{number}-US-{story}`
- Support all valid types
- Clear error messages
- Exit codes: 0 (valid), 1 (invalid)
- Fast (<100ms)

### TASK-003: Enhance Pre-Tool-Use Hook
**Estimate:** 2-3 hours
**Deliverables:**
- Updated `.claude/hooks/pre_tool_use.py`
- Integration tests
- Hook documentation

**Requirements:**
- Call `validate_branch.py` before git checkout
- Parse tool input to detect git operations
- Block with exit code 2 if validation fails
- Provide actionable error messages

### TASK-004: Update GIT_WORKFLOW.md
**Estimate:** 1-2 hours
**Deliverables:**
- Updated `.sdlc-workflow/GIT_WORKFLOW.md`
- Clear examples
- Rationale section

**Requirements:**
- Replace story-based pattern with task-based
- Add examples of all valid types
- Explain why this pattern was chosen
- Document validation enforcement

### TASK-005: Update CLAUDE.md and Supporting Docs
**Estimate:** 1 hour
**Deliverables:**
- Updated `CLAUDE.md`
- Updated `.claude/hooks/README.md`
- Updated `.sdlc-workflow/scripts/README.md`

**Requirements:**
- Remove contradictory branching information
- Add reference to validation
- Clarify branching workflow
- Update examples throughout

### TASK-006: Add Git Pre-Checkout Hook (Optional)
**Estimate:** 1 hour
**Deliverables:**
- `.git/hooks/pre-checkout` template
- Installation instructions

**Requirements:**
- Call `validate_branch.py`
- Works for manual git operations
- Optional installation

---

## Definition of Done

- [ ] All acceptance criteria met and verified
- [ ] All validation logic tested (unit + integration)
- [ ] All existing branches pass validation
- [ ] GIT_WORKFLOW.md updated and reviewed
- [ ] CLAUDE.md updated and consistent
- [ ] Hook documentation updated
- [ ] No performance regressions (<100ms validation)
- [ ] Manual testing completed (create valid/invalid branches)
- [ ] All documentation reviewed for clarity

---

## Notes

### Discovery Context

This story was created after discovering branch naming discrepancy during US-001B (RBAC + Audit Logging) work.

**Timeline:**
1. Working on `feat/TASK-002-US-001B` branch
2. User questioned why we're on TASK-002 branch with TASK-005 work
3. Research revealed GIT_WORKFLOW.md documents wrong pattern
4. Discovered actual practice is correct, documentation is wrong
5. Created this story to fix documentation + add validation

### Why Task-Based Branching?

**Rationale for `{type}/TASK-XXX-US-XXX` pattern:**

1. **One branch per task** - Clear ownership, focused changes
2. **Parallel work** - Multiple tasks on same story can work in parallel
3. **Better traceability** - Git history shows which task made which changes
4. **Automation-friendly** - Scripts can parse task ID from branch name
5. **CI/CD routing** - Branch patterns enable automated testing/deployment
6. **Clear completion** - Branch deleted when task completes, not story

**Why not story-based?**
- Stories can have 5-10 tasks
- Tasks may work in parallel (backend + frontend)
- Story-based = one long-lived branch with many commits
- Task-based = many short-lived branches, easier to review

### Future Improvements

- **Branch lifecycle automation** - Auto-create branches from `/task-new`
- **Branch cleanup** - Auto-delete merged task branches
- **Branch analytics** - Report on branch naming compliance
- **CI integration** - Validate branch names in GitHub Actions

### References

- **Research Report:** `.claude/reports/20251107-branching-research-findings.md`
- **Audit Report:** `.claude/reports/20251107-git-branching-audit.md`
- **Workflow Plan:** `.sdlc-workflow/.plan/03-workflow-diagrams.md` (line 71, 421)
- **Current Workflow:** `.sdlc-workflow/GIT_WORKFLOW.md` (needs update)

---

**Template Version:** 1.0
**Last Updated:** 2025-11-07
**Story ID:** US-017
