#!/usr/bin/env python3
"""
UserPromptSubmit Hook - Validate command prerequisites

Runs when: User submits a prompt/command
Purpose: Validate that prerequisites are met before processing

Input: JSON with user prompt
Exit codes:
- 0: Allow command to proceed
- 2: Block command with error message
"""
import json
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Find project root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent
    return Path.cwd()


def get_current_task() -> str | None:
    """Get current task ID."""
    try:
        project_root = get_project_root()
        current_file = project_root / ".claude" / "tasks" / "current.txt"
        if not current_file.exists():
            return None
        task_id = current_file.read_text().strip()
        return task_id if task_id and task_id != "none" else None
    except Exception:
        return None


def validate_command(prompt: str) -> bool:
    """
    Validate command prerequisites.

    Returns:
        True if command should be allowed, False if blocked
    """
    # Commands that require an active task
    requires_task_commands = [
        "/task-research",
        "/task-plan",
        "/task-implement",
        "/task-test",
        "/task-validate",
        "/task-complete",
        "/task-status"
    ]

    # Check if prompt starts with any command requiring a task
    requires_task = any(prompt.strip().startswith(cmd) for cmd in requires_task_commands)

    if requires_task:
        task_id = get_current_task()
        if not task_id:
            print("\n" + "=" * 70)
            print("❌ NO ACTIVE TASK")
            print("=" * 70)
            print(f"\nCommand requires an active task: {prompt.split()[0]}")
            print("\n💡 Create a task first:")
            print("   /task-new US-XXX <type>")
            print("\n   Or resume existing task:")
            print("   /task-resume TASK-XXX")
            print("=" * 70 + "\n")
            return False

    return True


def main():
    """Hook entry point."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
        prompt = input_data.get("prompt", "")

        # Validate
        if validate_command(prompt):
            sys.exit(0)  # Allow
        else:
            sys.exit(2)  # Block

    except json.JSONDecodeError:
        # Invalid input, allow to proceed (fail open)
        sys.exit(0)
    except Exception as e:
        # On error, log but don't block (fail open)
        print(f"⚠️  Validation hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
