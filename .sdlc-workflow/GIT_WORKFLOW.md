# Git Workflow - SDLC Integration

## Overview

Our git workflow integrates tightly with user stories and tasks to maintain full traceability.

---

## Branch Strategy

**Task-Based Feature Branch Workflow:**

```
main (production-ready)
  ├─ {type}/TASK-XXX[-semantic-name]-US-XXX (task branches)
  └─ main (always deployable)
```

**Branch Naming Convention:**

Pattern: `{type}/TASK-{number}[-semantic-name]-US-{story}`

**Valid Types:**
- `feat` - New features
- `fix` - Bug fixes
- `refactor` - Code improvements (no behavior change)
- `test` - Test additions/updates
- `docs` - Documentation only
- `chore` - Build/tooling changes

**Examples:**
- ✅ `feat/TASK-001-US-001` (backward compatible, no semantic name)
- ✅ `feat/TASK-001-clerk-mounting-US-001` (with semantic name - RECOMMENDED)
- ✅ `fix/TASK-042-login-tests-US-001B` (semantic name with story variant)
- ✅ `refactor/TASK-005-cleanup-US-001B`
- ✅ `test/TASK-010-e2e-tests-US-002`
- ✅ `main` (special case - always valid)
- ❌ `feature/US-001-description` (old pattern - not valid)
- ❌ `feat/some-branch` (missing task/story IDs)
- ❌ `feat/TASK-001-US-001-description` (description at end - old pattern)

**Semantic name (optional but RECOMMENDED):**
- 2-3 words describing task purpose (e.g., `clerk-mounting`, `login-tests`)
- Lowercase, hyphens only, alphanumeric
- Makes git history self-documenting

---

## Why Task-Based Branching?

We use **one branch per task** (not per story) for several key reasons:

1. **Parallel Work** - Multiple tasks within same story can work simultaneously
   - Example: `feat/TASK-001-US-002` (backend) + `feat/TASK-002-US-002` (frontend)

2. **Clear Ownership** - Each branch has focused, discrete changes
   - Easier code review (small, logical chunks)
   - Clear what changed and why

3. **Better Traceability** - Git history shows which task made which changes
   - Can trace any code back to specific task
   - Task folders provide full decision context

4. **Automation-Friendly** - Scripts can parse task/story IDs from branch name
   - Validation scripts enforce consistency
   - CI/CD pipelines can route based on branch type

5. **Clear Completion** - Branch deleted when task completes (not when story completes)
   - Short-lived branches (hours to days, not weeks)
   - Reduces merge conflicts
   - Keeps git history clean

**Why not story-based?**
- Stories can have 5-10 tasks spanning multiple domains
- Long-lived story branches accumulate many commits
- Hard to review/merge large changesets
- Difficult to work in parallel on different aspects

---

## Branch Validation

**Enforcement:** Branch names are automatically validated before creation/checkout.

### Validation Script

**Location:** `.sdlc-workflow/scripts/validate_branch.py`

**Usage:**
```bash
# Validate current branch
.sdlc-workflow/scripts/validate_branch.py

# Validate specific branch name
.sdlc-workflow/scripts/validate_branch.py feat/TASK-001-US-002
```

**Exit Codes:**
- `0` - Branch name is valid
- `1` - Branch name is invalid (with error message)
- `2` - Error (git not available, script error)

**Pattern Validation:**
- Regex: `^(feat|fix|refactor|test|docs|chore)/TASK-\d+(-[a-z0-9-]+)?-US-\d+[A-Z]?$`
- Checks type prefix, task ID, optional semantic name, story ID
- Semantic name: lowercase, alphanumeric, hyphens only
- Provides helpful error messages for common mistakes

### Integration with Hooks

**Pre-Tool-Use Hook:** `.claude/hooks/sdlc_guardian.py`

The SDLC guardian hook validates branch names before git operations:
- Automatically called before git checkout
- Blocks invalid branch names with actionable error messages
- Suggests correct pattern when validation fails

**Example Error:**
```
❌ Branch 'feature/US-001-description' uses old story-based naming.

Expected pattern: {type}/TASK-{number}[-semantic-name]-US-{story}

Valid examples:
  feat/TASK-001-US-001
  feat/TASK-001-clerk-mounting-US-001
  fix/TASK-042-login-tests-US-001B
  refactor/TASK-005-cleanup-US-001B

Semantic name: optional, 2-3 words, lowercase, hyphens only

Rationale: We use task-based branching (one branch per task, not per story)
to enable parallel work and better git history traceability.
```

