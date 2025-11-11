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

Philosophy: Fail open - if this hook has issues, allow tools to execute
rather than blocking everything.
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
    # Match: git switch -c <branch>
    # Match: git switch --create <branch>
    # Don't match: git checkout <existing-branch>
    patterns = [
        r'\bgit\s+checkout\s+-b\b',
        r'\bgit\s+checkout\s+--branch\b',
        r'\bgit\s+switch\s+-c\b',
        r'\bgit\s+switch\s+--create\b',
    ]

    for pattern in patterns:
        if re.search(pattern, command):
            return True

    return False


def extract_branch_name(command: str) -> Optional[str]:
    """
    Extract branch name from git branch creation command.

    Args:
        command: Shell command string

    Returns:
        Branch name or None if can't extract
    """
    # Pattern: git checkout -b <branch-name> [other args]
    # Pattern: git switch -c <branch-name> [other args]
    # Handle quotes: git checkout -b "branch-name"
    # Stop at: && || ; | (command separators)
    # Stop at: -flags

    # Try patterns for both checkout and switch
    patterns = [
        r'checkout\s+-b\s+([\'"]?)([^\s\'"&;|]+)\1',  # checkout -b
        r'checkout\s+--branch\s+([\'"]?)([^\s\'"&;|]+)\1',  # checkout --branch
        r'switch\s+-c\s+([\'"]?)([^\s\'"&;|]+)\1',  # switch -c
        r'switch\s+--create\s+([\'"]?)([^\s\'"&;|]+)\1',  # switch --create
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
