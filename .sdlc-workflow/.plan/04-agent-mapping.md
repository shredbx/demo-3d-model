# Agent-Skill Mapping & Enforcement Rules

**Created:** 2025-11-01 12:19
**Purpose:** Define mandatory agent-skill relationships, directory ownership, and enforcement mechanisms
**Status:** Architecture Specification

---

## Executive Summary

This document addresses the critical requirement:

> "Agents should have a complete list of skills they HAVE to use when they see a certain task. CLAUDE.md should list agents and tell them which agent responsible for which subsystem and ALWAYS invoke subagent of scoped area for any work inside that directory, main LLM thread should never break any SDLC flow for even small task related to the codebase."

**Key Principles:**

1. **Directory Ownership:** Each agent owns specific directories
2. **Mandatory Skills:** Each agent must use specific skills (not optional)
3. **Hard Enforcement:** PreToolUse hook BLOCKS incorrect agent usage
4. **No Direct Edits:** Main LLM NEVER edits code, only orchestrates

---

## 1. Directory Ownership Table

### 1.1 Ownership Rules

| Directory Pattern          | Owner Agent  | Access Control                            |
| -------------------------- | ------------ | ----------------------------------------- |
| `apps/server/**`           | dev-backend  | EXCLUSIVE (PreToolUse hook blocks others) |
| `tests/backend/**`         | dev-backend  | EXCLUSIVE                                 |
| `apps/frontend/**`         | dev-frontend | EXCLUSIVE                                 |
| `tests/frontend/**`        | dev-frontend | EXCLUSIVE                                 |
| `docker/**`                | devops-infra | EXCLUSIVE                                 |
| `Makefile`                 | devops-infra | EXCLUSIVE                                 |
| `docker-compose*.yml`      | devops-infra | EXCLUSIVE                                 |
| `.claude/tasks/**`         | ANY agent    | SHARED (task management)                  |
| `.sdlc-workflow/**`        | ANY agent    | SHARED (documentation)                    |
| `README.md`, `*.md` (root) | ANY agent    | SHARED                                    |

### 1.2 Enforcement Mechanism

**PreToolUse Hook:**

- Intercepts ALL Edit/Write operations
- Checks file path against ownership table
- Validates current agent matches required agent
- BLOCKS operation if mismatch
- Provides clear error message with remediation

**Example:**

```
Main LLM attempts: Edit apps/server/src/auth/routes.py

PreToolUse hook:
  → File: apps/server/src/auth/routes.py
  → Required agent: dev-backend
  → Current agent: none (main LLM)
  → ❌ BLOCKED

Error message:
"Cannot edit apps/server/src/auth/routes.py - requires dev-backend agent
 Action: Use Task tool to spawn dev-backend agent, or use /task-implement backend"
```

### 1.3 Dual Ownership Model

**Philosophy: Centralized + Declarative**

The ownership system uses a **dual approach**:

1. **Centralized Table (Above):** Provides quick reference and high-level rules
2. **Declarative README.md (Section 10):** Each directory declares its owner via YAML frontmatter

**Why Both?**

- **Table:** Fast lookup, overview, enforcement baseline
- **README.md:** Discoverable, visible to all tools/LLMs, self-documenting, no separate ownership files cluttering `.claude/`

**PreToolUse Hook Resolution:**

1. Try to find owner from README.md (walk up directory tree)
2. If not found, fall back to table lookup
3. Both methods must agree (if both provide owner)

**Ownership Philosophy (Reaffirmed):**

- Ownership centralized in PatternBook (this document provides the table)
- `.claude/` contains only core tools, not per-agent configuration
- README.md ownership is declarative and visible (fits "documentation is authority" principle)
- Agents operate through enforced context (.current_agent validation)

See Section 10 for README.md ownership implementation details.

---

## 2. dev-backend Agent

### 2.1 Agent Definition

**File:** `.claude/agents/dev-backend/AGENT.md`