**How It Works:**
1. You attempt to create/checkout a branch
2. Hook intercepts the git operation
3. Calls `validate_branch.py` to check name
4. If invalid → blocks operation + shows error
5. If valid → allows operation to proceed

**See:** `.claude/hooks/README.md` for hook system documentation

---

## Workflow Steps

### 1. Start Work on Task

**One branch per task** (not per story):

```bash
# Create task branch from main
git checkout main
git pull origin main
git checkout -b feat/TASK-001-clerk-mounting-US-001

# Branch name validates automatically via hook
# If invalid, you'll get error with correct pattern
```

**Pattern:** `{type}/TASK-{number}[-semantic-name]-US-{story}`

**Semantic name RECOMMENDED:**
- Makes git history self-documenting
- Shows task purpose without looking up task folder
- 2-3 words, lowercase, hyphens only (e.g., `clerk-mounting`, `login-tests`)

**Common types:**
- `feat/` for new features
- `fix/` for bug fixes
- `refactor/` for code improvements
- `test/` for test additions
- `docs/` for documentation

### 2. Break Down into Tasks

For each task in the user story:

```bash
# Create task folder (with semantic name)
cp -r .sdlc-workflow/tasks/TEMPLATE .sdlc-workflow/tasks/US-001-TASK-001-file-headers

# Edit task README.md with details
# Update progress.md to NOT_STARTED
```

**Task folder naming:** Match the semantic name from your branch
- Branch: `feat/TASK-001-clerk-mounting-US-001`
- Folder: `US-001-TASK-001-clerk-mounting`

### 3. Implement via Subagent

**COORDINATOR (main Claude):**
1. Launches appropriate subagent
2. Saves subagent report to task folder
3. Updates task progress.md
4. Documents any decisions

**SUBAGENT:**
- Modifies implementation files
- Returns report to coordinator

### 4. Commit with Task Reference

```bash
# Stage changes
git add <files-modified-by-subagent>

# Commit with proper format (include semantic task name)
git commit -m "type: description (US-XXX TASK-YYY-semantic-name)

Subagent: <subagent-name>
Files: <list>

<detailed description>

Story: US-XXX
Task: TASK-YYY-semantic-name"
```

### 5. Validation (Optional)

```bash
# Run SDLC validation script
.sdlc-workflow/scripts/validate_sdlc.py

# Checks:
# - Implementation files have task reference
# - Implementation commits have subagent marker
# - Coordinator only modifies allowed paths
```

### 6. Continue Until Story Complete

Repeat steps 2-5 for all tasks in the user story.

### 7. Merge to Main

```bash
# Ensure all tests pass
make test

# Update story status to COMPLETED
# Update CLAUDE.md SDLC progress

# Merge to main
git checkout main
git merge --no-ff feature/US-001-login-flow-validation
git push origin main

# Optional: Delete feature branch
git branch -d feature/US-001-login-flow-validation
```

---

## Commit Message Format

### Structure

```
type: description (US-XXX TASK-YYY-semantic-name)

Subagent: <subagent-name>
Files: <comma-separated list>

<Detailed description of changes>
<Why this change was needed>
<Any important notes>

Story: US-XXX
Task: TASK-YYY-semantic-name
```

### Type Prefixes

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `test:` Adding/updating tests
- `refactor:` Code restructuring (no behavior change)
- `perf:` Performance improvement
- `chore:` Build/tooling changes

### Example: Implementation Commit

```bash
git commit -m "feat: add file headers to backend dependencies (US-001 TASK-001-file-headers)

Subagent: dev-backend-fastapi
Files: server/api/deps.py, server/models/user.py, server/services/user_service.py

Added architecture documentation headers following the pattern established
in server/core/clerk.py and server/api/clerk_deps.py. Headers include:
- Architecture layer and pattern
- Dependencies (external and internal)
- Integration points
- Testing notes

This improves code discoverability and provides context for new developers.

Story: US-001
Task: TASK-001-file-headers"
```

