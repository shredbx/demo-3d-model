# Bestays SDLC: Comprehensive Process Documentation

**The LLM-First Software Development Life Cycle**

**Version:** 1.0
**Date:** 2025-11-10
**Purpose:** Complete documentation of Bestays' Claude Code-powered SDLC system

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Philosophy](#system-philosophy)
3. [Architecture Overview](#architecture-overview)
4. [Core Components](#core-components)
5. [SDLC Phase Flow](#sdlc-phase-flow)
6. [Quality Assurance System](#quality-assurance-system)
7. [Multi-Product Workflow](#multi-product-workflow)
8. [Context Restoration](#context-restoration)
9. [Tools and Automation](#tools-and-automation)
10. [Best Practices](#best-practices)

---

## 1. Executive Summary

### What Is This System?

Bestays uses a **revolutionary LLM-first SDLC** designed specifically for Claude Code as the primary development agent. Unlike traditional SDLCs adapted for AI assistance, this system is built **FROM THE GROUND UP** for AI-driven development.

### Key Characteristics

- **Single Developer + LLM Architecture**: One human developer + Claude Code coordinator + specialized subagents
- **Zero Context Loss**: Every decision preserved forever via memory print chain
- **<3 Minute Context Restoration**: From cold start to full understanding
- **Self-Enforcing Boundaries**: Hooks prevent coordinator from breaking workflow
- **90% Automation**: Only validation requires human input
- **Professional-Grade Output**: Production-ready code with comprehensive documentation

### System Performance

| Metric | Value |
|--------|-------|
| Context Restoration Time | < 3 minutes (vs 30-60 minutes manual) |
| Automation Level | ~90% (validation only requires human) |
| Code Quality | File headers, type safety, tests, documentation |
| Knowledge Retention | 100% (all decisions preserved) |
| Multi-Session Continuity | Perfect (via task folders + git + Memory MCP) |

---

## 2. System Philosophy

### Core Principle: Built FOR LLMs

**Traditional SDLC:**
- Designed for humans → Adapted for AI assistance
- Documentation is optional afterthought
- Context lives in human memory
- Processes are flexible guidelines

**Bestays LLM-First SDLC:**
- Designed for Claude Code → Human provides validation
- Documentation is mandatory (AI needs it for context)
- Context lives in filesystem (task folders, file headers, git)
- Processes are enforced via hooks and scripts

### Three Pillars

#### Pillar 1: Memory Print Chain

Every artifact leaves a "memory print" for instant context restoration:

```
User Story → Task → File Header → Comments → Git History
   ↓          ↓         ↓            ↓           ↓
High-level  Detailed  Design      Rationale   Timeline
 criteria   decisions patterns
```

**Time to Full Context:** < 3 minutes

#### Pillar 2: Trust But Verify

- Trust: AI can write professional code
- Verify: Automated tests, type checking, external validation
- Human role: Approve major decisions, validate acceptance criteria

#### Pillar 3: Self-Healing System

- Hooks prevent workflow violations (coordinator can't edit implementation)
- Quality gates prevent incomplete planning
- Documentation requirements ensure knowledge transfer
- Scripts ensure consistency (no manual file creation)

---

## 3. Architecture Overview

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TIER 1: COORDINATOR                       │
│                                                              │
│  Claude Code Main Instance                                  │
│  - Research (via Explore agents)                            │
│  - Planning (via sequential-thinking + quality gates)       │
│  - Coordination (spawn subagents)                           │
│  - Documentation (task folders, reports)                    │
│  - Git Operations (commits, branches, tracking)             │
│  - Progress Tracking (TodoWrite, STATE.json updates)        │
│                                                              │
│  CANNOT: Edit apps/*, tests/* (enforced by hooks)           │
│  CAN: Read all, write docs/workflow/configs                 │
└─────────────────────────────────────────────────────────────┘
                             ↓
                    Spawns subagents via
                      Task tool
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                  TIER 2: IMPLEMENTATION SUBAGENTS            │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ dev-backend-     │  │ dev-frontend-    │               │
│  │ fastapi          │  │ svelte           │               │
│  │                  │  │                  │               │
│  │ apps/server/**   │  │ apps/frontend/** │               │
│  │ Backend API      │  │ UI Components    │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ playwright-e2e-  │  │ qa-code-auditor  │               │
│  │ tester           │  │                  │               │
│  │                  │  │                  │               │
│  │ tests/e2e/**     │  │ Code review      │               │
│  │ E2E Testing      │  │ Quality audit    │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                              │
│  ┌──────────────────┐                                      │
│  │ devops-infra     │                                      │
│  │                  │                                      │
│  │ Docker/Deploy    │                                      │
│  │ Infrastructure   │                                      │
│  └──────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
                             ↓
                   Produces artifacts in
                     task folders
                             ↓
┌─────────────────────────────────────────────────────────────┐
│               TIER 3: KNOWLEDGE LAYER                        │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │ Task Folders   │  │ File Headers   │  │ Git History  │ │
│  │                │  │                │  │              │ │
│  │ .claude/tasks/ │  │ Design patterns│  │ Commit msgs  │ │
│  │ TASK-XXX/      │  │ Trade-offs     │  │ References   │ │
│  │                │  │ Integration    │  │ Timeline     │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │ User Stories   │  │ Memory MCP     │  │ SDLC Index   │ │
│  │                │  │                │  │              │ │
│  │ .sdlc-workflow/│  │ Patterns       │  │ context_index│ │
│  │ stories/       │  │ Quality gates  │  │ .json        │ │
│  │                │  │ Decisions      │  │              │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Core Components

### 4.1 Role System: Coordinator vs Subagents

#### Coordinator (Main Claude Code Instance)

**Responsibilities:**
- Research existing patterns (via Explore agents)
- Plan implementations (via sequential-thinking + quality gates)
- Spawn specialized subagents for implementation
- Document decisions and rationale
- Manage git workflow (branches, commits, tracking)
- Track progress (TodoWrite, STATE.json updates)
- Communicate with human developer

**Capabilities:**
- ✅ Read ANY file (needs context)
- ✅ Write workflow/doc files (`.sdlc-workflow/`, `.claude/`, `CLAUDE.md`, `*.md`)
- ✅ Execute git commands (status, log, add, commit, push)
- ✅ Run scripts (docs-stories scripts, make commands)
- ✅ Spawn subagents (Task tool)

**Restrictions (Enforced by Hook):**
- ❌ Edit `apps/server/**/*.py` → Must use dev-backend-fastapi
- ❌ Edit `apps/frontend/src/**` → Must use dev-frontend-svelte
- ❌ Edit `tests/e2e/**` → Must use playwright-e2e-tester
- ❌ Edit `docker/**`, `Makefile` → Must use devops-infra

**Enforcement:** `.claude/hooks/sdlc_guardian.py` (runs before Edit/Write tools)

#### Subagents (Specialized Agents)

**dev-backend-fastapi:**
- Scope: `apps/server/**/*.py`
- Skills: backend-fastapi, backend-async-python, backend-uv-manager
- Output: Backend code + subagent-reports/backend-report.md
- **MANDATORY:** External HTTP validation (curl, httpie, Postman)

**dev-frontend-svelte:**
- Scope: `apps/frontend/src/**`
- Skills: frontend-svelte, frontend-tailwind, frontend-typescript
- Output: Frontend code + subagent-reports/frontend-report.md
- **MANDATORY:** Svelte 5 compliance, SSR compatibility

**playwright-e2e-tester:**
- Scope: `tests/e2e/**/*.spec.ts`
- Skills: playwright-e2e-tester
- Output: E2E tests + subagent-reports/e2e-report.md
- **MANDATORY:** Browser compatibility (Chrome, Firefox, Safari)

**qa-code-auditor:**
- Scope: Code review across codebase
- Skills: qa-code-auditor, dev-code-quality
- Output: subagent-reports/code-review-report.md
- **Purpose:** Quality assessment, improvement recommendations

**devops-infra:**
- Scope: Docker, Makefile, deployment configs
- Skills: devops-bestays-infra, devops-database, devops-local-dev
- Output: Infrastructure changes + subagent-reports/devops-report.md

### 4.2 MCP Servers (External Knowledge)

#### memory (Knowledge Graph)

**Purpose:** Persistent cross-session patterns and decisions

**Tools:**
- `mcp__memory__open_nodes` - Load entities at session start
- `mcp__memory__search_nodes` - Query by topic
- `mcp__memory__create_entities` - Store new patterns
- `mcp__memory__add_observations` - Update existing entities

**Core Entities (Loaded Every Session):**
1. SDLC Workflow Pattern
2. Coordinator Role - CRITICAL
3. Planning Quality Gates - 7 Gates
4. Official Documentation Validation
5. Network Resilience Pattern
6. Task Folder System
7. Svelte 5 Mounting Pattern - onMount vs $effect
8. Backend Implementation Validation Gate

**Usage:**
```typescript
// Session start (ALWAYS run)
mcp__memory__open_nodes({
  names: [
    "SDLC Workflow Pattern",
    "Coordinator Role - CRITICAL",
    "Planning Quality Gates - 7 Gates",
    // ... all 8 core entities
  ]
})
```

#### svelte (Official Svelte/SvelteKit Documentation)

**Purpose:** Validate against official Svelte 5 and SvelteKit documentation

**Tools:**
- `mcp__svelte__list-sections` - Find relevant doc sections
- `mcp__svelte__get-documentation` - Fetch full documentation
- `mcp__svelte__playground-link` - Generate Svelte REPL links
- `mcp__svelte__svelte-autofixer` - Validate Svelte code for issues

**Mandatory Usage:**
- Planning phase for ALL frontend tasks (Quality Gate 7)
- Before implementation (validate patterns)
- After implementation (auto-fix issues)

**Example:**
```typescript
// Planning phase
mcp__svelte__list-sections() // Find relevant sections
mcp__svelte__get-documentation({
  section: ["$state", "load functions", "onMount"]
})

// After implementation
mcp__svelte__svelte-autofixer({
  code: componentCode,
  desired_svelte_version: 5
})
```

#### context7 (Third-Party Library Documentation)

**Purpose:** Fetch up-to-date documentation for any library

**Tools:**
- `mcp__context7__resolve-library-id` - Find library by name
- `mcp__context7__get-library-docs` - Fetch documentation

**Usage:**
```typescript
// Step 1: Resolve library name to ID
mcp__context7__resolve-library-id({
  libraryName: "Clerk"
})
// Returns: /clerk/clerk-js

// Step 2: Fetch docs
mcp__context7__get-library-docs({
  context7CompatibleLibraryID: "/clerk/clerk-js",
  topic: "authentication",
  tokens: 5000
})
```

#### sequential-thinking (Deep Analysis)

**Purpose:** Multi-step reasoning, planning, architecture decisions

**Tool:** `mcp__sequential-thinking__sequentialthinking`

**Mandatory Usage:**
- Planning SDLC implementations
- Designing architecture
- Making architectural decisions
- Analyzing complex problems
- Validating approaches

**Pattern:**
```typescript
// Thought 1: Understand problem
sequentialthinking({
  thought: "Analyzing requirements...",
  thoughtNumber: 1,
  totalThoughts: 10,
  nextThoughtNeeded: true
})

// Thought 2-9: Design solution
// ...

// Thought 10: Verify solution
sequentialthinking({
  thought: "Solution verified against requirements",
  thoughtNumber: 10,
  totalThoughts: 10,
  nextThoughtNeeded: false
})
```

#### playwright (Browser Automation)

**Purpose:** E2E test execution and debugging

**Tools:** 50+ tools for browser control (navigate, click, type, screenshot, etc.)

**Usage:** Testing phase, manual validation, debugging

---

### 4.3 Skills (Domain-Specific Knowledge)

Skills are markdown files loaded into agent context. They provide specialized knowledge and workflows.

#### Mandatory Skills (ALWAYS Loaded)

**docs-stories** (`.claude/skills/docs-stories/`)
- **Purpose:** ALL CRUD operations for stories/tasks
- **Scripts:** story_create.py, task_create.py, task_update_phase.py, context_index.py
- **Usage:** NEVER manually create story/task files, ALWAYS use scripts
- **Why:** Consistency, validation, automation, tracking

**dev-philosophy** (`.claude/skills/dev-philosophy/`)
- **Purpose:** Core development standards
- **Loaded by:** ALL agents (coordinator + subagents)
- **Content:** Trust but verify, memory print, LLM-first design

**dev-code-quality** (`.claude/skills/dev-code-quality/`)
- **Purpose:** Code quality standards
- **Loaded by:** ALL agents
- **Content:** File headers, design patterns, trade-offs documentation

**planning-quality-gates** (`.claude/skills/planning-quality-gates/`)
- **Purpose:** 7 mandatory quality gates for planning
- **Loaded by:** Coordinator before planning, Plan agents
- **Gates:**
  1. Network Operations
  2. Frontend SSR/UX
  3. Testing Requirements
  4. Deployment Safety
  5. Acceptance Criteria
  6. Dependencies
  7. Official Documentation Validation

#### Domain-Specific Skills (Loaded on Demand)

**frontend-svelte** - SvelteKit 5 patterns, Svelte runes, SSR handling
**backend-fastapi** - FastAPI patterns, async, Clean Architecture
**devops-bestays-infra** - Docker, migrations, multi-product deployment

---

### 4.4 Slash Commands (User-Facing Workflows)

Custom commands that expand to full prompts:

**/story-new** → Create new user story using docs-stories
**/task-new** → Create new task for a story
**/task-research** → Launch Explore agent for research phase
**/task-plan** → Execute planning phase with quality gates
**/task-implement** → Launch appropriate subagent for implementation

**Example:**
```
User types: /task-plan
→ SlashCommand tool expands to full planning prompt
→ Coordinator loads planning-quality-gates skill
→ Coordinator runs sequential-thinking
→ Coordinator validates 7 quality gates
→ Coordinator creates planning artifacts in task folder
```

---

### 4.5 Task Folder System (Artifact Preservation)

**Location:** `.claude/tasks/TASK-XXX-semantic-name/`

**Purpose:** Preserve ALL context, decisions, artifacts for every task

**Structure:**
```
.claude/tasks/TASK-019-route-guards/
├── STATE.json                     # Metadata, tracking, links
├── README.md                      # What this task does
├── research/                      # RESEARCH phase
│   ├── findings.md                # What we discovered
│   └── existing-patterns.md       # Similar implementations
├── planning/                      # PLANNING phase
│   ├── planning-summary.md        # Quick reference
│   ├── solution-architecture.md   # High-level design
│   ├── implementation-plan.md     # Detailed specs
│   ├── planning-quality-gates.md  # 7 gates validation
│   ├── acceptance-criteria.md     # Done definition
│   ├── official-docs-validation.md # Framework docs validation
│   └── test-plan.md               # Test strategy
├── subagent-reports/              # Subagent outputs
│   ├── frontend-implementation-report.md
│   └── e2e-test-report.md
├── testing/                       # TESTING phase (if applicable)
│   ├── unit-test-results.md
│   └── e2e-test-results.md
└── COMPLETION_SUMMARY.md          # Final summary
```

**STATE.json Schema:**
```json
{
  "task_id": "TASK-019",
  "semantic_name": "route-guards",
  "story_id": "US-028",
  "task_type": "feat",
  "branch": "feat/TASK-019-route-guards-US-028",
  "phase": {
    "current": "IMPLEMENTATION",
    "history": [
      {
        "phase": "RESEARCH",
        "started": "2025-11-10T11:10:22Z",
        "completed": "2025-11-10T11:17:15Z",
        "duration_minutes": 6.88
      },
      {
        "phase": "PLANNING",
        "started": "2025-11-10T11:25:58Z",
        "completed": "2025-11-10T11:42:04Z",
        "duration_minutes": 16.09
      }
    ]
  },
  "status": "in_progress",
  "commits": [
    {
      "sha": "71bf8f2a979d...",
      "message": "feat: implement protected route guards (US-028 TASK-019)",
      "timestamp": "2025-11-10T12:17:57Z",
      "files_changed": 3
    }
  ],
  "files_modified": [
    "apps/frontend/src/routes/dashboard/+layout.ts",
    "apps/frontend/src/lib/utils/redirect.ts"
  ]
}
```

**Semantic Task IDs:**
- Pattern: `TASK-{number}-{semantic-slug}`
- Example: `TASK-019-route-guards` (not just `TASK-019`)
- Why: Self-documenting git history, clear branch names

---

### 4.6 Git Workflow

#### Branch Naming

**Pattern:** `{type}/TASK-{number}-{semantic-name}-US-{story}`

**Examples:**
- `feat/TASK-019-route-guards-US-028`
- `fix/TASK-015-search-filters-US-027`
- `test/TASK-002-login-e2e-US-028`

#### Commit Message Format

```
{type}: {description} (US-XXX TASK-YYY-semantic-name)

Subagent: {which-subagent}
Product: {bestays | realestate}
Files: {list-of-files}

{detailed description}

Story: US-XXX
Task: TASK-YYY-semantic-name

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Example:**
```
feat: implement protected route guards (US-028 TASK-019-route-guards)

Subagent: dev-frontend-svelte
Product: bestays
Files: apps/frontend/src/routes/dashboard/+layout.ts,
       apps/frontend/src/lib/utils/redirect.ts

Implemented SvelteKit universal load function to guard dashboard routes.
Redirects unauthenticated users to login with destination preservation.

Story: US-028
Task: TASK-019-route-guards

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

#### Current Task Tracking

**Method 1: Git Branch**
```bash
git branch --show-current
# Returns: feat/TASK-019-route-guards-US-028
```

**Method 2: STATE.json**
```bash
cat .claude/tasks/TASK-019/STATE.json | jq '.status, .phase.current'
# Returns: "in_progress", "IMPLEMENTATION"
```

---

### 4.7 Hooks System (Self-Enforcement)

**Hook:** `.claude/hooks/sdlc_guardian.py`

**Trigger:** Before Edit/Write tool execution

**Purpose:** Prevent coordinator from editing implementation files

**Logic:**
```python
BLOCKED_PATTERNS = [
    "apps/server/**/*.py",
    "apps/frontend/src/**",
    "tests/e2e/**/*.spec.ts",
    "docker/**",
    "Makefile"
]

SUBAGENT_MAP = {
    "apps/server/**/*.py": "dev-backend-fastapi",
    "apps/frontend/src/**": "dev-frontend-svelte",
    "tests/e2e/**": "playwright-e2e-tester",
    "docker/**": "devops-infra"
}

def validate(file_path):
    if matches_blocked_pattern(file_path):
        subagent = SUBAGENT_MAP[pattern]
        return {
            "blocked": True,
            "message": f"❌ Coordinator cannot edit {file_path}",
            "suggestion": f"Use Task tool with subagent_type={subagent}"
        }
    return {"blocked": False}
```

**User-Facing Message:**
```
❌ BLOCKED: Coordinator cannot edit apps/server/api/auth.py

💡 Use Task tool to launch dev-backend-fastapi subagent

Example:
  Task tool with:
    - subagent_type: dev-backend-fastapi
    - prompt: "Implement login endpoint based on planning/implementation-plan.md"
```

---

## 5. SDLC Phase Flow

The SDLC has 5 sequential phases. Each phase MUST complete before moving to the next.

### Phase 1: RESEARCH

**Trigger:** Task created
**Status:** NOT_STARTED → IN_PROGRESS
**Duration:** 5-15 minutes

**Coordinator Actions:**
1. Launch Explore agent (Task tool, subagent_type=Explore)
2. Explore agent searches existing codebase for similar patterns
3. Explore agent reads related files, git history, documentation
4. Explore agent produces research findings

**Deliverables:**
- `research/findings.md` - Comprehensive codebase research
- `research/existing-patterns.md` - Similar implementations found
- `research/technical-constraints.md` - Limitations discovered

**Completion Criteria:**
- All relevant existing patterns documented
- Integration points identified
- Technical constraints understood
- Dependencies discovered

**Update:**
```bash
python3 .claude/skills/docs-stories/scripts/task_update_phase.py TASK-XXX PLANNING
```

---

### Phase 2: PLANNING

**Trigger:** Research complete
**Status:** IN_PROGRESS (phase: PLANNING)
**Duration:** 20-40 minutes

**Coordinator Actions:**
1. Load `planning-quality-gates` skill
2. Load Memory MCP entities (SDLC patterns, quality gates)
3. Use `sequential-thinking` for architecture design
4. Validate against 7 quality gates
5. Use Svelte MCP for frontend tasks (Quality Gate 7)
6. Use context7 for third-party libraries
7. Create planning artifacts
8. Human approval (if required)

**7 Quality Gates:**

**Gate 1: Network Operations** (Conditional)
- Applies to: Tasks with API calls, SDK loading
- Requirements: Retry logic, exponential backoff, offline detection, timeouts, error handling
- Deliverable: `planning/network-resilience-plan.md`
- Skip if: No network operations (justify in quality-gates.md)

**Gate 2: Frontend SSR/UX** (Conditional)
- Applies to: Frontend tasks
- Requirements: SSR compatibility, hydration, loading states, error states
- Deliverable: `planning/ssr-ux-plan.md`
- Skip if: Backend-only task (justify)

**Gate 3: Testing Requirements** (MANDATORY)
- Applies to: ALL tasks
- Requirements: Unit test plan, E2E test plan, error scenarios, browser compatibility
- Deliverable: `planning/test-plan.md`
- NEVER skip

**Gate 4: Deployment Safety** (Conditional)
- Applies to: Production-bound tasks
- Requirements: Risk assessment, rollback plan, monitoring
- Deliverable: `planning/deployment-safety-plan.md`
- Skip if: Research/spike task (justify)

**Gate 5: Acceptance Criteria** (MANDATORY)
- Applies to: ALL tasks
- Requirements: Technical AC, user story mapping, definition of done
- Deliverable: `planning/acceptance-criteria.md`
- NEVER skip

**Gate 6: Dependencies** (MANDATORY)
- Applies to: ALL tasks
- Requirements: External deps, internal deps, technical debt
- Deliverable: `planning/dependencies-analysis.md`
- NEVER skip

**Gate 7: Official Documentation Validation** (MANDATORY)
- Applies to: ALL tasks
- Requirements: Framework docs, web standards, third-party docs, industry best practices
- Deliverable: `planning/official-docs-validation.md`
- NEVER skip

**Deliverables:**
- `planning/planning-summary.md` - Quick reference (what, why, how)
- `planning/solution-architecture.md` - High-level design
- `planning/implementation-plan.md` - Detailed specs
- `planning/planning-quality-gates.md` - Gate validation results
- `planning/acceptance-criteria.md` - Success criteria
- `planning/official-docs-validation.md` - Framework/library validation
- `planning/test-plan.md` - Test strategy
- (Conditional gates as needed)

**Completion Criteria:**
- All 7 gates validated (or skip justified)
- Architecture designed and documented
- Implementation spec complete
- Acceptance criteria mapped
- Risks assessed

**Update:**
```bash
python3 .claude/skills/docs-stories/scripts/task_update_phase.py TASK-XXX IMPLEMENTATION
```

---

### Phase 3: IMPLEMENTATION

**Trigger:** Planning complete
**Status:** IN_PROGRESS (phase: IMPLEMENTATION)
**Duration:** 1-4 hours

**Coordinator Actions:**
1. Read planning artifacts
2. Determine which subagent(s) needed
3. Launch subagent(s) with Task tool
4. Subagent reads task folder, implements solution
5. Subagent produces implementation report
6. Subagent commits with proper message format
7. Coordinator updates STATE.json (commits, files_modified)

**Subagent Selection:**
- Backend: `dev-backend-fastapi`
- Frontend: `dev-frontend-svelte`
- Tests: `playwright-e2e-tester`
- Infrastructure: `devops-infra`
- Code review: `qa-code-auditor`

**Backend External Validation (MANDATORY):**

For ALL backend API implementations:
- Test with external HTTP tools (curl, httpie, Postman, Thunder Client)
- Test ALL scenarios: success cases, client errors (400, 401, 404), server errors (500)
- Measure performance vs targets
- Document in implementation report with curl commands and actual responses
- Coordinator REJECTS completion if no external validation

**Deliverables:**
- Modified implementation files (apps/server/, apps/frontend/src/)
- `subagent-reports/{subagent}-report.md`
- Git commits with proper format
- Updated STATE.json (commits, files_modified)

**Completion Criteria:**
- All implementation complete per spec
- Code compiles/runs without errors
- File headers added (design patterns, trade-offs)
- Subagent report created
- Committed to git
- Backend: External validation complete

**Update:**
```bash
python3 .claude/skills/docs-stories/scripts/task_update_phase.py TASK-XXX TESTING
```

---

### Phase 4: TESTING

**Trigger:** Implementation complete
**Status:** IN_PROGRESS (phase: TESTING)
**Duration:** 30-60 minutes

**Coordinator Actions:**
1. Backend: Run pytest, verify coverage
2. Frontend: Run E2E tests with Playwright
3. Manual testing validation
4. Error scenario testing
5. Browser compatibility testing (Chrome, Firefox, Safari)
6. Document results
7. If tests fail: Back to IMPLEMENTATION phase
8. If tests pass: Move to VALIDATION phase

**Test Types:**

**Unit Tests (Backend):**
```bash
cd apps/server
pytest tests/ --cov=server --cov-report=term
```
- Target: 85%+ coverage (security-critical: 95%+)
- Document in `testing/unit-test-results.md`

**E2E Tests (Frontend):**
```bash
cd apps/frontend
npm run test:e2e
```
- Test scenarios from planning/test-plan.md
- Browser compatibility: Chrome, Firefox, Safari
- Document in `testing/e2e-test-results.md`

**Manual Testing:**
- Checklist from planning/acceptance-criteria.md
- Document in `testing/manual-testing-checklist.md`

**Deliverables:**
- `testing/unit-test-results.md` (pytest output, coverage)
- `testing/e2e-test-results.md` (Playwright results, screenshots)
- `testing/manual-testing-checklist.md` (verified scenarios)

**Completion Criteria:**
- All automated tests passing
- Coverage targets met
- Manual testing complete
- All acceptance criteria verified

**Update:**
```bash
python3 .claude/skills/docs-stories/scripts/task_update_phase.py TASK-XXX VALIDATION
```

---

### Phase 5: VALIDATION

**Trigger:** Testing complete
**Status:** IN_PROGRESS (phase: VALIDATION)
**Duration:** 15-30 minutes

**Coordinator Actions:**
1. Verify acceptance criteria (from planning/acceptance-criteria.md)
2. User validation (human developer approval)
3. Optional: Code review (qa-code-auditor subagent)
4. Documentation review
5. Create completion summary
6. Update task status to COMPLETED

**Validation Checklist:**
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Code quality standards met
- [ ] Documentation complete
- [ ] File headers present
- [ ] No security issues
- [ ] Performance targets met
- [ ] Human approval received

**Deliverables:**
- `COMPLETION_SUMMARY.md` - What was accomplished, lessons learned
- Optional: `subagent-reports/code-review-report.md`

**Completion Criteria:**
- Human developer approves
- All acceptance criteria verified
- Completion summary created
- Ready for merge/deployment

**Update:**
```bash
python3 .claude/skills/docs-stories/scripts/task_update_state.py TASK-XXX COMPLETED
```

---

## 6. Quality Assurance System

### 6.1 Planning Quality Gates

See Phase 2: PLANNING section above for complete details on 7 gates.

**Enforcement:**
- Coordinator loads `planning-quality-gates` skill before planning
- Each gate produces artifact or skip justification
- No implementation without completed gates

**Rationale:**
- Prevents incomplete planning
- Catches issues early (cheaper to fix)
- Ensures professional-grade output
- Documents trade-offs for future

### 6.2 Backend External Validation

**MANDATORY for all backend implementations.**

**Requirements:**
1. Test with external HTTP tools (curl, httpie, Postman, Thunder Client)
2. Cover ALL scenarios:
   - Success cases (200, 201, 204)
   - Client errors (400, 401, 403, 404, 422)
   - Server errors (500, 503)
   - Edge cases (empty body, large payload, special characters)
   - Performance (response time vs target)

**Report Format (in subagent-reports/backend-report.md):**
```markdown
## External Validation

### Success Cases
\```bash
curl -X POST http://localhost:8011/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
\```

Response (200 OK):
\```json
{"user_id": "user_123", "session_token": "tok_xyz"}
\```

Validation:
✅ Status code correct (200)
✅ Response schema matches spec
✅ Response time: 0.15s (target: <0.5s)

### Error Cases
[Test 400, 401, 404, 500...]

### Performance
Average: 0.15s, P95: 0.25s, Target: <0.5s ✅ PASS
```

**Coordinator Enforcement:**
- REJECTS backend completion if no external validation section
- REJECTS if only unit tests shown
- ACCEPTS if all scenarios tested with actual HTTP requests

**Rationale:**
- Prevents "works on my machine" syndrome
- Validates actual HTTP behavior before frontend integration
- Reduces frontend/backend iteration loops
- Professional industry standard

### 6.3 Code Quality Standards

**File Headers (MANDATORY for all implementation files):**
```python
"""
{Module description}

ARCHITECTURE:
  Layer: {API | Service | Model | Component}
  Pattern: {Singleton | Factory | Repository | etc.}

DEPENDENCIES:
  External:
    - {library name}: {purpose}
  Internal:
    - {module}: {purpose}

DESIGN DECISIONS:
  - {Decision}: {Rationale}

TRADE-OFFS:
  - Pro: {benefit}
  - Con: {cost}
  - When to revisit: {trigger condition}

INTEGRATION POINTS:
  - {where this module connects}

TESTING:
  - {test strategy}

Story: US-XXX
Task: TASK-YYY-{semantic-name}
"""
```

**Inline Comments:**
- Explain WHY, not WHAT
- Document decisions and trade-offs
- Reference alternatives considered

**TypeScript/Python:**
- Type safety (no `any` in TypeScript, type hints in Python)
- ESLint/Pylint passing
- No compiler errors

### 6.4 Test Coverage Requirements

**Backend:**
- Unit tests: 85%+ coverage
- Security-critical code: 95%+ coverage
- All endpoints tested
- Error scenarios covered

**Frontend:**
- E2E tests for user flows
- Browser compatibility: Chrome, Firefox, Safari
- Error scenarios covered
- Loading states tested

**Test Strategy:**
- Write tests during TESTING phase (not during implementation)
- Follow test plan from planning/test-plan.md
- Document results in testing/ folder

---

## 7. Multi-Product Workflow

### 7.1 Products

**Bestays** (Vacation Rentals)
- Clerk: sacred-mayfly-55.clerk.accounts.dev
- URL: https://www.bestays.app
- Priority: Build FIRST

**Real Estate** (Property Sales/Rentals)
- Clerk: pleasant-gnu-25.clerk.accounts.dev
- URL: https://www.bestrealestate.app
- Priority: Port AFTER bestays complete

### 7.2 Strategy

**Build for Bestays first, then port to Real Estate.**

**Rationale:**
- Single source of truth (Bestays)
- Test thoroughly before porting
- Faster development (avoid duplication)
- Clear migration path

### 7.3 Porting Workflow

**Step 1: Implement for Bestays**
```bash
python3 story_create.py auth login flow
# Creates: US-028 (product: bestays, portable: true)

python3 task_create.py US-028 19 route-guards
# Creates: TASK-019 (product: bestays)

# Subagent implements for Bestays
# Commit: feat: implement route guards (US-028 TASK-019-route-guards)
```

**Step 2: Create Porting Task**
```bash
python3 task_create.py US-028 50 port-route-guards-realestate \
    --type PORTING \
    --source-product bestays \
    --target-product realestate \
    --source-task TASK-019
```

**Step 3: Execute Porting**
- Subagent reads porting-checklist.md
- Subagent reads source implementation (TASK-019)
- Subagent adapts for Real Estate:
  - Clerk instance keys (different publishable key)
  - Redirect URLs (if different)
  - Branding (Bestays → Best Real Estate)
  - Role mappings (if different)
- Commit: `feat: port route guards to real estate (US-028 TASK-050)`

**Step 4: Update Story Metadata**
```bash
python3 story_update_ported.py US-028 realestate
# Updates story: ported_to: [realestate]
```

### 7.4 Portable vs Product-Specific

**Portable (same for both products):**
- Auth logic
- Validation
- UI components
- Business logic (product-agnostic)

**Product-Specific (different per product):**
- Clerk instance keys
- Redirect URLs
- Branding (colors, logos, names)
- Role mappings (if different)
- Database fields (if schema differs)

---

## 8. Context Restoration

### 8.1 Memory Print Chain

Every artifact leaves a "memory print" for instant context restoration:

**Level 1: User Story**
- Location: `.sdlc-workflow/stories/{domain}/US-XXX-{title}.md`
- Contains: High-level acceptance criteria, business value, related stories

**Level 2: Task**
- Location: `.claude/tasks/TASK-XXX-{semantic-name}/`
- Contains: Detailed decisions, design patterns, trade-offs, alternatives

**Level 3: File Header**
- Location: Top of every implementation file
- Contains: Design pattern, architecture layer, dependencies, trade-offs, integration points

**Level 4: Comments**
- Location: Within code
- Contains: Rationale for decisions, alternatives considered, when to revisit

**Level 5: Git History**
- Location: Git log
- Contains: Timeline of changes, commit messages with story/task references

### 8.2 Context Restoration Flow

**Scenario:** New session, continue work on login feature

**Time: 0 minutes**
```bash
# Human: "Continue work on login"
```

**Time: 0.5 minutes**
```bash
# Coordinator reads git branch
git branch --show-current
# Returns: feat/TASK-019-route-guards-US-028
```

**Time: 1 minute**
```bash
# Coordinator reads task STATE.json
cat .claude/tasks/TASK-019/STATE.json
# Returns: story: US-028, phase: TESTING, status: in_progress
```

**Time: 1.5 minutes**
```bash
# Coordinator reads planning artifacts
ls .claude/tasks/TASK-019/planning/
# Reads: planning-summary.md, implementation-plan.md, quality-gates.md
```

**Time: 2 minutes**
```bash
# Coordinator reads subagent reports
cat .claude/tasks/TASK-019/subagent-reports/frontend-implementation-report.md
# Understands: What was implemented, what's left, issues encountered
```

**Time: 2.5 minutes**
```bash
# Coordinator reads git history
git log --grep="TASK-019" --oneline
# Sees: All commits for this task

# Coordinator reads modified files
git diff origin/main...HEAD
# Sees: Actual code changes
```

**Time: 3 minutes**
```
# Coordinator: "Ready to continue. Last status: Testing phase, E2E tests partially passing.
# Need to fix test selectors and investigate Real Estate multi-product issue."
```

**Total Time: < 3 minutes** (vs 30-60 minutes manual excavation)

### 8.3 Index System (Future Enhancement)

**Script:** `context_index.py` (to be implemented)

**Purpose:** Build bidirectional index of all SDLC artifacts

**Output:** `.sdlc-workflow/.index/sdlc-index.json`

**Schema:**
```json
{
  "stories": {
    "US-028": {
      "title": "Login & Logout Flow",
      "tasks": ["TASK-019"],
      "commits": ["71bf8f2a"],
      "files": ["apps/frontend/src/routes/dashboard/+layout.ts"]
    }
  },
  "tasks": {
    "TASK-019": {
      "story": "US-028",
      "semantic_name": "route-guards",
      "decisions": "...",
      "files_modified": ["..."]
    }
  },
  "commits": {...},
  "files": {...}
}
```

**Query Examples:**
- "Full context for US-028" → Instant JSON response
- "Files changed in US-028" → Instant list
- "Timeline for US-028" → Chronological commits

**Performance:** < 30 seconds for any query

---

## 9. Tools and Automation

### 9.1 docs-stories Scripts

**All scripts:** `.claude/skills/docs-stories/scripts/`

**Story Management:**
- `story_create.py <domain> <feature> <scope>` - Create new story
- `story_find.py [domain] [--status]` - Find existing stories

**Task Management:**
- `task_create.py <story> <num> <semantic-name>` - Create new task
- `task_list.py <story>` - List tasks for story
- `task_get_current.py` - Get current active task
- `task_update_state.py <task> <status>` - Update status (NOT_STARTED, IN_PROGRESS, COMPLETED)
- `task_update_phase.py <task> <phase>` - Update phase (RESEARCH, PLANNING, IMPLEMENTATION, TESTING, VALIDATION)
- `task_add_commit.py <task> <hash>` - Add commit to task record
- `task_add_file_modified.py <task> <file>` - Add modified file to task record

**Context Indexing:**
- `context_index.py [--story-id]` - Build SDLC index (future)

**Usage Pattern:**
```bash
# NEVER manually create files
# ALWAYS use scripts

# Create story
python3 .claude/skills/docs-stories/scripts/story_create.py auth login flow

# Create task
python3 .claude/skills/docs-stories/scripts/task_create.py US-028 19 route-guards

# Update phase
python3 .claude/skills/docs-stories/scripts/task_update_phase.py TASK-019 PLANNING

# Update status
python3 .claude/skills/docs-stories/scripts/task_update_state.py TASK-019 COMPLETED
```

### 9.2 Development Commands

**Makefile shortcuts:**
```bash
make dev          # Start all services with validation
make up           # Start without validation
make down         # Stop all services
make rebuild      # Full rebuild
make logs         # View all logs
make migrate      # Run Alembic migrations
make shell-db     # PostgreSQL shell
make shell-server # Backend container shell
make test-server  # Run backend tests
```

**Frontend commands:**
```bash
cd apps/frontend
npm run dev           # Start dev server
npm run build         # Build for production
npm run check         # TypeScript checking
npm run test:e2e      # Run E2E tests
npm run test:e2e:ui   # Playwright UI mode
```

**Backend commands:**
```bash
cd apps/server
pytest                # Run all tests
pytest --cov=server   # With coverage
python scripts/seed_bestays_production_properties.py  # Seed data
python scripts/backfill_property_embeddings.py both   # Generate embeddings
```

---

## 10. Best Practices

### 10.1 For Coordinators (Main Claude Instance)

**DO:**
- ✅ Load Memory MCP entities at session start
- ✅ Use docs-stories scripts for ALL story/task operations
- ✅ Use sequential-thinking for planning and architecture
- ✅ Validate against 7 quality gates during planning
- ✅ Use Svelte MCP for frontend tasks
- ✅ Spawn subagents for implementation
- ✅ Update STATE.json after phase transitions
- ✅ Create comprehensive documentation
- ✅ Ask questions when uncertain (AskUserQuestion tool)

**DON'T:**
- ❌ Edit implementation files (apps/*, tests/*) - use subagents
- ❌ Manually create story/task files - use scripts
- ❌ Skip quality gates - validate ALL gates
- ❌ Proceed with uncertainty - ask questions first
- ❌ Forget to update STATE.json - track progress
- ❌ Rush planning - quality gates exist for a reason

### 10.2 For Subagents (Implementation Agents)

**DO:**
- ✅ Read task folder (planning/, research/) before implementing
- ✅ Follow implementation-plan.md exactly
- ✅ Add comprehensive file headers
- ✅ Document decisions and trade-offs
- ✅ Create detailed implementation reports
- ✅ Commit with proper message format
- ✅ Test thoroughly before claiming completion
- ✅ (Backend) Validate with external HTTP tools

**DON'T:**
- ❌ Ignore planning artifacts - they exist for a reason
- ❌ Skip file headers - future context depends on them
- ❌ Commit without proper message format - breaks git workflow
- ❌ (Backend) Claim completion without external validation
- ❌ (Frontend) Ignore SSR considerations
- ❌ Assume - verify against official documentation

### 10.3 For Human Developers

**DO:**
- ✅ Review planning artifacts before approving implementation
- ✅ Validate acceptance criteria before marking task complete
- ✅ Provide clear high-level requirements in user stories
- ✅ Trust the SDLC process - it prevents issues
- ✅ Ask for clarification if planning seems unclear
- ✅ Review subagent reports - they contain important context

**DON'T:**
- ❌ Skip validation phase - it catches issues
- ❌ Bypass SDLC workflow - it's there for consistency
- ❌ Manually edit task STATE.json - use scripts
- ❌ Rush through acceptance criteria - they define success
- ❌ Ignore test failures - they indicate real problems

---

## Conclusion

The Bestays SDLC is a **revolutionary LLM-first system** that achieves:

- **Zero context loss** across sessions
- **< 3 minute context restoration** from cold start
- **90% automation** (validation only requires human input)
- **Professional-grade output** with comprehensive documentation
- **Self-enforcing boundaries** via hooks and scripts
- **Multi-product support** with efficient porting workflow

This system enables a **single human developer + Claude Code** to maintain a production-grade, multi-product platform with:
- Clear audit trail (who did what, when, why)
- Instant knowledge transfer (file headers, task folders, git history)
- Consistent quality (quality gates, automated tests, external validation)
- Sustainable development (documentation-first, memory print chain)

**The future of software development is LLM-first.** This system proves it works.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Maintained By:** Bestays Development Team
**Questions?** See `CLAUDE.md` or `.sdlc-workflow/` documentation