```markdown
---
name: dev-backend
description: FastAPI backend development agent. Handles ALL backend implementation, testing, and API design. MUST be invoked for ANY work in apps/server/ or tests/backend/.
trigger: Work in apps/server/ or tests/backend/ directories
working_directory: apps/server
---

# dev-backend Agent

## When to Invoke (MANDATORY)

This agent MUST be invoked for:

- ✅ ANY file creation/modification in `apps/server/`
- ✅ ANY file creation/modification in `tests/backend/`
- ✅ API endpoint implementation
- ✅ Database models and migrations
- ✅ Backend business logic
- ✅ Backend testing (pytest)
- ✅ FastAPI configuration
- ✅ Python package management (backend)

**Enforcement:** PreToolUse hook will BLOCK edits to backend files if this agent is not active.

## Directory Ownership

**EXCLUSIVE ownership:**

- `apps/server/**` - All backend code
- `tests/backend/**` - All backend tests

**Working directory:** `apps/server/`

## Mandatory Skills (MUST Use, No Exceptions)

When invoked, this agent MUST use these skills in this order:

### 1. backend-python-fastapi (ALWAYS)

**Purpose:** FastAPI patterns, MCP server integration, route design
**When:** For ANY backend implementation
**Why:** Ensures consistent FastAPI patterns and MCP usage

### 2. backend-architecture (ALWAYS)

**Purpose:** Clean Architecture, Hexagonal Architecture, DDD patterns
**When:** For architectural decisions, domain modeling
**Why:** Maintains clean separation of concerns and domain logic

### 3. backend-async-python (WHEN async/await involved)

**Purpose:** Python asyncio, concurrency, async/await patterns
**When:** Implementing async endpoints, background tasks, concurrent operations
**Why:** Ensures correct async usage and avoids common pitfalls

### 4. backend-python-testing (ALWAYS)

**Purpose:** Pytest patterns, fixtures, mocking, TDD
**When:** Creating or modifying tests (REQUIRED for every implementation)
**Why:** Ensures comprehensive test coverage and quality

### 5. backend-api-design (FOR new endpoints)

**Purpose:** REST/GraphQL design principles, API best practices
**When:** Designing new API endpoints or modifying existing API contracts
**Why:** Ensures intuitive, scalable, maintainable APIs

### 6. backend-python-performance (IF performance-critical)

**Purpose:** Profiling, optimization, performance best practices
**When:** Implementing performance-critical code or optimizing bottlenecks
**Why:** Ensures efficient implementations

## Workflow Pattern

**Typical invocation flow:**

1. Load task context (STATE.json, story, research, plan)
2. Invoke backend-python-fastapi skill → Design approach
3. Invoke backend-architecture skill → Structure domain logic
4. Implement features using FastAPI patterns
5. Invoke backend-python-testing skill → Create tests
6. Run tests to verify implementation
7. Commit with proper message format
8. Return results to main LLM

## Quality Requirements

Before completing, ensure:

- ✅ All new code has type hints
- ✅ All new functions/endpoints have docstrings
- ✅ Tests created/updated (100% of functionality)
- ✅ Tests passing locally
- ✅ No linting errors (ruff)
- ✅ No type checking errors (mypy)
- ✅ Commits made with proper format

## Context Passing

**Receives from main LLM:**

- Task context (story, research, plan)
- Acceptance criteria
- Dependencies identified
- API design requirements

**Returns to main LLM:**

- Files created/modified
- Commits made
- Test results
- Summary for context/backend-done.md (for frontend integration)

## Integration Points

**With Frontend:**

- Document API endpoints created (paths, methods, request/response schemas)
- Specify authentication requirements
- Note any real-time features (WebSockets, SSE)
- Save to `TASK-XXX/context/backend-done.md` for frontend agent

**With DevOps:**

- Note any new dependencies added
- Specify environment variables needed
- Document database migrations created

## Validation (SubagentStop Hook)

When agent completes, SubagentStop hook validates:

- ✅ At least 1 commit made
- ✅ Files in apps/server/ modified
- ✅ Test files created/modified
- ⚠️ Warns if incomplete

## Example Invocation

**Main LLM:**
```

Task tool:
subagent_type: dev-backend
description: Implement admin login API
prompt: |
Story: US-001-auth-login-admin
Requirements: [acceptance criteria]
Research findings: [existing patterns]
Implementation plan: [architecture design]

    Implement backend API for admin login using Clerk for authentication.
    Follow clean architecture patterns and create comprehensive tests.

```

**Agent must:**
1. Read context
2. Invoke backend-python-fastapi → Design endpoint
3. Invoke backend-architecture → Structure auth domain
4. Implement in apps/server/src/auth/
5. Invoke backend-python-testing → Create tests in tests/backend/
6. Run pytest to verify
7. Commit changes
8. Return summary
```

---

### 2.2 Mandatory Skills Checklist

dev-backend agent invocations must validate:

- [ ] backend-python-fastapi loaded for FastAPI patterns
- [ ] backend-architecture loaded for domain design
- [ ] backend-async-python loaded (if async code involved)
- [ ] backend-python-testing loaded for test creation
- [ ] backend-api-design loaded (if new endpoints)
- [ ] Tests created for all new functionality
- [ ] Tests passing
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Commits made

---

## 3. dev-frontend Agent

### 3.1 Agent Definition

**File:** `.claude/agents/dev-frontend/AGENT.md`

```markdown
---
name: dev-frontend
description: SvelteKit 5 frontend development agent. Handles ALL frontend implementation, component creation, and UI testing. MUST be invoked for ANY work in apps/frontend/ or tests/frontend/.
trigger: Work in apps/frontend/ or tests/frontend/ directories
working_directory: apps/frontend
---

# dev-frontend Agent

## When to Invoke (MANDATORY)

This agent MUST be invoked for:

- ✅ ANY file creation/modification in `apps/frontend/`
- ✅ ANY file creation/modification in `tests/frontend/`
- ✅ Svelte component creation/modification
- ✅ SvelteKit routes implementation
- ✅ Frontend state management
- ✅ UI/UX implementation
- ✅ Frontend testing (Vitest, Playwright)
- ✅ Frontend package management

**Enforcement:** PreToolUse hook will BLOCK edits to frontend files if this agent is not active.

## Directory Ownership

**EXCLUSIVE ownership:**

- `apps/frontend/**` - All frontend code
- `tests/frontend/**` - All frontend tests

**Working directory:** `apps/frontend/`

## Mandatory Skills (MUST Use)

### 1. frontend-svelte (ALWAYS)

**Purpose:** SvelteKit 5 patterns, Svelte 5 runes, component architecture
**When:** For ANY frontend implementation
**Why:** Ensures correct Svelte 5 usage and modern reactive patterns

**MCP Integration:**

- frontend-svelte skill uses mcp\_\_svelte for official documentation
- Automatically fetches relevant docs sections based on task
- Validates Svelte code using svelte-autofixer
- Can generate playground links for component examples

### 2. docs-stories (ALWAYS)

**Purpose:** Task management, STATE.json updates
**When:** Recording work, updating task state
**Why:** Maintains task tracking and context

## Workflow Pattern

1. Load task context (story, research, plan, **backend-done.md**)
2. Invoke frontend-svelte skill → Load relevant Svelte docs
3. Design component structure
4. Implement components/routes using Svelte 5 runes
5. Create/update tests (Vitest, Playwright)
6. Run tests to verify
7. Commit with proper message format
8. Return results

## Quality Requirements

Before completing, ensure:

- ✅ All components use Svelte 5 runes (not legacy reactivity)
- ✅ Proper TypeScript types
- ✅ Component tests created/updated
- ✅ E2E tests for critical flows
- ✅ Tests passing locally
- ✅ No linting errors (eslint)
- ✅ No type checking errors (tsc)
- ✅ Commits made

## Context Passing

**Receives from main LLM:**

- Task context (story, research, plan)
- Backend API documentation (from context/backend-done.md)
- UI/UX requirements
- Acceptance criteria

**Returns to main LLM:**

- Files created/modified
- Commits made
- Test results
- Routes/components added

## Backend Integration

**Reads:** `TASK-XXX/context/backend-done.md`

This file contains:

- API endpoints available (paths, methods, schemas)
- Authentication requirements
- Real-time features (if any)
- Integration points

Agent uses this to:

- Create correct API client calls
- Implement proper error handling
- Set up authentication flows
- Integrate WebSockets/SSE if needed

## Validation (SubagentStop Hook)

When agent completes, SubagentStop hook validates:

- ✅ At least 1 commit made
- ✅ Files in apps/frontend/ modified
- ✅ Test files created/modified
- ⚠️ Warns if incomplete

## Example Invocation

**Main LLM:**
```

Task tool:
subagent_type: dev-frontend
description: Implement admin login UI
prompt: |
Story: US-001-auth-login-admin
Backend API: /api/auth/login (POST)
Requirements: [acceptance criteria]

    Backend context:
    - Endpoint: POST /api/auth/login
    - Request: { email: string, password: string }
    - Response: { token: string, user: User }
    - Uses Clerk for auth

    Implement admin login page with form validation and error handling.
    Use Svelte 5 runes for state management.

```

**Agent must:**
1. Read context + backend-done.md
2. Invoke frontend-svelte skill
3. Create login route/page component
4. Implement API client integration
5. Create tests
6. Run tests
7. Commit
8. Return summary
```

---

### 3.2 Mandatory Skills Checklist

dev-frontend agent invocations must validate:

- [ ] frontend-svelte loaded for Svelte patterns
- [ ] docs-stories loaded for task management
- [ ] Backend context read (if exists)
- [ ] Components use Svelte 5 runes
- [ ] Tests created
- [ ] Tests passing
- [ ] Type checking passes
- [ ] Commits made

---

## 4. DevOps-Infra Agent

### 4.1 Agent Definition

**File:** `.claude/agents/devops-infra/AGENT.md`

```markdown
---
name: devops-infra
description: Infrastructure and DevOps agent. Handles Docker, Makefile, database migrations, backups, and service orchestration. MUST be invoked for ANY infrastructure changes.
trigger: Work in docker/, Makefile, docker-compose files, or infrastructure-related tasks
working_directory: /
---

# DevOps-Infra Agent

## When to Invoke (MANDATORY)

This agent MUST be invoked for:

- ✅ ANY file creation/modification in `docker/`
- ✅ ANY modification to `Makefile`
- ✅ ANY modification to `docker-compose*.yml`
- ✅ Database migrations (Alembic)
- ✅ Database backups/restoration
- ✅ Service configuration
- ✅ Environment setup
- ✅ Production deployments

**Enforcement:** PreToolUse hook will BLOCK edits to infrastructure files if this agent is not active.

## Directory Ownership

**EXCLUSIVE ownership:**

- `docker/**` - All Docker-related files
- `Makefile` - Build and dev workflows
- `docker-compose*.yml` - Service orchestration

**Working directory:** `/` (project root)

## Mandatory Skills (MUST Use)

### 1. devops-bestays-infra (ALWAYS)

**Purpose:** Bestays-specific infrastructure, Docker Compose, Makefile workflows, service orchestration
**When:** For ANY infrastructure work
**Why:** Ensures consistent infrastructure patterns and service management

### 2. devops-database (FOR database work)

**Purpose:** PostgreSQL, Alembic migrations, backups, pgvector
**When:** Creating/applying migrations, managing database, backups
**Why:** Ensures safe database operations and data integrity

### 3. devops-local-dev (FOR dev environment)

**Purpose:** Local development environment, hot-reload, logs monitoring
**When:** Troubleshooting dev setup, updating dev workflows
**Why:** Maintains smooth developer experience

### 4. docs-stories (ALWAYS)

**Purpose:** Task management
**When:** Recording infrastructure changes
**Why:** Maintains task tracking

## Workflow Pattern

1. Load task context
2. Invoke devops-bestays-infra skill
3. Invoke devops-database skill (if database-related)
4. Implement infrastructure changes
5. Test locally (docker-compose up, make commands)
6. Document changes in task
7. Commit
8. Return results

## Quality Requirements

Before completing, ensure:

- ✅ Services start successfully
- ✅ No breaking changes to existing setup
- ✅ Migrations tested (both up and down)
- ✅ Documentation updated (if workflow changes)
- ✅ Environment variables documented
- ✅ Commits made

## Context Passing

**Receives from main LLM:**

- Task context
- New service requirements
- Migration requirements
- Deployment requirements

**Returns to main LLM:**

- Infrastructure changes made
- New services added
- Migration files created
- Environment variables needed

## Backend/Frontend Integration

**Informs other agents:**

- New environment variables required
- Service URLs/ports changed
- Database schema changes (migrations)
- Dependency updates

## Validation (SubagentStop Hook)

When agent completes, SubagentStop hook validates:

- ✅ At least 1 commit made
- ✅ Infrastructure files modified
- ⚠️ Warns if no testing evidence

## Example Invocation

**Main LLM:**
```

Task tool:
subagent_type: devops-infra
description: Add Redis service for caching
prompt: |
Story: US-042-caching-layer
Requirements: - Add Redis container - Configure for development - Update Makefile with Redis commands

    Add Redis to docker-compose.yml and create Makefile targets for Redis management.

```

**Agent must:**
1. Read context
2. Invoke devops-bestays-infra skill
3. Modify docker-compose.yml
4. Update Makefile
5. Test: docker-compose up
6. Document environment variables
7. Commit
8. Return summary
```

---

### 4.2 Mandatory Skills Checklist

DevOps-infra agent invocations must validate:

- [ ] devops-bestays-infra loaded
- [ ] devops-database loaded (if database work)
- [ ] devops-local-dev loaded (if dev env)
- [ ] docs-stories loaded for task tracking
- [ ] Services tested locally
- [ ] Documentation updated
- [ ] Commits made

---

## 5. CLAUDE.md Enforcement Rules

### 5.1 Updated CLAUDE.md Section

Add this section to `CLAUDE.md`:

```markdown
## Directory Ownership & Agent Enforcement (CRITICAL)

**MANDATORY RULE:** Main LLM must NEVER directly edit codebase files. ALWAYS spawn the appropriate agent.

### Agent Responsibility Table

| Directory/File Pattern                    | Required Agent | Access    |
| ----------------------------------------- | -------------- | --------- |
| apps/server/**, tests/backend/**          | dev-backend    | EXCLUSIVE |
| apps/frontend/**, tests/frontend/**       | dev-frontend   | EXCLUSIVE |
| docker/\*_, Makefile, docker-compose_.yml | devops-infra   | EXCLUSIVE |

### Enforcement

- **PreToolUse Hook:** Automatically BLOCKS Edit/Write operations outside agent scope
- **Violation:** Attempting to edit apps/server/routes.py from main LLM → BLOCKED
- **Correct:** Spawn dev-backend agent, then edit

### Examples

❌ **WRONG:**
```

Main LLM: Edit apps/server/src/auth/routes.py
Result: BLOCKED by PreToolUse hook

```

✅ **CORRECT:**
```

Main LLM: Spawn dev-backend agent
dev-backend agent: Edit apps/server/src/auth/routes.py
Result: ALLOWED (correct agent scope)

```

### Agent Skill Requirements

Each agent MUST use specific skills (mandatory, not optional):

**dev-backend:**
- backend-python-fastapi (ALWAYS)
- backend-architecture (ALWAYS)
- backend-python-testing (ALWAYS)
- backend-async-python (when async)
- backend-api-design (for new endpoints)

**dev-frontend:**
- frontend-svelte (ALWAYS)
- docs-stories (ALWAYS)

**devops-infra:**
- devops-bestays-infra (ALWAYS)
- devops-database (for database work)
- devops-local-dev (for dev environment)
- docs-stories (ALWAYS)

### Workflow Rules

1. **Main LLM Role:** Orchestration ONLY
   - Load task context
   - Determine which agent(s) needed
   - Spawn agents with enriched context
   - Collect results
   - Update task state
   - Coordinate handoffs between agents

2. **Agent Role:** Implementation
   - Receive context from main LLM
   - Load mandatory skills
   - Implement features
   - Create tests
   - Make commits
   - Return results to main LLM

3. **No Direct Implementation:**
   - Main LLM NEVER uses Edit/Write on code files
   - "Even small fixes" must use appropriate agent
   - This ensures skills are ALWAYS used
   - Maintains clean separation of concerns

### SDLC Integration

For task-based workflow:
- `/task-implement backend` → Spawns dev-backend
- `/task-implement frontend` → Spawns dev-frontend
- `/task-implement fullstack` → Spawns dev-backend, then dev-frontend

PreToolUse hook ensures compliance throughout.
```

---

## 6. PreToolUse Hook Implementation

### 6.1 Full Hook Script

**File:** `.claude/hooks/pre_tool_use.py`

```python
#!/usr/bin/env python3
"""
PreToolUse Hook - Enforce Agent Scope Boundaries

CRITICAL: Prevents main LLM from editing code directly.
All code edits must go through appropriate specialized agents.

This hook implements HARD ENFORCEMENT of architectural boundaries.
"""
import sys
import json
import os
from pathlib import Path
from fnmatch import fnmatch

# Agent scope definitions
# Format: {agent_name: [glob_patterns]}
AGENT_SCOPES = {
    'dev-backend': [
        'apps/server/**',
        'apps/server/**/*',
        'tests/backend/**',
        'tests/backend/**/*'
    ],
    'dev-frontend': [
        'apps/frontend/**',
        'apps/frontend/**/*',
        'tests/frontend/**',
        'tests/frontend/**/*'
    ],
    'devops-infra': [
        'docker/**',
        'docker/**/*',
        'Makefile',
        'docker-compose.yml',
        'docker-compose.*.yml'
    ]
}

