#!/usr/bin/env python3
"""
Validate git branch names follow SDLC naming convention.

Pattern: {type}/TASK-{number}[-semantic-name]-US-{story}
Valid types: feat, fix, refactor, test, docs, chore
Special case: main

Semantic name (optional): 2-3 words, lowercase, hyphens only, alphanumeric

Exit codes:
  0 - Branch name is valid
  1 - Branch name is invalid
  2 - Error (git not available, script error)

Usage:
  ./validate_branch.py              # Validate current branch
  ./validate_branch.py <branch>     # Validate specific branch

Examples:
  ./validate_branch.py feat/TASK-001-US-001
  ./validate_branch.py feat/TASK-001-clerk-mounting-US-001
  ./validate_branch.py
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
# Pattern: {type}/TASK-{number}[-semantic-name]-US-{story}
# Examples:
#   - feat/TASK-001-US-001 (without semantic name - backward compatible)
#   - feat/TASK-001-clerk-mounting-US-001 (with semantic name)
# Semantic name: lowercase, alphanumeric, hyphens only (2-3 words max)
BRANCH_PATTERN = re.compile(
    r"^(feat|fix|refactor|test|docs|chore)/TASK-\d+(-[a-z0-9-]+)?-US-\d+[A-Z]?$"
)


def get_current_branch() -> str:
    """
    Get current git branch name.

    Returns:
        Current branch name

    Raises:
        RuntimeError: If git is not available or not in a git repository
        ValueError: If in detached HEAD state
    """
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

    Args:
        branch: Invalid branch name

    Returns:
        Detailed error message with guidance
    """
    # Check for old story-based pattern
    if branch.startswith("feature/US-"):
        return f"""❌ Branch '{branch}' uses old story-based naming.

Expected pattern: {{type}}/TASK-{{number}}[-semantic-name]-US-{{story}}

Valid examples:
  feat/TASK-001-US-001
  feat/TASK-001-clerk-mounting-US-001
  fix/TASK-042-login-tests-US-001B
  refactor/TASK-005-cleanup-US-001B

Valid types: {', '.join(VALID_TYPES)}
Semantic name: optional, 2-3 words, lowercase, hyphens only

Rationale: We use task-based branching (one branch per task, not per story)
to enable parallel work and better git history traceability.
"""

    # Check if missing TASK- prefix
    if "/US-" in branch and "/TASK-" not in branch:
        return f"""❌ Branch '{branch}' is missing task reference.

Expected pattern: {{type}}/TASK-{{number}}[-semantic-name]-US-{{story}}

Examples:
  feat/TASK-001-US-001
  feat/TASK-001-clerk-mounting-US-001

Each branch must reference both a task (TASK-XXX) and story (US-XXX).
Semantic name is optional but recommended for self-documenting git history.
"""

    # Generic invalid pattern
    return f"""❌ Branch '{branch}' doesn't follow SDLC naming convention.

Expected pattern: {{type}}/TASK-{{number}}[-semantic-name]-US-{{story}}

Valid examples:
  feat/TASK-001-US-001
  feat/TASK-001-clerk-mounting-US-001
  fix/TASK-042-login-tests-US-001B
  refactor/TASK-005-cleanup-US-001B
  test/TASK-010-e2e-tests-US-002
  docs/TASK-020-api-docs-US-005
  chore/TASK-030-build-config-US-010

Valid types: {', '.join(VALID_TYPES)}
Semantic name: optional, 2-3 words, lowercase, hyphens only
Special branches: main
"""


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0=valid, 1=invalid, 2=error)
    """
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
