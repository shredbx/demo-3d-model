#!/usr/bin/env python3
"""
Add file to files_modified array (if not already present).

Usage:
    task_add_file_modified.py <task-id> <file-path>

Arguments:
    task-id: TASK-001
    file-path: relative path from repo root

Examples:
    task_add_file_modified.py TASK-001 apps/server/api/auth.py
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def get_project_root() -> Path:
    """Find project root (where .claude/ exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Not in a project with .claude/")


def add_file_modified(task_id: str, file_path: str) -> None:
    """
    Add file to files_modified array if not already present.

    Args:
        task_id: Task identifier (TASK-001)
        file_path: Relative path from repo root
    """
    project_root = get_project_root()
    task_dir = project_root / ".claude" / "tasks" / task_id
    state_file = task_dir / "STATE.json"

    # Validate task exists
    if not task_dir.exists():
        raise FileNotFoundError(f"Task directory not found: {task_dir}")

    if not state_file.exists():
        raise FileNotFoundError(f"STATE.json not found: {state_file}")

    # Read STATE.json
    state = json.loads(state_file.read_text())

    # Add file if not already present
    if file_path not in state["files_modified"]:
        state["files_modified"].append(file_path)
        print(f"✓ File tracked: {file_path}")
    else:
        print(f"  File already tracked: {file_path}")

    # Update last_accessed
    now = datetime.now(timezone.utc).isoformat()
    state["timestamps"]["last_accessed"] = now

    # Write atomically (temp file + rename)
    temp_file = state_file.with_suffix('.json.tmp')
    temp_file.write_text(json.dumps(state, indent=2))
    temp_file.replace(state_file)


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    task_id = sys.argv[1]
    file_path = sys.argv[2]

    try:
        add_file_modified(task_id, file_path)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
