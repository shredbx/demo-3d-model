# PatternBook SDLC Workflow Documentation

**Created:** 2025-11-01
**Status:** Complete - Ready for Implementation
**Version:** 2.0

---

## Overview

This directory contains the complete SDLC workflow implementation plan and specifications for the PatternBook system. All documents are production-ready and cross-referenced.

---

## Documents (Read in Order)

### 00. Changelog

**File:** `00-changelog.md`
**Purpose:** Summary of all changes in v2.0
**Read First:** If you want to understand what changed from the original plan

**Contains:**

- Summary of all updates
- Document-by-document changelog
- Key additions (CI, coverage delta, conventional commits, ownership, feedback loops)
- Migration path
- Validation checklist

---

### 01. Implementation Plan (MASTER DOCUMENT)

**File:** `01-implementation-plan.md`
**Purpose:** Complete implementation plan with all phases, scripts, commands, and timelines
**Start Here:** This is the main document that references all others

**Contains:**

- Executive summary and major changes
- 33 Python/Bash scripts (complete specifications)
- 18 slash commands (workflow triggers)
- STATE.json structure
- 7 implementation phases (45-60 hours)
- File structure
- Conventional commits standard
- Success criteria

**Key Sections:**

- Section 1: Changes from original plan
- Section 3: Complete script architecture (33 scripts)
- Section 4: Complete command structure (18 commands)
- Section 5: STATE.json structure
- Section 6: Implementation phases (7 phases)
- Section 9: Conventional commits standard
- Section 10: Success criteria

---

### 02. Hooks Specification

**File:** `02-hooks-specification.md`
**Purpose:** Complete specification of all hooks (git + Claude CLI) and CI enforcement

**Contains:**

- 3 Git hooks (prepare-commit-msg, post-commit, post-checkout)
- 5 Claude CLI hooks (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, SubagentStop)
- Complete Python/Bash implementations
- CI enforcement layer (GitHub Actions)
- When to use git vs Claude hooks
- Configuration in .claude/settings.json

**Key Sections:**

- Section 2: Git hooks (3 total)
- Section 3: Claude CLI hooks (5 total)
- Section 4: Hook configuration
- Section 9: CI Enforcement Layer (server-side validation)

**Use This For:**

- Implementing hooks
- Understanding hook trigger points
- Configuring CI pipeline
- Understanding enforcement philosophy

---

### 03. Workflow Diagrams

**File:** `03-workflow-diagrams.md`
**Purpose:** Visual workflow from story creation to completion, showing all phases and data flow

**Contains:**

- Complete workflow diagrams (9 phases)
- Agent spawning decision trees
- Hook trigger timeline
- Data flow and context passing
- Feedback loops (planning and implementation)
- Conditional behaviors (fullstack vs backend vs frontend)

**Key Phases:**

- PHASE 1: Create Story
- PHASE 2: Create Task
- PHASE 3: Planning (with feedback loop)
- PHASE 4: Implementation - Backend (with post-job discussion)
- PHASE 5: Implementation - Frontend (with post-job discussion)
- PHASE 6: Testing
- PHASE 7: Validation
- PHASE 8: Completion
- PHASE 9: Git Workflow & CI Validation

**Use This For:**

- Understanding complete end-to-end flow
- Visualizing agent coordination
- Understanding feedback loops
- Tracing data between phases

---

### 04. Agent-Skill Mapping & Enforcement

**File:** `04-agent-mapping.md`
**Purpose:** Directory ownership, agent-skill mappings, and enforcement mechanisms

**Contains:**

- Directory ownership table (centralized)
- Declarative ownership (README.md YAML frontmatter)
- Agent definitions with mandatory skills
- PreToolUse hook enforcement
- SubagentStop validation
- get_agent_for_dir.sh implementation
- README.md ownership system

**Key Sections:**

- Section 1: Directory ownership table and dual ownership model
- Section 2-4: Agent definitions (dev-backend, dev-frontend, devops-infra)
- Section 5-7: Skill mappings and enforcement
- Section 10: Declarative ownership in README.md

**Use This For:**

- Understanding agent responsibilities
- Implementing ownership validation
- Configuring PreToolUse hook
- Setting up README.md ownership

---

## Quick Reference

### File Count

