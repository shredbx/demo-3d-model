# SDLC Workflow Documentation

Software Development Life Cycle (SDLC) documentation, user stories, tasks, and artifacts for the Bestays multi-product platform.

## 🎯 Purpose

This directory contains all SDLC processes, documentation, and artifacts designed specifically for **LLM-driven development** (Claude Code).

**Key Principle:** All SDLC processes exist to keep the LLM organized, consistent, and following established patterns across sessions.

## 📁 Directory Structure

```
.sdlc-workflow/
├── README.md                 # This file
├── .index/                   # Context indexes for fast restoration
│   └── context_*.json        # Generated context indexes by story
├── .plan/                    # High-level planning documents
│   ├── 01-architecture.md
│   ├── 02-phases.md
│   ├── 03-workflow-diagrams.md
│   └── progress.md
├── .specs/                   # Milestone specifications
│   ├── MILESTONE_01_WEBSITE_REPLICATION.md
│   └── ...
├── GIT_WORKFLOW.md          # Git workflow and branch naming
├── guides/                   # SDLC guides and best practices
│   ├── memory-print.md      # Memory print chain documentation
│   ├── confidence-criteria.md
│   └── ...
├── scripts/                  # Automation scripts
│   ├── story_create.py      # Create user stories
│   ├── task_create.py       # Create tasks
│   ├── task_update_*.py     # Update task state/phase
│   └── context_index.py     # Generate context indexes
├── stories/                  # User stories organized by domain
│   ├── authentication/
│   ├── chat/
│   ├── faq/
│   ├── properties/
│   └── infrastructure/
├── tasks/                    # Task folders (TEMPLATE/ + actual tasks)
│   ├── TEMPLATE/            # Task folder template
│   └── README.md            # Task system documentation
└── templates/               # Document templates
    ├── STORY_TEMPLATE.md
    └── TASK_TEMPLATE.md
```

## 🔄 SDLC Phases

### 1. RESEARCH
**Purpose:** Explore codebase, gather context, understand existing patterns

**Activities:**
- Code exploration (Glob, Grep, Read)
- Pattern identification
- Dependency analysis
- Context gathering

**Output:**
- Research findings in `.claude/tasks/TASK-XXX/research/`
- Pattern documentation
- Existing implementation references

**Coordinator tool usage:** ✅ Direct file reading allowed

### 2. PLANNING
**Purpose:** Design solution, define architecture, apply quality gates

**Activities:**
- Architecture design
- Sequential thinking (mandatory)
- Apply 7 quality gates (from `@.claude/skills/planning-quality-gates/`)
- Create specifications
- Define acceptance criteria

**Output:**
- Planning docs in `.claude/tasks/TASK-XXX/planning/`
- Architecture diagrams
- Quality gate checklists
- Acceptance criteria

**Coordinator tool usage:** ✅ Direct planning allowed

**Mandatory:** Must use `mcp__sequential-thinking__sequentialthinking` tool

**Quality Gates (7 Required):**
1. Network Operations (retry, error handling, offline detection)
2. Frontend SSR/UX (SSR compatibility, hydration)
3. Testing Requirements (coverage, scenarios, browsers)
4. Deployment Safety (risk assessment, rollback, monitoring)
5. Acceptance Criteria (technical criteria, story mapping, DoD)
6. Dependencies (external/internal deps, technical debt)
7. **Official Documentation Validation** (Svelte MCP, MDN, vendor docs)

### 3. IMPLEMENTATION
**Purpose:** Write code via specialized subagents

**Activities:**
- Launch appropriate subagents (dev-frontend-svelte, dev-backend-fastapi, etc.)
- Implement features
- Apply dev-philosophy and dev-code-quality skills
- Document code with file headers
- Create memory print chain

**Output:**
- Implementation code in `apps/server/` or `apps/frontend/`
- Subagent reports in `.claude/tasks/TASK-XXX/subagent-reports/`
- Git commits with semantic task IDs

**Coordinator tool usage:** ❌ NEVER edit implementation files directly (use subagents)