# Shared/unrestricted paths (any agent can modify)
SHARED_PATHS = [
    '.claude/tasks/**',
    '.sdlc-workflow/**',
    'README.md',
    '*.md',  # Root-level markdown files
    '.gitignore',
    '.env.example'
]

def main():
    """Main hook execution"""
    # Read hook context from stdin
    try:
        hook_context = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If can't read context, allow (fail-open for safety)
        return 0

    tool_name = hook_context.get('tool', '')
    parameters = hook_context.get('parameters', {})

    # Only check Edit and Write tools
    if tool_name not in ['Edit', 'Write']:
        return 0

    file_path = parameters.get('file_path', '')
    if not file_path:
        return 0  # No file path, allow

    # Check if file is in shared/unrestricted scope
    if is_shared_path(file_path):
        return 0  # Shared path, allow

    # Check if file is in protected scope
    required_agent = get_required_agent(file_path)

    if required_agent:
        # File is in protected scope, validate agent
        current_agent = get_current_agent()

        if current_agent != required_agent:
            # BLOCK: Wrong agent or no agent
            print(f"\n{'='*70}")
            print(f"❌ OPERATION BLOCKED - Agent Scope Violation")
            print(f"{'='*70}")
            print(f"\nFile: {file_path}")
            print(f"Required agent: {required_agent}")
            print(f"Current context: {current_agent or 'main LLM (orchestrator)'}")
            print(f"\n{'─'*70}")
            print(f"ACTION REQUIRED:")
            print(f"{'─'*70}")

            if not current_agent:
                # Main LLM trying to edit
                print(f"\n⚠️  Main LLM cannot edit code files directly.")
                print(f"\nOptions:")
                print(f"  1. Use Task tool to spawn {required_agent} agent:")
                print(f"     Task tool:")
                print(f"       subagent_type: {required_agent}")
                print(f"       description: <your task>")
                print(f"       prompt: <detailed instructions>")
                print(f"\n  2. Or use slash command:")
                if required_agent == 'dev-backend':
                    print(f"     /task-implement backend")
                elif required_agent == 'dev-frontend':
                    print(f"     /task-implement frontend")
                elif required_agent == 'devops-infra':
                    print(f"     /task-implement infrastructure")
            else:
                # Wrong agent
                print(f"\n⚠️  Agent {current_agent} cannot modify {required_agent} scope.")
                print(f"\nYou must:")
                print(f"  1. Complete current agent's work")
                print(f"  2. Return to main LLM")
                print(f"  3. Spawn {required_agent} agent for this file")

            print(f"\n{'─'*70}")
            print(f"WHY THIS ENFORCEMENT EXISTS:")
            print(f"{'─'*70}")
            print(f"  • Ensures agents ALWAYS use their mandatory skills")
            print(f"  • Maintains clean separation of concerns")
            print(f"  • Prevents mixing of domain logic")
            print(f"  • Guarantees consistent code quality")
            print(f"{'='*70}\n")

            return 1  # Block operation

    # Not in protected scope, or correct agent
    return 0  # Allow operation

