# SDLC Workflow - Mandatory Governance

**Purpose:** Define mandatory rules for story-driven development workflow
**Scope:** All development work on this project
**Status:** Active

---

## Core Principle: Story vs Task

### Story (WHAT)
- **Permanent documentation** in `.sdlc-workflow/stories/`
- User perspective: requirements, acceptance criteria
- Never deleted, always preserved
- Format: `US-XXX-domain-feature-scope.md`

### Task (HOW)
- **Temporary work session** in `.claude/tasks/`
- Developer perspective: implementation work
- Archived after completion
- Format: `TASK-XXX` with STATE.json tracking

**Golden Rule:** Every code change must trace back to a Story via a Task.

---

## Workflow Phases (Required)

All tasks must progress through these phases:

1. **PLANNING** - Initial setup, no code yet
2. **RESEARCH** - Explore agent finds patterns and dependencies
3. **PLANNING** - Plan agent designs architecture
4. **IMPLEMENTATION** - Specialized agents write code
5. **TESTING** - Verify behavior and coverage
6. **VALIDATION** - Quality gates (lint, type, security, acceptance)
7. **COMPLETED** - Archived with retrospective

**Skip phases only with explicit justification documented in task.**

---

## Agent Enforcement

### Main LLM (You) Role: COORDINATOR ONLY

You orchestrate work but **NEVER modify implementation files** directly:

- ✅ Read files (research, analysis)
- ✅ Plan and design
- ✅ Launch subagents for implementation
- ✅ Update workflow docs (.sdlc-workflow/, .claude/, CLAUDE.md)
- ✅ Git operations
- ❌ Edit apps/server/ (use dev-backend agent)
- ❌ Edit apps/frontend/ (use dev-frontend agent)
- ❌ Edit tests/ (use appropriate agent)

**Enforcement:** PreToolUse hook blocks violations automatically.

### Specialized Agents (Implementers)

- **dev-backend** - All apps/server/ code
- **dev-frontend** - All apps/frontend/ code
- **playwright-e2e-tester** - All tests/ code
- **devops-infra** - All docker/, Makefile, CI/CD

**Each agent has mandatory skills** - see agent definitions in `.claude/agents/`.

---

## When to Use Workflow

### Required (Must Use Workflow)
- All new features
- All bug fixes
- All refactoring work
- All test additions

### Optional (Can Skip Workflow)
- Documentation-only changes (README, comments)
- Configuration tweaks (.env.example, .gitignore)
- CLAUDE.md updates
- Workflow documents themselves

---

## State Management

All task state lives in `.claude/tasks/TASK-XXX/STATE.json`:

- Phase progress and duration
- Commits made (auto-tracked)
- Files modified (auto-tracked)
- Tests and coverage (auto-tracked)
- Quality gates status
- Agent usage

**Never manually edit STATE.json** - use scripts in `.claude/skills/docs-stories/scripts/`.

---

## Commit Format (Mandatory)

All commits must follow conventional commits:

```
type(scope): message [TASK-xxx/US-xxx]
```

**Enforcement:** Three-layer (git hook, Claude hook, CI pipeline).

---

## Progressive Disclosure

More detail available when needed:

1. **This file** (< 1k words) - Loaded every session (mandatory)
2. **docs-stories skill** (< 5k words) - Invoke for detailed guidance
3. **Reference docs** - Deep-dive on specific topics

**Use `/help sdlc` to see available commands.**

---

## Consequences of Non-Compliance

- PreToolUse hook blocks inappropriate edits
- CI pipeline blocks PRs with invalid commits
- STATE.json validation catches missing tracking
- No emergency bypass exists (by design)

**Friction is a feature** - ensures contextual integrity.

---

## Quick Commands Reference

```bash
/story-new          # Create user story
/task-new US-XXX    # Create task for story
/task-research      # Research phase (Explore agent)
/task-plan          # Planning phase (Plan agent)
/task-implement     # Implementation (specialized agents)
/task-test          # Run tests
/task-validate      # Quality gates
/task-complete      # Archive task
```

See `.claude/skills/docs-stories/` for complete documentation.

---

**This rule is mandatory and loaded every session. For detailed information, invoke the `docs-stories` skill.**
