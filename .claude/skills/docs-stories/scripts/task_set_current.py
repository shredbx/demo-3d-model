#!/usr/bin/env python3
"""
Set current active task ID.

Usage:
    task_set_current.py <task-id>
    task_set_current.py none

Examples:
    task_set_current.py TASK-001
    task_set_current.py none
"""
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Find project root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Not in a project with .claude/")


def set_current_task(task_id: str):
    """Set current task ID."""
    project_root = get_project_root()
    tasks_dir = project_root / ".claude" / "tasks"
    current_file = tasks_dir / "current.txt"

    # Validate task exists (unless setting to "none")
    if task_id != "none":
        task_dir = tasks_dir / task_id
        if not task_dir.exists():
            raise FileNotFoundError(f"Task does not exist: {task_id}")

    # Write current.txt
    tasks_dir.mkdir(parents=True, exist_ok=True)
    current_file.write_text(task_id)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    task_id = sys.argv[1]

    try:
        set_current_task(task_id)
        print(f"✓ Current task set to: {task_id}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