### 4. TESTING
**Purpose:** Validate implementation with automated and manual tests

**Activities:**
- Unit tests (Vitest, pytest)
- E2E tests (Playwright via playwright-e2e-tester agent)
- Manual testing with test credentials
- Integration testing
- Coverage validation (80% minimum enforced)

**Output:**
- Test results in `.claude/tasks/TASK-XXX/testing/`
- Test coverage reports
- Bug reports and fixes

**Test Automation:**
- ✅ **CI/CD pipeline** (`.github/workflows/ci.yml`) runs all tests on push/PR
- ✅ **Pre-commit hooks** (optional) for fast local validation (< 30s)
- ✅ **Coverage enforcement** blocks merge if < 80%
- ✅ **Multi-browser testing** (Chromium, Firefox, Webkit)
- ✅ **Merge gating** - PRs blocked if any test fails

**Quick commands:**
```bash
make test-all         # All tests (frontend + backend)
make test-fast        # Fast tests only (type check + unit tests)
make test-coverage    # With coverage reports
```

**Pre-commit hook installation:**
```bash
.sdlc-workflow/scripts/setup-git-hooks.sh
```

**Documentation:** See `.sdlc-workflow/guides/testing-strategy.md` for complete testing guide

**Coordinator tool usage:** ✅ Can run tests, ❌ Cannot fix code directly (use subagents)

### 5. VALIDATION
**Purpose:** Final review, merge, and deployment

**Activities:**
- Code review (qa-code-auditor agent)
- Merge to main branch
- Deploy to staging/production
- Update documentation

**Output:**
- Review reports
- Deployment logs
- Updated documentation

## 📖 User Stories

### Story Organization

Stories are organized by domain in `stories/`:

```
stories/
├── authentication/       # Login, signup, RBAC, Clerk
├── chat/                # AI chat, LLM integration
├── faq/                 # FAQ feature
├── properties/          # Property listings, search, details
└── infrastructure/      # SDLC, DevOps, tooling
```

### Story Structure

Each story is a markdown file with:
- **Title** and **ID** (US-XXX)
- **Description** and **Acceptance Criteria**
- **Multi-Product Metadata** (default product, portable, ported_to)
- **Tasks** (list of related tasks)
- **Technical Notes**
- **References**

**Example:**
```markdown
# US-001: User Login with Clerk

**Status:** completed
**Priority:** high
**Default Product:** bestays
**Portable:** true
**Ported To:** []

## Description
Implement user authentication using Clerk...

## Acceptance Criteria
- [ ] Users can log in with email/password
- [ ] Session persists across page reloads
- [ ] Login redirects to /home

## Tasks
- TASK-001-clerk-mounting (completed)
- TASK-002-login-tests (completed)
```

### Creating Stories

**Use the docs-stories skill:**
```bash
# Via skill
docs-stories create story <domain> <title>

# Via script
python .sdlc-workflow/scripts/story_create.py <domain> <title>
```

**Example:**
```bash
python .sdlc-workflow/scripts/story_create.py authentication user-login-clerk
# Creates: .sdlc-workflow/stories/authentication/US-XXX-user-login-clerk.md
```

## 📋 Tasks

### Task Folder System

**Purpose:** Preserve ALL decision context and implementation artifacts.

**Structure:**
```
.claude/tasks/TASK-XXX-semantic-name/
├── STATE.json           # Story, phase, status, type, commits, files
├── README.md            # What needs to be done
├── planning/            # Specs, decisions, quality gates
│   ├── architecture.md
│   ├── quality-gates-checklist.md
│   └── acceptance-criteria.md
├── research/            # Findings, patterns discovered
│   └── existing-patterns.md
├── implementation/      # Code artifacts, decisions
│   └── implementation-notes.md
├── testing/             # Test results, coverage
│   └── test-results.md
└── subagent-reports/    # Subagent outputs
    └── dev-frontend-svelte-report.md
```

### Task Types

