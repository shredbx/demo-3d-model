# Git Branching Audit - How We Missed the Branch Naming Issue

**Date:** 2025-11-07
**Issue:** Working on `feat/TASK-002-US-001B` branch with multiple tasks committed

---

## The Problem

### Current State
- **Branch:** `feat/TASK-002-US-001B` (named after TASK-002)
- **Commits on this branch:**
  - TASK-002: Database migrations
  - TASK-003: RBAC components
  - TASK-004: Audit logging system
  - TASK-005: E2E tests for audit logging

### Expected State (per GIT_WORKFLOW.md)
- **Branch should be:** `feature/US-001B-rbac-and-audit-logging` (named after user story)
- **Commits:** Multiple tasks on same story branch is **ALLOWED** ✅

---

## What Went Wrong

### 1. Branch Naming Convention Violated

**From `.sdlc-workflow/GIT_WORKFLOW.md` lines 11-22:**
```markdown
**Branch Naming:**
- User story work: `feature/US-XXX-short-description`
- Hotfixes: `hotfix/short-description`
- Experiments: `experiment/short-description`
```

**Violation:**
- ❌ Current: `feat/TASK-002-US-001B` (task-based naming)
- ✅ Should be: `feature/US-001B-rbac-and-audit-logging` (story-based naming)

### 2. No Validation Caught This

**File: `.claude/hooks/pre_tool_use.py`** (lines 1-23)
```python
"""
Pre-tool-use hook - runs before any tool execution

This is a pass-through hook that allows all tools to execute.
Currently serves as a placeholder for future tool-use monitoring.
"""

def main():
    """Allow all tool use - this is a placeholder hook."""
    # Could add monitoring/logging here in the future
    # For now, just pass through all tool calls
    sys.exit(0)
```

**Status:** 🚨 **Placeholder only - no validation**

**File: `.sdlc-workflow/scripts/validate_sdlc.py`**
- ✅ Validates commit messages (task reference, subagent marker)
- ✅ Validates coordinator vs implementer file modifications
- ❌ Does NOT validate branch names

**Git Pre-Commit Hook:**
- ❌ Not set up (optional per GIT_WORKFLOW.md line 280-293)

---

## Why Multiple Tasks on Same Branch is OK

**From `.sdlc-workflow/GIT_WORKFLOW.md` line 16:**
> One feature branch per user story

**From TASK-005 README line 7:**
```markdown
**Branch:** feat/TASK-002-US-001B (shared)
```

**Explicitly marked as "shared"** - multiple tasks on same story branch is intentional and allowed.

**The issue is ONLY the branch NAME, not the structure.**

---

## Root Causes

### 1. Incomplete Hook Implementation
- `pre_tool_use.py` is a pass-through placeholder
- No branch name validation logic

### 2. Missing Validation in Scripts
- `validate_sdlc.py` doesn't check branch names
- Only validates commit message format

### 3. No Git Hooks Configured
- Pre-commit hook not set up (optional but would have caught this)
- No branch name validation on checkout/creation

### 4. Manual Branch Creation
- Branch was likely created manually with wrong naming convention
- No automated branch creation from task/story system

---

## Impact Assessment

### Low Impact Issues ✅
- Work is still traceable (commits reference correct tasks)
- All commits have proper task references (TASK-002, TASK-003, etc.)
- Subagent markers present in implementation commits
- Task folders properly organized
- Full traceability maintained

### Medium Impact Issues ⚠️
- Branch name doesn't follow convention
- Could confuse future developers ("why is TASK-002 branch used for TASK-005?")
- Merging to main will show inconsistent branch name in history

### No Impact ✅
- Multiple tasks on same branch is **correct behavior** for single story
- All commits properly attributed
- All documentation in place

---

## Gaps in Our SDLC Validation

### Gap 1: Pre-Tool-Use Hook
**File:** `.claude/hooks/pre_tool_use.py`
**Status:** Placeholder only
**Missing:**
- Branch name validation before git operations
- Enforcement of naming conventions
- Warning when creating branches with wrong prefix

### Gap 2: Branch Name Validation
**File:** `.sdlc-workflow/scripts/validate_sdlc.py`
**Missing:**
```python
def validate_branch_name(branch: str) -> Tuple[bool, List[str]]:
    """Validate branch follows naming convention."""
    # Should check:
    # - feature/US-XXX-description (for story work)
    # - hotfix/description (for emergency fixes)
    # - NOT feat/TASK-XXX (task-based naming)
```

