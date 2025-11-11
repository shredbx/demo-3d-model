#!/bin/bash
# Setup Git Hooks for Bestays Platform
# Installs TDD enforcement pre-commit hook with quality gates
#
# Usage: .sdlc-workflow/scripts/setup-git-hooks.sh
# Or via Makefile: make install-hooks

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}📦 Setting up Git Hooks for Bestays Platform${NC}"
echo ""

# Check if we're in the repository root
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not in repository root${NC}"
    echo "   Please run from: /Users/solo/Projects/_repos/bestays/"
    exit 1
fi

# Check if template exists (new TDD enforcement hook)
TEMPLATE=".sdlc-workflow/templates/git-hooks/pre-commit-tdd"
if [ ! -f "$TEMPLATE" ]; then
    echo -e "${RED}❌ Error: Template not found${NC}"
    echo "   Expected: $TEMPLATE"
    echo ""
    echo "   This template includes:"
    echo "     - TDD compliance check (test files exist)"
    echo "     - TypeScript type checking"
    echo "     - Linting"
    echo "     - Unit tests"
    echo "     - Coverage validation"
    exit 1
fi

# Install pre-commit hook
HOOK_PATH=".git/hooks/pre-commit"

if [ -f "$HOOK_PATH" ]; then
    echo -e "${YELLOW}⚠️  Pre-commit hook already exists${NC}"
    echo ""
    echo "Options:"
    echo "  1. Backup and replace with TDD enforcement hook"
    echo "  2. Keep existing hook"
    echo "  3. Exit"
    echo ""
    read -p "Choose option (1-3): " choice

    case $choice in
        1)
            BACKUP="${HOOK_PATH}.backup.$(date +%Y%m%d-%H%M%S)"
            echo ""
            echo -e "${BLUE}Backing up existing hook to: $BACKUP${NC}"
            cp "$HOOK_PATH" "$BACKUP"
            ;;
        2)
            echo ""
            echo -e "${GREEN}✓ Keeping existing hook${NC}"
            exit 0
            ;;
        3)
            echo ""
            echo "Exiting without changes."
            exit 0
            ;;
        *)
            echo ""
            echo -e "${RED}Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
fi

echo -e "${BLUE}Installing TDD enforcement pre-commit hook...${NC}"
cp "$TEMPLATE" "$HOOK_PATH"
chmod +x "$HOOK_PATH"
echo -e "${GREEN}✓${NC} Installed: $HOOK_PATH"

# Verify installation
echo ""
echo -e "${BLUE}Verifying installation...${NC}"

if [ -x "$HOOK_PATH" ]; then
    echo -e "${GREEN}✓${NC} Hook is executable"
else
    echo -e "${RED}❌${NC} Hook is not executable"
    exit 1
fi

# Show what the hook does
echo ""
echo -e "${GREEN}✅ Git hooks installed successfully!${NC}"
echo ""
echo -e "${BLUE}What the hook does:${NC}"
echo "  When you run 'git commit', the hook will automatically:"
echo "    1. ✅ Check test files exist for implementation changes"
echo "    2. ✅ Run TypeScript type checking"
echo "    3. ✅ Run linting (warnings only)"
echo "    4. ✅ Run unit tests"
echo "    5. ✅ Validate coverage thresholds"
echo ""
echo "  Target execution time: < 30 seconds"
echo ""
echo -e "${BLUE}TDD Workflow:${NC}"
echo "  Write test first → Implement → Refactor → Commit"
echo "  Use: /tdd-red, /tdd-green, /tdd-refactor"
echo ""
echo -e "${BLUE}Bypass hook (emergency only):${NC}"
echo "  git commit --no-verify -m \"WIP: message\""
echo ""
echo -e "${YELLOW}⚠️  Only bypass for:${NC}"
echo "  - WIP commits on feature branches"
echo "  - Experimental work"
echo "  - NEVER for PRs or production"
echo ""
echo -e "${BLUE}Test hook manually:${NC}"
echo "  .git/hooks/pre-commit"
echo ""
echo -e "${YELLOW}Note:${NC} This is a local-only hook. Comprehensive tests still run"
echo "      in CI/CD pipeline on push (backend external validation,"
echo "      Storybook build, full test suite)."
echo ""
