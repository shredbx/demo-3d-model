# TASK-003: Implementation Specification

**For:** devops-infra subagent
**Task:** Enhance pre-tool-use hook with branch validation

---

## Overview

Enhance the existing `.claude/hooks/pre_tool_use.py` placeholder hook to validate git branch names before allowing branch creation commands.

**Critical:** This hook runs on EVERY tool call. Must be fast, reliable, and fail-safe.

---

## Current Hook (Placeholder)

**File:** `.claude/hooks/pre_tool_use.py`

```python
#!/usr/bin/env python3
"""
Pre-tool-use hook - runs before any tool execution

This is a pass-through hook that allows all tools to execute.
Currently serves as a placeholder for future tool-use monitoring.
"""

import sys


def main():
    """Allow all tool use - this is a placeholder hook."""
    # Could add monitoring/logging here in the future
    # For now, just pass through all tool calls
    sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## Enhanced Hook Implementation

**File:** `.claude/hooks/pre_tool_use.py`

```python
#!/usr/bin/env python3
"""
Pre-tool-use hook - validates git branch names before creation.

This hook runs before any tool execution and validates that git branch
creation commands follow the SDLC naming convention.

Pattern: {type}/TASK-{number}-US-{story}[-description]
Valid types: feat, fix, refactor, test, docs, chore

Exit codes:
  0 - Allow tool execution (valid branch OR not branch creation)
  2 - Block tool execution (invalid branch name)
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


# Exit codes
EXIT_ALLOW = 0   # Allow tool execution
EXIT_BLOCK = 2   # Block tool execution

# Path to validation script
REPO_ROOT = Path(__file__).parent.parent.parent
VALIDATE_SCRIPT = REPO_ROOT / ".sdlc-workflow" / "scripts" / "validate_branch.py"


def read_tool_input() -> dict:
    """
    Read tool call input from stdin.

    Returns:
        dict: Tool call information (tool name, parameters, etc.)
    """
    try:
        input_data = sys.stdin.read()
        if not input_data:
            return {}
        return json.loads(input_data)
    except json.JSONDecodeError:
        # If can't parse input, allow (fail-safe)
        return {}
    except Exception:
        # Any other error, allow (fail-safe)
        return {}


def is_branch_creation_command(command: str) -> bool:
    """
    Check if command is a git branch creation command.

    Args:
        command: Shell command string

    Returns:
        bool: True if command creates a new branch
    """
    # Match: git checkout -b <branch>
    # Match: git checkout --branch <branch>
    # Don't match: git checkout <existing-branch>
    patterns = [
        r'\bgit\s+checkout\s+-b\b',
        r'\bgit\s+checkout\s+--branch\b',
    ]

    for pattern in patterns:
        if re.search(pattern, command):
            return True

    return False


def extract_branch_name(command: str) -> Optional[str]:
    """
    Extract branch name from git checkout -b command.

    Args:
        command: Shell command string

    Returns:
        Branch name or None if can't extract
    """
    # Pattern: git checkout -b <branch-name> [other args]
    # Handle quotes: git checkout -b "branch-name"
    # Stop at: && || ; | (command separators)
    # Stop at: -flags

    # Try pattern: checkout -b <branch>
    patterns = [
        r'checkout\s+-b\s+([\'"]?)([^\s\'"&&||;|]+)\1',  # With optional quotes
        r'checkout\s+--branch\s+([\'"]?)([^\s\'"&&||;|]+)\1',
    ]

    for pattern in patterns:
        match = re.search(pattern, command)
        if match:
            # Return the captured group (without quotes)
            return match.group(2)

    return None


def validate_branch_via_script(branch: str) -> Tuple[bool, str]:
    """
    Call validation script to check branch name.

    Args:
        branch: Branch name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not VALIDATE_SCRIPT.exists():
        # Fail-safe: if script doesn't exist, allow
        print(f"⚠️  Warning: Validation script not found: {VALIDATE_SCRIPT}", file=sys.stderr)
        return True, ""

    try:
        result = subprocess.run(
            [str(VALIDATE_SCRIPT), branch],
            capture_output=True,
            text=True,
            timeout=1  # 1 second timeout
        )

        # Exit code 0 = valid, 1 = invalid, 2 = error
        if result.returncode == 0:
            return True, ""
        elif result.returncode == 1:
            # Invalid - use script's error message
            error_msg = result.stderr.strip() or result.stdout.strip()
            return False, error_msg
        else:
            # Script error - fail-safe: allow
            print(f"⚠️  Warning: Validation script error (exit {result.returncode})", file=sys.stderr)
            return True, ""

    except subprocess.TimeoutExpired:
        # Script timeout - fail-safe: allow
        print("⚠️  Warning: Validation script timeout", file=sys.stderr)
        return True, ""
    except Exception as e:
        # Any error - fail-safe: allow
        print(f"⚠️  Warning: Validation error: {e}", file=sys.stderr)
        return True, ""


