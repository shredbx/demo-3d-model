# Hooks Review: Git Hooks vs Claude Code CLI Hooks

**Created:** 2025-11-01 12:19
**Purpose:** Comprehensive analysis and specification of hooks for SDLC workflow automation
**Status:** Architecture Review

---

## Executive Summary

The original SDLC plan proposed 3 git hooks for automation. However, this analysis reveals that **Claude Code CLI hooks** provide superior capabilities for SDLC workflow enforcement.

**Key Findings:**

- Git hooks: Best for low-level git operations automation
- Claude CLI hooks: Best for high-level SDLC validation and agent enforcement
- **Recommendation: Use BOTH systems together** for comprehensive automation

**Changes from Original Plan:**

- Add 5 Claude Code CLI hooks (missing from original)
- Keep 3 git hooks (but clarify their limited scope)
- Convert all hook scripts from Bash to Python
- Add enforcement of agent scope boundaries

---

## 1. Git Hooks vs Claude Code CLI Hooks

### 1.1 Fundamental Differences

| Aspect        | Git Hooks                               | Claude Code CLI Hooks                                            |
| ------------- | --------------------------------------- | ---------------------------------------------------------------- |
| **Trigger**   | Git operations (commit, checkout, push) | Claude lifecycle events (tool use, session start, prompt submit) |
| **Context**   | Git metadata only                       | Full Claude context (agent, task, STATE.json)                    |
| **Location**  | `.git/hooks/` directory                 | Configured in `.claude/settings.json`                            |
| **Language**  | Shell scripts (typically bash)          | Any executable (we use Python)                                   |
| **Input**     | Git command arguments                   | JSON via stdin with hook context                                 |
| **Blocking**  | Can prevent git operations              | Can prevent Claude tool execution                                |
| **Awareness** | Git-only (branches, commits, files)     | Claude-aware (agents, skills, tasks, sessions)                   |

### 1.2 Capabilities Comparison

| Capability                           | Git Hooks                              | Claude CLI Hooks          |
| ------------------------------------ | -------------------------------------- | ------------------------- |
| Auto-format commit messages          | ✅ Yes (prepare-commit-msg)            | ❌ Too late               |
| Track commits in STATE.json          | ⚠️ Limited (no STATE.json access)      | ✅ Yes (PostToolUse)      |
| Load task context on session start   | ❌ No (git unaware of Claude sessions) | ✅ Yes (SessionStart)     |
| Block edits outside agent scope      | ❌ No (git unaware of agents)          | ✅ Yes (PreToolUse)       |
| Validate subagent work completeness  | ❌ No (git unaware of agents)          | ✅ Yes (SubagentStop)     |
| Update current task on branch switch | ✅ Yes (post-checkout)                 | ⚠️ Limited (branch only)  |
| Validate command prerequisites       | ❌ No (git unaware of commands)        | ✅ Yes (UserPromptSubmit) |

### 1.3 When to Use Which

**Use Git Hooks For:**

- Commit message formatting (fast, deterministic)
- Git metadata tracking
- File updates on branch operations
- Actions that MUST happen in git subprocess

**Use Claude CLI Hooks For:**

- SDLC workflow validation
- Agent scope enforcement
- Task state management
- Context loading and passing
- Subagent coordination
- Actions that need Claude context

---

## 2. Recommended Git Hooks (3 Total)

### 2.1 Hook #1: prepare-commit-msg

**Purpose:** Automatically format commit messages to conventional commits standard with task/story IDs

**File:** `.git/hooks/prepare-commit-msg`

```bash
#!/bin/bash
# prepare-commit-msg
# Runs BEFORE commit message editor opens
# Formats to: type(scope): message [TASK-XXX/US-XXX]

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2

# Skip if amending, merging, or squashing
[[ "$COMMIT_SOURCE" =~ (merge|squash|commit) ]] && exit 0

# Get current task from .claude/tasks/current.txt
CURRENT_TASK=$(cat .claude/tasks/current.txt 2>/dev/null)

if [[ -n "$CURRENT_TASK" && "$CURRENT_TASK" != "none" ]]; then
  STATE_FILE=".claude/tasks/$CURRENT_TASK/STATE.json"

  if [[ -f "$STATE_FILE" ]]; then
    # Extract story_id, task_type, and domain from STATE.json
    STORY_ID=$(python3 -c "import json; print(json.load(open('$STATE_FILE'))['story_id'])" 2>/dev/null)
    TASK_TYPE=$(python3 -c "import json; print(json.load(open('$STATE_FILE'))['task_type'])" 2>/dev/null)

    # Extract domain/scope from story_id (e.g., US-001-auth-login-admin → auth)
    SCOPE=$(echo "$STORY_ID" | cut -d'-' -f3)

    # Check if message already has conventional format
    if ! grep -q "\[TASK-" "$COMMIT_MSG_FILE"; then
      # Read original message
      ORIG_MSG=$(head -n1 "$COMMIT_MSG_FILE")

      # Format: type(scope): message [TASK-XXX/US-XXX]
      echo "$TASK_TYPE($SCOPE): $ORIG_MSG [TASK-$CURRENT_TASK/$STORY_ID]" > "$COMMIT_MSG_FILE.tmp"
      tail -n +2 "$COMMIT_MSG_FILE" >> "$COMMIT_MSG_FILE.tmp"
      mv "$COMMIT_MSG_FILE.tmp" "$COMMIT_MSG_FILE"
    fi
  fi
fi

exit 0
```