- **FEATURE** - New functionality
- **BUGFIX** - Fix existing issues
- **REFACTOR** - Code improvement
- **PORTING** - Port feature from one product to another
- **RESEARCH** - Investigation task
- **INFRASTRUCTURE** - DevOps, tooling

### Semantic Task IDs

**Pattern:** `TASK-{number}-{semantic-slug}`

**Examples:**
- `TASK-001-clerk-mounting`
- `TASK-002-login-tests`
- `TASK-050-port-login-realestate`

**Why:**
- Self-documenting git history
- Clear branch names
- Easy to understand context

### Creating Tasks

**Use the docs-stories skill:**
```bash
# Via skill
docs-stories create task <story-id> <task-number> <task-name>

# Via script
python .sdlc-workflow/scripts/task_create.py <story-id> <task-number> <task-name>
```

**Example:**
```bash
python .sdlc-workflow/scripts/task_create.py US-001 1 clerk-mounting
# Creates: .claude/tasks/TASK-001-clerk-mounting/
```

### Updating Task State

```bash
# Update phase
python .sdlc-workflow/scripts/task_update_phase.py TASK-001 IMPLEMENTATION

# Update status
python .sdlc-workflow/scripts/task_update_state.py TASK-001 in_progress

# Add commits
python .sdlc-workflow/scripts/task_update_commits.py TASK-001 <commit-hash>

# Mark complete
python .sdlc-workflow/scripts/task_update_state.py TASK-001 completed
```

## 🏗️ Multi-Product Workflow

### Strategy

**Build for Bestays first** (default product), then **port to Real Estate** via porting tasks.

### Story Metadata

```markdown
**Default Product:** bestays
**Portable:** true
**Ported To:** []
```

### 4-Step Porting Workflow

**Step 1: Implement for Bestays**
```bash
python .sdlc-workflow/scripts/story_create.py auth login-flow
python .sdlc-workflow/scripts/task_create.py US-XXX 1 login-bestays
# Subagent implements
# Commit: feat: implement login (US-XXX TASK-001-login-bestays)
```

**Step 2: Create Porting Task**
```bash
python .sdlc-workflow/scripts/task_create.py US-XXX 50 port-login-realestate \
    --type PORTING \
    --source-product bestays \
    --target-product realestate \
    --source-task TASK-001
```

**Step 3: Execute Porting**
```bash
# Subagent reads porting-checklist.md and source implementation
# Adapts files for realestate (redirects, branding, roles)
# Commit: feat: port login to real estate (US-XXX TASK-050-port-login-realestate)
```

**Step 4: Update Story Metadata**
```bash
python .sdlc-workflow/scripts/story_update_ported.py US-XXX realestate
# Story: ported_to: [realestate]
```

### Portable vs Product-Specific

**Portable (shared logic):**
- Authentication logic
- Validation rules
- UI components
- Business logic (product-agnostic)

**Product-Specific:**
- Redirect URLs (`/home` vs `/dashboard`)
- Branding (colors, logos, names)
- Role mappings (admin permissions)
- Domain logic (property types)
- Database-specific fields

**Full workflow:** See `.claude/reports/20251107-multi-product-story-workflow.md`

## 📝 Memory Print Chain

**Philosophy:** Every artifact leaves a "memory print" for instant context restoration.

**Chain:** User Story → Task → File Header → Comments → Git History

### File Headers Must Include:

- **Design pattern** (Singleton, Factory, Repository)
- **Architecture layer** (API, Service, Model, Component)
- **Dependencies** (external, internal)
- **Trade-offs** (pros, cons, when to revisit)
- **Integration points**
- **Testing notes**

**Example:**
```python
"""
User authentication service using Clerk.

Design Pattern: Singleton service
Layer: API/Service
Dependencies: Clerk SDK, FastAPI
Trade-offs:
  - Pro: Managed auth, no user table needed
  - Con: Vendor lock-in, external dependency
  - Revisit: If Clerk pricing changes or we need custom auth
Integration: Webhook endpoint at /api/v1/webhooks/clerk
Testing: Use test credentials from .env.bestays
"""
```

