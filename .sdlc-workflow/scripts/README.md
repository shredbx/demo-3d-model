# SDLC Validation Scripts

This directory contains validation scripts that enforce SDLC workflow conventions automatically.

## Philosophy

**Trust but verify** - We trust AI to follow the workflow, but we validate automatically to catch mistakes early.

**Fail fast** - Catch issues before they enter git history, not after.

**Clear feedback** - When validation fails, provide actionable error messages with examples.

---

## Scripts

### 1. Branch Name Validation (`validate_branch.py`)

**Purpose:** Enforce task-based branch naming conventions

**Pattern:** `{type}/TASK-{number}-US-{story}[-description]`

**Usage:**
```bash
# Validate current branch
./validate_branch.py

# Validate specific branch name
./validate_branch.py feat/TASK-001-US-002
```

**Exit Codes:**
- `0` - Branch name is valid
- `1` - Branch name is invalid (error message to stderr)
- `2` - Script error (git not available, etc.)

**Valid Types:**
- `feat` - New features
- `fix` - Bug fixes
- `refactor` - Code improvements (no behavior change)
- `test` - Test additions/updates
- `docs` - Documentation only
- `chore` - Build/tooling changes

**Examples:**
```bash
# ✅ Valid
./validate_branch.py feat/TASK-001-US-001
./validate_branch.py fix/TASK-042-US-001B
./validate_branch.py refactor/TASK-005-US-001B-cleanup
./validate_branch.py main  # Special case

# ❌ Invalid
./validate_branch.py feature/US-001-description  # Old pattern
./validate_branch.py feat/some-branch  # Missing task/story IDs
```

**Integration:**
- Called by `.claude/hooks/pre_tool_use.py` before git branch creation
- Can be called manually for validation
- Used in CI/CD pipelines (future)

**Error Messages:**
Provides context-specific error messages:
- Old story-based pattern detected → suggests correct task-based pattern
- Missing task reference → explains task-based branching
- Generic invalid → shows pattern with examples

**Performance:** < 100ms (fast enough for real-time validation)

**See:** `.sdlc-workflow/GIT_WORKFLOW.md` for full branch naming documentation

---

### 2. Commit Message Validation (`validate_sdlc.py`)

**Purpose:** Enforce commit message conventions and task references

**Usage:**
```bash
# Validate current staged changes
./validate_sdlc.py
```

**What It Checks:**
1. **Implementation files** → Must have task reference `(US-XXX TASK-YYY)`
2. **Implementation files** → Must have subagent marker `Subagent: xxx`
3. **Config files** → Warning only (but allows)
4. **Coordinator files** → No validation needed

**Implementation Paths:**
- `apps/server/src/` - Backend code
- `apps/frontend/src/` - Frontend code
- `tests/` - Test files

**Coordinator Paths (exempt from validation):**
- `.sdlc-workflow/` - SDLC documentation
- `.claude/` - Claude configuration
- `CLAUDE.md`, `README.md` - Project docs

**Valid Subagent Names:**
- `dev-backend-fastapi` - Backend Python/FastAPI
- `dev-frontend-svelte` - Frontend SvelteKit/Svelte
- `playwright-e2e-tester` - E2E tests
- `qa-code-auditor` - Code quality reviews
- `devops-infra` - Infrastructure/DevOps
- `none` - Coordinator work (docs, workflow files)

**Exit Codes:**
- `0` - All checks passed
- `1` - Validation failed (with error details)

**Example Output (failure):**
```
❌ SDLC VALIDATION FAILED
   - apps/server/src/api/endpoints.py: Missing task reference
   - apps/server/src/api/endpoints.py: Missing subagent marker
```

**Integration:**
- Can be called manually before commits
- Optional git pre-commit hook (see below)

**See:** `.sdlc-workflow/GIT_WORKFLOW.md` for commit message format

---

### 3. User Story Creation (`story_create.py`)

**Purpose:** Create new user stories from template

**Usage:**
```bash
./story_create.py <category> <title>

# Example:
./story_create.py auth "Login flow validation"
```

**Categories:**
- `auth` - Authentication/authorization
- `api` - API endpoints
- `ui` - User interface
- `infra` - Infrastructure
- `workflow` - SDLC workflow improvements
- `data` - Database/data models

**What It Does:**
1. Scans existing stories to find next ID
2. Creates story from TEMPLATE.md
3. Populates metadata (ID, category, date)
4. Opens in editor for completion

**Output:**
```
✅ Created: .sdlc-workflow/stories/auth/US-042-auth-login-flow-validation.md
📝 Next: Edit the file to complete all sections
```

**See:** `.sdlc-workflow/stories/README.md` for user story documentation

---

### 4. Install Git Hooks (`install_git_hooks.sh`)

**Purpose:** Install git hooks for local validation

**Usage:**
```bash
./install_git_hooks.sh
```

**What It Installs:**
- `pre-commit` hook → calls `validate_sdlc.py`

**Optional:** Git hooks are optional in our workflow (hooks in `.claude/hooks/` are primary)

**To Uninstall:**
```bash
rm .git/hooks/pre-commit
```

---

## Adding New Scripts

When adding a new validation script:

1. **Create script** in this directory
2. **Make executable:** `chmod +x script_name.py`
3. **Document it here** in this README
4. **Write tests** in `tests/` directory
5. **Add to hooks** if needed (`.claude/hooks/`)

**Best Practices:**
- Use clear exit codes (0=success, 1=validation failed, 2=error)
- Provide actionable error messages with examples
- Keep validation fast (< 100ms)
- Fail-safe when possible (allow on script errors)
- Document integration points

---

## Integration Points

### Claude Hooks

Branch validation:
- `.claude/hooks/pre_tool_use.py` → calls `validate_branch.py`

Coordinator enforcement:
- `.claude/hooks/sdlc_guardian.py` → blocks implementation file edits

### Git Hooks (Optional)

Commit validation:
- `.git/hooks/pre-commit` → calls `validate_sdlc.py`

**Note:** Claude hooks are primary enforcement. Git hooks are optional local validation.

### CI/CD (Future)

Planned integrations:
- GitHub Actions validation on PR
- Branch name validation on push
- Commit message linting
- SDLC compliance reporting

---

## Troubleshooting

### Script not executable

```bash
chmod +x .sdlc-workflow/scripts/validate_branch.py
chmod +x .sdlc-workflow/scripts/validate_sdlc.py
```

### Validation failing incorrectly

Test the script directly:
```bash
# Branch validation
./validate_branch.py feat/TASK-001-US-001
echo "Exit code: $?"

# Commit validation (requires staged changes)
git add <file>
./validate_sdlc.py
```

### Want to bypass validation temporarily

Not recommended, but if absolutely necessary:
- Comment out hook in `.claude/settings.local.json`
- Or use `--no-verify` flag (git only, doesn't affect Claude hooks)

---

## Related Documentation

- **Git Workflow:** `.sdlc-workflow/GIT_WORKFLOW.md`
- **Task Folders:** `.sdlc-workflow/tasks/README.md`
- **User Stories:** `.sdlc-workflow/stories/README.md`
- **Hooks:** `.claude/hooks/README.md`
- **SDLC Progress:** `CLAUDE.md` (SDLC Progress Status section)

---

**Last Updated:** 2025-11-07