def is_shared_path(file_path):
    """Check if path is in shared/unrestricted scope"""
    path = Path(file_path)

    for pattern in SHARED_PATHS:
        if path.match(pattern):
            return True

    return False

def get_required_agent(file_path):
    """Determine which agent is required for this file path"""
    path = Path(file_path)

    for agent, patterns in AGENT_SCOPES.items():
        for pattern in patterns:
            if path.match(pattern):
                return agent

    return None  # No agent required (unrestricted file)

def get_current_agent():
    """
    Determine current agent context

    Checks multiple sources to identify active agent:
    1. Environment variable (set by Task tool)
    2. .claude/tasks/.current_agent file
    3. Agent marker in session context
    """
    # Method 1: Environment variable (most reliable)
    agent = os.environ.get('CLAUDE_CURRENT_AGENT')
    if agent:
        return agent

    # Method 2: Current agent file
    agent_file = Path('.claude/tasks/.current_agent')
    if agent_file.exists():
        return agent_file.read_text().strip()

    # Method 3: Check if we're in subprocess (subagent context)
    # This is set by Claude Code when spawning agents
    if os.environ.get('CLAUDE_SUBAGENT'):
        return os.environ.get('CLAUDE_SUBAGENT')

    return None  # Main LLM context

if __name__ == "__main__":
    sys.exit(main())
