#!/usr/bin/env python3
"""
PostToolUse Hook - Update STATE.json after tool execution

Runs when: After any tool completes successfully
Purpose: Track commits, file modifications, and update task state

Input: JSON with tool name and results
Exit codes:
- 0: Success (always - never block post-execution)
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone


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


def update_state_file_modified(task_id: str, file_path: str):
    """Add file to files_modified array if not present."""
    try:
        project_root = get_project_root()
        state_file = project_root / ".claude" / "tasks" / task_id / "STATE.json"

        if not state_file.exists():
            return

        state = json.loads(state_file.read_text())

        # Add to files_modified if not already there
        if file_path not in state.get("files_modified", []):
            if "files_modified" not in state:
                state["files_modified"] = []
            state["files_modified"].append(file_path)

        # Update last_accessed
        state["timestamps"]["last_accessed"] = datetime.now(timezone.utc).isoformat()

        # Write atomically
        temp_file = state_file.with_suffix('.tmp')
        temp_file.write_text(json.dumps(state, indent=2))
        temp_file.replace(state_file)

    except Exception as e:
        print(f"⚠️  Failed to update file_modified: {e}", file=sys.stderr)


def track_git_commit(task_id: str):
    """Track latest git commit in STATE.json."""
    try:
        project_root = get_project_root()
        state_file = project_root / ".claude" / "tasks" / task_id / "STATE.json"

        if not state_file.exists():
            return

        # Get latest commit info
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%s|%at"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )

        sha, message, timestamp = result.stdout.strip().split('|')
        commit_time = datetime.fromtimestamp(int(timestamp), tz=timezone.utc).isoformat()

        # Get files changed count
        files_result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--numstat", "-r", sha],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        files_changed = len(files_result.stdout.strip().split('\n')) if files_result.stdout.strip() else 0

        # Update STATE.json
        state = json.loads(state_file.read_text())

        commit_entry = {
            "sha": sha,
            "message": message,
            "timestamp": commit_time,
            "files_changed": files_changed
        }

        # Add to commits array (avoid duplicates)
        if "commits" not in state:
            state["commits"] = []

        if not any(c.get("sha") == sha for c in state["commits"]):
            state["commits"].append(commit_entry)

        # Update last_accessed
        state["timestamps"]["last_accessed"] = datetime.now(timezone.utc).isoformat()

        # Write atomically
        temp_file = state_file.with_suffix('.tmp')
        temp_file.write_text(json.dumps(state, indent=2))
        temp_file.replace(state_file)

    except Exception as e:
        print(f"⚠️  Failed to track git commit: {e}", file=sys.stderr)


def main():
    """Hook entry point."""
    try:
        # Read hook input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Get current task
        task_id = get_current_task()
        if not task_id:
            # No active task, nothing to track
            sys.exit(0)

        # Handle Edit/Write tools - track file modifications
        if tool_name in ["Edit", "Write"]:
            file_path = tool_input.get("file_path", "")
            if file_path:
                update_state_file_modified(task_id, file_path)

        # Handle Bash tool - check for git commits
        elif tool_name == "Bash":
            command = tool_input.get("command", "")
            if command.startswith("git commit"):
                track_git_commit(task_id)

        # Always succeed (never block post-execution)
        sys.exit(0)

    except json.JSONDecodeError:
        # Invalid input, skip tracking
        sys.exit(0)
    except Exception as e:
        # On error, log but don't fail
        print(f"⚠️  PostToolUse hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
