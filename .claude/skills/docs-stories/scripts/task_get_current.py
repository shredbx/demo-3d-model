#!/usr/bin/env python3
"""
Get current active task ID.

Usage:
    task_get_current.py

Output:
    Prints task ID (e.g., TASK-001) or "none" if no active task

Examples:
    task_get_current.py
    → TASK-001
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


def get_current_task() -> str:
    """Get current task ID from current.txt."""
    project_root = get_project_root()
    current_file = project_root / ".claude" / "tasks" / "current.txt"

    if not current_file.exists():
        return "none"

    task_id = current_file.read_text().strip()
    return task_id if task_id else "none"


def main():
    """CLI entry point."""
    try:
        task_id = get_current_task()
        print(task_id)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