def format_error_message(branch: str, validation_error: str) -> str:
    """
    Format error message for invalid branch name.

    Args:
        branch: Invalid branch name
        validation_error: Error message from validation script

    Returns:
        Formatted error message for user
    """
    return f"""
{'='*70}
❌ BLOCKED: Invalid branch name '{branch}'
{'='*70}

{validation_error}

For more information, see: .sdlc-workflow/GIT_WORKFLOW.md
{'='*70}
"""


def main() -> int:
    """Main hook entry point."""
    try:
        # Read tool call input
        tool_input = read_tool_input()

        # Only validate Bash tool calls
        if tool_input.get("tool") != "Bash":
            return EXIT_ALLOW

        # Get command from tool input
        command = tool_input.get("command", "")
        if not command:
            return EXIT_ALLOW

        # Check if this is a branch creation command
        if not is_branch_creation_command(command):
            return EXIT_ALLOW

        # Extract branch name
        branch_name = extract_branch_name(command)
        if not branch_name:
            # Can't extract branch name - fail-safe: allow
            print("⚠️  Warning: Could not extract branch name from command", file=sys.stderr)
            return EXIT_ALLOW

        # Validate branch name
        is_valid, error_msg = validate_branch_via_script(branch_name)

        if is_valid:
            # Valid branch name - allow
            return EXIT_ALLOW
        else:
            # Invalid branch name - block with error message
            print(format_error_message(branch_name, error_msg), file=sys.stderr)
            return EXIT_BLOCK

    except Exception as e:
        # Any unexpected error - fail-safe: allow
        print(f"⚠️  Warning: Hook error: {e}", file=sys.stderr)
        return EXIT_ALLOW


if __name__ == "__main__":
    sys.exit(main())
