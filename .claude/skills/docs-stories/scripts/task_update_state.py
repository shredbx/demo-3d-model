#!/usr/bin/env python3
"""
Update STATE.json field atomically.

Usage:
    task_update_state.py <task-id> <field> <value>

Supports dot notation for nested fields:
    task_update_state.py TASK-001 status completed
    task_update_state.py TASK-001 timestamps.completed "2025-11-01T12:00:00Z"
    task_update_state.py TASK-001 phase.current IMPLEMENTATION

Examples:
    task_update_state.py TASK-001 status in_progress
    task_update_state.py TASK-001 timestamps.started "2025-11-01T10:00:00Z"
    task_update_state.py TASK-001 notes "Backend complete, frontend pending"
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone


def get_project_root() -> Path:
    """Find project root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Not in a project with .claude/")


def parse_value(value_str: str):
    """Parse value string to appropriate type."""
    # Try to parse as JSON first (handles numbers, booleans, lists, objects)
    try:
        return json.loads(value_str)
    except json.JSONDecodeError:
        # Return as string if not valid JSON
        return value_str


def update_state(task_id: str, field: str, value: str):
    """Update STATE.json field atomically."""
    project_root = get_project_root()
    state_file = project_root / ".claude" / "tasks" / task_id / "STATE.json"

    # Validate
    if not state_file.exists():
        raise FileNotFoundError(f"STATE.json not found for {task_id}")

    # Read current state
    state = json.loads(state_file.read_text())

    # Handle nested fields with dot notation
    keys = field.split('.')
    target = state
    for key in keys[:-1]:
        if key not in target:
            target[key] = {}
        target = target[key]

    # Set value (parse to correct type)
    parsed_value = parse_value(value)
    target[keys[-1]] = parsed_value

    # Update last_accessed timestamp
    state["timestamps"]["last_accessed"] = datetime.now(timezone.utc).isoformat()

    # Write atomically (temp file + rename)
    temp_file = state_file.with_suffix('.tmp')
    temp_file.write_text(json.dumps(state, indent=2))
    temp_file.replace(state_file)

    return state


def main():
    """CLI entry point."""
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    task_id = sys.argv[1]
    field = sys.argv[2]
    value = sys.argv[3]

    try:
        state = update_state(task_id, field, value)
        print(f"✓ Updated {task_id} {field} = {value}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
