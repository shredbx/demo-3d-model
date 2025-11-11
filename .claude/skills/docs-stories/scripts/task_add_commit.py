#!/usr/bin/env python3
"""
Add commit entry to STATE.json commits array.

Usage:
    task_add_commit.py <task-id> <sha> <message> <timestamp> <files-changed>

Arguments:
    task-id: TASK-001
    sha: git commit SHA (first 7 chars)
    message: commit message (escaped)
    timestamp: ISO 8601 format
    files-changed: number of files

Examples:
    task_add_commit.py TASK-001 abc1234 "feat: add login API" "2025-11-06T10:00:00Z" 3
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


def add_commit(task_id: str, sha: str, message: str, timestamp: str, files_changed: int) -> None:
    """
    Add commit entry to STATE.json.

    Args:
        task_id: Task identifier (TASK-001)
        sha: Commit SHA (first 7 chars)
        message: Commit message
        timestamp: ISO 8601 timestamp
        files_changed: Number of files changed
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

    # Add commit entry
    commit_entry = {
        "sha": sha,
        "message": message,
        "timestamp": timestamp,
        "files_changed": files_changed
    }

    state["commits"].append(commit_entry)

    # Update last_accessed
    now = datetime.now(timezone.utc).isoformat()
    state["timestamps"]["last_accessed"] = now

    # Write atomically (temp file + rename)
    temp_file = state_file.with_suffix('.json.tmp')
    temp_file.write_text(json.dumps(state, indent=2))
    temp_file.replace(state_file)

    print(f"✓ Commit added: {sha}")


def main():
    """CLI entry point."""
    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(1)

    task_id = sys.argv[1]
    sha = sys.argv[2]
    message = sys.argv[3]
    timestamp = sys.argv[4]
    files_changed = int(sys.argv[5])

    try:
        add_commit(task_id, sha, message, timestamp, files_changed)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