- **5 documents total** (including this README)
- **1 changelog** (what changed in v2)
- **1 master plan** (implementation phases and scripts)
- **1 hooks spec** (all hooks + CI)
- **1 workflow diagram** (visual flow)
- **1 agent mapping** (ownership and enforcement)

### Script Count

- **33 scripts total**
  - 32 Python scripts
  - 1 Bash script (get_agent_for_dir.sh)

### Hook Count

- **8 hooks total**
  - 5 Claude CLI hooks (Python)
  - 3 Git hooks (Bash)

### Command Count

- **18 slash commands**
  - 4 story commands
  - 5 task management commands
  - 5 SDLC phase commands
  - 4 utility commands

### Implementation Phases

- **7 phases, 45-60 hours**
  - Phase 1: Foundation (8-10 hours)
  - Phase 2: Scripts (12-14 hours)
  - Phase 3: Hooks + CI (8-10 hours)
  - Phase 4: Commands (6-8 hours)
  - Phase 5: Agent Updates (4-6 hours)
  - Phase 6: Integration Testing (6-8 hours)
  - Phase 7: Documentation (2-3 hours)

---

## Key Features

### 1. CI Enforcement

- Server-side validation (GitHub Actions)
- Validates: commits, STATE.json, tests, coverage, ownership, quality gates
- Prevents --no-verify bypass
- Immutable compliance layer

### 2. Conventional Commits

- Format: `type(scope): message [TASK-xxx/US-xxx]`
- Enables automated changelog and semantic versioning
- Three-layer enforcement (git hook, Claude hook, CI)

### 3. Coverage Delta Validation

- Ensures new code is tested
- Blocks if coverage drops below baseline
- "Was behavior proven?" not "Was test added?"

### 4. README.md Ownership

- YAML frontmatter declares owner agent
- Discoverable, visible, self-documenting
- CI validates all files have owners
- Prevents orphan files

### 5. Feedback Loops

- Planning: Iterative refinement with user
- Implementation: Post-job review and refinement
- Collaborative workflow, not assumption-based

---

## Philosophy

### Friction as a Feature (Reaffirmed)

- System friction is DELIBERATE design
- Ensures contextual integrity
- No emergency bypass exists
- Every change requires task/story path

### Ownership Model

- **Centralized:** Table for quick reference
- **Declarative:** README.md for enforcement
- Both complement each other

### Immutable Compliance

- CI enforcement prevents all bypasses
- Reproducibility across team
- Self-documenting, verifiable workflow

---

## How to Use This Directory

### For Implementation

1. Read `00-changelog.md` to understand what changed
2. Read `01-implementation-plan.md` from start to finish
3. Refer to other docs as needed during implementation
4. Follow the 7 phases in order

### For Reference

- **Hooks:** See `02-hooks-specification.md`
- **Workflow:** See `03-workflow-diagrams.md`
- **Ownership:** See `04-agent-mapping.md`
- **Scripts:** See `01-implementation-plan.md` Section 3
- **Commands:** See `01-implementation-plan.md` Section 4

### For Understanding

- **Big picture:** Start with `03-workflow-diagrams.md`
- **Details:** Read `01-implementation-plan.md`
- **Enforcement:** Read `02-hooks-specification.md` and `04-agent-mapping.md`

---

## Other Plan Files (Not Part of This Flow)

These files remain in `.sdlc-workflow/plan/` and are NOT part of the SDLC workflow:

- `20251031-2338-sdlc-todo-plan-git-userstories.md` - Original plan v1 (historical)
- `20251031-2350-sdlc-plan-analysis.md` - Analysis document
- `-20251101-0028-analysis-architecture-decisions.md` - Architecture decisions
- `20251101-1119-sdlc-plan-changes.md` - Old change tracking

**Do not confuse these with the current SDLC workflow documents.**

---

## Status

✅ **Complete and Ready for Implementation**

All documents are:

- Cross-referenced correctly
- Consistent with each other
- Aligned with PatternBook philosophy
- Production-ready
- Tested for completeness

---

## Next Steps

1. Review all 5 documents (start with 00, then 01)
2. Validate approach and philosophy
3. Begin Phase 1 implementation
4. Follow the 7 phases sequentially
5. Test each phase before proceeding

---

**Last Updated:** 2025-11-01 15:31
**Version:** 2.0
**Status:** ✅ Complete