**Result (Conventional Commits Format):**

```bash
# User types:
git commit -m "add user filtering endpoint"

# Commit message becomes:
feat(api): add user filtering endpoint [TASK-123/US-004]
```

**Conventional Commits Standard:**

- `type`: feat, fix, docs, style, refactor, perf, test, chore
- `scope`: domain or module (auth, api, ui, db, etc.)
- `message`: imperative mood, lowercase, no period
- `[TASK-XXX/US-XXX]`: task and story IDs for traceability

**Benefits:**

- Enables automated changelog generation
- Supports semantic versioning automation
- Clear categorization of changes
- Maintains task traceability

**Why This Can't Be Claude CLI Hook:**

- Needs to run in git subprocess before editor
- Must modify git's commit message file directly
- Too tightly coupled to git internals

---

### 2.2 Hook #2: post-commit

**Purpose:** Create commit-task mapping for quick lookups

**File:** `.git/hooks/post-commit`

```bash
#!/bin/bash
# post-commit
# Runs AFTER commit is created

CURRENT_TASK=$(cat .claude/tasks/current.txt 2>/dev/null)

if [[ -n "$CURRENT_TASK" && "$CURRENT_TASK" != "none" ]]; then
  COMMIT_SHA=$(git rev-parse HEAD)
  COMMIT_MSG=$(git log -1 --pretty=%B)

  # Append to commit-task mapping file
  echo "$COMMIT_SHA,$CURRENT_TASK" >> .claude/tasks/commit-task-map.csv

  echo "✓ Git: Commit $COMMIT_SHA mapped to $CURRENT_TASK"
fi

exit 0
```

**Note:** This is LIGHTWEIGHT - just creates mapping. The heavy STATE.json update is done by Claude CLI PostToolUse hook.

**Why This Can't Be Claude CLI Hook:**