```

---

### 6.2 Agent Context Tracking

To enable PreToolUse hook to detect current agent, agents must set context markers:

**Option 1: Environment Variable (Preferred)**

Task tool automatically sets when spawning agents:

```bash
export CLAUDE_CURRENT_AGENT=dev-backend
```

**Option 2: Context File**

Agents write to `.claude/tasks/.current_agent`:

```python
# When agent starts
Path('.claude/tasks/.current_agent').write_text('dev-backend')

# When agent completes
Path('.claude/tasks/.current_agent').unlink(missing_ok=True)
```

---

## 7. Validation & Testing

### 7.1 Testing Agent Enforcement

**Test 1: Main LLM blocked from backend**

```python
# In main LLM context:
Edit apps/server/src/auth/routes.py

# Expected result:
# ❌ BLOCKED by PreToolUse hook
# Error: "Required agent: dev-backend, Current: main LLM"
```

**Test 2: Correct agent allowed**

```python
# Spawn dev-backend agent:
Task tool:
  subagent_type: dev-backend
  ...

# In dev-backend context:
Edit apps/server/src/auth/routes.py

# Expected result:
# ✅ ALLOWED (correct agent)
```

**Test 3: Wrong agent blocked**

```python
# In dev-frontend agent context:
Edit apps/server/src/auth/routes.py

