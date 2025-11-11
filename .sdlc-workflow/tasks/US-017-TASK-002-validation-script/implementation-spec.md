# TASK-002: Implementation Specification

**For:** devops-infra subagent
**Task:** Create branch validation script

---

## Overview

Create a Python script that validates git branch names against the task-based naming convention. The script must be fast, reliable, and provide clear error messages.

---

## File: `.sdlc-workflow/scripts/validate_branch.py`

### Script Structure

```python
#!/usr/bin/env python3
"""
Validate git branch names follow SDLC naming convention.

Pattern: {type}/TASK-{number}-US-{story}[-description]
Valid types: feat, fix, refactor, test, docs, chore
Special case: main

Exit codes:
  0 - Branch name is valid
  1 - Branch name is invalid
  2 - Error (git not available, script error)

Usage:
  ./validate_branch.py              # Validate current branch
  ./validate_branch.py <branch>     # Validate specific branch
"""

import re
import subprocess
import sys
from typing import Tuple

# Exit codes
EXIT_VALID = 0
EXIT_INVALID = 1
EXIT_ERROR = 2

# Valid branch types
VALID_TYPES = ['feat', 'fix', 'refactor', 'test', 'docs', 'chore']

# Regex pattern for task-based branches
# Pattern: {type}/TASK-{number}-US-{story}[-description]
# Example: feat/TASK-001-US-001-login-flow
BRANCH_PATTERN = re.compile(
    r"^(feat|fix|refactor|test|docs|chore)/TASK-\d+-US-\d+[A-Z]?(-[\w-]+)?$"
)


def get_current_branch() -> str:
    """Get current git branch name."""
    # Implementation: call git branch --show-current
    # Handle errors if not in git repo
    pass


def validate_branch_name(branch: str) -> Tuple[bool, str]:
    """
    Validate branch name against SDLC convention.

    Args:
        branch: Branch name to validate

    Returns:
        Tuple of (is_valid, error_message)
        - (True, "") if valid
        - (False, "error message") if invalid
    """
    # Special case: main branch is always valid
    if branch == "main":
        return True, ""

    # Check if matches task-based pattern
    if BRANCH_PATTERN.match(branch):
        return True, ""

    # Generate helpful error message based on what's wrong
    error_msg = generate_error_message(branch)
    return False, error_msg


def generate_error_message(branch: str) -> str:
    """
    Generate helpful error message for invalid branch.

    Identifies common mistakes and provides specific guidance.
    """
    # Check for old story-based pattern
    if branch.startswith("feature/US-"):
        return f"""❌ Branch '{branch}' uses old story-based naming.

Expected pattern: {{type}}/TASK-{{number}}-US-{{story}}[-description]

Valid examples:
  feat/TASK-001-US-001
  fix/TASK-042-US-001B
  refactor/TASK-005-US-001B-cleanup

Valid types: {', '.join(VALID_TYPES)}

Rationale: We use task-based branching (one branch per task, not per story)
to enable parallel work and better git history traceability.
"""

    # Check if missing TASK- prefix
    if "/US-" in branch and "/TASK-" not in branch:
        return f"""❌ Branch '{branch}' is missing task reference.

Expected pattern: {{type}}/TASK-{{number}}-US-{{story}}[-description]

Example: feat/TASK-001-US-001

Each branch must reference both a task (TASK-XXX) and story (US-XXX).
"""

    # Generic invalid pattern
    return f"""❌ Branch '{branch}' doesn't follow SDLC naming convention.

Expected pattern: {{type}}/TASK-{{number}}-US-{{story}}[-description]

Valid examples:
  feat/TASK-001-US-001
  fix/TASK-042-US-001B
  refactor/TASK-005-US-001B-cleanup
  test/TASK-010-US-002
  docs/TASK-020-US-005
  chore/TASK-030-US-010

Valid types: {', '.join(VALID_TYPES)}
Special branches: main
"""


def main() -> int:
    """Main entry point."""
    try:
        # Get branch name (from arg or current branch)
        if len(sys.argv) > 1:
            branch = sys.argv[1]
        else:
            branch = get_current_branch()

        # Validate branch name
        is_valid, error_msg = validate_branch_name(branch)

        if is_valid:
            print(f"✅ Branch name valid: {branch}")
            return EXIT_VALID
        else:
            print(error_msg, file=sys.stderr)
            return EXIT_INVALID

    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Git command failed: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
```

