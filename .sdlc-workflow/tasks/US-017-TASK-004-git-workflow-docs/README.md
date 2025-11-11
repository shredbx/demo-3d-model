# TASK-004: Update GIT_WORKFLOW.md

**Story:** US-017
**Status:** NOT_STARTED  
**Assigned To:** devops-infra subagent
**Estimated Effort:** 1-2 hours
**Priority:** MEDIUM

---

## Objective

Update `.sdlc-workflow/GIT_WORKFLOW.md` to document the correct task-based branch naming convention, replacing the outdated story-based pattern.

---

## Context

GIT_WORKFLOW.md currently documents story-based branching (`feature/US-XXX-description`) which is incorrect. Actual practice uses task-based branching (`{type}/TASK-XXX-US-XXX`). This task updates the documentation to match reality.

**Current (WRONG):** Lines 11-22 show `feature/US-XXX-short-description`
**Should Be:** `{type}/TASK-{number}-US-{story}[-description]`

**Research:** `.claude/reports/20251107-branching-research-findings.md`

---

## What Needs to Be Done

1. **Replace branch naming section** (lines ~11-22)
   - Remove story-based pattern
   - Add task-based pattern with all 6 types
   - Add comprehensive examples
   - Add rationale explaining why task-based

2. **Add validation enforcement section**
   - Document that validation hook exists
   - Explain what happens if wrong pattern used
   - Show how to fix if you create wrong branch

3. **Add cross-references**
   - Link to validation script
   - Link to CLAUDE.md
   - Link to workflow diagrams

4. **Update any other mentions** of branching throughout document

---

## Acceptance Criteria

- [ ] AC-1: Branch naming section updated with correct pattern
- [ ] AC-2: All 6 valid types documented (feat, fix, refactor, test, docs, chore)
- [ ] AC-3: Examples show all valid types
- [ ] AC-4: Rationale section explains why task-based (not story-based)
- [ ] AC-5: Validation enforcement documented
- [ ] AC-6: "How to fix wrong branch" section added
- [ ] AC-7: Cross-references to related docs added
- [ ] AC-8: No contradictory information remains
- [ ] AC-9: Examples are consistent throughout document
- [ ] AC-10: Document reviewed for clarity

---

## Content to Replace

**OLD (lines 11-22):**
```markdown
**Branch Naming:**
- User story work: `feature/US-XXX-short-description`
- Hotfixes: `hotfix/short-description`
- Experiments: `experiment/short-description`

Example:
git checkout -b feature/US-001-login-flow-validation
```

**NEW:**
```markdown
**Branch Naming Convention:**

Pattern: `{type}/TASK-{number}-US-{story}[-description]`

**Valid Types:**
- `feat` - New features
- `fix` - Bug fixes  
- `refactor` - Code improvements without behavior change
- `test` - Test additions or modifications
- `docs` - Documentation changes
- `chore` - Build, tooling, dependencies

**Examples:**
```bash
# Basic pattern
git checkout -b feat/TASK-001-US-001

# With letter suffix on story ID
git checkout -b fix/TASK-042-US-001B

# With optional description
git checkout -b refactor/TASK-005-US-001B-cleanup

# All types valid
git checkout -b test/TASK-010-US-002
git checkout -b docs/TASK-020-US-005
git checkout -b chore/TASK-030-US-010
```

**Rationale:**
- **One branch per task** (not per story) enables parallel work
- **Better traceability** in git history (which task made which changes)
- **Automation-friendly** for CI/CD and scripts
- **Clear completion** (branch deleted when task completes)

**Validation:**
Branch names are automatically validated by `.claude/hooks/pre_tool_use.py`. If you attempt to create a branch with an invalid pattern, you'll see an error with the correct format.

**Fixing Wrong Branch Names:**
If you accidentally create a branch with the wrong name:
```bash
# Rename the branch
git branch -m old-branch-name new-branch-name

# Or create new branch and cherry-pick commits
git checkout -b correct-branch-name
git cherry-pick <commits-from-old-branch>
git branch -D old-branch-name
```
```

---

See `implementation-spec.md` for complete content specifications.

---

**Created:** 2025-11-07