**Full guide:** `.sdlc-workflow/guides/memory-print.md`

## 🔧 Scripts and Automation

### Story Management
- `story_create.py` - Create new user story
- `story_update_ported.py` - Mark story as ported
- `story_list.py` - List all stories

### Task Management
- `task_create.py` - Create new task
- `task_update_phase.py` - Update task phase
- `task_update_state.py` - Update task status
- `task_update_commits.py` - Add commits to task
- `task_list.py` - List all tasks

### Context Management
- `context_index.py` - Generate context index for story
- `context_restore.py` - Restore context from index

**All scripts use filesystem as source of truth (no complex registries).**

## 🎓 Skills

### Mandatory Skills

**docs-stories** (`.claude/skills/docs-stories/`)
- ALL story/task CRUD operations
- Context retrieval via indexes
- Never bypass docs-stories scripts

**sdlc-orchestrator** (`.claude/skills/sdlc-orchestrator/`)
- Phase transition checklists
- Quality gate enforcement
- "What to do next" guidance

### Core Development Skills

All subagents must use:
- `dev-philosophy` - Development standards
- `dev-code-quality` - Code quality standards

## 📊 Progress Tracking

### Current Milestone

**MILESTONE 01: Website Replication**

See: `.sdlc-workflow/.specs/MILESTONE_01_WEBSITE_REPLICATION.md`

### Progress Document

See: `.sdlc-workflow/.plan/progress.md`

Tracks:
- Completed stories
- In-progress tasks
- Blocked items
- Next priorities

## 🔀 Git Workflow

### Branch Naming

**Pattern:** `feat/TASK-{number}-{semantic-slug}-US-{story-id}`

**Examples:**
- `feat/TASK-001-clerk-mounting-US-001`
- `feat/TASK-050-port-login-realestate-US-001`

### Commit Messages

```
type: description (US-XXX TASK-YYY-semantic-name)

Subagent: <which-subagent>
Product: <bestays | realestate>
Files: <list-of-files>

<detailed description>

Story: US-XXX
Task: TASK-YYY-semantic-name

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Full workflow:** `.sdlc-workflow/GIT_WORKFLOW.md`

## 🚀 Quick Reference

### Creating a New Feature

1. **Create Story:**
   ```bash
   python .sdlc-workflow/scripts/story_create.py <domain> <feature-name>
   ```

2. **Create Task:**
   ```bash
   python .sdlc-workflow/scripts/task_create.py <story-id> 1 <task-name>
   ```

3. **Create Branch:**
   ```bash
   git checkout -b feat/TASK-001-<task-name>-<story-id>
   ```

4. **Research Phase:**
   - Explore codebase
   - Document findings in `.claude/tasks/TASK-001-<task-name>/research/`

5. **Planning Phase:**
   - Use Sequential Thinking
   - Apply 7 quality gates
   - Create specs in `.claude/tasks/TASK-001-<task-name>/planning/`

6. **Implementation Phase:**
   - Launch appropriate subagent
   - Implement feature
   - Subagent creates reports

7. **Testing Phase:**
   - Run unit tests
   - Run E2E tests
   - Manual testing

8. **Validation Phase:**
   - Code review
   - Merge to main
   - Update docs

### Context Restoration

```bash
# Generate context index for a story
python .sdlc-workflow/scripts/context_index.py US-001

# Use docs-stories skill to retrieve context
docs-stories get context US-001

# Loads all relevant files, decisions, and patterns
```

## 📚 Additional Documentation

- **CLAUDE.md** - Main Claude Code instructions
- **Root README.md** - Project overview
- **.claude/reports/** - Architecture decisions, reports
- **apps/server/README.md** - Backend documentation
- **apps/frontend/README.md** - Frontend documentation
- **docker/README.md** - Docker and multi-product setup

---

**Version:** 1.0
**Last Updated:** 2025-11-08
**Designed for:** LLM-driven development (Claude Code)
**Multi-Product Support:** Yes (Bestays + Real Estate)
