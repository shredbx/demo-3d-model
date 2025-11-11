# Task Folders - Implementation Work Tracking

## Purpose

Task folders contain **all artifacts from implementation work** for traceability and context preservation.

**Key Principle:** "Task folder is for any artifact to be saved during the work, so we always can look inside anytime later to see why we made those decisions and what else we discussed so we don't loop our solutions."

---

## Structure

```
.sdlc-workflow/tasks/
├── README.md (this file)
├── TEMPLATE/ (copy for new tasks)
└── US-XXX-TASK-YYY-short-description/ (actual tasks)
```

---

## Story vs Task

| Aspect | User Story | Task |
|--------|-----------|------|
| **Location** | `.sdlc-workflow/stories/` | `.sdlc-workflow/tasks/` |
| **Purpose** | WHAT (requirements) | HOW (implementation) |
| **Perspective** | User/product | Developer/technical |
| **Lifecycle** | Permanent | Preserved but not actively maintained after merge |
| **Contains** | Acceptance criteria, business value | Artifacts, decisions, subagent reports |

---

## When to Create Task Folder

Create a task folder when:
- Breaking down user story into implementation tasks
- Starting any implementation work
- Work requires subagent coordination
- Decisions need to be documented

**Format:** `US-XXX-TASK-YYY-short-description`

Examples:
- `US-001-TASK-001-add-file-headers`
- `US-001-TASK-002-create-e2e-tests`
- `US-016-TASK-001-migrate-schema`

---

## Task Folder Contents

### Required Files

1. **README.md** - Task description
   - What needs to be done
   - Which files to modify
   - Which subagent to use
   - Acceptance criteria

2. **progress.md** - Status tracking
   - Current status (NOT_STARTED → IN_PROGRESS → COMPLETED → MERGED)
   - Timeline of work
   - Blockers encountered
   - Resolution notes

### Optional Files (create as needed)

3. **decisions.md** - Architectural/design decisions
   - Why we chose approach X over Y
   - Trade-offs considered
   - Alternative approaches rejected
   - Rationale

4. **discussions.md** - Important conversations
   - User clarifications
   - Technical discussions
   - Questions and answers
   - Context that influenced decisions

