#!/bin/bash
#
# Install SDLC git hooks
#
# Copies hook templates from .claude/git-hooks/ to .git/hooks/
# and makes them executable.
#

set -e

# Get project root
PROJECT_ROOT="$(git rev-parse --show-toplevel)"

echo "Installing SDLC git hooks..."
echo

# Check if .claude/git-hooks/ exists
if [ ! -d "$PROJECT_ROOT/.claude/git-hooks" ]; then
    echo "❌ Error: .claude/git-hooks/ directory not found"
    exit 1
fi

# Create .git/hooks/ if it doesn't exist
mkdir -p "$PROJECT_ROOT/.git/hooks"

# Copy hooks
for hook_file in "$PROJECT_ROOT/.claude/git-hooks"/*; do
    hook_name=$(basename "$hook_file")
    target="$PROJECT_ROOT/.git/hooks/$hook_name"

    # Copy hook
    cp "$hook_file" "$target"

    # Make executable
    chmod +x "$target"

    echo "✓ Installed: $hook_name"
done

echo
echo "✅ All git hooks installed successfully!"
echo
echo "Installed hooks:"
echo "  - prepare-commit-msg  (auto-formats commit messages with TASK/US IDs)"
echo "  - post-commit         (tracks commits in commit-task-map.csv)"
echo "  - post-checkout       (auto-switches tasks when changing branches)"
echo

exit 0
