# SDLC Plan v2 - Production Quality with Python Scripts & Full Hook Integration

**Created:** 2025-11-01 12:19
**Status:** Ready for Implementation
**Approach:** Production-quality SDLC with comprehensive automation
**Version:** 2.0 (Major revision from original)

---

## Executive Summary

### Core Changes from Original Plan

This v2 plan addresses critical gaps identified in the original plan:

1. **Scripts:** All 31 scripts converted from Bash to **Python** (following claude-skill-manager patterns)
2. **Hooks:** Added 5 **Claude Code CLI hooks** (missing from original) + kept 3 git hooks
3. **Structure:** Clear separation of **permanent parts** (rules, skills, commands, scripts)
4. **Enforcement:** **Hard enforcement** of agent boundaries via PreToolUse hook
5. **Automation:** **Comprehensive validation** at every workflow step

### Key Principles

- **Story ≠ Task:** Stories are persistent requirements, tasks are ephemeral work sessions
- **ONE skill:** `docs-stories` contains all SDLC documentation conventions
- **Python scripts:** All 31 scripts in Python for better JSON handling and cross-platform support
- **Dual hooks:** Git hooks (3) for git operations + Claude CLI hooks (5) for SDLC validation
- **Agent enforcement:** PreToolUse hook BLOCKS inappropriate agent usage
- **Progressive disclosure:** Brief mandatory rule → detailed skill → deep-dive references

### Related Documents

This plan references three companion documents in `.sdlc-workflow/plan/walkthrough/`:

1. **20251101-1219-review-hooks-comparison-specification.md**

   - Complete hook specifications (git + Claude CLI)
   - All hook scripts with full code
   - Configuration examples

2. **20251101-1219-diagram-complete-workflow.md**

   - Visual workflow diagrams (end-to-end)
   - Agent spawning decision trees
   - Data flow and context passing
   - Hook trigger timelines

3. **20251101-1219-mapping-agents-skills-enforcement.md**
   - Agent-skill mandatory mappings
   - Directory ownership table
   - PreToolUse hook enforcement
   - CLAUDE.md updates for enforcement

**Read those documents for details.** This plan focuses on implementation structure and phases.

---

## 1. Changes from Original Plan

### 1.1 Major Changes

| Aspect                  | Original Plan           | v2 Plan                                  | Reason                                                                   |
| ----------------------- | ----------------------- | ---------------------------------------- | ------------------------------------------------------------------------ |
| **Scripts**             | 31 Bash scripts         | 33 Python scripts (+ 1 bash)             | Better JSON handling, cross-platform, type hints, easier testing         |
| **Hooks**               | 3 git hooks only        | 3 git + 5 Claude CLI hooks               | Original missed Claude CLI hooks entirely - critical for SDLC automation |
| **Agent enforcement**   | Mentioned, not enforced | PreToolUse hook BLOCKS                   | Hard enforcement, not suggestions                                        |
| **Permanent structure** | Single plan file        | Split into rules/skills/commands/scripts | Follows claude-code-config.md principles                                 |
| **Main LLM role**       | Could edit code         | Orchestration ONLY                       | Clean separation of concerns                                             |
| **Validation**          | Manual                  | Automated hooks at every step            | Reduces cognitive load, ensures completeness                             |
| **Commit format**       | Manual task IDs         | Conventional commits auto-formatted      | Enables changelog automation, semantic versioning                        |
| **CI enforcement**      | None                    | GitHub Actions validates all             | Immutable compliance, prevents bypass                                    |
| **Ownership**           | Centralized table only  | Table + declarative README.md            | Discoverable, visible, self-documenting                                  |
| **Test validation**     | File existence          | Coverage delta blocking                  | Ensures behavior proven, not just file added                             |
| **Agent workflow**      | Linear execution        | Feedback loops for refinement            | Planning and implementation can be iterative                             |

### 1.2 Hook System Comparison

**Original Plan:** Only git hooks

- post-checkout (auto-detect task switches)
- prepare-commit-msg (add task/story IDs)
- post-commit (track commits)

**v2 Plan:** Git hooks + Claude CLI hooks

- **Git hooks (3):** Same as original, for git-level automation
- **Claude CLI hooks (5 new):**
  - SessionStart: Load task context on every session
  - UserPromptSubmit: Validate command prerequisites
  - PreToolUse: BLOCK inappropriate agent usage
  - PostToolUse: Update STATE.json after operations
  - SubagentStop: Validate subagent completeness

**Why both?**

- Git hooks: Fast, deterministic, git-specific operations
- Claude CLI hooks: High-level, context-aware, SDLC validation
- They complement each other - see hooks document for full comparison

### 1.3 Python vs Bash Scripts

**Why Python for all scripts:**

```python
# Example: task_update_state.py (Python)
#!/usr/bin/env python3
import json
from pathlib import Path

def update_state(task_id, field, value):
    """Update STATE.json field atomically"""
    state_file = Path(f".claude/tasks/{task_id}/STATE.json")

    # Validation
    if not state_file.exists():
        raise FileNotFoundError(f"STATE.json not found for {task_id}")

    # Atomic update
    state = json.loads(state_file.read_text())
    # Handle nested fields (e.g., "timestamps.last_accessed")
    keys = field.split('.')
    target = state
    for key in keys[:-1]:
        target = target.setdefault(key, {})
    target[keys[-1]] = value

    # Write atomically
    temp_file = state_file.with_suffix('.tmp')
    temp_file.write_text(json.dumps(state, indent=2))
    temp_file.replace(state_file)

    return state
```

**Benefits:**

- Native JSON support (no jq dependency)
- Type hints and validation
- Cross-platform (Windows, macOS, Linux)
- Easier testing and mocking
- Better error messages
- Path library for file operations
- Standard library has everything we need

Compared to Bash:

```bash
# Bash equivalent - fragile and platform-specific
jq ".timestamps.last_accessed = \"$timestamp\"" \
   .claude/tasks/$task_id/STATE.json > temp.json
mv temp.json .claude/tasks/$task_id/STATE.json
```

---

## 2. Permanent Parts Structure

### 2.1 What Goes Where

Following claude-code-config.md recommendations and architecture analysis:

```
bestays-monorepo/
├── .claude/
│   ├── rules/                          # PERMANENT - Mandatory governance
│   │   └── sdlc-workflow.md           # < 1k words, loaded every session
│   │
│   ├── skills/                         # PERMANENT - Technical knowledge
│   │   └── docs-stories/              # The ONE skill for SDLC
│   │       ├── SKILL.md                # < 5k words, main documentation
│   │       ├── references/             # Deep-dive docs (progressive disclosure)
│   │       │   ├── state-management.md
│   │       │   ├── commit-conventions.md
│   │       │   ├── hooks-integration.md
│   │       │   └── script-reference.md
│   │       └── scripts/                # 31 Python scripts
│   │           ├── task_*.py          # Task management (10 scripts)
│   │           ├── story_*.py         # Story management (5 scripts)
│   │           ├── git_*.py           # Git integration (5 scripts)
│   │           ├── validation_*.py    # Quality gates (3 scripts)
│   │           └── ...                 # Others
│   │
│   ├── commands/                       # PERMANENT - Workflow triggers
│   │   ├── story-new.md               # < 50 lines each
│   │   ├── task-new.md
│   │   └── ...                        # 18 total commands
│   │
│   ├── hooks/                          # PERMANENT - Claude CLI hooks
│   │   ├── session_start.py
│   │   ├── validate_command.py
│   │   ├── pre_tool_use.py
│   │   ├── post_tool_use.py
│   │   └── subagent_stop.py
│   │
│   ├── git-hooks/                      # PERMANENT - Git hook templates
│   │   ├── prepare-commit-msg
│   │   ├── post-commit
│   │   └── post-checkout
│   │
│   ├── settings.json                   # PERMANENT - Hook configuration
│   │
│   └── tasks/                          # DYNAMIC - Active and archived tasks
│       ├── current.txt                 # Current active task ID
│       ├── TASK-001/                   # Active task
│       └── archive/                    # Completed tasks
│
└── .sdlc-workflow/                       # Project knowledge (separate from .claude/)
    ├── stories/                        # User stories
    │   ├── auth/
    │   │   └── login.md                # US-001-auth-login-admin
    │   └── ...
    │
    ├── plan/                           # TEMPORARY - Planning documents
    │   ├── 20251101-1219-sdlc-todo-plan-git-userstories-v2.md  # This file
    │   └── walkthrough/                # Implementation walkthrough docs
    │
    └── conventions/                    # Project-specific patterns
        ├── backend/
        └── frontend/
```

### 2.2 Progressive Disclosure Pattern

```
User needs info about SDLC workflow
  │
  ├─→ LEVEL 1: .claude/rules/sdlc-workflow.md (< 1k words)
  │     • Loaded every session (mandatory)
  │     • High-level overview
  │     • Story vs Task distinction
  │     • When to use workflow
  │     • References docs-stories skill for details
  │
  ├─→ LEVEL 2: .claude/skills/docs-stories/SKILL.md (< 5k words)
  │     • Loaded when skill invoked
  │     • Command reference (all 18 commands)
  │     • STATE.json structure overview
  │     • Script usage patterns
  │     • References references/ for deep-dive
  │
  └─→ LEVEL 3: .claude/skills/docs-stories/references/*.md
        • Loaded when specific detail needed
        • state-management.md: Deep dive on STATE.json
        • commit-conventions.md: All commit format examples
        • hooks-integration.md: Hook configurations
        • script-reference.md: All 31 scripts documented
```

**Why this structure:**

- Mandatory knowledge is brief (< 1k words)
- Detailed knowledge available when needed
- No duplication across levels
- Each level references next level
- Follows claude-code-config.md principles

---

## 3. Complete Script Architecture (31 Python Scripts)

All scripts follow this pattern:

```python
#!/usr/bin/env python3
"""
Script purpose and description

Usage:
    script_name.py <args>

Examples:
    script_name.py arg1 arg2
"""
import sys
from pathlib import Path
import json
from datetime import datetime

def main_function(args):
    """Actual logic with validation and error handling"""
    # 1. Validate inputs
    # 2. Perform operation
    # 3. Return result or raise exception
    pass

def main():
    """CLI entry point"""
    if len(sys.argv) < required_args:
        print(__doc__)
        sys.exit(1)

    try:
        result = main_function(sys.argv[1:])
        print(result)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 3.1 Task Management Scripts (10 scripts)

**File:** `.claude/skills/docs-stories/scripts/task_*.py`

1. **task_create.py**

```python
task_create.py <story-id> <type>

Creates new task:
- Generates TASK-XXX ID (sequential)
- Creates .claude/tasks/TASK-XXX/ directory
- Creates STATE.json from template
- Creates subdirectories (research/, planning/, context/, logs/)
- Creates git branch: <type>/TASK-XXX-<story-id>
- Updates current.txt → TASK-XXX
- Returns task ID

Example:
  task_create.py US-001 feat
  → Creates TASK-001, branch feat/TASK-001-US-001-auth-login-admin
```

2. **task_get_current.py**

```python
task_get_current.py

Returns current task ID from current.txt
Returns "none" if no active task

Example:
  task_get_current.py
  → TASK-001
```

3. **task_set_current.py**

```python
task_set_current.py <task-id>

Updates current.txt with given task ID
Validates task exists

Example:
  task_set_current.py TASK-001
```

4. **task_update_state.py**

```python
task_update_state.py <task-id> <field> <value>

Updates STATE.json field (supports nested fields with dot notation)
Writes atomically (temp file + rename)

Examples:
  task_update_state.py TASK-001 status completed
  task_update_state.py TASK-001 timestamps.completed "2025-11-01T12:00:00Z"
  task_update_state.py TASK-001 phase.current IMPLEMENTATION
```

5. **task_update_phase.py**

```python
task_update_phase.py <task-id> <phase> [status]

Updates current phase and adds to phase history
Calculates duration if completing previous phase
status: start | complete (default: start)

Examples:
  task_update_phase.py TASK-001 IMPLEMENTATION start
  task_update_phase.py TASK-001 RESEARCH complete
```

6. **task_get_status.py**

```python
task_get_status.py <task-id>

Displays comprehensive task status:
- Task ID, Story ID, Branch
- Current phase + duration
- Commits count
- Test status
- Quality gates status
- Files modified count
- Next suggested action

Example output:
  Task: TASK-001
  Story: US-001-auth-login-admin
  Phase: IMPLEMENTATION (3h 20m)
  Commits: 5
  Tests: 18 passing, 95% coverage
  Quality: All gates passed
  Next: /task-validate
```

7. **task_list.py**

```python
task_list.py [--active|--archived|--all] [--story US-XXX]

Lists tasks with filtering
Displays: ID, story, status, phase, last accessed