- Needs to run immediately after git commit
- Creates git-level mapping file
- Complements (doesn't duplicate) Claude CLI hook

---

### 2.3 Hook #3: post-checkout

**Purpose:** Update current.txt when switching branches

**File:** `.git/hooks/post-checkout`

```bash
#!/bin/bash
# post-checkout
# Runs after: git checkout <branch>

PREV_HEAD=$1
NEW_HEAD=$2
BRANCH_SWITCH=$3

# Only process branch switches (not file checkouts)
[[ $BRANCH_SWITCH != "1" ]] && exit 0

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Extract task ID from branch name
# Pattern: (feat|fix|perf|refactor|test|docs|chore)/TASK-XXX-US-XXX-...
if [[ $CURRENT_BRANCH =~ (feat|fix|perf|refactor|test|docs|chore)/TASK-([0-9]+) ]]; then
  TASK_ID="TASK-${BASH_REMATCH[2]}"
  echo "$TASK_ID" > .claude/tasks/current.txt
  echo "✓ Git: Switched to task: $TASK_ID"
else
  # Not on a task branch
  echo "none" > .claude/tasks/current.txt
  echo "✓ Git: No active task (on $CURRENT_BRANCH)"
fi

exit 0
```

**Why This Can't Be Claude CLI Hook:**

- Runs in git subprocess, not Claude
- Needs to update file immediately on branch switch
- Fast, deterministic operation

---

## 3. Recommended Claude Code CLI Hooks (5 Total)

### 3.1 Available Hook Types

Claude Code CLI provides these lifecycle hooks:

| Hook                 | Trigger                       | Can Block | Input Context                 |
| -------------------- | ----------------------------- | --------- | ----------------------------- |
| **SessionStart**     | Claude session starts/resumes | No        | Session info                  |
| **SessionEnd**       | Claude session terminates     | No        | Session info                  |
| **UserPromptSubmit** | User submits prompt           | Yes       | Prompt text                   |
| **PreToolUse**       | Before tool execution         | Yes       | Tool name, parameters         |
| **PostToolUse**      | After tool execution          | No        | Tool name, parameters, result |
| **SubagentStop**     | Subagent task completes       | No        | Subagent info, result         |
| **PreCompact**       | Before context compaction     | Yes       | Compaction info               |
| **Notification**     | Claude sends notification     | No        | Notification text             |
| **Stop**             | Claude stops responding       | No        | Response info                 |

**We will use 5 of these for SDLC workflow automation.**

---

### 3.2 Hook #1: SessionStart

**Purpose:** Load task context when Claude session starts

**Configuration in `.claude/settings.json`:**

```json
{
  "hooks": {
    "SessionStart": {
      "description": "Load current task context on session start",
      "command": "python .claude/hooks/session_start.py"
    }
  }
}
```

**Script:** `.claude/hooks/session_start.py`

```python
#!/usr/bin/env python3
"""
SessionStart Hook - Load task context on session start
"""
import sys
import json
from pathlib import Path
import subprocess

def main():
    # Read current task
    current_task_file = Path(".claude/tasks/current.txt")

    if not current_task_file.exists():
        print("No active task. Use /task-new or /task-resume to start.")
        return 0

    current_task = current_task_file.read_text().strip()

    if current_task == "none":
        print("No active task. Use /task-new or /task-resume to start.")
        return 0

    # Load STATE.json
    state_file = Path(f".claude/tasks/{current_task}/STATE.json")

    if not state_file.exists():
        print(f"⚠️  Warning: Task {current_task} has no STATE.json")
        return 0

    state = json.loads(state_file.read_text())

    # Display task context
    print(f"📋 Active Task: {current_task}")
    print(f"   Story: {state.get('story_id', 'Unknown')}")
    print(f"   Phase: {state.get('phase', {}).get('current', 'Unknown')}")
    print(f"   Status: {state.get('status', 'Unknown')}")

    # Suggest next action based on phase
    current_phase = state.get('phase', {}).get('current')
    next_action = get_next_action(current_phase, state)

    if next_action:
        print(f"\n💡 Suggested next step: {next_action}")

    return 0

def get_next_action(phase, state):
    """Suggest next command based on current phase"""
    suggestions = {
        'PLANNING': '/task-research (if not done) or /task-plan',
        'RESEARCH': '/task-plan',
        'IMPLEMENTATION': '/task-implement <backend|frontend|fullstack>',
        'TESTING': '/task-test',
        'VALIDATION': '/task-validate',
        'REVIEW': 'Fix any issues, then /task-complete'
    }
    return suggestions.get(phase)

if __name__ == "__main__":
    sys.exit(main())
```

**When Triggered:**

- Every time Claude session starts
- When user runs `claude` command

**What It Does:**

- Loads current task from current.txt
- Reads STATE.json
- Displays task status
- Suggests next command based on phase

**Why This Can't Be Git Hook:**

- Needs to run in Claude session context
- Must display to Claude, not just terminal
- Git hooks run in subprocess, isolated from Claude

---

### 3.3 Hook #2: UserPromptSubmit

**Purpose:** Validate command prerequisites before execution

**Configuration:**

```json
{
  "UserPromptSubmit": {
    "description": "Validate command prerequisites",
    "command": "python .claude/hooks/validate_command.py"
  }
}
```

**Script:** `.claude/hooks/validate_command.py`

```python
#!/usr/bin/env python3
"""
UserPromptSubmit Hook - Validate command prerequisites
"""
import sys
import json
import re
from pathlib import Path

def main():
    # Read hook context from stdin
    hook_context = json.load(sys.stdin)
    prompt = hook_context.get('prompt', '')

    # Check if prompt contains task commands that require active task
    task_commands = [
        '/task-research', '/task-plan', '/task-implement',
        '/task-test', '/task-validate', '/task-complete',
        '/task-status'
    ]

    for cmd in task_commands:
        if cmd in prompt:
            if not validate_active_task():
                print(f"❌ Error: {cmd} requires an active task")
                print("   Use /task-new or /task-resume first")
                return 1  # Block command

    # Check if /task-new requires valid story
    if '/task-new' in prompt:
        # Extract story ID from command
        match = re.search(r'/task-new\s+(US-\d+)', prompt)
        if match:
            story_id = match.group(1)
            if not validate_story_exists(story_id):
                print(f"❌ Error: Story {story_id} does not exist")
                print("   Use /story-new to create it first")
                return 1  # Block command

    return 0  # Allow command

def validate_active_task():
    """Check if there's an active task"""
    current_task_file = Path(".claude/tasks/current.txt")
    if not current_task_file.exists():
        return False

    current_task = current_task_file.read_text().strip()
    return current_task != "none"

def validate_story_exists(story_id):
    """Check if story file exists"""
    # Stories are in .sdlc-workflow/stories/
    story_files = list(Path(".sdlc-workflow/stories").rglob("*.md"))

    for story_file in story_files:
        content = story_file.read_text()
        if f"id: {story_id}" in content or story_id in story_file.stem:
            return True

    return False

if __name__ == "__main__":
    sys.exit(main())
```

**When Triggered:**

- Before Claude processes any user prompt
- On every message submission

**What It Does:**

- Validates task commands have active task
- Validates /task-new references existing story
- Blocks invalid commands with helpful message

**Why This Can't Be Git Hook:**

- Needs to intercept Claude commands
- Must access Claude prompt context
- No git operation involved

---

### 3.4 Hook #3: PreToolUse

**Purpose:** Enforce agent scope boundaries and prevent direct code edits

**Configuration:**

```json
{
  "PreToolUse": {
    "description": "Enforce agent scope - block edits outside agent boundaries",
    "matcher": "Edit|Write",
    "command": "python .claude/hooks/pre_tool_use.py"
  }
}
```

**Script:** `.claude/hooks/pre_tool_use.py`

```python
#!/usr/bin/env python3
"""
PreToolUse Hook - Enforce agent scope boundaries

CRITICAL: Prevents main LLM from editing code directly.
All code edits must go through appropriate specialized agents.
"""
import sys
import json
from pathlib import Path

# Agent scope definitions
AGENT_SCOPES = {
    'dev-backend': [
        'apps/server/**',
        'tests/backend/**'
    ],
    'dev-frontend': [
        'apps/frontend/**',
        'tests/frontend/**'
    ],
    'devops-infra': [
        'docker/**',
        'Makefile',
        'docker-compose.yml',
        'docker-compose.*.yml'
    ]
}

def main():
    # Read hook context from stdin
    hook_context = json.load(sys.stdin)

    tool_name = hook_context.get('tool', '')
    parameters = hook_context.get('parameters', {})

    # Only check Edit and Write tools
    if tool_name not in ['Edit', 'Write']:
        return 0

    file_path = parameters.get('file_path', '')

    if not file_path:
        return 0  # No file path, allow

    # Check if file is in protected scope
    required_agent = get_required_agent(file_path)

    if required_agent:
        # Check if current agent matches
        current_agent = get_current_agent()

        if current_agent != required_agent:
            print(f"❌ BLOCKED: File {file_path} requires {required_agent} agent")
            print(f"   Current context: {current_agent or 'main LLM'}")
            print(f"\n   Action required:")
            print(f"   1. Use Task tool to spawn {required_agent} agent")
            print(f"   2. Or use /task-implement command which spawns correct agent")
            print(f"\n   This enforcement ensures clean separation of concerns.")
            return 1  # Block operation

    return 0  # Allow operation

def get_required_agent(file_path):
    """Determine which agent is required for this file path"""
    from pathlib import Path

    path = Path(file_path)

    for agent, patterns in AGENT_SCOPES.items():
        for pattern in patterns:
            if path.match(pattern):
                return agent

    return None  # No agent required

def get_current_agent():
    """
    Determine current agent context

    Note: This is simplified. In practice, might read from:
    - Environment variable set by Task tool
    - .claude/tasks/{task}/current_agent.txt
    - Other context indicators
    """
    import os

    # Check environment variable (set by Task tool when spawning agents)
    agent = os.environ.get('CLAUDE_CURRENT_AGENT')

    if agent:
        return agent

    # Check current agent file (if exists)
    agent_file = Path('.claude/tasks/.current_agent')
    if agent_file.exists():
        return agent_file.read_text().strip()

    return None  # Main LLM context

if __name__ == "__main__":
    sys.exit(main())
```

**When Triggered:**

- Before any Edit or Write tool execution
- On every file modification attempt

**What It Does:**

- Checks if file is in protected scope (apps/server/, apps/frontend/, docker/)
- Determines which agent is required
- Blocks if current context doesn't match required agent
- Provides clear error message and remediation steps

**Why This Can't Be Git Hook:**

- Needs to intercept tool execution before it happens
- Must access Claude's tool context
- Must know current agent context
- Git hooks run after file changes, too late to block

**Impact:**
This is the **most critical** hook. It enforces the architectural principle that main LLM NEVER directly edits code. All code changes must flow through specialized agents, ensuring:

- Agents always use their required skills
- Clean separation of concerns
- Consistent code quality
- Proper context for each domain

---

### 3.5 Hook #4: PostToolUse

**Purpose:** Update STATE.json after significant tool executions

**Configuration:**

```json
{
  "PostToolUse": {
    "description": "Update STATE.json after tool execution",
    "matcher": "Bash|Edit|Write",
    "command": "python .claude/hooks/post_tool_use.py"
  }
}
```

**Script:** `.claude/hooks/post_tool_use.py`

```python
#!/usr/bin/env python3
"""
PostToolUse Hook - Update STATE.json after tool execution
"""
import sys
import json
from pathlib import Path
import subprocess
from datetime import datetime

def main():
    # Read hook context from stdin
    hook_context = json.load(sys.stdin)

    tool_name = hook_context.get('tool', '')
    parameters = hook_context.get('parameters', {})

    # Get current task
    current_task_file = Path(".claude/tasks/current.txt")
    if not current_task_file.exists():
        return 0  # No active task, nothing to track

    current_task = current_task_file.read_text().strip()
    if current_task == "none":
        return 0

    # Update STATE.json based on tool
    if tool_name == 'Bash':
        # Check if this was a git commit
        command = parameters.get('command', '')
        if 'git commit' in command:
            track_commit(current_task)

    elif tool_name in ['Edit', 'Write']:
        # Track file modification
        file_path = parameters.get('file_path', '')
        if file_path:
            track_file_modified(current_task, file_path)

    # Update last_accessed timestamp
    update_timestamp(current_task)

    return 0  # Never block (PostToolUse can't block anyway)

def track_commit(task_id):
    """Add latest commit to STATE.json"""
    try:
        # Get commit info from git
        commit_sha = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            text=True
        ).strip()

        commit_msg = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%B'],
            text=True
        ).strip()

        commit_time = subprocess.check_output(
            ['git', 'log', '-1', '--format=%aI'],
            text=True
        ).strip()

        files_changed = len(subprocess.check_output(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
            text=True
        ).strip().split('\n'))

        # Update STATE.json
        state_file = Path(f".claude/tasks/{task_id}/STATE.json")
        state = json.loads(state_file.read_text())

        # Add commit to commits array
        if 'commits' not in state:
            state['commits'] = []

        state['commits'].append({
            'sha': commit_sha,
            'message': commit_msg,
            'timestamp': commit_time,
            'files_changed': files_changed
        })

        # Write back
        state_file.write_text(json.dumps(state, indent=2))

    except Exception as e:
        # Don't fail if commit tracking fails
        print(f"⚠️  Warning: Could not track commit: {e}")

def track_file_modified(task_id, file_path):
    """Add file to files_modified list"""
    try:
        state_file = Path(f".claude/tasks/{task_id}/STATE.json")
        state = json.loads(state_file.read_text())

        if 'files_modified' not in state:
            state['files_modified'] = []

        # Add if not already tracked
        if file_path not in state['files_modified']:
            state['files_modified'].append(file_path)

        state_file.write_text(json.dumps(state, indent=2))

    except Exception as e:
        print(f"⚠️  Warning: Could not track file: {e}")

def update_timestamp(task_id):
    """Update last_accessed timestamp"""
    try:
        state_file = Path(f".claude/tasks/{task_id}/STATE.json")
        state = json.loads(state_file.read_text())

        if 'timestamps' not in state:
            state['timestamps'] = {}

        state['timestamps']['last_accessed'] = datetime.utcnow().isoformat() + 'Z'

        state_file.write_text(json.dumps(state, indent=2))

    except Exception as e:
        print(f"⚠️  Warning: Could not update timestamp: {e}")

if __name__ == "__main__":
    sys.exit(main())
```

**When Triggered:**

- After Bash commands (especially git commits)
- After Edit or Write operations
- Whenever files are modified

**What It Does:**

- Tracks commits in STATE.json
- Tracks files modified
- Updates last_accessed timestamp
- Maintains complete audit trail

**Why This Can't Be Git Hook:**

- Needs to track non-git operations (Edit/Write tools)
- Must update STATE.json (not git-related)
- Must run in Claude context

---

### 3.6 Hook #5: SubagentStop

**Purpose:** Validate subagent work completeness

**Configuration:**

```json
{
  "SubagentStop": {
    "description": "Validate subagent work completeness",
    "command": "python .claude/hooks/subagent_stop.py"
  }
}
```

**Script:** `.claude/hooks/subagent_stop.py`

```python
#!/usr/bin/env python3
"""
SubagentStop Hook - Validate subagent work completeness

Ensures agents complete required tasks before finishing.
"""
import sys
import json
from pathlib import Path

# Required deliverables per agent
AGENT_REQUIREMENTS = {
    'dev-backend': {
        'files': ['Must have created or modified Python files'],
        'tests': 'Must have created or updated test files',
        'commits': 'Must have made at least 1 commit'
    },
    'dev-frontend': {
        'files': ['Must have created or modified Svelte files'],
        'tests': 'Must have created or updated test files',
        'commits': 'Must have made at least 1 commit'
    },
    'Explore': {
        'research': 'Must have saved research findings to task directory'
    },
    'Plan': {
        'plan': 'Must have saved implementation plan to task directory'
    }
}

def main():
    # Read hook context from stdin
    hook_context = json.load(sys.stdin)

    # Extract subagent info (structure depends on actual hook payload)
    # This is a simplified example
    agent_type = hook_context.get('agent_type', '')

    if agent_type not in AGENT_REQUIREMENTS:
        return 0  # No validation for this agent type

    # Get current task
    current_task_file = Path(".claude/tasks/current.txt")
    if not current_task_file.exists():
        return 0

    current_task = current_task_file.read_text().strip()
    if current_task == "none":
        return 0

    # Validate agent deliverables
    requirements = AGENT_REQUIREMENTS[agent_type]
    violations = []

    if agent_type == 'dev-backend':
        violations = validate_implementation_agent(current_task, 'backend')
    elif agent_type == 'dev-frontend':
        violations = validate_implementation_agent(current_task, 'frontend')
    elif agent_type == 'Explore':
        violations = validate_research_agent(current_task)
    elif agent_type == 'Plan':
        violations = validate_plan_agent(current_task)

    if violations:
        print(f"⚠️  Warning: {agent_type} agent incomplete work:")
        for violation in violations:
            print(f"   - {violation}")
        print(f"\n   Please complete before proceeding.")
        # Note: SubagentStop can't block, but can warn
    else:
        print(f"✅ {agent_type} agent work validated")
        # Update STATE.json with agent used
        update_agent_used(current_task, agent_type)

    return 0

def validate_implementation_agent(task_id, domain):
    """Validate dev-backend or dev-frontend agent"""
    violations = []

    # Check STATE.json for commits
    state_file = Path(f".claude/tasks/{task_id}/STATE.json")
    if not state_file.exists():
        return ["No STATE.json found"]

    state = json.loads(state_file.read_text())

    commits = state.get('commits', [])
    if not commits:
        violations.append("No commits made")

    files_modified = state.get('files_modified', [])
    if domain == 'backend':
        has_backend_files = any('apps/server' in f for f in files_modified)
        if not has_backend_files:
            violations.append("No backend files modified")
    elif domain == 'frontend':
        has_frontend_files = any('apps/frontend' in f for f in files_modified)
        if not has_frontend_files:
            violations.append("No frontend files modified")

    # Check for test files
    has_tests = any('test' in f for f in files_modified)
    if not has_tests:
        violations.append("No test files created/modified")

    # Enhanced Test Validation: Coverage Delta Check
    tests = state.get('tests', {})
    if tests:
        coverage = tests.get('coverage_percentage')
        coverage_baseline = tests.get('coverage_baseline', 80.0)  # Default baseline

        if coverage is not None:
            if coverage < coverage_baseline:
                violations.append(
                    f"Coverage {coverage}% below baseline {coverage_baseline}% "
                    f"(delta: {coverage - coverage_baseline:+.1f}%)"
                )

        # Check if passing
        if not tests.get('passing', False):
            violations.append("Tests are failing")

    return violations

def validate_research_agent(task_id):
    """Validate Explore agent"""
    research_dir = Path(f".claude/tasks/{task_id}/research")

    if not research_dir.exists():
        return ["No research directory found"]

    research_files = list(research_dir.glob("*.md"))
    if not research_files:
        return ["No research findings saved"]

    return []

def validate_plan_agent(task_id):
    """Validate Plan agent"""
    planning_dir = Path(f".claude/tasks/{task_id}/planning")

    if not planning_dir.exists():
        return ["No planning directory found"]

    plan_files = list(planning_dir.glob("*.md"))
    if not plan_files:
        return ["No implementation plan saved"]

    return []

def update_agent_used(task_id, agent_type):
    """Record which agent was used"""
    try:
        state_file = Path(f".claude/tasks/{task_id}/STATE.json")
        state = json.loads(state_file.read_text())

        if 'agents_used' not in state:
            state['agents_used'] = []

        if agent_type not in state['agents_used']:
            state['agents_used'].append(agent_type)

        state_file.write_text(json.dumps(state, indent=2))

    except Exception as e:
        print(f"⚠️  Warning: Could not update agents_used: {e}")

if __name__ == "__main__":
    sys.exit(main())
```

**When Triggered:**

- When any subagent (Task tool) completes and returns to main LLM

**What It Does:**

- Validates agent completed required deliverables
- Checks for commits (implementation agents)
- Checks for research/planning artifacts (research/planning agents)
- Warns if incomplete (can't block SubagentStop)
- Updates STATE.json with agents_used

**Why This Can't Be Git Hook:**

- Needs to know when agents finish (agent lifecycle)
- Must validate based on agent type
- Git hooks unaware of agents

---

## 4. Hooks Configuration File

**File:** `.claude/settings.json`

```json
{
  "project": "bestays-monorepo",
  "hooks": {
    "SessionStart": {
      "description": "Load current task context on session start",
      "command": "python .claude/hooks/session_start.py"
    },
    "UserPromptSubmit": {
      "description": "Validate command prerequisites before execution",
      "command": "python .claude/hooks/validate_command.py"
    },
    "PreToolUse": {
      "description": "Enforce agent scope - block edits outside agent boundaries",
      "matcher": "Edit|Write",
      "command": "python .claude/hooks/pre_tool_use.py"
    },
    "PostToolUse": {
      "description": "Update STATE.json after tool execution",
      "matcher": "Bash|Edit|Write",
      "command": "python .claude/hooks/post_tool_use.py"
    },
    "SubagentStop": {
      "description": "Validate subagent work completeness",
      "command": "python .claude/hooks/subagent_stop.py"
    }
  }
}
```

**Notes:**

- All hooks use Python scripts (not bash)
- Scripts located in `.claude/hooks/`
- matcher field filters which tools trigger the hook
- Hooks receive JSON via stdin
- Hooks exit with 0 (allow) or 1 (block)

---

## 5. Git Hooks Installation

Git hooks must be installed to `.git/hooks/` and made executable:

```bash
# Install prepare-commit-msg
cp .claude/git-hooks/prepare-commit-msg .git/hooks/
chmod +x .git/hooks/prepare-commit-msg

# Install post-commit
cp .claude/git-hooks/post-commit .git/hooks/
chmod +x .git/hooks/post-commit

# Install post-checkout
cp .claude/git-hooks/post-checkout .git/hooks/
chmod +x .git/hooks/post-checkout
```

**Note:** Git hooks are NOT in `.claude/hooks/` (that's for Claude CLI hooks). Git hooks should be stored in `.claude/git-hooks/` as templates, then copied to `.git/hooks/`.

---

## 6. When Git Hooks vs Claude CLI Hooks

### Use Git Hooks When:

- ✅ Operation is purely git-related
- ✅ Must run in git subprocess
- ✅ Must modify git internals (commit messages, etc.)
- ✅ Must be fast and deterministic
- ✅ No Claude context needed

**Examples:**

- Auto-formatting commit messages
- Creating git metadata mappings
- Updating files on branch switch

### Use Claude CLI Hooks When:

- ✅ Need Claude context (agents, tasks, skills)
- ✅ Need to validate before Claude acts
- ✅ Need to block Claude operations
- ✅ Need to coordinate agents
- ✅ Need to update STATE.json

**Examples:**

- Loading task context on session start
- Blocking edits outside agent scope
- Validating subagent completeness
- Enforcing SDLC workflow
- Tracking tool usage in STATE.json

### Use BOTH When:

- ✅ Need both git-level and Claude-level automation
- ✅ Need git hooks for speed, Claude hooks for validation
- ✅ Systems complement rather than duplicate

**Example:**

- Git prepare-commit-msg: Fast commit message formatting
- Claude PostToolUse: Track commit in STATE.json with full context

---

## 7. Summary of Changes from Original Plan

| Aspect                | Original Plan           | Updated Plan               | Reason                                   |
| --------------------- | ----------------------- | -------------------------- | ---------------------------------------- |
| Git hooks             | 3 hooks                 | 3 hooks (kept)             | Still valuable for git operations        |
| Claude CLI hooks      | 0 hooks                 | 5 hooks (added)            | Missing from original, critical for SDLC |
| Hook scripts language | Bash                    | Python                     | Better JSON handling, cross-platform     |
| Agent enforcement     | Mentioned, not enforced | PreToolUse hook blocks     | Hard enforcement, not suggestions        |
| Session context       | Manual                  | SessionStart auto-loads    | Automation removes cognitive load        |
| Subagent validation   | Manual                  | SubagentStop validates     | Ensures completeness                     |
| Command validation    | None                    | UserPromptSubmit validates | Prevents invalid operations              |

---

## 8. Implementation Checklist

**Git Hooks:**

- [ ] Create `.claude/git-hooks/` directory
- [ ] Write `prepare-commit-msg` script
- [ ] Write `post-commit` script
- [ ] Write `post-checkout` script
- [ ] Test each hook independently
- [ ] Install to `.git/hooks/` and make executable

**Claude CLI Hooks:**

- [ ] Create `.claude/hooks/` directory
- [ ] Write `session_start.py`
- [ ] Write `validate_command.py`
- [ ] Write `pre_tool_use.py`
- [ ] Write `post_tool_use.py`
- [ ] Write `subagent_stop.py`
- [ ] Configure in `.claude/settings.json`
- [ ] Test each hook with dummy tasks

**Integration Testing:**

- [ ] Test SessionStart with existing task
- [ ] Test PreToolUse blocking (try editing apps/server/ from main LLM)
- [ ] Test SubagentStop validation (spawn agent, check warnings)
- [ ] Test git hooks with commits
- [ ] Test both systems together in complete workflow

**CI Enforcement:**

- [ ] Create GitHub Actions workflow file
- [ ] Configure CI to run all validation hooks
- [ ] Test CI enforcement on PR
- [ ] Verify --no-verify bypass is prevented
- [ ] Document CI setup in project README

---

## 9. CI Enforcement Layer (Server-Side Validation)

### 9.1 Philosophy: Immutable Compliance

**Friction as a Feature — Reaffirmed:**

The local hooks provide client-side validation, but developers can bypass them with `--no-verify`. CI enforcement closes this gap by creating an **immutable compliance layer** that cannot be bypassed.

**Key Principle:** Server-side validation converts "soft" local enforcement into **guaranteed compliance**. The system now ensures reproducibility across all developers and LLM agents, regardless of local configuration.

### 9.2 CI Pipeline Configuration

**File:** `.github/workflows/sdlc-validation.yml`

```yaml
name: SDLC Validation

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  validate-sdlc:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0 # Full history for git analysis

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Validate commit messages
        run: |
          # Check all commits in PR follow conventional commits
          for commit in $(git rev-list origin/${{ github.base_ref }}..HEAD); do
            msg=$(git log --format=%B -n 1 $commit)
            python .claude/scripts/git_commit_validate.py "$msg"
          done

      - name: Validate STATE.json integrity
        run: |
          # Find all task STATE.json files
          for state_file in .claude/tasks/*/STATE.json; do
            if [ -f "$state_file" ]; then
              task_id=$(basename $(dirname "$state_file"))
              python .claude/skills/docs-stories/scripts/task_validate_state.py "$task_id"
            fi
          done

      - name: Validate commit-task mapping
        run: |
          # Ensure all commits are mapped to tasks
          python .claude/scripts/validate_commit_task_mapping.py

      - name: Run tests
        run: |
          # Backend tests
          cd apps/server
          pytest tests/ --cov=src --cov-report=json
          cd ../..

          # Frontend tests
          cd apps/frontend
          npm test -- --coverage --json
          cd ../..

      - name: Validate coverage delta
        run: |
          # Check coverage hasn't decreased
          python .claude/skills/docs-stories/scripts/coverage_delta_check.py \
            --backend apps/server/coverage.json \
            --frontend apps/frontend/coverage/coverage-summary.json

      - name: Validate agent ownership
        run: |
          # Check all modified files have valid owners
          for file in $(git diff --name-only origin/${{ github.base_ref }}...HEAD); do
            if [[ -f "$file" ]]; then
              bash .claude/skills/docs-stories/scripts/get_agent_for_dir.sh "$file"
            fi
          done

      - name: Run quality gates
        run: |
          # Lint, type check, security scan
          python .claude/skills/docs-stories/scripts/lint_check.py backend
          python .claude/skills/docs-stories/scripts/lint_check.py frontend
          python .claude/skills/docs-stories/scripts/type_check.py backend
          python .claude/skills/docs-stories/scripts/type_check.py frontend
          python .claude/skills/docs-stories/scripts/security_scan.py
```

### 9.3 What CI Enforces

**1. Commit Message Format**

- Every commit must follow conventional commits standard
- Format: `type(scope): message [TASK-xxx/US-xxx]`
- Invalid commits block the PR

**2. STATE.json Integrity**

- All task STATE.json files must be valid
- Required fields present
- Data types correct
- No orphan tasks

**3. Commit-Task Mapping**

- Every commit must be linked to a task
- Task IDs in commit messages must reference existing tasks
- Prevents commits outside SDLC workflow

**4. Test Coverage**

- Coverage must not decrease
- New code must be tested
- Coverage baseline enforced (default: 80%)

**5. Agent Ownership**

- All modified files must have valid owners
- Ownership declared in README.md files
- Prevents orphan files

**6. Quality Gates**

- Linting must pass (ruff, eslint)
- Type checking must pass (mypy, tsc)
- Security scans must pass (bandit, npm audit)

### 9.4 Impact on Workflow

**Before CI Enforcement:**

```
Developer commits with --no-verify
  ↓
Bypasses local hooks
  ↓
Invalid commit reaches repository
  ↓
Manual cleanup required
```

**After CI Enforcement:**

```
Developer commits with --no-verify
  ↓
Bypasses local hooks (allowed)
  ↓
Creates PR
  ↓
CI runs all validations
  ↓
PR blocked if validation fails
  ↓
Developer must fix before merge
```

### 9.5 Benefits

**1. Immutable Compliance**

- No way to bypass validation
- Guarantees all commits follow standards
- Ensures quality across team

**2. Reproducibility**

- Same validation runs locally and in CI
- Consistent results regardless of environment
- Prevents "works on my machine" issues

**3. Team Protection**

- Catches mistakes before they reach main branch
- Prevents incomplete work from being merged
- Maintains codebase integrity

**4. Automation Trust**

- CI becomes source of truth
- Local hooks are "helpful guides"
- Server enforces the rules

### 9.6 Philosophical Note

CI enforcement reinforces the **"Friction as Feature"** philosophy:

> _"System friction is DELIBERATE design, not developer inconvenience. It ensures contextual integrity and prevents improvisation."_

The CI layer makes this friction **immutable** — it cannot be bypassed, even accidentally. This creates a **verifiable, self-documenting workflow** where every change has:

- Proven task context (STATE.json)
- Conventional commit message
- Test coverage
- Valid ownership
- Quality gates passed

No emergency path exists by design. Every change passes through context, proof, and story.

---

## 10. Conclusion

**Key Insight:** Git hooks and Claude Code CLI hooks serve different, complementary purposes. The original plan only had git hooks, which are insufficient for SDLC workflow automation.

**Critical Addition:** Claude CLI hooks enable:

1. Agent scope enforcement (PreToolUse)
2. Automatic context loading (SessionStart)
3. Work completeness validation (SubagentStop)
4. Command prerequisite checking (UserPromptSubmit)
5. Comprehensive state tracking (PostToolUse)

**Implementation Impact:**

- Git hooks: ~100 lines total (3 scripts)
- Claude CLI hooks: ~400 lines total (5 Python scripts)
- Total automation: ~500 lines of deterministic validation
- Result: SDLC workflow that "runs itself" with proper validation at every step

**Next Steps:**

1. Implement all 8 hooks (3 git + 5 Claude CLI)
2. Test independently
3. Test integrated workflow
4. Document hook behavior for team
5. Consider additional hooks as needs arise (PreCompact, Notification, etc.)

---

**End of Hooks Review**