# Expected result:
# ❌ BLOCKED
# Error: "Agent dev-frontend cannot modify dev-backend scope"
```

**Test 4: Shared files allowed**

```python
# In any context:
Edit README.md

# Expected result:
# ✅ ALLOWED (shared file)
```

### 7.2 Testing Mandatory Skills

**dev-backend validation:**

```python
# After dev-backend agent completes:
# Check STATE.json agents_used: should include dev-backend
# Check commits: should have backend changes
# Check tests: should have test files

# SubagentStop hook validates:
# ✓ Commits made
# ✓ Files in apps/server/ modified
# ✓ Test files created
```

**dev-frontend validation:**

```python
# After dev-frontend agent completes:
# Similar validation for frontend files
```

---

## 8. Implementation Checklist

**CLAUDE.md Updates:**

- [ ] Add "Directory Ownership & Agent Enforcement" section
- [ ] Include agent responsibility table
- [ ] Document enforcement mechanism
- [ ] Provide examples (wrong vs correct)
- [ ] Specify mandatory skills per agent

**Agent Definitions:**

- [ ] Update dev-backend/AGENT.md with mandatory skills list
- [ ] Update dev-frontend/AGENT.md with mandatory skills list
- [ ] Update devops-infra/AGENT.md with mandatory skills list
- [ ] Add "When to Invoke (MANDATORY)" sections
- [ ] Add quality requirements
- [ ] Add validation criteria

**PreToolUse Hook:**

- [ ] Create .claude/hooks/pre_tool_use.py
- [ ] Configure in .claude/settings.json
- [ ] Test blocking scenarios
- [ ] Test allowing scenarios
- [ ] Verify error messages are helpful

**Agent Context Tracking:**

- [ ] Ensure Task tool sets CLAUDE_CURRENT_AGENT env var
- [ ] Or implement .current_agent file mechanism
- [ ] Test agent detection works correctly

**Validation:**

- [ ] Test main LLM blocked from code edits
- [ ] Test correct agent allowed
- [ ] Test wrong agent blocked
- [ ] Test shared files allowed
- [ ] Verify SubagentStop validates completeness

**README.md Ownership:**

- [ ] Create get_agent_for_dir.sh script
- [ ] Add YAML frontmatter to all apps/\*/README.md files
- [ ] Update PreToolUse hook to use get_agent_for_dir.sh
- [ ] Test ownership resolution
- [ ] Verify script never escapes repo boundary

---

## 9. Summary

### Key Improvements from Original Plan

| Aspect              | Original        | Updated                  | Impact                         |
| ------------------- | --------------- | ------------------------ | ------------------------------ |
| Agent usage         | Suggested       | MANDATORY (enforced)     | Hard enforcement, no bypassing |
| Skill loading       | Optional        | MANDATORY per agent      | Skills always used             |
| Main LLM role       | Could edit code | Orchestration only       | Clean separation               |
| Directory ownership | Informal        | Table + hook enforcement | Clear boundaries               |
| Validation          | Manual          | Automated (hooks)        | Consistent quality             |

### Enforcement Stack

1. **CLAUDE.md:** Documents rules and expectations
2. **Agent AGENT.md:** Specifies mandatory skills
3. **PreToolUse hook:** BLOCKS violations (hard enforcement)
4. **SubagentStop hook:** Validates completeness (soft validation)

### Result

- Main LLM cannot accidentally edit code files
- Agents always use their mandatory skills
- Clean separation of concerns maintained
- Architectural boundaries enforced deterministically
- No human memory required - system enforces itself

---

## 10. Declarative Ownership in README.md

### 10.1 Concept

Each `apps/<app_name>/` directory contains a `README.md` with YAML frontmatter declaring the owner agent:

```markdown
---
owner: dev-backend
---

