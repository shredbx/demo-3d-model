# TASK-004: Implementation Specification

**For:** devops-infra subagent
**File:** `.sdlc-workflow/GIT_WORKFLOW.md`

---

## Exact Content Replacements

### 1. Replace Lines 11-22 (Branch Naming Section)

**Find and replace this:**
```markdown
**Branch Naming:**
- User story work: `feature/US-XXX-short-description`
- Hotfixes: `hotfix/short-description`
- Experiments: `experiment/short-description`
```

**With this complete section:**
```markdown
## Branch Naming Convention

**Pattern:** `{type}/TASK-{number}-US-{story}[-description]`

**Valid Branch Types:**
| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New features | `feat/TASK-001-US-005-user-auth` |
| `fix` | Bug fixes | `fix/TASK-042-US-003-login-error` |
| `refactor` | Code improvements (no behavior change) | `refactor/TASK-010-US-002-cleanup` |
| `test` | Test additions/modifications | `test/TASK-015-US-004-e2e-tests` |
| `docs` | Documentation changes | `docs/TASK-020-US-001-api-docs` |
| `chore` | Build, tooling, dependencies | `chore/TASK-030-US-006-deps-update` |

**Examples:**
```bash
# Basic pattern (most common)
git checkout -b feat/TASK-001-US-001

# With story letter suffix (US-001B, US-001C, etc.)
git checkout -b fix/TASK-042-US-001B

# With optional description
git checkout -b refactor/TASK-005-US-001B-database-cleanup

# All types are valid
git checkout -b test/TASK-010-US-002
git checkout -b docs/TASK-020-US-005
git checkout -b chore/TASK-030-US-010-update-deps
```

### Why Task-Based (Not Story-Based)?

**Our Approach:**
- One branch per **task** (TASK-XXX)
- Multiple tasks can work on same story in parallel
- Each task gets its own focused branch

**Benefits:**
1. **Parallel Work** - Frontend and backend tasks can work simultaneously
2. **Better Traceability** - Git history shows which task made which changes
3. **Smaller PRs** - Task-focused branches = smaller, easier reviews
4. **Automation-Friendly** - Scripts can parse task IDs from branch names
5. **Clear Completion** - Branch deleted when task completes (not when entire story completes)

**Example:**
```
Story: US-001B (RBAC + Audit Logging)
  ├─ feat/TASK-002-US-001B (Database migrations)
  ├─ feat/TASK-003-US-001B (RBAC components)
  ├─ feat/TASK-004-US-001B (Audit logging)
  └─ test/TASK-005-US-001B (E2E tests)

All 4 tasks work in parallel, merge independently.
```

### Automated Validation

Branch names are **automatically validated** by `.claude/hooks/pre_tool_use.py`.

**What happens:**
1. You run: `git checkout -b feature/US-001-login`
2. Hook detects invalid pattern
3. Tool call blocked with error message
4. Error shows correct pattern and examples

**Example Error:**
```
❌ BLOCKED: Invalid branch name 'feature/US-001-login'

Expected pattern: {type}/TASK-{number}-US-{story}[-description]

Valid examples:
  feat/TASK-001-US-001
  fix/TASK-042-US-001B
  refactor/TASK-005-US-001B-cleanup

Valid types: feat, fix, refactor, test, docs, chore
```

### Fixing Wrong Branch Names

If you create a branch with the wrong pattern:

**Option 1: Rename branch**
```bash
# If you haven't pushed yet
git branch -m old-wrong-name feat/TASK-XXX-US-XXX

# If you've already pushed
git branch -m old-wrong-name feat/TASK-XXX-US-XXX
git push origin --delete old-wrong-name
git push origin feat/TASK-XXX-US-XXX
git push origin -u feat/TASK-XXX-US-XXX
```

**Option 2: New branch + cherry-pick**
```bash
# Create correct branch from main
git checkout main
git checkout -b feat/TASK-XXX-US-XXX

# Cherry-pick commits from wrong branch
git cherry-pick <commit1> <commit2> ...

# Delete old branch
git branch -D old-wrong-name
```
```

---

### 2. Search and Replace Throughout Document

Search entire document for any mentions of:
- `feature/US-` → Replace with `feat/TASK-XXX-US-`
- Story-based examples → Replace with task-based examples

---

### 3. Add Cross-References Section

Add before or after branch naming section:

```markdown
### Related Documentation

- **Validation Script:** `.sdlc-workflow/scripts/validate_branch.py`
- **Hook Implementation:** `.claude/hooks/pre_tool_use.py`
- **Branching Strategy:** `.sdlc-workflow/.plan/03-workflow-diagrams.md` (line 71, 421)
- **Main Workflow Guide:** `CLAUDE.md` (branching section)
```

---

## Verification Steps

After implementation:
1. ✅ Search for "feature/US-" in document (should find none)
2. ✅ Verify all examples use task-based pattern
3. ✅ Check table of valid types is complete (all 6)
4. ✅ Verify rationale section explains "why"
5. ✅ Verify validation section mentions hook
6. ✅ Verify "how to fix" section is clear

---

## Files to Modify

- `.sdlc-workflow/GIT_WORKFLOW.md` (primary changes)

**Do NOT modify:**
- Commit message format (separate section, stays as-is)
- PR workflow (separate section)
- Other workflow sections

---

**Success:** Documentation matches actual practice, no contradictions