---

## Implementation Notes

### 1. get_current_branch() Implementation

```python
def get_current_branch() -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
        if not branch:
            raise ValueError("Not on a branch (detached HEAD?)")
        return branch
    except FileNotFoundError:
        raise RuntimeError("Git is not installed or not in PATH")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Not in a git repository: {e}")
```

### 2. Regex Pattern Explanation

```python
BRANCH_PATTERN = re.compile(
    r"^(feat|fix|refactor|test|docs|chore)/TASK-\d+-US-\d+[A-Z]?(-[\w-]+)?$"
)
```

**Pattern breakdown:**
- `^` - Start of string
- `(feat|fix|refactor|test|docs|chore)` - Valid type prefix
- `/` - Literal slash
- `TASK-` - Literal "TASK-"
- `\d+` - One or more digits (task number)
- `-US-` - Literal "-US-"
- `\d+` - One or more digits (story number)
- `[A-Z]?` - Optional single uppercase letter (for US-001B)
- `(-[\w-]+)?` - Optional description: dash + word chars/dashes
- `$` - End of string

**Test cases this pattern handles:**
- ✅ `feat/TASK-001-US-001` - Basic valid pattern
- ✅ `feat/TASK-001-US-001B` - Story with letter suffix
- ✅ `feat/TASK-001-US-001-login-flow` - With description
- ✅ `feat/TASK-001-US-001-login_flow` - Underscore in description
- ❌ `feature/US-001` - Wrong type, missing TASK
- ❌ `feat/TASK-001` - Missing US reference
- ❌ `feat/US-001` - Missing TASK reference

### 3. Error Message Strategy

Generate specific error messages based on detected pattern:

1. **Old story-based pattern** (`feature/US-XXX`)
   - Detected by: `branch.startswith("feature/US-")`
   - Message: Explain switch from story-based to task-based

2. **Missing TASK reference** (`feat/US-XXX`)
   - Detected by: `/US-` present but `/TASK-` missing
   - Message: Explain need for task reference

3. **Generic invalid pattern**
   - Fallback for all other cases
   - Message: Show full pattern with multiple examples

### 4. Performance Optimization

- Compile regex pattern once at module level (not in function)
- Use `re.match()` which is faster than `re.search()` for start-of-string patterns
- Minimize subprocess calls (only call git once)
- Simple string operations for special cases

**Expected performance:** < 10ms (well under 100ms requirement)

### 5. Error Handling

```python
try:
    # Main logic
except subprocess.CalledProcessError:
    # Git command failed (not in repo, git not available)
    return EXIT_ERROR
except Exception as e:
    # Unexpected error
    return EXIT_ERROR
```

**Fail-safe principle:** If script encounters unexpected error, return EXIT_ERROR (not EXIT_INVALID) to avoid blocking valid branches due to script bugs.

---

## Testing Requirements

### Unit Tests (pytest)

Create `tests/test_validate_branch.py` with following test cases:

#### 1. Valid Branch Names
```python
def test_valid_feat_branch():
    assert validate_branch_name("feat/TASK-001-US-001") == (True, "")

def test_valid_fix_branch():
    assert validate_branch_name("fix/TASK-042-US-001B") == (True, "")

def test_valid_with_description():
    assert validate_branch_name("feat/TASK-001-US-001-login") == (True, "")

def test_all_valid_types():
    for type in ['feat', 'fix', 'refactor', 'test', 'docs', 'chore']:
        branch = f"{type}/TASK-001-US-001"
        assert validate_branch_name(branch) == (True, "")

def test_main_branch():
    assert validate_branch_name("main") == (True, "")

def test_story_with_letter_suffix():
    assert validate_branch_name("feat/TASK-001-US-001B") == (True, "")
    assert validate_branch_name("feat/TASK-001-US-001Z") == (True, "")

def test_description_with_underscore():
    assert validate_branch_name("feat/TASK-001-US-001-login_flow") == (True, "")
```