# Backend Server

This is the FastAPI backend server...
```

### 10.2 Directory Structure Example

```
apps/
├── server/
│   └── README.md  (owner: dev-backend)
├── frontend/
│   └── README.md  (owner: dev-frontend)
└── admin/
    └── README.md  (owner: dev-frontend)

docker/
└── README.md  (owner: devops-infra)
```

### 10.3 Implementation: get_agent_for_dir.sh

**File:** `.claude/skills/docs-stories/scripts/get_agent_for_dir.sh`

```bash
#!/usr/bin/env bash
# get_agent_for_dir.sh
# Walks up directory tree to find owner in README.md YAML frontmatter
# Fails if no owner found before repo root (prevents orphan files)
# Never escapes repo boundary (security)

set -euo pipefail

# Get file path argument (or current directory)
target_path="${1:-.}"

# Resolve to absolute path
target_path=$(cd "$(dirname "$target_path")" && pwd)/$(basename "$target_path")

# Get repo root (hard boundary)
repo_root=$(git rev-parse --show-toplevel 2>/dev/null)

if [[ -z "$repo_root" ]]; then
  echo "❌ Error: Not in a git repository" >&2
  exit 1
fi

# Start at target's directory
if [[ -f "$target_path" ]]; then
  current=$(dirname "$target_path")
else
  current="$target_path"
fi

