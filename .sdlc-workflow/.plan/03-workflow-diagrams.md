# Complete SDLC Workflow Diagrams

**Created:** 2025-11-01 12:19
**Purpose:** Visual representation of command flows, agent spawning, hooks, and data flow
**Status:** Architecture Diagram

---

## Overview

This document provides comprehensive diagrams showing:

1. Complete SDLC workflow (end-to-end user story lifecycle)
2. Agent spawning decision tree
3. Hook trigger timeline
4. Data flow and context passing
5. Conditional behaviors

**Diagram Legend:**

```
[Command]     = User-invoked slash command
(Agent)       = Spawned subagent
{Hook}        = Claude CLI or git hook trigger
<Script>      = Python script execution
[[File]]      = File read/write
→             = Flow/transition
├─            = Branch/conditional
✓             = Validation checkpoint
```

---

## Diagram 1: Complete SDLC Workflow (End-to-End)

### Full User Story Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 0: STORY CREATION                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

User
  │
  └─→ [/story-new]
        │
        ├─→ <story_create.py>
        │     ├─→ Generate US-XXX ID
        │     ├─→ [[Create .sdlc-workflow/stories/domain/feature.md]]
        │     └─→ Set status: READY
        │
        └─→ Story created: US-001-auth-login-admin


┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: TASK CREATION & PLANNING                                           │
└─────────────────────────────────────────────────────────────────────────────┘

User
  │
  └─→ [/task-new US-001 feat]
        │
        ├─→ {UserPromptSubmit hook}
        │     └─→ <validate_command.py>
        │           └─→ ✓ Verify US-001 exists
        │
        ├─→ <task_create.py>
        │     ├─→ Generate TASK-001
        │     ├─→ [[Create .claude/tasks/TASK-001/]]
        │     ├─→ [[Create .claude/tasks/TASK-001/STATE.json]]
        │     ├─→ Create git branch: feat/TASK-001-US-001-auth-login-admin
        │     ├─→ {Git post-checkout hook}
        │     │     └─→ Update .claude/tasks/current.txt → TASK-001
        │     └─→ Set STATE.json phase: PLANNING
        │
        └─→ Task TASK-001 created, branch created, ready for research


┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: RESEARCH                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

