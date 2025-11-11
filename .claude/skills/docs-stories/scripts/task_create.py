#!/usr/bin/env python3
"""
Create a new task from template.

Usage:
    task_create.py <story-id> <type>

Arguments:
    story-id: The US-XXX story this task belongs to
    type: Task type (feat, fix, docs, test, refactor)

Examples:
    task_create.py US-001 feat
    → Creates TASK-001, branch feat/TASK-001-US-001

Output:
    - Creates .claude/tasks/TASK-XXX/
    - Creates STATE.json from template
    - Creates subdirectories (research/, planning/, context/, logs/)
    - Creates git branch
    - Updates current.txt
"""
import sys
import json
import subprocess
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


def get_next_task_id(tasks_dir: Path) -> int:
    """Scan existing tasks to get next ID."""
    task_dirs = [d for d in tasks_dir.glob("TASK-*") if d.is_dir()]

    if not task_dirs:
        return 1

    numbers = []
    for d in task_dirs:
        try:
            # TASK-001 -> 001
            num_str = d.name.split('-')[1]
            numbers.append(int(num_str))
        except (ValueError, IndexError):
            continue

    return max(numbers) + 1 if numbers else 1


def get_story_info(story_id: str, project_root: Path) -> dict:
    """Get story information."""
    stories_dir = project_root / ".sdlc-workflow" / "stories"

    # Find story file
    story_files = list(stories_dir.rglob(f"{story_id}*.md"))
    if not story_files:
        raise FileNotFoundError(f"Story not found: {story_id}")

    story_file = story_files[0]

    # Extract domain from filename (US-001-auth-login.md -> auth)
    parts = story_file.stem.split('-')
    domain = parts[2] if len(parts) > 2 else "unknown"

    return {
        "story_id": story_id,
        "domain": domain,
        "file": str(story_file)
    }


def create_task(story_id: str, task_type: str) -> dict:
    """
    Create new task from template.

    Returns:
        Task information dict
    """
    project_root = get_project_root()
    tasks_dir = project_root / ".claude" / "tasks"
    template_file = project_root / ".claude" / "templates" / "task-state.json"

    # Validate
    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_file}")

    # Get story info
    story_info = get_story_info(story_id, project_root)

    # Get next task ID
    next_id = get_next_task_id(tasks_dir)
    task_id = f"TASK-{next_id:03d}"

    # Create branch name
    branch_name = f"{task_type}/TASK-{next_id:03d}-{story_id}"

    # Create task directory
    task_dir = tasks_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=False)

    # Create subdirectories
    (task_dir / "research").mkdir()
    (task_dir / "planning").mkdir()
    (task_dir / "context").mkdir()
    (task_dir / "logs").mkdir()

    # Read and populate template
    template = json.loads(template_file.read_text())

    now = datetime.now(timezone.utc).isoformat()

    template["task_id"] = task_id
    template["story_id"] = story_info["story_id"]
    template["task_type"] = task_type
    template["branch"] = branch_name
    template["timestamps"]["created"] = now
    template["timestamps"]["last_accessed"] = now
    template["domains"] = [story_info["domain"]]

    # Write STATE.json
    state_file = task_dir / "STATE.json"
    state_file.write_text(json.dumps(template, indent=2))

    # Create git branch
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        # Rollback: remove task directory
        import shutil
        shutil.rmtree(task_dir)
        raise RuntimeError(f"Failed to create git branch: {e.stderr}")

    # Update current.txt
    current_file = tasks_dir / "current.txt"
    current_file.write_text(task_id)

    return {
        "task_id": task_id,
        "story_id": story_info["story_id"],
        "branch": branch_name,
        "task_dir": str(task_dir)
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    story_id = sys.argv[1]
    task_type = sys.argv[2]

    # Validate task type
    valid_types = ["feat", "fix", "docs", "test", "refactor", "chore"]
    if task_type not in valid_types:
        print(f"Error: Invalid task type. Must be one of: {', '.join(valid_types)}", file=sys.stderr)
        sys.exit(1)

    try:
        result = create_task(story_id, task_type)
        print(f"✓ Task created: {result['task_id']}")
        print(f"  Story: {result['story_id']}")
        print(f"  Branch: {result['branch']}")
        print(f"  Directory: {result['task_dir']}")
        print()
        print("Next steps:")
        print("  1. /task-research - Research existing patterns")
        print("  2. /task-plan - Create implementation plan")
        print("  3. /task-implement - Start coding")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
