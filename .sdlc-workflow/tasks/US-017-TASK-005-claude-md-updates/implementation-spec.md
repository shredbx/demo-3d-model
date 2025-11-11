# TASK-005: Implementation Specification

## Files to Modify

### 1. CLAUDE.md

**Search for:** `feature/US-`
**Replace with:** `feat/TASK-XXX-US-`

**Add to branching section:**
```markdown
## Branch Naming

**Pattern:** `{type}/TASK-{number}-US-{story}[-description]`

Valid types: feat, fix, refactor, test, docs, chore

**Automated Validation:** Branch names are validated by `.claude/hooks/pre_tool_use.py`. Invalid patterns will be blocked.

See `.sdlc-workflow/GIT_WORKFLOW.md` for full details.
```

### 2. .claude/hooks/README.md

**Add section:**
```markdown
## Branch Validation (pre_tool_use.py)

The pre-tool-use hook validates git branch names before branch creation.

**Pattern:** `{type}/TASK-{number}-US-{story}[-description]`

**What it does:**
- Detects `git checkout -b` commands
- Validates branch name pattern
- Blocks invalid patterns with error message
- Allows valid patterns to proceed

**Exit codes:**
- 0: Allow (valid branch or not branch creation)
- 2: Block (invalid branch name)

**Example Error:**
```
❌ BLOCKED: Invalid branch name 'feature/US-001'
Expected: feat/TASK-XXX-US-XXX
```

**Fail-safe:** If validation script missing or crashes, allows tool execution (doesn't break workflow).
```

### 3. .sdlc-workflow/scripts/README.md

**Add section:**
```markdown
## validate_branch.py

Validates git branch names against SDLC naming convention.

**Usage:**
```bash
.sdlc-workflow/scripts/validate_branch.py              # Current branch
.sdlc-workflow/scripts/validate_branch.py <branch>     # Specific branch
```

**Exit Codes:**
- 0: Valid branch name
- 1: Invalid branch name
- 2: Script error

**Integration:**
- Called by `.claude/hooks/pre_tool_use.py`
- Can be called manually for testing

**Extending:**
To add new branch type, edit `VALID_TYPES` in script.
```

---

**Verification:** grep -r "feature/US-" (should find none in updated docs)