Examples:
  task_list.py --active
  task_list.py --story US-001
  task_list.py --all
```

8. **task_list_by_story.py**

```python
task_list_by_story.py <story-id>

Lists all tasks (active + archived) for a story

Example:
  task_list_by_story.py US-001
  → TASK-001 (completed)
  → TASK-015 (active - bug fix)
```

9. **task_complete.py**

```python
task_complete.py <task-id> [--archive]

Completes task:
- Runs final validation
- Generates retrospective (calls git_stats.py)
- Updates STATE.json (status: completed, timestamps.completed)
- Optionally archives to archive/TASK-XXX/
- Clears current.txt → "none"

Example:
  task_complete.py TASK-001 --archive
```

10. **task_archive.py**

```python
task_archive.py <task-id>

Moves task to archive/:
- Moves TASK-XXX/ → archive/TASK-XXX/
- Preserves all history
- Clears current.txt if this was active task

Example:
  task_archive.py TASK-001
```

### 3.2 Task Data Scripts (5 scripts)

11. **task_add_commit.py**

```python
task_add_commit.py <task-id> <sha> <message> <timestamp> <files-changed>

Adds commit to STATE.json commits array

Called by: PostToolUse hook

Example:
  task_add_commit.py TASK-001 abc123 "feat: add login" "2025-11-01T12:00:00Z" 3
```

12. **task_add_file_modified.py**

```python
task_add_file_modified.py <task-id> <file-path>

Adds file to files_modified array (if not already present)

Called by: PostToolUse hook

Example:
  task_add_file_modified.py TASK-001 apps/server/src/auth/routes.py
```

13. **task_update_tests.py**

```python
task_update_tests.py <task-id> --files <files> --total <n> --passing --coverage <pct>

Updates STATE.json tests section

Called by: task-test command after running tests

Example:
  task_update_tests.py TASK-001 \
    --files "test_auth.py,test_login.py" \
    --total 18 \
    --passing \
    --coverage 95.5
```

14. **task_update_quality.py**

```python
task_update_quality.py <task-id> <gate> <status> [--errors <n>]

Updates quality_gates section
gate: lint | type_check | security | acceptance_criteria
status: passed | failed

Examples:
  task_update_quality.py TASK-001 lint passed
  task_update_quality.py TASK-001 type_check failed --errors 3
```

15. **task_validate_state.py**

```python
task_validate_state.py <task-id>

Validates STATE.json completeness and structure
Checks required fields, data types, etc.
Returns validation errors or success

Example:
  task_validate_state.py TASK-001
  → ✓ STATE.json valid
```

### 3.3 Story Management Scripts (5 scripts)

16. **story_create.py**

```python
story_create.py <domain> <feature> <scope>

Creates new story:
- Generates US-XXX ID (sequential)
- Creates .sdlc-workflow/stories/<domain>/<feature>.md from template
- Sets status: READY
- Returns story ID

Example:
  story_create.py auth login admin
  → US-001-auth-login-admin created
```

17. **story_find.py**

```python
story_find.py <query>

Finds stories by ID or keyword search
Searches in story files

Examples:
  story_find.py US-001
  story_find.py "login"
```

18. **story_list.py**

```python
story_list.py [--domain <domain>] [--status <status>]

Lists all stories with filtering
Displays: ID, domain, status, task count

Examples:
  story_list.py
  story_list.py --domain auth
  story_list.py --status READY
```

19. **story_update_status.py**

```python
story_update_status.py <story-id> <status>

Updates story status in story file
status: READY | IN_PROGRESS | COMPLETED | BLOCKED

Example:
  story_update_status.py US-001 COMPLETED
```

20. **story_validate.py**

```python
story_validate.py <story-id>

Validates story completeness:
- Has description
- Has acceptance criteria
- Has domain
- Proper format

Example:
  story_validate.py US-001
  → ✓ Story complete
```

### 3.4 Git Integration Scripts (5 scripts)

21. **git_commit_validate.py**

```python
git_commit_validate.py <message>

Validates commit message format:
- Follows conventional commits
- Has task/story IDs (type(TASK-XXX/US-XXX): message)

Example:
  git_commit_validate.py "feat(TASK-001/US-001): add login"
  → ✓ Valid
```

22. **git_story_history.py**

```python
git_story_history.py <story-id>

Gets all commits across all tasks for a story
Uses git log + grep for story ID

Example:
  git_story_history.py US-001
  → Lists all commits for US-001 across TASK-001, TASK-015, etc.
```

23. **git_story_stats.py**

```python
git_story_stats.py <story-id>

Generates statistics for story:
- Total commits
- Files changed
- Lines added/removed
- Time spent (from task STATE.json)
- Contributors

Example:
  git_story_stats.py US-001
  → JSON output with stats
```

24. **git_task_stats.py**

```python
git_task_stats.py <task-id>

Generates statistics for single task:
- Commit count
- Files changed
- Lines added/removed
- Time spent per phase
- Used for retrospective

Example:
  git_task_stats.py TASK-001
  → JSON output for retrospective.md
```

25. **git_research_patterns.py**

```python
git_research_patterns.py <keyword> [--domain <domain>]

Searches git history for similar implementations
Finds stories/commits that match keyword

Example:
  git_research_patterns.py "authentication" --domain auth
  → US-042, US-067 implemented auth patterns
```

### 3.5 Quality & Validation Scripts (3 scripts)

26. **lint_check.py**

```python
lint_check.py [backend|frontend]

Runs linting:
- backend: ruff check apps/server/
- frontend: eslint apps/frontend/
- Updates STATE.json quality_gates

Example:
  lint_check.py backend
  → Runs ruff, updates STATE.json
```

27. **type_check.py**

```python
type_check.py [backend|frontend]

Runs type checking:
- backend: mypy apps/server/
- frontend: tsc --noEmit

Example:
  type_check.py backend
```

28. **security_scan.py**

```python
security_scan.py

Runs security scans:
- backend: bandit apps/server/
- frontend: npm audit

Example:
  security_scan.py
  → Scans all, updates STATE.json
```

29. **acceptance_criteria_check.py**

```python
acceptance_criteria_check.py <task-id>

Checks if acceptance criteria met:
- Reads story acceptance criteria
- Checks STATE.json commits, tests, files
- Validates each criterion

Example:
  acceptance_criteria_check.py TASK-001
  → 4/4 criteria met ✓
```

30. **task_validate_quality.py**

```python
task_validate_quality.py <task-id> [--lint-only] [--criteria-only]

