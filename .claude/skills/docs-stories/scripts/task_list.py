#!/usr/bin/env python3
"""
List tasks with filtering and status.

Usage:
    task_list.py [--status STATUS] [--story STORY-ID]

Arguments:
    --status: Filter by status (not_started | in_progress | completed)
    --story: Filter by story ID (US-001)

Examples:
    task_list.py
    → Lists all tasks

    task_list.py --status in_progress
    → Lists only in-progress tasks

    task_list.py --story US-001
    → Lists all tasks for US-001

    task_list.py --status in_progress --story US-001
    → Lists in-progress tasks for US-001
"""
import json
import sys
from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """Find project root (where .claude/ exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Not in a project with .claude/")


def list_tasks(status_filter: Optional[str] = None, story_filter: Optional[str] = None) -> None:
    """
    List tasks with optional filtering.

    Args:
        status_filter: Filter by status (not_started, in_progress, completed)
        story_filter: Filter by story ID (US-001)
    """
    project_root = get_project_root()
    tasks_dir = project_root / ".claude" / "tasks"

    if not tasks_dir.exists():
        print("No tasks directory found")
        return

    # Find all TASK-* directories
    task_dirs = sorted([d for d in tasks_dir.glob("TASK-*") if d.is_dir()])

    if not task_dirs:
        print("No tasks found")
        return

    # Collect task info
    tasks = []
    for task_dir in task_dirs:
        state_file = task_dir / "STATE.json"
        if not state_file.exists():
            continue

        try:
            state = json.loads(state_file.read_text())

            # Apply filters
            if status_filter and state["status"] != status_filter:
                continue

            if story_filter:
                # Extract US-XXX from story_id
                story_id = state.get("story_id", "")
                if not story_id.startswith(story_filter):
                    continue

            tasks.append({
                "task_id": state["task_id"],
                "story_id": state.get("story_id", "unknown"),
                "status": state["status"],
                "phase": state["phase"]["current"]
            })
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not read {state_file}: {e}", file=sys.stderr)
            continue

    if not tasks:
        print("No tasks match filters")
        return

    # Display tasks
    print("Tasks:")
    for task in tasks:
        story_short = task["story_id"].split('-')[0] + "-" + task["story_id"].split('-')[1] if '-' in task["story_id"] else task["story_id"]
        print(f"  {task['task_id']} ({story_short}) - {task['status']} - {task['phase']}")


def main():
    """CLI entry point."""
    status_filter = None
    story_filter = None

    # Parse arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == "--status":
            if i + 1 >= len(sys.argv):
                print("Error: --status requires a value", file=sys.stderr)
                sys.exit(1)
            status_filter = sys.argv[i + 1]
            i += 2
        elif arg == "--story":
            if i + 1 >= len(sys.argv):
                print("Error: --story requires a value", file=sys.stderr)
                sys.exit(1)
            story_filter = sys.argv[i + 1]
            i += 2
        elif arg == "--help" or arg == "-h":
            print(__doc__)
            sys.exit(0)
        else:
            print(f"Error: Unknown argument: {arg}", file=sys.stderr)
            print(__doc__)
            sys.exit(1)

    # Validate status filter
    if status_filter:
        valid_statuses = ["not_started", "in_progress", "completed"]
        if status_filter not in valid_statuses:
            print(f"Error: Invalid status. Must be one of: {', '.join(valid_statuses)}", file=sys.stderr)
            sys.exit(1)

    try:
        list_tasks(status_filter, story_filter)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