User
  │
  └─→ [/task-research]
        │
        ├─→ {UserPromptSubmit hook}
        │     └─→ ✓ Verify active task exists (TASK-001)
        │
        ├─→ Load task context
        │     ├─→ [[Read STATE.json]]
        │     ├─→ [[Read .sdlc-workflow/stories/US-001...]]
        │     └─→ Prepare agent context
        │
        ├─→ Spawn (Explore agent) with "medium" thoroughness
        │     │
        │     │   ┌───────────────────────────────────────────┐
        │     │   │ EXPLORE AGENT SUBPROCESS                  │
        │     │   ├───────────────────────────────────────────┤
        │     │   │ • Analyzes apps/server/ for auth patterns│
        │     │   │ • Searches git history for similar impl  │
        │     │   │ • Identifies dependencies (Clerk, etc.)  │
        │     │   │ • Creates research findings              │
        │     │   └───────────────────────────────────────────┘
        │     │
        │     └─→ Returns: research findings
        │
        ├─→ {SubagentStop hook}
        │     └─→ <subagent_stop.py>
        │           ├─→ ✓ Verify research artifacts exist
        │           └─→ [[Save to TASK-001/research/*.md]]
        │
        ├─→ <task_update_phase.py TASK-001 RESEARCH complete>
        │     └─→ Update STATE.json phase history
        │
        └─→ Research complete, ready for planning


┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: PLANNING                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

User
  │
  └─→ [/task-plan --estimate]
        │
        ├─→ Load context
        │     ├─→ [[Read STATE.json]]
        │     ├─→ [[Read story]]
        │     ├─→ [[Read TASK-001/research/*.md]]
        │     └─→ Prepare planning context
        │
        ├─→ Spawn (Plan agent) ←──────────────┐ FEEDBACK LOOP
        │     │                             │
        │     │   ┌───────────────────────────────────────────┐
        │     │   │ PLAN AGENT SUBPROCESS                     │
        │     │   ├───────────────────────────────────────────┤
        │     │   │ • Designs architecture approach           │
        │     │   │ • Identifies: dev-backend + dev-frontend  │
        │     │   │ • Estimates complexity from git history   │
        │     │   │ • Creates implementation plan             │
        │     │   └───────────────────────────────────────────┘
        │     │
        │     └─→ Returns: draft implementation plan
        │
        ├─→ Main LLM presents plan to user
        │     "Here's the proposed plan. Review:
        │      • Architecture: Clean Architecture with DDD
        │      • Agents: dev-backend → dev-frontend
        │      • Estimate: ~8 hours
        │      Questions or changes needed?"
        │
        ├─→ User reviews and provides feedback
        │     │
        │     ├─→ IF: User has questions/concerns     │
        │     │     └─→ Main LLM discusses with user  │
        │     │           └─→ Respawn Plan agent ─────┘
        │     │               with refinement context
        │     │
        │     └─→ IF: User approves
        │           └─→ Continue (break loop)
        │
        ├─→ {SubagentStop hook}
        │     └─→ ✓ Verify plan has agent assignments
        │
        ├─→ [[Save to TASK-001/planning/implementation-plan.md]]
        │
        ├─→ <task_update_phase.py TASK-001 IMPLEMENTATION start>
        │
        └─→ Planning complete (approved), ready to implement


┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: IMPLEMENTATION (Backend)                                           │
└─────────────────────────────────────────────────────────────────────────────┘

User
  │
  └─→ [/task-implement backend]
        │
        ├─→ Load complete context
        │     ├─→ [[Read STATE.json]]
        │     ├─→ [[Read story]]
        │     ├─→ [[Read research]]
        │     ├─→ [[Read plan]]
        │     └─→ Enrich agent context with all findings
        │
        ├─→ Spawn (dev-backend agent)
        │     │
        │     │   ┌─────────────────────────────────────────────────┐
        │     │   │ dev-backend AGENT SUBPROCESS                    │
        │     │   ├─────────────────────────────────────────────────┤
        │     │   │ Working directory: apps/server/                 │
        │     │   │ Mandatory skills: backend-python-fastapi,              │
        │     │   │                  backend-architecture,          │
        │     │   │                  backend-async-python,          │
        │     │   │                  backend-python-testing         │
        │     │   ├─────────────────────────────────────────────────┤
        │     │   │ Actions:                                        │
        │     │   │ 1. Create apps/server/src/auth/routes.py        │
        │     │   │      ↓                                           │
        │     │   │    {PreToolUse hook}                            │
        │     │   │      └→ <pre_tool_use.py>                       │
        │     │   │           ├─→ Check: file in apps/server/ ✓     │
        │     │   │           ├─→ Required: dev-backend agent ✓     │
        │     │   │           └─→ Current: dev-backend agent ✓      │
        │     │   │                ALLOW                             │
        │     │   │      ↓                                           │
        │     │   │    [Edit tool executes]                         │
        │     │   │      ↓                                           │
        │     │   │    {PostToolUse hook}                           │
        │     │   │      └→ <post_tool_use.py>                      │
        │     │   │           └─→ Add to files_modified[]           │
        │     │   │                                                  │
        │     │   │ 2. Create apps/server/src/auth/clerk.py         │
        │     │   │    [Same hook flow]                             │
        │     │   │                                                  │
        │     │   │ 3. Create tests/backend/test_auth.py            │
        │     │   │    [Same hook flow]                             │
        │     │   │                                                  │
        │     │   │ 4. git commit -m "add login API endpoint"       │
        │     │   │      ↓                                           │
        │     │   │    {Git prepare-commit-msg hook}                │
        │     │   │      └→ Format: feat(auth): add login API       │
        │     │   │                  endpoint [TASK-001/US-001]     │
        │     │   │      ↓                                           │
        │     │   │    [Commit created]                             │
        │     │   │      ↓                                           │
        │     │   │    {Git post-commit hook}                       │
        │     │   │      └→ Map commit → TASK-001                   │
        │     │   │      ↓                                           │
        │     │   │    {PostToolUse hook}                           │
        │     │   │      └→ <post_tool_use.py>                      │
        │     │   │           ├─→ Get commit SHA, message, time     │
        │     │   │           └─→ Add to STATE.json commits[]       │
        │     │   │                                                  │
        │     │   │ 5. Repeat for additional files/commits          │
        │     │   └─────────────────────────────────────────────────┘
        │     │
        │     └─→ Returns: Files modified, commits made
        │
        ├─→ {SubagentStop hook}
        │     └─→ <subagent_stop.py>
        │           ├─→ ✓ Commits made (3 commits)
        │           ├─→ ✓ Backend files modified
        │           ├─→ ✓ Test files created
        │           ├─→ ✓ Coverage delta check passed
        │           └─→ Update STATE.json agents_used: [dev-backend]
        │
        ├─→ Main LLM presents results to user ←──────────┐ POST-JOB DISCUSSION
        │     "Backend implementation complete:           │
        │      • 3 commits made                           │
        │      • API endpoints: POST /api/auth/login      │
        │      • Tests: 12 passing, 94% coverage          │
        │      • All quality gates passed                 │
        │      Review and approve, or request changes?"   │
        │                                                  │
        ├─→ User reviews agent work                       │
        │     │                                            │
        │     ├─→ IF: User requests changes               │
        │     │     └─→ Main LLM respawns dev-backend ────┘
        │     │           agent with refinement context
        │     │
        │     └─→ IF: User approves
        │           └─→ Continue (break loop)
        │
        ├─→ [[Save TASK-001/context/backend-done.md]]
        │     └─→ Summary: API endpoints created, tests passing
        │
        └─→ Backend implementation complete and approved


┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: IMPLEMENTATION (Frontend)                                          │
└─────────────────────────────────────────────────────────────────────────────┘

User
  │
  └─→ [/task-implement frontend]
        │
        ├─→ Load enriched context
        │     ├─→ [[Read STATE.json]]
        │     ├─→ [[Read story]]
        │     ├─→ [[Read research]]
        │     ├─→ [[Read plan]]
        │     ├─→ [[Read TASK-001/context/backend-done.md]]  ← Backend results!
        │     └─→ Agent knows: "Backend API at /api/auth/login"
        │
        ├─→ Spawn (dev-frontend agent)
        │     │
        │     │   ┌─────────────────────────────────────────────────┐
        │     │   │ dev-frontend AGENT SUBPROCESS                   │
        │     │   ├─────────────────────────────────────────────────┤
        │     │   │ Working directory: apps/frontend/               │
        │     │   │ Mandatory skills: frontend-svelte               │
        │     │   │ Context: Knows backend API is ready             │
        │     │   ├─────────────────────────────────────────────────┤
        │     │   │ Actions:                                        │
        │     │   │ 1. Create apps/frontend/src/routes/admin/       │
        │     │   │           login/+page.svelte                    │
        │     │   │    → Integrates with backend API                │
        │     │   │    → [PreToolUse validates dev-frontend agent]  │
        │     │   │                                                  │
        │     │   │ 2. Create apps/frontend/src/lib/api/auth.ts     │
        │     │   │    → API client for /api/auth/login             │
        │     │   │                                                  │
        │     │   │ 3. Create tests/frontend/login.spec.ts          │
        │     │   │                                                  │
        │     │   │ 4. git commit (with hooks, same as backend)     │
        │     │   └─────────────────────────────────────────────────┘
        │     │
        │     └─→ Returns: Files modified, commits made
        │
        ├─→ {SubagentStop hook}
        │     └─→ ✓ Validate completeness
        │           └─→ Update agents_used: [dev-backend, dev-frontend]
        │
        └─→ Implementation complete (both domains)


┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 6: TESTING                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

User
  │
  └─→ [/task-test --coverage]
        │
        ├─→ <task_run_tests.py TASK-001 all>
        │     ├─→ Run backend tests: pytest apps/server/tests/
        │     │     └─→ 12 tests passing, 95% coverage
        │     │
        │     ├─→ Run frontend tests: vitest apps/frontend/tests/
        │     │     └─→ 6 tests passing, 92% coverage
        │     │
        │     └─→ <task_update_tests.py TASK-001>
        │           └─→ Update STATE.json tests section
        │
        └─→ All tests passing


┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 7: VALIDATION                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

User
  │
  └─→ [/task-validate]
        │
        ├─→ <task_validate_quality.py TASK-001>
        │     │
        │     ├─→ <lint_check.py>
        │     │     ├─→ ruff check apps/server/ → PASS
        │     │     └─→ eslint apps/frontend/ → PASS
        │     │
        │     ├─→ <type_check.py>
        │     │     ├─→ mypy apps/server/ → PASS
        │     │     └─→ tsc apps/frontend/ → PASS
        │     │
        │     ├─→ <security_scan.py>
        │     │     └─→ bandit apps/server/ → PASS (0 issues)
        │     │
        │     ├─→ <acceptance_criteria_check.py TASK-001>
        │     │     ├─→ [[Read story acceptance criteria]]
        │     │     ├─→ [[Read STATE.json commits]]
        │     │     ├─→ [[Read test results]]
        │     │     └─→ 4/4 criteria met → PASS
        │     │
        │     └─→ <task_update_quality.py TASK-001>
        │           └─→ Update STATE.json quality_gates
        │
        └─→ All quality gates passed


┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 8: COMPLETION                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

User
  │
  └─→ [/task-complete]
        │
        ├─→ Run final validation
        │     └─→ <task_validate_quality.py TASK-001> → ALL PASS
        │
        ├─→ Generate retrospective
        │     └─→ <git_stats.py TASK-001>
        │           ├─→ Analyze all commits
        │           ├─→ Calculate time spent per phase
        │           ├─→ Count files modified, tests created
        │           ├─→ Compare estimate vs actual
        │           └─→ [[Save TASK-001/retrospective.md]]
        │
        ├─→ Update STATE.json
        │     ├─→ status: completed
        │     ├─→ timestamps.completed: <now>
        │     └─→ Calculate total duration
        │
        ├─→ Ask: "Ready to archive?"
        │     └─→ User: "yes"
        │
        ├─→ <task_archive.py TASK-001>
        │     ├─→ Move TASK-001/ → archive/TASK-001/
        │     └─→ .claude/tasks/current.txt → "none"
        │
        └─→ Task complete! Summary:
              - 6 commits made
              - 8 files modified
              - 18 tests (all passing)
              - 94% coverage
              - All quality gates passed
              Ready to: git push, create PR, merge


┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 9: GIT WORKFLOW & CI VALIDATION                                       │
└─────────────────────────────────────────────────────────────────────────────┘

User (manual git operations)
  │
  ├─→ git push origin feat/TASK-001-US-001-auth-login-admin
  │
  ├─→ gh pr create --title "feat(auth): Admin login [US-001]"
  │     (Note: PR title also follows conventional commits)
  │
  ├─→ CI Pipeline Triggers (GitHub Actions)
  │     │
  │     ├─→ Validate Commit Messages
  │     │     └─→ ✓ All commits follow: type(scope): message [TASK-xxx/US-xxx]
  │     │
  │     ├─→ Validate STATE.json Integrity
  │     │     └─→ ✓ TASK-001/STATE.json valid
  │     │
  │     ├─→ Validate Commit-Task Mapping
  │     │     └─→ ✓ All commits mapped to TASK-001
  │     │
  │     ├─→ Run Tests
  │     │     ├─→ Backend: pytest (18 tests, all passing)
  │     │     └─→ Frontend: vitest (6 tests, all passing)
  │     │
  │     ├─→ Validate Coverage Delta
  │     │     ├─→ Backend: 94% (baseline: 80%) ✓
  │     │     └─→ Frontend: 92% (baseline: 75%) ✓
  │     │
  │     ├─→ Validate Agent Ownership
  │     │     └─→ ✓ All files have valid owners (README.md)
  │     │
  │     └─→ Run Quality Gates
  │           ├─→ Lint: PASS
  │           ├─→ Type check: PASS
  │           └─→ Security scan: PASS
  │
  ├─→ IF: CI FAILS
  │     ├─→ PR blocked, cannot merge
  │     ├─→ User must fix issues
  │     └─→ Push fixes → CI re-runs
  │
  ├─→ IF: CI PASSES
  │     ├─→ PR ready for review
  │     ├─→ [Code review, approval]
  │     └─→ Merge to main/develop
  │
  └─→ git branch -d feat/TASK-001-US-001-auth-login-admin

DONE! Story US-001 implemented, tested, validated by CI, merged.
```

---

## Diagram 2: Agent Spawning Decision Tree

### When to Spawn Which Agent

```
User Command Received
  │
  ├─→ [/task-research]
  │     └─→ Spawn (Explore agent)
  │           • Thoroughness: medium (default) or user-specified
  │           • Purpose: Find existing patterns, dependencies
  │           • Returns: Research findings
  │
  ├─→ [/task-plan]
  │     └─→ Spawn (Plan agent)
  │           • Purpose: Design architecture, identify agent needs
  │           • Returns: Implementation plan
  │
  ├─→ [/task-implement backend]
  │     └─→ Spawn (dev-backend agent)
  │           • Working dir: apps/server/
  │           • Skills: backend-python-fastapi, backend-architecture, etc.
  │           • Returns: Files modified, commits
  │
  ├─→ [/task-implement frontend]
  │     └─→ Spawn (dev-frontend agent)
  │           • Working dir: apps/frontend/
  │           • Skills: frontend-svelte
  │           • Returns: Files modified, commits
  │
  ├─→ [/task-implement fullstack]
  │     │
  │     ├─→ STEP 1: Spawn (dev-backend agent)
  │     │     ├─→ Implement backend
  │     │     ├─→ Wait for completion
  │     │     └─→ [[Save context/backend-done.md]]
  │     │
  │     └─→ STEP 2: Spawn (dev-frontend agent)
  │           ├─→ Load backend context
  │           ├─→ Implement frontend with backend knowledge
  │           └─→ Return results
  │
  ├─→ [/task-test] (if tests missing)
  │     │
  │     ├─→ IF: Backend tests missing
  │     │     └─→ Spawn (dev-backend agent) to create tests
  │     │
  │     └─→ IF: Frontend tests missing
  │           └─→ Spawn (dev-frontend agent) to create tests
  │
  └─→ [Direct file edit attempt]
        │
        ├─→ {PreToolUse hook triggers}
        │     │
        │     ├─→ IF: file in apps/server/**
        │     │     ├─→ Current agent: dev-backend? ✓ ALLOW
        │     │     └─→ Current agent: other/none? ✗ BLOCK
        │     │           └─→ Message: "Spawn dev-backend agent first"
        │     │
        │     ├─→ IF: file in apps/frontend/**
        │     │     ├─→ Current agent: dev-frontend? ✓ ALLOW
        │     │     └─→ Current agent: other/none? ✗ BLOCK
        │     │           └─→ Message: "Spawn dev-frontend agent first"
        │     │
        │     └─→ IF: file in docker/, Makefile
        │           ├─→ Current agent: devops-infra? ✓ ALLOW
        │           └─→ Current agent: other/none? ✗ BLOCK
        │                 └─→ Message: "Spawn devops-infra agent first"
        │
        └─→ IF BLOCKED: Operation aborted, user must spawn correct agent
```

---

## Diagram 3: Hook Trigger Timeline

### Hooks Throughout Session Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│ SESSION LIFECYCLE WITH HOOKS                                            │
└─────────────────────────────────────────────────────────────────────────┘

User runs: claude
  │
  └─→ {SessionStart hook}
        └─→ <session_start.py>
              ├─→ Read .claude/tasks/current.txt
              ├─→ IF task exists:
              │     ├─→ Read STATE.json
              │     ├─→ Display task info
              │     └─→ Suggest next command
              └─→ IF no task:
                    └─→ "No active task. Use /task-new or /task-resume"

┌─────────────────────────────────────────────────────────────────────────┐
│ USER PROMPT SUBMISSION                                                  │
└─────────────────────────────────────────────────────────────────────────┘

User types: /task-implement backend
  │
  └─→ {UserPromptSubmit hook}
        └─→ <validate_command.py>
              ├─→ Check: Does /task-implement require active task? Yes
              ├─→ Check: Is there an active task? Yes (TASK-001)
              └─→ ✓ ALLOW command to proceed

┌─────────────────────────────────────────────────────────────────────────┐
│ TOOL EXECUTION - BEFORE                                                 │
└─────────────────────────────────────────────────────────────────────────┘

Claude attempts: Edit apps/server/src/auth/routes.py
  │
  └─→ {PreToolUse hook}
        └─→ <pre_tool_use.py>
              ├─→ Tool: Edit
              ├─→ File: apps/server/src/auth/routes.py
              ├─→ Required agent: dev-backend (apps/server/ scope)
              ├─→ Current agent: dev-backend
              └─→ ✓ ALLOW edit

Alternative (blocked):
Claude attempts: Edit apps/server/src/auth/routes.py
  │
  └─→ {PreToolUse hook}
        └─→ <pre_tool_use.py>
              ├─→ Tool: Edit
              ├─→ File: apps/server/src/auth/routes.py
              ├─→ Required agent: dev-backend
              ├─→ Current agent: none (main LLM)
              └─→ ✗ BLOCK edit
                    └─→ "Must spawn dev-backend agent first"

┌─────────────────────────────────────────────────────────────────────────┐
│ TOOL EXECUTION - AFTER                                                  │
└─────────────────────────────────────────────────────────────────────────┘

Edit tool completes
  │
  └─→ {PostToolUse hook}
        └─→ <post_tool_use.py>
              ├─→ Tool: Edit
              ├─→ File: apps/server/src/auth/routes.py
              ├─→ Read current task: TASK-001
              ├─→ Update STATE.json:
              │     └─→ Add to files_modified[]
              └─→ Update timestamps.last_accessed

Git commit completes
  │
  ├─→ {Git prepare-commit-msg hook}
  │     └─→ Prepend task/story IDs to message
  │
  ├─→ [Commit created]
  │
  ├─→ {Git post-commit hook}
  │     └─→ Create commit-task mapping
  │
  └─→ {PostToolUse hook}
        └─→ <post_tool_use.py>
              ├─→ Tool: Bash (git commit)
              ├─→ Get commit SHA, message, timestamp
              └─→ Update STATE.json commits[]

┌─────────────────────────────────────────────────────────────────────────┐
│ SUBAGENT COMPLETION                                                     │
└─────────────────────────────────────────────────────────────────────────┘

(dev-backend agent) finishes and returns to main LLM
  │
  └─→ {SubagentStop hook}
        └─→ <subagent_stop.py>
              ├─→ Agent: dev-backend
              ├─→ Validate:
              │     ├─→ ✓ Commits made? Yes (3 commits)
              │     ├─→ ✓ Backend files modified? Yes
              │     └─→ ✓ Tests created? Yes
              ├─→ Update STATE.json:
              │     └─→ Add dev-backend to agents_used[]
              └─→ ✓ Validation passed

Alternative (incomplete work):
(dev-backend agent) finishes but missing tests
  │
  └─→ {SubagentStop hook}
        └─→ <subagent_stop.py>
              ├─→ Agent: dev-backend
              ├─→ Validate:
              │     ├─→ ✓ Commits made? Yes
              │     ├─→ ✓ Backend files modified? Yes
              │     └─→ ✗ Tests created? No
              └─→ ⚠️  Warning: "No test files created. Please add tests."
                    (SubagentStop can't block, but warns)

┌─────────────────────────────────────────────────────────────────────────┐
│ SESSION END                                                             │
└─────────────────────────────────────────────────────────────────────────┘

User exits or timeout
  │
  └─→ {SessionEnd hook} (optional, not configured yet)
        └─→ Could save final state, cleanup, etc.

```

---

## Diagram 4: Data Flow & Context Passing

### How Information Flows Through the System

```
┌─────────────────────────────────────────────────────────────────────────┐
│ DATA SOURCES → PROCESSING → STORAGE → RETRIEVAL                         │
└─────────────────────────────────────────────────────────────────────────┘

Story File (.sdlc-workflow/stories/auth/login.md)
  │
  │  Contains:
  │  • Story ID: US-001
  │  • Description: Admin login functionality
  │  • Acceptance criteria (4 items)
  │  • Domain: auth
  │
  └─→ READ by: /story-view, /task-new
        │
        └─→ FLOWS TO: Task STATE.json (story_id field)


Task STATE.json (.claude/tasks/TASK-001/STATE.json)
  │
  │  Contains:
  │  • task_id, story_id, task_type
  │  • timestamps (created, started, completed)
  │  • phase (current + history)
  │  • commits (all commits with SHA, message, time)
  │  • files_modified (all touched files)
  │  • tests (results, coverage)
  │  • quality_gates (lint, type check, security)
  │  • agents_used (which agents worked on this)
  │  • dependencies (blocked_by, blocks)
  │
  ├─→ WRITTEN by:
  │     • task_create.py (initial)
  │     • task_update_phase.py (phase transitions)
  │     • post_tool_use.py hook (commits, files)
  │     • task_update_tests.py (test results)
  │     • task_update_quality.py (quality gates)
  │     • subagent_stop.py hook (agents_used)
  │
  └─→ READ by:
        • session_start.py hook (display status)
        • All /task-* commands (load context)
        • Agents (task context)
        • task_complete.py (generate retrospective)


Research Artifacts (TASK-001/research/*.md)
  │
  │  Created by: (Explore agent)
  │  Contains:
  │  • Existing auth patterns found
  │  • Similar implementations (US-042, etc.)
  │  • Dependencies identified (Clerk, Redis)
  │  • Code analysis notes
  │
  └─→ READ by:
        • (Plan agent) - for architecture decisions
        • (Implementation agents) - for patterns to follow
        • /task-plan command - to inform planning


Planning Artifacts (TASK-001/planning/*.md)
  │
  │  Created by: (Plan agent)
  │  Contains:
  │  • Architecture design
  │  • Agent assignments (dev-backend, dev-frontend)
  │  • Implementation steps
  │  • Complexity estimate
  │
  └─→ READ by:
        • /task-implement command - to know which agent to spawn
        • (Implementation agents) - to follow plan
        • task_complete.py - for retrospective comparison


Context Handoff Files (TASK-001/context/*.md)
  │
  │  Created by: Main LLM between agent transitions
  │  Example: backend-done.md
  │  Contains:
  │  • What backend agent accomplished
  │  • API endpoints created
  │  • Data models defined
  │  • Integration points for frontend
  │
  └─→ READ by:
        • (dev-frontend agent) - knows what backend provides
        • Creates seamless integration


Git Commits (Repository)
  │
  │  Created by: All implementation agents
  │  Format: feat(TASK-001/US-001): Implement login API
  │  Metadata: SHA, author, timestamp, files changed
  │
  ├─→ TRACKED by:
  │     • Git post-commit hook → commit-task-map.csv
  │     • PostToolUse hook → STATE.json commits[]
  │
  └─→ ANALYZED by:
        • git_stats.py - for retrospective
        • git_research_patterns.py - for future research


Complete Data Flow Example:
═══════════════════════════════════════════════════════════════════════

1. Story created
     ↓
   US-001.md
     ↓
2. Task created, reads story
     ↓
   STATE.json (story_id: US-001)
     ↓
3. Research agent runs, saves findings
     ↓
   TASK-001/research/patterns.md
     ↓
4. Plan agent reads research, creates plan
     ↓
   TASK-001/planning/architecture.md
     ↓
5. Backend agent reads story + research + plan
     ↓
   Implements code, makes commits
     ↓
   Git commits + STATE.json updated
     ↓
   Saves summary
     ↓
   TASK-001/context/backend-done.md
     ↓
6. Frontend agent reads story + research + plan + backend summary
     ↓
   Implements UI, makes commits
     ↓
   Git commits + STATE.json updated
     ↓
7. Tests run, results saved
     ↓
   STATE.json.tests section
     ↓
8. Validation runs, quality gates updated
     ↓
   STATE.json.quality_gates section
     ↓
9. Task completes, retrospective generated
     ↓
   TASK-001/retrospective.md (reads all above)
     ↓
10. Task archived
     ↓
    archive/TASK-001/ (complete history preserved)
```

---

## Diagram 5: Conditional Behaviors

### Decision Points in the Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CONDITIONAL: /task-implement <domain>                                   │
└─────────────────────────────────────────────────────────────────────────┘

User runs: /task-implement ?
  │
  ├─→ IF: backend
  │     └─→ Spawn (dev-backend agent) only
  │           └─→ Work in apps/server/
  │
  ├─→ IF: frontend
  │     └─→ Spawn (dev-frontend agent) only
  │           └─→ Work in apps/frontend/
  │
  └─→ IF: fullstack
        │
        ├─→ STEP 1: Spawn (dev-backend agent)
        │     ├─→ Implement backend
        │     └─→ Save context/backend-done.md
        │
        ├─→ WAIT for backend completion
        │     └─→ {SubagentStop hook validates}
        │
        └─→ STEP 2: Spawn (dev-frontend agent)
              ├─→ Load: story + research + plan + backend context
              ├─→ Implement frontend knowing backend details
              └─→ Return results


┌─────────────────────────────────────────────────────────────────────────┐
│ CONDITIONAL: PreToolUse Hook (Agent Enforcement)                        │
└─────────────────────────────────────────────────────────────────────────┘

Edit/Write tool called for file: <file_path>
  │
  ├─→ IF: file in apps/server/**
  │     │
  │     ├─→ IF: current agent is dev-backend
  │     │     └─→ ✓ ALLOW
  │     │
  │     └─→ IF: current agent is not dev-backend
  │           └─→ ✗ BLOCK
  │                 └─→ Error: "Must use dev-backend agent for apps/server/"
  │
  ├─→ IF: file in apps/frontend/**
  │     │
  │     ├─→ IF: current agent is dev-frontend
  │     │     └─→ ✓ ALLOW
  │     │
  │     └─→ IF: current agent is not dev-frontend
  │           └─→ ✗ BLOCK
  │                 └─→ Error: "Must use dev-frontend agent for apps/frontend/"
  │
  ├─→ IF: file in docker/, Makefile, *.yml
  │     │
  │     ├─→ IF: current agent is devops-infra
  │     │     └─→ ✓ ALLOW
  │     │
  │     └─→ IF: current agent is not devops-infra
  │           └─→ ✗ BLOCK
  │                 └─→ Error: "Must use devops-infra agent for infrastructure/"
  │
  └─→ IF: file not in protected scope
        └─→ ✓ ALLOW (unrestricted)


┌─────────────────────────────────────────────────────────────────────────┐
│ CONDITIONAL: /task-test (Test Creation vs Execution)                    │
└─────────────────────────────────────────────────────────────────────────┘

User runs: /task-test
  │
  ├─→ Check: Do backend tests exist?
  │     │
  │     ├─→ IF: No backend tests
  │     │     └─→ Spawn (dev-backend agent)
  │     │           └─→ Create test files first
  │     │
  │     └─→ IF: Backend tests exist
  │           └─→ Skip to execution
  │
  ├─→ Check: Do frontend tests exist?
  │     │
  │     ├─→ IF: No frontend tests
  │     │     └─→ Spawn (dev-frontend agent)
  │     │           └─→ Create test files first
  │     │
  │     └─→ IF: Frontend tests exist
  │           └─→ Skip to execution
  │
  └─→ Execute all tests
        ├─→ pytest (backend)
        └─→ vitest (frontend)


┌─────────────────────────────────────────────────────────────────────────┐
│ CONDITIONAL: SessionStart Hook (Task Context Loading)                   │
└─────────────────────────────────────────────────────────────────────────┘

Session starts
  │
  └─→ {SessionStart hook}
        │
        ├─→ Read: .claude/tasks/current.txt
        │
        ├─→ IF: current.txt not found OR content is "none"
        │     └─→ Display: "No active task. Use /task-new or /task-resume"
        │           └─→ EXIT
        │
        ├─→ IF: current.txt contains TASK-XXX
        │     │
        │     ├─→ Read: TASK-XXX/STATE.json
        │     │
        │     ├─→ Display:
        │     │     • Task ID, Story ID
        │     │     • Current phase
        │     │     • Status
        │     │
        │     └─→ Suggest next command based on phase:
        │           │
        │           ├─→ IF: phase = PLANNING
        │           │     └─→ "Suggested: /task-research or /task-plan"
        │           │
        │           ├─→ IF: phase = RESEARCH
        │           │     └─→ "Suggested: /task-plan"
        │           │
        │           ├─→ IF: phase = IMPLEMENTATION
        │           │     └─→ "Suggested: /task-implement <domain>"
        │           │
        │           ├─→ IF: phase = TESTING
        │           │     └─→ "Suggested: /task-test"
        │           │
        │           ├─→ IF: phase = VALIDATION
        │           │     └─→ "Suggested: /task-validate"
        │           │
        │           └─→ IF: phase = REVIEW
        │                 └─→ "Suggested: Fix issues, then /task-complete"
        │
        └─→ EXIT


┌─────────────────────────────────────────────────────────────────────────┐
│ CONDITIONAL: SubagentStop Hook (Validation by Agent Type)               │
└─────────────────────────────────────────────────────────────────────────┘

Subagent completes
  │
  └─→ {SubagentStop hook}
        │
        ├─→ IF: agent = dev-backend OR dev-frontend
        │     │
        │     ├─→ Validate:
        │     │     • ✓ Commits made?
        │     │     • ✓ Files in correct domain modified?
        │     │     • ✓ Test files created?
        │     │
        │     ├─→ IF: All pass
        │     │     └─→ ✅ Update STATE.json agents_used
        │     │
        │     └─→ IF: Any fail
        │           └─→ ⚠️  Warn: "Incomplete work: <details>"
        │
        ├─→ IF: agent = Explore
        │     │
        │     ├─→ Validate:
        │     │     • ✓ Research files saved?
        │     │
        │     ├─→ IF: Pass
        │     │     └─→ ✅ Update STATE.json
        │     │
        │     └─→ IF: Fail
        │           └─→ ⚠️  Warn: "No research findings saved"
        │
        └─→ IF: agent = Plan
              │
              ├─→ Validate:
              │     • ✓ Planning files saved?
              │     • ✓ Agent assignments specified?
              │
              ├─→ IF: Pass
              │     └─→ ✅ Update STATE.json
              │
              └─→ IF: Fail
                    └─→ ⚠️  Warn: "Incomplete plan"
```

---

## Summary

### Workflow Characteristics

**Automation Level:**

- 8 hooks (3 git + 5 Claude CLI) provide continuous validation
- 31+ Python scripts handle all automation
- 18 commands orchestrate the workflow
- Minimal manual intervention required

**Validation Checkpoints:**

- SessionStart: Load task context
- UserPromptSubmit: Validate prerequisites
- PreToolUse: Enforce agent boundaries
- PostToolUse: Track all changes
- SubagentStop: Validate completeness
- Git hooks: Ensure commit consistency

**Context Flow:**

- Story → Task → Research → Planning → Implementation → Testing → Validation → Completion
- Each phase enriches context for next phase
- Backend results flow to frontend seamlessly
- Complete audit trail maintained in STATE.json

**Agent Coordination:**

- Main LLM orchestrates, never implements
- Specialized agents (dev-backend, dev-frontend, devops-infra) do all code work
- PreToolUse hook enforces boundaries (hard enforcement, not suggestions)
- Context passes between agents via TASK-XXX/context/ files

**Conditional Intelligence:**

- Hooks suggest next steps based on phase
- Commands spawn appropriate agents based on domain
- Agents create tests if missing, or skip if present
- Validation adapts to agent type

---

**End of Workflow Diagrams**
