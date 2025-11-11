# Bestays SDLC: Complete Memory Print Architecture

**Date:** 2025-11-09
**Status:** Comprehensive Reference
**Purpose:** Complete documentation of Bestays SDLC workflow, tools, patterns, and philosophy

---

## Table of Contents

1. [Philosophy & Core Principles](#1-philosophy--core-principles)
2. [The 5-Phase SDLC Workflow](#2-the-5-phase-sdlc-workflow)
3. [Actors & Responsibilities](#3-actors--responsibilities)
4. [Skills System](#4-skills-system)
5. [Hooks & Automation](#5-hooks--automation)
6. [Slash Commands](#6-slash-commands)
7. [MCP Integrations](#7-mcp-integrations)
8. [Memory Print Chain](#8-memory-print-chain)
9. [Git Workflow](#9-git-workflow)
10. [Task & Story Management](#10-task--story-management)
11. [Multi-Product Strategy](#11-multi-product-strategy)
12. [The Complete Picture: End-to-End Walkthrough](#12-the-complete-picture-end-to-end-walkthrough)

---

## 1. Philosophy & Core Principles

### 1.1 Why This SDLC Exists

**THIS SDLC WORKFLOW IS DESIGNED FOR LLM (CLAUDE CODE) ONLY.**

This is a **single developer (user) + LLM (Claude Code)** setup. All SDLC processes exist to:

- Keep the LLM (Claude Code) organized and following patterns
- Prevent LLM mistakes and inconsistencies
- Maintain context across ephemeral sessions
- Ensure reproducible, traceable work
- Enable instant context restoration (<3 minutes)

**Bottom line:** When you see "developer" in documentation, it means the LLM (Claude Code). All processes keep the LLM consistent and effective.

### 1.2 Core Principles

#### Trust but Verify

- We trust AI capabilities, but verify everything
- Scripts use filesystem as source of truth (no complex registries)
- Human review before irreversible operations
- Always include validation steps

#### Memory Print Chain

> Choose solutions that maximize "memory print" for minimal cost. The goal is to restore complete context about any code at any point in time, close to instant.

**Why This Matters:**

- LLM sessions are ephemeral - we lose context constantly
- New developers (human or AI) need to understand "why" not just "what"
- Future changes require understanding trade-offs of current implementation
- Debugging requires knowing original design decisions

**The Chain:**

```
User Story → Task → README → File Header → Comments → Git History
```

Each level provides a different perspective:

- **Git history:** WHAT changed, WHEN, by WHOM
- **Task folder:** WHY we made this change, HOW we implemented it
- **Story file:** WHAT business value this provides
- **File header:** HOW this file fits in architecture
- **Comments:** WHY specific code decisions were made
- **Index:** FAST lookup of everything

#### Coordinator vs Implementer Separation

**YOU (Claude Code coordinator) ARE COORDINATOR ONLY. NEVER IMPLEMENTER.**

✅ **Coordinator CAN:**
- Read files (research, context)
- Plan and coordinate work
- Launch subagents for implementation
- Update workflow docs (`.sdlc-workflow/`, `.claude/`, `CLAUDE.md`)
- Git operations
- Track progress (TodoWrite)
- Create documentation/reports

❌ **Coordinator CANNOT:**
- Edit/Write `apps/server/**` (backend code)
- Edit/Write `apps/frontend/src/**` (frontend code)
- Edit/Write `tests/**` (test files)
- Create implementation files yourself
- "Help" with quick fixes

**Enforcement:** `.claude/hooks/sdlc_guardian.py` blocks coordinator from modifying implementation files.

### 1.3 The Instant Context Problem We're Solving

**Problem:** LLM sessions are ephemeral. After 1 week/month/year, how do you restore full context about a feature?

**Solution:** Memory Print Chain creates a traceable path from high-level business value to low-level implementation decisions.

**Time to Context Restoration:**

- **Without Memory Print:** 30-60 minutes (read code, git log, try to infer reasoning)
- **With Memory Print:** <3 minutes (read story → task → file header → done)

---

## 2. The 5-Phase SDLC Workflow

Every user story follows a consistent 5-phase lifecycle:

```
RESEARCH → PLANNING → IMPLEMENTATION → TESTING → VALIDATION
```

### 2.1 RESEARCH Phase

**Purpose:** Understand the problem and identify existing patterns

**Activities:**
- Use Explore agent to find similar implementations
- Search git history for related features
- Identify dependencies (libraries, services, APIs)
- Analyze existing code patterns
- Document findings in `.claude/tasks/TASK-XXX/research/`

**Command:** `/task-research`

**Deliverables:**
- `research/patterns.md` - Existing patterns found
- `research/dependencies.md` - Required dependencies
- `research/similar-implementations.md` - Related features

**Exit Criteria:**
- Research findings documented
- Patterns identified
- Dependencies known
- Ready to plan architecture

---

### 2.2 PLANNING Phase

**Purpose:** Design implementation approach using Plan agent

**Activities:**
- Design architecture approach
- Determine which subagents needed (backend, frontend, both)
- Create file-by-file implementation plan
- Define testing strategy
- Estimate complexity
- Apply 7 quality gates (mandatory)

**Command:** `/task-plan`

**Quality Gates (MANDATORY):**

1. **Network Operations** - Retry logic, error handling, offline detection
2. **Frontend SSR/UX** - SSR compatibility, hydration, progressive enhancement
3. **Testing Requirements** - Coverage, scenarios, browsers
4. **Deployment Safety** - Risk assessment, rollback, monitoring
5. **Acceptance Criteria** - Technical criteria, story mapping, DoD
6. **Dependencies** - External/internal deps, technical debt
7. **Official Documentation Validation** - Svelte MCP, MDN, vendor docs

**Deliverables:**
- `planning/solution-architecture.md`
- `planning/implementation-spec.md` (file-by-file details)
- `planning/test-plan.md`
- `planning/acceptance-criteria.md`
- `planning/official-docs-validation.md`

**Exit Criteria:**
- User approves plan
- All quality gates passed
- Subagents identified
- Implementation ready to start

---

### 2.3 IMPLEMENTATION Phase

**Purpose:** Build the solution using specialized subagents

**Subagents:**
- **dev-backend-fastapi** - Backend work (`apps/server/**`)
- **dev-frontend-svelte** - Frontend work (`apps/frontend/src/**`)
- **devops-infra** - Infrastructure (`docker/`, `Makefile`, `docker-compose*.yml`)

**Command:** `/task-implement <domain>`

**Workflow:**
1. Coordinator loads context (story, research, plan)
2. Spawns appropriate subagent(s)
3. Subagent implements per spec
4. Subagent creates tests
5. Subagent commits work
6. Coordinator presents results to user
7. **FEEDBACK LOOP:** User can request changes → respawn subagent
8. User approves → move to testing

**Mandatory Skills per Subagent:**

**dev-backend-fastapi MUST use:**
- backend-fastapi (ALWAYS)
- backend-architecture (ALWAYS)
- backend-async-python (when async)
- backend-python-testing (ALWAYS)

**dev-frontend-svelte MUST use:**
- frontend-svelte (ALWAYS)
- Uses Svelte MCP for official docs

**devops-infra MUST use:**
- devops-bestays-infra (ALWAYS)
- devops-database (for DB work)
- devops-local-dev (for dev env)

**Deliverables:**
- Implementation files (code, tests)
- Git commits
- `subagent-reports/<agent>-report.md`

**Exit Criteria:**
- Code implemented per spec
- Tests created
- Commits made
- User approves

---

### 2.4 TESTING Phase

**Purpose:** Verify implementation meets requirements

**Activities:**
- Run backend tests (pytest)
- Run frontend tests (vitest, playwright)
- Validate coverage thresholds
- Test error scenarios
- Verify acceptance criteria

**Deliverables:**
- Test results
- Coverage reports
- Updated STATE.json with test metadata

**Exit Criteria:**
- All tests passing
- Coverage meets baseline
- Acceptance criteria verified

---

### 2.5 VALIDATION Phase

**Purpose:** Final quality checks before completion

**Activities:**
- Lint check (ruff, eslint)
- Type check (mypy, tsc)
- Security scan (bandit)
- Acceptance criteria validation
- Story-to-implementation traceability check

**Deliverables:**
- Quality gate results in STATE.json
- Validation report

**Exit Criteria:**
- All quality gates passed
- Ready for PR/merge

---

## 3. Actors & Responsibilities

### 3.1 Coordinator (Main Claude Code)

**Role:** Orchestration ONLY (no implementation)

**Responsibilities:**
- Load task context
- Determine which subagent(s) needed
- Spawn agents with enriched context
- Collect results
- Update task state (via docs-stories)
- Coordinate handoffs between agents
- Git operations (after implementation)

**Tools:**
- TodoWrite (track progress)
- Task tool (spawn subagents)
- docs-stories skill (CRUD operations)
- Memory MCP (load patterns)

**Boundaries (enforced by hook):**
- ❌ Cannot edit `apps/server/**`
- ❌ Cannot edit `apps/frontend/src/**`
- ❌ Cannot edit `tests/**`
- ✅ Can edit `.claude/**`, `.sdlc-workflow/**`, `CLAUDE.md`, `README.md`

---

### 3.2 dev-backend-fastapi Agent

**Ownership:** `apps/server/**`, `tests/backend/**`

**Mandatory Skills:**
1. backend-fastapi (ALWAYS) - FastAPI patterns, MCP server integration
2. backend-architecture (ALWAYS) - Clean Architecture, Hexagonal, DDD
3. backend-async-python (when async) - asyncio, concurrency
4. backend-python-testing (ALWAYS) - pytest, fixtures, mocking

**Quality Requirements:**
- ✅ All new code has type hints
- ✅ All functions have docstrings
- ✅ Tests created/updated (100% of functionality)
- ✅ Tests passing
- ✅ No linting errors (ruff)
- ✅ No type errors (mypy)

**Context Received:**
- Task context (story, research, plan)
- Acceptance criteria
- Dependencies identified
- API design requirements

**Context Returned:**
- Files created/modified
- Commits made
- Test results
- Summary for `context/backend-done.md` (for frontend integration)

---

### 3.3 dev-frontend-svelte Agent

**Ownership:** `apps/frontend/**`, `tests/frontend/**`

**Mandatory Skills:**
1. frontend-svelte (ALWAYS) - SvelteKit 5, Svelte 5 runes, component architecture
   - **MCP Integration:** Uses `mcp__svelte` for official documentation
   - Automatically fetches relevant docs based on task
   - Validates Svelte code using svelte-autofixer

**Quality Requirements:**
- ✅ All components use Svelte 5 runes (not legacy reactivity)
- ✅ Proper TypeScript types
- ✅ Component tests created/updated
- ✅ E2E tests for critical flows
- ✅ No linting errors (eslint)
- ✅ No type errors (tsc)

**Context Received:**
- Task context (story, research, plan)
- **Backend API documentation** (from `context/backend-done.md`)
- UI/UX requirements
- Acceptance criteria

**Context Returned:**
- Files created/modified
- Commits made
- Test results
- Routes/components added

---

### 3.4 devops-infra Agent

**Ownership:** `docker/**`, `Makefile`, `docker-compose*.yml`

**Mandatory Skills:**
1. devops-bestays-infra (ALWAYS) - Docker, Makefile, service orchestration
2. devops-database (for DB work) - Alembic, backups, pgvector
3. devops-local-dev (for dev env) - Hot-reload, logs monitoring

**Quality Requirements:**
- ✅ Services start successfully
- ✅ No breaking changes to existing setup
- ✅ Migrations tested (up and down)
- ✅ Documentation updated
- ✅ Environment variables documented

---

### 3.5 Enforcement: sdlc_guardian.py Hook

**File:** `.claude/hooks/sdlc_guardian.py`

**Trigger:** Before every Edit/Write tool use

**Logic:**
1. Check if file is in protected scope (implementation files)
2. Determine required agent for file path
3. Check current agent context
4. If mismatch → BLOCK operation with helpful error

**Example Block Message:**
```
🚨 SDLC WORKFLOW VIOLATION
❌ Coordinator cannot modify implementation files!

📄 File: apps/server/src/auth/routes.py
🤖 Use: Task(subagent_type="dev-backend-fastapi", ...)

💡 Remember: You are COORDINATOR only.
   - Launch subagents for ALL implementation work
```

---

## 4. Skills System

### 4.1 What Are Skills?

Skills are reusable knowledge modules that agents load to perform specific tasks. They provide:
- Framework-specific patterns
- Best practices
- Tool usage guidance
- Quality standards

### 4.2 Mandatory Skills (ALL agents/tasks)

#### docs-stories

**Purpose:** Complete CRUD for SDLC documentation

**When to Use:**
- Creating/managing stories
- Creating/managing tasks
- Updating task state/phase
- Retrieving context via index

**Key Scripts:**
- `story_create.py` - Create new user story
- `story_find.py` - Find existing stories
- `task_create.py` - Create new task
- `task_list.py` - List tasks for story
- `task_update_state.py` - Update task status
- `task_update_phase.py` - Update task phase
- `task_add_commit.py` - Track commits
- `task_add_file_modified.py` - Track files
- `context_index.py` - Build context index (planned)

**Integration:** ALL task state updates go through docs-stories scripts (never manual file edits).

---

#### planning-quality-gates

**Purpose:** Mandatory checklist for Plan agents

**7 Quality Gates:**

1. **Network Operations** (if applicable)
   - Retry strategy specified
   - Error handling for offline, timeout, blocked, server_error
   - Timeout values justified
   - Loading states defined (0-1s, 1-3s, 3-10s, 10s+)

2. **Frontend SSR/UX** (if applicable)
   - Network ops only in `onMount` or client-side
   - Initial loading state in SSR HTML
   - No flash of incorrect content (FOUC)
   - Progressive enhancement

3. **Testing Requirements** (ALWAYS)
   - Unit tests specified
   - E2E tests specified
   - Error scenarios covered
   - Browser compatibility defined

4. **Deployment Safety** (ALWAYS)
   - Risk level assessed
   - Rollback plan specified
   - Monitoring defined

5. **Acceptance Criteria** (ALWAYS)
   - Technical criteria defined
   - Story mapping complete
   - Definition of Done specified

6. **Dependencies** (ALWAYS)
   - External dependencies identified
   - Internal dependencies documented
   - Technical debt acknowledged

7. **Official Documentation Validation** (ALWAYS)
   - Used `mcp__svelte__list-sections` and `get-documentation`
   - Validated against official Svelte 5 patterns
   - Validated against web standards (MDN)
   - Validated against vendor docs

**Enforcement:** Plan agents MUST reference this skill and verify all applicable checks.

---

#### dev-philosophy

**Purpose:** Development standards and architectural principles

**Key Concepts:**
- SOLID principles
- Design patterns (when to use)
- Domain-Driven Design
- Refactoring practices
- Code smells to avoid
- Testing philosophy (TDD)

**Applies To:** ALL implementation work

---

#### dev-code-quality

**Purpose:** Universal code quality standards

**Standards:**
- Naming conventions
- Function design (single responsibility, max 3-4 params)
- Code organization
- Comments (why, not what)
- Error handling (fail fast, fail clearly)
- Magic numbers (extract to constants)

**Applies To:** ALL implementation work

---

### 4.3 Specialized Skills

#### frontend-svelte

**When:** Svelte/SvelteKit development

**Provides:**
- Svelte 5 runes ($state, $derived, $effect, $props)
- SvelteKit routing and data loading
- Component patterns
- SSR best practices
- MCP integration for official docs

**MCP Usage:**
1. List available docs: `mcp__svelte__list-sections`
2. Fetch relevant sections: `mcp__svelte__get-documentation({ section: [...] })`
3. Validate code: `mcp__svelte__svelte-autofixer`
4. Generate playground link: `mcp__svelte__playground-link`

---

#### backend-fastapi

**When:** FastAPI backend development

**Provides:**
- Clean Architecture patterns
- Hexagonal Architecture (Ports & Adapters)
- Domain-Driven Design (DDD) tactical patterns
- FastAPI-specific patterns
- Async/await best practices

**MCP Usage:**
- `mcp__context7__resolve-library-id({ libraryName: "fastapi" })`
- `mcp__context7__get-library-docs({ context7CompatibleLibraryID: "/fastapi/fastapi" })`

---

#### devops-bestays-infra

**When:** Infrastructure work

**Provides:**
- Docker Compose patterns
- Makefile workflows
- Preflight validation
- Component map (where info lives)
- Troubleshooting index

**Philosophy:** Pointer system (knows WHERE info is, not WHAT it is)

---

## 5. Hooks & Automation

### 5.1 Hook System Overview

Hooks are Python scripts that execute in response to events. They provide:
- Validation
- Automation
- Enforcement
- Context loading

---

### 5.2 session_start.py

**Trigger:** Claude Code session starts

**Purpose:** Load current task context

**Actions:**
1. Find all active tasks (status='in_progress')
2. Read current task from `.claude/tasks/current.txt`
3. Load task STATE.json
4. Display:
   - Current task ID, story ID, phase, status
   - Parallel tasks (if any)
   - Suggested next command

**Output Example:**
```
📋 Current Task: TASK-016
   Story: US-023
   Phase: IMPLEMENTATION
   Status: in_progress
   Branch: feat/TASK-016-US-023

🔀 Parallel Tasks (3 active):
   • TASK-001 (US-001) - PLANNING
     Branch: feat/TASK-001-US-001
   • TASK-007 (US-019) - TESTING
     Branch: feat/TASK-007-US-019

💡 Suggested: /task-implement <domain>
```

---

### 5.3 sdlc_guardian.py (PreToolUse Hook)

**Trigger:** Before every Edit/Write tool use

**Purpose:** Enforce coordinator vs implementer separation

**Logic:**
```python
COORDINATOR_ALLOWED = [
    ".claude/",
    ".sdlc-workflow/",
    "CLAUDE.md",
    "README.md",
    ".gitignore",
    ".env.example",
]

IMPLEMENTATION_PATHS = [
    "apps/server/src/",
    "apps/frontend/src/",
    "tests/",
]

SUBAGENT_MAP = {
    "apps/server/src/": "dev-backend-fastapi",
    "apps/frontend/src/": "dev-frontend-svelte",
    "tests/e2e/": "playwright-e2e-tester",
}
```

**Exit Codes:**
- `0` - Allow (coordinator-allowed file)
- `2` - Block (implementation file, need subagent)

---

### 5.4 validate_command.py (UserPromptSubmit Hook)

**Trigger:** Before command execution

**Purpose:** Validate prerequisites

**Checks:**
- Active task exists (for task commands)
- Story exists (for story-dependent operations)
- Branch naming follows conventions

---

### 5.5 post_tool_use.py

**Trigger:** After Edit/Write/Git operations

**Purpose:** Track changes in STATE.json

**Actions:**
- Add modified files to `files_modified[]`
- Track commits with SHA, message, timestamp
- Update `last_accessed` timestamp

---

### 5.6 subagent_stop.py

**Trigger:** When subagent completes

**Purpose:** Validate completeness

**Checks (by agent type):**

**dev-backend / dev-frontend:**
- ✅ Commits made?
- ✅ Files in correct domain modified?
- ✅ Test files created?

**Explore:**
- ✅ Research files saved?

**Plan:**
- ✅ Planning files saved?
- ✅ Agent assignments specified?

**If incomplete:** ⚠️ Warns but doesn't block (soft validation)

---

## 6. Slash Commands

Slash commands are shortcuts that expand to full prompts.

### 6.1 /story-new

**Purpose:** Create new user story

**Usage:** `/story-new <domain> <feature> <scope>`

**Example:** `/story-new auth login admin`

**Workflow:**
1. Generate story ID (US-XXX)
2. Create story file from template
3. Set default_product, portable, ported_to
4. Return story ID and path

---

### 6.2 /task-new

**Purpose:** Create new task for story

**Usage:** `/task-new <story-id> <task-type>`

**Arguments:**
- `story-id`: US-001
- `task-type`: feat | fix | refactor | test | docs

**Workflow:**
1. Validate story exists
2. Create task ID (TASK-XXX)
3. Create task folder structure
4. Create STATE.json
5. Create git branch: `feat/TASK-XXX-semantic-name-US-YYY`
6. Update `.claude/tasks/current.txt`

---

### 6.3 /task-research

**Purpose:** Research phase

**Workflow:**
1. Update phase to RESEARCH
2. Load task context
3. Spawn Explore agent with "medium" thoroughness
4. Agent finds patterns, dependencies, similar implementations
5. Save findings to `research/`
6. Update phase to RESEARCH complete

---

### 6.4 /task-plan

**Purpose:** Planning phase

**Workflow:**
1. Update phase to PLANNING
2. Load context (story, research)
3. Spawn Plan agent
4. **ITERATIVE REFINEMENT LOOP:**
   - Present plan to user
   - IF user has concerns → discuss → respawn Plan agent
   - IF user approves → continue
5. Save plan to `planning/`
6. Update phase to PLANNING complete
7. Commit planning artifacts

---

### 6.5 /task-implement

**Purpose:** Implementation phase

**Usage:** `/task-implement <domain>`

**Domains:** `backend` | `frontend` | `fullstack`

**Workflow:**
1. Update phase to IMPLEMENTATION
2. Load context (story, research, plan)
3. Determine subagent(s) needed
4. If `fullstack`:
   - Spawn dev-backend first
   - Save backend context to `context/backend-done.md`
   - Then spawn dev-frontend (with backend context)
5. **POST-JOB DISCUSSION LOOP:**
   - Present results to user
   - IF user requests changes → respawn subagent
   - IF user approves → continue
6. Update phase to IMPLEMENTATION complete

---

## 7. MCP Integrations

MCP (Model Context Protocol) provides external tools and data sources.

### 7.1 Memory MCP

**Purpose:** Knowledge graph for patterns and learnings

**Tools:**
- `mcp__memory__read_graph` - Read entire graph
- `mcp__memory__search_nodes` - Search by query
- `mcp__memory__open_nodes` - Load specific entities
- `mcp__memory__create_entities` - Store new patterns
- `mcp__memory__add_observations` - Update entities

**When to Use:**
- Start of session (load context)
- Before planning (load quality gates)
- Before frontend implementation (load Svelte 5 patterns)
- When discovering new patterns (store for future)

**Example Entities:**
- "SDLC Workflow Pattern"
- "Coordinator Role - CRITICAL"
- "Planning Quality Gates - 7 Gates"
- "Svelte 5 Mounting Pattern - onMount vs $effect"

**Usage:**
```javascript
mcp__memory__open_nodes({ names: [
  "SDLC Workflow Pattern",
  "Coordinator Role - CRITICAL",
  "Planning Quality Gates - 7 Gates",
  "Svelte 5 Mounting Pattern - onMount vs $effect"
]})
```

---

### 7.2 Svelte MCP

**Purpose:** Official Svelte 5 and SvelteKit documentation

**Tools:**
- `mcp__svelte__list-sections` - List all available docs with use_cases
- `mcp__svelte__get-documentation` - Fetch specific sections
- `mcp__svelte__svelte-autofixer` - Validate Svelte code
- `mcp__svelte__playground-link` - Generate playground link

**Workflow:**
1. **List sections** to understand what's available and when each is useful
2. **Analyze use_cases** to identify relevant sections for current task
3. **Fetch ALL relevant sections** at once
4. **Validate code** against official patterns
5. **Generate playground** for component examples (if needed)

**Example:**
```javascript
// Step 1: List sections
mcp__svelte__list-sections()

// Step 2: Fetch relevant docs
mcp__svelte__get-documentation({
  section: ["$state", "$effect", "Lifecycle hooks"]
})

// Step 3: Validate code
mcp__svelte__svelte-autofixer({
  code: "...",
  desired_svelte_version: 5,
  filename: "Component.svelte"
})
```

---

### 7.3 Context7 MCP

**Purpose:** Up-to-date library documentation

**Tools:**
- `mcp__context7__resolve-library-id` - Find library ID
- `mcp__context7__get-library-docs` - Fetch docs

**Workflow:**
1. Resolve library name to Context7 ID
2. Fetch documentation with topic focus

**Example:**
```javascript
// Step 1: Resolve
mcp__context7__resolve-library-id({ libraryName: "fastapi" })
// Returns: "/fastapi/fastapi"

// Step 2: Fetch docs
mcp__context7__get-library-docs({
  context7CompatibleLibraryID: "/fastapi/fastapi",
  topic: "dependency injection",
  tokens: 5000
})
```

---

### 7.4 Playwright MCP

**Purpose:** Browser automation for E2E testing

**Tools:**
- `mcp__playwright__browser_navigate` - Navigate to URL
- `mcp__playwright__browser_click` - Click elements
- `mcp__playwright__browser_snapshot` - Accessibility snapshot
- `mcp__playwright__browser_evaluate` - Execute JavaScript

**When to Use:** E2E testing with playwright-e2e-tester agent

---

### 7.5 Sequential Thinking MCP

**Purpose:** Dynamic problem-solving through chain of thought

**Tool:** `mcp__sequential-thinking__sequentialthinking`

**When to Use (MANDATORY):**
- Planning SDLC implementations
- Designing architecture
- Making architectural decisions
- Analyzing complex problems
- Validating approaches

**Pattern:** Think → Design → Specify → Spawn subagent → Validate

---

## 8. Memory Print Chain

### 8.1 The Chain

```
User Story → Task → README → File Header → Comments → Git History
```

Each link provides different information:

**User Story** (`.sdlc-workflow/stories/domain/US-XXX-feature.md`)
- Business value
- Acceptance criteria
- Product metadata (bestays/realestate)

**Task Folder** (`.claude/tasks/TASK-XXX/`)
- Implementation decisions
- Research findings
- Planning artifacts
- Subagent reports

**README.md** (per-directory)
- Module purpose
- Architecture overview
- Dependencies
- Development notes

**File Header** (every file)
- Design pattern used
- Architecture layer
- Dependencies (external, internal)
- Trade-offs (pros, cons, when to revisit)
- Integration points
- Testing notes

**Comments** (inline)
- Why specific decisions were made
- Non-obvious business rules
- Gotchas and workarounds

**Git History**
- WHAT changed
- WHEN it changed
- Which story/task it belongs to

---

### 8.2 File Header Template

```python
"""
[Component Name] - [Brief Description]

Design Pattern: [Pattern Name]
Architecture Layer: [API/Service/Model/Component]

Dependencies:
  External: [npm/pip packages]
  Internal: [local imports]

Integration Points:
  - [How this connects to other parts]
  - [API endpoints, database tables, etc.]

Trade-offs:
  Pro: [Benefits of this approach]
  Con: [Limitations or technical debt]
  When to revisit: [Conditions that would invalidate this choice]

Testing Notes:
  - [How to test this]
  - [What to watch for]
"""
```

---

### 8.3 Trade-offs Documentation Pattern

Every significant technical decision must document:

1. **Why we chose this approach** (benefits)
2. **What we gave up** (cons, limitations)
3. **When to revisit** (conditions that would invalidate this choice)

**Example:**
```markdown
# Decision: Use Clerk for Authentication (US-001 TASK-001)

## Why We Chose Clerk
- Fast integration (< 1 day vs 1 week for custom auth)
- Built-in security best practices (OWASP compliant)
- Multi-product support (bestays + realestate)

## What We Gave Up
- Vendor lock-in (migration cost if switching providers)
- Monthly cost at scale ($0.02/user/month after 10k users)
- Less customization than custom auth

## When to Revisit
- If Clerk pricing becomes >$500/month
- If we need custom auth flows Clerk doesn't support
- If compliance requires on-premise auth
- If Clerk has >3 major outages per year

## Migration Path (If Revisiting)
- Estimated effort: 2-3 weeks
- Replace Clerk SDK with custom auth service
- Migrate user data from Clerk to database
```

---

### 8.4 Memory Print in Action

**Scenario:** New session, need to understand auth flow (zero context)

**Step 1: Check git history**
```bash
git log --grep="auth" --oneline
# 509a519 feat: implement login flow (US-001 TASK-001-clerk-mounting)
```

**Step 2: Read task folder**
```
.claude/tasks/TASK-001-clerk-mounting/
├── README.md (What: Mount Clerk SDK for authentication)
├── planning/decisions.md (Why: Chose Clerk over Auth0)
└── subagent-reports/dev-backend-fastapi-report.md (How: Implementation)
```

**Step 3: Read story file**
```
.sdlc-workflow/stories/auth/US-001-login-flow-validation.md
- Business value: Secure authentication for users
- Acceptance criteria: Valid credentials authenticate, invalid rejected
```

**Step 4: Read file header**
```python
# apps/server/core/clerk.py
"""
Design Pattern: Singleton
Architecture Layer: Core Service
Trade-offs:
  - Vendor lock-in vs faster development
  - When to revisit: If Clerk pricing becomes prohibitive
"""
```

**Time to Full Context: ~2-5 minutes** (vs. 30-60 minutes without Memory Print)

---

## 9. Git Workflow

### 9.1 Branch Naming Convention

**Pattern:** `<type>/TASK-<number>-<semantic-name>-US-<story-id>`

**Examples:**
- `feat/TASK-001-clerk-mounting-US-001`
- `fix/TASK-002-login-validation-US-001`
- `refactor/TASK-003-auth-cleanup-US-001`

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

**Enforcement:** `validate_branch.py` script + PreToolUse hook

---

### 9.2 Commit Message Format

```
<type>(<scope>): <description> (US-XXX TASK-YYY-semantic-name)

Subagent: <which-subagent>
Product: <bestays | realestate>
Files: <list-of-files>

<detailed description>

Story: US-XXX
Task: TASK-YYY-semantic-name

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Example:**
```
feat(auth): implement login flow (US-001 TASK-001-clerk-mounting)

Subagent: dev-backend-fastapi
Product: bestays
Files: apps/server/src/auth/routes.py, apps/server/core/clerk.py

Implemented Clerk authentication with email/password login.
Redirects to /home after successful authentication.

Story: US-001
Task: TASK-001-clerk-mounting

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

### 9.3 Git Commit Workflow

When user requests commit:

1. Run `git status` and `git diff` in parallel
2. Draft commit message following format
3. Add relevant files to staging area
4. Create commit with message (using HEREDOC)
5. Run `git status` after commit to verify

**Important:**
- NEVER use git commands with `-i` flag (interactive not supported)
- DO NOT push to remote unless user explicitly asks
- Git hooks (prepare-commit-msg, post-commit) handle automation

---

## 10. Task & Story Management

### 10.1 User Story Structure

**Location:** `.sdlc-workflow/stories/<domain>/US-<number>-<feature>.md`

**Template:**
```markdown
---
id: US-XXX
title: <Feature Title>
domain: <auth|booking|admin|infrastructure>
status: READY|IN_PROGRESS|COMPLETED
default_product: bestays|realestate
portable: true|false
ported_to: []
---

# User Story: <Title>

## Background
[Context and motivation]

## Acceptance Criteria
AC-1: [Criterion]
AC-2: [Criterion]

## Porting Notes (if portable: true)
**Portable Elements:**
- [What can be ported]

**Product-Specific Elements:**
- [What needs adaptation]
```

---

### 10.2 Task Folder Structure

**Location:** `.claude/tasks/TASK-<number>/`

```
TASK-XXX-semantic-name/
├── STATE.json (metadata, commits, files, tests, quality gates)
├── README.md (what needs to be done)
├── research/ (RESEARCH phase)
│   ├── patterns.md
│   ├── dependencies.md
│   └── similar-implementations.md
├── planning/ (PLANNING phase)
│   ├── solution-architecture.md
│   ├── implementation-spec.md
│   ├── test-plan.md
│   ├── acceptance-criteria.md
│   └── official-docs-validation.md
├── implementation/ (IMPLEMENTATION phase)
│   └── [code artifacts if needed]
├── testing/ (TESTING phase)
│   └── test-results.md
├── validation/ (VALIDATION phase)
│   └── quality-gates.md
├── subagent-reports/
│   ├── dev-backend-fastapi-report.md
│   └── dev-frontend-svelte-report.md
└── context/
    └── backend-done.md (handoff to frontend)
```

---

### 10.3 STATE.json Schema

```json
{
  "task_id": "TASK-XXX",
  "story_id": "US-YYY",
  "task_type": "feat|fix|refactor|test|docs",
  "semantic_name": "descriptive-name",
  "branch": "feat/TASK-XXX-semantic-name-US-YYY",
  "timestamps": {
    "created": "ISO8601",
    "started": "ISO8601",
    "last_accessed": "ISO8601",
    "completed": "ISO8601"
  },
  "phase": {
    "current": "RESEARCH|PLANNING|IMPLEMENTATION|TESTING|VALIDATION",
    "history": ["PLANNING", "IMPLEMENTATION", ...]
  },
  "domains": ["backend", "frontend", "infrastructure"],
  "agents_used": ["dev-backend-fastapi", "dev-frontend-svelte"],
  "commits": [
    {
      "sha": "abc123",
      "message": "commit message",
      "timestamp": "ISO8601",
      "files_changed": 5
    }
  ],
  "tests": {
    "files_created": ["path/to/test.py"],
    "files_modified": ["path/to/test.ts"],
    "total_tests": 15,
    "passing": true,
    "coverage_percentage": 94.0,
    "coverage_baseline": 80.0,
    "last_run": "ISO8601"
  },
  "quality_gates": {
    "lint": { "status": "passed|failed|not_run", "last_run": "ISO8601" },
    "type_check": { "status": "passed|failed|not_run", "errors": 0, "last_run": "ISO8601" },
    "security_scan": { "status": "passed|failed|not_run", "vulnerabilities": 0, "last_run": "ISO8601" },
    "acceptance_criteria": { "total": 4, "met": 4, "status": "passed|pending" }
  },
  "files_modified": ["path/to/file1.py", "path/to/file2.ts"],
  "dependencies": {
    "blocked_by": ["TASK-001"],
    "blocks": ["TASK-003"],
    "status": "blocked|unblocked"
  },
  "status": "not_started|in_progress|completed|archived",
  "notes": ""
}
```

**Updates via docs-stories:**
- `task_update_state.py` - Update status
- `task_update_phase.py` - Update phase
- `task_add_commit.py` - Track commits
- `task_add_file_modified.py` - Track files

---

### 10.4 Semantic Task IDs

**Pattern:** `TASK-{number}-{semantic-slug}`

**Examples:**
- `TASK-001-clerk-mounting`
- `TASK-002-login-tests`
- `TASK-003-role-badge-indicator`

**Benefits:**
- Self-documenting git history
- Clear branch names
- Easier to remember and reference
- Instant understanding of task purpose

---

### 10.5 Context Indexing (Planned)

**Script:** `context_index.py` (US-001D)

**Purpose:** Build searchable index of all SDLC artifacts

**Index Schema:**
```json
{
  "metadata": { "generated": "ISO8601", "total_stories": 5, "total_tasks": 12 },
  "stories": {
    "US-001": {
      "id": "US-001",
      "title": "Login Flow Validation",
      "file": ".sdlc-workflow/stories/auth/US-001-...",
      "tasks": ["TASK-001-clerk-mounting"],
      "commits": ["abc123"],
      "implementation_files": ["apps/frontend/tests/..."]
    }
  },
  "tasks": {
    "TASK-001-clerk-mounting": {
      "story": "US-001",
      "folder": ".claude/tasks/TASK-001/",
      "decisions": "...",
      "files_modified": ["..."]
    }
  },
  "commits": { "abc123": { "story": "US-001", "task": "TASK-001", ... } },
  "files": { "path/to/file.py": { "design_pattern": "Singleton", "trade_offs": "..." } }
}
```

**Performance:**
- Indexing: <10 seconds for 20 stories, 50 tasks
- Retrieval: <3 minutes for full context of any story

---

## 11. Multi-Product Strategy

### 11.1 Two Products

1. **bestays.app** - Vacation rental platform
2. **Real Estate product** - Property sales/rental platform

**Strategy:** Build for `bestays` first (default), then port to `realestate` via porting tasks.

---

### 11.2 Story Metadata

```markdown
---
default_product: bestays
portable: true
ported_to: []
---
```

**Fields:**
- `default_product` - Which product this story is primarily built for
- `portable` - Whether this feature can be ported to other products
- `ported_to` - Array of products this story has been ported to

---

### 11.3 Porting Workflow (4 Steps)

**Step 1: Implement for bestays**
```bash
python story_create.py auth login flow
python task_create.py US-XXX 1 login-bestays
# Subagent implements → Commit: feat: implement login (US-XXX TASK-001-login-bestays)
```

**Step 2: Create porting task**
```bash
python task_create.py US-XXX 50 port-login-realestate \
    --type PORTING \
    --source-product bestays \
    --target-product realestate \
    --source-task TASK-001
```

**Step 3: Execute porting**
```
Subagent reads porting-checklist.md and source implementation
Adapts files for realestate (redirects, branding, roles)
Commit: feat: port login to real estate (US-XXX TASK-050-port-login-realestate)
```

**Step 4: Update story metadata**
```bash
python story_update_ported.py US-XXX realestate
# Story: ported_to: [realestate]
```

---

### 11.4 Portable vs Product-Specific

**Portable (shared across products):**
- Auth logic
- Validation
- UI components
- Business logic (product-agnostic)

**Product-Specific (requires adaptation):**
- Redirect URLs (bestays: /home, realestate: /dashboard)
- Branding and styling
- Role mappings
- Domain logic
- Database fields (product column)

---

### 11.5 Porting Task Structure

```
TASK-050-port-login-realestate/
├── STATE.json
│   {
│     "type": "PORTING",
│     "source_product": "bestays",
│     "target_product": "realestate",
│     "source_task": "TASK-001-login-bestays"
│   }
├── planning/
│   ├── porting-checklist.md
│   └── product-specific-requirements.md
└── subagent-reports/
```

---

## 12. The Complete Picture: End-to-End Walkthrough

### 12.1 Feature Request → Deployed Code

Let's walk through implementing a complete feature: "Admin Login Flow"

---

#### Phase 0: Story Creation

**User:** "Create story for admin login"

**Coordinator:**
```bash
python .claude/skills/docs-stories/scripts/story_create.py auth login admin
```

**Output:**
```
✓ Created: US-001-auth-login-admin
  File: .sdlc-workflow/stories/auth/US-001-auth-login-admin.md
  Status: READY
  Default Product: bestays
  Portable: true
```

---

#### Phase 1: Task Creation & Planning

**User:** `/task-new US-001 feat`

**Coordinator:**
```bash
# Validate story exists
python story_find.py US-001

# Create task
python task_create.py US-001 1 clerk-mounting

# Output:
✓ Task created: TASK-001
✓ Branch created: feat/TASK-001-clerk-mounting-US-001
✓ Current task: TASK-001
```

**session_start hook displays:**
```
📋 Current Task: TASK-001
   Story: US-001
   Phase: PLANNING
   Status: in_progress
   Branch: feat/TASK-001-clerk-mounting-US-001

💡 Suggested: /task-research or /task-plan
```

---

#### Phase 2: Research

**User:** `/task-research`

**Coordinator:**
1. Updates phase to RESEARCH
2. Spawns Explore agent with prompt:
   ```
   Analyze apps/server/ for auth patterns
   Search git history for similar implementations
   Identify dependencies (Clerk, etc.)
   Document findings in .claude/tasks/TASK-001/research/
   ```

**Explore agent:**
- Searches codebase
- Finds existing Clerk setup
- Identifies patterns
- Returns: research/patterns.md, research/dependencies.md

**SubagentStop hook validates:**
- ✅ Research files saved
- ✅ Updates STATE.json

---

#### Phase 3: Planning

**User:** `/task-plan`

**Coordinator:**
1. Updates phase to PLANNING
2. Loads context:
   - Story acceptance criteria
   - Research findings
3. Spawns Plan agent with prompt:
   ```
   Create implementation plan for TASK-001 (US-001):

   Story: Admin login functionality with Clerk

   Acceptance Criteria:
   AC-1: Valid credentials authenticate user
   AC-2: Invalid credentials rejected

   Research Findings:
   - Existing Clerk setup found
   - Pattern: Singleton for Clerk client
   - Dependencies: clerk-sdk-python

   Design:
   - Architecture approach
   - Files to modify/create
   - Which subagents (dev-backend, dev-frontend)
   - Testing strategy
   - Apply 7 quality gates

   Save to: .claude/tasks/TASK-001/planning/
   ```

**Plan agent:**
- Loads planning-quality-gates skill
- Designs architecture
- Creates file-by-file spec
- Applies all 7 quality gates
- Uses Svelte MCP for official docs validation
- Returns: planning artifacts

**Coordinator presents to user:**
```
Here's the proposed plan. Review:
• Architecture: Clean Architecture with Clerk integration
• Agents: dev-backend → dev-frontend
• Quality Gates: All 7 passed
• Estimate: ~8 hours

Questions or changes needed?
```

**User:** "Approved"

**Coordinator:**
- Updates phase to PLANNING complete
- Commits planning artifacts
- Suggests: `/task-implement backend`

---

#### Phase 4: Implementation (Backend)

**User:** `/task-implement backend`

**Coordinator:**
1. Updates phase to IMPLEMENTATION
2. Loads enriched context:
   - Story
   - Research
   - Plan
3. Spawns dev-backend-fastapi agent with prompt:
   ```
   Implement backend for TASK-001:

   Plan: [implementation spec]

   Files to create/modify:
   - apps/server/src/auth/routes.py
   - apps/server/core/clerk.py
   - tests/backend/test_auth.py

   Requirements:
   - Follow dev-philosophy skill
   - Follow dev-code-quality skill
   - MUST use backend-fastapi skill (ALWAYS)
   - MUST use backend-architecture skill (ALWAYS)
   - MUST use backend-python-testing skill (ALWAYS)
   - Add file headers to all files
   - Commit when done

   Save report to: .claude/tasks/TASK-001/subagent-reports/backend-report.md
   ```

**dev-backend-fastapi agent:**
1. Loads mandatory skills
2. Creates files:
   ```python
   # apps/server/src/auth/routes.py
   """
   Auth Routes

   Design Pattern: Router (FastAPI)
   Architecture Layer: API
   Dependencies:
     External: clerk-sdk-python
     Internal: server.core.clerk
   Trade-offs:
     Pro: Clerk handles security
     Con: Vendor lock-in
     When to revisit: If Clerk pricing >$500/month
   """
   ```

3. Creates tests:
   ```python
   # tests/backend/test_auth.py
   def test_valid_credentials_authenticate():
       # AC-1: Valid credentials authenticate user
       ...
   ```

4. Commits:
   ```bash
   git commit -m "$(cat <<'EOF'
   feat(auth): implement login API endpoint (US-001 TASK-001-clerk-mounting)

   Subagent: dev-backend-fastapi
   Product: bestays
   Files: apps/server/src/auth/routes.py, apps/server/core/clerk.py

   Story: US-001
   Task: TASK-001-clerk-mounting

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

5. Returns report

**SubagentStop hook validates:**
- ✅ Commits made (1 commit)
- ✅ Backend files modified
- ✅ Test files created
- ✅ Updates STATE.json agents_used: [dev-backend-fastapi]

**Coordinator presents results:**
```
Backend implementation complete:
• 1 commit made
• API endpoints: POST /api/auth/login
• Tests: 5 passing, 94% coverage
• All quality requirements met

Review and approve, or request changes?
```

**User:** "Approved"

**Coordinator:**
- Saves summary to `context/backend-done.md`:
  ```markdown
  # Backend Implementation Complete

  ## API Endpoints Created
  - POST /api/auth/login
    Request: { email: string, password: string }
    Response: { token: string, user: User }
    Uses Clerk for authentication

  ## Integration Points
  Frontend should:
  - Call POST /api/auth/login with credentials
  - Store token in localStorage
  - Redirect to /home on success
  ```

---

#### Phase 5: Implementation (Frontend)

**User:** `/task-implement frontend`

**Coordinator:**
1. Loads enriched context:
   - Story
   - Research
   - Plan
   - **context/backend-done.md** (backend results!)
2. Spawns dev-frontend-svelte agent with prompt:
   ```
   Implement frontend for TASK-001:

   Backend context:
   - Endpoint: POST /api/auth/login
   - Request: { email, password }
   - Response: { token, user }
   - Redirect to /home on success

   Files to create:
   - apps/frontend/src/routes/admin/login/+page.svelte
   - apps/frontend/src/lib/api/auth.ts

   Requirements:
   - MUST use frontend-svelte skill (ALWAYS)
   - Use Svelte 5 runes ($state, $derived)
   - Use Svelte MCP for official docs
   - Apply network resilience patterns (retry, error handling)
   - Create E2E test
   ```

**dev-frontend-svelte agent:**
1. Loads frontend-svelte skill
2. Uses Svelte MCP:
   ```javascript
   // List available sections
   mcp__svelte__list-sections()

   // Fetch relevant docs
   mcp__svelte__get-documentation({
     section: ["$state", "Form actions", "Load functions"]
   })
   ```

3. Creates component:
   ```svelte
   <!--
   Login Page - Admin authentication

   ARCHITECTURE:
     Layer: Page
     Pattern: Form with client-side validation

   PATTERNS USED:
     - Svelte 5 runes ($state for reactive state)
     - Progressive enhancement (works without JS)

   DEPENDENCIES:
     External: None
     Internal: $lib/api/auth.ts

   INTEGRATION:
     - API: POST /api/auth/login
     - Redirect: /home on success
   -->

   <script lang="ts">
     let email = $state('');
     let password = $state('');
     let error = $state('');

     async function handleLogin() {
       const response = await fetch('/api/auth/login', {
         method: 'POST',
         body: JSON.stringify({ email, password })
       });

       if (response.ok) {
         window.location.href = '/home';
       } else {
         error = 'Invalid credentials';
       }
     }
   </script>

   <form on:submit|preventDefault={handleLogin}>
     <input bind:value={email} type="email" required>
     <input bind:value={password} type="password" required>
     {#if error}
       <p class="error">{error}</p>
     {/if}
     <button type="submit">Login</button>
   </form>
   ```

4. Creates E2E test:
   ```typescript
   // tests/e2e/login.spec.ts
   test('valid credentials authenticate user', async ({ page }) => {
     // AC-1: Valid credentials authenticate user
     ...
   });
   ```

5. Commits and returns report

**SubagentStop hook validates:**
- ✅ Commits made
- ✅ Frontend files modified
- ✅ Test files created
- ✅ Updates agents_used: [dev-backend-fastapi, dev-frontend-svelte]

**Coordinator:** "Frontend implementation complete. Ready for testing."

---

#### Phase 6: Testing

**User:** "Run tests"

**Coordinator:**
```bash
# Backend tests
cd apps/server && pytest

# Frontend tests
cd apps/frontend && npm run test:e2e
```

**Results:**
```
Backend: 5 tests passing, 94% coverage ✅
Frontend: 3 E2E tests passing ✅
```

**Coordinator:**
- Updates STATE.json tests section
- Updates phase to TESTING complete

---

#### Phase 7: Validation

**Coordinator:**
```bash
# Lint
ruff check apps/server/ → PASS ✅
eslint apps/frontend/ → PASS ✅

# Type check
mypy apps/server/ → PASS ✅
tsc apps/frontend/ → PASS ✅

# Security scan
bandit apps/server/ → PASS (0 issues) ✅

# Acceptance criteria
AC-1: Valid credentials authenticate → PASS ✅
AC-2: Invalid credentials rejected → PASS ✅
```

**Coordinator:**
- Updates STATE.json quality_gates
- Updates phase to VALIDATION complete
- Updates status to COMPLETED

**Output:**
```
✅ All quality gates passed
✅ All acceptance criteria met
✅ Task complete!

Summary:
- 2 commits made
- 6 files modified
- 8 tests (all passing)
- 94% coverage
- All quality gates passed

Ready to: git push, create PR, merge
```

---

### 12.2 How Memory Print Enables Instant Context

**3 months later, new session, need to understand auth:**

**Step 1: Git log**
```bash
git log --grep="auth" --oneline
# 509a519 feat(auth): implement login API endpoint (US-001 TASK-001-clerk-mounting)
```

**Step 2: Read task folder**
```
.claude/tasks/TASK-001-clerk-mounting/
├── README.md → "What: Mount Clerk SDK for authentication"
├── planning/decisions.md → "Why: Chose Clerk over Auth0 for speed"
└── subagent-reports/backend-report.md → "How: Singleton pattern, dependency injection"
```

**Step 3: Read story**
```
.sdlc-workflow/stories/auth/US-001-auth-login-admin.md
→ Business value: Secure authentication for admins
→ Acceptance criteria: Valid auth, invalid reject
```

**Step 4: Read file header**
```python
# apps/server/core/clerk.py
"""
Design Pattern: Singleton
Trade-offs:
  - Vendor lock-in vs faster development
  - When to revisit: If Clerk pricing >$500/month
"""
```

**Time: 2-3 minutes**
**Understanding: Complete** (what, why, how, when to change, risks)

---

## Summary: How Everything Connects

```
┌─────────────────────────────────────────────────────────────┐
│                    PHILOSOPHY LAYER                          │
│  Trust but Verify • Memory Print • Coordinator/Implementer  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      WORKFLOW LAYER                          │
│  RESEARCH → PLANNING → IMPLEMENTATION → TESTING → VALIDATION│
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
┌─────────▼────┐  ┌────────▼────────┐  ┌──▼──────────┐
│   ACTORS     │  │     SKILLS      │  │    HOOKS    │
│              │  │                 │  │             │
│ Coordinator  │  │ docs-stories    │  │ session_    │
│ dev-backend  │  │ planning-gates  │  │ start       │
│ dev-frontend │  │ dev-philosophy  │  │ sdlc_       │
│ devops-infra │  │ dev-code-quality│  │ guardian    │
│              │  │ frontend-svelte │  │ subagent_   │
│              │  │ backend-fastapi │  │ stop        │
└──────────────┘  └─────────────────┘  └─────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      TOOLS LAYER                             │
│  Slash Commands • MCP Integrations • Scripts                │
│  /task-new • /task-plan • /task-implement                   │
│  Memory MCP • Svelte MCP • Context7 MCP                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   DOCUMENTATION LAYER                        │
│  User Stories • Task Folders • STATE.json                   │
│  File Headers • Comments • Git History                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    MEMORY PRINT CHAIN                        │
│  Story → Task → README → File Header → Comments → Git       │
│                                                              │
│  Result: <3 minutes to full context restoration             │
└──────────────────────────────────────────────────────────────┘
```

---

## Appendix: Quick Reference

### Essential Commands

```bash
# Story Management
python story_create.py <domain> <feature> <scope>
python story_find.py [domain] [--status STATUS]

# Task Management
python task_create.py <story-id> <task-number> <semantic-name>
python task_update_state.py <task-id> <status>
python task_update_phase.py <task-id> <phase>

# Development
make dev           # Start development environment
make logs          # View all logs
make check         # Check system health
make test-server   # Run backend tests
```

### Slash Commands

```
/story-new <domain> <feature> <scope>
/task-new <story-id> <type>
/task-research
/task-plan
/task-implement <backend|frontend|fullstack>
```

### File Locations

```
.claude/
├── tasks/                    # Task folders
│   └── TASK-XXX/
├── skills/                   # Skills
│   ├── docs-stories/
│   ├── planning-quality-gates/
│   ├── dev-philosophy/
│   └── ...
├── hooks/                    # Hooks
│   ├── session_start.py
│   └── sdlc_guardian.py
└── reports/                  # Reports

.sdlc-workflow/
├── stories/                  # User stories
│   └── <domain>/US-XXX.md
├── guides/                   # Guides
│   ├── memory-print.md
│   └── ...
└── .index/                   # Context index (planned)
    └── sdlc-index.json
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-09
**Maintained By:** Bestays SDLC Team

---

This document is the single source of truth for how Bestays achieves instant memory print through a comprehensive, LLM-focused SDLC workflow. Every process, tool, and pattern is designed to maximize context restoration speed while minimizing maintenance cost.
