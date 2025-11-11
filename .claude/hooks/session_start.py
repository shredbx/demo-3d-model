#!/usr/bin/env python3
"""
SessionStart Hook - Load task context when Claude session starts

Runs when: Claude Code starts a new session or resumes existing session
Purpose: Load current task context and display status

Exit codes:
- 0: Success (always allows session to continue)
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
    return Path.cwd()  # Fallback to current directory


def find_all_active_tasks(project_root: Path) -> list[dict]:
    """Find all tasks with status='in_progress'."""
    active_tasks = []
    tasks_dir = project_root / ".claude" / "tasks"

    if not tasks_dir.exists():
        return []

    for task_dir in tasks_dir.iterdir():
        if not task_dir.is_dir() or not task_dir.name.startswith("TASK-"):
            continue

        state_file = task_dir / "STATE.json"
        if not state_file.exists():
            continue

        try:
            state = json.loads(state_file.read_text())
            if state.get("status") == "in_progress":
                active_tasks.append({
                    "task_id": state.get("task_id", task_dir.name),
                    "story_id": state.get("story_id", "N/A"),
                    "branch": state.get("branch", "N/A"),
                    "phase": state.get("phase", {}).get("current", "N/A")
                })
        except Exception:
            continue

    return sorted(active_tasks, key=lambda x: x["task_id"])


def load_task_context():
    """Load and display current task context + all parallel tasks."""
    try:
        project_root = get_project_root()
        current_file = project_root / ".claude" / "tasks" / "current.txt"

        # Find all active tasks (for parallel workflow visibility)
        all_active = find_all_active_tasks(project_root)

        # Check if current.txt exists
        if not current_file.exists():
            if all_active:
                print("\n⚠️  Active tasks found but no current task set")
                print("   Use /task-resume or git checkout <branch>")
            else:
                print("\n📋 No active task")
                print("   Use /task-new to start working")
            return

        # Read current task
        task_id = current_file.read_text().strip()
        if not task_id or task_id == "none":
            if all_active:
                print("\n⚠️  Active tasks found but no current task set")
                print("   Use /task-resume or git checkout <branch>")
            else:
                print("\n📋 No active task")
                print("   Use /task-new to start working")
            return

        # Load current STATE.json
        state_file = project_root / ".claude" / "tasks" / task_id / "STATE.json"
        if not state_file.exists():
            print(f"\n⚠️  Task {task_id} is current but STATE.json not found")
            return

        state = json.loads(state_file.read_text())

        # Display current task context
        print(f"\n📋 Current Task: {task_id}")
        print(f"   Story: {state.get('story_id', 'N/A')}")
        print(f"   Phase: {state.get('phase', {}).get('current', 'N/A')}")
        print(f"   Status: {state.get('status', 'N/A')}")
        print(f"   Branch: {state.get('branch', 'N/A')}")

        # Show parallel tasks if any (excluding current)
        other_active = [t for t in all_active if t["task_id"] != task_id]
        if other_active:
            print(f"\n🔀 Parallel Tasks ({len(other_active)} active):")
            for task in other_active:
                print(f"   • {task['task_id']} ({task['story_id']}) - {task['phase']}")
                print(f"     Branch: {task['branch']}")
            print("   Switch: git checkout <branch>")

        # Suggest next action based on phase
        phase = state.get('phase', {}).get('current', '')
        if phase == 'PLANNING':
            print("\n💡 Suggested: /task-research or /task-plan")
        elif phase == 'RESEARCH':
            print("\n💡 Suggested: /task-plan")
        elif phase == 'IMPLEMENTATION':
            print("\n💡 Suggested: /task-implement <domain>")
        elif phase == 'TESTING':
            print("\n💡 Suggested: /task-test")
        elif phase == 'VALIDATION':
            print("\n💡 Suggested: /task-validate")
        elif state.get('status') == 'in_progress':
            print("\n💡 Suggested: Continue working or /task-status for details")

        print()  # Empty line for spacing

    except Exception as e:
        # Don't block session on errors
        print(f"\n⚠️  Session start hook error: {e}", file=sys.stderr)
        print("   Session continuing normally\n")


def main():
    """Hook entry point."""
    # Always succeed (never block session start)
    load_task_context()
    sys.exit(0)


if __name__ == "__main__":
    main()