#### 2. Invalid Branch Names
```python
def test_invalid_old_pattern():
    is_valid, msg = validate_branch_name("feature/US-001")
    assert not is_valid
    assert "old story-based naming" in msg

def test_invalid_no_task():
    is_valid, msg = validate_branch_name("feat/US-001")
    assert not is_valid
    assert "missing task reference" in msg.lower()

def test_invalid_no_story():
    is_valid, msg = validate_branch_name("feat/TASK-001")
    assert not is_valid

def test_invalid_wrong_type():
    is_valid, msg = validate_branch_name("feature/TASK-001-US-001")
    assert not is_valid

def test_invalid_malformed():
    is_valid, msg = validate_branch_name("feat-TASK-001")
    assert not is_valid
```

#### 3. Error Message Quality
```python
def test_error_message_for_old_pattern():
    _, msg = validate_branch_name("feature/US-001-login")
    assert "old story-based naming" in msg
    assert "feat/TASK-001-US-001" in msg  # Shows correct example

def test_error_message_shows_valid_types():
    _, msg = validate_branch_name("invalid-branch")
    assert "feat" in msg
    assert "fix" in msg
    assert "refactor" in msg
```

#### 4. Performance Test
```python
import time

def test_validation_performance():
    start = time.time()
    for i in range(100):
        validate_branch_name(f"feat/TASK-{i}-US-001")
    elapsed = time.time() - start
    assert elapsed < 0.1  # 100ms for 100 validations
```

#### 5. Integration Test
```python
def test_validates_current_branches():
    """Test that all current branches in repo are valid."""
    current_branches = [
        "main",
        "feat/TASK-001-US-001",
        "feat/TASK-002-US-001B",
        "feat/TASK-003-US-001B",
        "feat/TASK-004-US-001B",
        "refactor/TASK-005-US-001B",
        "test/TASK-006-US-001B",
    ]

    for branch in current_branches:
        is_valid, msg = validate_branch_name(branch)
        assert is_valid, f"Current branch {branch} should be valid but got: {msg}"
```

---

## File Permissions

After creating the script, set executable permission:

```bash
chmod +x .sdlc-workflow/scripts/validate_branch.py
```

---

## Verification Steps

After implementation:

1. **Run all unit tests:**
   ```bash
   pytest tests/test_validate_branch.py -v
   ```

2. **Test manually:**
   ```bash
   # Test current branch
   .sdlc-workflow/scripts/validate_branch.py

   # Test specific valid branch
   .sdlc-workflow/scripts/validate_branch.py feat/TASK-001-US-001
   echo $?  # Should be 0

   # Test invalid branch
   .sdlc-workflow/scripts/validate_branch.py feature/US-001
   echo $?  # Should be 1
   ```

3. **Verify all current branches pass:**
   ```bash
   git branch | while read branch; do
     .sdlc-workflow/scripts/validate_branch.py "$branch" || echo "FAILED: $branch"
   done
   ```

4. **Performance benchmark:**
   ```bash
   time .sdlc-workflow/scripts/validate_branch.py
   # Should be << 100ms
   ```

---

## Success Criteria

- [ ] Script created at correct location
- [ ] Script is executable
- [ ] All unit tests pass
- [ ] Code coverage > 90%
- [ ] All current branches validate successfully
- [ ] Performance < 100ms
- [ ] Error messages are clear and helpful
- [ ] Exit codes work correctly

---

## Subagent Notes

**Implementation Agent (devops-infra):**

You are implementing a validation script for git branch names. This script is critical infrastructure that will be called by the pre-tool-use hook to enforce branching conventions.

**Key Requirements:**
1. **Correctness:** Regex must match exactly the specified pattern
2. **Performance:** Must be fast (< 100ms)
3. **Error Messages:** Must be helpful and actionable
4. **Robustness:** Must handle errors gracefully
5. **Testing:** Comprehensive unit tests required

**Testing is Critical:**
- Test all 6 branch types
- Test edge cases (letter suffix, descriptions, special chars)
- Test all current branches validate successfully
- Test performance under load

After implementation:
- Run all tests
- Verify exit codes work correctly
- Verify error messages are clear
- Document any deviations from spec

Save implementation report to task folder's `subagent-reports/` directory.