```

---

## Implementation Notes

### 1. Tool Input Format

The hook receives tool call information via stdin as JSON:

```json
{
  "tool": "Bash",
  "command": "git checkout -b feat/TASK-001-US-001",
  "description": "Create new feature branch",
  ...
}
```

**Read with:** `json.loads(sys.stdin.read())`

### 2. Branch Name Extraction Regex

```python
r'checkout\s+-b\s+([\'"]?)([^\s\'"&&||;|]+)\1'
```

**Explanation:**
- `checkout\s+-b\s+` - Match "checkout -b " with whitespace
- `([\'"]?)` - Optional opening quote (captured group 1)
- `([^\s\'"&&||;|]+)` - Branch name: anything except whitespace, quotes, command separators (captured group 2)
- `\1` - Matching closing quote (backreference to group 1)

**Handles:**
- ✅ `git checkout -b feat/TASK-001-US-001`
- ✅ `git checkout -b "feat/TASK-001-US-001"`
- ✅ `git checkout -b 'feat/TASK-001-US-001'`
- ✅ `git checkout -b feat/TASK-001-US-001 --track origin/main`
- ✅ `git checkout -b feat/TASK-001-US-001 && git push`

### 3. Fail-Safe Strategy

**Principle:** When in doubt, allow (don't break workflow)

```python
# Pattern for all error handling:
try:
    # Validation logic
except Exception as e:
    print(f"Warning: {e}", file=sys.stderr)
    return EXIT_ALLOW  # Fail-safe: allow
```

**Fail-safe scenarios:**
1. Can't read tool input → allow
2. Can't parse JSON → allow
3. Validation script missing → allow (with warning)
4. Validation script crashes → allow (with warning)
5. Validation script timeout → allow (with warning)
6. Can't extract branch name → allow (with warning)
7. Any unexpected error → allow (with warning)

### 4. Performance Optimization

**Target:** < 100ms overhead

**Optimizations:**
1. Early returns (skip non-Bash tools immediately)
2. Skip non-git commands early
3. 1-second timeout on validation script
4. No complex parsing (simple regex)
5. Validation script itself is fast (< 10ms)

**Expected timing:**
- JSON parsing: ~1ms
- Pattern matching: ~1ms
- Subprocess call: ~10-50ms (validation script)
- **Total:** ~12-52ms (well under 100ms)

### 5. Error Message Format

**User sees:**
```
========================================================================
❌ BLOCKED: Invalid branch name 'feature/US-001-login'
========================================================================

❌ Branch 'feature/US-001-login' uses old story-based naming.

Expected pattern: {type}/TASK-{number}-US-{story}[-description]

Valid examples:
  feat/TASK-001-US-001
  fix/TASK-042-US-001B
  refactor/TASK-005-US-001B-cleanup

Valid types: feat, fix, refactor, test, docs, chore

For more information, see: .sdlc-workflow/GIT_WORKFLOW.md
========================================================================
```

**Format:** Clear separator lines, actionable guidance, reference to docs

---

## Testing Requirements

### Unit Tests

**File:** `tests/integration/test_pre_tool_use_hook.py`

```python
import json
import subprocess
from pathlib import Path

HOOK_PATH = Path(".claude/hooks/pre_tool_use.py")

def test_allows_non_git_commands():
    """Test hook allows non-git commands."""
    tool_input = json.dumps({"tool": "Bash", "command": "npm install"})

    result = subprocess.run(
        [str(HOOK_PATH)],
        input=tool_input,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0  # Allow

def test_allows_git_status():
    """Test hook allows non-branch-creation git commands."""
    tool_input = json.dumps({"tool": "Bash", "command": "git status"})

    result = subprocess.run(
        [str(HOOK_PATH)],
        input=tool_input,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0  # Allow

def test_allows_valid_branch():
    """Test hook allows valid branch creation."""
    tool_input = json.dumps({
        "tool": "Bash",
        "command": "git checkout -b feat/TASK-001-US-001"
    })

    result = subprocess.run(
        [str(HOOK_PATH)],
        input=tool_input,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0  # Allow

def test_blocks_invalid_branch():
    """Test hook blocks invalid branch creation."""
    tool_input = json.dumps({
        "tool": "Bash",
        "command": "git checkout -b feature/US-001-login"
    })

    result = subprocess.run(
        [str(HOOK_PATH)],
        input=tool_input,
        capture_output=True,
        text=True
    )

    assert result.returncode == 2  # Block
    assert "Invalid branch name" in result.stderr or "Invalid branch name" in result.stdout

def test_extracts_branch_with_quotes():
    """Test hook handles quoted branch names."""
    tool_input = json.dumps({
        "tool": "Bash",
        "command": 'git checkout -b "feat/TASK-001-US-001"'
    })

    result = subprocess.run(
        [str(HOOK_PATH)],
        input=tool_input,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0  # Allow

def test_fail_safe_on_missing_script():
    """Test hook allows if validation script missing."""
    # Temporarily rename validation script
    # Run hook
    # Verify it allows (fail-safe)
    # Restore script
    pass  # Implementation depends on test setup
```

### Integration Tests

1. **Test with all current branches:**
   ```bash
   for branch in $(git branch | sed 's/^[* ]*//'); do
     test_hook_allows "$branch"
   done
   ```

2. **Test invalid patterns:**
   ```bash
   test_hook_blocks "feature/US-001"
   test_hook_blocks "random-branch"
   test_hook_blocks "feat/US-001"
   ```

3. **Test command variations:**
   ```bash
   test_hook "git checkout -b feat/TASK-001-US-001"
   test_hook 'git checkout -b "feat/TASK-001-US-001"'
   test_hook "git checkout --branch feat/TASK-001-US-001"
   test_hook "git checkout -b feat/TASK-001-US-001 --track origin/main"
   ```

---

## Deployment Steps

1. **Backup original hook:**
   ```bash
   cp .claude/hooks/pre_tool_use.py .claude/hooks/pre_tool_use.py.backup
   ```

2. **Test validation script exists:**
   ```bash
   .sdlc-workflow/scripts/validate_branch.py
   # Should work
   ```

3. **Deploy enhanced hook:**
   ```bash
   # Copy new implementation to pre_tool_use.py
   ```

4. **Test manually:**
   ```bash
   # Try creating valid branch (should work)
   git checkout -b feat/TASK-999-US-999-test

   # Try creating invalid branch (should block)
   git checkout -b feature/US-999-test
   ```

5. **Rollback if issues:**
   ```bash
   cp .claude/hooks/pre_tool_use.py.backup .claude/hooks/pre_tool_use.py
   ```

---

## Success Criteria

- [ ] Hook detects branch creation commands
- [ ] Hook extracts branch names correctly
- [ ] Hook calls validation script
- [ ] Hook blocks invalid branches (exit 2)
- [ ] Hook allows valid branches (exit 0)
- [ ] Fail-safe behavior works (allows on errors)
- [ ] Error messages are clear
- [ ] Performance < 100ms overhead
- [ ] All integration tests pass
- [ ] Manual testing successful
- [ ] No false positives (valid branches blocked)
- [ ] No false negatives (invalid branches allowed)

---

## Subagent Notes

**Implementation Agent (devops-infra):**

This is a critical infrastructure component. Follow these guidelines:

1. **Preserve fail-safe behavior** - Always allow on errors
2. **Test thoroughly** - Integration tests are mandatory
3. **Keep backup** - Save original hook before modification
4. **Verify performance** - Benchmark overhead
5. **Manual testing** - Test with actual git commands

After implementation:
- Run all integration tests
- Verify all current branches work
- Test invalid branch rejection
- Verify fail-safe scenarios
- Document any deviations from spec

Save implementation report to `subagent-reports/` directory.