Master validation script:
- Runs all quality gates (lint, type, security, criteria)
- Updates STATE.json quality_gates
- Returns pass/fail

Example:
  task_validate_quality.py TASK-001
  → All gates passed ✓
```

### 3.6 Session Scripts (1 script - others are hooks)

31. **session_context_load.py**

```python
session_context_load.py <task-id>

Loads and displays task context:
- Task info
- Current phase
- Recent commits
- Next suggested action

Called by: SessionStart hook and /task-resume

Example:
  session_context_load.py TASK-001
  → Displays rich context
```

### 3.7 New Additions (2 scripts)

32. **coverage_delta_check.py**

```python
coverage_delta_check.py --backend <coverage-file> --frontend <coverage-file>

Validates test coverage hasn't decreased:
- Compares current coverage to baseline
- Checks coverage delta (change from baseline)
- Blocks if coverage dropped
- Reports coverage percentage per domain

Called by: CI pipeline and SubagentStop hook

Example:
  coverage_delta_check.py \
    --backend apps/server/coverage.json \
    --frontend apps/frontend/coverage/coverage-summary.json

  Output:
    Backend: 94.5% (baseline: 80.0%, delta: +14.5%) ✓
    Frontend: 92.0% (baseline: 75.0%, delta: +17.0%) ✓
    Overall: PASS

Baseline Storage:
  - Stored in STATE.json: tests.coverage_baseline
  - Updated on task completion
  - Default: 80% if not set
```

33. **get_agent_for_dir.sh**

```bash
get_agent_for_dir.sh <file-path>

Determines agent owner for a file by walking up directory tree:
- Reads YAML frontmatter from README.md files
- Extracts 'owner:' field
- Fails if no owner found before repo root
- Never escapes repository boundary (security)

Called by: PreToolUse hook and CI pipeline

Example:
  get_agent_for_dir.sh apps/server/src/auth/routes.py
  → dev-backend

  get_agent_for_dir.sh apps/frontend/src/routes/admin/
  → dev-frontend

  get_agent_for_dir.sh orphan/file.py
  → ❌ Error: No owner found

Note: This is the ONLY bash script (besides git hooks).
      All others are Python for consistency.
```

---

## 4. Complete Command Structure (18 Commands)

All commands in `.claude/commands/` are < 50 lines, just workflow logic.

### 4.1 Story Commands (4)

**story-new.md:**

```markdown
---
description: Create a new user story
---

Create a new user story by collecting domain, feature, and scope.

**Workflow:**

1. Ask user for domain, feature, scope (interactive)
2. Call `python .claude/skills/docs-stories/scripts/story_create.py <domain> <feature> <scope>`
3. Display created story ID
4. Show story file path
5. Suggest: "Use /task-new <story-id> to start working on it"
```

**story-list.md:** Lists all stories (calls story_list.py)
**story-view.md:** Shows story + associated tasks (calls story_find.py + task_list_by_story.py)
**story-update.md:** Updates story status (calls story_update_status.py)

### 4.2 Task Management Commands (5)

**task-new.md:**

```markdown
---
description: Create new task for a story
---

Create a new task for an existing story.

**Usage:** `/task-new <story-id> [type]`

**Workflow:**

1. Validate story exists (calls story_find.py)
2. Call task_create.py <story-id> <type>
3. Load story context
4. Display task created info
5. Suggest next step: "/task-research to start"
```

**task-list.md:** Lists tasks with filtering
**task-resume.md:** Resumes existing task (loads context, switches branch)
**task-switch.md:** Switches between tasks
**task-status.md:** Shows current task status

### 4.3 SDLC Phase Commands (5)

**task-research.md:**

```markdown
---
description: Research phase - analyze existing code and patterns
---

Research phase using Explore agent to find patterns and dependencies.

**Usage:** `/task-research [--patterns-only] [--analyze-only]`

**Requires:** Active task

**Workflow:**

1. Validate active task exists
2. Update phase: task_update_phase.py <task-id> RESEARCH start
3. Load story context
4. Spawn Explore agent with thoroughness: medium
5. Agent searches codebase and git history
6. Save results to TASK-XXX/research/
7. Update phase: task_update_phase.py <task-id> RESEARCH complete
8. Suggest: "/task-plan to design architecture"
```

**task-plan.md:** Planning with Plan agent (with feedback loop)

```markdown
---
description: Planning phase - design implementation architecture
---

Planning phase using Plan agent to create implementation strategy.

**Usage:** `/task-plan [--estimate]`

**Requires:** Active task with research completed

**Workflow (with Iterative Refinement):**

1. Validate active task exists
2. Update phase: task_update_phase.py <task-id> PLANNING start
3. Load context (story + research findings)
4. Spawn Plan agent to create initial plan
5. **Agent returns draft plan**
6. **Main LLM presents plan to user:**
   - Architecture approach
   - Agent assignments (dev-backend/dev-frontend/both)
   - Complexity estimate
   - Implementation steps
7. **User reviews and provides feedback**
   - IF user has questions/concerns:
     - Main LLM discusses with user
     - Respawns Plan agent with refinement context
     - LOOP back to step 6 (iterative refinement)
   - IF user approves:
     - Continue to step 8
8. Save approved plan to TASK-XXX/planning/implementation-plan.md
9. Update phase: task_update_phase.py <task-id> PLANNING complete
10. Suggest: "/task-implement to start coding"

