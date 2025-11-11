# Implementation Specification: Minimal Viable Task System

**Date:** 2025-11-06
**Status:** Ready for Implementation
**Target:** devops-infra subagent
**Goal:** Enable task creation and workflow for US-001
**Estimated Time:** 6-8 hours

---

## Executive Summary

Implement the Minimal Viable Task System that enables:
- Task creation from user stories
- Git-integrated task tracking (branch name → task ID)
- Automated STATE.json tracking via hooks
- Parallel workflow support (multiple tasks on different branches)
- Basic workflow phases (research, planning, implementation)

**Core Principle:** Git branch determines current task. Hooks automate everything.

---

## Architecture Overview

### Directory Structure

```
Repository:
├── .claude/                              # Developer tools (mostly committed)
│   ├── tasks/                           # LOCAL STATE (NOT committed, add to .gitignore)
│   │   ├── current.txt                  # "TASK-001" (active task pointer)
│   │   └── commit-task-map.csv         # All commits to tasks
│   │
│   ├── skills/docs-stories/scripts/    # Python scripts (committed)
│   │   ├── task_update_phase.py        # [NEW] Update task phase
│   │   ├── task_add_commit.py          # [NEW] Track commits in STATE.json
│   │   ├── task_add_file_modified.py   # [NEW] Track file modifications
│   │   ├── story_create.py             # [NEW] Create stories
│   │   ├── story_find.py               # [NEW] Find stories
│   │   ├── task_list.py                # [NEW] List tasks
│   │   ├── task_create.py              # [EXISTS] Already implemented
│   │   ├── task_get_current.py         # [EXISTS] Already implemented
│   │   ├── task_set_current.py         # [EXISTS] Already implemented
│   │   └── task_update_state.py        # [EXISTS] Already implemented
│   │
│   └── commands/                        # Slash commands (committed)
│       ├── story-new.md                 # [EXISTS] Already implemented
│       ├── task-new.md                  # [NEW] Create task
│       ├── task-research.md             # [NEW] Research phase
│       ├── task-plan.md                 # [NEW] Planning phase
│       └── task-implement.md            # [NEW] Implementation phase
│
└── .sdlc-workflow/
    ├── stories/                          # User stories (committed)
    │   └── auth/US-001-*.md             # [EXISTS]
    │
    └── tasks/                            # Task folders (committed)
        ├── TEMPLATE/                     # [EXISTS] Template folder
        │   ├── README.md
        │   ├── progress.md
        │   ├── decisions.md
        │   └── subagent-reports/
        │
        └── TASK-XXX/                     # [CREATED BY SCRIPTS]
            ├── STATE.json                # Structured state
            ├── README.md                 # Human description
            ├── research/                 # Research artifacts
            ├── planning/                 # Plans
            ├── context/                  # Loaded context
            └── logs/                     # Execution logs
```

### Git Workflow Integration

**How it works:**

1. **Task Creation:** `/task-new US-001 feat`
   - Creates `.sdlc-workflow/tasks/TASK-001/` with STATE.json
   - Creates branch: `feature/US-001-TASK-001`
   - Commits task folder to branch
   - Updates `.claude/tasks/current.txt` → "TASK-001"

2. **Work on Task:**
   - Make edits → PostToolUse hook updates STATE.json (files_modified)
   - Commit → prepare-commit-msg adds `[TASK-001/US-001]`
   - Commit → post-commit adds to commit-task-map.csv

3. **Switch Tasks (Parallel Workflow):**
   ```bash
   git checkout feature/US-002-TASK-002
   # post-checkout hook extracts TASK-002 from branch name
   # Updates .claude/tasks/current.txt → "TASK-002"
   # Git switches STATE.json automatically (different file on different branch)
   ```

4. **Back to Previous Task:**
   ```bash
   git checkout feature/US-001-TASK-001
   # post-checkout hook extracts TASK-001
   # Updates current.txt → "TASK-001"
   # Git restores original STATE.json
   ```