# Walk up until we find owner or hit repo root
while [[ "$current" != "$repo_root" && "$current" != "/" ]]; do
  readme="$current/README.md"

  if [[ -f "$readme" ]]; then
    # Extract YAML frontmatter (between --- markers)
    owner=$(awk '
      /^---$/ { in_yaml=!in_yaml; next }
      in_yaml && /^owner:/ { sub(/^owner:[[:space:]]*/, ""); print; exit }
    ' "$readme")

    if [[ -n "$owner" ]]; then
      echo "$owner"
      exit 0
    fi
  fi

  # Move up one directory
  current=$(dirname "$current")
done

# Reached repo root without finding owner
echo "❌ Error: No owner found for $target_path" >&2
echo "   Searched up to repo root: $repo_root" >&2
echo "   All files must have an owner declared in README.md" >&2
exit 1
```

### 10.4 Usage Examples

**Example 1: Find owner for file**

```bash
$ ./get_agent_for_dir.sh apps/server/src/auth/routes.py
dev-backend
```

**Example 2: Find owner for directory**

```bash
$ ./get_agent_for_dir.sh apps/frontend/src/routes/
dev-frontend
```

**Example 3: No owner found (error)**

```bash
$ ./get_agent_for_dir.sh some/orphan/file.py
❌ Error: No owner found for /repo/some/orphan/file.py
   Searched up to repo root: /repo
   All files must have an owner declared in README.md
```

### 10.5 Integration with PreToolUse Hook

Update `pre_tool_use.py` to use the script:

```python
def get_required_agent(file_path):
    """Determine which agent is required for this file path"""
    import subprocess
    from pathlib import Path

    # First try: README.md ownership (declarative)
    try:
        result = subprocess.run(
            ['bash', '.claude/skills/docs-stories/scripts/get_agent_for_dir.sh', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        owner = result.stdout.strip()
        if owner:
            return owner
    except subprocess.CalledProcessError:
        # No owner in README.md, fall back to table
        pass

    # Second try: Centralized table lookup (fallback)
    path = Path(file_path)
    for agent, patterns in AGENT_SCOPES.items():
        for pattern in patterns:
            if path.match(pattern):
                return agent

    return None  # No agent required (unrestricted file)
```

### 10.6 Benefits

**1. Discoverable**

- Any tool/LLM can read README.md
- No hidden ownership files
- Self-documenting

**2. Visible**

- Ownership is in documentation where it belongs
- Developers see it when browsing code
- README.md explains what the directory does AND who owns it

**3. Non-intrusive**

- No new config files
- README.md already exists
- Just adds YAML frontmatter

**4. Flexible**

- Can add multiple owners: `owner: [dev-backend, devops-infra]`
- Can add metadata: `reviewers: [senior-dev]`, `ci_required: true`
- Extensible for future needs

**5. Repo-bounded**

- Script never escapes git repo root
- Hard boundary prevents path injection attacks
- Fails explicitly if traversal reaches root without finding owner

### 10.7 README.md Template

**File:** `.claude/templates/app-readme.md`

```markdown
---
owner: <agent-name>
---

# <App Name>

<Description of what this app/module does>

## Owner

This directory is owned by the `<agent-name>` agent.

All modifications must go through this agent:

- Use `/task-implement <domain>` command
- Or spawn agent via Task tool

## Architecture

<Architecture overview>

## Dependencies

<Key dependencies>

## Development

<How to work with this code>
```

### 10.8 Migration Plan

**For Existing Directories:**

```bash
# Add ownership to all apps/*/README.md
echo "---
owner: dev-backend
---
" | cat - apps/server/README.md > temp && mv temp apps/server/README.md

# Repeat for frontend, docker, etc.
```

### 10.9 CI Enforcement

The CI pipeline (from hooks document) validates ownership:

```yaml
- name: Validate agent ownership
  run: |
    # Check all modified files have valid owners
    for file in $(git diff --name-only origin/${{ github.base_ref }}...HEAD); do
      if [[ -f "$file" ]]; then
        bash .claude/skills/docs-stories/scripts/get_agent_for_dir.sh "$file"
      fi
    done
```

If any file lacks an owner, CI fails and PR is blocked.

### 10.10 Philosophical Alignment

This approach aligns with the **"Centralized Ownership Philosophy"**:

- **Centralized:** Table in this document provides canonical ownership rules
- **Declarative:** README.md declares specific ownership at each level
- **Discoverable:** Both humans and LLMs can find ownership easily
- **Enforced:** PreToolUse hook + CI ensure compliance

README.md ownership **complements** the table, not replaces it:

- **Table:** High-level patterns and rules
- **README.md:** Specific directory ownership

Both work together to create a **verifiable, self-documenting ownership system** that prevents orphan files and ensures every change has a responsible agent.

---

**End of Agent-Skill Mapping & Enforcement**
