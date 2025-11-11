# Claude Code Hooks

This folder contains Claude Code hooks that enforce our SDLC workflow automatically.

## What are Hooks?

Hooks are shell commands that run at specific points in Claude Code's lifecycle. They provide **deterministic enforcement** of workflow rules, ensuring certain behaviors always happen rather than relying on the LLM to remember.

**Philosophy:** "Trust but verify" - We trust AI to generate good work, but we verify it follows our process automatically.

---

## Active Hooks

### 1. Branch Validation (`pre_tool_use.py`)

**Type:** PreToolUse (runs before Bash tool calls)

**Purpose:** Enforce task-based branch naming conventions

**What it does:**
- ✅ Validates branch names match pattern: `{type}/TASK-{number}-US-{story}[-description]`
- ❌ Blocks creation of invalidly named branches
- 💡 Provides error message with correct pattern and examples
- 🚀 Calls `.sdlc-workflow/scripts/validate_branch.py` for validation logic

**Valid branch types:**
- `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
- Special case: `main` (always valid)

**Example Valid Branches:**
- ✅ `feat/TASK-001-US-001`
- ✅ `fix/TASK-042-US-001B`
- ✅ `refactor/TASK-005-US-001B-cleanup`

**Example Invalid Branches:**
- ❌ `feature/US-001-description` (old story-based pattern)
- ❌ `feat/some-branch` (missing task/story IDs)

**Example Output (when blocked):**
```
======================================================================
❌ BLOCKED: Invalid branch name 'feature/US-001-description'
======================================================================

❌ Branch 'feature/US-001-description' uses old story-based naming.

Expected pattern: {type}/TASK-{number}-US-{story}[-description]

Valid examples:
  feat/TASK-001-US-001
  fix/TASK-042-US-001B
  refactor/TASK-005-US-001B-cleanup

Rationale: We use task-based branching (one branch per task, not per story)
to enable parallel work and better git history traceability.

For more information, see: .sdlc-workflow/GIT_WORKFLOW.md
======================================================================
```

**Testing:**
```bash
# Test valid branch name:
echo '{"tool":"Bash","command":"git checkout -b feat/TASK-001-US-002"}' | .claude/hooks/pre_tool_use.py
# Exit code: 0 (allowed)

# Test invalid branch name:
echo '{"tool":"Bash","command":"git checkout -b feature/US-001"}' | .claude/hooks/pre_tool_use.py
# Exit code: 2 (blocked)
```

**Why it matters:**
1. **Consistency** - All branches follow same naming pattern
2. **Automation** - Scripts can reliably parse task/story IDs
3. **Traceability** - Git history clearly shows task → branch → commits
4. **Early Feedback** - Catch naming mistakes before branch is created

---

### 2. SDLC Guardian (`sdlc_guardian.py`)

**Type:** PreToolUse (runs before Edit/Write tool calls)

**Purpose:** Enforce Coordinator vs Implementer separation

**What it does:**
- ✅ Allows coordinator to modify workflow docs (`.sdlc-workflow/`, `.claude/`, `CLAUDE.md`)
- ❌ Blocks coordinator from modifying implementation files (`apps/server/src/`, `apps/frontend/src/`, `tests/`)
- 💡 Provides helpful error message with correct subagent to use

**Why it matters:**
1. **Context Preservation** - Subagent work saved in task folders forever
2. **Code Consistency** - Subagents enforce domain-specific patterns
3. **Audit Trail** - Clear record of who did what and why
4. **Prevent Mistakes** - Catches violations before they happen (not after)

**Example Output (when blocked):**
```
======================================================================
🚨 SDLC WORKFLOW VIOLATION
======================================================================

❌ Coordinator cannot modify implementation files!

📄 File: apps/server/src/api/deps.py

🤖 Use: Task(subagent_type="dev-backend-fastapi", ...)

💡 Remember: You are COORDINATOR only.
   - Launch subagents for ALL implementation work
   - Save subagent reports in task folder
   - Maintain audit trail

📖 See: CLAUDE.md section 'Coordinator vs Implementer Roles'
======================================================================
```

**Testing:**
```bash
# This should be BLOCKED:
echo '{"tool_name":"Edit","tool_input":{"file_path":"apps/server/src/api/deps.py"}}' | .claude/hooks/sdlc_guardian.py
# Exit code: 2 (blocked)

# This should be ALLOWED:
echo '{"tool_name":"Edit","tool_input":{"file_path":".sdlc-workflow/tasks/README.md"}}' | .claude/hooks/sdlc_guardian.py
# Exit code: 0 (allowed)
```

---

## Hook Configuration

Hooks are registered in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/sdlc_guardian.py"
          }
        ]
      }
    ]
  }
}
```

**Matcher:** Only runs on `Edit` and `Write` tools (not Read, Grep, Glob)

**Storage:** Project-specific (`.claude/settings.local.json`) - only applies to this project

---

## Path Definitions

### Coordinator-Allowed Paths

Coordinator (main Claude) CAN modify these:
- `.claude/` - Claude Code configuration
- `.sdlc-workflow/` - User stories, tasks, workflow docs
- `CLAUDE.md` - Project instructions
- `README.md` - Top-level documentation
- `.gitignore` - Git configuration
- `.env.example` - Environment template

### Implementation Paths (Require Subagent)

These MUST be modified by subagents:
- `apps/server/src/` → `dev-backend-fastapi`
- `apps/frontend/src/` → `dev-frontend-svelte`
- `tests/` → `playwright-e2e-tester`

---

## Adding New Hooks

To add a new hook:

1. **Create hook script** in this folder (`.claude/hooks/your_hook.py`)
2. **Make it executable:** `chmod +x .claude/hooks/your_hook.py`
3. **Register in settings:** Update `.claude/settings.local.json`
4. **Document it here** in this README

**Best Practices:**
- Exit code 0 = allow (pass through)
- Exit code 2 = block with message
- Fail open (exit 0) on errors
- Provide helpful error messages
- Keep checks fast (<100ms)

---

## Troubleshooting

### Hook not running?

Check `.claude/settings.local.json` has the hook registered:
```bash
cat .claude/settings.local.json | grep -A 10 '"hooks"'
```

### Hook blocking incorrectly?

Test the hook directly:
```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"YOUR_FILE_PATH"}}' | .claude/hooks/sdlc_guardian.py
echo "Exit code: $?"
```

### Want to disable temporarily?

Comment out the hook in `.claude/settings.local.json` (don't delete - you'll forget to re-enable!)

---

## Related Documentation

- **Git Workflow:** `.sdlc-workflow/GIT_WORKFLOW.md` (branch naming, task-based workflow)
- **Branch Validation:** `.sdlc-workflow/scripts/validate_branch.py` (validation logic)
- **Commit Validation:** `.sdlc-workflow/scripts/validate_sdlc.py` (commit message validation)
- **Coordinator Role:** `CLAUDE.md` section "Coordinator vs Implementer Roles"
- **Task Folders:** `.sdlc-workflow/tasks/README.md`
- **Claude Hooks Docs:** https://code.claude.com/docs/en/hooks-guide

---

## Hook Effectiveness

**Before Hook:**
- Coordinator would occasionally modify implementation files
- Context lost (no subagent reports saved)
- Audit trail incomplete
- Had to manually remind and revert work

**After Hook:**
- Immediate feedback when violation attempted
- Zero implementation file modifications by coordinator
- Complete audit trail maintained
- Confidence in workflow adherence

**Result:** Rapid, safe development with maintained quality standards.