**Note on Feedback Loops:**
Planning agent may be called multiple times in a single planning phase
to refine the approach based on user feedback. This ensures the plan
is well-understood and approved before implementation begins.
```

**task-implement.md:** Implementation (spawns dev-backend/dev-frontend/both, with post-job discussion)

```markdown
Note: Implementation commands also support feedback loops.
After agent completes work, main LLM presents results to user
for review. If changes needed, agent can be respawned with
refinement context. This applies to both dev-backend and
dev-frontend agents.
```

**task-test.md:** Testing (runs tests, may spawn agents to create tests)
**task-validate.md:** Quality validation (runs all quality gates)

### 4.4 Completion & Utility (4)

**task-complete.md:** Completes and archives task
**research-find-patterns.md:** Git pattern search utility
**research-analyze-code.md:** Code analysis utility
**research-git-history.md:** Git history for story

---

## 5. STATE.json Structure (Complete)

**File:** `.claude/tasks/TASK-001/STATE.json`

```json
{
  "task_id": "TASK-001",
  "story_id": "US-001-auth-login-admin",
  "task_type": "feat",
  "branch": "feat/TASK-001-US-001-auth-login-admin",

  "timestamps": {
    "created": "2025-11-01T10:00:00Z",
    "started": "2025-11-01T10:05:00Z",
    "last_accessed": "2025-11-01T14:30:00Z",
    "completed": null
  },

  "phase": {
    "current": "IMPLEMENTATION",
    "history": [
      {
        "phase": "RESEARCH",
        "started": "2025-11-01T10:05:00Z",
        "completed": "2025-11-01T10:45:00Z",
        "duration_minutes": 40
      },
      {
        "phase": "PLANNING",
        "started": "2025-11-01T10:45:00Z",
        "completed": "2025-11-01T11:30:00Z",
        "duration_minutes": 45
      },
      {
        "phase": "IMPLEMENTATION",
        "started": "2025-11-01T11:30:00Z",
        "completed": null
      }
    ]
  },

  "domains": ["backend", "frontend"],
  "agents_used": ["dev-backend", "dev-frontend"],

  "commits": [
    {
      "sha": "abc123",
      "message": "feat(TASK-001/US-001): Implement login API endpoint",
      "timestamp": "2025-11-01T12:00:00Z",
      "files_changed": 3
    }
  ],

  "tests": {
    "files_created": ["test_login_api.py", "test_login_ui.spec.ts"],
    "files_modified": ["test_auth.py"],
    "total_tests": 18,
    "passing": true,
    "coverage_percentage": 95.5,
    "last_run": "2025-11-01T14:00:00Z"
  },

  "quality_gates": {
    "lint": {
      "status": "passed",
      "last_run": "2025-11-01T14:15:00Z"
    },
    "type_check": {
      "status": "passed",
      "errors": 0,
      "last_run": "2025-11-01T14:16:00Z"
    },
    "security_scan": {
      "status": "passed",
      "vulnerabilities": 0,
      "last_run": "2025-11-01T14:17:00Z"
    },
    "acceptance_criteria": {
      "total": 4,
      "met": 4,
      "status": "complete"
    }
  },

  "files_modified": [
    "apps/server/src/api/auth/login.py",
    "apps/server/src/middleware/rate_limit.py",
    "apps/frontend/src/routes/admin/login/+page.svelte",
    "apps/frontend/src/lib/api/auth.ts"
  ],

  "dependencies": {
    "blocked_by": [],
    "blocks": ["TASK-005"],
    "status": "unblocked"
  },

  "status": "in_progress",
  "notes": "Rate limiting working correctly. Frontend integration pending."
}
```

---

## 6. Implementation Phases

### Phase 1: Foundation (Week 1, 8-10 hours)

**1.1 Permanent Rule File**

- [ ] Create `.claude/rules/sdlc-workflow.md` (< 1k words)
- [ ] Story vs Task distinction
- [ ] Phase definitions
- [ ] When to use workflow
- [ ] Reference to docs-stories skill

**1.2 Skill Structure**

- [ ] Create `.claude/skills/docs-stories/SKILL.md` (< 5k words)
- [ ] Create `.claude/skills/docs-stories/references/`
  - [ ] state-management.md
  - [ ] commit-conventions.md
  - [ ] hooks-integration.md
  - [ ] script-reference.md

**1.3 Templates**

- [ ] Create `.claude/templates/user-story.md` (~30 lines)
- [ ] Create `.claude/templates/task-state.json`
- [ ] Create `.claude/templates/app-readme.md` (with owner frontmatter)

**1.4 README.md Ownership Setup**

- [ ] Add YAML frontmatter to `apps/server/README.md` (owner: dev-backend)
- [ ] Add YAML frontmatter to `apps/frontend/README.md` (owner: dev-frontend)
- [ ] Add YAML frontmatter to `docker/README.md` (owner: devops-infra)
- [ ] Create `get_agent_for_dir.sh` script
- [ ] Test ownership resolution for all directories

**Deliverables:**

- Permanent structure created
- All documentation locations defined
- Templates ready
- README.md ownership configured

---

### Phase 2: Python Scripts (Week 1-2, 10-12 hours)

**2.1 Task Management Scripts (10 scripts)**

- [ ] task_create.py
- [ ] task_get_current.py
- [ ] task_set_current.py
- [ ] task_update_state.py
- [ ] task_update_phase.py
- [ ] task_get_status.py
- [ ] task_list.py
- [ ] task_list_by_story.py
- [ ] task_complete.py
- [ ] task_archive.py

**2.2 Task Data Scripts (5 scripts)**

- [ ] task_add_commit.py
- [ ] task_add_file_modified.py
- [ ] task_update_tests.py
- [ ] task_update_quality.py
- [ ] task_validate_state.py

**2.3 Story Scripts (5 scripts)**

- [ ] story_create.py
- [ ] story_find.py
- [ ] story_list.py
- [ ] story_update_status.py
- [ ] story_validate.py

**2.4 Git Scripts (5 scripts)**

- [ ] git_commit_validate.py
- [ ] git_story_history.py
- [ ] git_story_stats.py
- [ ] git_task_stats.py
- [ ] git_research_patterns.py

**2.5 Quality Scripts (3 scripts)**

- [ ] lint_check.py
- [ ] type_check.py
- [ ] security_scan.py

**2.6 Validation Scripts (2 scripts)**

- [ ] acceptance_criteria_check.py
- [ ] task_validate_quality.py

**2.7 Session Script (1 script)**

- [ ] session_context_load.py

**2.8 New Additions (2 scripts)**

- [ ] coverage_delta_check.py (Python)
- [ ] get_agent_for_dir.sh (Bash - special case)

**Testing:**

- [ ] Test each script independently
- [ ] Create test fixtures (sample STATE.json, etc.)
- [ ] Validate JSON operations
- [ ] Check error handling
- [ ] Test coverage_delta_check.py with sample coverage files
- [ ] Test get_agent_for_dir.sh boundary conditions (repo root, no owner)

**Deliverables:**

- 33 scripts fully tested (32 Python + 1 Bash)
- All scripts executable and documented
- Script tests passing

---

### Phase 3: Hooks (Week 2, 6-8 hours)

**3.1 Claude CLI Hooks (5 scripts)**

- [ ] `.claude/hooks/session_start.py`
- [ ] `.claude/hooks/validate_command.py`
- [ ] `.claude/hooks/pre_tool_use.py`
- [ ] `.claude/hooks/post_tool_use.py`
- [ ] `.claude/hooks/subagent_stop.py`

**3.2 Git Hooks (3 scripts)**

- [ ] `.claude/git-hooks/prepare-commit-msg`
- [ ] `.claude/git-hooks/post-commit`
- [ ] `.claude/git-hooks/post-checkout`

**3.3 Hook Configuration**

- [ ] Update `.claude/settings.json` with hook configurations
- [ ] Test hook triggers
- [ ] Validate hook blocking/allowing behavior

**3.4 Install Git Hooks**

- [ ] Copy git-hooks/ templates to .git/hooks/
- [ ] Make executable (chmod +x)
- [ ] Test with actual git operations

**Testing:**

- [ ] Test SessionStart hook loads task context
- [ ] Test PreToolUse blocks wrong agent
- [ ] Test PostToolUse updates STATE.json
- [ ] Test SubagentStop validates completeness (with coverage delta)
- [ ] Test git hooks format commits correctly (conventional commits)

**3.5 CI Enforcement Setup**

- [ ] Create `.github/workflows/sdlc-validation.yml`
- [ ] Configure CI to validate commit messages (conventional format)
- [ ] Configure CI to validate STATE.json integrity
- [ ] Configure CI to validate commit-task mapping
- [ ] Configure CI to run tests and check coverage delta
- [ ] Configure CI to validate agent ownership (get_agent_for_dir.sh)
- [ ] Configure CI to run quality gates (lint, type, security)
- [ ] Test CI on sample PR
- [ ] Verify --no-verify bypass is prevented by CI

**Deliverables:**

- 8 hooks working (5 Claude CLI + 3 git)
- All hooks tested and validated
- .claude/settings.json configured
- CI pipeline enforcing all validations

**Reference:** See `20251101-1219-review-hooks-comparison-specification.md` for full hook implementations and CI setup

---

### Phase 4: Commands (Week 2-3, 6-8 hours)

**4.1 Story Commands (4)**

- [ ] `.claude/commands/story-new.md`
- [ ] `.claude/commands/story-list.md`
- [ ] `.claude/commands/story-view.md`
- [ ] `.claude/commands/story-update.md`

**4.2 Task Management Commands (5)**

- [ ] `.claude/commands/task-new.md`
- [ ] `.claude/commands/task-list.md`
- [ ] `.claude/commands/task-resume.md`
- [ ] `.claude/commands/task-switch.md`
- [ ] `.claude/commands/task-status.md`

**4.3 SDLC Phase Commands (5)**

- [ ] `.claude/commands/task-research.md`
- [ ] `.claude/commands/task-plan.md`
- [ ] `.claude/commands/task-implement.md`
- [ ] `.claude/commands/task-test.md`
- [ ] `.claude/commands/task-validate.md`

**4.4 Completion & Utility (4)**

- [ ] `.claude/commands/task-complete.md`
- [ ] `.claude/commands/research-find-patterns.md`
- [ ] `.claude/commands/research-analyze-code.md`
- [ ] `.claude/commands/research-git-history.md`

**Testing:**

- [ ] Test each command end-to-end
- [ ] Verify scripts are called correctly
- [ ] Check error handling
- [ ] Validate output formatting

**Deliverables:**

- 18 commands working
- All commands < 50 lines
- Commands call appropriate scripts

---

### Phase 5: Agent Updates & Enforcement (Week 3, 4-6 hours)

**5.1 Update CLAUDE.md**

- [ ] Add "Directory Ownership & Agent Enforcement" section
- [ ] Add agent responsibility table
- [ ] Document enforcement rules
- [ ] Add examples (wrong vs correct)

**5.2 Update Agent Definitions**

- [ ] Update `.claude/agents/dev-backend/AGENT.md`
  - [ ] Add mandatory skills list
  - [ ] Add "When to Invoke (MANDATORY)" section
  - [ ] Add quality requirements
- [ ] Update `.claude/agents/dev-frontend/AGENT.md` (same structure)
- [ ] Update `.claude/agents/devops-infra/AGENT.md` (same structure)

**5.3 Test Enforcement**

- [ ] Test PreToolUse hook blocks main LLM from code edits
- [ ] Test correct agent is allowed
- [ ] Test wrong agent is blocked
- [ ] Verify error messages are helpful

**Deliverables:**

- CLAUDE.md updated with enforcement rules
- All 3 agents updated with mandatory skills
- Enforcement tested and working

**Reference:** See `20251101-1219-mapping-agents-skills-enforcement.md` for complete agent specifications

---

### Phase 6: Integration Testing (Week 3-4, 6-8 hours)

**6.1 Complete Workflow Test**

- [ ] Test: Create story → Create task → Research → Plan → Implement → Test → Validate → Complete
- [ ] Verify: All hooks trigger at correct points
- [ ] Verify: STATE.json updated correctly throughout
- [ ] Verify: Context passes between phases
- [ ] Verify: Agents spawn correctly

**6.2 Agent Coordination Test**

- [ ] Test: Backend agent → Frontend agent handoff
- [ ] Verify: Backend context saved to context/backend-done.md
- [ ] Verify: Frontend agent receives backend context
- [ ] Verify: Both agents tracked in STATE.json

**6.3 Hook Validation Test**

- [ ] Test: SessionStart loads correct task
- [ ] Test: PreToolUse blocks violations
- [ ] Test: PostToolUse tracks commits
- [ ] Test: SubagentStop validates completeness
- [ ] Test: Git hooks format commits

**6.4 Error Recovery Test**

- [ ] Test: Task creation fails gracefully
- [ ] Test: Missing dependencies handled
- [ ] Test: Invalid STATE.json detected
- [ ] Test: Agent failures reported

**Deliverables:**

- Complete workflow tested end-to-end
- All edge cases handled
- Error recovery working
- Documentation of test results

**Reference:** See `20251101-1219-diagram-complete-workflow.md` for expected workflow behavior

---

### Phase 7: Documentation & Rollout (Week 4, 2-3 hours)

**7.1 Update Documentation**

- [ ] Update docs-stories/SKILL.md with final content
- [ ] Complete all reference docs in docs-stories/references/
- [ ] Update .claude/rules/sdlc-workflow.md
- [ ] Create troubleshooting guide

**7.2 Create Quick Start**

- [ ] Create QUICKSTART.md in .claude/
- [ ] Document common workflows
- [ ] Add FAQ section
- [ ] Include example outputs

**7.3 Team Training**

- [ ] Share documentation
- [ ] Walk through example workflow
- [ ] Demonstrate hook behavior
- [ ] Collect feedback

**Deliverables:**

- All documentation complete
- Quick start guide created
- Team trained
- System in production use

---

## 7. File Structure (Complete)

```
bestays-monorepo/
│
├── .git/
│   └── hooks/
│       ├── post-checkout          # Git hook (installed from .claude/git-hooks/)
│       ├── prepare-commit-msg     # Git hook
│       └── post-commit            # Git hook
│
├── .gitmessage                    # Commit message template
│
├── .claude/
│   ├── settings.json              # Hook configurations
│   │
│   ├── rules/                     # PERMANENT - Mandatory governance
│   │   └── sdlc-workflow.md      # < 1k words, loaded every session
│   │
│   ├── tasks/                     # DYNAMIC - Task management
│   │   ├── current.txt            # Current active task ID
│   │   ├── commit-task-map.csv    # Git commit → task mapping
│   │   ├── TASK-001/
│   │   │   ├── STATE.json         # Complete task state
│   │   │   ├── context/           # Context files
│   │   │   │   ├── backend-done.md
│   │   │   │   └── frontend-done.md
│   │   │   ├── research/          # Research findings
│   │   │   │   ├── patterns.md
│   │   │   │   └── dependencies.md
│   │   │   ├── planning/          # Planning artifacts
│   │   │   │   └── implementation-plan.md
│   │   │   └── logs/              # Execution logs
│   │   │       └── research.log
│   │   ├── TASK-002/
│   │   └── archive/               # Completed tasks
│   │       └── TASK-001/
│   │           ├── STATE.json
│   │           ├── retrospective.md
│   │           └── [all other files]
│   │
│   ├── skills/
│   │   ├── docs-stories/          # THE skill for SDLC
│   │   │   ├── SKILL.md           # < 5k words
│   │   │   ├── references/        # Progressive disclosure
│   │   │   │   ├── state-management.md
│   │   │   │   ├── commit-conventions.md
│   │   │   │   ├── hooks-integration.md
│   │   │   │   └── script-reference.md
│   │   │   └── scripts/           # 31 Python scripts
│   │   │       ├── task_create.py
│   │   │       ├── task_update_state.py
│   │   │       ├── story_create.py
│   │   │       ├── git_stats.py
│   │   │       ├── lint_check.py
│   │   │       └── ... (all 31 scripts)
│   │   │
│   │   ├── backend-*/             # Existing backend skills (9 skills)
│   │   ├── frontend-*/            # Existing frontend skills (1 skill)
│   │   └── devops-*/              # Existing devops skills (3 skills)
│   │
│   ├── agents/                    # Agent definitions (updated)
│   │   ├── dev-backend/
│   │   │   └── AGENT.md           # Updated with mandatory skills
│   │   ├── dev-frontend/
│   │   │   └── AGENT.md
│   │   └── devops-infra/
│   │       └── AGENT.md
│   │
│   ├── commands/                  # 18 slash commands
│   │   ├── story-new.md
│   │   ├── story-list.md
│   │   ├── story-view.md
│   │   ├── story-update.md
│   │   ├── task-new.md
│   │   ├── task-list.md
│   │   ├── task-resume.md
│   │   ├── task-switch.md
│   │   ├── task-status.md
│   │   ├── task-research.md
│   │   ├── task-plan.md
│   │   ├── task-implement.md
│   │   ├── task-test.md
│   │   ├── task-validate.md
│   │   ├── task-complete.md
│   │   ├── research-find-patterns.md
│   │   ├── research-analyze-code.md
│   │   └── research-git-history.md
│   │
│   ├── hooks/                     # Claude CLI hooks (5 Python scripts)
│   │   ├── session_start.py
│   │   ├── validate_command.py
│   │   ├── pre_tool_use.py
│   │   ├── post_tool_use.py
│   │   └── subagent_stop.py
│   │
│   ├── git-hooks/                 # Git hook templates (3 bash scripts)
│   │   ├── prepare-commit-msg
│   │   ├── post-commit
│   │   └── post-checkout
│   │
│   └── templates/                 # Templates
│       ├── user-story.md
│       └── task-state.json
│
├── .sdlc-workflow/                  # Project knowledge (separate from .claude/)
│   ├── stories/                   # User stories
│   │   ├── auth/
│   │   │   └── login.md           # US-001-auth-login-admin
│   │   ├── properties/
│   │   └── payments/
│   │
│   ├── plan/                      # TEMPORARY planning (this document)
│   │   ├── 20251101-1219-sdlc-todo-plan-git-userstories-v2.md
│   │   └── walkthrough/           # Implementation walkthrough
│   │       ├── 20251101-1219-review-hooks-comparison-specification.md
│   │       ├── 20251101-1219-diagram-complete-workflow.md
│   │       └── 20251101-1219-mapping-agents-skills-enforcement.md
│   │
│   └── conventions/               # Project-specific patterns
│       ├── backend/
│       └── frontend/
│
└── [rest of project unchanged]
```

---

## 8. Summary of Deliverables

### Documentation

- `.claude/rules/sdlc-workflow.md` (< 1k words, mandatory)
- `.claude/skills/docs-stories/SKILL.md` (< 5k words, detailed)
- `.claude/skills/docs-stories/references/` (4 reference docs)
- Updated CLAUDE.md (with enforcement rules)
- Updated agent AGENT.md files (3 agents)

### Scripts (33 total)

- 10 task management scripts
- 5 task data scripts
- 5 story management scripts
- 5 git integration scripts
- 3 quality checking scripts
- 2 validation scripts
- 1 session script
- 2 new additions (coverage_delta_check.py, get_agent_for_dir.sh)

**Note:** 32 Python scripts + 1 Bash script (get_agent_for_dir.sh)

### Hooks (8 total)

- 5 Claude CLI hooks (Python)
- 3 git hooks (bash, with conventional commits support)

### CI Enforcement

- GitHub Actions workflow (`.github/workflows/sdlc-validation.yml`)
- Validates: commits, STATE.json, tests, coverage, ownership, quality gates
- Prevents bypass of local hooks

### Commands (18 total)

- 4 story commands
- 5 task management commands (with feedback loop support)
- 5 SDLC phase commands (planning and implementation support iterative refinement)
- 4 utility commands

### Templates

- User story template
- Task STATE.json template
- App README.md template (with owner frontmatter)

### Ownership System

- Centralized table (in agent mapping document)
- Declarative README.md with YAML frontmatter
- get_agent_for_dir.sh for automated resolution
- CI validation of all file ownership

### Total Implementation Effort

- 45-60 hours over 4 weeks (increased from 42-55 due to CI and ownership additions)
- Phase 1: 8-10 hours (foundation + README ownership)
- Phase 2: 12-14 hours (scripts, +2 new scripts)
- Phase 3: 8-10 hours (hooks + CI enforcement)
- Phase 4: 6-8 hours (commands)
- Phase 5: 4-6 hours (agents/enforcement)
- Phase 6: 6-8 hours (integration testing)
- Phase 7: 2-3 hours (documentation/rollout)

---

## 9. Conventional Commits Standard

### 9.1 Format

All commit messages must follow the Conventional Commits specification:

```
type(scope): message [TASK-xxx/US-xxx]
```

**Components:**

- `type`: The type of change (feat, fix, docs, style, refactor, perf, test, chore)
- `scope`: The domain or module affected (auth, api, ui, db, etc.)
- `message`: Imperative mood description of what was done (lowercase, no period)
- `[TASK-xxx/US-xxx]`: Task and story IDs for traceability

### 9.2 Examples

```bash
feat(auth): add admin login endpoint [TASK-001/US-001]
fix(api): resolve rate limiting bug [TASK-023/US-004]
docs(readme): update installation instructions [TASK-045/US-012]
test(auth): add unit tests for login flow [TASK-001/US-001]
refactor(db): optimize user query performance [TASK-067/US-019]
```

### 9.3 Type Definitions

| Type       | Usage                                            | Example                                     |
| ---------- | ------------------------------------------------ | ------------------------------------------- |
| `feat`     | New feature or functionality                     | `feat(api): add user filtering endpoint`    |
| `fix`      | Bug fix                                          | `fix(ui): resolve modal close button issue` |
| `docs`     | Documentation only                               | `docs(api): add swagger annotations`        |
| `style`    | Code style changes (formatting, no logic change) | `style(server): apply ruff formatting`      |
| `refactor` | Code refactoring (no feature/fix)                | `refactor(auth): extract validation logic`  |
| `perf`     | Performance improvement                          | `perf(db): add index on user email`         |
| `test`     | Adding or updating tests                         | `test(api): add integration tests`          |
| `chore`    | Build, dependencies, tooling                     | `chore(deps): update fastapi to 0.104.0`    |

### 9.4 Scope Conventions

Scope should match the domain from the story ID when possible:

- `auth` - Authentication/authorization
- `api` - API endpoints
- `ui` - User interface
- `db` - Database/models
- `admin` - Admin panel
- `booking` - Booking system
- `payment` - Payment processing

### 9.5 Automation Benefits

**Conventional commits enable:**

1. **Automated Changelog Generation**

   ```markdown
   ## [1.2.0] - 2025-11-01

   ### Features

   - **auth**: add admin login endpoint [TASK-001/US-001]
   - **api**: add user filtering endpoint [TASK-123/US-004]

   ### Bug Fixes

   - **ui**: resolve modal close button issue [TASK-089/US-002]
   ```

2. **Semantic Versioning**

   - `feat` → MINOR version bump (1.1.0 → 1.2.0)
   - `fix` → PATCH version bump (1.1.0 → 1.1.1)
   - `BREAKING CHANGE` footer → MAJOR version bump (1.1.0 → 2.0.0)

3. **Release Notes**

   - Group commits by type
   - Link to tasks/stories
   - Filter by scope

4. **Git Statistics**
   - Track feature velocity
   - Measure bug fix rate
   - Analyze work distribution by domain

### 9.6 Enforcement

**Three-layer enforcement:**

1. **prepare-commit-msg hook** (git): Auto-formats commits
2. **PostToolUse hook** (Claude CLI): Validates format before accepting
3. **CI pipeline** (GitHub Actions): Blocks PRs with invalid commits

No commit can reach main/develop without following the standard.

---

## 10. Success Criteria

### Automation Metrics

- [ ] SessionStart hook loads task context automatically
- [ ] PreToolUse hook blocks 100% of inappropriate agent usage
- [ ] PostToolUse hook tracks 100% of commits in STATE.json
- [ ] SubagentStop hook validates agent completeness
- [ ] Git hooks format 100% of commits correctly

### Workflow Metrics

- [ ] Task creation: < 5 minutes (was 30 minutes)
- [ ] Context loading: Automatic (was manual)
- [ ] Agent enforcement: 100% (was 0%)
- [ ] State accuracy: 100% (was manual/error-prone)
- [ ] Validation: Automated (was manual)

### Quality Metrics

- [ ] All 31 scripts have tests
- [ ] All hooks tested independently
- [ ] Complete workflow tested end-to-end
- [ ] Error recovery tested
- [ ] Documentation complete

---

## 10. Next Steps

**Immediate:**

1. Review this plan and all companion documents
2. Approve architecture and approach
3. Begin Phase 1 implementation

**Implementation:**

1. Follow phases 1-7 sequentially
2. Test each phase before proceeding
3. Document issues and solutions
4. Collect feedback throughout

**Post-Implementation:**

1. Monitor usage and effectiveness
2. Refine based on feedback
3. Add additional features as needed
4. Share learnings with team

---

## 11. References

**Companion Documents (Read These First):**

1. `.sdlc-workflow/plan/walkthrough/20251101-1219-review-hooks-comparison-specification.md`

   - Git hooks vs Claude CLI hooks
   - Complete hook implementations
   - Configuration examples

2. `.sdlc-workflow/plan/walkthrough/20251101-1219-diagram-complete-workflow.md`

   - Visual workflow diagrams
   - Agent spawning flows
   - Data flow and context passing

3. `.sdlc-workflow/plan/walkthrough/20251101-1219-mapping-agents-skills-enforcement.md`
   - Agent-skill mandatory mappings
   - Directory ownership enforcement
   - CLAUDE.md and agent updates

**Original Documents:**

- Original plan: `.sdlc-workflow/plan/20251031-2338-sdlc-todo-plan-git-userstories.md`
- Architecture analysis: `.sdlc-workflow/plan/-20251101-0028-analysis-architecture-decisions.md`
- Plan analysis: `.sdlc-workflow/plan/20251031-2350-sdlc-plan-analysis.md`

**Configuration References:**

- Claude Code hooks guide: https://docs.claude.com/en/docs/claude-code/hooks-guide
- Claude Code config principles: `.claude/rules/claude-code-config.md`

---

**Status:** Ready for implementation
**Version:** 2.0
**Last Updated:** 2025-11-01 12:19

---

**End of SDLC Plan v2**
