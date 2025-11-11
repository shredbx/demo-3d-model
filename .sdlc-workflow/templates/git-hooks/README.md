# Git Hook Templates (Optional)

This directory contains **optional** git hook templates for local validation and testing.

**Note:** These are supplementary to the primary validation system (Claude hooks in `.claude/hooks/` and CI/CD pipeline in `.github/workflows/`).

---

## Why Optional?

This project uses **Claude Code** for all development work. The primary validation happens through:
- **Claude hooks** (`.claude/hooks/pre_tool_use.py`) - Validates branch names before creation
- **SDLC guardian** (`.claude/hooks/sdlc_guardian.py`) - Enforces coordinator role
- **CI/CD Pipeline** (`.github/workflows/ci.yml`) - Automated testing on push/PR

**Git hooks are optional** because:
1. Claude hooks cover 99% of branch creation (via Claude Code)
2. CI/CD pipeline runs comprehensive tests automatically
3. Direct git usage is rare in this LLM-focused workflow
4. Git hooks add local feedback but aren't required

**When to use git hooks:**
- Want fast feedback before CI/CD (< 30s)
- Manual git operations outside Claude Code
- Testing before pushing to remote
- Want double validation as safety net

---

## Available Templates

### 1. Pre-Commit Tests (`pre-commit-tests`)

**Purpose:** Run fast tests before allowing commits (TypeScript check + unit tests)

**Target execution time:** < 30 seconds

**Installation:**
```bash
# Use installation script (recommended)
.sdlc-workflow/scripts/setup-git-hooks.sh

# Or manual installation
cp .sdlc-workflow/templates/git-hooks/pre-commit-tests .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**What it runs:**
1. TypeScript type checking (`npm run check`)
2. Unit tests (`npm run test:unit`)

**What it skips:**
- E2E tests (too slow, run in CI/CD)
- Backend tests (run in CI/CD)
- Coverage enforcement (run in CI/CD)

**Usage:**
```bash
# Normal commit (hook runs automatically)
git add .
git commit -m "feat: add login page"

# Output:
# 🔍 Running pre-commit tests...
# [1/2] TypeScript type checking...
#   ✓ TypeScript check passed
# [2/2] Unit tests...
#   ✓ Unit tests passed (31 tests)
# ✅ All pre-commit tests passed!
#    Execution time: 12s

# Bypass hook for WIP commits
git commit --no-verify -m "WIP: experimenting"
```

**When to bypass (--no-verify):**
- Work in progress commits
- Experimental branches
- Quick fixes needing immediate push
- **Never for PRs or production**

### 2. Pre-Checkout Wrapper (`pre-checkout-wrapper`)

**Purpose:** Validate branch names before creation via manual git commands

**Note:** Git doesn't have a native "pre-checkout" hook, so this is a wrapper script.

**Installation:**

```bash
# Option 1: Add to PATH (recommended)
mkdir -p ~/bin
cp .sdlc-workflow/templates/git-hooks/pre-checkout-wrapper ~/bin/git-new-branch
chmod +x ~/bin/git-new-branch

# Option 2: Use directly from repo
alias git-new-branch='.sdlc-workflow/templates/git-hooks/pre-checkout-wrapper'
```

**Usage:**

```bash
# Instead of:
git checkout -b feat/TASK-001-US-001

# Use:
git-new-branch -b feat/TASK-001-US-001

# Or with alias:
git-new-branch -b feat/TASK-001-US-001
```

**What it does:**
1. Validates branch name using `.sdlc-workflow/scripts/validate_branch.py`
2. If valid → creates branch with `git checkout -b`
3. If invalid → shows error and aborts

**Example Output (valid):**
```
🔍 Validating branch name: feat/TASK-001-US-001
✅ Branch name valid
🚀 Creating branch: feat/TASK-001-US-001
Switched to a new branch 'feat/TASK-001-US-001'
```

**Example Output (invalid):**
```
🔍 Validating branch name: feature/US-001
❌ Branch name validation failed

❌ Branch 'feature/US-001' uses old story-based naming.

Expected pattern: {type}/TASK-{number}-US-{story}[-description]

Valid examples:
  feat/TASK-001-US-001
  fix/TASK-042-US-001B
  refactor/TASK-005-US-001B-cleanup