### Gap 3: Git Pre-Commit Hook
**Status:** Not configured
**Location:** `.git/hooks/pre-commit` (should exist but doesn't)
**Missing:**
- Automated validation before commits
- Branch name check
- Task reference check

### Gap 4: Branch Creation Automation
**Status:** Manual process only
**Missing:**
- Automated branch creation from story ID
- Validation of branch name on creation
- Connection between story creation and branch setup

---

## Recommended Fixes

### Immediate: Rename Current Branch

**Option 1: Rename and continue**
```bash
# Rename branch
git branch -m feat/TASK-002-US-001B feature/US-001B-rbac-and-audit-logging

# Update remote if pushed
git push origin --delete feat/TASK-002-US-001B
git push origin feature/US-001B-rbac-and-audit-logging
git push origin -u feature/US-001B-rbac-and-audit-logging
```

**Option 2: Create new branch and cherry-pick**
```bash
# Create correctly named branch from main
git checkout main
git checkout -b feature/US-001B-rbac-and-audit-logging

# Cherry-pick commits from old branch
git cherry-pick <commit-range-from-TASK-002-branch>
```

### Short-Term: Add Branch Validation

**File:** `.sdlc-workflow/scripts/validate_branch.py` (new)
```python
#!/usr/bin/env python3
"""Validate git branch name follows SDLC conventions."""

import subprocess
import sys
import re

def get_current_branch():
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def validate_branch_name(branch: str) -> tuple[bool, str]:
    """
    Validate branch follows naming convention:
    - feature/US-XXX-description
    - hotfix/description
    - experiment/description
    """
    patterns = [
        r"^feature/US-\d+[A-Z]?-[\w-]+$",  # feature/US-001-login
        r"^hotfix/[\w-]+$",                # hotfix/security-fix
        r"^experiment/[\w-]+$",            # experiment/new-approach
        r"^main$",                         # main branch
    ]

    for pattern in patterns:
        if re.match(pattern, branch):
            return True, ""

    # Check common mistakes
    if re.match(r"^feat/TASK-\d+", branch):
        return False, (
            f"❌ Branch '{branch}' uses task-based naming.\n"
            f"   Should be: feature/US-XXX-description (story-based)\n"
            f"   Example: feature/US-001B-rbac-and-audit-logging"
        )

    return False, (
        f"❌ Branch '{branch}' doesn't follow naming convention.\n"
        f"   Expected formats:\n"
        f"   - feature/US-XXX-description (for story work)\n"
        f"   - hotfix/description (for emergency fixes)\n"
        f"   - experiment/description (for experiments)"
    )

def main():
    current_branch = get_current_branch()
    is_valid, error_msg = validate_branch_name(current_branch)

    if is_valid:
        print(f"✅ Branch name valid: {current_branch}")
        return 0
    else:
        print(error_msg)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Usage:**
```bash
# Validate current branch
.sdlc-workflow/scripts/validate_branch.py

# Add to pre-commit hook
echo ".sdlc-workflow/scripts/validate_branch.py" >> .git/hooks/pre-commit
```

### Medium-Term: Enhance Pre-Tool-Use Hook

**File:** `.claude/hooks/pre_tool_use.py`

Add branch validation before git operations:
```python
def validate_git_operation(tool_input: dict) -> tuple[bool, str]:
    """Validate git operations follow SDLC conventions."""

    if tool_input.get("tool") == "Bash":
        command = tool_input.get("command", "")

        # Check for branch creation
        if "git checkout -b" in command:
            branch_name = extract_branch_name(command)
            is_valid, error = validate_branch_name(branch_name)
            if not is_valid:
                return False, error

    return True, ""
```

### Long-Term: Automated Branch Creation

**Integration with story creation:**
```python
# When creating story with /story-new
# Automatically create correctly named branch
def create_story_with_branch(story_id: str, description: str):
    # Create story folder
    create_story_folder(story_id, description)

    # Create git branch
    branch_name = f"feature/{story_id}-{slugify(description)}"
    subprocess.run(["git", "checkout", "-b", branch_name])

    # Update story README with branch name
    update_story_readme(story_id, branch_name)
```

---

## Lessons Learned

### What Worked ✅
- Task folders maintain full context
- Commits properly reference tasks and subagents
- Multiple tasks on same story branch (correct pattern)
- Validation script catches commit message issues

### What Failed ❌
- No branch name validation
- Pre-tool-use hook is placeholder only
- Manual branch creation prone to errors
- No automated enforcement

### What to Improve 🔧
1. **Implement branch name validation** (high priority)
2. **Enhance pre-tool-use hook** (medium priority)
3. **Set up git pre-commit hook** (low priority, optional)
4. **Automate branch creation** (low priority, nice-to-have)

---

## Decision Required

**Question for user:**

Should we:

1. **Rename current branch** to `feature/US-001B-rbac-and-audit-logging`?
   - ✅ Fixes naming convention
   - ✅ Clean git history
   - ⚠️ Requires coordination if branch was pushed

2. **Keep current branch** and fix going forward?
   - ✅ No disruption to current work
   - ✅ Document as exception
   - ❌ Git history shows incorrect branch name

3. **Implement validation first** then decide?
   - ✅ Prevents future issues
   - ✅ Can test validation before renaming
   - ⏱️ Takes time to implement

---

## Summary

**The Issue:**
- Branch named `feat/TASK-002-US-001B` instead of `feature/US-001B-rbac-and-audit-logging`
- Multiple tasks on same branch is **correct**, name is **wrong**

**Why Missed:**
- Pre-tool-use hook is placeholder only
- No branch name validation in any script
- No git pre-commit hook configured
- Manual branch creation without validation

**Impact:**
- Low (work is traceable, commits are correct)
- Cosmetic issue in git history
- Potential confusion for future developers

**Recommendation:**
1. Rename branch to follow convention (if not pushed to remote yet)
2. Add branch validation script (short-term)
3. Enhance pre-tool-use hook (medium-term)
4. Consider automated branch creation (long-term)