5. **subagent-reports/** - Subagent outputs
   - Save report from each subagent invocation
   - Name by subagent: `backend-report.md`, `frontend-report.md`
   - Include timestamp if multiple runs

6. **evidence/** - Supporting artifacts
   - Screenshots (before/after)
   - Log files
   - Test results
   - Performance benchmarks

---

## Workflow

### 1. Create Task Folder

```bash
# Copy template
cp -r .sdlc-workflow/tasks/TEMPLATE .sdlc-workflow/tasks/US-001-TASK-001-add-file-headers

# Edit README.md with task details
```

### 2. Launch Subagent

Coordinator (main Claude) launches appropriate subagent:

```python
Task(
    subagent_type="dev-backend-fastapi",
    prompt="Add file headers to these files: ... Follow pattern in clerk_deps.py",
    description="Add backend file headers"
)
```

### 3. Save Subagent Report

```bash
# Save subagent output
echo "..." > .sdlc-workflow/tasks/US-001-TASK-001/subagent-reports/backend-report.md
```

### 4. Update Progress

```bash
# Update progress.md
# Change status to COMPLETED
# Add completion timestamp
# Note any issues
```

### 5. Document Decisions

If decisions were made during implementation:

```bash
# Update decisions.md
# Explain why approach X was chosen
# Document alternatives considered
```

### 6. Commit with Task Reference

```bash
git commit -m "feat: add file headers (US-001 TASK-001)

Subagent: dev-backend-fastapi
Files: server/api/deps.py, server/models/user.py

Story: US-001
Task: TASK-001"
```

---

## For Subagents: Integration Guide

**When coordinator spawns you (dev-backend-fastapi, dev-frontend-svelte, etc.), you must integrate with the SDLC system.**

### What Coordinator Provides

- Task folder path (`.claude/tasks/TASK-XXX/`)
- Implementation spec (`planning/implementation-spec.md` or similar)
- Story acceptance criteria
- Task STATE.json with context

### Your Responsibilities

**1. Read Context:**
- Read task STATE.json to understand story, task semantic name, current phase
- Read implementation spec for detailed instructions
- Read user story acceptance criteria

**2. Do Implementation:**
- Modify implementation files (your core job)
- Follow patterns from dev-philosophy and dev-code-quality skills
- Apply framework-specific best practices

**3. Document Your Work:**
- Create report in `subagent-reports/{your-name}-report.md`
- Document: what you did, files modified, decisions made, trade-offs, testing notes
- Be thorough - your report is part of Memory Print Chain

**4. DON'T Touch:**
- ❌ DON'T update task STATE.json (coordinator does this via docs-stories)
- ❌ DON'T create/modify story files (coordinator's job)
- ❌ DON'T manually update task phase (coordinator's job)

### Integration Pattern

```
Coordinator spawns you with:
  "Implement login form per spec in .claude/tasks/TASK-001/planning/implementation-spec.md"
  "Save report to .claude/tasks/TASK-001/subagent-reports/dev-frontend-svelte-report.md"

You do:
  1. Read .claude/tasks/TASK-001/STATE.json (understand context)
  2. Read .claude/tasks/TASK-001/planning/implementation-spec.md (requirements)
  3. Implement solution (modify apps/frontend/src/...)
  4. Save report (document what you did, trade-offs, testing notes)
  5. Return report path to coordinator

Coordinator does:
  1. Saves your report (already done by you)
  2. Updates STATE.json via docs-stories scripts
  3. Commits with proper references (US-XXX TASK-YYY-semantic-name)
  4. Updates task phase if needed
```

### Why This Division

- **Coordinator orchestrates workflow** (docs-stories + orchestrator)
- **Subagents focus on implementation** (their expertise)
- **Clear separation prevents conflicts**
- **All SDLC operations go through docs-stories** (consistency)

---

## Benefits

### Context Preservation
- All implementation details saved forever
- Decisions documented with rationale
- Can review months/years later

### No Repeated Discussions
- Check `decisions.md` before proposing "improvements"
- Avoid circular problem-solving
- Understand historical context

### Audit Trail
- Complete record of who did what
- Subagent outputs preserved
- Evidence for compliance/reviews

### Knowledge Transfer
- New developers read task folders
- Understand "why" not just "what"
- Faster onboarding

### Resumability
- Anyone can continue work
- Check progress.md for status
- Read README.md for context

---

## Maintenance

### Active Tasks
- Update progress.md regularly
- Save subagent reports immediately
- Document decisions as they're made

### Completed Tasks
- Mark progress as COMPLETED
- Add completion date
- No further updates needed (preserved as-is)

### After Merge
- Task folder stays forever (historical record)
- Not actively maintained
- Referenced when needed

---

## Example Task Folder

```
US-001-TASK-001-add-file-headers/
├── README.md
│   Task: Add architecture documentation headers to 5 files
│   Files: deps.py, user.py, user_service.py, clerk.ts, ErrorBoundary.svelte
│   Subagents: dev-backend-fastapi, dev-frontend-svelte
│
├── progress.md
│   2025-11-06 10:00 - Task created (NOT_STARTED)
│   2025-11-06 10:15 - Backend work started (IN_PROGRESS)
│   2025-11-06 10:45 - Backend completed
│   2025-11-06 11:00 - Frontend work started
│   2025-11-06 11:30 - Frontend completed
│   2025-11-06 11:35 - Task completed (COMPLETED)
│   2025-11-06 14:20 - Merged to main (MERGED)
│
├── decisions.md
│   Decision: Follow pattern from clerk_deps.py (comprehensive headers)
│   Rationale: Provides architecture context, dependencies, testing notes
│   Rejected: Minimal headers (insufficient documentation)
│
├── subagent-reports/
│   ├── backend-report-2025-11-06-1015.md
│   └── frontend-report-2025-11-06-1100.md
│
└── evidence/
    └── before-after-screenshots/
        ├── deps-before.png
        └── deps-after.png
```

---

## Template Usage

Copy the TEMPLATE folder for each new task:

```bash
cp -r .sdlc-workflow/tasks/TEMPLATE .sdlc-workflow/tasks/US-XXX-TASK-YYY-description
cd .sdlc-workflow/tasks/US-XXX-TASK-YYY-description
# Edit README.md with task details
# Update progress.md to NOT_STARTED
```

---

## Notes

- Task folders are created BY COORDINATOR (main Claude)
- Implementation is done BY SUBAGENTS (not coordinator)
- Subagent reports saved BY COORDINATOR after work completes
- Progress updated BY COORDINATOR throughout lifecycle
- All artifacts preserved forever (never deleted)