💡 Tip: See .sdlc-workflow/GIT_WORKFLOW.md for branch naming conventions
```

---

## Other Hooks (Not Included)

### Why no pre-commit hook?

We have a commit validation script (`.sdlc-workflow/scripts/validate_sdlc.py`) but don't install it as a git hook because:

1. **Coordinator doesn't commit implementation files** - SDLC guardian blocks this
2. **Task references added during commit** - Natural workflow step
3. **Validation is fast** - Can run manually if needed

**To use commit validation manually:**
```bash
# Before committing
.sdlc-workflow/scripts/validate_sdlc.py

# If checks pass, commit
git commit
```

**To install as git hook (optional):**
```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
.sdlc-workflow/scripts/validate_sdlc.py
EOF

chmod +x .git/hooks/pre-commit
```

---

## Relationship to Claude Hooks

| Hook Type | Location | When It Runs | Purpose |
|-----------|----------|--------------|---------|
| **Claude Hook** | `.claude/hooks/pre_tool_use.py` | Before Bash tool in Claude | Primary branch validation |
| **Claude Hook** | `.claude/hooks/sdlc_guardian.py` | Before Edit/Write in Claude | Coordinator enforcement |
| **Git Hook** (optional) | `.git/hooks/pre-commit` | Before git commit | Commit validation |
| **Git Wrapper** (optional) | `pre-checkout-wrapper` | Manual invocation | Branch validation outside Claude |

**Primary enforcement:** Claude hooks (always active in Claude Code)
**Optional safety net:** Git hooks/wrappers (for manual git usage)

---

## Installation Script

**Optional:** Install all git hooks at once:

```bash
# Create installation script
cat > .sdlc-workflow/scripts/install_git_hooks.sh << 'EOF'
#!/bin/bash
# Install optional git hooks

# Pre-commit (commit validation)
if [ ! -f .git/hooks/pre-commit ]; then
    echo "Installing pre-commit hook..."
    cat > .git/hooks/pre-commit << 'HOOK'
#!/bin/bash
.sdlc-workflow/scripts/validate_sdlc.py
HOOK
    chmod +x .git/hooks/pre-commit
    echo "✅ Installed pre-commit hook"
else
    echo "⚠️  Pre-commit hook already exists"
fi

# Branch validation wrapper (to PATH)
if [ ! -f ~/bin/git-new-branch ]; then
    echo "Installing git-new-branch wrapper..."
    mkdir -p ~/bin
    cp .sdlc-workflow/templates/git-hooks/pre-checkout-wrapper ~/bin/git-new-branch
    chmod +x ~/bin/git-new-branch
    echo "✅ Installed git-new-branch to ~/bin/"
    echo "💡 Add ~/bin to PATH if not already: export PATH=\$HOME/bin:\$PATH"
else
    echo "⚠️  git-new-branch already exists in ~/bin/"
fi

echo ""
echo "✅ Git hooks installation complete!"
echo ""
echo "Usage:"
echo "  git-new-branch -b feat/TASK-001-US-001  # Create validated branch"
echo "  git commit                              # Runs pre-commit validation"
EOF

chmod +x .sdlc-workflow/scripts/install_git_hooks.sh

# Run it
.sdlc-workflow/scripts/install_git_hooks.sh
```

---

## Uninstallation

```bash
# Remove git hooks
rm .git/hooks/pre-commit

# Remove wrapper
rm ~/bin/git-new-branch

# Or disable without deleting
chmod -x .git/hooks/pre-commit
```

---

## Troubleshooting

### Wrapper not found after installation

Check PATH:
```bash
echo $PATH | grep "$HOME/bin"

# Add to PATH if missing (add to ~/.bashrc or ~/.zshrc)
export PATH=$HOME/bin:$PATH
```

### Validation failing incorrectly

Test validation script directly:
```bash
.sdlc-workflow/scripts/validate_branch.py feat/TASK-001-US-001
echo "Exit code: $?"  # Should be 0 for valid
```

### Want to bypass validation

**Not recommended**, but if absolutely necessary:
```bash
# Use regular git (bypasses wrapper)
git checkout -b branch-name

# Or rename hook temporarily
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
```

---

## Summary

✅ **Primary validation:** Claude hooks (`.claude/hooks/`) - always active
📋 **Optional helpers:** Git hooks/wrappers - for manual git usage
🎯 **Recommendation:** Use Claude Code for all operations (hooks work automatically)
⚡ **When needed:** Install git hooks if doing manual git operations frequently

**See:**
- Branch naming: `.sdlc-workflow/GIT_WORKFLOW.md`
- Claude hooks: `.claude/hooks/README.md`
- Validation scripts: `.sdlc-workflow/scripts/README.md`

---

**Last Updated:** 2025-11-07
