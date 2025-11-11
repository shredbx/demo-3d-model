# TASK-006: Implementation Specification

## File: .git-hooks/pre-commit.template

```bash
#!/bin/bash
# Git pre-commit hook - validates branch name
# 
# OPTIONAL: Install this to validate branch names in native git
# Installation: cp .git-hooks/pre-commit.template .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

# Path to validation script
SCRIPT="$(git rev-parse --show-toplevel)/.sdlc-workflow/scripts/validate_branch.py"

# Check if validation script exists
if [ ! -f "$SCRIPT" ]; then
    echo "Warning: Branch validation script not found"
    exit 0  # Don't block commits
fi

# Get current branch
BRANCH=$(git branch --show-current)

# Validate branch name
if ! "$SCRIPT" "$BRANCH" > /dev/null 2>&1; then
    echo "=================================="
    echo "❌ Invalid branch name: $BRANCH"
    echo "=================================="
    "$SCRIPT" "$BRANCH"  # Show error message
    echo ""
    echo "Fix by renaming branch:"
    echo "  git branch -m <new-correct-name>"
    echo ""
    exit 1  # Block commit
fi

# Branch is valid, allow commit
exit 0
```

## Installation Instructions

Create `.git-hooks/README.md`:
```markdown
# Git Hooks (Optional)

## pre-commit Hook

Validates branch names on commit.

**Installation:**
```bash
cp .git-hooks/pre-commit.template .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Uninstall:**
```bash
rm .git/hooks/pre-commit
```

**Note:** This is optional. Branch validation already happens in Claude's pre-tool-use hook.
```

---

**Verification:** Test by creating invalid branch manually, attempt commit