**Key Insight:** STATE.json is version controlled (in .sdlc-workflow/tasks/), so it travels with the branch. current.txt is local (in .claude/tasks/), so it's just a pointer.

---

## Part 1: Infrastructure Setup

### Task 1.1: Create .claude/tasks/ Directory

**Purpose:** Local state storage (not version controlled)

**Actions:**
```bash
mkdir -p .claude/tasks
```

**Create Files:**

1. `.claude/tasks/current.txt`:
```
none
```

2. `.claude/tasks/commit-task-map.csv`:
```
commit_sha,task_id,commit_message,timestamp
```

3. `.claude/tasks/README.md`:
```markdown
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
```

### Task 1.2: Update .gitignore

**Purpose:** Ensure .claude/tasks/ is not committed

**Action:**
Add to `.gitignore`:
```
# Local task state (not version controlled)
.claude/tasks/current.txt
.claude/tasks/commit-task-map.csv
```

**Note:** Keep .claude/tasks/README.md committed (it's documentation).

### Task 1.3: Verify Git Hooks Installation

**Purpose:** Ensure git hooks are installed and working

**Actions:**
1. Check if `.git/hooks/` has our hooks:
   - prepare-commit-msg
   - post-commit
   - post-checkout

2. If missing, run:
```bash
bash .sdlc-workflow/scripts/install_git_hooks.sh
```

3. Verify hooks are executable:
```bash
chmod +x .git/hooks/prepare-commit-msg
chmod +x .git/hooks/post-commit
chmod +x .git/hooks/post-checkout
```

4. Test post-checkout hook manually:
```bash
# Should update current.txt based on branch name
.git/hooks/post-checkout prev_head new_head 1
```

### Task 1.4: Update post-checkout Hook Path

**Current Issue:** post-checkout hook looks for current.txt in wrong location.

**Current Code:**
```bash
echo "$TASK_ID" > "$PROJECT_ROOT/.claude/tasks/current.txt"
```

**Required:** Verify this path is correct. If hook was written before we decided on .claude/tasks/, update it.

**Expected Behavior:**
- Extract TASK-XXX from branch name
- Write to `.claude/tasks/current.txt`
- If no TASK-XXX in branch name, write "none"

---

## Part 2: Python Scripts Specifications

### General Script Pattern

All scripts should follow this pattern:

```python
#!/usr/bin/env python3
"""
Script purpose and usage.

Usage:
    script_name.py <args>

Examples:
    script_name.py arg1 arg2
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


def main_function(args):
    """Core logic with validation."""
    # Implementation
    pass


def main():
    """CLI entry point."""
    if len(sys.argv) < required_args:
        print(__doc__)
        sys.exit(1)
    try:
        result = main_function(sys.argv[1:])
        if result:
            print(result)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

### Script 2.1: task_update_phase.py

**Purpose:** Update task phase in STATE.json

**Location:** `.claude/skills/docs-stories/scripts/task_update_phase.py`

**Usage:**
```bash
task_update_phase.py <task-id> <phase> <action>
```

**Arguments:**
- `task-id`: TASK-001, TASK-002, etc.
- `phase`: RESEARCH | PLANNING | IMPLEMENTATION | TESTING | VALIDATION | COMPLETED
- `action`: start | complete

**Logic:**
1. Read STATE.json from `.sdlc-workflow/tasks/<task-id>/STATE.json`
2. If action == "start":
   - Update `phase.current` to new phase
   - Add entry to `phase.history`: {phase, started: now(), completed: null}
3. If action == "complete":
   - Find current phase in `phase.history`
   - Set `completed` timestamp
   - Calculate `duration_minutes`
4. Update `timestamps.last_accessed` to now()
5. Write STATE.json atomically (temp file + rename)

**Output:**
```
✓ Phase updated: RESEARCH → start
```

**Error Handling:**
- Task doesn't exist → Exit 1 with message
- STATE.json malformed → Exit 1 with message
- Invalid phase name → Exit 1 with message

---

### Script 2.2: task_add_commit.py

**Purpose:** Add commit entry to STATE.json commits array

**Location:** `.claude/skills/docs-stories/scripts/task_add_commit.py`

**Usage:**
```bash
task_add_commit.py <task-id> <sha> <message> <timestamp> <files-changed>
```

**Arguments:**
- `task-id`: TASK-001
- `sha`: git commit SHA (first 7 chars)
- `message`: commit message (escaped)
- `timestamp`: ISO 8601 format
- `files-changed`: number of files

**Logic:**
1. Read STATE.json
2. Append to `commits` array:
```json
{
  "sha": "abc1234",
  "message": "feat: add login API",
  "timestamp": "2025-11-06T10:00:00Z",
  "files_changed": 3
}
```
3. Update `timestamps.last_accessed`
4. Write STATE.json atomically

**Output:**
```
✓ Commit added: abc1234
```

**Called By:** PostToolUse hook after git commit detected

---

### Script 2.3: task_add_file_modified.py

**Purpose:** Add file to files_modified array (if not already present)

**Location:** `.claude/skills/docs-stories/scripts/task_add_file_modified.py`

**Usage:**
```bash
task_add_file_modified.py <task-id> <file-path>
```

**Arguments:**
- `task-id`: TASK-001
- `file-path`: relative path from repo root

**Logic:**
1. Read STATE.json
2. If file not in `files_modified` array, append it
3. Update `timestamps.last_accessed`
4. Write STATE.json atomically

**Output:**
```
✓ File tracked: apps/server/api/auth.py
```

**Called By:** PostToolUse hook after Edit/Write tool detected

---

### Script 2.4: story_create.py

**Purpose:** Create new user story from template

**Location:** `.claude/skills/docs-stories/scripts/story_create.py`

**Usage:**
```bash
story_create.py <domain> <feature> <scope>
```

**Arguments:**
- `domain`: auth, booking, admin, etc.
- `feature`: login, signup, dashboard, etc.
- `scope`: admin, user, validation, etc.

**Logic:**
1. Scan `.sdlc-workflow/stories/` for existing US-XXX stories
2. Find highest number, increment by 1
3. Generate story ID: `US-{num:03d}-{domain}-{feature}-{scope}`
4. Create directory: `.sdlc-workflow/stories/{domain}/`
5. Read template: `.claude/templates/user-story.md`
6. Replace placeholders:
   - {ID} → US-001-auth-login-admin
   - {domain} → auth
   - {feature} → login
   - {scope} → admin
   - {created_date} → 2025-11-06
7. Write story file: `.sdlc-workflow/stories/{domain}/{story-id}.md`
8. Return story ID

**Output:**
```
US-001-auth-login-admin
```

**Template Placeholders:**
From `.claude/templates/user-story.md`:
- {ID}
- {domain}
- {feature}
- {scope}
- {created_date}

---

### Script 2.5: story_find.py

**Purpose:** Find story by ID or validate story exists

**Location:** `.claude/skills/docs-stories/scripts/story_find.py`

**Usage:**
```bash
story_find.py <story-id>
```

**Arguments:**
- `story-id`: US-001 or US-001-auth-login-admin (flexible)

**Logic:**
1. Normalize story ID (accept US-001 or full US-001-auth-login-admin)
2. Scan `.sdlc-workflow/stories/**/*.md` for matching file
3. If found, return full path
4. If not found, exit 1

**Output:**
```
.sdlc-workflow/stories/auth/US-001-auth-login-admin.md
```

**Error:**
```
Error: Story US-001 not found
```

---

### Script 2.6: task_list.py

**Purpose:** List tasks with filtering and status

**Location:** `.claude/skills/docs-stories/scripts/task_list.py`

**Usage:**
```bash
task_list.py [--status STATUS] [--story STORY-ID]
```

**Arguments:**
- `--status`: Filter by status (not_started | in_progress | completed)
- `--story`: Filter by story ID (US-001)

**Logic:**
1. Scan `.sdlc-workflow/tasks/` for TASK-* directories
2. Read each STATE.json
3. Filter by status if provided
4. Filter by story_id if provided
5. Sort by task_id
6. Display formatted list

**Output:**
```
Tasks:
  TASK-001 (US-001) - in_progress - IMPLEMENTATION
  TASK-002 (US-001) - not_started - PLANNING
  TASK-003 (US-003) - in_progress - TESTING
```

**Format Per Line:**
```
  {task_id} ({story_id}) - {status} - {phase.current}
```

---

## Part 3: Slash Commands Specifications

### Command 3.1: /task-new

**File:** `.claude/commands/task-new.md`

**Purpose:** Create new task for a story

**Frontmatter:**
```yaml
---
description: Create new task for a user story
---
```

**Content:**
```markdown
Create a new task for an existing user story and set up git branch.

**Usage:** `/task-new <story-id> <type>`

**Arguments:**
- `story-id`: User story ID (e.g., US-001)
- `type`: Task type (feat | fix | refactor | test | docs)

**Workflow:**

1. **Validate story exists:**
   ```bash
   story_path=$(python .claude/skills/docs-stories/scripts/story_find.py <story-id>)
   if [ $? -ne 0 ]; then
     echo "❌ Story <story-id> not found"
     exit 1
   fi
   ```

2. **Create task:**
   ```bash
   result=$(python .claude/skills/docs-stories/scripts/task_create.py <story-id> <type>)
   task_id=$(echo "$result" | jq -r '.task_id')
   branch=$(echo "$result" | jq -r '.branch')
   ```

3. **Load story context:**
   - Read story file
   - Display story description and acceptance criteria
   - Show task ID and branch created

4. **Display success:**
   ```
   ✓ Task created: TASK-001
   ✓ Branch created: feature/US-001-TASK-001
   ✓ Branch checked out
   ✓ Current task: TASK-001

   Story: US-001 - Login Flow Validation

   Next steps:
   - Use /task-research to start research phase
   - Or jump to /task-plan if no research needed
   ```

**Error Handling:**
- Story doesn't exist → Show error, list available stories
- Task creation fails → Show error details
```

---

### Command 3.2: /task-research

**File:** `.claude/commands/task-research.md`

**Purpose:** Research phase using Explore agent

**Frontmatter:**
```yaml
---
description: Research phase - analyze existing code and patterns
---
```

**Content:**
```markdown
Research phase: Analyze existing code, find patterns, understand dependencies.

**Usage:** `/task-research`

**Requires:** Active task (current.txt must contain task ID)

**Workflow:**

1. **Validate active task:**
   ```bash
   task_id=$(cat .claude/tasks/current.txt)
   if [ "$task_id" = "none" ]; then
     echo "❌ No active task. Use /task-new first."
     exit 1
   fi
   ```

2. **Update phase:**
   ```bash
   python .claude/skills/docs-stories/scripts/task_update_phase.py $task_id RESEARCH start
   ```

3. **Load story and task context:**
   - Read `.sdlc-workflow/tasks/$task_id/STATE.json`
   - Get story_id from STATE.json
   - Read story file
   - Display what needs to be researched

4. **Spawn Explore agent:**
   ```
   Use Task tool with subagent_type="Explore"

   Prompt for Explore agent:
   "Research the following for TASK-{task_id} ({story_id}):

   Story: {story_description}

   Research Goals:
   - Find existing similar implementations in the codebase
   - Identify relevant files and patterns
   - Understand dependencies and integration points
   - Document any constraints or gotchas

   Use medium thoroughness.

   Save findings to: .sdlc-workflow/tasks/{task_id}/research/findings.md
   ```

5. **After agent completes:**
   ```bash
   python .claude/skills/docs-stories/scripts/task_update_phase.py $task_id RESEARCH complete
   ```

6. **Save agent report:**
   ```bash
   # Save Explore agent's final report to:
   .sdlc-workflow/tasks/$task_id/research/agent-report.md
   ```

7. **Commit research artifacts:**
   ```bash
   git add .sdlc-workflow/tasks/$task_id/research/
   git commit -m "research: complete research phase (TASK-$task_id/US-XXX)"
   ```

8. **Display next steps:**
   ```
   ✓ Research phase complete

   Next: /task-plan to design implementation
   ```

**Error Handling:**
- No active task → Show error, suggest /task-new
- Explore agent fails → Save partial results, allow retry
```

---

### Command 3.3: /task-plan

**File:** `.claude/commands/task-plan.md`

**Purpose:** Planning phase using Plan agent

**Frontmatter:**
```yaml
---
description: Planning phase - design implementation architecture
---
```

**Content:**
```markdown
Planning phase: Design implementation approach using Plan agent.

**Usage:** `/task-plan`

**Requires:** Active task with RESEARCH phase complete (or can skip research)

**Workflow:**

1. **Validate active task:**
   ```bash
   task_id=$(cat .claude/tasks/current.txt)
   if [ "$task_id" = "none" ]; then
     echo "❌ No active task. Use /task-new first."
     exit 1
   fi
   ```

2. **Update phase:**
   ```bash
   python .claude/skills/docs-stories/scripts/task_update_phase.py $task_id PLANNING start
   ```

3. **Load context:**
   - Read STATE.json
   - Read story file
   - Read research findings (if exist)
   - Prepare context for Plan agent

4. **Spawn Plan agent:**
   ```
   Use Task tool with subagent_type="Plan"

   Prompt for Plan agent:
   "Create implementation plan for TASK-{task_id} ({story_id}):

   Story: {story_description}

   Acceptance Criteria:
   {acceptance_criteria}

   Research Findings:
   {research_findings}

   Design:
   - Architecture approach
   - Which files to modify/create
   - Which subagents to use (dev-backend-fastapi, dev-frontend-svelte, both)
   - Implementation steps
   - Testing strategy
   - Complexity estimate

   Save plan to: .sdlc-workflow/tasks/{task_id}/planning/implementation-plan.md
   ```

5. **Present plan to user (ITERATIVE REFINEMENT):**
   - Display Plan agent's proposal
   - Ask user for feedback
   - IF user has concerns:
     - Discuss with user
     - Respawn Plan agent with refinement context
     - LOOP back to step 5
   - IF user approves:
     - Continue to step 6

6. **After plan approved:**
   ```bash
   python .claude/skills/docs-stories/scripts/task_update_phase.py $task_id PLANNING complete
   ```

7. **Save agent report:**
   ```bash
   # Save Plan agent's report to:
   .sdlc-workflow/tasks/$task_id/planning/agent-report.md
   ```

8. **Commit planning artifacts:**
   ```bash
   git add .sdlc-workflow/tasks/$task_id/planning/
   git commit -m "plan: complete planning phase (TASK-$task_id/US-XXX)"
   ```

9. **Display next steps:**
   ```
   ✓ Planning phase complete
   ✓ Plan approved

   Implementation Plan Summary:
   - Files to modify: {count}
   - Subagents needed: {agents}
   - Estimated complexity: {complexity}

   Next: /task-implement to start coding
   ```

**Error Handling:**
- No active task → Show error
- Plan agent fails → Allow retry
- User rejects plan → Allow re-planning
```

---

### Command 3.4: /task-implement

**File:** `.claude/commands/task-implement.md`

**Purpose:** Implementation phase using dev subagents

**Frontmatter:**
```yaml
---
description: Implementation phase - spawn dev agents to write code
---
```

**Content:**
```markdown
Implementation phase: Spawn dev-backend-fastapi and/or dev-frontend-svelte to implement the plan.

**Usage:** `/task-implement`

**Requires:** Active task with PLANNING phase complete

**Workflow:**

1. **Validate active task:**
   ```bash
   task_id=$(cat .claude/tasks/current.txt)
   if [ "$task_id" = "none" ]; then
     echo "❌ No active task. Use /task-new first."
     exit 1
   fi
   ```

2. **Update phase:**
   ```bash
   python .claude/skills/docs-stories/scripts/task_update_phase.py $task_id IMPLEMENTATION start
   ```

3. **Load context:**
   - Read STATE.json
   - Read planning/implementation-plan.md
   - Determine which subagents needed (backend, frontend, both)

4. **Spawn appropriate dev subagent(s):**

   **If backend work needed:**
   ```
   Use Task tool with subagent_type="dev-backend-fastapi"

   Prompt:
   "Implement backend changes for TASK-{task_id}:

   Plan: {implementation_plan}

   Files to modify/create:
   {backend_files_list}

   Requirements:
   - Follow dev-philosophy skill
   - Follow dev-code-quality skill
   - Write tests for all new functionality
   - Add file headers to all modified files
   - Commit work when done

   Save implementation report to:
   .sdlc-workflow/tasks/{task_id}/subagent-reports/backend-report.md
   ```

   **If frontend work needed:**
   ```
   Use Task tool with subagent_type="dev-frontend-svelte"

   Prompt:
   "Implement frontend changes for TASK-{task_id}:

   Plan: {implementation_plan}

   Files to modify/create:
   {frontend_files_list}

   Requirements:
   - Follow dev-philosophy skill
   - Follow dev-code-quality skill
   - Use Svelte 5 runes (no legacy syntax)
   - Create Storybook stories for new components
   - Add file headers to all modified files
   - Commit work when done

   Save implementation report to:
   .sdlc-workflow/tasks/{task_id}/subagent-reports/frontend-report.md
   ```

5. **After subagent(s) complete:**
   - SubagentStop hook validates completeness
   - Hooks have tracked commits and file modifications in STATE.json

6. **Present results to user (FEEDBACK LOOP):**
   - Display what was implemented
   - Show commits made
   - Show files modified
   - IF user wants changes:
     - Discuss requirements
     - Respawn subagent with refinement context
     - LOOP back to step 6
   - IF user approves:
     - Continue to step 7

7. **Update phase:**
   ```bash
   python .claude/skills/docs-stories/scripts/task_update_phase.py $task_id IMPLEMENTATION complete
   ```

8. **Display next steps:**
   ```
   ✓ Implementation complete
   ✓ Commits: {commit_count}
   ✓ Files modified: {file_count}

   Next: /task-test to run tests and validation
   ```

**Error Handling:**
- No active task → Show error
- No plan found → Suggest /task-plan first
- Subagent fails → Display error, allow retry
```

---

## Part 4: STATE.json Format

### Complete Schema

Location: `.sdlc-workflow/tasks/TASK-XXX/STATE.json`

```json
{
  "task_id": "TASK-001",
  "story_id": "US-001-auth-login-admin",
  "task_type": "feat",
  "branch": "feature/US-001-TASK-001",

  "timestamps": {
    "created": "2025-11-06T10:00:00Z",
    "started": "2025-11-06T10:05:00Z",
    "last_accessed": "2025-11-06T14:30:00Z",
    "completed": null
  },

  "phase": {
    "current": "IMPLEMENTATION",
    "history": [
      {
        "phase": "RESEARCH",
        "started": "2025-11-06T10:05:00Z",
        "completed": "2025-11-06T10:45:00Z",
        "duration_minutes": 40
      },
      {
        "phase": "PLANNING",
        "started": "2025-11-06T10:45:00Z",
        "completed": "2025-11-06T11:30:00Z",
        "duration_minutes": 45
      },
      {
        "phase": "IMPLEMENTATION",
        "started": "2025-11-06T11:30:00Z",
        "completed": null
      }
    ]
  },

  "domains": ["backend", "frontend"],
  "agents_used": ["dev-backend-fastapi", "dev-frontend-svelte"],

  "commits": [
    {
      "sha": "abc1234",
      "message": "feat(TASK-001/US-001): Implement login API endpoint",
      "timestamp": "2025-11-06T12:00:00Z",
      "files_changed": 3
    }
  ],

  "tests": {
    "files_created": [],
    "files_modified": [],
    "total_tests": 0,
    "passing": false,
    "coverage_percentage": 0.0,
    "coverage_baseline": 80.0,
    "last_run": null
  },

  "quality_gates": {
    "lint": {"status": "not_run", "last_run": null},
    "type_check": {"status": "not_run", "errors": 0, "last_run": null},
    "security_scan": {"status": "not_run", "vulnerabilities": 0, "last_run": null},
    "acceptance_criteria": {"total": 0, "met": 0, "status": "pending"}
  },

  "files_modified": [
    "apps/server/src/api/auth/login.py",
    "apps/frontend/src/routes/login/+page.svelte"
  ],

  "dependencies": {
    "blocked_by": [],
    "blocks": [],
    "status": "unblocked"
  },

  "status": "in_progress",
  "notes": ""
}
```

### Field Descriptions

**Top Level:**
- `task_id`: Task identifier (TASK-001, TASK-002, etc.)
- `story_id`: Full story ID (US-001-auth-login-admin)
- `task_type`: feat | fix | refactor | test | docs
- `branch`: Git branch name (feature/US-001-TASK-001)

**timestamps:**
- `created`: When task was created (ISO 8601)
- `started`: When work began (first phase start)
- `last_accessed`: Last time STATE.json was updated
- `completed`: When task finished (or null)

**phase:**
- `current`: Current phase name
- `history`: Array of phase transitions with duration tracking

**domains:** Array of domains touched (backend, frontend, infra, etc.)

**agents_used:** Array of subagents spawned (tracked by SubagentStop hook)

**commits:** Array of commits made during task (tracked by post_tool_use hook)

**files_modified:** Array of files changed (tracked by post_tool_use hook)

**status:** not_started | in_progress | completed

---

## Part 5: Testing Plan

### Test 5.1: Infrastructure Setup

**Goal:** Verify directory structure and initialization

**Steps:**
1. Check `.claude/tasks/` exists
2. Check `current.txt` contains "none"
3. Check `commit-task-map.csv` has header row
4. Check git hooks installed in `.git/hooks/`
5. Check `.gitignore` excludes local state files

**Expected:**
```
✓ .claude/tasks/ exists
✓ current.txt initialized to "none"
✓ commit-task-map.csv has header
✓ Git hooks installed
✓ .gitignore updated
```

---

### Test 5.2: Script Functionality

**For each script, test:**

1. **task_update_phase.py:**
```bash
# Create test task manually
mkdir -p .sdlc-workflow/tasks/TASK-TEST
cp .claude/templates/task-state.json .sdlc-workflow/tasks/TASK-TEST/STATE.json

# Test phase update
python .claude/skills/docs-stories/scripts/task_update_phase.py TASK-TEST RESEARCH start

# Verify STATE.json updated
jq '.phase.current' .sdlc-workflow/tasks/TASK-TEST/STATE.json
# Expected: "RESEARCH"
```

2. **story_find.py:**
```bash
# Test with existing story
python .claude/skills/docs-stories/scripts/story_find.py US-001

# Expected: .sdlc-workflow/stories/auth/US-001-auth-login-admin.md
```

3. **task_list.py:**
```bash
# After creating test task
python .claude/skills/docs-stories/scripts/task_list.py

# Expected: List showing TASK-TEST
```

---

### Test 5.3: Git Workflow Integration

**Goal:** Verify hooks update current.txt correctly

**Steps:**

1. **Create task with /task-new:**
```bash
# Use command to create TASK-001
/task-new US-001 feat

# Verify:
# - .sdlc-workflow/tasks/TASK-001/ exists
# - STATE.json created
# - Branch created: feature/US-001-TASK-001
# - current.txt contains "TASK-001"
```

2. **Test branch switching:**
```bash
# Create second task
/task-new US-001 feat  # Creates TASK-002

# Switch back to first task
git checkout feature/US-001-TASK-001

# Verify:
cat .claude/tasks/current.txt
# Expected: TASK-001
```

3. **Test commit tracking:**
```bash
# Make a change
echo "test" > test.txt
git add test.txt
git commit -m "test: verify commit tracking"

# Verify:
# - Commit message has [TASK-001/US-001] added
# - commit-task-map.csv has new entry
# - STATE.json commits array has new entry
```

---

### Test 5.4: End-to-End Workflow

**Goal:** Complete workflow for a dummy task

**Steps:**

1. Create task: `/task-new US-001 feat`
2. Research: `/task-research` (Explore agent runs)
3. Plan: `/task-plan` (Plan agent runs)
4. Implement: `/task-implement` (Dev agent runs)
5. Verify STATE.json shows all phases complete
6. Verify commits tracked
7. Verify files tracked

**Expected Final STATE.json:**
```json
{
  "task_id": "TASK-001",
  "phase": {
    "current": "IMPLEMENTATION",
    "history": [
      {"phase": "RESEARCH", "completed": "..."},
      {"phase": "PLANNING", "completed": "..."},
      {"phase": "IMPLEMENTATION", "started": "..."}
    ]
  },
  "commits": [
    {"sha": "...", "message": "research: ..."},
    {"sha": "...", "message": "plan: ..."},
    {"sha": "...", "message": "feat: ..."}
  ],
  "files_modified": [...],
  "agents_used": ["Explore", "Plan", "dev-backend-fastapi"]
}
```

---

## Part 6: Implementation Checklist

### Phase 1: Infrastructure (30 min)
- [ ] Create `.claude/tasks/` directory
- [ ] Create `current.txt` with "none"
- [ ] Create `commit-task-map.csv` with header
- [ ] Create `.claude/tasks/README.md`
- [ ] Update `.gitignore`
- [ ] Verify git hooks installed
- [ ] Test post-checkout hook manually

### Phase 2: Python Scripts (2-3 hours)
- [ ] Implement `task_update_phase.py`
- [ ] Implement `task_add_commit.py`
- [ ] Implement `task_add_file_modified.py`
- [ ] Implement `story_create.py`
- [ ] Implement `story_find.py`
- [ ] Implement `task_list.py`
- [ ] Test each script independently

### Phase 3: Slash Commands (2-3 hours)
- [ ] Implement `/task-new.md`
- [ ] Implement `/task-research.md`
- [ ] Implement `/task-plan.md`
- [ ] Implement `/task-implement.md`
- [ ] Test each command independently

### Phase 4: Integration Testing (1 hour)
- [ ] Test infrastructure setup
- [ ] Test script functionality
- [ ] Test git workflow integration
- [ ] Test end-to-end workflow
- [ ] Verify parallel workflow (multiple branches)

### Phase 5: Documentation (30 min)
- [ ] Create implementation summary
- [ ] Document any deviations from spec
- [ ] List known issues or limitations
- [ ] Provide usage examples

---

## Success Criteria

✅ **Infrastructure:**
- .claude/tasks/ directory created
- Initialization files created
- Git hooks installed and working
- .gitignore updated

✅ **Scripts:**
- All 6 scripts implemented and tested
- Scripts follow consistent pattern
- Error handling implemented
- Integration points working

✅ **Commands:**
- All 4 commands implemented
- Commands call scripts correctly
- Commands spawn agents correctly
- Error handling implemented

✅ **Integration:**
- Git branch name → current.txt works
- Hooks update STATE.json correctly
- Parallel workflow works (multiple branches)
- STATE.json version controlled correctly

✅ **Testing:**
- All tests pass
- End-to-end workflow complete
- Documentation created

---

## Notes for devops-infra Subagent

**Core Skills:**
Remember to use:
- `@.claude/skills/dev-philosophy/` - Development philosophy
- `@.claude/skills/dev-code-quality/` - Code quality standards

**Code Quality:**
- Follow Python PEP 8 style
- Use type hints where appropriate
- Add docstrings to all functions
- Handle errors gracefully
- Use atomic file operations (temp + rename)

**Testing:**
- Test scripts independently before integration
- Verify git hooks behavior manually
- Test parallel workflow with multiple branches
- Document any edge cases discovered

**Integration:**
- Scripts must be executable (`chmod +x`)
- Commands must have valid YAML frontmatter
- STATE.json must be valid JSON always
- Hooks must fail-open (don't block on errors)

**Documentation:**
- Create implementation summary when done
- Document any spec deviations
- List known limitations
- Provide usage examples

---

**End of Specification**
