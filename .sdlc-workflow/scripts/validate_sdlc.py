#!/usr/bin/env python3
"""
SDLC Validation Script

Validates that commits follow SDLC workflow rules:
- Implementation changes must reference task
- Implementation changes must indicate subagent
- Coordinator can only modify workflow/docs
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Paths that coordinator (main Claude) CAN modify
COORDINATOR_ALLOWED = [
    ".claude/",
    ".sdlc-workflow/",
    "CLAUDE.md",
    "README.md",
    ".gitignore",
    ".env.example",
]

# Paths that require subagent (implementation code)
IMPLEMENTATION_PATHS = [
    "apps/server/src/",
    "apps/frontend/src/",
    "tests/",
]

# Paths that are configuration (either can modify with caution)
CONFIG_PATHS = [
    "apps/server/pyproject.toml",
    "apps/frontend/package.json",
    "docker-compose.yml",
    "Makefile",
]


def get_staged_files() -> List[str]:
    """Get list of staged files for commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [f for f in result.stdout.strip().split("\n") if f]


def get_commit_message() -> str:
    """Get the commit message being prepared."""
    # Try to read from .git/COMMIT_EDITMSG
    commit_msg_file = Path(".git/COMMIT_EDITMSG")
    if commit_msg_file.exists():
        return commit_msg_file.read_text()
    return ""


def is_coordinator_file(filepath: str) -> bool:
    """Check if file can be modified by coordinator."""
    for allowed in COORDINATOR_ALLOWED:
        if filepath.startswith(allowed):
            return True
    return False


def is_implementation_file(filepath: str) -> bool:
    """Check if file is implementation code requiring subagent."""
    for impl_path in IMPLEMENTATION_PATHS:
        if filepath.startswith(impl_path):
            return True
    return False


def is_config_file(filepath: str) -> bool:
    """Check if file is configuration."""
    for config_path in CONFIG_PATHS:
        if filepath == config_path:
            return True
    return False


def has_task_reference(commit_msg: str) -> bool:
    """Check if commit message references a task."""
    # Look for "TASK-XXX" or "Task: TASK-XXX"
    import re
    return bool(re.search(r"TASK-\d+", commit_msg, re.IGNORECASE))


def has_subagent_marker(commit_msg: str) -> bool:
    """Check if commit message indicates subagent was used."""
    # Look for "Subagent: xxxx"
    return "Subagent:" in commit_msg or "subagent:" in commit_msg.lower()


def validate_commit() -> Tuple[bool, List[str]]:
    """
    Validate that commit follows SDLC rules.

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    try:
        staged_files = get_staged_files()
        commit_msg = get_commit_message()

        if not staged_files:
            return True, []  # No files to validate

        # Check each staged file
        implementation_files = []
        coordinator_files = []
        config_files = []

        for filepath in staged_files:
            if is_implementation_file(filepath):
                implementation_files.append(filepath)
            elif is_coordinator_file(filepath):
                coordinator_files.append(filepath)
            elif is_config_file(filepath):
                config_files.append(filepath)
            else:
                # Unknown path - warn but don't block
                pass

        # If there are implementation files, validate commit message
        if implementation_files:
            if not has_task_reference(commit_msg):
                errors.append(
                    "❌ Implementation changes require task reference (TASK-XXX)\n"
                    f"   Files: {', '.join(implementation_files[:3])}"
                    + ("..." if len(implementation_files) > 3 else "")
                )

            if not has_subagent_marker(commit_msg):
                errors.append(
                    "❌ Implementation changes must be done by subagent\n"
                    "   Add to commit message: 'Subagent: <subagent-name>'\n"
                    "   Valid subagents: dev-backend-fastapi, dev-frontend-svelte, "
                    "playwright-e2e-tester"
                )

        # Warn about config files (but don't block)
        if config_files:
            print("⚠️  WARNING: Modifying configuration files:")
            for cfg in config_files:
                print(f"    - {cfg}")
            print("   Ensure changes are intentional and documented.\n")

        return len(errors) == 0, errors

    except subprocess.CalledProcessError as e:
        errors.append(f"❌ Git command failed: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"❌ Validation error: {e}")
        return False, errors


def main():
    """Run SDLC validation."""
    print("\n🔍 SDLC Workflow Validation")
    print("=" * 50)

    is_valid, errors = validate_commit()

    if is_valid:
        print("✅ All checks passed!")
        print("=" * 50 + "\n")
        return 0
    else:
        print("\n" + "=" * 50)
        print("🚨 SDLC VALIDATION FAILED")
        print("=" * 50 + "\n")

        for error in errors:
            print(error + "\n")

        print("=" * 50)
        print("\n📖 See CLAUDE.md section: 'Coordinator vs Implementer Roles'")
        print("   for proper workflow.\n")

        return 1


if __name__ == "__main__":
    sys.exit(main())