### Example: Documentation Commit

```bash
git commit -m "docs: create SDLC task folder infrastructure (US-001 TASK-000-task-folders)

Subagent: none (coordinator work)
Files: .sdlc-workflow/tasks/, CLAUDE.md

Created task folder system for tracking implementation work:
- Task template with all required files
- README explaining task system
- Validation script for commit messages
- Updated CLAUDE.md with coordinator/implementer roles

This establishes the foundation for proper SDLC workflow with
full traceability and context preservation.

Story: US-001
Task: TASK-000-task-folders"
```

---

## Commit Guidelines

### DO:
✅ Reference user story and task
✅ Indicate which subagent did the work
✅ List all modified files
✅ Explain **why** the change was made
✅ Commit incrementally (small, logical chunks)
✅ Run validation script before push

### DON'T:
❌ Commit without task reference (for implementation)
❌ Mix multiple tasks in one commit
❌ Commit coordinator work without indicating "Subagent: none"
❌ Use vague messages like "fix stuff" or "updates"
❌ Commit broken code or failing tests
❌ Bypass subagents for "quick fixes"

---

## Task References in Commits

### When to Include Task Reference

**MUST include for:**
- Implementation files (`apps/server/`, `apps/frontend/src/`, `tests/`)
- Test files
- Configuration changes that affect behavior

**Optional for:**
- Documentation in `.sdlc-workflow/`
- Documentation in `.claude/`
- CLAUDE.md updates
- README updates in workflow folders

**Format:**
```
(US-XXX TASK-YYY-semantic-name)
```

Always in parentheses, always in commit title.
Include semantic name to make git history self-documenting.

---

## Subagent Markers

### When to Include

**MUST include for:**
- Any implementation file modification
- Test creation/modification
- Code reviews

**Format:**
```
Subagent: <subagent-name>
```

**Valid subagent names:**
- `dev-backend-fastapi` - Backend Python/FastAPI
- `dev-frontend-svelte` - Frontend SvelteKit/Svelte
- `playwright-e2e-tester` - E2E tests
- `qa-code-auditor` - Code quality reviews
- `devops-infra` - Infrastructure/DevOps
- `none` - Coordinator work (docs, workflow files)

---

## Commit Validation Script

**For commit message validation** (separate from branch name validation above)

### Usage

```bash
# Validate current staged changes and commit message
.sdlc-workflow/scripts/validate_sdlc.py

# Output:
# ✅ All checks passed!
# or
# ❌ SDLC VALIDATION FAILED
#    - Missing task reference
#    - Missing subagent marker
```

### What It Checks

1. **Implementation files** → Must have task reference
2. **Implementation files** → Must have subagent marker
3. **Config files** → Warning (but allows)
4. **Coordinator files** → No validation needed

### Integration with Git (Optional)

Create pre-commit hook:

```bash
# .git/hooks/pre-commit
#!/bin/bash
.sdlc-workflow/scripts/validate_sdlc.py
exit $?
```

```bash
chmod +x .git/hooks/pre-commit
```

---

## Traceability Chain

Our workflow maintains complete traceability:

```
User Story → Tasks → Subagent Work → Commits → Files → Git History

Example:
US-001 (Login Flow Validation)
  ├─ TASK-001 (Add file headers)
  │   ├─ Subagent: dev-backend-fastapi
  │   ├─ Commit: abc123
  │   └─ Files: deps.py, user.py, user_service.py
  │
  ├─ TASK-002 (Create E2E tests)
  │   ├─ Subagent: playwright-e2e-tester
  │   ├─ Commit: def456
  │   └─ Files: login-flow.spec.ts
  │
  └─ Merged to main: commit ghi789
```

**Benefits:**
- Can trace any code change back to user story
- Can see which subagent made the change
- Can review task folder for decision context
- Complete audit trail for compliance

---

## Common Scenarios

### Scenario 1: Single Task, Single Commit

```bash
# Task requires modifying 3 files
# Subagent modifies all 3
# Coordinator commits all 3 together

git add file1.py file2.py file3.py
git commit -m "feat: implement feature X (US-002 TASK-001-feature-x)
...
Subagent: dev-backend-fastapi
Files: file1.py, file2.py, file3.py"
```

### Scenario 2: Single Task, Multiple Commits

