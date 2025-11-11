#!/usr/bin/env python3
"""
Update task phase in STATE.json.

Usage:
    task_update_phase.py <task-id> <phase> <action>

Arguments:
    task-id: TASK-001, TASK-002, etc.
    phase: RESEARCH | PLANNING | IMPLEMENTATION | TESTING | VALIDATION | COMPLETED
    action: start | complete

Examples:
    task_update_phase.py TASK-001 RESEARCH start
    task_update_phase.py TASK-001 RESEARCH complete
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


def update_phase(task_id: str, phase: str, action: str) -> None:
    """
    Update task phase in STATE.json.

    Args:
        task_id: Task identifier (TASK-001)
        phase: Phase name (RESEARCH, PLANNING, etc.)
        action: Either 'start' or 'complete'
    """
    project_root = get_project_root()
    task_dir = project_root / ".claude" / "tasks" / task_id
    state_file = task_dir / "STATE.json"

    # Validate task exists
    if not task_dir.exists():
        raise FileNotFoundError(f"Task directory not found: {task_dir}")

    if not state_file.exists():
        raise FileNotFoundError(f"STATE.json not found: {state_file}")

    # Valid phases
    valid_phases = ["RESEARCH", "PLANNING", "IMPLEMENTATION", "TESTING", "VALIDATION", "COMPLETED"]
    if phase not in valid_phases:
        raise ValueError(f"Invalid phase: {phase}. Must be one of: {', '.join(valid_phases)}")

    # Read STATE.json
    state = json.loads(state_file.read_text())

    now = datetime.now(timezone.utc).isoformat()

    if action == "start":
        # Update current phase
        state["phase"]["current"] = phase

        # Add to history
        state["phase"]["history"].append({
            "phase": phase,
            "started": now,
            "completed": None
        })

        # Update started timestamp if this is the first phase
        if state["timestamps"]["started"] is None:
            state["timestamps"]["started"] = now
            state["status"] = "in_progress"

    elif action == "complete":
        # Find current phase in history and mark complete
        for entry in reversed(state["phase"]["history"]):
            if entry["phase"] == phase and entry["completed"] is None:
                entry["completed"] = now

                # Calculate duration
                started = datetime.fromisoformat(entry["started"].replace('Z', '+00:00'))
                completed = datetime.fromisoformat(now.replace('Z', '+00:00'))
                duration = (completed - started).total_seconds() / 60
                entry["duration_minutes"] = round(duration, 2)
                break
        else:
            raise ValueError(f"No active {phase} phase found to complete")
    else:
        raise ValueError(f"Invalid action: {action}. Must be 'start' or 'complete'")

    # Update last_accessed
    state["timestamps"]["last_accessed"] = now

    # Write atomically (temp file + rename)
    temp_file = state_file.with_suffix('.json.tmp')
    temp_file.write_text(json.dumps(state, indent=2))
    temp_file.replace(state_file)

    print(f"✓ Phase updated: {phase} → {action}")


def main():
    """CLI entry point."""
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    task_id = sys.argv[1]
    phase = sys.argv[2].upper()
    action = sys.argv[3].lower()

    try:
        update_phase(task_id, phase, action)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
