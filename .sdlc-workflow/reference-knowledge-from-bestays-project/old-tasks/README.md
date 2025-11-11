# Local Task State

This directory contains local developer state and is NOT version controlled.

## Files

- **current.txt** - Current active task ID (e.g., "TASK-001" or "none")
- **commit-task-map.csv** - Tracks all commits to all tasks

## How It Works

The `current.txt` file is automatically updated by the `post-checkout` git hook
based on the current branch name. For example:

- Branch `feature/US-001-TASK-001` → current.txt contains "TASK-001"
- Branch `main` → current.txt contains "none"

This enables parallel workflow: switching git branches automatically switches
the active task context.

## Integration

Scripts read `current.txt` to determine which task to operate on:
- `task_update_phase.py` - Updates phase for current task
- `task_add_commit.py` - Adds commit to current task
- Commands like `/task-implement` use current task

## Parallel Workflow

Multiple tasks can have `status: "in_progress"` simultaneously. The `current.txt`
just points to whichever task corresponds to your currently checked out git branch.

Switch branches to switch tasks:
```bash
git checkout feature/US-001-TASK-001  # current.txt → "TASK-001"
git checkout feature/US-002-TASK-002  # current.txt → "TASK-002"
```