```bash
# Task requires backend + frontend work
# Two subagents, two commits

# First commit (backend)
git add backend-files
git commit -m "feat: add backend for feature X (US-002 TASK-001-feature-x)
...
Subagent: dev-backend-fastapi"

# Second commit (frontend)
git add frontend-files
git commit -m "feat: add frontend for feature X (US-002 TASK-001-feature-x)
...
Subagent: dev-frontend-svelte"
```

### Scenario 3: Coordinator Documentation Work

```bash
# Coordinator creates/updates workflow docs
git add .sdlc-workflow/ CLAUDE.md
git commit -m "docs: update SDLC workflow (US-001 TASK-000-workflow-docs)

Subagent: none (coordinator work)
Files: .sdlc-workflow/tasks/README.md, CLAUDE.md

Created task folder documentation and updated coordinator
role guidelines.

Story: US-001
Task: TASK-000-workflow-docs"
```

---

## Troubleshooting

### "Missing task reference" error

**Problem:** Committing implementation files without (US-XXX TASK-YYY-semantic-name)

**Solution:**
```bash
# Add task reference to commit message
git commit --amend
# Edit message to include: (US-XXX TASK-YYY-semantic-name)
```

### "Missing subagent marker" error

**Problem:** Committing implementation files without "Subagent: xxx"

**Solution:**
```bash
# Add subagent marker to commit message
git commit --amend
# Add line: "Subagent: <subagent-name>"
```

### Committed to wrong branch

**Problem:** Made commits on main instead of task branch

**Solution:**
```bash
# Create task branch from current position
git checkout -b feat/TASK-XXX-US-YYY

# Reset main to before commits
git checkout main
git reset --hard origin/main

# Task branch has your commits
git checkout feat/TASK-XXX-US-YYY
```

### Invalid branch name error

**Problem:** Attempted to create branch with wrong naming pattern

**Example Error:**
```
❌ Branch 'feature/US-001-description' uses old story-based naming.
Expected pattern: {type}/TASK-{number}[-semantic-name]-US-{story}
```

**Solution:**
```bash
# Use correct pattern (with semantic name - RECOMMENDED)
git checkout -b feat/TASK-001-clerk-mounting-US-001

# Or without semantic name (backward compatible)
git checkout -b feat/TASK-001-US-001
```

---

## Best Practices

1. **One feature branch per user story** - Keep work isolated
2. **Create task folders before implementation** - Plan ahead
3. **Launch subagents for all implementation** - Never bypass
4. **Commit incrementally** - Small, logical chunks
5. **Write descriptive messages** - Future you will thank you
6. **Run validation before push** - Catch issues early
7. **Keep main stable** - Only merge working, tested code
8. **Document decisions in task folders** - Context preservation

---

## Quick Reference

```bash
# Start new task (with semantic name - RECOMMENDED)
git checkout -b {type}/TASK-XXX-{semantic-name}-US-YYY

# Examples:
git checkout -b feat/TASK-001-clerk-mounting-US-001
git checkout -b fix/TASK-010-login-tests-US-001B
git checkout -b refactor/TASK-005-cleanup-US-003
git checkout -b test/TASK-020-e2e-tests-US-002

# Backward compatible (without semantic name)
git checkout -b feat/TASK-001-US-002

# Validate branch name manually (optional - hook does this)
.sdlc-workflow/scripts/validate_branch.py

# Create task folder (match semantic name from branch)
cp -r .sdlc-workflow/tasks/TEMPLATE .sdlc-workflow/tasks/US-YYY-TASK-XXX-semantic-name

# After subagent work
git add <files>
git commit  # Follow format above (include semantic name)

# Validate commit
.sdlc-workflow/scripts/validate_sdlc.py

# Merge when task complete
git checkout main
git merge --no-ff {type}/TASK-XXX-{semantic-name}-US-YYY
git branch -d {type}/TASK-XXX-{semantic-name}-US-YYY  # Clean up
```

---

## References

- User Stories: `.sdlc-workflow/stories/README.md`
- Task Folders: `.sdlc-workflow/tasks/README.md`
- Coordinator Role: `CLAUDE.md` (Coordinator vs Implementer section)
- Commit Messages: [Conventional Commits](https://www.conventionalcommits.org/)
